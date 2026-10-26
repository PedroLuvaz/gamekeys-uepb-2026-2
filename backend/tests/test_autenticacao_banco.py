"""Login e autorização integrados ao PostgreSQL isolado (GK-81)."""

from fastapi.testclient import TestClient
from psycopg_pool import ConnectionPool

from app.main import app
from app.servicos import autenticacao, clientes


def test_cadastro_login_e_rota_protegida_usam_usuario_persistido(banco, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "integracao-local-com-mais-de-trinta-e-dois-bytes")
    monkeypatch.setenv("JWT_DURACAO_MINUTOS", "60")
    pool = ConnectionPool(banco, min_size=1, max_size=2, open=True)
    monkeypatch.setattr(clientes, "obter_pool", lambda: pool)
    monkeypatch.setattr(autenticacao, "obter_pool", lambda: pool)
    client = TestClient(app)
    cadastro = {
        "nome": "Cliente Autenticado",
        "email": "autenticado@example.com",
        "data_nascimento": "1998-04-12",
        "senha": "segredo123",
    }

    criada = client.post("/clientes", json=cadastro)
    login = client.post(
        "/auth/login", json={"email": cadastro["email"], "senha": cadastro["senha"]}
    )
    conta = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert criada.status_code == 201
    assert login.status_code == 200
    assert login.json()["expires_in"] == 3600
    assert conta.status_code == 200
    assert conta.json() == criada.json()

    respostas_invalidas = [
        client.post("/auth/login", json={"email": cadastro["email"], "senha": "senha-errada"}),
        client.post(
            "/auth/login", json={"email": "inexistente@example.com", "senha": "senha-errada"}
        ),
    ]
    assert [resposta.status_code for resposta in respostas_invalidas] == [401, 401]
    assert respostas_invalidas[0].json() == respostas_invalidas[1].json()

    with pool.connection() as conexao:
        conexao.execute(
            "update core.usuarios set ativo = false where id = %s",
            (criada.json()["id"],),
        )
    bloqueada = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )
    assert bloqueada.status_code == 401

    with pool.connection() as conexao:
        conexao.execute("delete from core.usuarios where id = %s", (criada.json()["id"],))
    pool.close()
