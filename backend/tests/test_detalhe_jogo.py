"""Contrato de detalhe usado na navegação do catálogo, sem acessar o banco compartilhado."""

from decimal import Decimal

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.esquemas.catalogo import DetalheDoJogo, Disponibilidade
from app.main import app
from app.servicos import catalogo

client = TestClient(app)


def test_detalhe_publico_exibe_os_campos_do_jogo(monkeypatch):
    def consultar(jogo_id):
        return DetalheDoJogo(
            id=jogo_id,
            nome="Tempestade de Aço",
            capa_url=None,
            preco=Decimal("139.90"),
            disponibilidade=Disponibilidade.ESGOTADO,
            descricao="Combate de robôs gigantes.",
            genero="Ação",
            plataforma="PC",
            classificacao="14",
        )

    monkeypatch.setattr(catalogo, "consultar_jogo", consultar)

    resposta = client.get("/jogos/23")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": 23,
        "nome": "Tempestade de Aço",
        "capa_url": None,
        "preco": "139.90",
        "disponibilidade": "Esgotado",
        "descricao": "Combate de robôs gigantes.",
        "genero": "Ação",
        "plataforma": "PC",
        "classificacao": "14",
    }


def test_jogo_ausente_responde_nao_encontrado(monkeypatch):
    monkeypatch.setattr(catalogo, "consultar_jogo", lambda _: None)

    resposta = client.get("/jogos/24")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Jogo não encontrado."}


@pytest.mark.parametrize("identificador", ["0", "-1", "abc", "9223372036854775808"])
def test_identificador_invalido_nao_consulta_banco(monkeypatch, identificador):
    def nao_consultar(_):
        pytest.fail("Identificador inválido não deve consultar o banco")

    monkeypatch.setattr(catalogo, "consultar_jogo", nao_consultar)

    assert client.get(f"/jogos/{identificador}").status_code == 422


def test_falha_no_detalhe_nao_expoe_conexao(monkeypatch):
    def falhar(_):
        raise psycopg.OperationalError("conexão privada")

    monkeypatch.setattr(catalogo, "consultar_jogo", falhar)

    resposta = client.get("/jogos/1")

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "Catálogo indisponível. Tente novamente mais tarde."}
