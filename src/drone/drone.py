# Código fornecido pela documentação do drone
# Tello Python3 Control Demo + Video Stream

import threading
import socket
import time
import platform
import sys
import os
from pathlib import Path
import cv2
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drone.network_routes import bind_tello_socket, describe_network_plan, load_tello_config


load_dotenv()
TELLO_CONFIG = load_tello_config()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = TELLO_CONFIG.command_address
TELLO_BIND = bind_tello_socket(sock, TELLO_CONFIG)

video_running = False


def recv():
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print("Tello:", data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break


VIDEO_URL = TELLO_CONFIG.video_url
WINDOW_NAME = "Video do Tello"

# O video precisa continuar fluido mesmo quando o YOLO/OCR demora.
# Por isso a deteccao roda em uma thread separada e sem fila acumulada.
YOLO_EVERY_N_FRAMES = 3
MIN_SECONDS_BETWEEN_DETECTIONS = 0.25
DETECTION_OVERLAY_TTL_SECONDS = 1.5
BUFFER_FLUSH_FRAMES = 2


def flush_buffer(cap, n=BUFFER_FLUSH_FRAMES):
    # Descarta frames acumulados no buffer para pegar sempre o mais recente
    for _ in range(n):
        cap.grab()


def run_plate_recognition(frame):
    """
    Executa YOLO + OCR fora da thread da camera.

    Importar aqui tambem evita travar o inicio do programa carregando o modelo.
    Depois da primeira chamada, o Python reutiliza o modulo ja carregado.
    """
    try:
        from src.visao_computacional.yolo26.plate_recognizer import process_frame
    except ModuleNotFoundError:
        from visao_computacional.yolo26.plate_recognizer import process_frame

    _, frame_results = process_frame(frame)
    return frame_results


def draw_detection_results(frame, frame_results):
    """
    Desenha o ultimo resultado conhecido no frame atual.

    Isso mantem o video ao vivo. A gente nao exibe o frame antigo processado,
    porque ele poderia trazer de volta exatamente o atraso que queremos evitar.
    """
    for result in frame_results:
        bbox = result.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = map(int, bbox)
        color = (0, 255, 0) if result.get("valid") else (0, 200, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

        plate = result.get("plate", "")
        plate_format = result.get("format", "")
        label = plate
        if plate and plate_format and plate_format != "UNKNOWN":
            label = f"{plate} | {plate_format}"

        if not label:
            confidence = result.get("confidence")
            if confidence is not None:
                label = f"placa? {confidence:.2f}"

        if label:
            text_y = max(30, y1 - 20)
            cv2.putText(
                frame,
                label,
                (x1, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),
                4,
            )
            cv2.putText(
                frame,
                label,
                (x1, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )


def video_stream():
    global video_running

    print(f"Abrindo vídeo do Tello em {VIDEO_URL}...")
    os.environ.setdefault(
        "OPENCV_FFMPEG_CAPTURE_OPTIONS",
        "fifo_size;50000000|overrun_nonfatal;1",
    )

    cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # buffer mínimo — reduz delay acumulado

    if not cap.isOpened():
        print("Não foi possível abrir o vídeo.")
        return

    frame_count = 0
    last_frame_results = []
    last_results_at = 0
    next_processing_at = 0
    processing_future = None
    executor = ThreadPoolExecutor(max_workers=1)

    try:
        while video_running:
            flush_buffer(cap)
            ret, frame = cap.read()

            if not ret:
                print("Aguardando imagem do drone...")
                time.sleep(0.5)
                continue

            frame_count += 1
            now = time.monotonic()

            # Se o processamento terminou, pegamos o resultado.
            # Se ainda estiver rodando, o video continua sem esperar.
            if processing_future is not None and processing_future.done():
                try:
                    last_frame_results = processing_future.result()
                    last_results_at = now
                    if last_frame_results:
                        print(last_frame_results)
                except Exception as exc:
                    print(f"Erro ao processar frame: {exc}")
                finally:
                    processing_future = None

            should_process = (
                processing_future is None
                and frame_count % YOLO_EVERY_N_FRAMES == 0
                and now >= next_processing_at
            )

            if should_process:
                processing_future = executor.submit(run_plate_recognition, frame.copy())
                next_processing_at = now + MIN_SECONDS_BETWEEN_DETECTIONS

            display_frame = frame.copy()
            has_recent_results = (
                last_frame_results
                and now - last_results_at <= DETECTION_OVERLAY_TTL_SECONDS
            )
            if has_recent_results:
                draw_detection_results(display_frame, last_frame_results)

            cv2.imshow(WINDOW_NAME, display_frame)

            # Aperte Q na janela do vídeo para fechar apenas a janela
            if cv2.waitKey(1) & 0xFF == ord('q'):
                video_running = False
                break
    finally:
        if processing_future is not None and not processing_future.done():
            processing_future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        cap.release()
        cv2.destroyAllWindows()
        print("Vídeo encerrado.")


print('\r\n\r\nTello Python3 Demo com Vídeo.\r\n')
print(describe_network_plan(TELLO_CONFIG))
print("")

print('Tello: command takeoff land flip forward back left right')
print('       up down cw ccw speed speed? battery? streamon streamoff')
print('end -- quit demo.\r\n')

# recvThread create
recvThread = threading.Thread(target=recv)
recvThread.daemon = True
recvThread.start()

while True:
    try:
        python_version = str(platform.python_version())
        version_init_num = int(python_version.partition('.')[0])

        if version_init_num == 3:
            msg = input("")
        elif version_init_num == 2:
            msg = raw_input("")

        if not msg:
            continue

        msg = msg.strip()

        if msg.lower() == 'end':
            print('Encerrando...')
            video_running = False
            sock.close()
            break

        # Envia comando para o Tello
        sent = sock.sendto(msg.encode(encoding="utf-8"), tello_address)

        # Se o usuário digitar streamon, abre a janela de vídeo
        if msg.lower() == "streamon":
            time.sleep(2)

            if not video_running:
                video_running = True
                videoThread = threading.Thread(target=video_stream)
                videoThread.daemon = True
                videoThread.start()

        # Se o usuário digitar streamoff, fecha a janela de vídeo
        if msg.lower() == "streamoff":
            video_running = False

    except KeyboardInterrupt:
        print('\n . . .\n')
        video_running = False
        sock.close()
        break
