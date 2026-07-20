import psycopg2
from psycopg2 import pool
from flask import g

# Variável global que guarda o pool durante o ciclo de vida da aplicação
_pool: pool.ThreadedConnectionPool = None


def init_pool(database_url: str, minconn: int = 2, maxconn: int = 10):
    """Inicializa o pool de conexões."""
    global _pool
    _pool = pool.ThreadedConnectionPool(minconn, maxconn, database_url)


def _discard_connection(conn):
    """Remove uma conexão quebrada do pool."""
    if conn is not None and _pool is not None:
        _pool.putconn(conn, close=True)


def _connection_is_alive(conn) -> bool:
    """
    Verifica se a conexão ainda pode ser usada.
    Bancos gerenciados podem encerrar conexões ociosas sem aviso;
    nesse caso o pool precisa abrir uma nova conexão.
    """
    if conn is None or conn.closed:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except (psycopg2.InterfaceError, psycopg2.DatabaseError):
        return False


def get_db_connection():
    """
    Retorna uma conexão do pool.
    A conexão é armazenada no contexto da requisição Flask (flask.g)
    para que a mesma conexão seja reutilizada dentro de uma única requisição.
    """
    conn = g.get('db_conn')

    if conn is None or not _connection_is_alive(conn):
        if conn is not None:
            _discard_connection(conn)
            g.pop('db_conn', None)
        # Solicita uma conexão livre do pool
        conn = _pool.getconn()
        if not _connection_is_alive(conn):
            _discard_connection(conn)
            conn = _pool.getconn()
        g.db_conn = conn

    return g.db_conn


def release_connection(exception=None):
    """
    Devolve a conexão ao pool ao final de cada requisição.
    Deve ser registrado via app.teardown_appcontext em create_app().
    """
    conn = g.pop('db_conn', None)
    if conn is not None:
        try:
            if conn.closed:
                _discard_connection(conn)
                return

            if exception:
                # Em caso de erro não tratado, descarta a conexão suja fazendo rollback
                conn.rollback()

            _pool.putconn(conn)
        except (psycopg2.InterfaceError, psycopg2.DatabaseError):
            _discard_connection(conn)
