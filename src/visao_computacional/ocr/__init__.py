from .config import OCRConfig, load_ocr_config
from .metrics import OcrRuntimeMetrics
from .pipeline import (
    OcrCooldown,
    PlateTemporalBuffer,
    correct_homoglyphs_by_plate_format,
    generate_plate_image_candidates,
    generate_ocr_image_candidates,
    has_partial_plate_hint,
    normalize_ocr_result,
    read_plate_from_roi,
    resize_plate,
    run_ocr_on_candidates,
    select_best_ocr_candidate,
)
from .plate_text import (
    clean_plate_text,
    empty_plate_info,
    validate_plate_text,
)
from .quality import calculate_blur_variance, get_roi_quality_info, should_run_ocr_on_roi
