"""GK-16: pagamento simulado e entrega das chaves reservadas na GK-15."""

from decimal import Decimal

from psycopg import Connection

from app.db import obter_pool
from app.esquemas.clientes import ClienteCadastrado
from app.esquemas.pedidos import ChaveEntregue, PedidoDetalhado
from app.esquemas.reservas import ItemReservado
from app.servicos.carrinho import ClienteNaoPermitido


class PedidoNaoEncontrado(LookupError):
    """O pedido não existe ou pertence a outro cliente."""


class PedidoNaoPagavel(ValueError):
    """O pedido não está aguardando pagamento (ex.: cancelado)."""


def _detalhar(
    conexao: Connection, pedido_id: int, status: str, valor_total: Decimal
) -> PedidoDetalhado:
    itens = conexao.execute(
        "select jogo_id, count(*), preco_unitario, sum(preco_unitario)"
        " from vendas.itens_pedido where pedido_id = %s"
        " group by jogo_id, preco_unitario order by jogo_id",
        (pedido_id,),
    ).fetchall()
    chaves = []
    # O código só é lido do banco depois da entrega: antes disso nem entra na memória da API.
    if status == "entregue":
        chaves = conexao.execute(
            "select i.jogo_id, j.nome, c.codigo from vendas.itens_pedido i"
            " join catalogo.chaves c on c.id = i.chave_id"
            " join catalogo.jogos j on j.id = i.jogo_id"
            " where i.pedido_id = %s order by i.jogo_id, i.id",
            (pedido_id,),
        ).fetchall()
    return PedidoDetalhado(
        pedido_id=pedido_id,
        status=status,
        valor_total=valor_total,
        itens=[
            ItemReservado(jogo_id=j, quantidade=q, preco_unitario=p, subtotal=s)
            for j, q, p, s in itens
        ],
        chaves=[ChaveEntregue(jogo_id=j, nome=n, codigo=c) for j, n, c in chaves],
    )


def consultar_pedido(cliente: ClienteCadastrado, pedido_id: int) -> PedidoDetalhado:
    if cliente.perfil != "cliente":
        raise ClienteNaoPermitido
    with obter_pool().connection() as conexao, conexao.transaction():
        pedido = conexao.execute(
            "select status, valor_total from vendas.pedidos where id = %s and usuario_id = %s",
            (pedido_id, cliente.id),
        ).fetchone()
        if not pedido:
            raise PedidoNaoEncontrado
        return _detalhar(conexao, pedido_id, pedido[0], pedido[1])


def pagar_pedido(cliente: ClienteCadastrado, pedido_id: int, metodo: str) -> PedidoDetalhado:
    """Aprova o pagamento simulado e entrega as chaves na mesma transação.

    O bloqueio da linha do pedido serializa dois cliques simultâneos: o segundo encontra o
    pedido já entregue e recebe o mesmo resultado, sem segundo pagamento. Qualquer falha
    desfaz pagamento, status do pedido e estado das chaves.
    """
    if cliente.perfil != "cliente":
        raise ClienteNaoPermitido
    with obter_pool().connection() as conexao, conexao.transaction():
        conexao.execute("set local lock_timeout = '2s'; set local statement_timeout = '5s'")
        pedido = conexao.execute(
            "select status, valor_total from vendas.pedidos"
            " where id = %s and usuario_id = %s for update",
            (pedido_id, cliente.id),
        ).fetchone()
        if not pedido:
            raise PedidoNaoEncontrado
        status, valor_total = pedido
        if status == "entregue":
            return _detalhar(conexao, pedido_id, status, valor_total)
        if status != "aguardando_pagamento":
            raise PedidoNaoPagavel
        conexao.execute(
            "insert into vendas.pagamentos (pedido_id, metodo, status, valor)"
            " values (%s, %s, 'aprovado', %s)",
            (pedido_id, metodo, valor_total),
        )
        vendidas = conexao.execute(
            "update catalogo.chaves set status = 'vendida' where status = 'reservada'"
            " and id in (select chave_id from vendas.itens_pedido where pedido_id = %s)",
            (pedido_id,),
        ).rowcount
        esperadas = conexao.execute(
            "select count(*) from vendas.itens_pedido where pedido_id = %s", (pedido_id,)
        ).fetchone()[0]
        if vendidas != esperadas:
            # Chave do pedido fora do estado "reservada": não entregar nada pela metade.
            raise RuntimeError("Chaves do pedido em estado inconsistente")
        conexao.execute(
            "update vendas.pedidos set status = 'entregue', pago_em = now(), entregue_em = now()"
            " where id = %s",
            (pedido_id,),
        )
        return _detalhar(conexao, pedido_id, "entregue", valor_total)
