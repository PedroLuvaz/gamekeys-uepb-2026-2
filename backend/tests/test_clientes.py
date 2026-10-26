"""Contrato e regras unitárias do cadastro de clientes (GK-78)."""

from datetime import date

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.db import BancoNaoConfigurado
from app.esquemas.clientes import CadastroDeCliente, ClienteCadastrado
from app.main import app
from app.servicos import clientes

client = TestClient(app)

DADOS_VALIDOS = {
    "nome": "Ana Cliente",
    "email": "ana@example.com",
    "data_nascimento": "2000-05-20",
    "senha": "segredo123",
}


def test_hash_bcrypt_nao_contem_senha():
    senha = "segredo123"
    senha_hash = clientes.gerar_hash(senha)

    assert senha not in senha_hash
    assert senha_hash.startswith(("$2a$", "$2b$", "$2y$"))
    assert len(senha_hash) == 60


def test_cadastro_valido_retorna_cliente_sem_senha(monkeypatch):
    recebido = None

    def cadastrar(dados):
        nonlocal recebido
        recebido = dados
        return ClienteCadastrado(
            id=42,
            nome=dados.nome,
            email=dados.email,
            data_nascimento=dados.data_nascimento,
            perfil="cliente",
        )

    monkeypatch.setattr(clientes, "cadastrar", cadastrar)

    resposta = client.post("/clientes", json=DADOS_VALIDOS)

    assert resposta.status_code == 201
    assert recebido.email == "ana@example.com"
    assert resposta.json() == {
        "id": 42,
        "nome": "Ana Cliente",
        "email": "ana@example.com",
        "data_nascimento": "2000-05-20",
        "perfil": "cliente",
    }
    assert "senha" not in resposta.text.lower()
    assert "hash" not in resposta.text.lower()


@pytest.mark.parametrize("senha", ["", "1234567"])
def test_senha_curta_e_recusada_sem_cadastrar(monkeypatch, senha):
    monkeypatch.setattr(clientes, "cadastrar", lambda _: pytest.fail("não deve cadastrar"))

    resposta = client.post("/clientes", json={**DADOS_VALIDOS, "senha": senha})

    assert resposta.status_code == 422
    assert "pelo menos 8 caracteres" in resposta.text


def test_email_repetido_recebe_mensagem_clara(monkeypatch):
    def duplicar(_):
        raise psycopg.errors.UniqueViolation("índice interno que não deve ser exposto")

    monkeypatch.setattr(clientes, "cadastrar", duplicar)

    resposta = client.post("/clientes", json=DADOS_VALIDOS)

    assert resposta.status_code == 409
    assert resposta.json() == {"detail": "Este e-mail já está em uso."}


@pytest.mark.parametrize(
    "erro", [BancoNaoConfigurado("segredo"), psycopg.OperationalError("host privado")]
)
def test_falha_de_banco_nao_expoe_detalhes(monkeypatch, erro):
    def falhar(_):
        raise erro

    monkeypatch.setattr(clientes, "cadastrar", falhar)

    resposta = client.post("/clientes", json=DADOS_VALIDOS)

    assert resposta.status_code == 503
    assert resposta.json() == {
        "detail": "Não foi possível concluir o cadastro. Tente novamente mais tarde."
    }
    assert "segredo" not in resposta.text
    assert "host privado" not in resposta.text


def test_normaliza_nome_e_email():
    dados = CadastroDeCliente(
        nome="  Ana Cliente  ",
        email="  ANA@EXAMPLE.COM ",
        data_nascimento=date(2000, 5, 20),
        senha="segredo123",
    )

    assert dados.nome == "Ana Cliente"
    assert dados.email == "ana@example.com"
