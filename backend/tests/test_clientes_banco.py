"""Integração do cadastro com o PostgreSQL isolado (GK-78/GK-69)."""

import bcrypt
from fastapi.testclient import TestClient
from psycopg_pool import ConnectionPool

from app.main import app
from app.servicos import clientes


def test_cadastro_persiste_cliente_com_hash_e_email_unico(banco, monkeypatch):
    pool = ConnectionPool(banco, min_size=1, max_size=1, open=True)
    monkeypatch.setattr(clientes, "obter_pool", lambda: pool)
    client = TestClient(app)
    dados = {
        "nome": "Cliente Persistido",
        "email": "CLIENTE@EXAMPLE.COM",
        "data_nascimento": "1997-08-14",
        "senha": "senha-forte",
    }

    resposta = client.post("/clientes", json=dados)

    assert resposta.status_code == 201
    with pool.connection() as conexao:
        usuario = conexao.execute(
            "select nome, email, senha_hash, data_nascimento, perfil"
            " from core.usuarios where id = %s",
            (resposta.json()["id"],),
        ).fetchone()
    assert usuario[:2] == ("Cliente Persistido", "cliente@example.com")
    assert str(usuario[3]) == "1997-08-14"
    assert usuario[4] == "cliente"
    assert usuario[2] != dados["senha"]
    assert bcrypt.checkpw(dados["senha"].encode(), usuario[2].encode())
    assert set(resposta.json()) == {"id", "nome", "email", "data_nascimento", "perfil"}

    duplicado = client.post("/clientes", json={**dados, "email": "cliente@example.com"})

    assert duplicado.status_code == 409
    with pool.connection() as conexao:
        quantidade = conexao.execute(
            "select count(*) from core.usuarios where lower(email) = 'cliente@example.com'"
        ).fetchone()[0]
        conexao.execute("delete from core.usuarios where id = %s", (resposta.json()["id"],))
    assert quantidade == 1
    pool.close()
