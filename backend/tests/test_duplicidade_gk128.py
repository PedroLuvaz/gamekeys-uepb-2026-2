"""GK-128: consultas no PostgreSQL real e corrupção limitada a rollback."""

from uuid import uuid4

import psycopg
import pytest
from test_reservas_banco import adicionar, ambiente, reserva, reservar  # noqa: F401

from qa.duplicidade import chaves_em_mais_de_um_pedido, chaves_inconsistentes


@pytest.fixture
def jogo_com_chaves(reserva):  # noqa: F811
    jogo_id = reserva.jogo_fisico(0)
    with reserva.pool.connection() as conexao:
        chaves = [
            conexao.execute(
                "insert into catalogo.chaves (jogo_id, codigo, cadastrada_por)"
                " values (%s, %s, %s) returning id",
                (jogo_id, "GK-TESTE-" + uuid4().hex, reserva.administrador.id),
            ).fetchone()[0]
            for _ in range(2)
        ]
    return jogo_id, chaves


def test_consultas_vazias_depois_de_reservas_normais(reserva, jogo_com_chaves):  # noqa: F811
    jogo_id, _ = jogo_com_chaves
    for _ in range(2):
        _, headers = reserva.cliente()
        assert adicionar(reserva, headers, jogo_id).status_code == 200
        assert reservar(reserva, headers).status_code == 200
    with reserva.pool.connection() as conexao:
        assert chaves_em_mais_de_um_pedido(conexao) == []
        assert chaves_inconsistentes(conexao) == []


def test_detecta_chave_em_pedidos_distintos_e_rollback_restaura_unique(
    reserva,  # noqa: F811
    jogo_com_chaves,
):
    jogo_id, chaves = jogo_com_chaves
    usuario, headers = reserva.cliente()
    assert adicionar(reserva, headers, jogo_id).status_code == 200
    primeiro = reservar(reserva, headers).json()["pedido_id"]
    with reserva.pool.connection() as conexao:
        with conexao.transaction(force_rollback=True):
            conexao.execute(
                "alter table vendas.itens_pedido drop constraint itens_pedido_chave_id_key"
            )
            # Repetir um item no mesmo pedido não significa dois pedidos distintos.
            conexao.execute(
                "insert into vendas.itens_pedido (pedido_id, jogo_id, chave_id, preco_unitario)"
                " values (%s, %s, %s, 19.90)",
                (primeiro, jogo_id, chaves[0]),
            )
            assert chaves_em_mais_de_um_pedido(conexao) == []
            segundo = conexao.execute(
                "insert into vendas.pedidos (usuario_id, chave_idempotencia, valor_total)"
                " values (%s, %s, 19.90) returning id",
                (usuario.id, uuid4()),
            ).fetchone()[0]
            conexao.execute(
                "insert into vendas.itens_pedido (pedido_id, jogo_id, chave_id, preco_unitario)"
                " values (%s, %s, %s, 19.90)",
                (segundo, jogo_id, chaves[0]),
            )
            assert chaves_em_mais_de_um_pedido(conexao) == [
                {"chave_id": chaves[0], "jogo_id": jogo_id, "pedido_ids": [primeiro, segundo]}
            ]
        assert chaves_em_mais_de_um_pedido(conexao) == []
        with pytest.raises(psycopg.errors.UniqueViolation), conexao.transaction():
            conexao.execute(
                "insert into vendas.itens_pedido (pedido_id, jogo_id, chave_id, preco_unitario)"
                " values (%s, %s, %s, 19.90)",
                (primeiro, jogo_id, chaves[0]),
            )


@pytest.mark.parametrize("status", ["reservada", "vendida"])
def test_detecta_chave_sem_item_de_pedido(reserva, jogo_com_chaves, status):  # noqa: F811
    jogo_id, chaves = jogo_com_chaves
    with reserva.pool.connection() as conexao, conexao.transaction(force_rollback=True):
        conexao.execute("update catalogo.chaves set status = %s where id = %s", (status, chaves[0]))
        assert chaves_inconsistentes(conexao) == [
            {
                "chave_id": chaves[0],
                "jogo_id": jogo_id,
                "status": status,
                "pedido_ids": [],
                "motivo": "sem_item_pedido",
            }
        ]
        assert chaves_em_mais_de_um_pedido(conexao) == []


def test_detecta_item_com_chave_disponivel(reserva, jogo_com_chaves):  # noqa: F811
    jogo_id, chaves = jogo_com_chaves
    _, headers = reserva.cliente()
    assert adicionar(reserva, headers, jogo_id).status_code == 200
    pedido_id = reservar(reserva, headers).json()["pedido_id"]
    with reserva.pool.connection() as conexao, conexao.transaction(force_rollback=True):
        conexao.execute(
            "update catalogo.chaves set status = 'disponivel' where id = %s", (chaves[0],)
        )
        assert chaves_inconsistentes(conexao) == [
            {
                "chave_id": chaves[0],
                "jogo_id": jogo_id,
                "status": "disponivel",
                "pedido_ids": [pedido_id],
                "motivo": "disponivel_com_item",
            }
        ]
