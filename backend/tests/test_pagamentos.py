"""GK-16: contrato, validação e erros públicos do pagamento e da consulta do pedido."""

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg_pool import PoolTimeout

from app.db import BancoNaoConfigurado
from app.esquemas.clientes import ClienteCadastrado
from app.esquemas.pedidos import ChaveEntregue, ItemDoPedido, PedidoDetalhado
from app.main import criar_app
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho, pagamentos


def pedido(status="entregue", chaves=True):
    return PedidoDetalhado(
        pedido_id=7,
        status=status,
        valor_total=Decimal("19.90"),
        itens=[
            ItemDoPedido(
                jogo_id=3,
                nome="Jogo",
                quantidade=1,
                preco_unitario=Decimal("19.90"),
                subtotal=Decimal("19.90"),
            )
        ],
        chaves=[ChaveEntregue(jogo_id=3, nome="Jogo", codigo="AAAA-BBBB")] if chaves else [],
    )


@pytest.fixture
def api_pedido():
    app = criar_app()
    cliente = ClienteCadastrado(
        id=9,
        nome="Cliente Pagamento",
        email="pagamento@example.com",
        data_nascimento=date(1990, 1, 1),
        perfil="cliente",
    )
    app.dependency_overrides[usuario_atual] = lambda: cliente
    with TestClient(app) as api:
        yield api


def test_pagamento_devolve_pedido_entregue_com_chaves_do_cliente_da_sessao(api_pedido, monkeypatch):
    def pagar(cliente, pedido_id, metodo):
        assert (cliente.id, pedido_id, metodo) == (9, 7, "pix")
        return pedido()

    monkeypatch.setattr(pagamentos, "pagar_pedido", pagar)
    resposta = api_pedido.post("/pedidos/7/pagamento", json={"metodo": "pix"})
    assert resposta.status_code == 200
    assert resposta.json() == {
        "pedido_id": 7,
        "status": "entregue",
        "valor_total": "19.90",
        "itens": [
            {
                "jogo_id": 3,
                "nome": "Jogo",
                "quantidade": 1,
                "preco_unitario": "19.90",
                "subtotal": "19.90",
            }
        ],
        "chaves": [{"jogo_id": 3, "nome": "Jogo", "codigo": "AAAA-BBBB"}],
    }


def test_consulta_antes_da_entrega_nao_traz_codigos(api_pedido, monkeypatch):
    monkeypatch.setattr(
        pagamentos, "consultar_pedido", lambda *_: pedido("aguardando_pagamento", chaves=False)
    )
    resposta = api_pedido.get("/pedidos/7")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "aguardando_pagamento"
    assert resposta.json()["chaves"] == []


@pytest.mark.parametrize(
    "corpo",
    [
        {},
        {"metodo": "dinheiro"},
        {"metodo": None},
        {"metodo": "pix", "valor": 1},
        {"metodo": "pix", "usuario_id": 8},
        {"metodo": "pix", "status": "aprovado"},
    ],
)
def test_entrada_invalida_nao_chega_ao_banco(api_pedido, monkeypatch, corpo):
    monkeypatch.setattr(pagamentos, "pagar_pedido", lambda *_: pytest.fail("Não pagar"))
    resposta = api_pedido.post("/pedidos/7/pagamento", json=corpo)
    assert resposta.status_code == 422
    # Q-06: nenhuma mensagem do Pydantic em inglês chega ao cliente.
    assert all(
        "should" not in item["msg"] and "required" not in item["msg"].lower()
        for item in resposta.json()["detail"]
    )


@pytest.mark.parametrize("pedido_id", ["0", "-1", "abc", "9223372036854775808"])
def test_identificador_invalido_nao_chega_ao_banco(api_pedido, monkeypatch, pedido_id):
    monkeypatch.setattr(pagamentos, "pagar_pedido", lambda *_: pytest.fail("Não pagar"))
    monkeypatch.setattr(pagamentos, "consultar_pedido", lambda *_: pytest.fail("Não consultar"))
    assert api_pedido.get(f"/pedidos/{pedido_id}").status_code == 422
    resposta = api_pedido.post(f"/pedidos/{pedido_id}/pagamento", json={"metodo": "pix"})
    assert resposta.status_code == 422


@pytest.mark.parametrize(
    ("erro", "status", "mensagem"),
    [
        (carrinho.ClienteNaoPermitido(), 403, "O pagamento é exclusivo de clientes."),
        (pagamentos.PedidoNaoEncontrado(), 404, "Pedido não encontrado."),
        (pagamentos.PedidoNaoPagavel(), 409, "Este pedido não está aguardando pagamento."),
        (BancoNaoConfigurado(), 503, "Pagamento temporariamente indisponível."),
        (psycopg.OperationalError("senha=x"), 503, "Pagamento temporariamente indisponível."),
        (PoolTimeout(), 503, "Pagamento temporariamente indisponível."),
    ],
)
def test_erros_do_pagamento_tem_mensagem_publica(api_pedido, monkeypatch, erro, status, mensagem):
    def falhar(*_):
        raise erro

    monkeypatch.setattr(pagamentos, "pagar_pedido", falhar)
    resposta = api_pedido.post("/pedidos/7/pagamento", json={"metodo": "cartao"})
    assert resposta.status_code == status
    assert resposta.json() == {"detail": mensagem}


@pytest.mark.parametrize(
    ("erro", "status", "mensagem"),
    [
        (carrinho.ClienteNaoPermitido(), 403, "Os pedidos são exclusivos de clientes."),
        (pagamentos.PedidoNaoEncontrado(), 404, "Pedido não encontrado."),
        (psycopg.OperationalError("senha=nao-vazar"), 503, "Pedido temporariamente indisponível."),
    ],
)
def test_erros_da_consulta_tem_mensagem_publica(api_pedido, monkeypatch, erro, status, mensagem):
    def falhar(*_):
        raise erro

    monkeypatch.setattr(pagamentos, "consultar_pedido", falhar)
    resposta = api_pedido.get("/pedidos/7")
    assert resposta.status_code == status
    assert resposta.json() == {"detail": mensagem}


def test_pagamento_e_consulta_exigem_autenticacao():
    with TestClient(criar_app()) as api:
        assert api.get("/pedidos/7").status_code == 401
        assert api.post("/pedidos/7/pagamento", json={"metodo": "pix"}).status_code == 401
