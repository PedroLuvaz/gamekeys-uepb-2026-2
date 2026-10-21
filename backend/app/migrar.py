"""Aplica as migrações de `migracoes/` e, com --carga, a carga de demonstração.

Uso (a partir de backend/):
    python -m app.migrar            # só a estrutura
    python -m app.migrar --carga    # estrutura + jogos de demonstração

Usa DATABASE_URL_UNPOOLED (conexão direta, sem PgBouncer), como o Neon recomenda para
migrações. Sem ela, cai para DATABASE_URL.
"""

import argparse
import os
import sys
from pathlib import Path

import psycopg

from app.db import RAIZ_DO_REPO  # noqa: F401  (carrega o .env.local)

PASTA_BACKEND = Path(__file__).resolve().parents[1]
PASTA_MIGRACOES = PASTA_BACKEND / "migracoes"
ARQUIVO_CARGA = PASTA_BACKEND / "carga" / "demonstracao.sql"


def url_de_migracao() -> str:
    url = os.getenv("DATABASE_URL_UNPOOLED") or os.getenv("DATABASE_URL")
    if not url:
        sys.exit("Defina DATABASE_URL_UNPOOLED (ou DATABASE_URL) no .env.local")
    return url


def aplicar_migracoes(conexao: psycopg.Connection) -> list[str]:
    conexao.execute(
        "create table if not exists public.migracoes_aplicadas ("
        " nome text primary key, aplicada_em timestamptz not null default now())"
    )
    conexao.commit()
    feitas = {nome for (nome,) in conexao.execute("select nome from public.migracoes_aplicadas")}
    aplicadas = []
    for arquivo in sorted(PASTA_MIGRACOES.glob("*.sql")):
        if arquivo.name in feitas:
            continue
        with conexao.transaction():
            conexao.execute(arquivo.read_text(encoding="utf-8"))
            conexao.execute(
                "insert into public.migracoes_aplicadas (nome) values (%s)", (arquivo.name,)
            )
        aplicadas.append(arquivo.name)
    return aplicadas


def aplicar_carga(conexao: psycopg.Connection) -> None:
    with conexao.transaction():
        conexao.execute(ARQUIVO_CARGA.read_text(encoding="utf-8"))


def migrar(url: str, carga: bool = False) -> list[str]:
    with psycopg.connect(url) as conexao:
        aplicadas = aplicar_migracoes(conexao)
        if carga:
            aplicar_carga(conexao)
    return aplicadas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--carga", action="store_true", help="aplica a carga de demonstração")
    args = parser.parse_args()

    aplicadas = migrar(url_de_migracao(), carga=args.carga)
    print("Migrações aplicadas:", ", ".join(aplicadas) if aplicadas else "nenhuma (já em dia)")
    if args.carga:
        print("Carga de demonstração aplicada.")


if __name__ == "__main__":
    main()
