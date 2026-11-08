"""Primitiva reutilizável pela GK-126: uma transação externa controla o commit."""

from psycopg import Connection
from psycopg.pq import TransactionStatus

from app.servicos.carrinho import EstoqueInsuficiente


def reservar_chaves(conexao: Connection, jogo_id: int, quantidade: int) -> list[int]:
    """Chamador bloqueia carrinho/jogos em ordem e desfaz tudo se faltar uma chave.

    Não abre pool, não faz commit e nunca lê códigos. Rodar em autocommit permitiria
    perder os bloqueios entre seleção e atualização, portanto é recusado.
    """
    if conexao.info.transaction_status != TransactionStatus.INTRANS:
        raise RuntimeError("A reserva exige uma transação externa ativa")
    if not 1 <= quantidade <= 1000:
        raise ValueError("Quantidade fora do limite operacional da reserva")
    linhas = conexao.execute(
        "select id from catalogo.chaves where jogo_id = %s and status = 'disponivel'"
        " order by id limit %s for update skip locked",
        (jogo_id, quantidade),
    ).fetchall()
    if len(linhas) != quantidade:
        raise EstoqueInsuficiente
    ids = [linha[0] for linha in linhas]
    conexao.execute("update catalogo.chaves set status = 'reservada' where id = any(%s)", (ids,))
    return ids
