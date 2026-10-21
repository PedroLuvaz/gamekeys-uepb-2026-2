"""Conexão com o PostgreSQL (Neon).

A aplicação usa a URL com pool (DATABASE_URL, host com -pooler). Migrações e pg_dump
devem usar DATABASE_URL_UNPOOLED, que é a conexão direta.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

RAIZ_DO_REPO = Path(__file__).resolve().parents[2]

# `neon env pull` grava as variáveis na raiz do repositório. Variáveis já definidas no
# ambiente (CI, deploy) têm prioridade sobre os arquivos.
load_dotenv(RAIZ_DO_REPO / ".env.local")
load_dotenv(RAIZ_DO_REPO / ".env")

_pool: ConnectionPool | None = None


class BancoNaoConfigurado(RuntimeError):
    """DATABASE_URL não foi definida."""


def obter_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise BancoNaoConfigurado("DATABASE_URL não definida")
        # O PgBouncer do Neon roda em modo transação: sem prepared statements no servidor.
        _pool = ConnectionPool(
            url,
            min_size=1,
            max_size=5,
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
