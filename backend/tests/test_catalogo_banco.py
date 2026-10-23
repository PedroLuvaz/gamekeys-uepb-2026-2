"""GK-84: consulta real ao PostgreSQL isolado configurado em TEST_DATABASE_URL."""

from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.servicos import catalogo


@pytest.fixture
def cliente_catalogo(conexao, monkeypatch):
    # A fixture existente desfaz as alterações; o serviço usa esta mesma conexão.
    pool = SimpleNamespace(connection=lambda: nullcontext(conexao))
    monkeypatch.setattr(catalogo, "obter_pool", lambda: pool)
    return TestClient(app)


def test_paginas_cobrem_todos_os_ativos_sem_repetir(cliente_catalogo, conexao):
    esperados = [
        id_jogo
        for (id_jogo,) in conexao.execute(
            "select id from catalogo.jogos where ativo order by nome, id"
        )
    ]

    primeira_resposta = cliente_catalogo.get("/jogos")
    segunda_resposta = cliente_catalogo.get("/jogos?pagina=2")

    assert primeira_resposta.status_code == segunda_resposta.status_code == 200
    primeira, segunda = primeira_resposta.json(), segunda_resposta.json()
    assert len(primeira["itens"]) == 20
    assert len(segunda["itens"]) == 3
    assert primeira["total"] == segunda["total"] == 23
    assert primeira["total_paginas"] == segunda["total_paginas"] == 2
    assert primeira["por_pagina"] == segunda["por_pagina"] == 20
    obtidos = [item["id"] for pagina in (primeira, segunda) for item in pagina["itens"]]
    assert obtidos == esperados
    assert len(set(obtidos)) == 23


def test_esgotado_aparece_e_inativo_nao_aparece(cliente_catalogo, conexao):
    ids_inativos = {
        id_jogo for (id_jogo,) in conexao.execute("select id from catalogo.jogos where not ativo")
    }
    id_esgotado = conexao.execute(
        "select id from catalogo.jogos where ativo and chaves_disponiveis = 0"
    ).fetchone()[0]

    itens = [
        item
        for pagina in (1, 2)
        for item in cliente_catalogo.get(f"/jogos?pagina={pagina}").json()["itens"]
    ]

    assert not ids_inativos.intersection(item["id"] for item in itens)
    esgotados = [item for item in itens if item["disponibilidade"] == "Esgotado"]
    assert [item["id"] for item in esgotados] == [id_esgotado]
    assert all(item["disponibilidade"] == "Disponível" for item in itens if item not in esgotados)


def test_campos_publicos_correspondem_ao_banco(cliente_catalogo, conexao):
    conexao.execute(
        "update catalogo.jogos set capa_url = 'https://example.com/capa.png' where ativo"
    )
    resposta = cliente_catalogo.get("/jogos")

    for item in resposta.json()["itens"]:
        nome, capa, preco = conexao.execute(
            "select nome, capa_url, preco from catalogo.jogos where id = %s", (item["id"],)
        ).fetchone()
        assert item["nome"] == nome
        assert item["capa_url"] == capa
        assert item["preco"] == str(preco)
        assert set(item) == {"id", "nome", "capa_url", "preco", "disponibilidade"}


def test_pagina_apos_a_ultima_preserva_total(cliente_catalogo):
    resposta = cliente_catalogo.get("/jogos?pagina=3")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "itens": [],
        "pagina": 3,
        "por_pagina": 20,
        "total": 23,
        "total_paginas": 2,
    }


def test_catalogo_sem_ativos_responde_lista_vazia(cliente_catalogo, conexao):
    conexao.execute("update catalogo.jogos set ativo = false")

    resposta = cliente_catalogo.get("/jogos")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "itens": [],
        "pagina": 1,
        "por_pagina": 20,
        "total": 0,
        "total_paginas": 0,
    }


def test_nome_repetido_usa_identificador_para_desempatar(cliente_catalogo, conexao):
    conexao.execute("update catalogo.jogos set nome = 'Mesmo nome' where ativo")
    esperados = [
        id_jogo
        for (id_jogo,) in conexao.execute("select id from catalogo.jogos where ativo order by id")
    ]

    obtidos = [
        item["id"]
        for pagina in (1, 2)
        for item in cliente_catalogo.get(f"/jogos?pagina={pagina}").json()["itens"]
    ]

    assert obtidos == esperados


def test_detalhe_corresponde_ao_jogo_ativo(cliente_catalogo, conexao):
    jogo_id, descricao, genero, plataforma, classificacao = conexao.execute(
        "select j.id, j.descricao, c.nome, j.plataforma, j.classificacao"
        " from catalogo.jogos j join catalogo.categorias c on c.id = j.categoria_id"
        " where j.ativo order by j.id limit 1"
    ).fetchone()

    resposta = cliente_catalogo.get(f"/jogos/{jogo_id}")

    assert resposta.status_code == 200
    assert resposta.json()["descricao"] == descricao
    assert resposta.json()["genero"] == genero
    assert resposta.json()["plataforma"] == plataforma
    assert resposta.json()["classificacao"] == classificacao


def test_detalhe_inativo_nao_expoe_dados(cliente_catalogo, conexao):
    jogo_id = conexao.execute("select id from catalogo.jogos where not ativo limit 1").fetchone()[0]

    resposta = cliente_catalogo.get(f"/jogos/{jogo_id}")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Jogo não encontrado."}


def test_detalhe_inexistente_nao_encontrado(cliente_catalogo):
    resposta = cliente_catalogo.get("/jogos/9223372036854775807")

    assert resposta.status_code == 404
