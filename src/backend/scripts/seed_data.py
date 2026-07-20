"""
seed_data.py — Popula o banco com dados fictícios para testes.

Uso:
    cd src/backend
    python3 scripts/seed_data.py
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import get_db_connection

# ─────────────────────────────────────────────────────────────────────────────
# Dados fictícios
# ─────────────────────────────────────────────────────────────────────────────

OPERACOES = [
    ("Operação Águia Norte",    "ativa",      "Av. Paulista, 1578 — São Paulo, SP"),
    ("Operação Farol Sul",      "ativa",      "Rua XV de Novembro, 45 — Curitiba, PR"),
    ("Operação Sentinela Leste","pausada",    "Av. Getúlio Vargas, 200 — Belo Horizonte, MG"),
    ("Operação Cobra Oeste",    "encerrada",  "Rua da Consolação, 930 — São Paulo, SP"),
    ("Operação Trovão",         "ativa",      "Av. Atlântica, 500 — Rio de Janeiro, RJ"),
    ("Operação Cruzeiro Delta", "pausada",    "Rua dos Andradas, 1200 — Porto Alegre, RS"),
    ("Operação Horizonte",      "ativa",      "Taguatinga Sul, Quadra 5 — Brasília, DF"),
    ("Operação Névoa Cinzenta", "encerrada",  "Rua 25 de Março, 800 — São Paulo, SP"),
    ("Operação Alfa Zero",      "ativa",      "Av. Beira-Mar Norte, 300 — Florianópolis, SC"),
    ("Operação Bravo Seis",     "pausada",    "Rua das Flores, 555 — Campinas, SP"),
]

NOMES_DRONES = [
    "Falcão-1", "Corvo-2", "Gavião-3", "Águia-4", "Beija-flor-5",
    "Sabiá-6",  "Andorinha-7", "Pardal-8", "Harpia-9", "Tucano-10",
    "Carcará-11","Seriema-12", "Arara-13", "Papagaio-14","Urubu-15",
    "Ema-16",   "Quero-Quero-17","Socó-18","Jabiru-19", "Flamingo-20",
]

STATUS_VOO = ["em_voo", "em_voo", "em_voo", "pousado", "manutencao"]

CONECTIVIDADES = ["4G", "5G", "WiFi", "LoRa", "Satélite"]

PLACAS = [
    "ABC1D23", "XYZ9F87", "MNO3G45", "PQR7H12", "STU2I98",
    "VWX5J34", "ACD8K67", "EFG4L01", "HIJ6M56", "KLM0N89",
    "NOP1O23", "QRS2P45", "TUV3Q78", "WXY4R90", "ZAB5S12",
    "CDE6T34", "FGH7U56", "IJK8V78", "LMN9W90", "OPQ0X12",
    "RST1Y34", "UVW2Z56", "XYZ3A78", "BCD4B90", "EFG5C12",
    "HIJ6D34", "KLM7E56", "NOP8F78", "QRS9G90", "TUV0H12",
]

MODELOS = [
    "Fiat Uno", "VW Gol", "Chevrolet Onix", "Toyota Corolla", "Honda Civic",
    "Ford Ka", "Hyundai HB20", "Renault Kwid", "Jeep Renegade", "Nissan Kicks",
    "Fiat Argo", "VW Polo", "Chevrolet Tracker", "Toyota Hilux", "Ford Ranger",
]

CORES = ["Branco", "Preto", "Prata", "Cinza", "Vermelho", "Azul", "Verde", "Amarelo"]

AREAS_SP = [
    (-23.5505, -46.6333), (-23.5615, -46.6562), (-23.5489, -46.6388),
    (-23.5330, -46.6252), (-23.5785, -46.6518), (-23.5100, -46.6000),
    (-23.6000, -46.7000), (-23.5200, -46.5800), (-23.5700, -46.6100),
    (-23.5450, -46.6450),
]

STATUS_VALIDACAO = ["pendente", "pendente", "aprovado", "rejeitado"]

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def rand_date(days_back=180):
    delta = timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return (datetime.now() - delta).replace(microsecond=0)

def rand_coord(base_lat, base_lon, spread=0.05):
    return (
        round(base_lat + random.uniform(-spread, spread), 8),
        round(base_lon + random.uniform(-spread, spread), 8),
    )

# ─────────────────────────────────────────────────────────────────────────────
# Seed
# ─────────────────────────────────────────────────────────────────────────────

def seed():
    app = create_app()
    with app.app_context():
        conn = get_db_connection()
        cur  = conn.cursor()

        print("🌱 Iniciando seed de dados fictícios...\n")

        # ── Veículos ───────────────────────────────────────────────────────
        print("📌 Inserindo veículos...")
        veiculo_ids = []
        placas_usadas = random.sample(PLACAS, len(PLACAS))
        for i, placa in enumerate(placas_usadas):
            vid   = str(uuid.uuid4())
            modelo = random.choice(MODELOS)
            cor    = random.choice(CORES)
            roubado = random.random() < 0.40          # 40% dos veículos roubados
            data_roubo = rand_date(365) if roubado else rand_date(30)
            cur.execute(
                "INSERT INTO veiculos (id, placa, modelo, cor, roubado, data_roubo) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (placa) DO UPDATE SET "
                "modelo=EXCLUDED.modelo, cor=EXCLUDED.cor, roubado=EXCLUDED.roubado, data_roubo=EXCLUDED.data_roubo RETURNING id",
                (vid, placa, modelo, cor, roubado, data_roubo),
            )
            actual_vid = cur.fetchone()[0]
            veiculo_ids.append((actual_vid, placa, roubado))
        print(f"   ✔ {len(placas_usadas)} veículos inseridos.")

        # ── Operações ──────────────────────────────────────────────────────
        print("📌 Inserindo operações...")
        operacao_ids = []
        for name, status, localizacao in OPERACOES:
            oid = str(uuid.uuid4())
            created_at = rand_date(90)
            cur.execute(
                "INSERT INTO operacoes (id, name, status, localizacao, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                (oid, name, status, localizacao, created_at),
            )
            operacao_ids.append(oid)
        print(f"   ✔ {len(OPERACOES)} operações inseridas.")

        # ── Drones ────────────────────────────────────────────────────────
        print("📌 Inserindo drones...")
        drone_ids = []
        nomes_shuffled = NOMES_DRONES[:]
        random.shuffle(nomes_shuffled)
        for i, oid in enumerate(operacao_ids):
            qtd = random.randint(2, 4)
            for j in range(qtd):
                did  = str(uuid.uuid4())
                nome = f"{random.choice(nomes_shuffled)}-{random.randint(100,999)}"
                bat  = random.randint(5, 100)
                conn_type = random.choice(CONECTIVIDADES)
                sv   = random.choice(STATUS_VOO)
                base = random.choice(AREAS_SP)
                lat, lon = rand_coord(*base)
                cur.execute(
                    "INSERT INTO drones (id, operacao_id, nome, bateria, conectividade, status_voo, latitude, longitude) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (did, oid, nome, bat, conn_type, sv, lat, lon),
                )
                drone_ids.append((did, oid))
        print(f"   ✔ {len(drone_ids)} drones inseridos.")

        # ── Scans ─────────────────────────────────────────────────────────
        print("📌 Inserindo scans...")
        scan_ids = []
        for did, oid in drone_ids:
            qtd_scans = random.randint(3, 12)
            for _ in range(qtd_scans):
                sid   = str(uuid.uuid4())
                veiculo = random.choice(veiculo_ids)
                placa = veiculo[1]
                match = veiculo[2]           # match = True se o veículo é roubado
                base  = random.choice(AREAS_SP)
                lat, lon = rand_coord(*base)
                horario  = rand_date(60)
                status_v = random.choice(STATUS_VALIDACAO)
                imagem_url = "https://www.comparaonline.com.br/blog-statics/br/uploads/2021/09/2019-10-30-placa-mercosul-nova.jpg"
                cur.execute(
                    "INSERT INTO scans (id, id_drone, placa, match, imagem_url, latitude, longitude, horario_scan, status_validacao) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (sid, did, placa, match, imagem_url, lat, lon, horario, status_v),
                )
                scan_ids.append((sid, veiculo[0]))
        print(f"   ✔ {len(scan_ids)} scans inseridos.")

        # ── Veiculos_Scans ────────────────────────────────────────────────
        print("📌 Inserindo vínculos veiculos_scans...")
        for sid, vid in scan_ids:
            vsid = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO veiculos_scans (id, id_scan, id_veiculos) VALUES (%s, %s, %s)",
                (vsid, sid, vid),
            )
        print(f"   ✔ {len(scan_ids)} vínculos inseridos.")

        conn.commit()
        cur.close()

        print("\n✅ Seed concluído com sucesso!")
        print(f"   Veículos  : {len(placas_usadas)}")
        print(f"   Operações : {len(OPERACOES)}")
        print(f"   Drones    : {len(drone_ids)}")
        print(f"   Scans     : {len(scan_ids)}")
        print(f"   Vínculos  : {len(scan_ids)}")


if __name__ == "__main__":
    seed()
