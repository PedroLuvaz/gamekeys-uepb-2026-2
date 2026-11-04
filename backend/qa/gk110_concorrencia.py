"""Experimento reproduzível da GK-110 em PostgreSQL local real.

O experimento usa o schema isolado ``qa_gk110``. Ele não implementa o checkout nem a
reserva definitiva da aplicação: esses fluxos pertencem às GK-15/GK-46. A proteção da URL
recusa qualquer host remoto e qualquer banco diferente de ``gamekeys_teste`` antes do DDL.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Barrier

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg_pool import ConnectionPool

HOSTS_LOCAIS = {"localhost", "127.0.0.1", "::1"}
SCHEMA = "qa_gk110"


class BancoDeTesteInseguro(ValueError):
    """A URL não aponta para o PostgreSQL local isolado autorizado."""


class FalhaReservaExperimental(RuntimeError):
    """Falha proposital usada para comprovar o rollback da transação."""


@dataclass(frozen=True)
class ResultadoReserva:
    status: str
    pedido_id: int
    chave_id: int | None
    isolamento: str


def validar_url_local(url: str) -> str:
    """Aceita somente ``gamekeys_teste`` em loopback, sem abrir conexão."""
    __tracebackhide__ = True
    try:
        parametros = conninfo_to_dict(url)
    except (psycopg.Error, ValueError) as erro:
        raise BancoDeTesteInseguro("TEST_DATABASE_URL não é uma URL PostgreSQL válida") from erro

    banco = parametros.get("dbname")
    host = (parametros.get("host") or "").lower()
    hostaddr = (parametros.get("hostaddr") or "").lower()
    if banco != "gamekeys_teste":
        raise BancoDeTesteInseguro("o banco deve ser exatamente gamekeys_teste")
    if host not in HOSTS_LOCAIS or (hostaddr and hostaddr not in HOSTS_LOCAIS):
        raise BancoDeTesteInseguro("somente PostgreSQL local em loopback é permitido")
    return url


def criar_estrutura(url: str) -> None:
    """Recria apenas o schema descartável do experimento."""
    url = validar_url_local(url)
    with psycopg.connect(url, autocommit=True) as conexao:
        conexao.execute(f"drop schema if exists {SCHEMA} cascade")
        conexao.execute(f"create schema {SCHEMA}")
        conexao.execute(
            f"""
            create table {SCHEMA}.jogos (
                id bigint generated always as identity primary key,
                nome text not null
            );
            create table {SCHEMA}.chaves (
                id bigint generated always as identity primary key,
                jogo_id bigint not null references {SCHEMA}.jogos(id),
                estado text not null default 'disponivel'
                    check (estado in ('disponivel', 'reservada'))
            );
            create table {SCHEMA}.pedidos (
                id bigint primary key,
                cliente_id bigint not null
            );
            create table {SCHEMA}.itens_pedido (
                pedido_id bigint not null references {SCHEMA}.pedidos(id),
                chave_id bigint not null unique references {SCHEMA}.chaves(id),
                primary key (pedido_id, chave_id)
            );
            """
        )


def excluir_estrutura(url: str) -> None:
    """Remove apenas o schema descartável do experimento."""
    url = validar_url_local(url)
    with psycopg.connect(url, autocommit=True) as conexao:
        conexao.execute(f"drop schema if exists {SCHEMA} cascade")


def preparar_ultima_chave(url: str) -> int:
    """Reinicia uma rodada com um jogo e exatamente uma chave disponível."""
    url = validar_url_local(url)
    with psycopg.connect(url) as conexao:
        conexao.execute(
            f"truncate {SCHEMA}.itens_pedido, {SCHEMA}.pedidos, "
            f"{SCHEMA}.chaves, {SCHEMA}.jogos restart identity cascade"
        )
        jogo_id = conexao.execute(
            f"insert into {SCHEMA}.jogos (nome) values (%s) returning id",
            ("Jogo do experimento GK-110",),
        ).fetchone()[0]
        conexao.execute(
            f"insert into {SCHEMA}.chaves (jogo_id) values (%s)",
            (jogo_id,),
        )
    return jogo_id


def reservar_ultima_chave(
    pool: ConnectionPool,
    *,
    jogo_id: int,
    pedido_id: int,
    cliente_id: int,
    barreira: Barrier | None = None,
    ao_bloquear: Callable[[], None] | None = None,
    falhar_apos_reserva: bool = False,
) -> ResultadoReserva:
    """Tenta reservar uma chave em uma transação independente por chamada."""
    with pool.connection() as conexao:
        if barreira is not None:
            barreira.wait(timeout=10)
        with conexao.transaction():
            conexao.execute("set transaction isolation level read committed")
            isolamento = conexao.execute("show transaction_isolation").fetchone()[0]
            linha = conexao.execute(
                f"""
                select id
                  from {SCHEMA}.chaves
                 where jogo_id = %s and estado = 'disponivel'
                 order by id
                 limit 1
                   for update skip locked
                """,
                (jogo_id,),
            ).fetchone()
            if linha is None:
                return ResultadoReserva("esgotado", pedido_id, None, isolamento)

            chave_id = linha[0]
            if ao_bloquear is not None:
                ao_bloquear()
            conexao.execute(
                f"insert into {SCHEMA}.pedidos (id, cliente_id) values (%s, %s)",
                (pedido_id, cliente_id),
            )
            conexao.execute(
                f"update {SCHEMA}.chaves set estado = 'reservada' where id = %s",
                (chave_id,),
            )
            if falhar_apos_reserva:
                raise FalhaReservaExperimental("falha provocada antes do commit")
            conexao.execute(
                f"insert into {SCHEMA}.itens_pedido (pedido_id, chave_id) values (%s, %s)",
                (pedido_id, chave_id),
            )
            return ResultadoReserva("reservada", pedido_id, chave_id, isolamento)


def consultar_integridade(url: str) -> dict[str, int]:
    """Mede pedidos, itens, estoque e eventual duplicidade sem ler códigos de ativação."""
    url = validar_url_local(url)
    with psycopg.connect(url) as conexao:
        pedidos = conexao.execute(f"select count(*) from {SCHEMA}.pedidos").fetchone()[0]
        itens = conexao.execute(f"select count(*) from {SCHEMA}.itens_pedido").fetchone()[0]
        disponiveis = conexao.execute(
            f"select count(*) from {SCHEMA}.chaves where estado = 'disponivel'"
        ).fetchone()[0]
        duplicadas = conexao.execute(
            f"""
            select count(*) from (
                select chave_id
                  from {SCHEMA}.itens_pedido
                 group by chave_id
                having count(*) > 1
            ) as repetidas
            """
        ).fetchone()[0]
    return {
        "pedidos": pedidos,
        "itens_pedido": itens,
        "chaves_disponiveis": disponiveis,
        "chaves_duplicadas": duplicadas,
    }


def executar_estresse(url: str, *, rodadas: int = 100, concorrentes: int = 20) -> dict:
    """Executa 20 tentativas concorrentes da última chave em 100 rodadas por padrão."""
    url = validar_url_local(url)
    if rodadas < 1 or concorrentes < 2:
        raise ValueError("use ao menos 1 rodada e 2 concorrentes")

    inicio = time.perf_counter()
    totais: Counter[str] = Counter()
    falhas: list[dict] = []
    with ConnectionPool(
        url,
        min_size=concorrentes,
        max_size=concorrentes,
        timeout=15,
        kwargs={"prepare_threshold": None},
        open=True,
    ) as pool:
        pool.wait(timeout=30)
        for rodada in range(1, rodadas + 1):
            jogo_id = preparar_ultima_chave(url)
            barreira = Barrier(concorrentes)
            with ThreadPoolExecutor(max_workers=concorrentes) as executor:
                futuros = [
                    executor.submit(
                        reservar_ultima_chave,
                        pool,
                        jogo_id=jogo_id,
                        pedido_id=rodada * 10_000 + indice,
                        cliente_id=indice,
                        barreira=barreira,
                    )
                    for indice in range(1, concorrentes + 1)
                ]
                resultados = [futuro.result(timeout=30) for futuro in futuros]

            contagem = Counter(resultado.status for resultado in resultados)
            integridade = consultar_integridade(url)
            totais.update(contagem)
            if contagem != {"reservada": 1, "esgotado": concorrentes - 1} or integridade != {
                "pedidos": 1,
                "itens_pedido": 1,
                "chaves_disponiveis": 0,
                "chaves_duplicadas": 0,
            }:
                falhas.append(
                    {
                        "rodada": rodada,
                        "resultados": dict(contagem),
                        "integridade": integridade,
                    }
                )

    return {
        "experimento": "GK-110/GK-116",
        "executado_em_utc": datetime.now(UTC).isoformat(),
        "banco": "gamekeys_teste local",
        "isolamento": "read committed",
        "rodadas": rodadas,
        "concorrentes_por_rodada": concorrentes,
        "tentativas": rodadas * concorrentes,
        "resultados": dict(totais),
        "rodadas_com_falha": len(falhas),
        "falhas": falhas,
        "duracao_segundos": round(time.perf_counter() - inicio, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rodadas", type=int, default=100)
    parser.add_argument("--concorrentes", type=int, default=20)
    args = parser.parse_args()
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        parser.error("defina TEST_DATABASE_URL para o gamekeys_teste local")

    criar_estrutura(url)
    relatorio = executar_estresse(
        url,
        rodadas=args.rodadas,
        concorrentes=args.concorrentes,
    )
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return 1 if relatorio["rodadas_com_falha"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
