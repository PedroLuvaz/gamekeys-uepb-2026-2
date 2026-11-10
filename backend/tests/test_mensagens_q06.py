"""Q-06: erros de validação públicos permanecem claros e em português."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.esquemas.clientes import ClienteCadastrado
from app.main import criar_app
from app.rotas.autenticacao import usuario_atual


@pytest.fixture
def api():
    app = criar_app()
    app.dependency_overrides[usuario_atual] = lambda: ClienteCadastrado(
        id=91,
        nome="Cliente Q-06",
        email="q06@example.com",
        data_nascimento=date(1990, 1, 1),
        perfil="cliente",
    )
    return TestClient(app)


def mensagens_por_campo(resposta):
    assert resposta.status_code == 422
    detalhes = resposta.json()["detail"]
    assert detalhes
    assert all("Field required" not in item["msg"] for item in detalhes)
    assert all("Input should be" not in item["msg"] for item in detalhes)
    return {item["loc"][-1]: item["msg"] for item in detalhes}


def test_cadastro_obrigatorio_nao_expoe_field_required(api):
    mensagens = mensagens_por_campo(api.post("/clientes", json={}))

    assert mensagens == {
        "nome": "Informe um nome entre 2 e 120 caracteres.",
        "email": "Informe um e-mail válido.",
        "data_nascimento": "Informe uma data de nascimento válida.",
        "senha": "Informe sua senha.",
    }


@pytest.mark.parametrize(
    "campo,valor,mensagem",
    [
        ("email", "sem-arroba", "Informe um e-mail válido."),
        ("senha", "1234567", "A senha deve ter pelo menos 8 caracteres."),
        ("data_nascimento", "2026-02-30", "Informe uma data de nascimento válida."),
    ],
)
def test_cadastro_invalido_tem_mensagem_em_portugues(api, campo, valor, mensagem):
    dados = {
        "nome": "Cliente Mensagem",
        "email": "mensagem@example.com",
        "data_nascimento": "2000-01-01",
        "senha": "segredo123",
        campo: valor,
    }

    assert mensagens_por_campo(api.post("/clientes", json=dados))[campo] == mensagem


@pytest.mark.parametrize(
    "metodo,caminho,corpo,campo,mensagem",
    [
        (
            "post",
            "/auth/login",
            {"email": "invalido", "senha": "segredo123"},
            "email",
            "Informe um e-mail válido.",
        ),
        (
            "post",
            "/carrinho/itens",
            {"jogo_id": 1, "quantidade": "2"},
            "quantidade",
            "Informe uma quantidade inteira maior que zero.",
        ),
        (
            "patch",
            "/carrinho/itens/1",
            {},
            "quantidade",
            "Informe uma quantidade inteira maior que zero.",
        ),
        (
            "patch",
            "/carrinho/itens/invalido",
            {"quantidade": 1},
            "jogo_id",
            "Informe um jogo válido.",
        ),
        (
            "post",
            "/pedidos/reservas",
            {"chave_idempotencia": "invalida"},
            "chave_idempotencia",
            "Informe um identificador de reserva válido.",
        ),
    ],
)
def test_validacoes_dos_fluxos_nao_expoem_input_should(
    api, metodo, caminho, corpo, campo, mensagem
):
    resposta = api.request(metodo, caminho, json=corpo)

    assert mensagens_por_campo(resposta)[campo] == mensagem


def test_campo_extra_tem_mensagem_clara(api):
    resposta = api.post("/carrinho/itens", json={"jogo_id": 1, "usuario_id": 91})

    assert mensagens_por_campo(resposta)["usuario_id"] == "Este campo não é aceito."
