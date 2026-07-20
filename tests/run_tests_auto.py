# -*- coding: utf-8 -*-
"""
Execucao automatizada dos testes originalmente manuais do relatorio de testes
(docs/docs/sprint-4/relatorio-testes.md), com procedimentos adaptados para
execucao sem avaliadores humanos e sem o drone fisico:

  dataset - gera 50 imagens sinteticas de placas BR com ground truth
  tv01    - qualidade de imagem via metricas objetivas (OpenCV)
  tv02    - fluxo da Central de Alertas simulado via API (tarefas cronometradas)
  tv03    - deteccao de drone desconectado via telemetria simulada
  tm01    - acuracia do pipeline YOLO26 + EasyOCR sobre o dataset sintetico
  tm04    - latencia end-to-end com imagens estaticas (CV -> SQLite -> matcher -> scan)
  tm06    - latencia de streaming MJPEG com timestamp embutido nos frames

Uso: python run_tests_auto.py [dataset tv01 tv02 tv03 tm01 tm04 tm06]
Resultados gravados em resultados_testes_auto.json.
"""
import json
import os
import random
import re
import sqlite3
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2
import numpy as np
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))          # p/ src.visao_computacional...
sys.path.insert(0, str(ROOT / "src"))  # p/ local_detections / supabase_matcher
load_dotenv(ROOT / ".env")

BASE = "http://127.0.0.1:5000"
DATABASE_URL = os.environ["DATABASE_URL"]
DATASET_DIR = ROOT / "dataset_placas"
GT_PATH = DATASET_DIR / "ground_truth.json"
RESULTS_PATH = ROOT / "resultados_testes_auto.json"

random.seed(42)
np.random.seed(42)

RESULTS = {}
CREATED_SCAN_IDS = []
CREATED_PLACAS = []
CREATED_DRONE_IDS = []
TEST_USER_EMAILS = []


def db():
    return psycopg2.connect(DATABASE_URL)


def login(email, password):
    r = requests.post(f"{BASE}/api/auth/login",
                      json={"email": email, "password": password}, timeout=30)
    r.raise_for_status()
    return r.json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def get_token_remoto():
    return login("gestorremoto@gestorremoto.com", "gestorremoto")


def get_drone_ativo(token):
    with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT d.id AS drone_id, o.id AS operacao_id, o.localizacao
            FROM drones d JOIN operacoes o ON o.id = d.operacao_id
            WHERE o.status = 'ativa' LIMIT 1
        """)
        return cur.fetchone()


# ═════════════════════════ geracao do dataset sintetico ═════════════════════════

LETRAS = "ABCDEFGHJKLMNPRSTUVWXYZ"  # sem I/O/Q para reduzir ambiguidade proposital
DIGITOS = "0123456789"


def gerar_texto_placa(formato):
    if formato == "BR_OLD":          # LLLNNNN
        return "".join(random.choices(LETRAS, k=3)) + "".join(random.choices(DIGITOS, k=4))
    return ("".join(random.choices(LETRAS, k=3)) + random.choice(DIGITOS)
            + random.choice(LETRAS) + "".join(random.choices(DIGITOS, k=2)))  # LLLNLNN


def render_placa(texto, formato):
    """Renderiza uma placa brasileira sintetica (520x150 px, estilo simplificado)."""
    w, h = 520, 150
    img = np.full((h, w, 3), 245, dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (w - 1, h - 1), (30, 30, 30), 8)
    if formato == "BR_MERCOSUL":
        cv2.rectangle(img, (4, 4), (w - 5, 34), (160, 80, 0), -1)  # faixa azul (BGR)
        cv2.putText(img, "BRASIL", (200, 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 255), 2, cv2.LINE_AA)
        y_text = 118
    else:
        cv2.rectangle(img, (4, 4), (w - 5, 30), (200, 200, 200), -1)
        y_text = 115
    # texto espacado manualmente para parecer placa real
    x = 30
    for ch in texto:
        cv2.putText(img, ch, (x, y_text), cv2.FONT_HERSHEY_DUPLEX,
                    2.6, (10, 10, 10), 9, cv2.LINE_AA)
        x += 68
    return img


def compor_cena(placa_img, dist, luz, angulo):
    """Insere a placa numa cena sintetica variando distancia, iluminacao e angulo."""
    H, W = 720, 1280
    bg = np.full((H, W, 3), 0, dtype=np.uint8)
    bg[:] = (random.randint(60, 90), random.randint(60, 90), random.randint(60, 90))
    # "carro": retangulo mais escuro atras da placa + para-choque
    cv2.rectangle(bg, (W // 2 - 350, 130), (W // 2 + 350, 620),
                  (random.randint(25, 50),) * 3, -1)
    cv2.rectangle(bg, (W // 2 - 350, 520), (W // 2 + 350, 620), (20, 20, 20), -1)

    target_w = {"perto": 420, "media": 260, "longe": 150}[dist]
    scale = target_w / placa_img.shape[1]
    placa = cv2.resize(placa_img, None, fx=scale, fy=scale,
                       interpolation=cv2.INTER_AREA)
    ph, pw = placa.shape[:2]

    # rotacao com mascara para overlay
    diag = int(np.hypot(ph, pw)) + 4
    canvas = np.zeros((diag, diag, 3), dtype=np.uint8)
    mask = np.zeros((diag, diag), dtype=np.uint8)
    oy, ox = (diag - ph) // 2, (diag - pw) // 2
    canvas[oy:oy + ph, ox:ox + pw] = placa
    mask[oy:oy + ph, ox:ox + pw] = 255
    M = cv2.getRotationMatrix2D((diag / 2, diag / 2), angulo, 1.0)
    canvas = cv2.warpAffine(canvas, M, (diag, diag))
    mask = cv2.warpAffine(mask, M, (diag, diag))

    px = W // 2 - diag // 2 + random.randint(-60, 60)
    py = 460 - diag // 2 + random.randint(-30, 30)
    roi = bg[py:py + diag, px:px + diag]
    roi[mask > 0] = canvas[mask > 0]

    # bbox da placa na cena (a partir da mascara)
    ys, xs = np.where(mask > 0)
    bbox = [int(px + xs.min()), int(py + ys.min()),
            int(px + xs.max()), int(py + ys.max())]

    # iluminacao
    alpha, beta = {"normal": (1.0, 0), "escura": (0.55, -35), "clara": (1.35, 45)}[luz]
    bg = cv2.convertScaleAbs(bg, alpha=alpha, beta=beta)
    # ruido leve de sensor
    noise = np.random.normal(0, 6, bg.shape).astype(np.int16)
    bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    if dist == "longe":
        bg = cv2.GaussianBlur(bg, (3, 3), 0)
    return bg, bbox


def gerar_dataset(n=50):
    DATASET_DIR.mkdir(exist_ok=True)
    distancias = ["perto", "media", "longe"]
    luzes = ["normal", "escura", "clara"]
    angulos = [0, 0, 5, -5, 8]
    gt = []
    for i in range(n):
        formato = "BR_MERCOSUL" if i % 2 == 0 else "BR_OLD"
        texto = gerar_texto_placa(formato)
        dist = distancias[i % 3]
        luz = luzes[(i // 3) % 3]
        ang = angulos[i % 5]
        cena, bbox = compor_cena(render_placa(texto, formato), dist, luz, ang)
        nome = f"placa_{i:03d}.jpg"
        cv2.imwrite(str(DATASET_DIR / nome), cena, [cv2.IMWRITE_JPEG_QUALITY, 92])
        gt.append({"arquivo": nome, "placa": texto, "formato": formato,
                   "distancia": dist, "iluminacao": luz, "angulo": ang, "bbox": bbox})
    GT_PATH.write_text(json.dumps(gt, indent=2, ensure_ascii=False), encoding="utf-8")
    RESULTS["dataset"] = {"imagens": n, "dir": str(DATASET_DIR)}
    print(f"dataset: {n} imagens geradas em {DATASET_DIR}")


def carregar_gt():
    return json.loads(GT_PATH.read_text(encoding="utf-8"))


# ═════════════════════════ TV-01: qualidade de imagem ═════════════════════════

def tv01():
    """Substitui os avaliadores humanos por metricas objetivas de qualidade
    de imagem (OpenCV): nitidez (variancia do Laplaciano), brilho medio,
    contraste (desvio padrao) e resolucao minima."""
    gt = carregar_gt()
    avaliacoes = []
    for item in gt:
        img = cv2.imread(str(DATASET_DIR / item["arquivo"]))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x1, y1, x2, y2 = item["bbox"]
        # metricas computadas na regiao da placa: e o que da valor de evidencia
        crop = gray[max(0, y1):y2, max(0, x1):x2]
        nitidez = cv2.Laplacian(crop, cv2.CV_64F).var()
        brilho = float(crop.mean())
        contraste = float(crop.std())
        res_ok = img.shape[1] >= 640 and img.shape[0] >= 480

        if nitidez >= 100 and 60 <= brilho <= 200 and contraste >= 40 and res_ok:
            classe = "adequada"
        elif nitidez >= 50 and 40 <= brilho <= 220 and contraste >= 25 and res_ok:
            classe = "aceitavel"
        else:
            classe = "inadequada"
        avaliacoes.append({"arquivo": item["arquivo"], "distancia": item["distancia"],
                           "iluminacao": item["iluminacao"],
                           "nitidez": round(nitidez, 1), "brilho": round(brilho, 1),
                           "contraste": round(contraste, 1), "classe": classe})

    aproveitaveis = sum(1 for a in avaliacoes if a["classe"] in ("adequada", "aceitavel"))
    pct = round(aproveitaveis / len(avaliacoes) * 100, 1)
    por_classe = {c: sum(1 for a in avaliacoes if a["classe"] == c)
                  for c in ("adequada", "aceitavel", "inadequada")}
    RESULTS["TV-01"] = {
        "total_imagens": len(avaliacoes), "por_classe": por_classe,
        "percentual_aproveitavel": pct,
        "amostra": avaliacoes[:10],
        "criterio": ">= 80% adequada ou aceitavel",
        "aprovado": pct >= 80,
    }
    print(f"TV-01: {pct}% aproveitaveis {por_classe}")


# ═════════════════════════ TV-02: fluxo da Central de Alertas ═════════════════════════

def tv02():
    """Substitui o avaliador humano por um cliente automatizado que executa,
    via API (mesmos endpoints do frontend), as tarefas do operador na Central
    de Alertas, cronometrando cada uma."""
    token_remoto = get_token_remoto()
    drone = get_drone_ativo(token_remoto)

    # usuario operador (gestor_local), como no pre-requisito do teste
    email = "tv02.operador@teste-sprint4.com"
    TEST_USER_EMAILS.append(email)
    requests.post(f"{BASE}/api/auth/register", headers=auth(token_remoto),
                  json={"name": "TV02 Operador", "email": email,
                        "password": "operador123", "role": "gestor_local"}, timeout=30)

    # dois alertas pendentes com match=true e imagem
    sids = []
    for i in (1, 2):
        placa = f"TV2T00{i}"
        CREATED_PLACAS.append(placa)
        r = requests.post(f"{BASE}/api/scans/", headers=auth(token_remoto),
                          json={"id_drone": drone["drone_id"], "placa": placa,
                                "match": True, "modelo": "Teste TV-02", "cor": "Teste",
                                "imagem_url": "uploaded_frames/teste/tv02.jpg"},
                          timeout=30)
        assert r.status_code == 201, r.text
        sids.append(r.json()["scan"]["id"])
    CREATED_SCAN_IDS.extend(sids)

    tarefas = []
    t_inicio = time.perf_counter()

    def tarefa(nome, fn):
        t0 = time.perf_counter()
        ok, detalhe = fn()
        tarefas.append({"tarefa": nome, "duracao_s": round(time.perf_counter() - t0, 3),
                        "sucesso": bool(ok), "detalhe": detalhe})
        return ok

    # T1: autenticar como operador
    token_op = {}
    tarefa("login do operador", lambda: (
        token_op.update(t=login(email, "operador123")) or True, "token emitido"))

    # T2: acessar a Central de Alertas (fila de pendentes)
    pendentes = {}
    def t2():
        r = requests.get(f"{BASE}/api/scans/pendentes?per_page=100",
                         headers=auth(token_op["t"]), timeout=30)
        pendentes["lista"] = r.json().get("scans", [])
        return r.status_code == 200, f"{len(pendentes['lista'])} scans pendentes"
    tarefa("acessar Central de Alertas (GET /scans/pendentes)", t2)

    # T3: localizar os alertas pendentes com match
    def t3():
        achados = [s for s in pendentes["lista"] if s["id"] in sids]
        return len(achados) == 2, f"{len(achados)}/2 alertas de teste localizados"
    tarefa("localizar alertas pendentes", t3)

    # T4: visualizar informacoes do alerta (placa, zona, data/hora, imagem)
    def t4():
        r = requests.get(f"{BASE}/api/scans/{sids[0]}", headers=auth(token_op["t"]), timeout=30)
        scan = r.json()
        rd = requests.get(f"{BASE}/api/drones/{scan['id_drone']}",
                          headers=auth(token_op["t"]), timeout=30).json()
        ro = requests.get(f"{BASE}/api/operacoes/{rd['operacao_id']}",
                          headers=auth(token_op["t"]), timeout=30).json()
        campos = {"placa": scan.get("placa"), "data_hora": scan.get("horario_scan"),
                  "imagem": scan.get("imagem_url"), "zona": ro.get("localizacao")}
        faltando = [k for k, v in campos.items() if not v]
        return not faltando, {"campos": campos, "faltando": faltando}
    tarefa("visualizar informacoes do alerta", t4)

    # T5/T6: aprovar um alerta e rejeitar o outro
    def validar(sid, status):
        def fn():
            r = requests.patch(f"{BASE}/api/scans/{sid}/validar",
                               headers=auth(token_op["t"]),
                               json={"status_validacao": status}, timeout=30)
            return r.status_code == 200, f"HTTP {r.status_code}"
        return fn
    tarefa("aprovar alerta 1", validar(sids[0], "aprovado"))
    tarefa("rejeitar alerta 2", validar(sids[1], "rejeitado"))

    total = round(time.perf_counter() - t_inicio, 3)
    todas_ok = all(t["sucesso"] for t in tarefas)
    RESULTS["TV-02"] = {
        "tarefas": tarefas, "tempo_total_s": total,
        "criterio": "fluxo completo em ate 180 s com todas as tarefas concluidas "
                    "e informacoes completas (substitui questionario de satisfacao)",
        "aprovado": todas_ok and total <= 180,
    }
    print(f"TV-02: fluxo completo em {total}s, sucesso={todas_ok}")


# ═════════════════════════ TV-03: conectividade dos drones ═════════════════════════

def tv03():
    """Substitui o avaliador humano por um monitor automatizado que consome os
    mesmos dados da tela OperationsManager (GET /api/drones) e tenta identificar
    a desconexao de um drone cuja telemetria foi interrompida."""
    token = get_token_remoto()
    drone_base = get_drone_ativo(token)

    r = requests.post(f"{BASE}/api/drones/", headers=auth(token),
                      json={"operacao_id": drone_base["operacao_id"],
                            "nome": "TV03-Drone-Teste", "status_voo": "em_voo",
                            "bateria": 90, "conectividade": "WiFi",
                            "latitude": -23.55, "longitude": -46.63}, timeout=30)
    assert r.status_code == 201, r.text
    did = r.json()["drone"]["id"]
    CREATED_DRONE_IDS.append(did)

    parar = threading.Event()

    def telemetria():
        lat = -23.55
        while not parar.is_set():
            lat += 0.0001
            requests.patch(f"{BASE}/api/drones/{did}/localizacao", headers=auth(token),
                           json={"latitude": lat, "longitude": -46.63,
                                 "bateria": random.randint(70, 90)}, timeout=30)
            parar.wait(1.0)

    def snapshot():
        return requests.get(f"{BASE}/api/drones/{did}", headers=auth(token), timeout=30).json()

    th = threading.Thread(target=telemetria, daemon=True)
    th.start()
    time.sleep(5)
    visto_conectado = snapshot()

    # Cenario A: telemetria interrompida abruptamente (drone "morre" sem avisar)
    parar.set()
    th.join()
    t0 = time.perf_counter()
    detectado_a, tempo_a = False, None
    anterior = snapshot()
    while time.perf_counter() - t0 < 60:
        atual = snapshot()
        # unico sinal de desconexao que a API poderia expor: mudanca de status
        if atual.get("status_voo") in ("offline",):
            detectado_a, tempo_a = True, round(time.perf_counter() - t0, 1)
            break
        anterior = atual
        time.sleep(2)

    # Cenario B: o cliente do drone reporta a queda antes de cair
    # (unico mecanismo disponivel hoje: PATCH explicito de status)
    requests.patch(f"{BASE}/api/drones/{did}", headers=auth(token),
                   json={"status_voo": "offline"}, timeout=30)
    t0 = time.perf_counter()
    detectado_b, tempo_b = False, None
    while time.perf_counter() - t0 < 30:
        if snapshot().get("status_voo") == "offline":
            detectado_b, tempo_b = True, round(time.perf_counter() - t0, 1)
            break
        time.sleep(2)

    RESULTS["TV-03"] = {
        "estado_conectado_observado": {k: visto_conectado.get(k)
                                       for k in ("status_voo", "bateria", "conectividade")},
        "cenario_A_telemetria_interrompida": {
            "detectado_em_60s": detectado_a, "tempo_s": tempo_a,
            "achado": "o backend nao registra timestamp de telemetria (last_seen) nem "
                      "marca drones como offline automaticamente; sem acao do proprio "
                      "drone, a interface continua exibindo o ultimo estado conhecido",
        },
        "cenario_B_drone_reporta_offline": {
            "detectado_em_30s": detectado_b, "tempo_s": tempo_b,
        },
        "criterio": "estado de desconexao identificavel pelos dados da interface em ate 30 s",
        "aprovado": detectado_a,  # criterio do RNF-05: deteccao apenas pela telemetria
    }
    print(f"TV-03: cenario A detectado={detectado_a}, cenario B detectado={detectado_b} ({tempo_b}s)")


# ═════════════════════════ TM-01: acuracia YOLO + OCR ═════════════════════════

def tm01():
    """Executa o pipeline real (YOLO26 + EasyOCR, via process_frame) sobre o
    dataset sintetico com ground truth; mede tambem a acuracia isolada do
    estagio de OCR usando o recorte exato da placa."""
    import src.visao_computacional.yolo26.plate_recognizer as pr

    gt = carregar_gt()
    casos = []
    for item in gt:
        img = cv2.imread(str(DATASET_DIR / item["arquivo"]))
        pr.plate_history.clear()
        pr.plate_final.clear()

        _, frame_results = pr.process_frame(img.copy())
        validos = [r for r in frame_results if r.get("plate")]
        pipeline_pred = max(validos, key=lambda r: r["confidence"])["plate"] if validos else ""
        detectou = bool(frame_results)

        x1, y1, x2, y2 = item["bbox"]
        m = 4
        crop = img[max(0, y1 - m):y2 + m, max(0, x1 - m):x2 + m]
        ocr_pred = pr.recognize_plate(crop)["plate"]

        casos.append({"arquivo": item["arquivo"], "gt": item["placa"],
                      "distancia": item["distancia"], "iluminacao": item["iluminacao"],
                      "yolo_detectou": detectou,
                      "pipeline_pred": pipeline_pred,
                      "pipeline_ok": pipeline_pred == item["placa"],
                      "ocr_pred": ocr_pred, "ocr_ok": ocr_pred == item["placa"]})

    n = len(casos)
    det = sum(1 for c in casos if c["yolo_detectou"])
    pipe_ok = sum(1 for c in casos if c["pipeline_ok"])
    ocr_ok = sum(1 for c in casos if c["ocr_ok"])
    RESULTS["TM-01"] = {
        "total_imagens": n,
        "deteccao_yolo_pct": round(det / n * 100, 1),
        "acuracia_pipeline_pct": round(pipe_ok / n * 100, 1),
        "acuracia_ocr_isolado_pct": round(ocr_ok / n * 100, 1),
        "amostra": casos[:10],
        "criterio": "acuracia >= 80% (RNF-04)",
        "obs": "dataset sintetico renderizado; o YOLO26 foi treinado com placas reais, "
               "entao a etapa de deteccao pode subperformar em imagens sinteticas",
        "aprovado_pipeline": pipe_ok / n >= 0.8,
        "aprovado_ocr": ocr_ok / n >= 0.8,
    }
    print(f"TM-01: deteccao {det}/{n}, pipeline {pipe_ok}/{n}, ocr {ocr_ok}/{n}")


# ═════════════════════════ TM-04: latencia end-to-end ═════════════════════════

def tm04():
    """Substitui a captura do drone por imagens estaticas (modo previsto no
    proprio relatorio) e mede t0 (leitura do frame) -> YOLO+OCR -> SQLite ->
    supabase_matcher -> t1 (scan visivel no banco)."""
    import src.visao_computacional.yolo26.plate_recognizer as pr
    import database.local_detections as local_detections
    import database.supabase_matcher as supabase_matcher

    token = get_token_remoto()
    drone = get_drone_ativo(token)
    supabase_matcher.DEFAULT_DRONE_ID = drone["drone_id"]

    gt = carregar_gt()
    # metade das placas cadastradas como roubadas (caminho com match e gravacao de frame)
    selecao = gt[:10]
    cadastradas = [item["placa"] for item in selecao[:5]]
    CREATED_PLACAS.extend(cadastradas)
    with db() as conn, conn.cursor() as cur:
        for placa in cadastradas:
            cur.execute(
                "INSERT INTO veiculos (id, placa, modelo, cor, roubado, data_roubo) "
                "VALUES (%s, %s, 'Teste TM-04', 'Teste', TRUE, NOW()) "
                "ON CONFLICT (placa) DO NOTHING", (str(uuid.uuid4()), placa))
        conn.commit()

    tmp_db = Path(tempfile.gettempdir()) / f"tm04_{uuid.uuid4().hex}.db"
    local_detections.SQLITE_DB_PATH = tmp_db
    sconn = sqlite3.connect(tmp_db)
    sconn.execute("""CREATE TABLE plate_frames (
        id INTEGER PRIMARY KEY AUTOINCREMENT, plate TEXT, plate_format TEXT,
        confidence REAL, bbox TEXT, frame_blob BLOB, status TEXT, created_at TEXT)""")
    sconn.commit()

    medicoes = []
    for item in selecao:
        path = DATASET_DIR / item["arquivo"]
        pr.plate_history.clear()
        pr.plate_final.clear()

        t0 = time.perf_counter()
        frame = cv2.imread(str(path))                      # captura (estatica)
        _, frame_results = pr.process_frame(frame.copy())  # YOLO + OCR
        t_cv = time.perf_counter()

        validos = [r for r in frame_results if r.get("plate")]
        placa_lida = (max(validos, key=lambda r: r["confidence"])["plate"]
                      if validos else item["placa"])  # fallback p/ medir o restante
        leitura_real = bool(validos)

        ok_jpg, blob = cv2.imencode(".jpg", frame)
        cur = sconn.execute(
            "INSERT INTO plate_frames (plate, plate_format, confidence, bbox, frame_blob, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (placa_lida, item["formato"], 0.9, "[0,0,0,0]",
             blob.tobytes() if ok_jpg else b"", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        sconn.commit()
        supabase_matcher.process_pending_detections(limit=1)  # matcher + insert scan

        # confirma o scan no banco
        scan_id = None
        with db() as conn, conn.cursor() as pcur:
            while time.perf_counter() - t0 < 15:
                pcur.execute("""SELECT id FROM scans WHERE placa = %s AND id_drone = %s
                                ORDER BY horario_scan DESC LIMIT 1""",
                             (placa_lida, drone["drone_id"]))
                row = pcur.fetchone()
                if row:
                    scan_id = str(row[0])
                    break
                time.sleep(0.1)
        t1 = time.perf_counter()
        if scan_id:
            CREATED_SCAN_IDS.append(scan_id)
        medicoes.append({"arquivo": item["arquivo"], "placa": placa_lida,
                         "leitura_cv_real": leitura_real,
                         "tempo_cv_s": round(t_cv - t0, 3),
                         "tempo_total_s": round(t1 - t0, 3),
                         "scan_criado": scan_id is not None})

    sconn.close()
    tmp_db.unlink(missing_ok=True)

    tempos = sorted(m["tempo_total_s"] for m in medicoes)
    mediana = tempos[len(tempos) // 2] if len(tempos) % 2 else \
        round((tempos[len(tempos) // 2 - 1] + tempos[len(tempos) // 2]) / 2, 3)
    RESULTS["TM-04"] = {
        "medicoes": medicoes,
        "mediana_s": mediana, "media_s": round(sum(tempos) / len(tempos), 3),
        "max_s": max(tempos), "min_s": min(tempos),
        "criterio": "mediana <= 5 s; nenhum caso > 8 s",
        "obs": "captura do drone substituida por leitura de imagem estatica "
               "(cv2.imread), conforme modo de teste previsto no relatorio",
        "aprovado": mediana <= 5 and max(tempos) <= 8 and all(m["scan_criado"] for m in medicoes),
    }
    print(f"TM-04: mediana {mediana}s, max {max(tempos)}s")


# ═════════════════════════ TM-06: latencia de streaming ═════════════════════════

STREAM_PORT = 8090
_FRAME_LOCK = threading.Lock()


def _frame_com_timestamp():
    """Frame sintetico com timestamp em ms codificado em 48 blocos binarios
    (robusto a compressao JPEG) + relogio legivel."""
    H, W = 480, 960
    img = np.full((H, W, 3), 30, dtype=np.uint8)
    t_ms = int(time.time() * 1000)
    # conteudo dinamico (forca o encoder a trabalhar como num video real)
    cx = int((t_ms / 30) % W)
    cv2.circle(img, (cx, 300), 60, (0, 180, 255), -1)
    cv2.putText(img, datetime.now().strftime("%H:%M:%S.%f")[:-3], (40, 440),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    for i in range(48):  # bit mais significativo primeiro
        bit = (t_ms >> (47 - i)) & 1
        x = 10 + i * 19
        cv2.rectangle(img, (x, 10), (x + 16, 42), (255, 255, 255) if bit else (0, 0, 0), -1)
    return img


def _decodificar_timestamp(frame):
    t_ms = 0
    for i in range(48):
        x = 10 + i * 19
        bloco = frame[14:38, x + 2:x + 14]
        bit = 1 if bloco.mean() > 127 else 0
        t_ms = (t_ms << 1) | bit
    return t_ms


class _MJPEGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()
        try:
            while True:
                ok, jpg = cv2.imencode(".jpg", _frame_com_timestamp(),
                                       [cv2.IMWRITE_JPEG_QUALITY, 90])
                self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n")
                self.wfile.write(jpg.tobytes())
                self.wfile.write(b"\r\n")
                time.sleep(1 / 30)  # ~30 fps, como o feed do Tello
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def log_message(self, *args):
        pass


def tm06():
    """Substitui o feed UDP do Tello por um servidor MJPEG local emitindo
    frames com timestamp embutido; o consumidor usa o mesmo mecanismo do
    sistema (cv2.VideoCapture + descarte de buffer, como em drone.py)."""
    server = ThreadingHTTPServer(("127.0.0.1", STREAM_PORT), _MJPEGHandler)
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    time.sleep(0.5)

    cap = cv2.VideoCapture(f"http://127.0.0.1:{STREAM_PORT}/", cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    assert cap.isOpened(), "nao foi possivel abrir o stream MJPEG"

    amostras = []
    fim = time.time() + 12
    while time.time() < fim:
        for _ in range(2):   # flush_buffer, como em drone.py
            cap.grab()
        ret, frame = cap.read()
        if not ret:
            continue
        agora_ms = time.time() * 1000
        ts = _decodificar_timestamp(frame)
        lat = (agora_ms - ts) / 1000
        if 0 <= lat < 60:    # descarta decodificacoes corrompidas
            amostras.append(round(lat, 3))
        time.sleep(0.1)

    cap.release()
    server.shutdown()
    server.server_close()

    assert amostras, "nenhuma amostra valida de latencia"
    RESULTS["TM-06"] = {
        "n_amostras": len(amostras),
        "latencia_media_s": round(sum(amostras) / len(amostras), 3),
        "latencia_max_s": max(amostras), "latencia_min_s": min(amostras),
        "criterio": "latencia media < 5 s",
        "obs": "feed do drone substituido por servidor MJPEG local a 30 fps com "
               "timestamp binario embutido nos frames; consumo via cv2.VideoCapture "
               "com descarte de buffer identico ao drone.py",
        "aprovado": (sum(amostras) / len(amostras)) < 5,
    }
    print(f"TM-06: media {RESULTS['TM-06']['latencia_media_s']}s "
          f"({len(amostras)} amostras)")


# ═════════════════════════ limpeza ═════════════════════════

def cleanup():
    try:
        token = get_token_remoto()
        for did in CREATED_DRONE_IDS:
            requests.delete(f"{BASE}/api/drones/{did}", headers=auth(token), timeout=30)
    except Exception as e:
        print(f"cleanup drones: {e}")
    with db() as conn, conn.cursor() as cur:
        if CREATED_SCAN_IDS:
            cur.execute("DELETE FROM scans WHERE id = ANY(%s::uuid[])", (CREATED_SCAN_IDS,))
        if CREATED_PLACAS:
            cur.execute("DELETE FROM veiculos WHERE placa = ANY(%s)", (CREATED_PLACAS,))
        if TEST_USER_EMAILS:
            cur.execute("DELETE FROM users WHERE email = ANY(%s)", (TEST_USER_EMAILS,))
        conn.commit()


TESTES = {"dataset": gerar_dataset, "tv01": tv01, "tv02": tv02, "tv03": tv03,
          "tm01": tm01, "tm04": tm04, "tm06": tm06}

if __name__ == "__main__":
    selecionados = sys.argv[1:] or list(TESTES)
    try:
        for nome in selecionados:
            try:
                TESTES[nome]()
            except Exception as e:
                RESULTS[nome.upper()] = {"erro": repr(e)}
                print(f"{nome}: ERRO {e!r}")
    finally:
        cleanup()
        existentes = {}
        if RESULTS_PATH.exists():
            existentes = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        existentes.update(RESULTS)
        RESULTS_PATH.write_text(json.dumps(existentes, indent=2, ensure_ascii=False,
                                           default=str), encoding="utf-8")
        print(f"\nresultados gravados em {RESULTS_PATH}")
