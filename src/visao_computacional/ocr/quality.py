import cv2

from .config import load_ocr_config


def calculate_blur_variance(roi):
    """
    Mede nitidez pela variancia do Laplaciano.

    Nao garante que a leitura sera boa, mas funciona como proxy barato para
    decidir se vale a pena gastar uma chamada de OCR.
    """

    if roi is None or roi.size == 0:
        return 0.0
    gray = roi if roi.ndim == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def get_roi_quality_info(roi, bbox=None, config=None):
    """
    Retorna diagnostico detalhado da ROI sem esconder o motivo do descarte.
    """

    del bbox
    config = config or load_ocr_config()

    if roi is None:
        return {"should_run": False, "reason": "invalid_crop"}
    if getattr(roi, "size", 0) == 0:
        return {"should_run": False, "reason": "empty_crop"}

    height, width = roi.shape[:2]
    info = {
        "should_run": True,
        "reason": "passed",
        "width": width,
        "height": height,
    }

    if width < config.min_roi_width:
        info.update({"should_run": False, "reason": "low_width"})
        return info

    if height < config.min_roi_height:
        info.update({"should_run": False, "reason": "low_height"})
        return info

    aspect_ratio = width / max(1, height)
    info["aspect_ratio"] = aspect_ratio
    if aspect_ratio < config.min_aspect_ratio:
        info.update({"should_run": False, "reason": "aspect_too_small"})
        return info
    if aspect_ratio > config.max_aspect_ratio:
        info.update({"should_run": False, "reason": "aspect_too_large"})
        return info

    blur_variance = calculate_blur_variance(roi)
    info["blur_variance"] = blur_variance
    if blur_variance < config.min_blur_variance:
        info.update({"should_run": False, "reason": "low_blur_variance"})
        return info

    return info


def should_run_ocr_on_roi(roi, bbox=None, config=None):
    """
    Fachada de compatibilidade usada pelo runtime atual.
    """

    info = get_roi_quality_info(roi, bbox=bbox, config=config)
    return info["should_run"], info
