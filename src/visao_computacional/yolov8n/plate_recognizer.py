''' 
Modelo do fine tunning
https://colab.research.google.com/drive/1DjqOnKIXzIr9KiI-3bLIQwIbEntpjh2L#scrollTo=eSMj10nqfopx&uniqifier=2 
'''

import cv2 
import numpy as np 
from ultralytics import YOLO 
import easyocr
import re
import time
from collections import defaultdict, deque
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().with_name("license_plate_best.pt")


def torch_accelerator_available():
    try:
        import torch

        has_cuda = torch.cuda.is_available()
        has_mps = (
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        )
        return has_cuda or has_mps
    except Exception:
        return False


# Initialize YOLO & OCR
model = YOLO(str(MODEL_PATH))  # weights
reader = easyocr.Reader(['en'], gpu=torch_accelerator_available())

# Regex: O projeto final prioriza Brasil, mas mantemos UK como fallback de teste.
uk_model = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z]{3}$")
old_model_br = re.compile(r"^[A-Z]{3}[0-9]{4}$")
mercosul_model_br = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")

# O OCR costuma confundir letras e números parecidos.
NUM_TO_ALPHA = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "5": "S",
    "8": "B",
}

ALPHA_TO_NUM = {
    "O": "0",
    "I": "1",
    "Z": "2",
    "S": "5",
    "B": "8",
}


def clean_plate_text(text):
    # Normaliza o texto para só letras maiúsculas e números.
    text = text.upper().replace(" ", "").replace("-", "")
    return re.sub(r"[^A-Z0-9]", "", text)


def correct_plate_format_old(ocr_text):
    # Padrão antigo brasileiro: LLLNNNN
    ocr_text = clean_plate_text(ocr_text)
    if len(ocr_text) != 7:
        return ""

    corrected = []

    for i, ch in enumerate(ocr_text):
        if i < 3:
            if ch.isdigit() and ch in NUM_TO_ALPHA:
                corrected.append(NUM_TO_ALPHA[ch])
            elif ch.isalpha():
                corrected.append(ch)
            else:
                return ""
        else:
            if ch.isdigit():
                corrected.append(ch)
            elif ch.isalpha() and ch in ALPHA_TO_NUM:
                corrected.append(ALPHA_TO_NUM[ch])
            else:
                return ""

    candidate = "".join(corrected)
    return candidate if old_model_br.fullmatch(candidate) else ""


def correct_plate_format_mercosul(ocr_text):
    # Padrão Mercosul brasileiro: LLLNLNN
    ocr_text = clean_plate_text(ocr_text)
    if len(ocr_text) != 7:
        return ""

    corrected = []

    for i, ch in enumerate(ocr_text):
        if i < 3 or i == 4:
            if ch.isdigit() and ch in NUM_TO_ALPHA:
                corrected.append(NUM_TO_ALPHA[ch])
            elif ch.isalpha():
                corrected.append(ch)
            else:
                return ""
        else:
            if ch.isdigit():
                corrected.append(ch)
            elif ch.isalpha() and ch in ALPHA_TO_NUM:
                corrected.append(ALPHA_TO_NUM[ch])
            else:
                return ""

    candidate = "".join(corrected)
    return candidate if mercosul_model_br.fullmatch(candidate) else ""


def correct_plate_format_uk(ocr_text):
    # Formato de teste UK: AA00AAA
    ocr_text = clean_plate_text(ocr_text)
    return ocr_text if uk_model.fullmatch(ocr_text) else ""


def empty_plate_info():
    return {
        "plate": "",
        "format": "UNKNOWN",
        "raw_text": "",
        "valid": False,
    }

def recognize_plate(plate_crop):
    if plate_crop.size == 0:
        return empty_plate_info()
    
    # Pré-processamento para melhorar o OCR.
    gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    plate_resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    best_info = empty_plate_info()

    try: 
        ocr_result = reader.readtext(
            plate_resized, 
            detail=0, 
            allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        )

        for raw_text in ocr_result:
            cleaned = clean_plate_text(raw_text)
            if not cleaned:
                continue

            candidate = correct_plate_format_old(cleaned)
            if candidate:
                return {
                    "plate": candidate,
                    "format": "BR_OLD",
                    "raw_text": cleaned,
                    "valid": True,
                }

            candidate = correct_plate_format_mercosul(cleaned)
            if candidate:
                return {
                    "plate": candidate,
                    "format": "BR_MERCOSUL",
                    "raw_text": cleaned,
                    "valid": True,
                }

            candidate = correct_plate_format_uk(cleaned)
            if candidate:
                if not best_info["valid"]:
                    best_info = {
                        "plate": candidate,
                        "format": "UK_TEST",
                        "raw_text": cleaned,
                        "valid": True,
                    }

    except: 
        pass
    
    return best_info

plate_history = defaultdict(lambda: deque(maxlen=10)) # last 10
plate_final = {}

def get_box_id(x1, y1, x2, y2):
    # Usa coordenadas arredondadas como pseudo ID.
    return f"{int(x1/10)}_{int(y1/10)}_{int(x2/10)}_{int(y2/10)}"

def get_stable_plate_info(box_id, plate_info):
    if plate_info["valid"]:
        plate_history[box_id].append(plate_info)

        plates = [item["plate"] for item in plate_history[box_id] if item["plate"]]
        if plates:
            most_common_plate = max(set(plates), key=plates.count)

            for item in reversed(plate_history[box_id]):
                if item["plate"] == most_common_plate:
                    plate_final[box_id] = {
                        "plate": most_common_plate,
                        "format": item["format"],
                        "raw_text": item["raw_text"],
                        "valid": True,
                    }
                    break

    return plate_final.get(box_id, empty_plate_info())


CONF_THRESH = 0.3 #confiança - voltar aqui para ver com base na regra de negocio

def process_frame(frame):
    """
    Recebe um frame (numpy array BGR), roda YOLO + OCR,
    desenha as anotações no frame e retorna os resultados.

    Returns:
        frame:        frame anotado com bounding boxes e labels
        frame_results: lista de dicts com plate, format, raw_text, valid, confidence, bbox, timestamp
    """
    frame_results = []

    results = model(frame, verbose=False)

    for r in results: 
        boxes = r.boxes
        for box in boxes:
            conf = float(box.conf.item()) #calculo da confiança
            if conf < CONF_THRESH: 
                continue
    
            x1, y1, x2, y2 = map(int, box.xyxy.cpu().numpy()[0])
            plate_crop = frame[y1:y2, x1:x2]

            # OCR com validação por formato.
            plate_info = recognize_plate(plate_crop)
            text = plate_info["plate"]
            plate_format = plate_info["format"]

            # Estabiliza o resultado usando o histórico da mesma região.
            box_id = get_box_id(x1, y1, x2, y2)
            stable_info = get_stable_plate_info(box_id, plate_info)
            stable_text = stable_info["plate"]
            stable_format = stable_info["format"]

            result_info = {
                "plate": stable_text or text,
                "format": stable_format if stable_text else plate_format,
                "raw_text": plate_info["raw_text"],
                "valid": stable_info["valid"] or plate_info["valid"],
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "timestamp": time.time(),
            }
            frame_results.append(result_info)

            cv2.rectangle(frame, (x1,y1), (x2,y2), (0, 255, 0), 3)

            # Mostra a placa estável e o tipo reconhecido.
            if stable_text:
                label = f"{stable_text} | {stable_format}"
            elif text:
                label = f"{text} | {plate_format}"
            else:
                label = ""

            if label:
                text_y = max(30, y1 - 20)
                cv2.putText(
                    frame, 
                    label, 
                    (x1, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4
                )
                cv2.putText(
                    frame, 
                    label, 
                    (x1, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2
                )

    return frame, frame_results


# Permite rodar o arquivo diretamente para testar com webcam
if __name__ == "__main__":
    import sys

    SRC_DIR = Path(__file__).resolve().parents[2]
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    from drone.network_routes import load_tello_config

    input_video = load_tello_config().video_url

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise RuntimeError("Nao foi possivel abrir a camera.")

    detected_results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, frame_results = process_frame(frame)

        if frame_results:
            detected_results.extend(frame_results)
            print(frame_results)

        cv2.imshow("Annotated Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
