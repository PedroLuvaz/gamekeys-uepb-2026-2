"""Fixtures dos testes que usam um PostgreSQL local e descartável.

O banco é apagado e recriado uma vez por execução do pytest. A validação abaixo recusa
Neon e qualquer host remoto antes de abrir a primeira conexão destrutiva.
"""

import os

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict

from app import db  # noqa: F401  (carrega o .env.local)
from app.migrar import migrar

URL_TESTE = os.getenv("TEST_DATABASE_URL")
HOSTS_LOCAIS = {"localhost", "127.0.0.1", "::1"}


def _validar_url_banco_teste(url: str) -> str:
    """Aceita somente o banco local explícito ``gamekeys_teste``."""
    try:
        parametros = conninfo_to_dict(url)
    except (psycopg.Error, ValueError) as erro:
        raise pytest.UsageError("TEST_DATABASE_URL não é uma conexão PostgreSQL válida") from erro

    banco = parametros.get("dbname")
    host = (parametros.get("host") or "").lower()
    hostaddr = (parametros.get("hostaddr") or "").lower()

    if banco != "gamekeys_teste":
        raise pytest.UsageError("TEST_DATABASE_URL precisa apontar exatamente para gamekeys_teste")
    if host not in HOSTS_LOCAIS:
        raise pytest.UsageError(
            "TEST_DATABASE_URL precisa usar PostgreSQL local isolado "
            "(localhost, 127.0.0.1 ou ::1); hosts remotos e Neon são proibidos"
        )
    if hostaddr and hostaddr not in HOSTS_LOCAIS:
        raise pytest.UsageError(
            "TEST_DATABASE_URL não pode redirecionar hostaddr para endereço remoto"
        )

    return url


@pytest.fixture(scope="session")
def banco():
    if not URL_TESTE:
        pytest.skip("sem TEST_DATABASE_URL")
    url_teste = _validar_url_banco_teste(URL_TESTE)
    with psycopg.connect(url_teste, autocommit=True) as conexao:
        conexao.execute(
            "drop schema if exists core, catalogo cascade;"
            " drop table if exists public.migracoes_aplicadas"
        )
    migrar(url_teste, carga=True)
    return url_teste


@pytest.fixture
def conexao(banco):
    """Conexão cujas alterações são desfeitas ao fim do teste."""
    with psycopg.connect(banco) as conexao:
        yield conexao
        conexao.rollback()
