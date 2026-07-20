from app.db import get_db_connection
import psycopg2.extras


class UserModel:

    @staticmethod
    def insert(data: dict):
        """Executa INSERT de um usuário. data deve conter: id, name, email, senha, role."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (id, name, email, senha, role) VALUES (%s, %s, %s, %s, %s)",
                (data['id'], data['name'], data['email'], data['senha'], data['role'])
            )
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def get_all(page=1, per_page=20, role=None) -> tuple:
        """Executa SELECT paginado de usuários. Retorna (lista_de_dicts, total)."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            if role:
                cur.execute("SELECT id, name, email, role FROM users WHERE role = %s LIMIT %s OFFSET %s",
                            (role, per_page, offset))
                cur.execute("SELECT COUNT(*) FROM users WHERE role = %s", (role,))
            else:
                cur.execute("SELECT id, name, email, role FROM users LIMIT %s OFFSET %s", (per_page, offset))
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM users" + (" WHERE role = %s" if role else ""),
                        ((role,) if role else ()))
            total = cur.fetchone()['count']
            return [dict(r) for r in rows], total
        finally:
            cur.close()

    @staticmethod
    def get_by_id(user_id: str) -> dict:
        """Executa SELECT de um usuário pelo UUID. Retorna dict ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT id, name, email, senha, role FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def get_by_email(email: str) -> dict:
        """Executa SELECT de um usuário pelo e-mail. Retorna dict ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT id, name, email, senha, role FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def update(user_id: str, name: str = None, role: str = None):
        """Executa UPDATE de name e/ou role de um usuário."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            updates, values = [], []
            if name:
                updates.append("name = %s")
                values.append(name)
            if role:
                updates.append("role = %s")
                values.append(role)
            if not updates:
                return
            values.append(user_id)
            cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", values)
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def update_password(user_id: str, hashed_password: str):
        """Executa UPDATE da senha (já em hash) de um usuário."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET senha = %s WHERE id = %s", (hashed_password, user_id))
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def delete(user_id: str) -> bool:
        """Executa DELETE de um usuário. Retorna True se deletado."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            affected = cur.rowcount
            conn.commit()
            return affected > 0
        finally:
            cur.close()

    @staticmethod
    def search_by_name(query: str) -> list:
        """Executa SELECT com ILIKE para busca parcial por nome."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT id, name, email, role FROM users WHERE name ILIKE %s", (f'%{query}%',))
            return [dict(r) for r in cur.fetchall()]
        finally:
            cur.close()
