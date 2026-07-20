"""
Servidor WebRTC + Telemetria para o drone Tello.

Substitui drone.py quando o operador quer transmitir o vídeo para o
dashboard web em vez de exibir apenas localmente no OpenCV.

Portas usadas:
  8765  — HTTP: POST /offer (sinalização WebRTC) e WS /telemetry
  11111 — UDP leitura do stream H.264 do Tello (entrada)
  8890  — UDP leitura do estado do Tello: bateria, orientação etc. (entrada)
  8889  — UDP envio de comandos SDK para o Tello (saída)

Como usar:
  1. Conecte uma interface Wi-Fi ao Tello (SSID: TELLO-XXXXXX)
     e mantenha Internet por uma segunda interface quando precisar de APIs/banco.
  2. python -m src.drone_webrtc_server
"""

import asyncio
import concurrent.futures
import json
import logging
import os
import socket
import threading
import time

import aiohttp_cors
import cv2
import numpy as np
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaRelay
from av import VideoFrame
from dotenv import load_dotenv

try:
    from .network_routes import bind_tello_socket, describe_network_plan, load_tello_config
except ImportError:
    from drone.network_routes import bind_tello_socket, describe_network_plan, load_tello_config

try:
    from ..database.local_detections import SQLITE_DB_PATH, ensure_table, save_detection
except ImportError:
    from database.local_detections import SQLITE_DB_PATH, ensure_table, save_detection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("drone_webrtc")

load_dotenv()
TELLO_CONFIG = load_tello_config()
TELLO_ADDRESS = TELLO_CONFIG.command_address
TELLO_VIDEO_URL = TELLO_CONFIG.video_url
TELLO_STATE_PORT = TELLO_CONFIG.state_port
SERVER_HOST = os.getenv("TELLO_WEBRTC_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("TELLO_WEBRTC_PORT", "8765"))

COMMAND_RESPONSE_TIMEOUT = float(os.getenv("TELLO_COMMAND_TIMEOUT", "7.0"))
# Distância padrão (cm) para forward/back/up/down — SDK aceita 20..500
MOVE_DISTANCE_CM = int(os.getenv("TELLO_MOVE_DISTANCE_CM", "30"))
# Rotação padrão (graus) para esquerda/direita (yaw) — SDK aceita 1..360
ROTATE_DEGREES = int(os.getenv("TELLO_ROTATE_DEGREES", "30"))
# Velocidade máxima dos controles contínuos rc — SDK aceita -100..100
RC_SPEED_MAX = int(os.getenv("TELLO_RC_SPEED_MAX", "60"))
# Watchdog (s): sem rc por esse tempo, o drone paira por segurança
RC_WATCHDOG_TIMEOUT = float(os.getenv("TELLO_RC_WATCHDOG_TIMEOUT", "0.5"))

# Detecção YOLO/OCR durante o streaming (produtor da fila SQLite).
# O reconhecimento é caro, então roda só a cada N frames e respeitando um
# intervalo mínimo, sem bloquear a entrega de vídeo ao WebRTC.
YOLO_EVERY_N_FRAMES = 3
MIN_SECONDS_BETWEEN_DETECTIONS = 2

# Estado global do drone atualizado pela thread de leitura UDP 8890
_drone_state: dict = {
    "battery": None,
    "connectivity": "Wi-Fi",
    "status": "pousado",
}
_state_lock = threading.Lock()

# Timestamp do último pacote de estado recebido do Tello (UDP 8890)
# None = nunca recebeu; float = time.time() do último pacote
_last_state_time: float | None = None
_DRONE_TIMEOUT_SECONDS = 3.0


# ---------------------------------------------------------------------------
# Leitura do estado do Tello (UDP 8890)
# ---------------------------------------------------------------------------

def _parse_tello_state(raw: str) -> dict:
    """Converte 'pitch:0;bat:87;h:0;...' em dict."""
    result = {}
    for pair in raw.strip().rstrip(";").split(";"):
        if ":" in pair:
            k, v = pair.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def _state_receiver_loop():
    """Thread bloqueante que escuta UDP 8890 e atualiza _drone_state."""
    global _last_state_time

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("", TELLO_STATE_PORT))
    except OSError as exc:
        logger.error("Nao foi possivel escutar estado UDP :%d: %s", TELLO_STATE_PORT, exc)
        logger.error("Feche CLIs/probes que estejam usando 8890 ou rode scripts/run_tello_webrtc_server.ps1.")
        return

    sock.settimeout(2.0)
    logger.info("Estado do Tello: escutando UDP :%d", TELLO_STATE_PORT)

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            parsed = _parse_tello_state(data.decode("utf-8", errors="ignore"))

            battery_raw = parsed.get("bat")
            battery = f"{battery_raw}%" if battery_raw is not None else None

            height_raw = parsed.get("h", "0")
            try:
                in_flight = float(height_raw) > 20
            except ValueError:
                in_flight = False

            now = time.time()
            was_disconnected = _last_state_time is None or (now - _last_state_time) >= _DRONE_TIMEOUT_SECONDS

            with _state_lock:
                _drone_state["battery"] = battery
                _drone_state["status"] = "em_voo" if in_flight else "pousado"
            _last_state_time = now

            if was_disconnected:
                logger.info("Drone conectado — recebendo estado via UDP 8890")

        except socket.timeout:
            pass
        except Exception as exc:
            logger.debug("Erro ao ler estado do Tello: %s", exc)


# ---------------------------------------------------------------------------
# Reconhecimento de placas + gravação na fila local (produtor)
# ---------------------------------------------------------------------------

def _run_plate_recognition(frame: np.ndarray) -> list:
    """
    Roda YOLO + OCR num frame e devolve a lista de resultados.

    O import é feito aqui (lazy) para não carregar o modelo no import do módulo
    e para suportar execução tanto como pacote (`python -m src.drone_webrtc_server`)
    quanto solta.
    """
    try:
        from src.visao_computacional.yolo26.plate_recognizer import process_frame
    except ModuleNotFoundError:
        from visao_computacional.yolo26.plate_recognizer import process_frame

    _, results = process_frame(frame)
    return results


def _save_valid_detections(results: list, frame: np.ndarray):
    """Grava no SQLite apenas as placas válidas detectadas no frame."""
    for r in results:
        if not r.get("valid") or not r.get("plate"):
            continue
        save_detection(
            plate=r["plate"],
            plate_format=r.get("format", "UNKNOWN"),
            confidence=r.get("confidence", 0.0),
            bbox=r.get("bbox", []),
            frame_bgr=frame,
        )
        logger.info("Detecção salva na fila local: %s", r["plate"])


# ---------------------------------------------------------------------------
# Track de vídeo WebRTC — lê frames do OpenCV
# ---------------------------------------------------------------------------

class TelloVideoTrack(VideoStreamTrack):
    """
    VideoStreamTrack que captura frames do Tello via UDP 11111.

    VideoStreamTrack (aiortc) já define kind="video" e fornece
    next_timestamp() que retorna (pts, time_base) no formato correto
    para o PyAV — não há necessidade de gerenciar pts manualmente.

    Além de transmitir o vídeo, este track também é o **produtor** da fila
    local: a cada N frames roda YOLO+OCR numa thread separada e grava as
    placas válidas no SQLite (plate_frames). O frame enviado por WebRTC
    continua sem overlay — a gravação é um efeito colateral da captura.
    """

    _RETRY_INTERVAL = 5.0   # segundos entre tentativas de abrir o stream
    _RESEND_EVERY = 3       # reenvia streamon a cada N tentativas falhas

    def __init__(self):
        super().__init__()
        self._cap = None
        # 2 workers: 1 para a leitura bloqueante do frame, 1 para o YOLO/OCR.
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._last_open_attempt: float = 0.0
        self._failed_opens: int = 0
        # Estado da detecção assíncrona (produtor da fila SQLite).
        self._frame_count: int = 0
        self._next_processing_at: float = 0.0
        self._processing_future = None

    def _open_capture(self):
        logger.info("Tentando abrir stream UDP do Tello (%s)...", TELLO_VIDEO_URL)
        cap = cv2.VideoCapture(TELLO_VIDEO_URL, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not cap.isOpened():
            logger.warning("Stream não disponível (drone offline ou streamon não recebido).")
        else:
            logger.info("Stream do Tello aberto com sucesso.")
        return cap

    def _read_frame_blocking(self):
        """Leitura bloqueante — roda no executor para não travar o asyncio."""
        now = time.monotonic()

        if self._cap is None or not self._cap.isOpened():
            # Throttle: não tenta abrir antes do intervalo mínimo
            if now - self._last_open_attempt < self._RETRY_INTERVAL:
                time.sleep(0.05)
                return None

            self._last_open_attempt = now
            self._failed_opens += 1

            # Reenvia streamon periodicamente para o caso do Tello ter ignorado
            if self._failed_opens == 1 or self._failed_opens % self._RESEND_EVERY == 0:
                logger.info("Reenviando streamon ao Tello (tentativa %d)...", self._failed_opens)
                _send_command("command")
                time.sleep(0.3)
                _send_command("streamon")

            self._cap = self._open_capture()
            if not self._cap.isOpened():
                return None

            self._failed_opens = 0  # abriu com sucesso — zera o contador

        # Descarta frames acumulados no buffer (reduz latência)
        for _ in range(2):
            self._cap.grab()

        ret, frame = self._cap.read()
        if not ret:
            # Tello parou de transmitir — libera o cap para reabrir na próxima tentativa
            logger.warning("Leitura de frame falhou — drone pode ter desligado.")
            self._cap.release()
            self._cap = None
            self._last_open_attempt = time.monotonic()  # começa o throttle de retry
            return None

        return frame

    def _on_detection_done(self, future):
        """Callback do YOLO: registra falhas e libera o slot de processamento."""
        try:
            future.result()
        except Exception as exc:
            logger.warning("Erro no YOLO/OCR: %s", exc)
        finally:
            self._processing_future = None

    async def recv(self):
        # next_timestamp() retorna (pts, Fraction) com a frequência correta
        pts, time_base = await self.next_timestamp()

        loop = asyncio.get_running_loop()
        bgr_frame = await loop.run_in_executor(self._executor, self._read_frame_blocking)

        if bgr_frame is None:
            # Frame preto enquanto aguarda conexão com o drone
            bgr_frame = np.zeros((720, 960, 3), dtype=np.uint8)
        else:
            self._frame_count += 1
            now = time.monotonic()
            should_detect = (
                self._processing_future is None
                and self._frame_count % YOLO_EVERY_N_FRAMES == 0
                and now >= self._next_processing_at
            )
            if should_detect:
                # Captura uma cópia do frame no closure para que a detecção
                # assíncrona não veja o buffer sobrescrito por frames futuros.
                def _make_task(frame_copy):
                    def _task():
                        results = _run_plate_recognition(frame_copy)
                        _save_valid_detections(results, frame_copy)
                        return results
                    return _task

                self._processing_future = loop.run_in_executor(
                    self._executor, _make_task(bgr_frame.copy())
                )
                self._processing_future.add_done_callback(self._on_detection_done)
                self._next_processing_at = now + MIN_SECONDS_BETWEEN_DETECTIONS

        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(rgb_frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    def stop(self):
        super().stop()
        if self._cap and self._cap.isOpened():
            self._cap.release()
        self._executor.shutdown(wait=False)


# ---------------------------------------------------------------------------
# Endpoints HTTP
# ---------------------------------------------------------------------------

# Captura de video unica e compartilhada entre todos os clientes WebRTC.
# Um unico TelloVideoTrack le o UDP 11111 e o MediaRelay distribui os frames
# para cada conexao (cada /offer recebe uma "assinatura" da mesma fonte).
# Motivo: criar um TelloVideoTrack por /offer abria varias capturas concorrentes
# na porta 11111 e cada uma reenviava 'streamon' periodicamente, causando a
# "tempestade de streamon" e conflito do stream de video.
_video_source: "TelloVideoTrack | None" = None
_relay: "MediaRelay | None" = None


def _get_shared_video_track():
    """Retorna uma assinatura (relay) da captura unica do Tello.

    Cria a fonte e o relay no primeiro /offer. Roda no event loop, entao nao
    precisa de lock. A fonte permanece viva entre conexoes: clientes entram e
    saem sem reabrir a captura nem reenviar 'streamon'.
    """
    global _video_source, _relay
    if _relay is None:
        _relay = MediaRelay()
    if _video_source is None:
        _video_source = TelloVideoTrack()
        logger.info("Captura de video compartilhada criada (fonte unica do Tello).")
    return _relay.subscribe(_video_source)


async def handle_offer(request: web.Request) -> web.Response:
    """POST /offer — recebe SDP offer do browser, retorna SDP answer."""
    try:
        body = await request.json()
    except Exception:
        return web.Response(status=400, text="JSON inválido")

    logger.info("WebRTC: offer recebido (type=%s)", body.get("type"))

    offer = RTCSessionDescription(sdp=body["sdp"], type=body["type"])

    pc = RTCPeerConnection()
    # Captura unica compartilhada via MediaRelay: todos os clientes assistem a
    # MESMA captura do UDP 11111. Antes, cada /offer criava um TelloVideoTrack
    # novo -> varias capturas concorrentes na porta 11111, cada uma reenviando
    # 'streamon' (tempestade de streamon + conflito de stream).
    video_track = _get_shared_video_track()
    pc.addTrack(video_track)

    ice_complete = asyncio.Event()

    @pc.on("icegatheringstatechange")
    def on_ice_state():
        logger.info("ICE gathering state: %s", pc.iceGatheringState)
        if pc.iceGatheringState == "complete":
            ice_complete.set()

    @pc.on("connectionstatechange")
    async def on_conn_state():
        logger.info("WebRTC connection state: %s", pc.connectionState)
        if pc.connectionState in ("failed", "closed"):
            # Encerra apenas a assinatura do relay deste cliente; a captura
            # compartilhada (_video_source) segue ativa para os demais.
            video_track.stop()
            await pc.close()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Aguarda ICE gathering com timeout de 10s
    try:
        await asyncio.wait_for(ice_complete.wait(), timeout=10.0)
    except asyncio.TimeoutError:
        logger.warning("ICE gathering timeout — retornando resposta parcial")

    logger.info("WebRTC: answer enviado")
    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )


async def handle_telemetry(request: web.Request) -> web.WebSocketResponse:
    """GET /telemetry — WebSocket; envia JSON de telemetria a cada 1s."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    logger.info("WebSocket telemetria: cliente conectado de %s", request.remote)

    prev_connected: bool | None = None

    try:
        while not ws.closed:
            now = time.time()
            drone_connected = (
                _last_state_time is not None
                and (now - _last_state_time) < _DRONE_TIMEOUT_SECONDS
            )

            if drone_connected != prev_connected:
                state = "conectado" if drone_connected else "desconectado"
                logger.info("Drone %s (último pacote: %.1fs atrás)",
                            state,
                            (now - _last_state_time) if _last_state_time else float("inf"))
                prev_connected = drone_connected

            with _state_lock:
                payload = dict(_drone_state)

            payload["drone_connected"] = drone_connected

            # Quando offline, limpa bateria para evitar exibir valor antigo
            if not drone_connected:
                payload["battery"] = None
                payload["status"] = "offline"

            await ws.send_str(json.dumps(payload))
            await asyncio.sleep(1.0)
    except Exception as exc:
        logger.debug("WebSocket telemetria encerrado: %s", exc)
    finally:
        logger.info("WebSocket telemetria: cliente desconectado")

    return ws


async def handle_control(request: web.Request) -> web.WebSocketResponse:
    """GET /control — WebSocket de controle continuo (rc a b c d).

    O cliente envia, em alta frequencia, JSON {lr, fb, ud, yaw} com cada eixo em
    -RC_SPEED_MAX..RC_SPEED_MAX. O servidor traduz para 'rc a b c d' (fire-and-
    forget; o Tello nao responde a rc). Salvaguardas contra runaway:
      - watchdog (deadman): se o drone estiver em movimento e nao chegar rc por
        RC_WATCHDOG_TIMEOUT, envia 'rc 0 0 0 0' (paira);
      - ao desconectar, envia 'rc 0 0 0 0'.
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    logger.info("WebSocket controle: cliente conectado de %s", request.remote)

    loop = asyncio.get_running_loop()
    last_rc = time.monotonic()
    moving = False

    async def send_rc(a: int, b: int, c: int, d: int):
        await loop.run_in_executor(None, _send_command, f"rc {a} {b} {c} {d}")

    async def watchdog():
        nonlocal moving
        try:
            while not ws.closed:
                await asyncio.sleep(0.1)
                if moving and (time.monotonic() - last_rc) > RC_WATCHDOG_TIMEOUT:
                    logger.warning(
                        "Watchdog rc: sem updates ha >%.0fms — pairando (rc 0 0 0 0)",
                        RC_WATCHDOG_TIMEOUT * 1000,
                    )
                    await send_rc(0, 0, 0, 0)
                    moving = False
        except asyncio.CancelledError:
            pass

    wd_task = asyncio.create_task(watchdog())
    try:
        async for msg in ws:
            if msg.type != web.WSMsgType.TEXT:
                if msg.type == web.WSMsgType.ERROR:
                    break
                continue
            try:
                data = json.loads(msg.data)
            except (ValueError, TypeError):
                continue
            a = _clamp_int(data.get("lr", 0), -RC_SPEED_MAX, RC_SPEED_MAX, 0)
            b = _clamp_int(data.get("fb", 0), -RC_SPEED_MAX, RC_SPEED_MAX, 0)
            c = _clamp_int(data.get("ud", 0), -RC_SPEED_MAX, RC_SPEED_MAX, 0)
            d = _clamp_int(data.get("yaw", 0), -RC_SPEED_MAX, RC_SPEED_MAX, 0)
            await send_rc(a, b, c, d)
            last_rc = time.monotonic()
            moving = bool(a or b or c or d)
    except Exception as exc:
        logger.debug("WebSocket controle encerrado: %s", exc)
    finally:
        wd_task.cancel()
        await send_rc(0, 0, 0, 0)  # garante hover ao desconectar
        logger.info("WebSocket controle: cliente desconectado — drone pairando")

    return ws


# ---------------------------------------------------------------------------
# Controle de voo via dashboard (POST /command)
# ---------------------------------------------------------------------------

def _clamp_int(value, low: int, high: int, default: int) -> int:
    """Converte para int e limita ao intervalo [low, high]; usa default se invalido."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, v))


def _build_sdk_command(action: str, value=None) -> str | None:
    """
    Mapeia uma acao do dashboard para um comando do Tello SDK (allowlist).

    Decisao da Sprint 5: esquerda/direita = rotacao no proprio eixo (yaw),
    para o operador varrer o ambiente e enquadrar a placa dos veiculos.
    Retorna None se a acao nao estiver na allowlist (impede comando arbitrario).
    """
    if action == "takeoff":
        return "takeoff"
    if action == "land":
        return "land"
    if action == "up":
        return f"up {_clamp_int(value, 20, 500, MOVE_DISTANCE_CM)}"
    if action == "down":
        return f"down {_clamp_int(value, 20, 500, MOVE_DISTANCE_CM)}"
    if action == "forward":
        return f"forward {_clamp_int(value, 20, 500, MOVE_DISTANCE_CM)}"
    if action == "back":
        return f"back {_clamp_int(value, 20, 500, MOVE_DISTANCE_CM)}"
    if action == "left":
        return f"ccw {_clamp_int(value, 1, 360, ROTATE_DEGREES)}"
    if action == "right":
        return f"cw {_clamp_int(value, 1, 360, ROTATE_DEGREES)}"
    if action == "stop":
        # rc 0 0 0 0 (controles neutros) faz o Tello pairar/parar e funciona em
        # qualquer firmware. O comando "stop" do SDK 2.0 nao existe no SDK 1.3 e
        # e recusado ("unknown command"/"error") por firmwares antigos.
        return "rc 0 0 0 0"
    return None


async def handle_command(request: web.Request) -> web.Response:
    """POST /command — recebe acao do dashboard e envia o comando SDK ao Tello."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "JSON invalido"}, status=400)

    action = str(body.get("action", "")).strip().lower()
    cmd = _build_sdk_command(action, body.get("value"))
    if cmd is None:
        return web.json_response(
            {"ok": False, "error": f"Acao nao permitida: {action or '(vazio)'}"},
            status=400,
        )

    # Defesa em profundidade: so envia comando se o drone estiver transmitindo
    # estado (UDP 8890). O frontend ja esconde os botoes quando desconectado.
    now = time.time()
    drone_connected = (
        _last_state_time is not None
        and (now - _last_state_time) < _DRONE_TIMEOUT_SECONDS
    )
    if not drone_connected:
        return web.json_response(
            {"ok": False, "error": "Drone desconectado - comando nao enviado"},
            status=409,
        )

    loop = asyncio.get_running_loop()

    # Comandos 'rc' (hover/controle continuo, ex.: Parar) NAO recebem resposta
    # do Tello; envia fire-and-forget (em executor, pois pode aguardar o lock do
    # socket compartilhado) e confirma o envio sem esperar 'ok'.
    if cmd.startswith("rc "):
        await loop.run_in_executor(None, _send_command, cmd)
        return web.json_response({"ok": True, "action": action, "command": cmd})

    # Demais comandos: aguarda a resposta real do Tello em executor, para nao
    # travar o event loop enquanto a manobra e concluida. Assim o dashboard sabe
    # se o comando foi de fato aceito (ex.: forward pode retornar "error").
    response = await loop.run_in_executor(None, _send_command_await, cmd)

    if response is None:
        return web.json_response(
            {"ok": False, "action": action, "command": cmd,
             "error": "Sem resposta do Tello (timeout)"},
            status=504,
        )

    accepted = response.lower().startswith("ok")
    if accepted:
        return web.json_response(
            {"ok": True, "action": action, "command": cmd, "response": response}
        )
    return web.json_response(
        {"ok": False, "action": action, "command": cmd, "response": response,
         "error": f"Tello recusou '{cmd}': {response}"},
        status=502,
    )


# ---------------------------------------------------------------------------
# Comunicação com o Tello
# ---------------------------------------------------------------------------

# Socket de comando compartilhado: faz bind na porta local (9000) uma unica vez
# e e reutilizado por startup, retry de video e comandos de controle. Evita o
# WinError 10048 de re-bindar uma porta exclusiva a cada envio; o lock serializa
# os envios para que so haja um comando em transito por vez.
_command_sock: socket.socket | None = None
_command_lock = threading.Lock()


def _get_command_socket() -> socket.socket:
    """Cria (no primeiro uso) e retorna o socket de comando compartilhado.

    Deve ser chamada com _command_lock ja adquirido.
    """
    global _command_sock
    if _command_sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bind_tello_socket(sock, TELLO_CONFIG)
        _command_sock = sock
        host, port = TELLO_CONFIG.public_bind_address
        logger.info("Socket de comando do Tello vinculado em %s:%d", host, port)
    return _command_sock


def _reset_command_socket_locked() -> None:
    """Fecha e zera o socket compartilhado para recriacao no proximo uso.

    Auto-recuperacao caso o socket entre em estado de erro (ex.: WSAECONNRESET no
    Windows apos um ICMP 'port unreachable'). Requer _command_lock adquirido.
    """
    global _command_sock
    if _command_sock is not None:
        try:
            _command_sock.close()
        except OSError:
            pass
        _command_sock = None


def _close_command_socket() -> None:
    """Fecha o socket de comando compartilhado (chamado no encerramento)."""
    with _command_lock:
        _reset_command_socket_locked()


def _drain_command_socket(sock: socket.socket) -> None:
    """Descarta respostas antigas pendentes no buffer (de envios fire-and-forget).

    Sem isso, um 'ok' deixado por um envio anterior seria lido como se fosse a
    resposta do comando atual. Deve ser chamada com _command_lock adquirido.
    """
    sock.setblocking(False)
    try:
        while True:
            try:
                sock.recvfrom(1024)
            except OSError:
                break
    finally:
        sock.setblocking(True)


def _send_command(cmd: str) -> None:
    """Envia comando SDK para o Tello via UDP (fire-and-forget).

    Usa o socket de comando compartilhado sob lock, evitando disputa pela porta
    local 9000 com outros envios (startup, retry de video, controle).
    """
    with _command_lock:
        try:
            sock = _get_command_socket()
            sock.sendto(cmd.encode("utf-8"), TELLO_ADDRESS)
            logger.info("Tello ← %s", cmd)
        except OSError as exc:
            logger.warning("Falha ao enviar '%s': %s", cmd, exc)
            _reset_command_socket_locked()


def _send_command_await(cmd: str, timeout: float = COMMAND_RESPONSE_TIMEOUT) -> str | None:
    """
    Envia comando SDK e aguarda a resposta do Tello no socket compartilhado (9000).

    Diferente do envio fire-and-forget, aqui lemos a resposta real do drone.
    Comandos de movimento (forward/back/up/down/cw/ccw) e takeoff/land so
    respondem "ok" depois de concluir a manobra; por isso o timeout cobre a acao.

    O lock garante uso exclusivo do socket durante envio+leitura, serializando os
    comandos e eliminando conflito de porta. Antes de enviar, descarta respostas
    antigas no buffer para nao confundir com a resposta deste comando.

    Retorna a resposta como string (ex.: "ok", "error", "out of range") ou None
    em caso de timeout/erro. E bloqueante: deve ser chamada via executor para nao
    travar o event loop do aiohttp.
    """
    with _command_lock:
        try:
            sock = _get_command_socket()
            _drain_command_socket(sock)
            sock.settimeout(timeout)
            sock.sendto(cmd.encode("utf-8"), TELLO_ADDRESS)
            logger.info("Tello ← %s", cmd)
            data, _ = sock.recvfrom(1024)
        except socket.timeout:
            logger.warning("Tello → sem resposta para '%s' (timeout %.1fs)", cmd, timeout)
            return None
        except OSError as exc:
            logger.warning("Falha ao enviar '%s': %s", cmd, exc)
            _reset_command_socket_locked()
            return None

    response = data.decode("utf-8", errors="ignore").strip()
    logger.info("Tello → '%s' respondeu: %s", cmd, response)
    return response


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    logger.info(describe_network_plan(TELLO_CONFIG))

    # Garante que a fila local (plate_frames) existe antes de produzir detecções
    ensure_table()
    logger.info("Banco local pronto: %s", SQLITE_DB_PATH)

    # Inicia thread de leitura de estado do drone
    state_thread = threading.Thread(target=_state_receiver_loop, daemon=True)
    state_thread.start()

    # Ativa o SDK e o stream de vídeo do Tello
    _send_command("command")
    time.sleep(1.5)
    _send_command("streamon")
    logger.info("Tello: SDK ativo, stream de vídeo iniciado")

    # Configura app aiohttp
    app = web.Application()

    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "OPTIONS"],
            )
        },
    )

    offer_resource = cors.add(app.router.add_resource("/offer"))
    cors.add(offer_resource.add_route("POST", handle_offer))

    command_resource = cors.add(app.router.add_resource("/command"))
    cors.add(command_resource.add_route("POST", handle_command))

    app.router.add_route("GET", "/telemetry", handle_telemetry)
    app.router.add_route("GET", "/control", handle_control)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, SERVER_HOST, SERVER_PORT)
    await site.start()

    logger.info("=" * 50)
    logger.info("Servidor WebRTC rodando em http://localhost:%d", SERVER_PORT)
    logger.info("  POST /offer      — sinalização WebRTC")
    logger.info("  POST /command    — controle de voo (takeoff/land/up/down/forward/back/cw/ccw/stop)")
    logger.info("  WS   /telemetry  — telemetria em tempo real")
    logger.info("  WS   /control    — controle continuo (rc a b c d) com watchdog")
    logger.info("Pressione Ctrl+C para encerrar.")
    logger.info("=" * 50)

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        _send_command("streamoff")
        _close_command_socket()
        await runner.cleanup()
        logger.info("Servidor encerrado.")


if __name__ == "__main__":
    asyncio.run(main())
