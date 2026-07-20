from app.db import get_db_connection
import psycopg2.extras


class ScanModel:

    @staticmethod
    def _normalize(row: dict) -> dict:
        """Normaliza tipos do banco para JSON (UUID→str, Decimal→float, Timestamp→str)."""
        r = dict(row)
        for k in ['id', 'id_drone', 'validado_por']:
            if r.get(k):
                r[k] = str(r[k])
        for k in ['horario_scan', 'validado_em']:
            if r.get(k):
                r[k] = str(r[k])
        for k in ['latitude', 'longitude']:
            if r.get(k) is not None:
                r[k] = float(r[k])
        return r

    @staticmethod
    def insert(data: dict) -> dict:
        """Executa INSERT de um scan e retorna o registro criado."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                "INSERT INTO scans (id, id_drone, placa, match, imagem_url, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *",
                (data['id'], data['id_drone'], data['placa'], data['match'],
                 data.get('imagem_url'), data.get('latitude'), data.get('longitude'))
            )
            row = cur.fetchone()
            conn.commit()
            return ScanModel._normalize(row)
        finally:
            cur.close()

    @staticmethod
    def get_all(page=1, per_page=20, status=None, match=None, drone_id=None) -> tuple:
        """Executa SELECT paginado com filtros opcionais. Retorna (lista, total)."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            filters, values = [], []
            if status:
                filters.append("s.status_validacao = %s"); values.append(status)
            if match is not None:
                filters.append("s.match = %s"); values.append(match)
            if drone_id:
                filters.append("s.id_drone = %s"); values.append(drone_id)
            where = ("WHERE " + " AND ".join(filters)) if filters else ""
            
            query = f"""
                SELECT 
                    s.*, 
                    v.modelo as veiculo_modelo, 
                    v.cor as veiculo_cor, 
                    v.data_roubo as veiculo_data_roubo,
                    v.id as veiculo_id
                FROM scans s
                LEFT JOIN veiculos_scans vs ON vs.id_scan = s.id
                LEFT JOIN veiculos v ON vs.id_veiculos = v.id
                {where} 
                ORDER BY s.horario_scan DESC 
                LIMIT %s OFFSET %s
            """
            cur.execute(query, values + [per_page, offset])
            rows = cur.fetchall()
            
            cur.execute(f"SELECT COUNT(*) FROM scans s {where}", values)
            total = cur.fetchone()['count']
            return [ScanModel._normalize(r) for r in rows], total
        finally:
            cur.close()

    @staticmethod
    def get_by_id(sid: str) -> dict:
        """Executa SELECT de um scan pelo UUID. Retorna dict normalizado ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM scans WHERE id = %s", (sid,))
            row = cur.fetchone()
            return ScanModel._normalize(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def update_validacao(sid: str, status: str, validado_por: str, placa=None, cor=None, modelo=None) -> dict:
        """Executa UPDATE de validação de um scan. Retorna o registro atualizado ou None."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Busca o scan atual
            cur.execute("SELECT * FROM scans WHERE id=%s", (sid,))
            scan = cur.fetchone()
            if not scan:
                return None
            
            # Usa os valores editados ou mantém os originais
            final_placa = placa if placa is not None else scan['placa']
            
            # Atualiza o scan com a validação e campos editados
            cur.execute(
                "UPDATE scans SET status_validacao=%s, validado_por=%s, validado_em=NOW(), placa=%s WHERE id=%s RETURNING *",
                (status, validado_por, final_placa, sid)
            )
            row = cur.fetchone()
            
            # Se há veiculo vinculado e foram editados cor/modelo, atualiza também
            if row and (cor is not None or modelo is not None):
                cur.execute(
                    """SELECT id_veiculos FROM veiculos_scans WHERE id_scan=%s LIMIT 1""",
                    (sid,)
                )
                veiculo_link = cur.fetchone()
                if veiculo_link:
                    vid = veiculo_link['id_veiculos']
                    if cor is not None and modelo is not None:
                        cur.execute(
                            "UPDATE veiculos SET cor=%s, modelo=%s WHERE id=%s",
                            (cor, modelo, vid)
                        )
                    elif cor is not None:
                        cur.execute(
                            "UPDATE veiculos SET cor=%s WHERE id=%s",
                            (cor, vid)
                        )
                    elif modelo is not None:
                        cur.execute(
                            "UPDATE veiculos SET modelo=%s WHERE id=%s",
                            (modelo, vid)
                        )
            
            conn.commit()
            return ScanModel._normalize(row) if row else None
        finally:
            cur.close()

    @staticmethod
    def delete(sid: str) -> bool:
        """Executa DELETE de um scan. Retorna True se deletado."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM scans WHERE id = %s", (sid,))
            affected = cur.rowcount
            conn.commit()
            return affected > 0
        finally:
            cur.close()

    @staticmethod
    def get_pendentes(page=1, per_page=20) -> list:
        """Executa SELECT de scans pendentes, do mais antigo ao mais recente."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            cur.execute("SELECT * FROM scans WHERE status_validacao = 'pendente' ORDER BY horario_scan ASC LIMIT %s OFFSET %s",
                        (per_page, offset))
            return [ScanModel._normalize(r) for r in cur.fetchall()]
        finally:
            cur.close()

    @staticmethod
    def get_matches(page=1, per_page=20) -> list:
        """Executa SELECT de scans com match positivo."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            offset = (page - 1) * per_page
            cur.execute("""
                SELECT 
                    s.*, 
                    v.modelo as veiculo_modelo, 
                    v.cor as veiculo_cor, 
                    v.data_roubo as veiculo_data_roubo,
                    v.id as veiculo_id
                FROM scans s
                LEFT JOIN veiculos_scans vs ON vs.id_scan = s.id
                LEFT JOIN veiculos v ON vs.id_veiculos = v.id
                WHERE s.match = TRUE AND s.status_validacao = 'aprovado' 
                ORDER BY s.horario_scan DESC 
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            return [ScanModel._normalize(r) for r in cur.fetchall()]
        finally:
            cur.close()

    @staticmethod
    def get_veiculos(sid: str) -> list:
        """Executa SELECT de veículos vinculados a um scan via veiculos_scans."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT v.* FROM veiculos v
                INNER JOIN veiculos_scans vs ON vs.id_veiculos = v.id
                WHERE vs.id_scan = %s
            """, (sid,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            cur.close()

    @staticmethod
    def vincular_veiculo(sid: str, vid: str, link_id: str) -> dict:
        """Executa INSERT na tabela veiculos_scans."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("INSERT INTO veiculos_scans (id, id_scan, id_veiculos) VALUES (%s, %s, %s) RETURNING *",
                        (link_id, sid, vid))
            row = cur.fetchone()
            conn.commit()
            return dict(row)
        finally:
            cur.close()

    @staticmethod
    def registrar_acao(log_id: str, usuario_id: str, scan_id: str, acao: str) -> dict:
        """Executa INSERT na tabela usuarios_scans (audit log)."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("INSERT INTO usuarios_scans (id, usuario_id, scan_id, acao_realizada) VALUES (%s, %s, %s, %s) RETURNING *",
                        (log_id, usuario_id, scan_id, acao))
            row = cur.fetchone()
            conn.commit()
            return dict(row)
        finally:
            cur.close()

    @staticmethod
    def get_historico_usuario(usuario_id: str) -> list:
        """Executa SELECT com JOIN para o histórico de ações de um usuário em scans."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT us.*, s.placa, s.match, s.status_validacao, s.horario_scan
                FROM usuarios_scans us
                INNER JOIN scans s ON s.id = us.scan_id
                WHERE us.usuario_id = %s
                ORDER BY s.horario_scan DESC
            """, (usuario_id,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            cur.close()
