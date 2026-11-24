"""GK-136: decisões de publicação/recusa/rollback, sem alterar Vercel ou Neon."""

import json
from copy import deepcopy
from types import SimpleNamespace

import psycopg
import pytest

from qa import gk136_configurar as configurar
from qa import gk136_homologacao as h
from qa.gk136_configurar import completar_ruleset

SHA = "a" * 40


def ci_aprovado():
    return {
        "id": 123,
        "head_sha": SHA,
        "head_branch": "main",
        "event": "push",
        "path": ".github/workflows/ci.yml",
        "status": "completed",
        "conclusion": "success",
        "head_repository": {"full_name": h.REPOSITORIO},
    }


def github(run):
    def consultar(caminho):
        if caminho == "/git/ref/heads/main":
            return {"object": {"sha": SHA}}
        if caminho.startswith("/actions/workflows/"):
            return {"workflow_runs": [run]}
        assert caminho == "/actions/runs/123"
        return run

    return consultar


@pytest.mark.parametrize("run_id", [None, "123"])
def test_ci_exige_commit_atual_da_main(run_id):
    assert h.confirmar_ci(github(ci_aprovado()), run_id) == (SHA, "123")


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("conclusion", "failure"),
        ("status", "in_progress"),
        ("event", "pull_request"),
        ("head_branch", "feature/terceiro"),
        ("head_sha", "b" * 40),
        ("path", ".github/workflows/outro.yml"),
        ("head_sha", "invalid"),
        ("head_repository", {"full_name": "terceiro/fork"}),
    ],
)
def test_ci_inseguro_ou_desatualizado_nao_publica(campo, valor):
    run = ci_aprovado()
    run[campo] = valor
    with pytest.raises(h.PublicacaoBloqueada):
        h.confirmar_ci(github(run), "123")


class VercelFalso:
    def __init__(self, falha=None):
        self.eventos = []
        self.falha = falha

    def projeto(self, nome):
        return {"name": nome, "id": nome, "targets": {"production": {"id": "anterior-" + nome}}}

    def preparar(self, projeto, sha):
        self.eventos.append(("preparar", projeto["name"]))
        if self.falha == "build" and projeto["name"] == "gamekeys-web":
            raise h.PublicacaoBloqueada("build recusado")
        return "https://" + projeto["name"] + "-staged.vercel.app"

    def consultar(self, projeto, url, caminho):
        if caminho == "/saude/banco":
            return {"status": "ok", "banco": "gamekeys"}
        return {"commit": "b" * 40 if self.falha == "versao" else SHA}

    def promover(self, projeto, url):
        self.eventos.append(("promover", projeto["name"]))
        if self.falha in {"promocao", "restauracao"} and projeto["name"] == "gamekeys-web":
            raise h.PublicacaoBloqueada("promoção recusada")
        if self.falha == "inesperada":
            raise RuntimeError("detalhe protegido")

    def restaurar(self, projeto, anterior):
        self.eventos.append(("restaurar", projeto["name"]))
        assert anterior == "anterior-" + projeto["name"]
        if self.falha == "restauracao":
            raise h.PublicacaoBloqueada("restauração recusada")


def test_sucesso_prepara_os_dois_antes_de_promover_e_registra_versao():
    vercel = VercelFalso()
    relatorio, leituras, verificacoes = {}, [], []

    def banco():
        leituras.append("somente leitura")
        return ["0001.sql"]

    h.publicar(
        SHA,
        github(ci_aprovado()),
        vercel,
        banco,
        lambda url, sha: verificacoes.append((url, sha)),
        relatorio,
    )
    assert vercel.eventos == [
        ("preparar", "gamekeys-api"),
        ("preparar", "gamekeys-web"),
        ("promover", "gamekeys-api"),
        ("promover", "gamekeys-web"),
    ]
    assert len(leituras) == 2
    assert verificacoes == [
        ("https://gamekeys-api.vercel.app", SHA),
        ("https://gamekeys-web.vercel.app", SHA),
    ]
    assert set(relatorio["publicacoes"]) == set(h.PROJETOS)


@pytest.mark.parametrize("falha", ["build", "versao"])
def test_build_ou_versao_errada_preserva_enderecos_anteriores(falha):
    vercel = VercelFalso(falha)
    with pytest.raises(h.PublicacaoBloqueada):
        h.publicar(SHA, github(ci_aprovado()), vercel, lambda: [], lambda *_: None, {})
    assert not any(e[0] in {"promover", "restaurar"} for e in vercel.eventos)


def test_migracao_pendente_bloqueia_antes_de_chamar_vercel():
    vercel = VercelFalso()

    def banco():
        raise h.PublicacaoBloqueada("migração pendente")

    with pytest.raises(h.PublicacaoBloqueada, match="migração"):
        h.publicar(SHA, github(ci_aprovado()), vercel, banco, lambda *_: None, {})
    assert vercel.eventos == []


@pytest.mark.parametrize("falha", ["promocao", "inesperada", "smoke"])
def test_falha_durante_promocao_ou_smoke_restaura_versoes_anteriores(falha):
    vercel = VercelFalso(falha)
    relatorio = {}

    def smoke(*_):
        if falha == "smoke":
            raise h.PublicacaoBloqueada("verificação recusada")

    with pytest.raises(h.PublicacaoBloqueada, match="restauradas"):
        h.publicar(SHA, github(ci_aprovado()), vercel, lambda: [], smoke, relatorio)
    tentados = [p for acao, p in vercel.eventos if acao == "promover"]
    restaurados = [p for acao, p in vercel.eventos if acao == "restaurar"]
    assert restaurados == list(reversed(tentados))
    assert set(relatorio["restauracao"].values()) == {"confirmada"}


def test_falha_de_rollback_e_registrada_sem_anunciar_restauracao_confirmada():
    vercel, relatorio = VercelFalso("restauracao"), {}
    with pytest.raises(h.PublicacaoBloqueada, match="não confirmada"):
        h.publicar(SHA, github(ci_aprovado()), vercel, lambda: [], lambda *_: None, relatorio)
    assert set(relatorio["restauracao"].values()) == {"nao_confirmada"}


@pytest.mark.parametrize("fase", ["main", "migracoes"])
def test_main_ou_banco_mudando_durante_build_bloqueia_promocao(fase):
    vercel = VercelFalso()

    def consultar(_):
        return {"object": {"sha": "b" * 40 if fase == "main" else SHA}}

    contador = 0

    def banco():
        nonlocal contador
        contador += 1
        if contador == 2 and fase == "migracoes":
            raise h.PublicacaoBloqueada("banco alterado")
        return []

    with pytest.raises(h.PublicacaoBloqueada):
        h.publicar(SHA, consultar, vercel, banco, lambda *_: None, {})
    assert not any(e[0] == "promover" for e in vercel.eventos)


def test_checker_migracoes_le_banco_real_e_recusa_manifesto_divergente(
    banco, monkeypatch, tmp_path
):
    # O alvo real é o banco local já validado pela fixture, nunca o endereço fictício.
    leituras = []

    class ConexaoVigiada(psycopg.Connection):
        def execute(self, consulta, *args, **kwargs):
            if consulta == "select nome from public.migracoes_aplicadas":
                assert super().execute("show transaction_read_only").fetchone() == ("on",)
                leituras.append("read only")
            return super().execute(consulta, *args, **kwargs)

    def conectar(url, **kwargs):
        assert url == "dbname=gamekeys host=localhost"
        conexao = ConexaoVigiada.connect(banco, **kwargs)
        conexao.execute("set role gamekeys_equipe")
        return conexao

    monkeypatch.setattr(h.ConexaoPostgres, "connect", conectar)
    assert h.conferir_migracoes("dbname=gamekeys host=localhost") == sorted(
        p.name for p in h.PASTA_MIGRACOES.glob("*.sql")
    )
    (tmp_path / "0000_pendente.sql").write_text("select 1", encoding="utf-8")
    with pytest.raises(h.PublicacaoBloqueada, match="divergentes"):
        h.conferir_migracoes("dbname=gamekeys host=localhost", tmp_path)
    assert leituras == ["read only", "read only"]


def test_checker_recusa_credencial_de_administracao(banco, monkeypatch):
    monkeypatch.setattr(h.ConexaoPostgres, "connect", lambda *_, **kw: psycopg.connect(banco, **kw))
    with pytest.raises(h.PublicacaoBloqueada, match="administrativos"):
        h.conferir_migracoes("dbname=gamekeys host=localhost")


def test_equipe_so_pode_ler_registro_de_migracoes(conexao):
    permissoes = conexao.execute(
        "select has_table_privilege('gamekeys_equipe', 'public.migracoes_aplicadas', 'SELECT'),"
        " has_table_privilege('gamekeys_equipe', 'public.migracoes_aplicadas', 'INSERT'),"
        " has_table_privilege('gamekeys_equipe', 'public.migracoes_aplicadas', 'UPDATE'),"
        " has_table_privilege('gamekeys_equipe', 'public.migracoes_aplicadas', 'DELETE')"
    ).fetchone()
    assert permissoes == (True, False, False, False)


@pytest.mark.parametrize(
    "url",
    [
        "dbname=gamekeys_teste host=localhost",
        "dbname=gamekeys host=exemplo-pooler.neon.tech",
        "dbname=gamekeys host=exemplo.neon.tech",
    ],
)
def test_banco_errado_ou_pooler_recusado_sem_conexao(url):
    with pytest.raises(h.PublicacaoBloqueada):
        h.conferir_migracoes(url)


def test_erro_driver_e_saida_cli_nao_expoem_credenciais(monkeypatch):
    marcador = "SEGREDO_FICTICIO_GK136"

    def falhar(*_, **__):
        raise psycopg.OperationalError(marcador)

    monkeypatch.setattr(h.ConexaoPostgres, "connect", falhar)
    with pytest.raises(h.PublicacaoBloqueada) as erro:
        h.conferir_migracoes("dbname=gamekeys host=localhost")
    assert marcador not in str(erro.value)
    monkeypatch.setattr(h.shutil, "which", lambda _: "vercel")
    monkeypatch.setattr(
        h.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout=marcador, stderr=marcador),
    )
    with pytest.raises(h.PublicacaoBloqueada) as erro:
        h.Vercel(marcador).comando({"accountId": "org", "id": "projeto"}, "deploy")
    assert marcador not in str(erro.value)


# O `vercel curl` 65.2.0 só consome --deployment, --protection-bypass, --scope, --team,
# --yes, --help, --trace e --json antes de `--`; qualquer outra opção, como --token e o
# seu valor, segue para o curl. Execução 45303218571: curl recusou a opção e a
# verificação HTTP falhou sem nenhuma requisição chegar ao build.
CURL_OPCOES_DO_CLI = {"--deployment", "--yes", "--scope"}


def test_token_do_vercel_vai_so_pelo_ambiente_no_curl(monkeypatch):
    monkeypatch.setattr(h.shutil, "which", lambda _: "vercel")

    def executar(args, env, **_):
        assert "token-ficticio" not in args
        assert "--token" not in args
        antes = args[3 : args.index("--")]
        assert {a for a in antes if a.startswith("-")} <= CURL_OPCOES_DO_CLI
        assert env["VERCEL_TOKEN"] == "token-ficticio"
        return SimpleNamespace(returncode=0, stdout=json.dumps({"commit": SHA}))

    monkeypatch.setattr(h.subprocess, "run", executar)
    assert h.Vercel("token-ficticio").consultar(
        {"accountId": "org", "id": "projeto"}, "https://exemplo.vercel.app", "/saude/versao"
    ) == {"commit": SHA}


def test_token_do_vercel_nao_aparece_nos_argumentos_do_deploy(monkeypatch):
    monkeypatch.setattr(h.shutil, "which", lambda _: "vercel")

    def executar(args, env, **_):
        assert "token-ficticio" not in args
        assert env["VERCEL_TOKEN"] == "token-ficticio"
        return SimpleNamespace(returncode=0, stdout="https://exemplo.vercel.app")

    monkeypatch.setattr(h.subprocess, "run", executar)
    assert (
        h.Vercel("token-ficticio").preparar({"accountId": "org", "id": "projeto"}, SHA)
        == "https://exemplo.vercel.app"
    )


def test_cli_nao_recebe_segredos_do_banco_ou_github(monkeypatch):
    monkeypatch.setattr(h.shutil, "which", lambda _: "vercel")
    monkeypatch.setenv("HOMOLOGACAO_DATABASE_URL_UNPOOLED", "valor-ficticio")
    monkeypatch.setenv("GH_TOKEN", "valor-ficticio")
    monkeypatch.setenv("DATABASE_URL", "valor-ficticio")
    ambiente = h.Vercel("token-ficticio").ambiente({"accountId": "org", "id": "projeto"})
    assert not {"GH_TOKEN", "HOMOLOGACAO_DATABASE_URL_UNPOOLED", "DATABASE_URL"} & ambiente.keys()
    assert ambiente["VERCEL_PROJECT_ID"] == "projeto"


def test_ruleset_adiciona_checks_sem_enfraquecer_revisao_e_e_idempotente():
    atual = {
        "name": "Proteção da main",
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "bypass_actors": [],
        "rules": [
            {"type": "pull_request", "parameters": {"required_approving_review_count": 1}},
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": False,
                    "required_status_checks": [{"context": "backend"}],
                },
            },
        ],
    }
    antes = deepcopy(atual)
    novo = completar_ruleset(atual)
    assert atual == antes
    assert novo["rules"][0] == antes["rules"][0]
    assert novo["rules"][1]["parameters"]["required_status_checks"] == [
        {"context": "backend"},
        {"context": "Vercel – gamekeys-api"},
        {"context": "Vercel – gamekeys-web"},
    ]
    assert completar_ruleset(novo) == novo


def test_main_sem_segredos_falha_fechado_com_relatorio(monkeypatch, tmp_path):
    monkeypatch.setattr(h, "RAIZ", tmp_path)
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.delenv("VERCEL_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    assert h.main() == 1
    relatorio = json.loads(
        (tmp_path / "backend/relatorios/homologacao.json").read_text(encoding="utf-8")
    )
    assert relatorio["resultado"] == "bloqueado"
    assert "segredos" in relatorio["motivo"]


@pytest.mark.parametrize("admin", [False, True])
def test_ativacao_exige_admin_preserva_regras_e_envia_segredos_por_stdin(
    monkeypatch, capsys, admin
):
    monkeypatch.setattr(
        configurar.argparse.ArgumentParser, "parse_args", lambda _: SimpleNamespace(aplicar=True)
    )
    atual = {
        "name": "Proteção da main",
        "target": "branch",
        "enforcement": "active",
        "rules": [
            {
                "type": "required_status_checks",
                "parameters": {"required_status_checks": [{"context": "backend"}]},
            }
        ],
    }
    mutacoes = []

    def api(caminho, metodo="GET", corpo=None):
        nonlocal atual
        if caminho == "":
            return {"permissions": {"admin": admin}, "id": 123}
        if caminho == "/rulesets":
            return [{"id": 1, "name": "Proteção da main"}]
        if metodo == "PUT":
            mutacoes.append("ruleset")
            atual = corpo
        return atual

    monkeypatch.setattr(configurar, "api", api)
    valores = iter(["TOKEN_FICTICIO_GK136", "URL_FICTICIA_GK136"])

    def senha(_):
        assert admin
        return next(valores)

    monkeypatch.setattr(configurar, "getpass", senha)
    monkeypatch.setattr(configurar, "conferir_migracoes", lambda _: [])
    monkeypatch.setattr(
        configurar,
        "json_api",
        lambda _, caminho, token: {
            "name": "gamekeys-api" if "gamekeys-api?" in caminho else "gamekeys-web",
            "link": {"repoId": 123},
        },
    )

    def cli(*args, entrada=None):
        assert "TOKEN_FICTICIO_GK136" not in args
        assert "URL_FICTICIA_GK136" not in args
        mutacoes.append((args, entrada))
        return ""

    monkeypatch.setattr(configurar, "gh", cli)
    assert configurar.main() == (0 if admin else 1)
    saida = capsys.readouterr().out
    assert "TOKEN_FICTICIO_GK136" not in saida
    assert "URL_FICTICIA_GK136" not in saida
    assert len(mutacoes) == (3 if admin else 0)
