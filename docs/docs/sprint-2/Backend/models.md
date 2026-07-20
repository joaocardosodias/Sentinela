---
sidebar_position: 5
title: Models e Persistência
description: Documentação técnica da camada de acesso ao banco de dados com queries SQL reais e padrões de conexão.
---

# Models e Persistência

A camada de **Models** é a única do sistema com acesso direto ao banco de dados PostgreSQL. Ela contém exclusivamente funções que executam queries SQL — sem validações, sem regras de negócio, sem objetos de domínio.

Cada método segue um padrão fixo:
1. Obtém uma conexão do pool via `get_db_connection()` — a conexão fica vinculada ao contexto da requisição atual.
2. Cria um cursor e executa a query com parâmetros posicionais `%s` (protegidos contra SQL Injection pelo psycopg2).
3. Faz `commit()` em operações de escrita.
4. Fecha **apenas o cursor** no bloco `finally` — a conexão é devolvida ao pool automaticamente ao final da requisição pelo `teardown_appcontext`.

> Os Models recebem apenas tipos primitivos (`str`, `int`, `bool`, `dict`) e retornam apenas `dict` ou `list`. Nenhum objeto de domínio ou entidade é conhecido aqui.

---

## Por que SQL puro em vez de um ORM?

A decisão de usar `psycopg2` com queries SQL diretamente — em vez de SQLAlchemy ou outro ORM — foi deliberada. ORMs introduzem uma camada de abstração que, embora conveniente em projetos simples, torna o código mais difícil de entender à medida que as queries crescem em complexidade.

Com SQL puro:
- A query que executa é exatamente a query que está escrita no código — sem geração automática.
- Um `SELECT * FROM scans WHERE status_validacao = 'pendente' ORDER BY horario_scan ASC` é legível por qualquer pessoa, com ou sem conhecimento do ORM.
- O debug é direto: ao identificar um problema de performance, a query já está visível no código e pode ser copiada diretamente para um cliente SQL para inspeção.

---

## Como funciona o `get_db_connection()`?

O gerenciamento de conexões usa um `ThreadedConnectionPool` do psycopg2, inicializado uma única vez na criação da aplicação Flask e compartilhado entre todas as requisições.

**`app/db.py` — código completo:**

```python title="app/db.py"
import psycopg2
from psycopg2 import pool
from flask import g

# Pool global — criado uma vez e mantido durante toda a vida da aplicação
_pool: pool.ThreadedConnectionPool = None


def init_pool(database_url: str, minconn: int = 2, maxconn: int = 10):
    """Inicializa o pool de conexões."""
    global _pool
    # Garante entre 2 e 10 conexões abertas simultaneamente com o PostgreSQL
    _pool = pool.ThreadedConnectionPool(minconn, maxconn, database_url)


def get_db_connection():
    """
    Retorna uma conexão do pool vinculada ao contexto da requisição atual (flask.g).
    Se já houver uma conexão aberta para esta requisição, reutiliza a mesma.
    """
    if 'db_conn' not in g:
        # Solicita uma conexão livre do pool — bloqueia até haver uma disponível
        g.db_conn = _pool.getconn()
    return g.db_conn


def release_connection(exception=None):
    """
    Devolve a conexão ao pool ao final de cada requisição HTTP.
    Registrado via app.teardown_appcontext em create_app().
    """
    conn = g.pop('db_conn', None)
    if conn is not None:
        if exception:
            # Em caso de erro não capturado, faz rollback antes de devolver
            conn.rollback()
        _pool.putconn(conn)
```

**`app/__init__.py` — inicialização e registro do teardown:**

```python title="app/__init__.py"
from app.db import init_pool, release_connection

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Cria o pool com mínimo 2 e máximo 10 conexões simultâneas
    init_pool(app.config['DATABASE_URL'])

    # Ao final de cada requisição, devolve a conexão ao pool automaticamente
    app.teardown_appcontext(release_connection)
    ...
```

**Padrão nos Models após o pool:** os métodos fecham apenas o cursor. A conexão **não é fechada manualmente** — ela é devolvida ao pool pelo `teardown`.

```python
conn = get_db_connection()  # pega do pool (ou reutiliza a da requisição)
cur = conn.cursor()
try:
    # executa a query
    conn.commit()
finally:
    cur.close()  # fecha apenas o cursor
    # conn.close() removido — o teardown_appcontext cuida da devolução ao pool
```

---


## Usuários — `user_model.py`

---

### `insert`

```python title="app/models/user_model.py"
@staticmethod
def insert(data: dict):
    """Executa INSERT de um novo usuário. Não usa RETURNING — o ID já vem no dict."""
    conn = get_db_connection()
    # Cursor padrão (sem RealDictCursor) pois não há retorno de linhas
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (id, name, email, senha, role) VALUES (%s, %s, %s, %s, %s)",
            # Os valores são passados como tupla — psycopg2 protege contra SQL Injection
            (data['id'], data['name'], data['email'], data['senha'], data['role'])
        )
        conn.commit()  # Confirma a transação no banco
    finally:
        # Garante fechamento mesmo em caso de exceção durante o INSERT
        cur.close()
        conn.close()
```

---

### `get_all`

```python title="app/models/user_model.py"
@staticmethod
def get_all(page=1, per_page=20, role=None) -> tuple:
    """SELECT paginado com filtro opcional por cargo. Retorna (lista_de_dicts, total)."""
    conn = get_db_connection()
    # RealDictCursor converte cada linha do banco em um dicionário Python automaticamente
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # Calcula o OFFSET a partir da página solicitada
        offset = (page - 1) * per_page

        if role:
            # Filtra por cargo quando o parâmetro é fornecido
            cur.execute(
                "SELECT id, name, email, role FROM users WHERE role = %s LIMIT %s OFFSET %s",
                (role, per_page, offset)
            )
        else:
            cur.execute(
                "SELECT id, name, email, role FROM users LIMIT %s OFFSET %s",
                (per_page, offset)
            )
        rows = cur.fetchall()

        # Segunda query para contar o total — necessário para o frontend calcular páginas
        cur.execute(
            "SELECT COUNT(*) FROM users" + (" WHERE role = %s" if role else ""),
            ((role,) if role else ())
        )
        total = cur.fetchone()['count']
        # Converte cada RealDictRow para dict Python comum antes de retornar
        return [dict(r) for r in rows], total
    finally:
        cur.close()
        conn.close()
```

---

### `get_by_id` e `get_by_email`

```python title="app/models/user_model.py"
@staticmethod
def get_by_id(user_id: str) -> dict:
    """SELECT por UUID. Inclui a coluna 'senha' pois o service precisa para verificar o hash."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT id, name, email, senha, role FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        # Retorna None se o usuário não existir — o service trata esse caso
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

@staticmethod
def get_by_email(email: str) -> dict:
    """SELECT por e-mail. Utilizado no login e na verificação de duplicidade no registro."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT id, name, email, senha, role FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()
```

---

### `update` e `update_password`

```python title="app/models/user_model.py"
@staticmethod
def update(user_id: str, name: str = None, role: str = None):
    """UPDATE dinâmico: monta a cláusula SET apenas com os campos que foram fornecidos."""
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
            return  # Nenhum campo fornecido — encerra sem executar query
        values.append(user_id)
        # A query é montada dinamicamente para evitar SET de colunas desnecessárias
        cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    finally:
        cur.close()
        conn.close()

@staticmethod
def update_password(user_id: str, hashed_password: str):
    """UPDATE exclusivo para senha — separado do update geral por segurança."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Recebe apenas o hash — nunca a senha em texto puro
        cur.execute("UPDATE users SET senha = %s WHERE id = %s", (hashed_password, user_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()
```

---

## Operações — `operacao_model.py`

---

### `insert` e `get_all`

```python title="app/models/operacao_model.py"
@staticmethod
def insert(data: dict) -> dict:
    """INSERT com RETURNING * — retorna o registro completo como dict, incluindo dados gerados pelo banco."""
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
        conn.close()

@staticmethod
def get_all(page=1, per_page=20, status=None) -> tuple:
    """SELECT paginado ordenado por data de criação decrescente (mais recentes primeiro)."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        offset = (page - 1) * per_page
        if status:
            cur.execute(
                "SELECT * FROM operacoes WHERE status = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (status, per_page, offset)
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM operacoes WHERE status = %s", (status,))
        else:
            cur.execute(
                "SELECT * FROM operacoes ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (per_page, offset)
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM operacoes")
        total = cur.fetchone()[0]
        return [dict(r) for r in rows], total
    finally:
        cur.close()
        conn.close()
```

---

### `update` e `get_drones`

```python title="app/models/operacao_model.py"
@staticmethod
def update(oid: str, name=None, status=None, localizacao=None) -> dict:
    """UPDATE dinâmico com RETURNING * — retorna o registro atualizado ou None se sem campos."""
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
        cur.execute(
            f"UPDATE operacoes SET {', '.join(updates)} WHERE id = %s RETURNING *",
            values
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

@staticmethod
def get_drones(oid: str) -> list:
    """SELECT de todos os drones vinculados à operação — usado para expandir o recurso."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT * FROM drones WHERE operacao_id = %s", (oid,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
```

---

## Drones — `drone_model.py`

---

### `insert`

```python title="app/models/drone_model.py"
@staticmethod
def insert(data: dict) -> dict:
    """INSERT com todos os campos do drone, incluindo opcionais (bateria, conectividade, GPS)."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """INSERT INTO drones
               (id, operacao_id, nome, bateria, conectividade, status_voo, latitude, longitude)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
            (
                data['id'], data['operacao_id'], data['nome'],
                data.get('bateria'),        # None é aceito pelo psycopg2 como NULL no banco
                data.get('conectividade'),
                data['status_voo'],
                data.get('latitude'),
                data.get('longitude')
            )
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row)
    finally:
        cur.close()
        conn.close()
```

---

### `update` com campos dinâmicos

```python title="app/models/drone_model.py"
@staticmethod
def update(did: str, **fields) -> dict:
    """UPDATE genérico baseado em kwargs — aceita qualquer subconjunto de campos permitidos."""
    # Lista explícita de colunas permitidas para impedir injeção via nome de campo
    allowed = ['nome', 'bateria', 'conectividade', 'status_voo', 'latitude', 'longitude']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # Filtra apenas os campos que estão na whitelist
        updates = [f"{k} = %s" for k in fields if k in allowed]
        values  = [v for k, v in fields.items() if k in allowed]
        if not updates:
            return None  # Nenhum campo válido enviado — não executa query
        values.append(did)
        cur.execute(
            f"UPDATE drones SET {', '.join(updates)} WHERE id = %s RETURNING *",
            values
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()
```

---

### `get_scans`

```python title="app/models/drone_model.py"
@staticmethod
def get_scans(did: str, page=1, per_page=20) -> list:
    """SELECT de scans de um drone específico, do mais recente para o mais antigo."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        offset = (page - 1) * per_page
        cur.execute(
            # ORDER BY DESC: histórico de detecções mostra as mais recentes primeiro
            "SELECT * FROM scans WHERE id_drone = %s ORDER BY horario_scan DESC LIMIT %s OFFSET %s",
            (did, per_page, offset)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
```

---

## Scans — `scan_model.py`

O model de scans é o mais complexo do sistema, responsável por consultas com JOIN, normalização de tipos e o registro do audit log.

---

### `_normalize` — Utilitário Interno

```python title="app/models/scan_model.py"
@staticmethod
def _normalize(row: dict) -> dict:
    """Converte tipos nativos do PostgreSQL para tipos serializáveis em JSON."""
    r = dict(row)
    # UUID vem do banco como objeto uuid.UUID — converte para string
    for k in ['id', 'id_drone', 'validado_por']:
        if r.get(k):
            r[k] = str(r[k])
    # Timestamps vêm como datetime — converte para string ISO para o JSON serializer
    for k in ['horario_scan', 'validado_em']:
        if r.get(k):
            r[k] = str(r[k])
    # Coordenadas vêm como Decimal do banco — converte para float Python
    for k in ['latitude', 'longitude']:
        if r.get(k) is not None:
            r[k] = float(r[k])
    return r
```

---

### `insert` e `get_pendentes`

```python title="app/models/scan_model.py"
@staticmethod
def insert(data: dict) -> dict:
    """INSERT do scan detectado pelo drone. status_validacao não é inserido — assume DEFAULT 'pendente' no schema."""
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
        # _normalize é chamado em todo retorno para garantir tipos corretos no JSON
        return ScanModel._normalize(row)
    finally:
        cur.close()
        conn.close()

@staticmethod
def get_pendentes(page=1, per_page=20) -> list:
    """SELECT da fila FIFO de scans aguardando validação humana."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        offset = (page - 1) * per_page
        cur.execute(
            # ORDER BY ASC: o mais antigo é apresentado primeiro (FIFO)
            # Isso garante que nenhum scan fique esquecido na fila
            "SELECT * FROM scans WHERE status_validacao = 'pendente' ORDER BY horario_scan ASC LIMIT %s OFFSET %s",
            (per_page, offset)
        )
        return [ScanModel._normalize(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
```

---

### `update_validacao`

```python title="app/models/scan_model.py"
@staticmethod
def update_validacao(sid: str, status: str, validado_por: str) -> dict:
    """UPDATE exclusivo de validação — registra o gestor responsável e o timestamp da decisão."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            # NOW() é gerado pelo banco — garante timestamp correto independente do fuso do servidor Flask
            "UPDATE scans SET status_validacao=%s, validado_por=%s, validado_em=NOW() WHERE id=%s RETURNING *",
            (status, validado_por, sid)
        )
        row = cur.fetchone()
        conn.commit()
        return ScanModel._normalize(row) if row else None
    finally:
        cur.close()
        conn.close()
```

---

### Audit Log e Vínculos com Veículos

```python title="app/models/scan_model.py"
@staticmethod
def registrar_acao(log_id: str, usuario_id: str, scan_id: str, acao: str) -> dict:
    """INSERT na tabela usuarios_scans — cria um registro imutável da ação do gestor."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO usuarios_scans (id, usuario_id, scan_id, acao_realizada) VALUES (%s, %s, %s, %s) RETURNING *",
            (log_id, usuario_id, scan_id, acao)
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row)
    finally:
        cur.close()
        conn.close()

@staticmethod
def get_veiculos(sid: str) -> list:
    """SELECT com INNER JOIN para obter os veículos vinculados a um scan via tabela de junção."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT v.*
            FROM veiculos v
            INNER JOIN veiculos_scans vs ON vs.id_veiculos = v.id
            WHERE vs.id_scan = %s
        """, (sid,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

@staticmethod
def get_historico_usuario(usuario_id: str) -> list:
    """SELECT com JOIN para o histórico completo de ações de um gestor em scans."""
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
        conn.close()
```

---

## Veículos — `veiculo_model.py`

---

### `insert` e `search`

```python title="app/models/veiculo_model.py"
@staticmethod
def insert(data: dict):
    """INSERT de um veículo. Sem RETURNING — o dict completo já foi retornado pelo service via to_dict()."""
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
        conn.close()

@staticmethod
def search(query: str) -> list:
    """SELECT com ILIKE em placa, modelo e cor — busca parcial e case-insensitive."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # O padrão %query% busca o texto em qualquer posição do campo
        q = f'%{query}%'
        cur.execute(
            "SELECT * FROM veiculos WHERE placa ILIKE %s OR modelo ILIKE %s OR cor ILIKE %s",
            (q, q, q)  # O mesmo parâmetro é passado três vezes, um para cada coluna
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
```

---

### `update`

```python title="app/models/veiculo_model.py"
@staticmethod
def update(vid: str, placa=None, modelo=None, cor=None, roubado=None, data_roubo=None):
    """UPDATE dinâmico — monta a cláusula SET apenas com os campos que foram fornecidos."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        updates, values = [], []
        # Verifica `is not None` (não apenas falsy) para permitir roubado=False como atualização válida
        if placa      is not None: updates.append("placa = %s");      values.append(placa)
        if modelo     is not None: updates.append("modelo = %s");     values.append(modelo)
        if cor        is not None: updates.append("cor = %s");        values.append(cor)
        if roubado    is not None: updates.append("roubado = %s");    values.append(roubado)
        if data_roubo is not None: updates.append("data_roubo = %s"); values.append(data_roubo)
        if not updates:
            return  # Nenhum campo para atualizar — aborta sem executar query
        values.append(vid)
        cur.execute(f"UPDATE veiculos SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    finally:
        cur.close()
        conn.close()
```
