"""GK-128: consultas de integridade do modelo real, sem códigos de ativação."""

from pathlib import Path

from psycopg import Connection
from psycopg.rows import dict_row

SQL_DUPLICIDADE = (Path(__file__).parent / "sql" / "chave_em_mais_de_um_pedido.sql").read_text(
    encoding="utf-8"
)

SQL_INCONSISTENCIAS = """
select c.id as chave_id,
       c.jogo_id,
       c.status,
       coalesce(
           array_agg(distinct i.pedido_id order by i.pedido_id)
               filter (where i.pedido_id is not null),
           '{}'::bigint[]
       ) as pedido_ids,
       case when c.status = 'disponivel' then 'disponivel_com_item'
            else 'sem_item_pedido'
       end as motivo
  from catalogo.chaves as c
  left join vendas.itens_pedido as i on i.chave_id = c.id
 group by c.id, c.jogo_id, c.status
having (c.status in ('reservada', 'vendida') and count(i.id) = 0)
    or (c.status = 'disponivel' and count(i.id) > 0)
 order by c.id
"""


def chaves_em_mais_de_um_pedido(conexao: Connection) -> list[dict]:
    """Retorna chave_id, jogo_id e pedido_ids ordenados de pedidos distintos."""
    with conexao.cursor(row_factory=dict_row) as cursor:
        return cursor.execute(SQL_DUPLICIDADE).fetchall()


def chaves_inconsistentes(conexao: Connection) -> list[dict]:
    """Uma linha por chave: status, pedido_ids (vazio se órfã) e motivo."""
    with conexao.cursor(row_factory=dict_row) as cursor:
        return cursor.execute(SQL_INCONSISTENCIAS).fetchall()
