"""GK-129: CLI, reserva concorrente real, falhas e limpeza do cenário local."""

import json
import os
import subprocess
import sys
from pathlib import Path

import psycopg
import pytest

from qa import gk129_reserva_concorrente as experimento
from qa.gk110_concorrencia import BancoDeTesteInseguro


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://usuario:segredo@exemplo.neon.tech/gamekeys_teste",
        "postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys",
        "host=localhost hostaddr=203.0.113.1 dbname=gamekeys_teste",
    ],
)
def test_recusa_url_insegura_antes_de_abrir_pool(url, monkeypatch):
    def pool_proibido(*args, **kwargs):
        pytest.fail("não deve abrir conexão para URL insegura")

    monkeypatch.setattr(experimento, "ConnectionPool", pool_proibido)
    with pytest.raises(BancoDeTesteInseguro):
        experimento.executar_estresse(url, rodadas=1, concorrentes=2)


@pytest.mark.parametrize("rodadas,concorrentes", [(0, 20), (3, 1)])
def test_recusa_quantidades_invalidas(rodadas, concorrentes):
    with pytest.raises(ValueError, match="ao menos"):
        experimento.executar_estresse(
            "postgresql://gamekeys:gamekeys@localhost/gamekeys_teste",
            rodadas=rodadas,
            concorrentes=concorrentes,
        )


def contagens(url: str) -> list[int]:
    with psycopg.connect(url) as conexao:
        return [
            conexao.execute(f"select count(*) from {tabela}").fetchone()[0]
            for tabela in (
                "core.usuarios",
                "catalogo.categorias",
                "catalogo.jogos",
                "catalogo.chaves",
                "vendas.carrinhos",
                "vendas.itens_carrinho",
                "vendas.pedidos",
                "vendas.itens_pedido",
            )
        ]


@pytest.mark.concorrencia
def test_cli_tres_rodadas_vinte_clientes_com_reserva_real_e_limpeza(banco):
    antes = contagens(banco)
    processo = subprocess.run(
        [
            sys.executable,
            "-m",
            "qa.gk129_reserva_concorrente",
            "--rodadas",
            "3",
            "--concorrentes",
            "20",
        ],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "TEST_DATABASE_URL": banco, "PYTHON_DOTENV_DISABLED": "1"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
    )
    assert processo.returncode == 0, processo.stderr
    relatorio = json.loads(processo.stdout)
    assert relatorio["rodadas"] == 3
    assert relatorio["concorrentes_por_rodada"] == 20
    assert relatorio["tentativas"] == 60
    assert relatorio["resultados"] == {"reservada": 3, "esgotado": 57}
    assert relatorio["rodadas_com_falha"] == 0
    assert relatorio["falhas"] == []
    assert relatorio["duplicidades"] == 0
    assert relatorio["duracao_segundos"] > 0
    assert contagens(banco) == antes


@pytest.mark.concorrencia
def test_erro_do_servico_falha_rodada_sem_confundir_com_estoque_e_limpa(banco, monkeypatch):
    from app.servicos import reservas

    def falhar(*args):
        raise psycopg.OperationalError("erro proposital")

    antes = contagens(banco)
    monkeypatch.setattr(reservas, "reservar_na_conexao", falhar)
    relatorio = experimento.executar_estresse(banco, rodadas=1, concorrentes=2)
    assert relatorio["resultados"] == {"erro": 2}
    assert relatorio["rodadas_com_falha"] == 1
    assert relatorio["falhas"][0]["erros"] == ["OperationalError", "OperationalError"]
    assert contagens(banco) == antes


@pytest.mark.parametrize("falhas,codigo", [(0, 0), (1, 1)])
def test_cli_codigo_de_saida_conforme_relatorio(monkeypatch, capsys, falhas, codigo):
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://localhost/gamekeys_teste")
    monkeypatch.setattr(sys, "argv", ["gk129_reserva_concorrente"])
    monkeypatch.setattr(
        experimento, "executar_estresse", lambda *a, **k: {"rodadas_com_falha": falhas}
    )
    assert experimento.main() == codigo
    assert json.loads(capsys.readouterr().out) == {"rodadas_com_falha": falhas}
