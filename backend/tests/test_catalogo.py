"""Contrato HTTP e regra de disponibilidade da GK-84; não acessa banco."""

from decimal import Decimal

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg_pool import PoolTimeout

from app.db import BancoNaoConfigurado
from app.esquemas.catalogo import Disponibilidade, JogoNoCatalogo, PaginaDeJogos
from app.main import app
from app.servicos import catalogo

client = TestClient(app)


@pytest.mark.parametrize(
    ("quantidade", "esperada"),
    [
        (0, Disponibilidade.ESGOTADO),
        (1, Disponibilidade.DISPONIVEL),
        (40, Disponibilidade.DISPONIVEL),
    ],
)
def test_disponibilidade_depende_das_chaves(quantidade, esperada):
    assert catalogo.disponibilidade_do_jogo(quantidade) == esperada


@pytest.mark.parametrize("consulta,pagina", [("", 1), ("?pagina=2", 2)])
def test_catalogo_publico_tem_contrato_paginado(monkeypatch, consulta, pagina):
    paginas_consultadas = []

    def listar(numero):
        paginas_consultadas.append(numero)
        return PaginaDeJogos(
            itens=[
                JogoNoCatalogo(
                    id=7,
                    slug="lamina-do-sertao",
                    nome="Lâmina do Sertão",
                    capa_url=None,
                    preco=Decimal("149.90"),
                    disponibilidade=Disponibilidade.DISPONIVEL,
                )
            ],
            pagina=numero,
            por_pagina=20,
            total=23,
            total_paginas=2,
        )

    monkeypatch.setattr(catalogo, "listar_jogos", listar)

    resposta = client.get(f"/jogos{consulta}")

    assert paginas_consultadas == [pagina]
    assert resposta.status_code == 200
    assert resposta.json() == {
        "itens": [
            {
                "id": 7,
                "slug": "lamina-do-sertao",
                "nome": "Lâmina do Sertão",
                "capa_url": None,
                "preco": "149.90",
                "disponibilidade": "Disponível",
            }
        ],
        "pagina": pagina,
        "por_pagina": 20,
        "total": 23,
        "total_paginas": 2,
    }


@pytest.mark.parametrize("pagina", ["0", "-1", "abc", "1.5", "2147483648"])
def test_pagina_invalida_nao_consulta_o_banco(monkeypatch, pagina):
    def nao_consultar(_):
        pytest.fail("Página inválida não deve consultar o banco")

    monkeypatch.setattr(catalogo, "listar_jogos", nao_consultar)

    resposta = client.get("/jogos", params={"pagina": pagina})

    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "erro",
    [
        BancoNaoConfigurado("DATABASE_URL não definida"),
        psycopg.OperationalError("postgresql://usuario:senha-privada@servidor/gamekeys"),
        PoolTimeout("pool indisponível: servidor privado"),
    ],
)
def test_catalogo_indisponivel_nao_expoe_conexao(monkeypatch, erro):
    def falhar(_):
        raise erro

    monkeypatch.setattr(catalogo, "listar_jogos", falhar)

    resposta = client.get("/jogos")

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "Catálogo indisponível. Tente novamente mais tarde."}
