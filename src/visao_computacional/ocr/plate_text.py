import re


# Regex: o fluxo principal prioriza os formatos brasileiros.
# `UK_TEST` permanece apenas como compatibilidade de teste.
UK_MODEL = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z]{3}$")
OLD_MODEL_BR = re.compile(r"^[A-Z]{3}[0-9]{4}$")
MERCOSUL_MODEL_BR = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")

# Homóglifos comuns em OCR.
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
    text = (text or "").upper().replace(" ", "").replace("-", "")
    return re.sub(r"[^A-Z0-9]", "", text)


def empty_plate_info():
    return {
        "plate": "",
        "format": "UNKNOWN",
        "raw_text": "",
        "valid": False,
        "confidence": 0.0,
    }


def correct_plate_format_old(ocr_text):
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
    return candidate if OLD_MODEL_BR.fullmatch(candidate) else ""


def correct_plate_format_mercosul(ocr_text):
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
    return candidate if MERCOSUL_MODEL_BR.fullmatch(candidate) else ""


def correct_plate_format_uk(ocr_text):
    ocr_text = clean_plate_text(ocr_text)
    return ocr_text if UK_MODEL.fullmatch(ocr_text) else ""


def validate_plate_text(ocr_text):
    cleaned = clean_plate_text(ocr_text)
    if not cleaned:
        return empty_plate_info()

    candidate = correct_plate_format_old(cleaned)
    if candidate:
        return {
            "plate": candidate,
            "format": "BR_OLD",
            "raw_text": cleaned,
            "valid": True,
            "confidence": 0.0,
        }

    candidate = correct_plate_format_mercosul(cleaned)
    if candidate:
        return {
            "plate": candidate,
            "format": "BR_MERCOSUL",
            "raw_text": cleaned,
            "valid": True,
            "confidence": 0.0,
        }

    candidate = correct_plate_format_uk(cleaned)
    if candidate:
        return {
            "plate": candidate,
            "format": "UK_TEST",
            "raw_text": cleaned,
            "valid": True,
            "confidence": 0.0,
        }

    info = empty_plate_info()
    info["raw_text"] = cleaned
    return info
