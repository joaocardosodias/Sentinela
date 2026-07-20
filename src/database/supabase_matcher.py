import os
import time
import re
import json
import uuid
from datetime import datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Importações para fazer a comparação e lidar melhor com os problemas com a API da Pier
import urllib.error
import urllib.parse
import urllib.request

# Importando funções da localização local 
try:
    from database.local_detections import (
        delete_local_detection,
        get_pending_detections,
        update_local_detection_status,
    )
except ModuleNotFoundError:
    from local_detections import (
        delete_local_detection,
        get_pending_detections,
        update_local_detection_status,
    )


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_DRONE_ID = os.getenv("DEFAULT_DRONE_ID")
DATABASE_CONNECT_TIMEOUT = int(os.getenv("DATABASE_CONNECT_TIMEOUT", "10"))

# Configurações da API da Pier.
PIER_AUTH_URL = (
    "https://auth.stag.pier.zone"
    "/realms/pier-ext-auth-apis/protocol/openid-connect/token"
)
PIER_LOOKUP_URL = "https://gw2.stag.pier.zone/v1/inteli/vehicle-lookups"
PIER_USERNAME = os.getenv("PIER_USERNAME")
PIER_PASSWORD = os.getenv("PIER_PASSWORD")
PIER_CLIENT_ID = os.getenv("PIER_CLIENT_ID", "pier-ext-auth-apis-client")
PIER_CLIENT_SECRET = os.getenv("PIER_CLIENT_SECRET")
PIER_LATITUDE = float(os.getenv("PIER_LATITUDE", "-23.5505"))
PIER_LONGITUDE = float(os.getenv("PIER_LONGITUDE", "-46.6333"))
PIER_TIMEOUT_SECONDS = float(os.getenv("PIER_TIMEOUT_SECONDS", "10"))

# Responsável por pegar os frames do SQLite.
BASE_DIR = Path(__file__).resolve().parent
# Raiz do projeto (g03/) — MESMO diretório que o backend serve em
# /uploaded_frames (config.UPLOADED_FRAMES_DIR). Sobe database/ -> src/ -> raiz.
PROJECT_ROOT = BASE_DIR.parent.parent
FRAME_OUTPUT_DIR = PROJECT_ROOT / "uploaded_frames"


if not DATABASE_URL:
    raise RuntimeError("Variável DATABASE_URL não encontrada no .env")

# ---------------------------------------------------------------------------
# Identidade do drone — IDs fixos cadastrados no Supabase
# Mesmo valor usado em drone_pipeline.py para consistência.
# ---------------------------------------------------------------------------
DEFAULT_DRONE_ID    = "a1b2c3d4-0001-4000-8000-000000000001"  # drones.id
DEFAULT_OPERACAO_ID = "a1b2c3d4-0002-4000-8000-000000000001"  # operacoes.id


# Erro técnico ao autenticar ou consultar a API da Pier.
class PierApiError(RuntimeError):

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except Exception:
        return False


def get_connection():
    """Abre uma conexão com o banco PostgreSQL/Supabase."""
    return psycopg2.connect(DATABASE_URL)


def normalize_plate(plate):
    """Normaliza a placa antes de enviá-la à Pier e salvar o frame."""
    if not plate:
        return ""

    return re.sub(r"[^A-Z0-9]", "", plate.upper())


def save_matched_frame_as_file(frame_blob, plate):
    """
    Salva localmente o frame que deu match e retorna o caminho relativo
    usado em scans.imagem_url.
    """
    if not frame_blob:
        return None

    normalized_plate = normalize_plate(plate) or "UNKNOWN"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    output_dir = FRAME_OUTPUT_DIR / normalized_plate
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{timestamp}.jpg"
    output_path = output_dir / filename

    with open(output_path, "wb") as file:
        file.write(frame_blob)

    return f"uploaded_frames/{normalized_plate}/{filename}"

#Garante que as credenciais necessárias foram definidas no .env para minimizar erros
def validate_pier_configuration():

    missing_variables = []

    if not PIER_USERNAME:
        missing_variables.append("PIER_USERNAME")
    if not PIER_PASSWORD:
        missing_variables.append("PIER_PASSWORD")
    if not PIER_CLIENT_SECRET:
        missing_variables.append("PIER_CLIENT_SECRET")

    if missing_variables:
        missing = ", ".join(missing_variables)
        raise PierApiError(
            f"Variáveis da Pier ausentes no .env: {missing}"
        )


def get_pier_access_token():
    """Autentica na Pier e devolve um access_token temporário."""
    validate_pier_configuration()

    payload = {
        "grant_type": "password",
        "username": PIER_USERNAME,
        "password": PIER_PASSWORD,
        "client_id": PIER_CLIENT_ID,
        "client_secret": PIER_CLIENT_SECRET,
    }

    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(PIER_AUTH_URL, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(
            request,
            timeout=PIER_TIMEOUT_SECONDS,
        ) as response:
            token_data = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise PierApiError(
            f"Falha de autenticação na Pier ({error.code}): {body}",
            status_code=error.code,
        ) from error

    except urllib.error.URLError as error:
        raise PierApiError(
            f"Falha de conexão ao autenticar na Pier: {error}"
        ) from error

    except json.JSONDecodeError as error:
        raise PierApiError(
            "A Pier devolveu uma resposta inválida ao autenticar."
        ) from error

    access_token = token_data.get("access_token")

    if not access_token:
        raise PierApiError("A Pier não devolveu access_token na autenticação.")

    return access_token


def lookup_vehicle_on_pier(access_token, plate):
    """
    Consulta uma placa na Pier.

    Retorna o JSON recebido quando a chamada é válida. Se a Pier responder
    404, devolve status='not_found'. Outros erros são tratados como falhas
    técnicas para evitar falsos negativos.
    """
    normalized_plate = normalize_plate(plate)

    if not normalized_plate:
        raise PierApiError("Placa vazia após normalização.")

    payload = {
        "license_plate": normalized_plate,
        "geolocation": {
            "latitude": PIER_LATITUDE,
            "longitude": PIER_LONGITUDE,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(PIER_LOOKUP_URL, data=data, method="POST")
    request.add_header("Authorization", f"Bearer {access_token}")
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(
            request,
            timeout=PIER_TIMEOUT_SECONDS,
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")

        # Placa não encontrada é um resultado válido da comparação.
        if error.code == 404:
            return {
                "status": "Não Tem no Nosso Banco de Dados.",
                "message": "Veículo Não Achado na Pier.",
            }

        raise PierApiError(
            f"Erro ao consultar placa {normalized_plate} na Pier "
            f"({error.code}): {body}",
            status_code=error.code,
        ) from error

    except urllib.error.URLError as error:
        raise PierApiError(
            f"Falha de conexão ao consultar placa {normalized_plate} na Pier: "
            f"{error}"
        ) from error

    except json.JSONDecodeError as error:
        raise PierApiError(
            f"A Pier devolveu JSON inválido para a placa {normalized_plate}."
        ) from error


def pier_result_has_match(pier_result):
    """Interpreta status='found' como match no catálogo retornado pela Pier."""
    if not isinstance(pier_result, dict):
        raise PierApiError("Resposta inesperada recebida da Pier.")

    return str(pier_result.get("status", "")).lower() == "found"


def _extract_vehicle_fields(pier_result):
    """
    Extrai modelo, cor e marca da resposta da Pier.

    A Pier retorna os dados aninhados em "vehicle":
        {"vehicle": {"make": ..., "model": ..., "color": ...}, "status": "found"}
    Retorna (modelo, cor, marca) com fallbacks seguros, já que a tabela
    veiculos exige modelo e cor NOT NULL.
    """
    vehicle = {}
    if isinstance(pier_result, dict):
        vehicle = pier_result.get("vehicle") or {}

    modelo = (vehicle.get("model") or "").strip() or "Desconhecido"
    cor = (vehicle.get("color") or "").strip() or "Desconhecida"
    marca = (vehicle.get("make") or "").strip() or None
    return modelo, cor, marca


def _get_or_create_vehicle(cursor, placa, modelo, cor, data_roubo):
    """
    Encontra um veículo pela placa (UNIQUE) ou cria um novo.

    Retorna o id (UUID) do veículo. Atualiza modelo/cor se o veículo já
    existir, para refletir os dados mais recentes da Pier.
    """
    cursor.execute("SELECT id FROM veiculos WHERE placa = %s", (placa,))
    row = cursor.fetchone()
    if row:
        vehicle_id = row["id"]
        cursor.execute(
            "UPDATE veiculos SET modelo = %s, cor = %s WHERE id = %s",
            (modelo, cor, vehicle_id),
        )
        return vehicle_id

    vehicle_id = str(uuid.uuid4())
    cursor.execute(
        """
        INSERT INTO veiculos (id, placa, modelo, cor, roubado, data_roubo)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (vehicle_id, placa, modelo, cor, True, data_roubo),
    )
    return vehicle_id


def _link_vehicle_scan(cursor, scan_id, vehicle_id):
    """Cria o vínculo na tabela intermediária veiculos_scans."""
    cursor.execute(
        "INSERT INTO veiculos_scans (id, id_scan, id_veiculos) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), scan_id, vehicle_id),
    )


def create_scan(cursor, detection, has_match, imagem_url=None, pier_result=None):
    """
    Cria um registro na tabela scans.

    Quando há match, também garante o veículo na tabela veiculos e o vínculo
    em veiculos_scans, para que o backend (que faz JOIN scans -> veiculos_scans
    -> veiculos) consiga retornar modelo e cor ao frontend.
    """
    scan_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO scans (
            id,
            id_drone,
            placa,
            match,
            imagem_url,
            latitude,
            longitude,
            horario_scan,
            status_validacao
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            scan_id,
            DEFAULT_DRONE_ID,
            detection["plate"],
            has_match,
            imagem_url,
            None,
            None,
            detection["created_at"],
            "pendente",
        ),
    )
    scan_row = cursor.fetchone()

    # Com match: popular veiculos + veiculos_scans a partir dos dados da Pier.
    if has_match and pier_result is not None:
        modelo, cor, _marca = _extract_vehicle_fields(pier_result)
        # A Pier não retorna data de roubo; usamos o horário do scan como
        # fallback, já que veiculos.data_roubo é NOT NULL.
        data_roubo = detection["created_at"]
        vehicle_id = _get_or_create_vehicle(
            cursor, detection["plate"], modelo, cor, data_roubo
        )
        _link_vehicle_scan(cursor, scan_id, vehicle_id)

    return scan_row


def process_pending_detections(limit=10):
    """
    Fluxo:
    1. Busca registros pending no SQLite.
    2. Autentica uma vez na API da Pier.
    3. Para cada placa, consulta a API da Pier em vez da tabela veiculos.
    4. Se houver match, salva o frame localmente e preenche imagem_url.
    5. Cria um scan no Supabase/PostgreSQL.
    6. Remove o registro local do SQLite após sucesso.
    7. Se ocorrer erro técnico, marca o registro local como error.
    """
    pending_detections = get_pending_detections(limit=limit)

    if not pending_detections:
        print("Nenhuma detecção pendente encontrada.")
        return

    try:
        access_token = get_pier_access_token()
    except PierApiError as error:
        # Mantemos os registros como pending para tentar novamente depois.
        print(f"Não foi possível iniciar a sincronização com a Pier: {error}")
        return

    for detection in pending_detections:
        detection_id = detection["id"]
        plate = detection["plate"]
        conn = None

        try:
            try:
                pier_result = lookup_vehicle_on_pier(access_token, plate)

            except PierApiError as error:
                # O token expira rapidamente. Em caso de 401, renovamos uma
                # vez e repetimos somente a consulta atual.
                if error.status_code != 401:
                    raise

                access_token = get_pier_access_token()
                pier_result = lookup_vehicle_on_pier(access_token, plate)

            has_match = pier_result_has_match(pier_result)
            imagem_url = None

            if has_match:
                imagem_url = save_matched_frame_as_file(
                    frame_blob=detection["frame_blob"],
                    plate=plate,
                )

            conn = get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            create_scan(
                cursor=cursor,
                detection=detection,
                has_match=has_match,
                imagem_url=imagem_url,
                pier_result=pier_result,
            )

            if has_match:
                print(
                    f"Match encontrado na Pier para {plate}. "
                    "Scan criado com match=True e imagem_url preenchida."
                )
            else:
                print(
                    f"Sem match na Pier para {plate}. "
                    "Scan criado com match=False e imagem_url=None."
                )

            conn.commit()
            delete_local_detection(detection_id)

        except Exception as error:
            if conn:
                conn.rollback()

            update_local_detection_status(detection_id, "error")
            print(f"Erro ao processar {plate}: {error}")

        finally:
            if conn:
                conn.close()


# ---------------------------------------------------------------------------
# Worker automático (loop) — drena a fila local em tempo real.
# Antes vivia em sync_worker.py / drone_pipeline.py; agora consolidado aqui.
# ---------------------------------------------------------------------------

SYNC_INTERVAL_SECONDS = float(os.getenv("SYNC_INTERVAL_SECONDS", "5"))
SYNC_BATCH_LIMIT = int(os.getenv("SYNC_BATCH_LIMIT", "10"))


def run_sync_loop():
    """
    Executa process_pending_detections em intervalos regulares, para sempre.

    Falhas de um ciclo (ex.: oscilação de rede com a Pier) são capturadas e
    registradas; o próximo ciclo tenta novamente, sem derrubar o worker.
    """
    print(
        f"Worker de sincronização iniciado "
        f"(intervalo={SYNC_INTERVAL_SECONDS}s, lote={SYNC_BATCH_LIMIT}). "
        f"Ctrl+C para parar."
    )
    while True:
        try:
            process_pending_detections(limit=SYNC_BATCH_LIMIT)
        except Exception as error:
            print(f"Ciclo de sincronização falhou: {error}")
        time.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        run_sync_loop()
    except KeyboardInterrupt:
        print("\nWorker encerrado.")