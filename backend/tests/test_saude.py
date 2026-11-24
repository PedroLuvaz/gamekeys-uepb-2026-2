import pytest
from fastapi.testclient import TestClient

from app.config import Configuracoes
from app.main import app, criar_app

client = TestClient(app)


def configuracoes(ambiente: str) -> Configuracoes:
    return Configuracoes(ambiente=ambiente, database_url=None, origens_cors=(), timeout_banco=1)


@pytest.mark.smoke
def test_saude_responde_ok():
    resposta = client.get("/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_documentacao_automatica_em_desenvolvimento():
    cliente = TestClient(criar_app(configuracoes("desenvolvimento")))

    assert cliente.get("/docs").status_code == 200
    assert "/saude" in cliente.get("/openapi.json").json()["paths"]


def test_documentacao_desligada_em_producao():
    cliente = TestClient(criar_app(configuracoes("producao")))

    assert cliente.get("/docs").status_code == 404
    assert cliente.get("/openapi.json").status_code == 404


@pytest.mark.parametrize("commit", ["a" * 40, "valor-invalido", ""])
def test_versao_publica_apenas_sha_valido(monkeypatch, commit):
    monkeypatch.setenv("GAMEKEYS_COMMIT", commit)
    monkeypatch.delenv("VERCEL_GIT_COMMIT_SHA", raising=False)
    monkeypatch.setenv("SEGREDO_FICTICIO", "nao-publicar")
    resposta = client.get("/saude/versao")
    assert resposta.status_code == 200
    assert resposta.json() == {"commit": commit if len(commit) == 40 else "desenvolvimento"}
