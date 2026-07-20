import sqlite3
import json
from datetime import datetime
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_PATH = BASE_DIR / "local_detections.db"

# Qualidade do JPEG ao guardar o frame como BLOB no SQLite.
JPEG_QUALITY = 85


def ensure_table():
    """
    Cria a tabela plate_frames se ela ainda não existir.

    Este é o esquema único da fila local de detecções. Tanto o produtor
    (drone_webrtc_server) quanto o consumidor (sync_pending/supabase_matcher)
    dependem destas colunas.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plate_frames (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            plate        TEXT    NOT NULL,
            plate_format TEXT,
            confidence   REAL,
            bbox         TEXT,
            frame_blob   BLOB,
            status       TEXT    NOT NULL DEFAULT 'pending',
            created_at   TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_detection(plate, plate_format, confidence, bbox, frame_bgr):
    """
    Persiste uma detecção válida na fila local com status='pending'.

    Codifica o frame (numpy array BGR) como JPEG e guarda como BLOB, junto com
    os metadados da placa. Retorna o id gerado, ou None se a codificação falhar.
    """
    ok, buffer = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    frame_blob = buffer.tobytes() if ok else None

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO plate_frames (
            plate,
            plate_format,
            confidence,
            bbox,
            frame_blob,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (
        plate,
        plate_format,
        float(confidence),
        json.dumps(bbox),
        frame_blob,
        datetime.now().isoformat(),
    ))

    detection_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return detection_id


def get_pending_detections(limit=10):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            plate,
            plate_format,
            confidence,
            bbox,
            frame_blob,
            status,
            created_at
        FROM plate_frames
        WHERE status = 'pending'
        ORDER BY id ASC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows

# Caso não ser match, excluí placa do SQLite
def delete_local_detection(detection_id):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM plate_frames
        WHERE id = ?
    """, (detection_id,))

    conn.commit()
    conn.close()

# se der match, guardar no banco de dados
def update_local_detection_status(detection_id, status):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plate_frames
        SET status = ?
        WHERE id = ?
    """, (status, detection_id))

    conn.commit()
    conn.close()

# manda o frame 
def parse_bbox(bbox_value):
    if not bbox_value:
        return None

    if isinstance(bbox_value, list):
        return bbox_value

    return json.loads(bbox_value)