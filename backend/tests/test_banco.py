import os

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app

client = TestClient(app)
ORIGEM_DO_FRONT = "http://localhost:5173"


@pytest.fixture(autouse=True)
def pool_novo():
    db.fechar_pool()
    yield
    db.fechar_pool()


def test_saude_banco_sem_url_responde_503(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    resposta = client.get("/saude/banco")

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "DATABASE_URL não definida"}


def test_banco_indisponivel_responde_503_sem_expor_a_conexao(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://usuario:senha-secreta@127.0.0.1:1/gamekeys")
    monkeypatch.setenv("BANCO_TIMEOUT_SEGUNDOS", "1")

    resposta = client.get("/saude/banco")

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "banco indisponível"}
    assert "senha-secreta" not in resposta.text
    assert "127.0.0.1" not in resposta.text


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="sem DATABASE_URL")
@pytest.mark.smoke
def test_saude_banco_consulta_o_postgres():
    resposta = client.get("/saude/banco")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["banco"]
    assert corpo["versao"]


@pytest.mark.smoke
def test_front_na_origem_permitida_consulta_a_api():
    preflight = client.options(
        "/saude",
        headers={"Origin": ORIGEM_DO_FRONT, "Access-Control-Request-Method": "GET"},
    )
    resposta = client.get("/saude", headers={"Origin": ORIGEM_DO_FRONT})

    assert preflight.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == ORIGEM_DO_FRONT


def test_origem_desconhecida_nao_recebe_liberacao_de_cors():
    resposta = client.get("/saude", headers={"Origin": "http://site-qualquer.com"})

    assert "access-control-allow-origin" not in resposta.headers
