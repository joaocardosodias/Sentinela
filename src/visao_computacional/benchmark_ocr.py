import argparse
import csv
import json
import sys
import time
from pathlib import Path

import cv2

from src.visao_computacional.yolo26.plate_recognizer import (
    clean_plate_text,
    recognize_plate_easyocr,
    recognize_plate_paddle,
)


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def image_paths(input_path):
    path = Path(input_path)
    if path.is_file():
        return [path]

    return sorted(
        file_path
        for file_path in path.rglob("*")
        if file_path.suffix.lower() in IMAGE_EXTENSIONS
    )


def load_expected_plates(csv_path):
    if not csv_path:
        return {}

    expected = {}
    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            filename = row.get("filename") or row.get("image") or row.get("arquivo")
            plate = row.get("plate") or row.get("placa")
            if filename and plate:
                expected[Path(filename).name] = plate.strip().upper()

    return expected


def run_provider(provider_name, provider_func, image):
    started_at = time.perf_counter()
    result = provider_func(image)
    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

    return {
        "provider": provider_name,
        "latency_ms": latency_ms,
        "plate": result.get("plate", ""),
        "format": result.get("format", ""),
        "raw_text": result.get("raw_text", ""),
        "valid": result.get("valid", False),
    }


def benchmark_image(path, expected_plate):
    if not expected_plate:
        candidate = clean_plate_text(path.stem)
        expected_plate = candidate if len(candidate) == 7 else ""

    image = cv2.imread(str(path))
    if image is None:
        return [
            {
                "image": str(path),
                "provider": "error",
                "latency_ms": "",
                "plate": "",
                "format": "",
                "raw_text": "nao foi possivel abrir a imagem",
                "valid": False,
                "expected_plate": expected_plate,
                "match": False,
            }
        ]

    rows = []
    for provider_name, provider_func in (
        ("easyocr", recognize_plate_easyocr),
        ("paddleocr", recognize_plate_paddle),
    ):
        row = run_provider(provider_name, provider_func, image)
        row["image"] = str(path)
        row["expected_plate"] = expected_plate
        row["match"] = bool(expected_plate and row["plate"] == expected_plate)
        rows.append(row)

    return rows


def write_csv(rows, output_path):
    fieldnames = [
        "image",
        "provider",
        "latency_ms",
        "plate",
        "format",
        "raw_text",
        "valid",
        "expected_plate",
        "match",
    ]

    output_file = (
        open(output_path, "w", newline="", encoding="utf-8")
        if output_path
        else None
    )
    try:
        target = output_file or sys.stdout
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if output_file:
            output_file.close()


def main():
    parser = argparse.ArgumentParser(
        description="Compara EasyOCR e PaddleOCR nos mesmos recortes de placa."
    )
    parser.add_argument(
        "input",
        help="Imagem ou pasta com recortes de placas.",
    )
    parser.add_argument(
        "--expected-csv",
        help="CSV opcional com colunas filename/plate ou arquivo/placa.",
    )
    parser.add_argument(
        "--output",
        help="Caminho opcional para salvar o CSV de resultados.",
    )
    parser.add_argument(
        "--json-summary",
        action="store_true",
        help="Mostra um resumo agregado em JSON ao final.",
    )
    args = parser.parse_args()

    expected = load_expected_plates(args.expected_csv)
    rows = []

    for path in image_paths(args.input):
        rows.extend(benchmark_image(path, expected.get(path.name, "")))

    write_csv(rows, args.output)

    if args.json_summary:
        summary = {}
        for provider in ("easyocr", "paddleocr"):
            provider_rows = [row for row in rows if row["provider"] == provider]
            matches = [row for row in provider_rows if row["match"]]
            valid = [row for row in provider_rows if row["valid"]]
            latencies = [
                row["latency_ms"]
                for row in provider_rows
                if row["latency_ms"] != ""
            ]
            summary[provider] = {
                "total": len(provider_rows),
                "valid": len(valid),
                "matches": len(matches),
                "avg_latency_ms": (
                    round(sum(latencies) / len(latencies), 2)
                    if latencies
                    else None
                ),
            }

        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
