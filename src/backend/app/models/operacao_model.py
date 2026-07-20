from app.db import get_db_connection
import psycopg2.extras


class OperacaoModel:

    @staticmethod
    def insert(data: dict) -> dict:
        """Executa INSERT de uma operação e retorna o registro criado."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                "INSERT INTO operacoes (id, name, status, localizacao, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                (data['id'], data['name'], data['status'], data['localizacao'], data['created_at'])
            )
            row = cur.fetchone()
            conn.commit()
            return dict(row)
        finally:
            cur.close()

    @staticmethod
    def get_all(page=1, per_page=20, status=None) -> tuple:
        """Executa SELECT paginado de operações ordenado por created_at. Retorna (lista, total)."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            if status:
                cur.execute("SELECT * FROM operacoes WHERE status = %s ORDER BY created_at DESC LIMIT %s OFFSET %s", (status, per_page, offset))
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM operacoes WHERE status = %s", (status,))
            else:
                cur.execute("SELECT * FROM operacoes ORDER BY created_at DESC LIMIT %s OFFSET %s", (per_page, offset))
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM operacoes")
            total = cur.fetchone()['count']
            return [dict(r) for r in rows], total
        finally:
            cur.close()

    @staticmethod
    def get_by_id(oid: str) -> dict:
        """Executa SELECT de uma operação pelo UUID. Retorna dict ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM operacoes WHERE id = %s", (oid,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def update(oid: str, name=None, status=None, localizacao=None) -> dict:
        """Executa UPDATE de name, status e/ou localização de uma operação. Retorna o registro atualizado ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            updates, values = [], []
            if name:
                updates.append("name = %s"); values.append(name)
            if status:
                updates.append("status = %s"); values.append(status)
            if localizacao:
                updates.append("localizacao = %s"); values.append(localizacao)
            if not updates:
                return None
            values.append(oid)
            cur.execute(f"UPDATE operacoes SET {', '.join(updates)} WHERE id = %s RETURNING *", values)
            row = cur.fetchone()
            conn.commit()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def delete(oid: str) -> bool:
        """Executa DELETE de uma operação. Retorna True se deletada."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM operacoes WHERE id = %s", (oid,))
            affected = cur.rowcount
            conn.commit()
            return affected > 0
        finally:
            cur.close()

    @staticmethod
    def get_drones(oid: str) -> list:
        """Executa SELECT de todos os drones vinculados a uma operação."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM drones WHERE operacao_id = %s", (oid,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            cur.close()
