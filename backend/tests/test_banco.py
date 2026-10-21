import os

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app

client = TestClient(app)


def test_saude_banco_sem_url_responde_503(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    db.fechar_pool()

    resposta = client.get("/saude/banco")

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "DATABASE_URL não definida"}


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="sem DATABASE_URL")
def test_saude_banco_consulta_o_postgres():
    db.fechar_pool()

    resposta = client.get("/saude/banco")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["banco"]
    assert corpo["versao"]
