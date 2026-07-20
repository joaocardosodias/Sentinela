from app.db import get_db_connection
import psycopg2.extras


class VeiculoModel:

    @staticmethod
    def insert(data: dict):
        """Executa INSERT de um veículo. data deve conter: id, placa, modelo, cor, roubado, data_roubo."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO veiculos (id, placa, modelo, cor, roubado, data_roubo) VALUES (%s, %s, %s, %s, %s, %s)",
                (data['id'], data['placa'], data['modelo'], data['cor'], data['roubado'], data['data_roubo'])
            )
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def get_all(page=1, per_page=20, roubado=None) -> tuple:
        """Executa SELECT paginado de veículos. Aceita filtro por roubado. Retorna (lista, total)."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            if roubado is not None:
                cur.execute("SELECT * FROM veiculos WHERE roubado = %s LIMIT %s OFFSET %s", (roubado, per_page, offset))
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM veiculos WHERE roubado = %s", (roubado,))
            else:
                cur.execute("SELECT * FROM veiculos LIMIT %s OFFSET %s", (per_page, offset))
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM veiculos")
            total = cur.fetchone()['count']
            return [dict(r) for r in rows], total
        finally:
            cur.close()

    @staticmethod
    def get_by_id(vid: str) -> dict:
        """Executa SELECT de um veículo pelo UUID. Retorna dict ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM veiculos WHERE id = %s", (vid,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def get_by_placa(placa: str) -> dict:
        """Executa SELECT de um veículo pela placa (ILIKE). Retorna dict ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM veiculos WHERE placa ILIKE %s", (placa,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def search(query: str) -> list:
        """Executa SELECT com ILIKE em placa, modelo e cor."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            q = f'%{query}%'
            cur.execute("SELECT * FROM veiculos WHERE placa ILIKE %s OR modelo ILIKE %s OR cor ILIKE %s", (q, q, q))
            return [dict(r) for r in cur.fetchall()]
        finally:
            cur.close()

    @staticmethod
    def update(vid: str, placa=None, modelo=None, cor=None, roubado=None, data_roubo=None):
        """Executa UPDATE dos campos fornecidos de um veículo."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            updates, values = [], []
            if placa is not None:
                updates.append("placa = %s"); values.append(placa)
            if modelo is not None:
                updates.append("modelo = %s"); values.append(modelo)
            if cor is not None:
                updates.append("cor = %s"); values.append(cor)
            if roubado is not None:
                updates.append("roubado = %s"); values.append(roubado)
            if data_roubo is not None:
                updates.append("data_roubo = %s"); values.append(data_roubo)
            if not updates:
                return
            values.append(vid)
            cur.execute(f"UPDATE veiculos SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def delete(vid: str) -> bool:
        """Executa DELETE de um veículo. Retorna True se deletado."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM veiculos WHERE id = %s", (vid,))
            affected = cur.rowcount
            conn.commit()
            return affected > 0
        finally:
            cur.close()
