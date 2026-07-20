import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO

from src.visao_computacional.ocr.config import load_ocr_config
from src.visao_computacional.ocr.pipeline import generate_plate_image_candidates
from src.visao_computacional.yolo26.plate_recognizer import _resolve_video_source


MODEL_PATH = Path(__file__).resolve().parent.parent / "yolo26" / "license_plate_best.pt"
OCR_CONFIG = load_ocr_config()
CONF_THRESH = 0.1


def _ensure_color(image):
    if image is None:
        return None
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def _resize_for_panel(image, height=220):
    image = _ensure_color(image)
    if image is None or image.size == 0:
        return None
    scale = height / max(1, image.shape[0])
    width = max(1, int(image.shape[1] * scale))
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)


def _add_label(image, label):
    image = image.copy()
    cv2.rectangle(image, (0, 0), (image.shape[1], 32), (0, 0, 0), -1)
    cv2.putText(image, label, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return image


def _build_comparison_image(original_roi, processed_roi):
    original_panel = _add_label(_resize_for_panel(original_roi), "ROI original")
    processed_panel = _add_label(_resize_for_panel(processed_roi), "ROI processada")

    target_height = max(original_panel.shape[0], processed_panel.shape[0])

    def _pad(image):
        if image.shape[0] == target_height:
            return image
        pad = target_height - image.shape[0]
        return cv2.copyMakeBorder(image, 0, pad, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    original_panel = _pad(original_panel)
    processed_panel = _pad(processed_panel)
    gap = 255 * (original_panel[:, :20] * 0 + 1)
    return cv2.hconcat([original_panel, gap, processed_panel])


def _save_outputs(frame, bbox, original_roi, processed_roi, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    x1, y1, x2, y2 = bbox
    annotated = frame.copy()
    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 3)

    comparison = _build_comparison_image(original_roi, processed_roi)

    frame_path = output_dir / "frame_camera_bbox.png"
    original_path = output_dir / "roi_original_camera.png"
    processed_path = output_dir / "roi_processada_camera.png"
    comparison_path = output_dir / "roi_comparacao_camera.png"

    cv2.imwrite(str(frame_path), annotated)
    cv2.imwrite(str(original_path), original_roi)
    cv2.imwrite(str(processed_path), processed_roi)
    cv2.imwrite(str(comparison_path), comparison)

    return frame_path, original_path, processed_path, comparison_path


def main():
    parser = argparse.ArgumentParser(description="Abre a câmera e salva a ROI da placa antes e depois do tratamento de imagem.")
    parser.add_argument("--source", default="0", help="Fonte de vídeo. Use 0 para webcam local, caminho de arquivo ou URL.")
    parser.add_argument("--output-dir", default="docs/static/img/sprint4", help="Diretório para salvar as imagens de comparação.")
    args = parser.parse_args()

    model = YOLO(str(MODEL_PATH))
    cap = cv2.VideoCapture(_resolve_video_source(args.source))
    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir a camera/fonte: {args.source}")

    last_detection = None

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        preview = frame.copy()
        results = model(frame, verbose=False)
        detected_roi = None

        for result in results:
            for box in result.boxes:
                conf = float(box.conf.item())
                if conf < CONF_THRESH:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy.cpu().numpy()[0])
                roi = frame[y1:y2, x1:x2]
                if roi is None or roi.size == 0:
                    continue

                candidates = generate_plate_image_candidates(roi, mode=OCR_CONFIG.mode, config=OCR_CONFIG)
                if not candidates:
                    continue

                processed = candidates[0]["image"]
                last_detection = {
                    "bbox": [x1, y1, x2, y2],
                    "original_roi": roi,
                    "processed_roi": processed,
                }
                detected_roi = roi
                cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(preview, "Placa detectada - pressione S para salvar", (x1, max(30, y1 - 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                break
            if detected_roi is not None:
                break

        cv2.putText(preview, "Q: sair | S: salvar comparacao", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imshow("OCR camera comparison", preview)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s") and last_detection is not None:
            frame_path, original_path, processed_path, comparison_path = _save_outputs(
                frame,
                last_detection["bbox"],
                last_detection["original_roi"],
                last_detection["processed_roi"],
                Path(args.output_dir),
            )
            print("Imagens salvas:")
            print(frame_path)
            print(original_path)
            print(processed_path)
            print(comparison_path)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
