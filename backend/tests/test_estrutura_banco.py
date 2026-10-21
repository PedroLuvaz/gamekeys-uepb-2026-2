"""GK-92: estrutura, restrições e carga validadas contra o banco de testes (TEST_DATABASE_URL).

O banco de testes é apagado e recriado a cada execução; nunca aponte para o banco gamekeys.
"""

import os

import psycopg
import pytest

from app import db  # noqa: F401  (carrega o .env.local)
from app.migrar import migrar

URL_TESTE = os.getenv("TEST_DATABASE_URL")
HASH_BCRYPT = "$2b$12$" + "a" * 53

pytestmark = pytest.mark.skipif(not URL_TESTE, reason="sem TEST_DATABASE_URL")


@pytest.fixture(scope="module")
def banco():
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
    with psycopg.connect(banco) as conexao:
        yield conexao
        conexao.rollback()


def inserir_usuario(conexao, email, senha_hash=HASH_BCRYPT):
    return conexao.execute(
        "insert into core.usuarios (nome, email, senha_hash, data_nascimento)"
        " values ('Ana Teste', %s, %s, '2000-01-01') returning id, perfil",
        (email, senha_hash),
    ).fetchone()


def test_carga_tem_ativos_esgotado_e_inativo(conexao):
    ativos, esgotados, inativos = conexao.execute(
        "select count(*) filter (where ativo),"
        " count(*) filter (where ativo and chaves_disponiveis = 0),"
        " count(*) filter (where not ativo) from catalogo.jogos"
    ).fetchone()

    assert ativos > 20
    assert esgotados == 1
    assert inativos == 1


def test_repetir_migracao_e_carga_nao_duplica(banco, conexao):
    antes = conexao.execute("select count(*) from catalogo.jogos").fetchone()[0]

    assert migrar(banco, carga=True) == []

    assert conexao.execute("select count(*) from catalogo.jogos").fetchone()[0] == antes


def test_cadastro_usa_perfil_cliente_por_padrao(conexao):
    _, perfil = inserir_usuario(conexao, "perfil@teste.com")

    assert perfil == "cliente"


def test_email_repetido_e_recusado_sem_diferenciar_maiusculas(conexao):
    inserir_usuario(conexao, "repetido@teste.com")

    with pytest.raises(psycopg.errors.UniqueViolation):
        inserir_usuario(conexao, "Repetido@Teste.com")


def test_senha_fora_do_formato_bcrypt_e_recusada(conexao):
    with pytest.raises(psycopg.errors.CheckViolation):
        inserir_usuario(conexao, "texto@teste.com", senha_hash="senha123")


def test_jogo_com_categoria_inexistente_e_recusado(conexao):
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        conexao.execute(
            "insert into catalogo.jogos"
            " (categoria_id, slug, nome, descricao, preco, plataforma, classificacao)"
            " values (999999, 'sem-categoria', 'Sem categoria', '-', 10, 'PC', 'L')"
        )


def test_dado_gravado_continua_disponivel_em_nova_conexao(banco):
    with psycopg.connect(banco) as conexao:
        usuario_id, _ = inserir_usuario(conexao, "persistente@teste.com")
        conexao.commit()

    with psycopg.connect(banco) as outra:
        email = outra.execute(
            "select email from core.usuarios where id = %s", (usuario_id,)
        ).fetchone()[0]
        outra.execute("delete from core.usuarios where id = %s", (usuario_id,))
        outra.commit()

    assert email == "persistente@teste.com"
