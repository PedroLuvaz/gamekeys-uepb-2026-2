"""Transições e histórico de status dos pedidos (GK-13)."""

from psycopg import Connection
from psycopg.pq import TransactionStatus

TRANSICOES_PERMITIDAS = {("aguardando_pagamento", "entregue")}


class TransicaoStatusInvalida(ValueError):
    """A mudança de status não pertence ao fluxo confirmado."""


def _exigir_transacao(conexao: Connection) -> None:
    if conexao.info.transaction_status != TransactionStatus.INTRANS:
        raise RuntimeError("A mudança de status exige uma transação ativa")


def registrar_status_inicial(conexao: Connection, pedido_id: int, responsavel_id: int) -> None:
    _exigir_transacao(conexao)
    inseridos = conexao.execute(
        "insert into vendas.historico_status_pedido"
        " (pedido_id, status_anterior, status_novo, responsavel_id)"
        " select id, null, status, %s from vendas.pedidos where id = %s",
        (responsavel_id, pedido_id),
    ).rowcount
    if inseridos != 1:
        raise RuntimeError("Pedido não encontrado ao registrar o status inicial")


def alterar_status(
    conexao: Connection,
    pedido_id: int,
    status_anterior: str,
    status_novo: str,
    responsavel_id: int,
) -> None:
    _exigir_transacao(conexao)
    if (status_anterior, status_novo) not in TRANSICOES_PERMITIDAS:
        raise TransicaoStatusInvalida
    alterados = conexao.execute(
        "update vendas.pedidos set status = %s where id = %s and status = %s",
        (status_novo, pedido_id, status_anterior),
    ).rowcount
    if alterados != 1:
        raise TransicaoStatusInvalida
    conexao.execute(
        "insert into vendas.historico_status_pedido"
        " (pedido_id, status_anterior, status_novo, responsavel_id)"
        " values (%s, %s, %s, %s)",
        (pedido_id, status_anterior, status_novo, responsavel_id),
    )
