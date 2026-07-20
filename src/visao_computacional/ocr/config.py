import os
from dataclasses import dataclass


@dataclass
class OCRConfig:
    """
    Configuracao central do pipeline de OCR.

    A classe preserva os nomes e defaults ja usados pelo runtime para que a
    refatoracao seja estrutural, e nao comportamental.
    """

    runtime_profile: str = "fast"
    mode: str = "runtime"
    max_candidates_runtime: int = 1
    max_time_ms: float = 80.0
    debug: bool = False

    # Flags de evolucao da ROI. Hoje continuam majoritariamente em modo
    # conservador para evitar mudar o comportamento padrao.
    enable_perspective: bool = False
    enable_padding: bool = False
    padding_ratio: float = 0.0
    enable_experimental: bool = False
    enable_clahe: bool = False
    enable_bilateral: bool = False

    # Politica operacional do runtime.
    accept_confidence: float = 0.60
    log_interval_frames: int = 60
    debug_dir: str = "debug_ocr"
    primary_preprocess: str = "gray_resized"
    secondary_preprocess: str = "resized_color"
    enable_secondary_candidate: bool = False
    min_partial_confidence: float = 0.45

    # Gates para proteger custo e evitar OCR redundante.
    cooldown_enabled: bool = True
    cooldown_frames_valid: int = 30
    cooldown_frames_invalid: int = 10
    quality_filter_enabled: bool = True
    min_roi_width: int = 80
    min_roi_height: int = 25
    min_blur_variance: float = 40.0
    min_aspect_ratio: float = 2.0
    max_aspect_ratio: float = 6.5


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _profile_defaults(profile):
    normalized = (profile or "fast").strip().lower()
    if normalized == "balanced":
        return {
            "mode": "runtime",
            "max_candidates_runtime": 2,
            "enable_secondary_candidate": True,
            "enable_experimental": False,
            "enable_perspective": False,
            "debug": False,
            "cooldown_enabled": True,
            "quality_filter_enabled": True,
            "primary_preprocess": "gray_resized",
            "secondary_preprocess": "resized_color",
        }
    if normalized == "benchmark":
        return {
            "mode": "benchmark",
            "max_candidates_runtime": 2,
            "enable_secondary_candidate": True,
            "enable_experimental": True,
            "enable_perspective": False,
            "debug": True,
            "cooldown_enabled": False,
            "quality_filter_enabled": False,
            "primary_preprocess": "gray_resized",
            "secondary_preprocess": "resized_color",
        }
    return {
        "mode": "runtime",
        "max_candidates_runtime": 1,
        "enable_secondary_candidate": False,
        "enable_experimental": False,
        "enable_perspective": False,
        "debug": False,
        "cooldown_enabled": True,
        "quality_filter_enabled": True,
        "primary_preprocess": "gray_resized",
        "secondary_preprocess": "resized_color",
    }


def load_ocr_config():
    """
    Carrega a configuracao via ambiente preservando o contrato OCR_* atual.
    """

    runtime_profile = os.getenv("OCR_RUNTIME_PROFILE", "fast")
    defaults = _profile_defaults(runtime_profile)
    return OCRConfig(
        runtime_profile=runtime_profile,
        mode=os.getenv("OCR_MODE", defaults["mode"]),
        max_candidates_runtime=int(os.getenv("OCR_MAX_CANDIDATES_RUNTIME", str(defaults["max_candidates_runtime"]))),
        max_time_ms=float(os.getenv("OCR_MAX_TIME_MS", "80")),
        debug=_env_bool("OCR_DEBUG", defaults["debug"]),
        enable_perspective=_env_bool("OCR_ENABLE_PERSPECTIVE", defaults["enable_perspective"]),
        enable_padding=_env_bool("OCR_ENABLE_PADDING", False),
        padding_ratio=float(os.getenv("OCR_PADDING_RATIO", "0.0")),
        enable_experimental=_env_bool("OCR_ENABLE_EXPERIMENTAL", defaults["enable_experimental"]),
        enable_clahe=_env_bool("OCR_ENABLE_CLAHE", False),
        enable_bilateral=_env_bool("OCR_ENABLE_BILATERAL", False),
        accept_confidence=float(os.getenv("OCR_ACCEPT_CONFIDENCE", "0.60")),
        log_interval_frames=int(os.getenv("OCR_LOG_INTERVAL_FRAMES", "60")),
        debug_dir=os.getenv("OCR_DEBUG_DIR", "debug_ocr"),
        primary_preprocess=os.getenv("OCR_PRIMARY_PREPROCESS", defaults["primary_preprocess"]),
        secondary_preprocess=os.getenv("OCR_SECONDARY_PREPROCESS", defaults["secondary_preprocess"]),
        enable_secondary_candidate=_env_bool("OCR_ENABLE_SECONDARY_CANDIDATE", defaults["enable_secondary_candidate"]),
        min_partial_confidence=float(os.getenv("OCR_MIN_PARTIAL_CONFIDENCE", "0.45")),
        cooldown_enabled=_env_bool("OCR_COOLDOWN_ENABLED", defaults["cooldown_enabled"]),
        cooldown_frames_valid=int(os.getenv("OCR_COOLDOWN_FRAMES_VALID", "30")),
        cooldown_frames_invalid=int(os.getenv("OCR_COOLDOWN_FRAMES_INVALID", "10")),
        quality_filter_enabled=_env_bool("OCR_QUALITY_FILTER_ENABLED", defaults["quality_filter_enabled"]),
        min_roi_width=int(os.getenv("OCR_MIN_ROI_WIDTH", "80")),
        min_roi_height=int(os.getenv("OCR_MIN_ROI_HEIGHT", "25")),
        min_blur_variance=float(os.getenv("OCR_MIN_BLUR_VARIANCE", "40.0")),
        min_aspect_ratio=float(os.getenv("OCR_MIN_ASPECT_RATIO", "2.0")),
        max_aspect_ratio=float(os.getenv("OCR_MAX_ASPECT_RATIO", "6.5")),
    )
