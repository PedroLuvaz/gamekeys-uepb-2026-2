"""GK-87/GK-89: detalhe com PostgreSQL isolado e alterações desfeitas por teste."""

from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.servicos import catalogo


@pytest.fixture
def cliente_detalhe(conexao, monkeypatch):
    pool = SimpleNamespace(connection=lambda: nullcontext(conexao))
    monkeypatch.setattr(catalogo, "obter_pool", lambda: pool)
    return TestClient(app)


@pytest.mark.parametrize("chaves", [0, 1, 30])
def test_seis_dados_e_disponibilidade_correspondem_ao_banco(cliente_detalhe, conexao, chaves):
    jogo = conexao.execute(
        "select j.id, j.nome, j.descricao, c.nome, j.plataforma, j.classificacao, j.preco"
        " from catalogo.jogos j join catalogo.categorias c on c.id = j.categoria_id"
        " where j.ativo order by j.nome, j.id limit 1"
    ).fetchone()
    jogo_id, nome, descricao, genero, plataforma, classificacao, preco = jogo
    conexao.execute(
        "update catalogo.jogos set chaves_disponiveis = %s where id = %s", (chaves, jogo_id)
    )

    resposta = cliente_detalhe.get(f"/jogos/{jogo_id}")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": jogo_id,
        "nome": nome,
        "capa_url": None,
        "descricao": descricao,
        "genero": genero,
        "plataforma": plataforma,
        "classificacao": classificacao,
        "preco": str(preco),
        "disponibilidade": "Disponível" if chaves else "Esgotado",
    }
    item_da_lista = next(
        j for j in cliente_detalhe.get("/jogos").json()["itens"] if j["id"] == jogo_id
    )
    assert resposta.json()["disponibilidade"] == item_da_lista["disponibilidade"]
    assert resposta.json()["preco"] == item_da_lista["preco"]


def test_jogo_desativado_depois_da_listagem_deixa_de_ter_detalhe(cliente_detalhe, conexao):
    jogo_id = cliente_detalhe.get("/jogos").json()["itens"][0]["id"]
    assert cliente_detalhe.get(f"/jogos/{jogo_id}").status_code == 200
    conexao.execute("update catalogo.jogos set ativo = false where id = %s", (jogo_id,))

    resposta = cliente_detalhe.get(f"/jogos/{jogo_id}")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Jogo não encontrado."}
    assert all(j["id"] != jogo_id for j in cliente_detalhe.get("/jogos").json()["itens"])


def test_inativo_e_inexistente_tem_a_mesma_resposta_publica(cliente_detalhe, conexao):
    jogo_id, nome = conexao.execute(
        "select id, nome from catalogo.jogos where not ativo limit 1"
    ).fetchone()

    inativo = cliente_detalhe.get(f"/jogos/{jogo_id}")
    inexistente = cliente_detalhe.get("/jogos/9223372036854775807")

    assert inativo.status_code == inexistente.status_code == 404
    assert inativo.json() == inexistente.json() == {"detail": "Jogo não encontrado."}
    assert nome not in inativo.text
