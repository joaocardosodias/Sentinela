from app.db import get_db_connection
import psycopg2.extras


class DroneModel:

    @staticmethod
    def insert(data: dict) -> dict:
        """Executa INSERT de um drone e retorna o registro criado."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                "INSERT INTO drones (id, operacao_id, nome, bateria, conectividade, status_voo, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                (data['id'], data['operacao_id'], data['nome'], data.get('bateria'),
                 data.get('conectividade'), data['status_voo'], data.get('latitude'), data.get('longitude'))
            )
            row = cur.fetchone()
            conn.commit()
            return dict(row)
        finally:
            cur.close()

    @staticmethod
    def get_all(page=1, per_page=20, operacao_id=None, status_voo=None) -> tuple:
        """Executa SELECT paginado de drones com filtros opcionais. Retorna (lista, total)."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            filters, values = [], []
            if operacao_id:
                filters.append("operacao_id = %s"); values.append(operacao_id)
            if status_voo:
                filters.append("status_voo = %s"); values.append(status_voo)
            where = ("WHERE " + " AND ".join(filters)) if filters else ""
            cur.execute(f"SELECT * FROM drones {where} LIMIT %s OFFSET %s", values + [per_page, offset])
            rows = cur.fetchall()
            cur.execute(f"SELECT COUNT(*) AS total FROM drones {where}", values)
            total_row = cur.fetchone() or {}
            total = total_row.get('total', 0)
            return [dict(r) for r in rows], total
        finally:
            cur.close()

    @staticmethod
    def get_by_id(did: str) -> dict:
        """Executa SELECT de um drone pelo UUID. Retorna dict ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM drones WHERE id = %s", (did,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def update(did: str, **fields) -> dict:
        """Executa UPDATE dinâmico de campos do drone. Retorna o registro atualizado ou None."""
        allowed = ['nome', 'bateria', 'conectividade', 'status_voo', 'latitude', 'longitude']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            updates = [f"{k} = %s" for k in fields if k in allowed]
            values = [v for k, v in fields.items() if k in allowed]
            if not updates:
                return None
            values.append(did)
            cur.execute(f"UPDATE drones SET {', '.join(updates)} WHERE id = %s RETURNING *", values)
            row = cur.fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def delete(did: str) -> bool:
        """Executa DELETE de um drone. Retorna True se deletado."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM drones WHERE id = %s", (did,))
            affected = cur.rowcount
            conn.commit()
            return affected > 0
        finally:
            cur.close()

    @staticmethod
    def get_scans(did: str, page=1, per_page=20) -> list:
        """Executa SELECT de scans de um drone, do mais recente ao mais antigo."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            cur.execute("SELECT * FROM scans WHERE id_drone = %s ORDER BY horario_scan DESC LIMIT %s OFFSET %s",
                        (did, per_page, offset))
            return [dict(r) for r in cur.fetchall()]
        finally:
            cur.close()
