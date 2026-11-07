"""GK-120: a preparação destrutiva do navegador também recusa banco compartilhado."""

import pytest

from qa import gk11_carrinho
from qa.gk110_concorrencia import BancoDeTesteInseguro


@pytest.mark.parametrize(
    "acao",
    [
        gk11_carrinho.preparar,
        lambda: gk11_carrinho.limpar({"chave": "a" * 32}),
        lambda: gk11_carrinho.estado({"chave": "a" * 32}),
    ],
)
@pytest.mark.parametrize(
    "url",
    [
        "postgresql://teste:segredo@exemplo.neon.tech/gamekeys_teste",
        "postgresql://teste:segredo@127.0.0.1/gamekeys",
    ],
)
def test_fixture_recusa_alvo_inseguro_antes_de_conectar(monkeypatch, acao, url):
    monkeypatch.setenv("TEST_DATABASE_URL", url)
    monkeypatch.setattr(
        gk11_carrinho.psycopg, "connect", lambda *_a, **_kw: pytest.fail("Não conectar")
    )
    with pytest.raises(BancoDeTesteInseguro):
        acao()


def test_limpeza_recusa_identificador_arbitrario_antes_de_conectar(monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://teste:local@127.0.0.1/gamekeys_teste")
    monkeypatch.setattr(
        gk11_carrinho.psycopg, "connect", lambda *_a, **_kw: pytest.fail("Não conectar")
    )
    with pytest.raises(ValueError):
        gk11_carrinho.limpar({"chave": "outro-usuario"})
