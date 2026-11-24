"""Ativação única da GK-136 pelo administrador, com credenciais lidas sem eco.

python -m qa.gk136_configurar             # diagnóstico sem alterar nada
python -m qa.gk136_configurar --aplicar   # configura segredos e preserva as regras atuais
"""

import argparse
import json
import shutil
import subprocess
from getpass import getpass

from qa.gk136_homologacao import (
    ESCOPO,
    PROJETOS,
    REPOSITORIO,
    PublicacaoBloqueada,
    conferir_migracoes,
    json_api,
)

CHECKS = ("Vercel – gamekeys-api", "Vercel – gamekeys-web")


def completar_ruleset(atual: dict) -> dict:
    # Preserva, inclusive, número de aprovações, bypass e demais restrições.
    copia = json.loads(json.dumps(atual))
    regras = copia["rules"]
    regra = next((r for r in regras if r["type"] == "required_status_checks"), None)
    if regra is None:
        raise PublicacaoBloqueada("Ruleset sem checks obrigatórios; confira com o administrador.")
    checks = regra["parameters"]["required_status_checks"]
    nomes = {r["context"] for r in checks}
    checks.extend({"context": nome} for nome in CHECKS if nome not in nomes)
    return {
        k: copia[k]
        for k in ("name", "target", "enforcement", "bypass_actors", "conditions", "rules")
        if k in copia
    }


def gh(*args, entrada=None):
    cli = shutil.which("gh")
    if not cli:
        raise PublicacaoBloqueada("Instale o GitHub CLI e faça gh auth login com a conta do Pedro.")
    r = subprocess.run([cli, *args], input=entrada, capture_output=True, text=True, check=False)
    if r.returncode:
        raise PublicacaoBloqueada(
            "Operação no GitHub recusada; confira o login e o acesso de administrador."
        )
    return r.stdout


def api(caminho, metodo="GET", corpo=None):
    args = ["api", "repos/" + REPOSITORIO + caminho, "--method", metodo]
    if corpo is not None:
        args += ["--input", "-"]
    return json.loads(gh(*args, entrada=None if corpo is None else json.dumps(corpo)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aplicar", action="store_true")
    opcoes = parser.parse_args()
    try:
        repo = api("")
        regras = api("/rulesets")
        protecao = next((r for r in regras if r["name"] == "Proteção da main"), None)
        if not protecao:
            raise PublicacaoBloqueada("Ruleset Proteção da main não encontrado.")
        caminho = "/rulesets/" + str(protecao["id"])
        atual = api(caminho)
        nomes = [
            c["context"]
            for regra in atual["rules"]
            if regra["type"] == "required_status_checks"
            for c in regra["parameters"]["required_status_checks"]
        ]
        print(
            json.dumps(
                {
                    "administrador": repo["permissions"].get("admin", False),
                    "checks_atuais": nomes,
                    "checks_a_acrescentar": list(CHECKS),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        if not opcoes.aplicar:
            print("Diagnóstico concluído. Nenhuma configuração alterada.")
            return 0
        if not repo["permissions"].get("admin"):
            raise PublicacaoBloqueada(
                "A ativação deve ser executada pelo Pedro, administrador do repositório."
            )
        vercel_token = getpass("Token Vercel do Pedro (entrada oculta): ").strip()
        banco_url = getpass("Conexão DIRETA de homologação gamekeys (entrada oculta): ").strip()
        if not vercel_token or not banco_url:
            raise PublicacaoBloqueada("Credenciais não informadas; ativação interrompida.")
        conferir_migracoes(banco_url)
        for nome in PROJETOS:
            projeto = json_api(
                "api.vercel.com", "/v9/projects/" + nome + "?slug=" + ESCOPO, vercel_token
            )
            if projeto.get("name") != nome or str(projeto.get("link", {}).get("repoId")) != str(
                repo["id"]
            ):
                raise PublicacaoBloqueada(
                    "Projeto do Vercel não corresponde ao repositório esperado."
                )
        # Valores só no stdin do GitHub CLI; não entram em argumentos, arquivos ou prints.
        for nome, valor in (
            ("VERCEL_TOKEN", vercel_token),
            ("HOMOLOGACAO_DATABASE_URL_UNPOOLED", banco_url),
        ):
            gh("secret", "set", nome, "--repo", REPOSITORIO, entrada=valor)
        api(caminho, "PUT", completar_ruleset(atual))
        depois = api(caminho)
        checks = {
            c["context"]
            for r in depois["rules"]
            if r["type"] == "required_status_checks"
            for c in r["parameters"]["required_status_checks"]
        }
        if not set(CHECKS).issubset(checks):
            raise PublicacaoBloqueada(
                "Proteção não confirmada; confira a configuração antes de integrar o PR."
            )
        print("Segredos configurados e checks Vercel obrigatórios. Regras anteriores preservadas.")
        print("Após revisão e CI verde, integrar o PR da GK-136 e conferir o workflow Homologação.")
        return 0
    except PublicacaoBloqueada as erro:
        print(str(erro))
        return 1
    except Exception:
        print("Ativação não confirmada. Confira acessos e configuração sem publicar segredos.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
