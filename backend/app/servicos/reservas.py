"""GK-124: reserva integral do carrinho autenticado, com repetição segura."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from psycopg import Connection
from psycopg.pq import TransactionStatus
from psycopg.rows import dict_row

from app.db import obter_pool
from app.esquemas.clientes import ClienteCadastrado
from app.esquemas.reservas import ItemReservado, PedidoReservado
from app.servicos.carrinho import (
    ClassificacaoNaoPermitida,
    ClienteNaoPermitido,
    EstoqueInsuficiente,
    JogoNaoEncontrado,
    bloquear_carrinho,
    idade_em_anos,
)
from app.servicos.reserva_chaves import reservar_chaves

MAX_ITENS = 100
MAX_UNIDADES = 1000
MAX_VALOR = Decimal("99999999.99")  # numeric(10,2) do DER v1.0.


class CarrinhoVazio(ValueError):
    """Não há itens para reservar."""


class LimiteDoPedido(ValueError):
    """Trabalho e valor limitados antes de alocar chaves."""


def _consultar_pedido(conexao: Connection, pedido_id: int) -> PedidoReservado:
    pedido = conexao.execute(
        "select status, valor_total from vendas.pedidos where id = %s", (pedido_id,)
    ).fetchone()
    itens = conexao.execute(
        "select jogo_id, count(*), preco_unitario, sum(preco_unitario)"
        " from vendas.itens_pedido where pedido_id = %s"
        " group by jogo_id, preco_unitario order by jogo_id",
        (pedido_id,),
    ).fetchall()
    return PedidoReservado(
        pedido_id=pedido_id,
        status=pedido[0],
        valor_total=pedido[1],
        itens=[
            ItemReservado(jogo_id=j, quantidade=q, preco_unitario=p, subtotal=s)
            for j, q, p, s in itens
        ],
    )


def reservar_na_conexao(
    conexao: Connection, cliente: ClienteCadastrado, chave_idempotencia: UUID
) -> PedidoReservado:
    """Integração futura com GK-14: o chamador fornece a mesma transação ativa.

    A ordem é carrinho do cliente -> jogos por ID -> chaves por ID. Jogos usam
    NO KEY UPDATE para manter preço/estoque estáveis sem bloquear as FKs de outros clientes.
    """
    if cliente.perfil != "cliente":
        raise ClienteNaoPermitido
    if conexao.info.transaction_status != TransactionStatus.INTRANS:
        raise RuntimeError("A reserva exige uma transação externa ativa")
    # Savepoint: um chamador da GK-14 que trate uma recusa não pode efetivar
    # as reservas parciais dos jogos já processados na sua transação externa.
    with conexao.transaction():
        return _reservar_na_transacao(conexao, cliente, chave_idempotencia)


def _reservar_na_transacao(
    conexao: Connection, cliente: ClienteCadastrado, chave_idempotencia: UUID
) -> PedidoReservado:
    conexao.execute("set local lock_timeout = '2s'; set local statement_timeout = '5s'")
    carrinho_id = bloquear_carrinho(conexao, cliente.id)
    anterior = conexao.execute(
        "select id from vendas.pedidos where usuario_id = %s and chave_idempotencia = %s",
        (cliente.id, chave_idempotencia),
    ).fetchone()
    if anterior:
        return _consultar_pedido(conexao, anterior[0])
    itens = conexao.execute(
        "select jogo_id, quantidade from vendas.itens_carrinho"
        " where carrinho_id = %s order by jogo_id limit %s",
        (carrinho_id, MAX_ITENS + 1),
    ).fetchall()
    if not itens:
        raise CarrinhoVazio
    if len(itens) > MAX_ITENS or sum(q for _, q in itens) > MAX_UNIDADES:
        raise LimiteDoPedido
    with conexao.cursor(row_factory=dict_row) as cursor:
        jogos = cursor.execute(
            "select id, ativo, preco, classificacao, chaves_disponiveis"
            " from catalogo.jogos where id = any(%s) order by id for no key update",
            ([j for j, _ in itens],),
        ).fetchall()
    if len(jogos) != len(itens) or any(not jogo["ativo"] for jogo in jogos):
        raise JogoNaoEncontrado
    idade = idade_em_anos(cliente.data_nascimento, datetime.now(UTC).date())
    total = Decimal("0.00")
    for jogo, (_, quantidade) in zip(jogos, itens, strict=True):
        minima = 0 if jogo["classificacao"] == "L" else int(jogo["classificacao"])
        if idade < minima:
            raise ClassificacaoNaoPermitida
        if quantidade > jogo["chaves_disponiveis"]:
            raise EstoqueInsuficiente
        total += jogo["preco"] * quantidade
    if total > MAX_VALOR:
        raise LimiteDoPedido
    pedido_id = conexao.execute(
        "insert into vendas.pedidos (usuario_id, chave_idempotencia, valor_total)"
        " values (%s, %s, %s) returning id",
        (cliente.id, chave_idempotencia, total),
    ).fetchone()[0]
    for jogo, (_, quantidade) in zip(jogos, itens, strict=True):
        ids = reservar_chaves(conexao, jogo["id"], quantidade)
        conexao.execute(
            "insert into vendas.itens_pedido (pedido_id, jogo_id, chave_id, preco_unitario)"
            " select %s, %s, chave, %s from unnest(%s::bigint[]) as chave",
            (pedido_id, jogo["id"], jogo["preco"], ids),
        )
    conexao.execute("delete from vendas.itens_carrinho where carrinho_id = %s", (carrinho_id,))
    return _consultar_pedido(conexao, pedido_id)


def reservar_carrinho(cliente: ClienteCadastrado, chave_idempotencia: UUID) -> PedidoReservado:
    if cliente.perfil != "cliente":
        raise ClienteNaoPermitido
    with obter_pool().connection() as conexao, conexao.transaction():
        return reservar_na_conexao(conexao, cliente, chave_idempotencia)
