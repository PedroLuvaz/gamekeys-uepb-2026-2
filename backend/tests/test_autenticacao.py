"""Contrato de login, JWT e autorização sem acesso ao banco (GK-81)."""

from datetime import UTC, date, datetime

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.servicos import autenticacao

client = TestClient(app)
SEGREDO_TESTE = "segredo-de-teste-com-mais-de-trinta-e-dois-bytes"


@pytest.fixture(autouse=True)
def configurar_jwt(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", SEGREDO_TESTE)
    monkeypatch.setenv("JWT_DURACAO_MINUTOS", "60")


def usuario() -> autenticacao.UsuarioPersistido:
    return autenticacao.UsuarioPersistido(
        id=9,
        nome="Cliente Login",
        email="cliente@example.com",
        senha_hash="$2b$12$" + "b" * 53,
        data_nascimento=date(2000, 1, 1),
        perfil="cliente",
        ativo=True,
    )


def test_login_valido_emite_jwt_de_60_minutos(monkeypatch):
    monkeypatch.setattr(autenticacao, "autenticar", lambda email, senha: usuario())
    agora = datetime.now(UTC)

    resposta = client.post(
        "/auth/login", json={"email": "CLIENTE@example.com", "senha": "segredo123"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["expires_in"] == 3600
    assert set(corpo["usuario"]) == {"id", "nome", "email", "data_nascimento", "perfil"}
    dados = jwt.decode(
        corpo["access_token"],
        SEGREDO_TESTE,
        algorithms=["HS256"],
        issuer="gamekeys",
    )
    assert dados["sub"] == "9"
    assert dados["perfil"] == "cliente"
    assert 3595 <= dados["exp"] - int(agora.timestamp()) <= 3605


@pytest.mark.parametrize("email,senha", [("nao@existe.com", "segredo123"), ("a@b.com", "errada")])
def test_credenciais_incorretas_tem_a_mesma_resposta(monkeypatch, email, senha):
    monkeypatch.setattr(autenticacao, "autenticar", lambda _email, _senha: None)

    resposta = client.post("/auth/login", json={"email": email, "senha": senha})

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "E-mail ou senha incorretos."}


def test_rota_protegida_recusa_token_ausente():
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401
    assert resposta.headers["www-authenticate"] == "Bearer"
    assert resposta.json() == {"detail": "Não foi possível autenticar. Entre novamente."}


@pytest.mark.parametrize("token", ["token-adulterado", "", "abc.def.ghi"])
def test_rota_protegida_recusa_token_invalido(token):
    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "Não foi possível autenticar. Entre novamente."}


def test_rota_protegida_recusa_token_expirado(monkeypatch):
    token, _ = autenticacao.criar_token(
        usuario(), agora=datetime(2025, 1, 1, tzinfo=UTC), duracao_minutos=1
    )
    monkeypatch.setattr(
        autenticacao,
        "buscar_ativo_por_id",
        lambda _: pytest.fail("token expirado não deve consultar o usuário"),
    )

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401


def test_rota_protegida_reconsulta_usuario_ativo(monkeypatch):
    token, _ = autenticacao.criar_token(usuario())
    ids = []

    def buscar(usuario_id):
        ids.append(usuario_id)
        return usuario()

    monkeypatch.setattr(autenticacao, "buscar_ativo_por_id", buscar)

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert ids == [9]
    assert resposta.json()["email"] == "cliente@example.com"


def test_login_sem_segredo_configurado_falha_sem_expor_configuracao(monkeypatch):
    monkeypatch.setattr(autenticacao, "autenticar", lambda email, senha: usuario())
    monkeypatch.delenv("JWT_SECRET", raising=False)

    resposta = client.post(
        "/auth/login", json={"email": "cliente@example.com", "senha": "segredo123"}
    )

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "Autenticação temporariamente indisponível."}
    assert "JWT_SECRET" not in resposta.text


def test_login_com_segredo_curto_falha_sem_emitir_token(monkeypatch):
    monkeypatch.setattr(autenticacao, "autenticar", lambda email, senha: usuario())
    monkeypatch.setenv("JWT_SECRET", "curto")

    resposta = client.post(
        "/auth/login", json={"email": "cliente@example.com", "senha": "segredo123"}
    )

    assert resposta.status_code == 503
    assert "access_token" not in resposta.text


def test_senha_maior_que_limite_do_bcrypt_e_tratada_como_incorreta(monkeypatch):
    monkeypatch.setattr(autenticacao, "buscar_por_email", lambda email: usuario())

    assert autenticacao.autenticar("cliente@example.com", "á" * 73) is None
