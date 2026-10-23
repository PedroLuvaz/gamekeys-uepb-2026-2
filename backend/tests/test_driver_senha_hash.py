"""Driver DA-SEG-I1-01 (GK-69): senha guardada só como hash bcrypt e nunca devolvida pela API.

Medida do driver: 0 senhas em texto puro no banco e 0 respostas com senha ou hash.
Este arquivo cobre o banco e o contrato de todas as respostas da API. A verificação de ponta
a ponta (cadastrar pela API e ler o registro) entra junto com o cadastro da GK-7.
"""

import re

import psycopg
import pytest

from app.main import app

SENHA = "segredo123"
HASH_BCRYPT = "$2b$12$" + "b" * 53
# Mesmo padrão da restrição de core.usuarios na migração 0001.
FORMATO_BCRYPT = r"^\$2[aby]\$\d{2}\$.{53}$"
CAMPO_SENSIVEL = re.compile(r"senha|password|hash", re.IGNORECASE)


def inserir_usuario(conexao, email, senha_hash):
    return conexao.execute(
        "insert into core.usuarios (nome, email, senha_hash, data_nascimento)"
        " values ('Cliente Driver', %s, %s, '2000-01-01') returning id",
        (email, senha_hash),
    ).fetchone()[0]


def campos_das_respostas(openapi: dict) -> set[str]:
    """Nomes de todos os campos que alguma resposta da API pode devolver."""
    esquemas = openapi.get("components", {}).get("schemas", {})
    campos: set[str] = set()
    vistos: set[str] = set()

    def visitar(esquema: dict) -> None:
        if "$ref" in esquema:
            nome = esquema["$ref"].rsplit("/", 1)[-1]
            if nome not in vistos:
                vistos.add(nome)
                visitar(esquemas.get(nome, {}))
            return
        for nome, sub in esquema.get("properties", {}).items():
            campos.add(nome)
            visitar(sub)
        for chave in ("items", "additionalProperties"):
            if isinstance(esquema.get(chave), dict):
                visitar(esquema[chave])
        for chave in ("allOf", "anyOf", "oneOf"):
            for sub in esquema.get(chave, []):
                visitar(sub)

    for operacoes in openapi.get("paths", {}).values():
        for operacao in operacoes.values():
            for resposta in operacao.get("responses", {}).values():
                for conteudo in resposta.get("content", {}).values():
                    visitar(conteudo.get("schema", {}))
    return campos


def test_varredura_enxerga_os_campos_das_respostas():
    # Garante que o teste seguinte não passa por não encontrar nada.
    assert {"status", "banco", "versao"} <= campos_das_respostas(app.openapi())


def test_nenhuma_resposta_da_api_devolve_senha_ou_hash():
    expostos = sorted(c for c in campos_das_respostas(app.openapi()) if CAMPO_SENSIVEL.search(c))

    assert expostos == []


def test_banco_recusa_senha_em_texto_puro(conexao):
    with pytest.raises(psycopg.errors.CheckViolation):
        inserir_usuario(conexao, "texto-puro@teste.com", SENHA)


def test_banco_guarda_o_hash_e_nao_a_senha(conexao):
    usuario_id = inserir_usuario(conexao, "hash@teste.com", HASH_BCRYPT)

    guardado = conexao.execute(
        "select senha_hash from core.usuarios where id = %s", (usuario_id,)
    ).fetchone()[0]

    assert guardado == HASH_BCRYPT
    assert SENHA not in guardado


def test_nenhuma_senha_em_texto_puro_no_banco(conexao):
    inserir_usuario(conexao, "medida@teste.com", HASH_BCRYPT)

    fora_do_formato = conexao.execute(
        "select count(*) from core.usuarios where senha_hash !~ %s", (FORMATO_BCRYPT,)
    ).fetchone()[0]

    assert fora_do_formato == 0
