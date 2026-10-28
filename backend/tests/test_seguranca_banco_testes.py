"""Regressão da GK-106: pytest nunca pode destruir PostgreSQL remoto."""

import pytest
from conftest import _validar_url_banco_teste


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "[::1]"])
def test_aceita_banco_de_testes_local(host):
    url = f"postgresql://gamekeys:gamekeys@{host}:5433/gamekeys_teste?sslmode=disable"

    assert _validar_url_banco_teste(url) == url


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://usuario:senha@ep-neon.aws.neon.tech/gamekeys_teste?sslmode=require",
        "postgresql://usuario:senha@banco.exemplo.com/gamekeys_teste",
        "postgresql://usuario:senha@127.0.0.1:5433/gamekeys",
        "dbname=gamekeys_teste service=neon",
        (
            "postgresql://usuario:senha@localhost/gamekeys_teste"
            "?hostaddr=203.0.113.10&sslmode=require"
        ),
    ],
)
def test_recusa_banco_remoto_ou_banco_incorreto(url):
    with pytest.raises(pytest.UsageError):
        _validar_url_banco_teste(url)


def test_recusa_url_invalida_sem_expor_credenciais():
    with pytest.raises(pytest.UsageError, match="conexão PostgreSQL válida"):
        _validar_url_banco_teste("não-é-uma-url")
