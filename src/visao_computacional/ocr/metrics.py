import csv
import json
import math
import statistics
import time
from collections import Counter
from pathlib import Path

import cv2

from .config import OCRConfig
from .pipeline import (
    generate_ocr_image_candidates,
    read_plate_from_roi,
    run_ocr_on_candidates,
    select_best_ocr_candidate,
)
from .plate_text import validate_plate_text


class OcrRuntimeMetrics:
    """
    Agrega metricas operacionais do OCR sem poluir `plate_recognizer.py`.
    """

    def __init__(self, log_interval_frames):
        self.log_interval_frames = log_interval_frames
        self.frames_processed = 0
        self.plates_detected = 0
        self.ocr_attempts = 0
        self.valid_plates = 0
        self.fallbacks_used = 0
        self.process_frame_ms = []
        self.preprocess_time_ms = []
        self.easyocr_time_ms = []
        self.total_ocr_time_ms = []
        self.runtime_candidates = []
        self.quality_samples_all = []
        self.quality_samples_passed = []
        self.quality_samples_skipped = []
        self.skip_counters = Counter()

    def update_detection(self):
        self.plates_detected += 1

    def update_frame(self, process_frame_ms):
        self.frames_processed += 1
        self.process_frame_ms.append(process_frame_ms)

    def update_skipped(self, reason, quality_info=None):
        self.skip_counters[reason] += 1
        self._record_quality_sample(quality_info, bucket="skipped")

    def update_attempt(self, result_info):
        if result_info.get("ocr_attempted"):
            self.ocr_attempts += 1
            self.runtime_candidates.append(result_info.get("candidates_tested", 0))
            self.preprocess_time_ms.append(result_info.get("preprocess_time_ms", 0.0))
            self.easyocr_time_ms.append(result_info.get("easyocr_time_ms", 0.0))
            self.total_ocr_time_ms.append(result_info.get("total_ocr_time_ms", 0.0))

        if result_info.get("valid"):
            self.valid_plates += 1
        if result_info.get("used_fallback"):
            self.fallbacks_used += 1

        quality_info = result_info.get("quality_info")
        if result_info.get("ocr_attempted"):
            self._record_quality_sample(quality_info, bucket="passed")

    def _record_quality_sample(self, quality_info, bucket):
        if not quality_info:
            return
        self.quality_samples_all.append(quality_info)
        if bucket == "passed":
            self.quality_samples_passed.append(quality_info)
        elif bucket == "skipped":
            self.quality_samples_skipped.append(quality_info)

    def _mean(self, values):
        return statistics.mean(values) if values else 0.0

    def _p95(self, values):
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)
        return ordered[index]

    def _quality_mean(self, items, key):
        values = [item[key] for item in items if key in item]
        return self._mean(values)

    def summary(self):
        avg_process = self._mean(self.process_frame_ms)
        return {
            "frames_processed": self.frames_processed,
            "plates_detected": self.plates_detected,
            "ocr_attempts": self.ocr_attempts,
            "ocr_skipped_low_width": self.skip_counters["low_width"],
            "ocr_skipped_low_height": self.skip_counters["low_height"],
            "ocr_skipped_aspect_too_small": self.skip_counters["aspect_too_small"],
            "ocr_skipped_aspect_too_large": self.skip_counters["aspect_too_large"],
            "ocr_skipped_low_blur_variance": self.skip_counters["low_blur_variance"],
            "ocr_skipped_invalid_crop": self.skip_counters["invalid_crop"] + self.skip_counters["empty_crop"],
            "ocr_skipped_cooldown": self.skip_counters["cooldown"],
            "valid_plates": self.valid_plates,
            "avg_preprocess_time_ms": self._mean(self.preprocess_time_ms),
            "avg_easyocr_time_ms": self._mean(self.easyocr_time_ms),
            "avg_total_ocr_time_ms": self._mean(self.total_ocr_time_ms),
            "p95_total_ocr_time_ms": self._p95(self.total_ocr_time_ms),
            "estimated_fps": (1000.0 / avg_process) if avg_process > 0 else 0.0,
            "runtime_candidates_avg": self._mean(self.runtime_candidates),
            "fallbacks_used": self.fallbacks_used,
            "avg_roi_width": self._quality_mean(self.quality_samples_all, "width"),
            "avg_roi_height": self._quality_mean(self.quality_samples_all, "height"),
            "avg_roi_aspect_ratio": self._quality_mean(self.quality_samples_all, "aspect_ratio"),
            "avg_blur_variance_all": self._quality_mean(self.quality_samples_all, "blur_variance"),
            "avg_blur_variance_passed": self._quality_mean(self.quality_samples_passed, "blur_variance"),
            "avg_blur_variance_skipped": self._quality_mean(self.quality_samples_skipped, "blur_variance"),
        }

    def log_if_needed(self, frame_id):
        if frame_id == 0 or frame_id % self.log_interval_frames != 0:
            return
        summary = self.summary()
        print("[OCR_RUNTIME_METRICS]")
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"{key}={value:.2f}")
            else:
                print(f"{key}={value}")


def load_labels(labels_csv):
    labels_path = Path(labels_csv)
    if not labels_path.exists():
        return {}

    labels = {}
    with open(labels_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            labels[row["filename"]] = row["plate"]
    return labels


def edit_distance(left, right):
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)

    prev = list(range(len(right) + 1))
    for i, ch_left in enumerate(left, start=1):
        curr = [i]
        for j, ch_right in enumerate(right, start=1):
            insert_cost = curr[j - 1] + 1
            delete_cost = prev[j] + 1
            replace_cost = prev[j - 1] + (ch_left != ch_right)
            curr.append(min(insert_cost, delete_cost, replace_cost))
        prev = curr
    return prev[-1]


def build_baseline_candidates(image):
    resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return [
        {
            "name": "baseline_resized_color",
            "image": resized,
            "experimental": False,
            "preprocess_time_ms": 0.0,
        }
    ]


def run_pipeline(reader, image, config, mode_name):
    started_at = time.perf_counter()
    if mode_name == "baseline":
        candidates = build_baseline_candidates(image)
        preprocess_time_ms = 0.0
        ocr_results = run_ocr_on_candidates(reader, candidates)
        selected = select_best_ocr_candidate(ocr_results, validators=[validate_plate_text], config=config)
    else:
        result = read_plate_from_roi(reader, image, mode=config.mode, config=config)
        total_time_ms = (time.perf_counter() - started_at) * 1000
        if not result.get("valid"):
            return {
                "plate": None,
                "text_raw": result.get("text_raw", ""),
                "text_clean": result.get("text_clean", ""),
                "confidence": result.get("confidence", 0.0),
                "format": None,
                "valid_regex": False,
                "preprocess_name": result.get("preprocess_name", ""),
                "preprocess_time_ms": result.get("preprocess_time_ms", 0.0),
                "ocr_time_ms": result.get("easyocr_time_ms", 0.0),
                "total_time_ms": total_time_ms,
                "candidates_tested": result.get("candidates_tested", 0),
            }
        return {
            "plate": result["plate"],
            "text_raw": result.get("text_raw", ""),
            "text_clean": result.get("text_clean", ""),
            "confidence": result["confidence"],
            "format": result["format"],
            "valid_regex": True,
            "preprocess_name": result.get("preprocess_name", ""),
            "preprocess_time_ms": result.get("preprocess_time_ms", 0.0),
            "ocr_time_ms": result.get("easyocr_time_ms", 0.0),
            "total_time_ms": total_time_ms,
            "candidates_tested": result.get("candidates_tested", 0),
        }

    preprocess_time_ms = sum(candidate.get("preprocess_time_ms", 0.0) for candidate in candidates)
    total_time_ms = (time.perf_counter() - started_at) * 1000
    if selected is None:
        best_any = max(ocr_results, key=lambda item: item.get("confidence", 0.0), default=None)
        return {
            "plate": None,
            "text_raw": best_any.get("text_raw", "") if best_any else "",
            "text_clean": best_any.get("text_clean", "") if best_any else "",
            "confidence": best_any.get("confidence", 0.0) if best_any else 0.0,
            "format": None,
            "valid_regex": False,
            "preprocess_name": best_any.get("preprocess_name", "") if best_any else "",
            "preprocess_time_ms": preprocess_time_ms,
            "ocr_time_ms": sum(item.get("ocr_time_ms", 0.0) for item in ocr_results),
            "total_time_ms": total_time_ms,
            "candidates_tested": len(candidates),
        }

    return {
        "plate": selected["plate"],
        "text_raw": selected["text_raw"],
        "text_clean": selected["text_clean"],
        "confidence": selected["confidence"],
        "format": selected["format"],
        "valid_regex": True,
        "preprocess_name": selected["preprocess_name"],
        "preprocess_time_ms": preprocess_time_ms,
        "ocr_time_ms": sum(item.get("ocr_time_ms", 0.0) for item in ocr_results),
        "total_time_ms": total_time_ms,
        "candidates_tested": len(candidates),
    }


def _safe_mean(values):
    return statistics.mean(values) if values else 0.0


def _safe_ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def _p95(values):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)
    return ordered[index]


def summarize_results(results, labels):
    del labels
    total_samples = len(results)
    labeled_samples = sum(1 for item in results if item["expected_plate"] is not None)
    total_with_any_text = sum(1 for item in results if item["text_clean"])
    total_valid_regex = sum(1 for item in results if item["valid_regex"])
    total_exact_matches = sum(1 for item in results if item["exact_match"])
    valid_but_wrong = sum(1 for item in results if item["valid_regex"] and item["expected_plate"] and not item["exact_match"])
    false_negatives = sum(1 for item in results if item["expected_plate"] and not item["valid_regex"])

    cer_values = []
    for item in results:
        expected = item["expected_plate"]
        predicted = item["plate"]
        if expected:
            predicted = predicted or ""
            cer_values.append(edit_distance(predicted, expected) / max(1, len(expected)))

    confidences_all = [item["confidence"] for item in results if item["text_clean"]]
    confidences_valid = [item["confidence"] for item in results if item["valid_regex"]]
    confidences_exact = [item["confidence"] for item in results if item["exact_match"]]
    preprocess_times = [item["preprocess_time_ms"] for item in results]
    ocr_times = [item["ocr_time_ms"] for item in results]
    total_times = [item["total_time_ms"] for item in results]
    winning_versions = Counter(item["preprocess_name"] for item in results if item["valid_regex"] and item["preprocess_name"])

    return {
        "total_samples": total_samples,
        "labeled_samples": labeled_samples,
        "read_rate": _safe_ratio(total_with_any_text, total_samples),
        "valid_regex_rate": _safe_ratio(total_valid_regex, total_samples),
        "exact_accuracy": _safe_ratio(total_exact_matches, labeled_samples),
        "cer": _safe_mean(cer_values),
        "average_confidence_all": _safe_mean(confidences_all),
        "average_confidence_valid_regex": _safe_mean(confidences_valid),
        "average_confidence_exact_match": _safe_mean(confidences_exact),
        "false_positive_rate": _safe_ratio(valid_but_wrong, labeled_samples),
        "false_negative_rate": _safe_ratio(false_negatives, labeled_samples),
        "average_preprocess_time_ms": _safe_mean(preprocess_times),
        "average_ocr_time_ms": _safe_mean(ocr_times),
        "average_total_time_ms": _safe_mean(total_times),
        "min_total_time_ms": min(total_times) if total_times else 0.0,
        "max_total_time_ms": max(total_times) if total_times else 0.0,
        "p95_total_time_ms": _p95(total_times),
        "estimated_fps": (1000.0 / _safe_mean(total_times)) if _safe_mean(total_times) > 0 else 0.0,
        "winning_preprocess_versions": dict(winning_versions),
    }


def compare_summaries(baseline, new_pipeline):
    return {
        "valid_regex_rate_gain": new_pipeline["valid_regex_rate"] - baseline["valid_regex_rate"],
        "exact_accuracy_gain": new_pipeline["exact_accuracy"] - baseline["exact_accuracy"],
        "cer_delta": new_pipeline["cer"] - baseline["cer"],
        "false_positive_rate_delta": new_pipeline["false_positive_rate"] - baseline["false_positive_rate"],
        "false_negative_rate_delta": new_pipeline["false_negative_rate"] - baseline["false_negative_rate"],
        "average_total_time_ms_delta": new_pipeline["average_total_time_ms"] - baseline["average_total_time_ms"],
        "estimated_fps_delta": new_pipeline["estimated_fps"] - baseline["estimated_fps"],
    }


def build_recommendation(new_pipeline):
    winners = sorted(
        new_pipeline["winning_preprocess_versions"].items(),
        key=lambda item: item[1],
        reverse=True,
    )
    runtime_enabled = [name for name, _ in winners[:2]] or ["resized_color", "gray_resized"]
    runtime_disabled = [name for name, _ in winners[2:] if "experimental" in name or "sharpen" in name]
    if "threshold_experimental" not in runtime_disabled:
        runtime_disabled.append("threshold_experimental")
    if "sharpen_light" not in runtime_disabled:
        runtime_disabled.append("sharpen_light")
    return {
        "runtime_enabled_versions": runtime_enabled,
        "runtime_disabled_versions": runtime_disabled,
        "max_runtime_candidates": min(2, max(1, len(runtime_enabled))),
    }


def format_markdown_report(report):
    baseline = report["baseline"]
    new_pipeline = report["new_pipeline"]
    gains = report["gain"]
    recommendation = report["recommendation"]
    winners = new_pipeline["winning_preprocess_versions"]

    winner_lines = "\n".join(
        f"- {name}: {count}"
        for name, count in sorted(winners.items(), key=lambda item: item[1], reverse=True)
    ) or "- Nenhuma versão válida identificada"

    return f"""# OCR Evaluation Report

Total de amostras: {report['total_samples']}
Amostras com gabarito: {report['labeled_samples']}

## Baseline

- Taxa de leitura: {baseline['read_rate']:.3f}
- Taxa de regex válida: {baseline['valid_regex_rate']:.3f}
- Acurácia exata: {baseline['exact_accuracy']:.3f}
- CER médio: {baseline['cer']:.3f}
- Confiança média: {baseline['average_confidence_all']:.3f}
- Falsos positivos: {baseline['false_positive_rate']:.3f}
- Falsos negativos: {baseline['false_negative_rate']:.3f}
- Tempo médio total: {baseline['average_total_time_ms']:.1f}ms
- FPS estimado: {baseline['estimated_fps']:.1f}

## Novo pipeline

- Taxa de leitura: {new_pipeline['read_rate']:.3f}
- Taxa de regex válida: {new_pipeline['valid_regex_rate']:.3f}
- Acurácia exata: {new_pipeline['exact_accuracy']:.3f}
- CER médio: {new_pipeline['cer']:.3f}
- Confiança média: {new_pipeline['average_confidence_all']:.3f}
- Falsos positivos: {new_pipeline['false_positive_rate']:.3f}
- Falsos negativos: {new_pipeline['false_negative_rate']:.3f}
- Tempo médio total: {new_pipeline['average_total_time_ms']:.1f}ms
- FPS estimado: {new_pipeline['estimated_fps']:.1f}

## Ganho

- Regex válida: {gains['valid_regex_rate_gain']:+.3f}
- Acurácia exata: {gains['exact_accuracy_gain']:+.3f}
- CER: {gains['cer_delta']:+.3f}
- Falsos positivos: {gains['false_positive_rate_delta']:+.3f}
- Falsos negativos: {gains['false_negative_rate_delta']:+.3f}
- Tempo médio: {gains['average_total_time_ms_delta']:+.1f}ms
- FPS estimado: {gains['estimated_fps_delta']:+.1f}

## Versões vencedoras

{winner_lines}

## Recomendação

- Ativar no runtime: {", ".join(recommendation['runtime_enabled_versions'])}
- Desativar no runtime: {", ".join(recommendation['runtime_disabled_versions'])}
- Máximo de candidatos em runtime: {recommendation['max_runtime_candidates']}
"""


def save_report_files(report, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / "ocr_metrics_report.json"
    md_path = output_path / "ocr_metrics_report.md"

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(format_markdown_report(report))

    return json_path, md_path
