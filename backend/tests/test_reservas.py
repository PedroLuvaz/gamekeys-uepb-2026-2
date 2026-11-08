"""GK-124: contrato, validação e erros públicos da reserva."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg_pool import PoolTimeout

from app.db import BancoNaoConfigurado
from app.esquemas.clientes import ClienteCadastrado
from app.esquemas.reservas import ItemReservado, PedidoReservado
from app.main import criar_app
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho, reservas


@pytest.fixture
def api_reserva():
    app = criar_app()
    cliente = ClienteCadastrado(
        id=9,
        nome="Cliente Reserva",
        email="reserva@example.com",
        data_nascimento=date(1990, 1, 1),
        perfil="cliente",
    )
    app.dependency_overrides[usuario_atual] = lambda: cliente
    with TestClient(app) as api:
        yield api


def test_contrato_nao_expoe_chaves_e_usa_cliente_da_sessao(api_reserva, monkeypatch):
    chave = uuid4()

    def reservar(cliente, idempotencia):
        assert cliente.id == 9 and idempotencia == chave
        return PedidoReservado(
            pedido_id=7,
            status="aguardando_pagamento",
            valor_total=Decimal("39.80"),
            itens=[
                ItemReservado(
                    jogo_id=3,
                    quantidade=2,
                    preco_unitario=Decimal("19.90"),
                    subtotal=Decimal("39.80"),
                )
            ],
        )

    monkeypatch.setattr(reservas, "reservar_carrinho", reservar)
    resposta = api_reserva.post("/pedidos/reservas", json={"chave_idempotencia": str(chave)})
    assert resposta.status_code == 200
    assert resposta.json() == {
        "pedido_id": 7,
        "status": "aguardando_pagamento",
        "valor_total": "39.80",
        "itens": [{"jogo_id": 3, "quantidade": 2, "preco_unitario": "19.90", "subtotal": "39.80"}],
    }


@pytest.mark.parametrize(
    "corpo",
    [
        {},
        {"chave_idempotencia": "invalida"},
        {"chave_idempotencia": None},
        {"chave_idempotencia": str(uuid4()), "usuario_id": 8},
        {"chave_idempotencia": str(uuid4()), "itens": []},
        {"chave_idempotencia": str(uuid4()), "valor_total": 0},
    ],
)
def test_entrada_invalida_nao_chega_ao_banco(api_reserva, monkeypatch, corpo):
    monkeypatch.setattr(reservas, "reservar_carrinho", lambda *_: pytest.fail("Não reservar"))
    assert api_reserva.post("/pedidos/reservas", json=corpo).status_code == 422


@pytest.mark.parametrize(
    "erro,status",
    [
        (carrinho.ClienteNaoPermitido(), 403),
        (carrinho.ClassificacaoNaoPermitida(), 403),
        (carrinho.JogoNaoEncontrado(), 404),
        (carrinho.EstoqueInsuficiente(), 409),
        (reservas.CarrinhoVazio(), 409),
        (reservas.LimiteDoPedido(), 422),
        (BancoNaoConfigurado("senha-privada"), 503),
        (psycopg.OperationalError("senha-privada"), 503),
        (PoolTimeout("senha-privada"), 503),
    ],
)
def test_erros_publicos_sanitizados(api_reserva, monkeypatch, erro, status):
    def falhar(*_):
        raise erro

    monkeypatch.setattr(reservas, "reservar_carrinho", falhar)
    resposta = api_reserva.post("/pedidos/reservas", json={"chave_idempotencia": str(uuid4())})
    assert resposta.status_code == status
    assert "senha-privada" not in resposta.text


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer adulterado"}])
def test_autenticacao_obrigatoria(monkeypatch, headers):
    monkeypatch.setenv("JWT_SECRET", "gk124-teste-contrato-com-mais-de-trinta-e-dois-bytes")
    monkeypatch.setattr(reservas, "reservar_carrinho", lambda *_: pytest.fail("Não reservar"))
    with TestClient(criar_app()) as api:
        resposta = api.post(
            "/pedidos/reservas", headers=headers, json={"chave_idempotencia": str(uuid4())}
        )
    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"


def test_perfil_administrador_recusado_antes_do_pool(monkeypatch):
    monkeypatch.setattr(reservas, "obter_pool", lambda: pytest.fail("Não abrir pool"))
    cliente = ClienteCadastrado(
        id=3,
        nome="Admin",
        email="admin@example.com",
        data_nascimento=date(1990, 1, 1),
        perfil="administrador",
    )
    with pytest.raises(carrinho.ClienteNaoPermitido):
        reservas.reservar_carrinho(cliente, uuid4())
