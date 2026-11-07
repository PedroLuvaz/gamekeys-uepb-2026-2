"""Operações atômicas do carrinho (GK-11/GK-12). Não reserva chaves."""

from datetime import UTC, date, datetime
from decimal import Decimal

from psycopg import Connection
from psycopg.rows import dict_row

from app.db import obter_pool
from app.esquemas.carrinho import (
    AdicaoAoCarrinho,
    AlteracaoQuantidade,
    CarrinhoConsultado,
    ItemDoCarrinho,
    ItemListadoNoCarrinho,
)
from app.esquemas.clientes import ClienteCadastrado


class ClienteNaoPermitido(ValueError):
    """A operação é exclusiva de contas de cliente."""


class JogoNaoEncontrado(ValueError):
    """Não distinguir jogo inativo de identificador inexistente."""


class EstoqueInsuficiente(ValueError):
    """A quantidade final do item ultrapassaria o estoque atual."""


class ClassificacaoNaoPermitida(ValueError):
    """O cliente ainda não completou a idade mínima do jogo."""


class ItemCarrinhoNaoEncontrado(ValueError):
    """O jogo não pertence ao carrinho do cliente autenticado."""


def idade_em_anos(nascimento: date, hoje: date) -> int:
    """Idade completa; nascidos em 29/02 completam anos em 01/03 nos anos não bissextos."""
    return (
        hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    )


def bloquear_carrinho(conexao: Connection, usuario_id: int) -> int:
    """Cria/obtém e bloqueia só o carrinho do cliente, até a transação externa terminar.

    GK-12 e GK-15 devem usar a mesma ordem: carrinho, jogos (por id), chaves.
    O conflito no índice único protege também a primeira criação concorrente.
    """
    with conexao.cursor(row_factory=dict_row) as cursor:
        return cursor.execute(
            "insert into vendas.carrinhos (usuario_id) values (%s)"
            " on conflict (usuario_id) do update set atualizado_em = now()"
            " returning id",
            (usuario_id,),
        ).fetchone()["id"]


def _validar_cliente(cliente: ClienteCadastrado) -> None:
    if cliente.perfil != "cliente":
        raise ClienteNaoPermitido


def _configurar_transacao(conexao: Connection) -> None:
    # Limites locais, compatíveis com PgBouncer em modo transação.
    conexao.execute("set local lock_timeout = '2s'; set local statement_timeout = '5s'")


def _consultar_na_conexao(conexao: Connection, usuario_id: int) -> CarrinhoConsultado:
    """Busca todo o carrinho em uma query, sem N+1 e sem criar carrinho vazio."""
    with conexao.cursor(row_factory=dict_row) as cursor:
        linhas = cursor.execute(
            "select j.id as jogo_id, j.slug, j.nome, j.capa_url,"
            " i.quantidade, j.chaves_disponiveis as estoque_disponivel, j.preco"
            " from vendas.carrinhos c"
            " join vendas.itens_carrinho i on i.carrinho_id = c.id"
            " join catalogo.jogos j on j.id = i.jogo_id"
            " where c.usuario_id = %s order by i.adicionado_em, j.id",
            (usuario_id,),
        ).fetchall()

    itens = [
        ItemListadoNoCarrinho(
            jogo_id=linha["jogo_id"],
            slug=linha["slug"],
            nome=linha["nome"],
            capa_url=linha["capa_url"],
            quantidade=linha["quantidade"],
            estoque_disponivel=linha["estoque_disponivel"],
            preco_unitario=linha["preco"],
            subtotal=linha["preco"] * linha["quantidade"],
        )
        for linha in linhas
    ]
    total = sum((item.subtotal for item in itens), start=Decimal("0.00"))
    return CarrinhoConsultado(itens=itens, total=total)


def consultar_carrinho(cliente: ClienteCadastrado) -> CarrinhoConsultado:
    _validar_cliente(cliente)
    with obter_pool().connection() as conexao:
        return _consultar_na_conexao(conexao, cliente.id)


def adicionar_item(cliente: ClienteCadastrado, dados: AdicaoAoCarrinho) -> ItemDoCarrinho:
    _validar_cliente(cliente)

    with obter_pool().connection() as conexao, conexao.transaction():
        # Uma disputa não ocupa o pool indefinidamente. Nenhuma retentativa automática de POST.
        _configurar_transacao(conexao)
        carrinho_id = bloquear_carrinho(conexao, cliente.id)
        with conexao.cursor(row_factory=dict_row) as cursor:
            jogo = cursor.execute(
                "select id, nome, preco, classificacao, chaves_disponiveis"
                " from catalogo.jogos where id = %s and ativo for share",
                (dados.jogo_id,),
            ).fetchone()
            if jogo is None:
                raise JogoNaoEncontrado
            idade_minima = 0 if jogo["classificacao"] == "L" else int(jogo["classificacao"])
            if idade_em_anos(cliente.data_nascimento, datetime.now(UTC).date()) < idade_minima:
                raise ClassificacaoNaoPermitida
            if dados.quantidade > jogo["chaves_disponiveis"]:
                raise EstoqueInsuficiente

            # A PK impede linhas duplicadas; a guarda verifica a quantidade acumulada.
            # Cast para bigint evita overflow antes da comparação com o estoque integer.
            item = cursor.execute(
                "insert into vendas.itens_carrinho (carrinho_id, jogo_id, quantidade)"
                " values (%s, %s, %s)"
                " on conflict (carrinho_id, jogo_id) do update"
                " set quantidade = vendas.itens_carrinho.quantidade + excluded.quantidade"
                " where vendas.itens_carrinho.quantidade::bigint + excluded.quantidade <= %s"
                " returning quantidade",
                (carrinho_id, jogo["id"], dados.quantidade, jogo["chaves_disponiveis"]),
            ).fetchone()
            if item is None:
                raise EstoqueInsuficiente

            return ItemDoCarrinho(
                carrinho_id=carrinho_id,
                jogo_id=jogo["id"],
                nome=jogo["nome"],
                quantidade=item["quantidade"],
                preco_unitario=jogo["preco"],
                subtotal=jogo["preco"] * item["quantidade"],
            )


def alterar_quantidade(
    cliente: ClienteCadastrado, jogo_id: int, dados: AlteracaoQuantidade
) -> CarrinhoConsultado:
    """Substitui a quantidade, serializando mudanças do mesmo carrinho."""
    _validar_cliente(cliente)
    with obter_pool().connection() as conexao, conexao.transaction():
        _configurar_transacao(conexao)
        carrinho_id = bloquear_carrinho(conexao, cliente.id)
        with conexao.cursor(row_factory=dict_row) as cursor:
            # Ordem de bloqueios: carrinho e depois jogo por ID. GK-15 acrescentará chaves.
            jogo = cursor.execute(
                "select id, chaves_disponiveis from catalogo.jogos"
                " where id = %s and ativo for share",
                (jogo_id,),
            ).fetchone()
            if jogo is None:
                raise ItemCarrinhoNaoEncontrado
            if dados.quantidade > jogo["chaves_disponiveis"]:
                raise EstoqueInsuficiente
            item = cursor.execute(
                "update vendas.itens_carrinho set quantidade = %s"
                " where carrinho_id = %s and jogo_id = %s returning jogo_id",
                (dados.quantidade, carrinho_id, jogo_id),
            ).fetchone()
            if item is None:
                raise ItemCarrinhoNaoEncontrado
        return _consultar_na_conexao(conexao, cliente.id)


def remover_item(cliente: ClienteCadastrado, jogo_id: int) -> CarrinhoConsultado:
    """Remove somente o item do carrinho pertencente ao cliente autenticado."""
    _validar_cliente(cliente)
    with obter_pool().connection() as conexao, conexao.transaction():
        _configurar_transacao(conexao)
        carrinho_id = bloquear_carrinho(conexao, cliente.id)
        removido = conexao.execute(
            "delete from vendas.itens_carrinho"
            " where carrinho_id = %s and jogo_id = %s returning jogo_id",
            (carrinho_id, jogo_id),
        ).fetchone()
        if removido is None:
            raise ItemCarrinhoNaoEncontrado
        return _consultar_na_conexao(conexao, cliente.id)
