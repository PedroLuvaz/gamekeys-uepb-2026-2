"""Fixtures compartilhadas pelos testes que usam o banco de testes (TEST_DATABASE_URL).

O banco de testes é apagado e recriado uma vez por execução do pytest; nunca aponte para o
banco gamekeys.
"""

import os

import psycopg
import pytest

from app import db  # noqa: F401  (carrega o .env.local)
from app.migrar import migrar

URL_TESTE = os.getenv("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def banco():
    if not URL_TESTE:
        pytest.skip("sem TEST_DATABASE_URL")
    assert "gamekeys_teste" in URL_TESTE, "TEST_DATABASE_URL precisa ser o banco de testes"
    with psycopg.connect(URL_TESTE, autocommit=True) as conexao:
        conexao.execute(
            "drop schema if exists core, catalogo cascade;"
            " drop table if exists public.migracoes_aplicadas"
        )
    migrar(URL_TESTE, carga=True)
    return URL_TESTE


@pytest.fixture
def conexao(banco):
    """Conexão cujas alterações são desfeitas ao fim do teste."""
    with psycopg.connect(banco) as conexao:
        yield conexao
        conexao.rollback()
