import time
from collections import defaultdict, deque

import cv2

from .config import load_ocr_config
from .plate_text import (
    clean_plate_text,
    correct_plate_format_mercosul,
    correct_plate_format_old,
    correct_plate_format_uk,
    empty_plate_info,
    validate_plate_text,
)
from .quality import should_run_ocr_on_roi


def resize_plate(roi, scale=2.0):
    """
    Upscaling simples da ROI antes do OCR.
    """

    if roi is None or roi.size == 0:
        return roi
    return cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def _to_gray(image):
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _apply_light_blur(image, kernel_size=(3, 3), sigma=0):
    # Blur leve reduz ruido fino sem tentar "embelezar" demais a ROI.
    return cv2.GaussianBlur(image, kernel_size, sigma)


def _apply_crop_padding(image, padding_ratio=0.05):
    if image is None or image.size == 0 or padding_ratio <= 0:
        return image
    height, width = image.shape[:2]
    pad_y = max(1, int(height * padding_ratio))
    pad_x = max(1, int(width * padding_ratio))
    return cv2.copyMakeBorder(
        image,
        pad_y,
        pad_y,
        pad_x,
        pad_x,
        borderType=cv2.BORDER_REPLICATE,
    )


def _optimize_plate_crop(image, config):
    optimized = image
    if getattr(config, "enable_padding", False):
        optimized = _apply_crop_padding(optimized, getattr(config, "padding_ratio", 0.0))
    return optimized


def _build_candidate(name, image, experimental, preprocess_time_ms):
    return {
        "name": name,
        "image": image,
        "experimental": experimental,
        "preprocess_time_ms": preprocess_time_ms,
    }


def _timed_candidate(name, builder, experimental):
    started_at = time.perf_counter()
    image = builder()
    preprocess_time_ms = (time.perf_counter() - started_at) * 1000
    return _build_candidate(name, image, experimental, preprocess_time_ms)


def generate_plate_image_candidates(roi, mode="runtime", config=None):
    """
    Gera candidatos leves para OCR.

    No perfil `fast`, o runtime deve usar apenas um candidato por ROI. Mantemos
    a estrutura em lista para preservar o contrato do restante da pipeline.
    """

    config = config or load_ocr_config()
    if roi is None or roi.size == 0:
        return []

    optimized_crop = _optimize_plate_crop(roi, config)
    candidates = []

    candidates.append(
        _timed_candidate(
            "resized_color",
            lambda: resize_plate(optimized_crop, 2.0),
            False,
        )
    )

    gray = _to_gray(optimized_crop)
    candidates.append(
        _timed_candidate(
            "gray_resized",
            lambda: resize_plate(gray, 2.0),
            False,
        )
    )

    gray_resized = candidates[-1]["image"]
    candidates.append(
        _timed_candidate(
            "gray_blur_light",
            lambda: _apply_light_blur(gray_resized, (3, 3), 0),
            False,
        )
    )

    if mode != "runtime":
        return candidates

    order = [config.primary_preprocess, config.secondary_preprocess]
    selected = []
    for name in order:
        for candidate in candidates:
            if candidate["name"] == name and candidate not in selected:
                selected.append(candidate)
    for candidate in candidates:
        if candidate["name"] not in order and not candidate["experimental"]:
            selected.append(candidate)
    return selected[: max(1, config.max_candidates_runtime)]


def generate_ocr_image_candidates(roi, mode="runtime", config=None):
    return generate_plate_image_candidates(roi, mode=mode, config=config)


def normalize_ocr_result(raw_text):
    return "".join(ch for ch in (raw_text or "").upper() if ch.isalnum())


def run_ocr_on_candidates(reader, image_candidates, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    results = []

    for candidate in image_candidates:
        started_at = time.perf_counter()
        try:
            ocr_output = reader.readtext(candidate["image"], allowlist=allowlist, detail=1)
        except Exception:
            ocr_output = []

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        if not ocr_output:
            results.append(
                {
                    "text_raw": "",
                    "text_clean": "",
                    "confidence": 0.0,
                    "preprocess_name": candidate["name"],
                    "experimental": candidate.get("experimental", False),
                    "ocr_time_ms": elapsed_ms,
                    "preprocess_time_ms": candidate.get("preprocess_time_ms", 0.0),
                }
            )
            continue

        for _, raw_text, confidence in ocr_output:
            results.append(
                {
                    "text_raw": raw_text,
                    "text_clean": normalize_ocr_result(raw_text),
                    "confidence": float(confidence),
                    "preprocess_name": candidate["name"],
                    "experimental": candidate.get("experimental", False),
                    "ocr_time_ms": elapsed_ms,
                    "preprocess_time_ms": candidate.get("preprocess_time_ms", 0.0),
                }
            )

    return results


def correct_homoglyphs_by_plate_format(text):
    """
    Tenta corrigir ambiguidades comuns de OCR respeitando formatos conhecidos.
    """

    cleaned = clean_plate_text(text)
    for formatter in (
        correct_plate_format_old,
        correct_plate_format_mercosul,
        correct_plate_format_uk,
    ):
        candidate = formatter(cleaned)
        if candidate:
            return candidate
    return cleaned


def has_partial_plate_hint(text_clean):
    if not text_clean or len(text_clean) < 4:
        return False
    has_alpha = any(ch.isalpha() for ch in text_clean)
    has_digit = any(ch.isdigit() for ch in text_clean)
    return has_alpha or has_digit


def select_best_ocr_candidate(candidates, validators=None, config=None):
    config = config or load_ocr_config()
    del config
    validators = validators or []

    aggressiveness_rank = {
        "resized_color": 0,
        "gray_resized": 1,
        "gray_blur_light": 2,
        "clahe": 2,
        "bilateral": 2,
        "sharpen_light": 3,
        "threshold_experimental": 4,
    }

    valid_candidates = []
    total_ocr_time_ms = sum(candidate.get("ocr_time_ms", 0.0) for candidate in candidates)

    for candidate in candidates:
        text_clean = candidate.get("text_clean") or normalize_ocr_result(candidate.get("text_raw", ""))
        for validator in validators:
            validation = validator(text_clean)
            if validation and validation.get("valid"):
                enriched = dict(candidate)
                enriched.update(
                    {
                        "plate": validation["plate"],
                        "plate_format": validation["format"],
                        "is_valid_plate": True,
                        "text_clean": validation["raw_text"],
                        "total_ocr_time_ms": total_ocr_time_ms,
                    }
                )
                valid_candidates.append(enriched)
                break

    if not valid_candidates:
        return None

    valid_candidates.sort(
        key=lambda item: (
            -item.get("confidence", 0.0),
            aggressiveness_rank.get(item.get("preprocess_name"), 99),
            item.get("ocr_time_ms", 0.0),
        )
    )

    best = dict(valid_candidates[0])
    best["format"] = best.pop("plate_format")
    return best


def _build_empty_runtime_result(reason="", quality_info=None):
    result = empty_plate_info()
    result.update(
        {
            "status": "invalid",
            "reason": reason,
            "quality_info": quality_info or {},
            "preprocess_name": "",
            "preprocess_time_ms": 0.0,
            "easyocr_time_ms": 0.0,
            "total_ocr_time_ms": 0.0,
            "candidates_tested": 0,
            "used_fallback": False,
            "ocr_attempted": False,
            "timing": {
                "preprocess_ms": 0.0,
                "easyocr_ms": 0.0,
                "total_ms": 0.0,
            },
        }
    )
    return result

def _finalize_result(result, preprocess_time_ms, easyocr_time_ms, quality_info, candidates_tested):
    result["preprocess_time_ms"] = preprocess_time_ms
    result["easyocr_time_ms"] = easyocr_time_ms
    result["total_ocr_time_ms"] = preprocess_time_ms + easyocr_time_ms
    result["quality_info"] = quality_info or {}
    result["candidates_tested"] = candidates_tested
    result["timing"] = {
        "preprocess_ms": preprocess_time_ms,
        "easyocr_ms": easyocr_time_ms,
        "total_ms": preprocess_time_ms + easyocr_time_ms,
    }
    return result


def read_plate_from_roi(reader, roi, bbox=None, mode="runtime", config=None):
    """
    API de alto nivel consumida pelo runtime de deteccao.

    O objetivo desta funcao e esconder os detalhes internos de preprocessamento,
    OCR e validacao atras de um contrato unico e mais simples.
    """

    config = config or load_ocr_config()
    if roi is None:
        return _build_empty_runtime_result(reason="invalid_crop")
    if roi.size == 0:
        return _build_empty_runtime_result(reason="empty_crop")

    quality_info = {"should_run": True, "reason": "passed"}
    if config.quality_filter_enabled:
        should_run, quality_info = should_run_ocr_on_roi(roi, bbox=bbox, config=config)
        if not should_run:
            result = _build_empty_runtime_result(reason=quality_info["reason"], quality_info=quality_info)
            result["status"] = "skipped"
            result["skipped_reason"] = quality_info["reason"]
            return result

    image_candidates = generate_ocr_image_candidates(roi, mode=mode, config=config)
    if not image_candidates:
        return _build_empty_runtime_result(reason="no_candidates", quality_info=quality_info)

    collected_results = []
    selected = None
    preprocess_time_ms = 0.0
    easyocr_time_ms = 0.0
    if mode == "runtime":
        primary_candidate = image_candidates[0]
        preprocess_time_ms += primary_candidate.get("preprocess_time_ms", 0.0)
        current_results = run_ocr_on_candidates(reader, [primary_candidate])
        easyocr_time_ms += sum(item.get("ocr_time_ms", 0.0) for item in current_results)
        collected_results.extend(current_results)
        selected = select_best_ocr_candidate(collected_results, validators=[validate_plate_text], config=config)
    else:
        preprocess_time_ms = sum(item.get("preprocess_time_ms", 0.0) for item in image_candidates)
        collected_results = run_ocr_on_candidates(reader, image_candidates)
        easyocr_time_ms = sum(item.get("ocr_time_ms", 0.0) for item in collected_results)
        selected = select_best_ocr_candidate(collected_results, validators=[validate_plate_text], config=config)

    if selected is None:
        best_raw = max(collected_results, key=lambda item: item.get("confidence", 0.0), default=None)
        result = _build_empty_runtime_result(reason="regex_failed", quality_info=quality_info)
        result.update(
            {
                "status": "invalid",
                "reason": "regex_failed",
                "raw_text": best_raw.get("text_raw", "") if best_raw else "",
                "text_raw": best_raw.get("text_raw", "") if best_raw else "",
                "text_clean": correct_homoglyphs_by_plate_format(best_raw.get("text_clean", "")) if best_raw else "",
                "confidence": best_raw.get("confidence", 0.0) if best_raw else 0.0,
                "preprocess_name": best_raw.get("preprocess_name", image_candidates[0]["name"]) if best_raw else image_candidates[0]["name"],
                "ocr_attempted": True,
            }
        )
        result = _finalize_result(
            result,
            preprocess_time_ms,
            easyocr_time_ms,
            quality_info,
            max(1, len(collected_results)),
        )
    else:
        result = {
            "status": "valid",
            "reason": "",
            "plate": selected["plate"],
            "format": selected["format"],
            "raw_text": selected["text_clean"],
            "text_raw": selected.get("text_raw", ""),
            "text_clean": selected["text_clean"],
            "valid": True,
            "confidence": selected["confidence"],
            "preprocess_name": selected["preprocess_name"],
            "used_fallback": False,
            "ocr_attempted": True,
        }
        result = _finalize_result(
            result,
            preprocess_time_ms,
            easyocr_time_ms,
            quality_info,
            max(1, len(collected_results)),
        )

    return result


class PlateTemporalBuffer:
    """
    Estabiliza leituras ao longo de poucos frames sem mudar a API principal.
    """

    def __init__(self, maxlen=5, min_repetitions=2):
        self.maxlen = maxlen
        self.min_repetitions = min_repetitions
        self._history = defaultdict(lambda: deque(maxlen=maxlen))

    def _bbox_key(self, bbox):
        x1, y1, x2, y2 = bbox
        return f"{int(x1/10)}_{int(y1/10)}_{int(x2/10)}_{int(y2/10)}"

    def add_reading(self, bbox, plate_text, confidence):
        if plate_text:
            self._history[self._bbox_key(bbox)].append((plate_text, confidence))

    def get_stable_reading(self, bbox):
        history = list(self._history.get(self._bbox_key(bbox), []))
        if len(history) < self.min_repetitions:
            return None

        counts = defaultdict(list)
        for plate_text, confidence in history:
            counts[plate_text].append(confidence)

        best_text = max(counts, key=lambda text: (len(counts[text]), sum(counts[text]) / len(counts[text])))
        if len(counts[best_text]) < self.min_repetitions:
            return None

        return {
            "plate": best_text,
            "confidence": sum(counts[best_text]) / len(counts[best_text]),
            "repetitions": len(counts[best_text]),
        }


class OcrCooldown:
    """
    Evita repetir OCR na mesma bbox em frames muito proximos.
    """

    def __init__(self, valid_frames=30, invalid_frames=10):
        self.valid_frames = valid_frames
        self.invalid_frames = invalid_frames
        self._entries = {}

    def _bbox_key(self, bbox):
        x1, y1, x2, y2 = bbox
        return f"{int(x1/10)}_{int(y1/10)}_{int(x2/10)}_{int(y2/10)}"

    def should_process(self, bbox, current_frame_id):
        key = self._bbox_key(bbox)
        entry = self._entries.get(key)
        if entry is None:
            return True, None

        last_frame_id = entry["frame_id"]
        cooldown = self.valid_frames if entry["valid"] else self.invalid_frames
        if current_frame_id - last_frame_id < cooldown:
            return False, entry
        return True, entry

    def update(self, bbox, result, current_frame_id):
        self._entries[self._bbox_key(bbox)] = {
            "frame_id": current_frame_id,
            "valid": bool(result.get("valid")),
            "result": dict(result),
        }
