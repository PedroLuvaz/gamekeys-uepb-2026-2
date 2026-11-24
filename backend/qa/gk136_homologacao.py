"""GK-136: publica o commit aprovado da main, com bloqueios e relatório sem segredos.

Não aplica migrações. A conexão de homologação é usada só em transação READ ONLY.
O CLI oficial do Vercel prepara builds de produção sem promover seus domínios.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

import psycopg

from app.conexao import ConexaoPostgres, parametros_conexao
from app.migrar import PASTA_MIGRACOES

REPOSITORIO = "PedroLuvaz/gamekeys-uepb-2026-2"
ESCOPO = "pedro-andrades-projects-abe06b11"
RAIZ = Path(__file__).resolve().parents[2]
PROJETOS = ("gamekeys-api", "gamekeys-web")


class PublicacaoBloqueada(RuntimeError):
    """Só mensagens fixas e identificadores públicos podem sair deste módulo."""

    def __init__(self, mensagem: str, diagnostico: dict | None = None):
        super().__init__(mensagem)
        self.diagnostico = diagnostico


class SemRedirecionamento(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def json_api(host: str, caminho: str, token: str, metodo="GET", corpo=None):
    """A origem é fixa; nem erros nem redirecionamentos podem repassar o token."""
    if host not in {"api.github.com", "api.vercel.com"} or not caminho.startswith("/"):
        raise PublicacaoBloqueada("Origem de API não permitida.")
    dados = None if corpo is None else json.dumps(corpo).encode()
    pedido = Request(
        "https://" + host + caminho,
        data=dados,
        method=metodo,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    try:
        with build_opener(SemRedirecionamento).open(pedido, timeout=30) as resposta:
            conteudo = resposta.read()
            return json.loads(conteudo) if conteudo else {}
    except (HTTPError, URLError, TimeoutError, ValueError):
        raise PublicacaoBloqueada("Não foi possível confirmar a operação na API externa.") from None


def confirmar_ci(github, run_id: str | None = None) -> tuple[str, str]:
    if run_id:
        if not re.fullmatch(r"[0-9]+", run_id):
            raise PublicacaoBloqueada("Identificador de CI inválido.")
        run = github(f"/actions/runs/{run_id}")
    else:
        runs = github("/actions/workflows/ci.yml/runs?branch=main&event=push&per_page=1")
        if not runs.get("workflow_runs"):
            raise PublicacaoBloqueada("Nenhum CI da main disponível.")
        run = runs["workflow_runs"][0]
    sha = run.get("head_sha", "")
    if (
        not re.fullmatch(r"[0-9a-f]{40}", sha)
        or run.get("head_branch") != "main"
        or run.get("head_repository", {}).get("full_name") != REPOSITORIO
        or run.get("event") != "push"
        or run.get("path") != ".github/workflows/ci.yml"
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
    ):
        raise PublicacaoBloqueada("Publicação exige CI concluído e aprovado de push na main.")
    confirmar_main(github, sha)
    return sha, str(run["id"])


def confirmar_main(github, sha: str) -> None:
    if github("/git/ref/heads/main")["object"]["sha"] != sha:
        raise PublicacaoBloqueada("A main avançou; aguarde o CI do commit mais recente.")


def conferir_migracoes(url: str, pasta: Path = PASTA_MIGRACOES) -> list[str]:
    __tracebackhide__ = True
    try:
        parametros = parametros_conexao(url)
        if parametros.get("dbname") != "gamekeys":
            raise PublicacaoBloqueada("Homologação deve usar o banco gamekeys.")
        if "-pooler" in parametros.get("host", ""):
            raise PublicacaoBloqueada("A verificação de migrações exige conexão direta.")
        local = parametros.get("host") in {"localhost", "127.0.0.1", "::1"}
        if not local and parametros.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            raise PublicacaoBloqueada("A conexão remota de homologação exige TLS.")
        esperadas = {p.name for p in pasta.glob("*.sql")}
        if not esperadas:
            raise PublicacaoBloqueada("Manifesto de migrações ausente.")
        with ConexaoPostgres.connect(url, connect_timeout=5) as conexao:
            conexao.execute("set transaction read only")
            conexao.execute("set local statement_timeout = '5s'")
            privilegiada = conexao.execute(
                "select r.rolsuper or r.rolcreatedb or r.rolcreaterole or r.oid=d.datdba"
                " from pg_roles r cross join pg_database d"
                " where r.rolname=current_user and d.datname=current_database()"
            ).fetchone()
            if not privilegiada or privilegiada[0]:
                raise PublicacaoBloqueada("Use conta de leitura sem privilégios administrativos.")
            aplicadas = {
                nome for (nome,) in conexao.execute("select nome from public.migracoes_aplicadas")
            }
        if aplicadas != esperadas:
            raise PublicacaoBloqueada(
                "Migrações divergentes: aplique e confira as migrações antes de republicar."
            )
        return sorted(esperadas)
    except (psycopg.Error, ValueError):
        raise PublicacaoBloqueada(
            "Não foi possível conferir as migrações; nenhuma publicação autorizada."
        ) from None


class Vercel:
    def __init__(self, token: str):
        self.token = token
        self.cli = shutil.which("vercel")
        if not self.cli:
            raise PublicacaoBloqueada("CLI do Vercel não instalado.")

    def api(self, caminho, metodo="GET"):
        separador = "&" if "?" in caminho else "?"
        return json_api(
            "api.vercel.com", caminho + separador + urlencode({"slug": ESCOPO}), self.token, metodo
        )

    def projeto(self, nome):
        return self.api("/v9/projects/" + nome)

    def ambiente(self, projeto):
        # O CLI não precisa receber credenciais do banco nem do GitHub.
        remover = {
            "GH_TOKEN",
            "GITHUB_TOKEN",
            "HOMOLOGACAO_DATABASE_URL_UNPOOLED",
            "DATABASE_URL",
            "DATABASE_URL_UNPOOLED",
            "TEST_DATABASE_URL",
            "JWT_SECRET",
            "PGPASSWORD",
        }
        ambiente = {k: v for k, v in os.environ.items() if k not in remover}
        ambiente.update(
            VERCEL_ORG_ID=projeto["accountId"],
            VERCEL_PROJECT_ID=projeto["id"],
            VERCEL_TELEMETRY_DISABLED="1",
            NO_COLOR="1",
            # O token vai pelo ambiente: o `vercel curl` repassa ao curl opções que não
            # reconhece, e `--token` antes de `--` chegaria ao curl com o valor do token.
            VERCEL_TOKEN=self.token,
        )
        return ambiente

    def comando(self, projeto, *args, timeout=600):
        ambiente = self.ambiente(projeto)
        try:
            resultado = subprocess.run(
                [self.cli, *args, "--scope", ESCOPO],
                cwd=RAIZ,
                env=ambiente,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise PublicacaoBloqueada("A operação do Vercel não foi confirmada no prazo.") from None
        if resultado.returncode:
            # Não reproduzir o log bruto do build, que pode conter variáveis protegidas.
            raise PublicacaoBloqueada("Falha na operação do Vercel; confira o painel protegido.")
        return resultado.stdout.strip()

    def preparar(self, projeto, sha):
        saida = self.comando(
            projeto,
            "deploy",
            "--prod",
            "--skip-domain",
            "--yes",
            "--env",
            "GAMEKEYS_COMMIT=" + sha,
            "--build-env",
            "GAMEKEYS_COMMIT=" + sha,
            "--meta",
            "gamekeysCommit=" + sha,
        )
        url = saida.splitlines()[-1] if saida else ""
        if not re.fullmatch(r"https://[a-zA-Z0-9-]+\.vercel\.app", url):
            raise PublicacaoBloqueada("O Vercel não retornou um endereço de build válido.")
        return url

    def consultar(self, projeto, url, caminho):
        if caminho not in {"/saude/versao", "/saude/banco", "/versao.json"}:
            raise PublicacaoBloqueada("Caminho de verificação não permitido.")
        if not re.fullmatch(r"https://[a-zA-Z0-9-]+\.vercel\.app", url):
            raise PublicacaoBloqueada("Endereço do build preparado não permitido.")
        diagnostico = {
            "projeto": projeto.get("name")
            if projeto.get("name") in PROJETOS
            else "nao_identificado",
            "caminho": caminho,
            "codigo_cli": None,
            "http": None,
        }
        # O parser de curl do CLI 65.2.0 repassa --token ao curl nativo.
        # Autenticação só via VERCEL_TOKEN; nunca incluir credenciais nos argumentos.
        args = [
            self.cli,
            "curl",
            caminho,
            "--deployment",
            url,
            "--yes",
            "--scope",
            ESCOPO,
            "--",
            "--fail",
            "--silent",
            "--show-error",
            "--max-time",
            "30",
            "--write-out",
            "\n%{http_code}",
        ]
        ambiente = self.ambiente(projeto)
        try:
            r = subprocess.run(
                args,
                cwd=RAIZ,
                env=ambiente,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as erro:
            diagnostico["motivo"] = (
                "timeout" if isinstance(erro, subprocess.TimeoutExpired) else "execucao"
            )
            raise PublicacaoBloqueada(
                "Falha na verificação HTTP do build preparado.", diagnostico
            ) from None
        diagnostico["codigo_cli"] = r.returncode
        corpo, _, codigo = r.stdout.rpartition("\n")
        if re.fullmatch(r"[0-9]{3}", codigo):
            diagnostico["http"] = int(codigo)
        if r.returncode or diagnostico["http"] != 200:
            diagnostico["motivo"] = "http" if diagnostico["http"] else "cli"
            raise PublicacaoBloqueada("Falha na verificação HTTP do build preparado.", diagnostico)
        try:
            return json.loads(corpo)
        except ValueError:
            diagnostico["motivo"] = "json_invalido"
            raise PublicacaoBloqueada(
                "Falha na verificação HTTP do build preparado.", diagnostico
            ) from None

    def promover(self, projeto, url):
        self.comando(projeto, "promote", url, "--yes", "--timeout", "3m", timeout=210)

    def restaurar(self, projeto, deployment_id):
        self.api(f"/v1/projects/{projeto['id']}/rollback/{deployment_id}", "POST")
        for _ in range(30):
            atual = self.projeto(projeto["name"])
            if atual.get("targets", {}).get("production", {}).get("id") == deployment_id:
                return
            time.sleep(2)
        raise PublicacaoBloqueada(
            "Restauração não confirmada; intervenção do responsável necessária."
        )


def verificar_http(url: str, sha: str):
    """Verificação pública usa origens fixas e apenas requisições GET."""
    if url not in {"https://gamekeys-api.vercel.app", "https://gamekeys-web.vercel.app"}:
        raise PublicacaoBloqueada("Endereço de homologação não permitido.")
    caminhos = (
        ("/saude/versao", "/saude/banco")
        if "-api." in url
        else ("/versao.json", "/api/saude/versao", "/api/saude/banco")
    )
    try:
        for caminho in caminhos:
            pedido = Request(url + caminho, headers={"Cache-Control": "no-cache"})
            with build_opener(SemRedirecionamento).open(pedido, timeout=30) as resposta:
                dados = json.load(resposta)
            if caminho.endswith("versao") or caminho.endswith("versao.json"):
                if dados != {"commit": sha}:
                    raise ValueError
            elif dados.get("status") != "ok" or dados.get("banco") != "gamekeys":
                raise ValueError
    except (HTTPError, URLError, TimeoutError, ValueError):
        raise PublicacaoBloqueada(
            "A versão pública ou a conexão com o banco não foi confirmada."
        ) from None


def publicar(sha, github, vercel, verificar_banco, verificar_publico, relatorio):
    relatorio["migracoes"] = verificar_banco()
    anteriores, preparados = {}, {}
    for nome in PROJETOS:
        projeto = vercel.projeto(nome)
        anterior = projeto.get("targets", {}).get("production", {}).get("id")
        if not anterior:
            raise PublicacaoBloqueada("Projeto sem versão anterior disponível para restauração.")
        anteriores[nome] = (projeto, anterior)
    for nome in PROJETOS:
        projeto = anteriores[nome][0]
        url = vercel.preparar(projeto, sha)
        caminho = "/saude/versao" if nome == "gamekeys-api" else "/versao.json"
        if vercel.consultar(projeto, url, caminho) != {"commit": sha}:
            raise PublicacaoBloqueada("O build preparado não corresponde ao commit aprovado.")
        if nome == "gamekeys-api":
            saude = vercel.consultar(projeto, url, "/saude/banco")
            if saude.get("status") != "ok" or saude.get("banco") != "gamekeys":
                raise PublicacaoBloqueada("O build preparado não alcança o banco de homologação.")
        preparados[nome] = url
    # Nada é promovido se a main ou o registro de migrações mudou durante os builds.
    confirmar_main(github, sha)
    verificar_banco()
    tentados = []
    try:
        for nome in PROJETOS:
            tentados.append(nome)
            vercel.promover(anteriores[nome][0], preparados[nome])
        for nome in PROJETOS:
            verificar_publico("https://" + nome + ".vercel.app", sha)
    except Exception:
        relatorio["restauracao"] = {}
        for nome in reversed(tentados):
            try:
                vercel.restaurar(*anteriores[nome])
                relatorio["restauracao"][nome] = "confirmada"
            except Exception:
                relatorio["restauracao"][nome] = "nao_confirmada"
        if "nao_confirmada" in relatorio["restauracao"].values():
            raise PublicacaoBloqueada(
                "Falha de publicação com restauração não confirmada."
            ) from None
        raise PublicacaoBloqueada("Publicação recusada; versões anteriores restauradas.") from None
    relatorio["publicacoes"] = {
        nome: {"url": "https://" + nome + ".vercel.app", "build": preparados[nome]}
        for nome in PROJETOS
    }


def main():
    relatorio = {"data": datetime.now(UTC).isoformat(), "card": "GK-136", "resultado": "bloqueado"}
    try:
        if os.getenv("GITHUB_REF") != "refs/heads/main":
            raise PublicacaoBloqueada("Publicação permitida somente a partir da main.")
        valores = [
            os.getenv(k) for k in ("GH_TOKEN", "VERCEL_TOKEN", "HOMOLOGACAO_DATABASE_URL_UNPOOLED")
        ]
        if not all(valores):
            raise PublicacaoBloqueada("Configure os segredos de homologação antes de publicar.")
        github_token, vercel_token, url_banco = valores

        def github(caminho):
            return json_api("api.github.com", "/repos/" + REPOSITORIO + caminho, github_token)

        sha, run_id = confirmar_ci(github, os.getenv("CI_RUN_ID") or None)
        local = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True, capture_output=True, check=True
        ).stdout.strip()
        if local != sha:
            raise PublicacaoBloqueada("O checkout não corresponde ao CI aprovado.")
        relatorio.update(
            commit=sha, ci="https://github.com/" + REPOSITORIO + "/actions/runs/" + run_id
        )
        publicar(
            sha,
            github,
            Vercel(vercel_token),
            lambda: conferir_migracoes(url_banco),
            verificar_http,
            relatorio,
        )
        relatorio["resultado"] = "aprovado"
    except PublicacaoBloqueada as erro:
        relatorio["motivo"] = str(erro)
        if erro.diagnostico:
            relatorio["verificacao_http"] = erro.diagnostico
    except Exception:
        # Nenhuma exceção imprevista deve imprimir ambiente, argumentos do CLI ou credenciais.
        relatorio["motivo"] = (
            "Falha inesperada; consulte o responsável sem publicar logs sensíveis."
        )
    destino = RAIZ / "backend/relatorios/homologacao.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    texto = (
        "## GK-136 — Homologação\n\n```json\n"
        + json.dumps(relatorio, ensure_ascii=False, indent=2)
        + "\n```\n"
    )
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as arquivo:
            arquivo.write(texto)
    print(texto)
    return 0 if relatorio["resultado"] == "aprovado" else 1


if __name__ == "__main__":
    sys.exit(main())
