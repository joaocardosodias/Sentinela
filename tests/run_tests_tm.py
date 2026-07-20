# -*- coding: utf-8 -*-
"""
Execucao automatizada dos testes objetivos (TM-02, TM-03, TM-05, TM-07)
descritos em docs/relatorio-testes.md, contra o backend local + Supabase.
Script temporario de execucao de testes — remove os dados criados ao final.
"""
import json
import os
import sqlite3
import sys
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt as pyjwt
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

BASE = "http://127.0.0.1:5000"
DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET_KEY"]

RESULTS = {}
CREATED_SCAN_IDS = []
CREATED_PLACAS = []          # placas de veiculos criados pelos testes (p/ limpeza)
LOCAL_USER_EMAIL = "tm07.gestorlocal@teste-sprint4.com"


def db():
    return psycopg2.connect(DATABASE_URL)


def login(email, password):
    r = requests.post(f"{BASE}/api/auth/login",
                      json={"email": email, "password": password}, timeout=30)
    r.raise_for_status()
    return r.json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ───────────────────────── setup ─────────────────────────
token_remoto = login("gestorremoto@gestorremoto.com", "gestorremoto")

# drone vinculado a uma operacao ativa (necessario para TM-02/03/05)
with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("""
        SELECT d.id AS drone_id, d.nome AS drone_nome,
               o.id AS operacao_id, o.name AS operacao_nome, o.localizacao
        FROM drones d JOIN operacoes o ON o.id = d.operacao_id
        WHERE o.status = 'ativa' LIMIT 1
    """)
    drone = cur.fetchone()
assert drone, "Nenhum drone de operacao ativa encontrado"
DRONE_ID = drone["drone_id"]


# ───────────────────────── TM-07: autenticacao e RBAC ─────────────────────────
def tm07():
    cases = []

    # 1) sem header Authorization -> 401
    r = requests.get(f"{BASE}/api/scans/", timeout=30)
    cases.append(("sem token -> 401", r.status_code, 401))

    # 2a) token expirado (assinado com o segredo real, exp no passado) -> 401
    expired = pyjwt.encode(
        {"sub": str(uuid.uuid4()), "type": "access", "role": "gestor_remoto",
         "fresh": False, "jti": str(uuid.uuid4()),
         "iat": datetime.now(timezone.utc) - timedelta(hours=2),
         "nbf": datetime.now(timezone.utc) - timedelta(hours=2),
         "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
        JWT_SECRET, algorithm="HS256")
    r = requests.get(f"{BASE}/api/scans/", headers=auth(expired), timeout=30)
    cases.append(("token expirado -> 401", r.status_code, 401))

    # 2b) token com assinatura invalida -> 401
    invalid = pyjwt.encode(
        {"sub": str(uuid.uuid4()), "type": "access", "role": "gestor_remoto",
         "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "segredo-errado", algorithm="HS256")
    r = requests.get(f"{BASE}/api/scans/", headers=auth(invalid), timeout=30)
    cases.append(("token invalido -> 401", r.status_code, 401))

    # 3) gestor_local em rota exclusiva de gestor_remoto -> 403
    reg = requests.post(f"{BASE}/api/auth/register", headers=auth(token_remoto),
                        json={"name": "TM07 Gestor Local", "email": LOCAL_USER_EMAIL,
                              "password": "senhalocal123", "role": "gestor_local"},
                        timeout=30)
    assert reg.status_code in (201, 400), reg.text  # 400 = ja existe
    token_local = login(LOCAL_USER_EMAIL, "senhalocal123")
    r = requests.delete(f"{BASE}/api/scans/{uuid.uuid4()}", headers=auth(token_local), timeout=30)
    cases.append(("gestor_local em DELETE /scans -> 403", r.status_code, 403))

    # 4) papel correto -> 200 / 201
    r = requests.get(f"{BASE}/api/scans/", headers=auth(token_remoto), timeout=30)
    cases.append(("gestor_remoto GET /scans -> 200", r.status_code, 200))
    r = requests.post(f"{BASE}/api/scans/", headers=auth(token_remoto),
                      json={"id_drone": DRONE_ID, "placa": "TM7T001", "match": False},
                      timeout=30)
    cases.append(("gestor_remoto POST /scans -> 201", r.status_code, 201))
    if r.status_code == 201:
        CREATED_SCAN_IDS.append(r.json()["scan"]["id"])

    ok = sum(1 for _, got, exp in cases if got == exp)
    RESULTS["TM-07"] = {
        "casos": [{"caso": c, "obtido": got, "esperado": exp, "ok": got == exp}
                  for c, got, exp in cases],
        "acertos": ok, "total": len(cases),
        "aprovado": ok == len(cases),
    }


# ───────────────────────── TM-02: registro temporal e zona ─────────────────────────
def tm02():
    sids = []
    post_times = []
    for i in range(1, 6):
        t_post = datetime.now(timezone.utc)
        r = requests.post(f"{BASE}/api/scans/", headers=auth(token_remoto),
                          json={"id_drone": DRONE_ID, "placa": f"TM2T00{i}", "match": False},
                          timeout=30)
        assert r.status_code == 201, r.text
        sids.append(r.json()["scan"]["id"])
        post_times.append(t_post)
    CREATED_SCAN_IDS.extend(sids)

    checks = []
    with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        for sid, t_post in zip(sids, post_times):
            # via API
            r = requests.get(f"{BASE}/api/scans/{sid}", headers=auth(token_remoto), timeout=30)
            api_ok = r.status_code == 200 and r.json().get("horario_scan")
            # via banco: timestamp + vinculo com operacao/zona
            cur.execute("""
                SELECT s.horario_scan, o.id AS operacao_id, o.name, o.localizacao, o.status
                FROM scans s
                JOIN drones d ON d.id = s.id_drone
                JOIN operacoes o ON o.id = d.operacao_id
                WHERE s.id = %s
            """, (sid,))
            row = cur.fetchone()
            ts = row["horario_scan"].replace(tzinfo=timezone.utc) if row and row["horario_scan"] else None
            delta = abs((ts - t_post).total_seconds()) if ts else None
            checks.append({
                "scan_id": sid,
                "timestamp_presente": bool(ts) and bool(api_ok),
                "vinculo_operacao": bool(row and row["operacao_id"] and row["status"] == "ativa"),
                "zona": row["localizacao"] if row else None,
                "delta_segundos": round(delta, 2) if delta is not None else None,
                "coerente": delta is not None and delta < 10,
            })

    ok = sum(1 for c in checks
             if c["timestamp_presente"] and c["vinculo_operacao"] and c["coerente"])
    RESULTS["TM-02"] = {
        "scans": checks, "conformes": ok, "total": len(checks),
        "percentual": round(ok / len(checks) * 100, 1),
        "aprovado": ok == len(checks),
    }


# ───────────────────────── TM-03: correspondencia base de sinistros ─────────────────────────
def tm03():
    os.environ["DEFAULT_DRONE_ID"] = DRONE_ID
    import database.local_detections as local_detections
    import database.supabase_matcher as supabase_matcher
    supabase_matcher.DEFAULT_DRONE_ID = DRONE_ID

    # insere manualmente 5 placas de teste na base de sinistros (procedimento do TM-03)
    roubadas = [f"TM3R00{i}" for i in range(1, 6)]
    with db() as conn, conn.cursor() as cur:
        for placa in roubadas:
            cur.execute(
                "INSERT INTO veiculos (id, placa, modelo, cor, roubado, data_roubo) "
                "VALUES (%s, %s, %s, %s, TRUE, NOW()) ON CONFLICT (placa) DO NOTHING",
                (str(uuid.uuid4()), placa, "Veiculo Teste TM-03", "Teste"))
        conn.commit()
    CREATED_PLACAS.extend(roubadas)
    nao_cadastradas = [f"ZZT9X{i:02d}" for i in range(1, 6)]
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT placa FROM veiculos WHERE placa = ANY(%s)", (nao_cadastradas,))
        assert not cur.fetchall(), "placa de teste ja cadastrada"

    # SQLite temporario com 10 deteccoes pendentes
    tmp_db = Path(tempfile.gettempdir()) / f"tm03_{uuid.uuid4().hex}.db"
    local_detections.SQLITE_DB_PATH = tmp_db
    sconn = sqlite3.connect(tmp_db)
    sconn.execute("""CREATE TABLE plate_frames (
        id INTEGER PRIMARY KEY AUTOINCREMENT, plate TEXT, plate_format TEXT,
        confidence REAL, bbox TEXT, frame_blob BLOB, status TEXT, created_at TEXT)""")
    for placa in roubadas + nao_cadastradas:
        sconn.execute(
            "INSERT INTO plate_frames (plate, plate_format, confidence, bbox, frame_blob, status, created_at) "
            "VALUES (?, 'mercosul', 0.9, '[0,0,10,10]', ?, 'pending', ?)",
            (placa, b"\xff\xd8fakejpg", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    sconn.commit()
    sconn.close()

    supabase_matcher.process_pending_detections(limit=10)

    casos = []
    with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        for placa, esperado in [(p, True) for p in roubadas] + [(p, False) for p in nao_cadastradas]:
            cur.execute("""SELECT id, match FROM scans
                           WHERE placa = %s AND id_drone = %s
                           ORDER BY horario_scan DESC LIMIT 1""", (placa, DRONE_ID))
            row = cur.fetchone()
            obtido = row["match"] if row else None
            if row:
                CREATED_SCAN_IDS.append(str(row["id"]))
            casos.append({"placa": placa, "esperado": esperado, "obtido": obtido,
                          "ok": obtido == esperado})
    tmp_db.unlink(missing_ok=True)

    ok = sum(1 for c in casos if c["ok"])
    RESULTS["TM-03"] = {
        "casos": casos, "acertos": ok, "total": len(casos),
        "percentual": round(ok / len(casos) * 100, 1),
        "aprovado": ok == len(casos),
    }


# ───────────────────────── TM-05: latencia de alerta critico ─────────────────────────
def tm05():
    def poll(url, sid, t0, limite=10):
        while time.perf_counter() - t0 < limite:
            g = requests.get(url, headers=auth(token_remoto), timeout=30)
            if any(s["id"] == sid for s in g.json().get("scans", [])):
                return True, time.perf_counter() - t0
            time.sleep(0.2)
        return False, time.perf_counter() - t0

    latencias = []
    for i in range(1, 6):
        placa = f"TM5T00{i}"
        CREATED_PLACAS.append(placa)

        # etapa 1: match criado -> alerta disponivel na API (lista de scans com match)
        t0 = time.perf_counter()
        r = requests.post(f"{BASE}/api/scans/", headers=auth(token_remoto),
                          json={"id_drone": DRONE_ID, "placa": placa, "match": True,
                                "modelo": "Veiculo Teste TM-05", "cor": "Teste"},
                          timeout=30)
        assert r.status_code == 201, r.text
        sid = r.json()["scan"]["id"]
        CREATED_SCAN_IDS.append(sid)
        ok1, lat1 = poll(f"{BASE}/api/scans/?match=true&per_page=100", sid, t0)

        # etapa 2: aprovacao humana -> publicado em /scans/matches (consumido pelo frontend)
        t1 = time.perf_counter()
        p = requests.patch(f"{BASE}/api/scans/{sid}/validar", headers=auth(token_remoto),
                           json={"status_validacao": "aprovado"}, timeout=30)
        assert p.status_code == 200, p.text
        ok2, lat2 = poll(f"{BASE}/api/scans/matches?per_page=100", sid, t1)

        latencias.append({"placa": placa,
                          "alerta_disponivel_s": round(lat1, 3), "alerta_ok": ok1,
                          "publicado_matches_s": round(lat2, 3), "matches_ok": ok2})

    v1 = [l["alerta_disponivel_s"] for l in latencias]
    v2 = [l["publicado_matches_s"] for l in latencias]
    RESULTS["TM-05"] = {
        "medicoes": latencias,
        "alerta_media_s": round(sum(v1) / len(v1), 3), "alerta_max_s": max(v1),
        "pos_aprovacao_media_s": round(sum(v2) / len(v2), 3), "pos_aprovacao_max_s": max(v2),
        "obs": "GET /api/scans/matches filtra status_validacao='aprovado'; "
               "scan recem-criado (pendente) nao aparece sem validacao humana",
        "aprovado": all(l["alerta_ok"] and l["alerta_disponivel_s"] < 2
                        and l["matches_ok"] and l["publicado_matches_s"] < 2
                        for l in latencias),
    }


# ───────────────────────── limpeza ─────────────────────────
def cleanup():
    with db() as conn, conn.cursor() as cur:
        if CREATED_SCAN_IDS:
            cur.execute("DELETE FROM scans WHERE id = ANY(%s::uuid[])", (CREATED_SCAN_IDS,))
        if CREATED_PLACAS:
            cur.execute("DELETE FROM veiculos WHERE placa = ANY(%s)", (CREATED_PLACAS,))
        cur.execute("DELETE FROM users WHERE email = %s", (LOCAL_USER_EMAIL,))
        conn.commit()


selecionados = sys.argv[1:] or ["tm07", "tm02", "tm03", "tm05"]
try:
    for test in (tm07, tm02, tm03, tm05):
        if test.__name__ not in selecionados:
            continue
        try:
            test()
        except Exception as e:
            RESULTS[test.__name__.upper().replace("TM0", "TM-0")] = {"erro": repr(e)}
finally:
    cleanup()

print(json.dumps(RESULTS, indent=2, ensure_ascii=False, default=str))
