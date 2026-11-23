"""GK-149: credenciais fictícias nunca aparecem em traceback, log ou resposta HTTP."""

import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app import db
from app.conexao import ConexaoPostgres, parametros_conexao
from app.main import app

BACKEND = Path(__file__).resolve().parents[1]


def marcador() -> str:
    return "GK149_FICTICIA_" + uuid4().hex


def url_malformada(senha: str) -> str:
    return f"postgresql://qa:{senha}%ZZ@127.0.0.1:1/gamekeys_teste?connect_timeout=1"


@pytest.fixture(autouse=True)
def pool_novo():
    db.fechar_pool()
    yield
    db.fechar_pool()


@pytest.mark.parametrize("formato", ["uri", "keyword"])
def test_parser_nao_expoe_senha_na_cadeia_de_excecoes(formato):
    senha = marcador()
    url = url_malformada(senha) if formato == "uri" else f"host=127.0.0.1 password='{senha}"
    with pytest.raises(psycopg.ProgrammingError) as capturada:
        parametros_conexao(url)

    assert "Configuração da conexão PostgreSQL inválida." in str(capturada.value)
    assert senha not in "".join(traceback.format_exception(capturada.value))


def test_senha_codificada_valida_continua_aceita():
    senha = "ficticia%@ :/"
    parametros = parametros_conexao(
        f"postgresql://qa:{quote(senha, safe='')}@127.0.0.1/gamekeys_teste"
    )
    assert parametros["password"] == senha


@pytest.mark.parametrize(
    "classe",
    [
        psycopg.ProgrammingError,
        psycopg.OperationalError,
        psycopg.errors.InvalidPassword,
        ValueError,
    ],
)
def test_conexao_remove_detalhes_sensiveis_preservando_tipo_e_sqlstate(monkeypatch, classe):
    senha = marcador()
    erro = classe("Detalhe interno que não pode sair: " + senha)
    if isinstance(erro, psycopg.Error) and erro.sqlstate is None:
        erro.sqlstate = "08001"

    def falhar(cls, *args, **kwargs):
        raise erro

    monkeypatch.setattr(psycopg.Connection, "connect", classmethod(falhar))
    esperado = classe if issubclass(classe, psycopg.Error) else psycopg.ProgrammingError
    with pytest.raises(esperado) as capturada:
        ConexaoPostgres.connect("host=127.0.0.1")

    assert senha not in "".join(traceback.format_exception(capturada.value))
    assert "Falha ao conectar ao PostgreSQL." in str(capturada.value)
    assert capturada.value.sqlstate == getattr(erro, "sqlstate", None)


@pytest.mark.parametrize("modo", ["configuracao", "conexao"])
def test_api_e_logs_do_pool_nao_expoem_segredo(monkeypatch, caplog, modo):
    senha = marcador()
    url = url_malformada(senha)
    if modo == "conexao":
        # O parser aceita a URL; o erro de conexão também pode conter detalhes sensíveis.
        url = "postgresql://qa@127.0.0.1:1/gamekeys_teste"

        def falhar(cls, *args, **kwargs):
            raise psycopg.OperationalError("Mensagem interna com senha: " + senha)

        monkeypatch.setattr(psycopg.Connection, "connect", classmethod(falhar))

    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("BANCO_TIMEOUT_SEGUNDOS", "0.1")
    with caplog.at_level(logging.WARNING, logger="psycopg.pool"):
        resposta = TestClient(app).get("/saude/banco")
        db.fechar_pool()

    assert resposta.status_code == 503
    assert resposta.json() == {"detail": "banco indisponível"}
    assert senha not in resposta.text
    assert senha not in caplog.text
    if modo == "conexao":
        assert "Falha ao conectar ao PostgreSQL." in caplog.text


@pytest.mark.parametrize("entrada", ["pytest", "qa110", "qa129", "carrinho", "checkout"])
def test_processos_reais_recusam_url_malformada_sem_imprimir_senha(entrada):
    senha = marcador()
    url = url_malformada(senha)
    ambiente = os.environ.copy()
    ambiente.update(
        PYTHON_DOTENV_DISABLED="1",
        PYTHONUTF8="1",
        PYTEST_ADDOPTS="",
        DATABASE_URL=url,
        DATABASE_URL_UNPOOLED=url,
        TEST_DATABASE_URL=url,
        PGHOST="127.0.0.1",
        PGPORT="1",
        PGDATABASE="gamekeys_teste",
        PGUSER="qa",
        PGPASSWORD=senha,
        JWT_SECRET="segredo-ficticio-gk149-exclusivo-do-subprocesso",
    )
    comandos = {
        "pytest": [
            "-m",
            "pytest",
            "tests/test_estrutura_banco.py::test_carga_tem_ativos_esgotado_e_inativo",
            "--tb=short",
            "-q",
        ],
        "qa110": ["-m", "qa.gk110_concorrencia", "--rodadas", "1", "--concorrentes", "2"],
        "qa129": ["-m", "qa.gk129_reserva_concorrente", "--rodadas", "1", "--concorrentes", "2"],
        "carrinho": ["-m", "qa.gk11_carrinho", "preparar"],
        "checkout": ["-m", "qa.gk14_checkout", "preparar"],
    }
    processo = subprocess.run(
        [sys.executable, *comandos[entrada]],
        cwd=BACKEND,
        env=ambiente,
        input="{}",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    saida = processo.stdout + processo.stderr
    assert processo.returncode == 1
    assert senha not in saida
    # Prova que executamos a recusa esperada, não apenas um processo que falhou ao importar.
    assert (
        "conexão PostgreSQL válida" in saida
        or "URL PostgreSQL válida" in saida
        or '"tipo": "BancoDeTesteInseguro"' in saida
    )
