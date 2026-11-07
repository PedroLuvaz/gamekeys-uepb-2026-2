"""Adição atômica ao carrinho (GK-118). Não reserva estoque nem cria pedidos."""

from datetime import UTC, date, datetime

from psycopg import Connection
from psycopg.rows import dict_row

from app.db import obter_pool
from app.esquemas.carrinho import AdicaoAoCarrinho, ItemDoCarrinho
from app.esquemas.clientes import ClienteCadastrado


class ClienteNaoPermitido(ValueError):
    """A operação é exclusiva de contas de cliente."""


class JogoNaoEncontrado(ValueError):
    """Não distinguir jogo inativo de identificador inexistente."""


class EstoqueInsuficiente(ValueError):
    """A quantidade final do item ultrapassaria o estoque atual."""


class ClassificacaoNaoPermitida(ValueError):
    """O cliente ainda não completou a idade mínima do jogo."""


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


def adicionar_item(cliente: ClienteCadastrado, dados: AdicaoAoCarrinho) -> ItemDoCarrinho:
    if cliente.perfil != "cliente":
        raise ClienteNaoPermitido

    with obter_pool().connection() as conexao, conexao.transaction():
        # Limites locais à transação, compatíveis com PgBouncer em modo transação.
        # Uma disputa não ocupa o pool indefinidamente. Nenhuma retentativa automática de POST.
        conexao.execute("set local lock_timeout = '2s'; set local statement_timeout = '5s'")
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
