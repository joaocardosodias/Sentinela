"""
Modelo do fine tuning:
https://colab.research.google.com/drive/1UXTbqkUaAp-qYKDlbPn3vqOSIH38I2wb?usp=sharing
"""

import argparse
import os
import time
from collections import defaultdict, deque
from pathlib import Path

import cv2
import easyocr
from dotenv import load_dotenv
from ultralytics import YOLO

from src.visao_computacional.ocr.config import load_ocr_config
from src.visao_computacional.ocr.metrics import OcrRuntimeMetrics
from src.visao_computacional.ocr.pipeline import (
    OcrCooldown,
    PlateTemporalBuffer,
    read_plate_from_roi,
)
from src.visao_computacional.ocr.plate_text import empty_plate_info

MODEL_PATH = Path(__file__).resolve().with_name("license_plate_best.pt")
OCR_CONFIG = load_ocr_config()

load_dotenv()

OCR_PROVIDER = os.getenv("OCR_PROVIDER", "easyocr").strip().lower()
OCR_COMPARE_PRIMARY = os.getenv("OCR_COMPARE_PRIMARY", "paddle").strip().lower()

model = None
easyocr_reader = None
easyocr_import_error = None
paddle_reader = None
paddle_import_error = None


def torch_accelerator_available():
    try:
        import torch

        has_cuda = torch.cuda.is_available()
        has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        return has_cuda or has_mps
    except Exception:
        return False


model = YOLO(str(MODEL_PATH))
reader = easyocr.Reader(["en"], gpu=torch_accelerator_available())


plate_history = defaultdict(lambda: deque(maxlen=10))
plate_final = {}
temporal_buffer = PlateTemporalBuffer(maxlen=5, min_repetitions=2)
ocr_cooldown = OcrCooldown(
    valid_frames=OCR_CONFIG.cooldown_frames_valid,
    invalid_frames=OCR_CONFIG.cooldown_frames_invalid,
)

CONF_THRESH = 0.1


runtime_metrics = OcrRuntimeMetrics(log_interval_frames=max(1, OCR_CONFIG.log_interval_frames))



def get_box_id(x1, y1, x2, y2):
    return f"{int(x1/10)}_{int(y1/10)}_{int(x2/10)}_{int(y2/10)}"


def get_stable_plate_info(box_id, plate_info, bbox):
    if plate_info["valid"]:
        plate_history[box_id].append(plate_info)
        temporal_buffer.add_reading(bbox, plate_info["plate"], plate_info.get("confidence", 0.0))

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
                        "confidence": item.get("confidence", 0.0),
                    }
                    break

    temporal_match = temporal_buffer.get_stable_reading(bbox)
    if temporal_match and box_id in plate_final:
        plate_final[box_id]["confidence"] = max(
            plate_final[box_id].get("confidence", 0.0),
            temporal_match.get("confidence", 0.0),
        )

    return plate_final.get(box_id, empty_plate_info())


def recognize_plate(plate_crop):
    return read_plate_from_roi(reader, plate_crop, mode=OCR_CONFIG.mode, config=OCR_CONFIG)


def process_frame(frame):
    """
    Recebe um frame (numpy array BGR), roda YOLO + OCR,
    desenha as anotacoes no frame e retorna os resultados.

    Returns:
        frame: frame anotado com bounding boxes e labels
        frame_results: lista de dicts com os dados da placa detectada
    """
    process_started_at = time.perf_counter()
    frame_results = []
    process_frame.frame_id = getattr(process_frame, "frame_id", 0) + 1
    frame_id = process_frame.frame_id

    yolo_started_at = time.perf_counter()
    results = model(frame, verbose=False)
    yolo_time_ms = (time.perf_counter() - yolo_started_at) * 1000

    for r in results:
        boxes = r.boxes
        for box in boxes:
            conf = float(box.conf.item())
            if conf < CONF_THRESH:
                continue
            runtime_metrics.update_detection()

            x1, y1, x2, y2 = map(int, box.xyxy.cpu().numpy()[0])

            crop_started_at = time.perf_counter()
            plate_crop = frame[y1:y2, x1:x2]
            crop_time_ms = (time.perf_counter() - crop_started_at) * 1000
            bbox = [x1, y1, x2, y2]

            if OCR_CONFIG.cooldown_enabled:
                should_process, cached_entry = ocr_cooldown.should_process(bbox, frame_id)
                if not should_process:
                    runtime_metrics.update_skipped("cooldown")
                    cached_result = dict(cached_entry["result"])
                    plate_info = cached_result
                    plate_info["skipped_reason"] = "cooldown"
                    plate_info["ocr_attempted"] = False
                    plate_info.setdefault("preprocess_time_ms", 0.0)
                    plate_info.setdefault("easyocr_time_ms", 0.0)
                    plate_info.setdefault("total_ocr_time_ms", 0.0)
                    plate_info.setdefault("candidates_tested", 0)
                else:
                    plate_info = None
            else:
                plate_info = None

            if plate_info is None:
                plate_info = recognize_plate(plate_crop)
                if plate_info.get("status") == "skipped":
                    runtime_metrics.update_skipped(
                        plate_info.get("skipped_reason", plate_info.get("reason", "skipped")),
                        plate_info.get("quality_info"),
                    )
                if OCR_CONFIG.cooldown_enabled:
                    ocr_cooldown.update(bbox, plate_info, frame_id)
            text = plate_info["plate"]
            plate_format = plate_info["format"]
            box_id = get_box_id(x1, y1, x2, y2)
            stable_info = get_stable_plate_info(box_id, plate_info, bbox)
            stable_text = stable_info["plate"]
            stable_format = stable_info["format"]

            final_plate = stable_text or text
            final_format = stable_format if stable_text else plate_format
            is_valid = stable_info["valid"] or plate_info["valid"]

            result_info = {
                "plate": final_plate,
                "format": final_format,
                "raw_text": plate_info["raw_text"],
                "valid": is_valid,
                "confidence": conf,
                "bbox": bbox,
                "timestamp": time.time(),
                "ocr_confidence": plate_info.get("confidence", 0.0),
                "preprocess_name": plate_info.get("preprocess_name", ""),
                "preprocess_time_ms": plate_info.get("preprocess_time_ms", 0.0),
                "easyocr_time_ms": plate_info.get("easyocr_time_ms", 0.0),
                "total_ocr_time_ms": plate_info.get("total_ocr_time_ms", 0.0),
                "candidates_tested": plate_info.get("candidates_tested", 0),
                "used_fallback": plate_info.get("used_fallback", False),
                "ocr_attempted": plate_info.get("ocr_attempted", False),
                "skipped_reason": plate_info.get("skipped_reason"),
                "crop_time_ms": crop_time_ms,
                "yolo_time_ms": yolo_time_ms,
            }
            if "ocr_comparison" in plate_info:
                result_info["ocr_comparison"] = plate_info["ocr_comparison"]

            frame_results.append(result_info)
            runtime_metrics.update_attempt(
                {
                    "valid": is_valid,
                    "ocr_attempted": plate_info.get("ocr_attempted", False),
                    "preprocess_time_ms": plate_info.get("preprocess_time_ms", 0.0),
                    "easyocr_time_ms": plate_info.get("easyocr_time_ms", 0.0),
                    "total_ocr_time_ms": plate_info.get("total_ocr_time_ms", 0.0),
                    "candidates_tested": plate_info.get("candidates_tested", 0),
                    "used_fallback": plate_info.get("used_fallback", False),
                    "quality_info": plate_info.get("quality_info"),
                }
            )

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

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

    process_frame_ms = (time.perf_counter() - process_started_at) * 1000
    runtime_metrics.update_frame(process_frame_ms)
    runtime_metrics.log_if_needed(frame_id)
    return frame, frame_results


def _resolve_video_source(source):
    if isinstance(source, int):
        return source

    normalized = str(source).strip()
    if normalized.isdigit():
        return int(normalized)

    return normalized


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teste local do detector de placas com webcam, vídeo ou stream UDP.")
    parser.add_argument(
        "--source",
        default="udp://0.0.0.0:11111",
        help="Fonte de vídeo. Use 0 para webcam local, caminho de arquivo ou URL UDP.",
    )
    args = parser.parse_args()

    input_video = _resolve_video_source(args.source)

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir a camera/fonte: {args.source}")

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
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
