"""GK-118: contrato, validação, autorização e erros sem acesso ao banco."""

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.db import BancoNaoConfigurado
from app.esquemas.carrinho import AdicaoAoCarrinho, ItemDoCarrinho
from app.esquemas.clientes import ClienteCadastrado
from app.main import criar_app
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho


@pytest.fixture
def cliente_autorizado():
    return ClienteCadastrado(
        id=7,
        nome="Cliente Teste",
        email="carrinho@example.com",
        data_nascimento=date(2000, 1, 1),
        perfil="cliente",
    )


@pytest.fixture
def api(cliente_autorizado):
    app = criar_app()
    app.dependency_overrides[usuario_atual] = lambda: cliente_autorizado
    return TestClient(app)


def test_adicionar_retorna_quantidade_final_e_dinheiro_decimal(api, monkeypatch):
    chamadas = []

    def adicionar(cliente, dados):
        chamadas.append((cliente.id, dados.jogo_id, dados.quantidade))
        return ItemDoCarrinho(
            carrinho_id=4,
            jogo_id=9,
            nome="Aventura",
            quantidade=3,
            preco_unitario=Decimal("19.90"),
            subtotal=Decimal("59.70"),
        )

    monkeypatch.setattr(carrinho, "adicionar_item", adicionar)
    resposta = api.post("/carrinho/itens", json={"jogo_id": 9})

    assert resposta.status_code == 200
    assert chamadas == [(7, 9, 1)]
    assert resposta.json() == {
        "carrinho_id": 4,
        "jogo_id": 9,
        "nome": "Aventura",
        "quantidade": 3,
        "preco_unitario": "19.90",
        "subtotal": "59.70",
    }


@pytest.mark.parametrize(
    "dados",
    [
        {},
        {"jogo_id": 0},
        {"jogo_id": -1},
        {"jogo_id": True},
        {"jogo_id": "1"},
        {"jogo_id": 9223372036854775808},
        *(
            {"jogo_id": 1, "quantidade": valor}
            for valor in (0, -1, 1.5, True, "2", None, 2147483648)
        ),
        {"jogo_id": 1, "usuario_id": 8},
        {"jogo_id": 1, "carrinho_id": 8},
        {"jogo_id": 1, "preco_unitario": "0.01"},
        {"jogo_id": 1, "data_nascimento": "1900-01-01"},
    ],
)
def test_entrada_invalida_nao_chega_ao_servico(api, monkeypatch, dados):
    def nao_chamar(*_):
        pytest.fail("Entrada inválida não pode modificar o carrinho")

    monkeypatch.setattr(carrinho, "adicionar_item", nao_chamar)
    assert api.post("/carrinho/itens", json=dados).status_code == 422


@pytest.mark.parametrize(
    "erro,status,mensagem",
    [
        (carrinho.ClienteNaoPermitido(), 403, "O carrinho é exclusivo de clientes."),
        (
            carrinho.ClassificacaoNaoPermitida(),
            403,
            "Sua idade não permite adicionar este jogo ao carrinho.",
        ),
        (carrinho.JogoNaoEncontrado(), 404, "Jogo não encontrado."),
        (carrinho.EstoqueInsuficiente(), 409, "Estoque insuficiente para a quantidade solicitada."),
        (
            BancoNaoConfigurado(),
            503,
            "Carrinho temporariamente indisponível. Tente novamente em instantes.",
        ),
        (
            psycopg.OperationalError("dados privados de conexão"),
            503,
            "Carrinho temporariamente indisponível. Tente novamente em instantes.",
        ),
    ],
)
def test_erros_publicos_nao_expoem_dados_internos(api, monkeypatch, erro, status, mensagem):
    def falhar(*_):
        raise erro

    monkeypatch.setattr(carrinho, "adicionar_item", falhar)
    resposta = api.post("/carrinho/itens", json={"jogo_id": 1})

    assert resposta.status_code == status
    assert resposta.json() == {"detail": mensagem}


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer adulterado"}])
def test_sem_autenticacao_nao_chama_o_servico(monkeypatch, headers):
    def nao_chamar(*_):
        pytest.fail("Token inválido não pode chegar ao carrinho")

    monkeypatch.setenv("JWT_SECRET", "segredo-local-de-contrato-com-mais-de-32-bytes")
    monkeypatch.setattr(carrinho, "adicionar_item", nao_chamar)
    resposta = TestClient(criar_app()).post("/carrinho/itens", json={"jogo_id": 1}, headers=headers)

    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"


def test_administrador_nao_chega_ao_banco(cliente_autorizado, monkeypatch):
    monkeypatch.setattr(carrinho, "obter_pool", lambda: pytest.fail("Não abrir conexão"))
    administrador = cliente_autorizado.model_copy(update={"perfil": "administrador"})

    with pytest.raises(carrinho.ClienteNaoPermitido):
        carrinho.adicionar_item(administrador, AdicaoAoCarrinho(jogo_id=1))


@pytest.mark.parametrize(
    "nascimento,hoje,idade",
    [
        (date(2008, 11, 7), date(2026, 11, 7), 18),
        (date(2008, 11, 8), date(2026, 11, 7), 17),
        (date(2008, 2, 29), date(2026, 2, 28), 17),
        (date(2008, 2, 29), date(2026, 3, 1), 18),
    ],
)
def test_idade_completa_no_aniversario_e_em_ano_nao_bissexto(nascimento, hoje, idade):
    assert carrinho.idade_em_anos(nascimento, hoje) == idade
