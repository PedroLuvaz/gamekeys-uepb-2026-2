"""Acesso ao PostgreSQL, compartilhado por todas as rotas.

A aplicação usa a URL com pool (DATABASE_URL, host com -pooler no Neon). Migrações e pg_dump
devem usar DATABASE_URL_UNPOOLED, que é a conexão direta.
"""

from psycopg_pool import ConnectionPool

from app.config import carregar

_pool: ConnectionPool | None = None


class BancoNaoConfigurado(RuntimeError):
    """DATABASE_URL não foi definida."""


def obter_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        config = carregar()
        if not config.database_url:
            raise BancoNaoConfigurado("DATABASE_URL não definida")
        # O PgBouncer do Neon roda em modo transação: sem prepared statements no servidor.
        _pool = ConnectionPool(
            config.database_url,
            min_size=1,
            max_size=5,
            timeout=config.timeout_banco,
            kwargs={"prepare_threshold": None},
            open=True,
        )
    return _pool


def fechar_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def verificar_banco() -> dict[str, str]:
    """Consulta simples para provar que a API alcança o banco."""
    with obter_pool().connection() as conexao:
        banco, versao = conexao.execute(
            "select current_database(), current_setting('server_version')"
        ).fetchone()
    return {"banco": banco, "versao": versao}
