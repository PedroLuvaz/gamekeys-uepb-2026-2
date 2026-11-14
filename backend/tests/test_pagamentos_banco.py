"""GK-16: pagamento e entrega pela API/JWT/PostgreSQL reais, só em gamekeys_teste local."""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from test_carrinho_banco import adicionar, ambiente  # noqa: F401
from test_reservas_banco import reserva, reservar  # noqa: F401

from app.servicos import pagamentos


@pytest.fixture
def loja(reserva, monkeypatch):  # noqa: F811 (fixture reutilizada da reserva)
    monkeypatch.setattr(pagamentos, "obter_pool", lambda: reserva.pool)
    pedidos = []

    def pedido_reservado(headers, jogo, quantidade=1):
        assert adicionar(reserva, headers, jogo, quantidade).status_code == 200
        resposta = reservar(reserva, headers)
        assert resposta.status_code == 200
        pedidos.append(resposta.json()["pedido_id"])
        return resposta.json()["pedido_id"]

    reserva.pedido_reservado = pedido_reservado
    try:
        yield reserva
    finally:
        # A limpeza da reserva apaga os pedidos; o pagamento aponta para eles e sai antes.
        with reserva.pool.connection() as c:
            c.execute("delete from vendas.pagamentos where pedido_id = any(%s)", (pedidos,))


def pagar(loja, headers, pedido_id, metodo="pix"):
    url = f"/pedidos/{pedido_id}/pagamento"
    return loja.api.post(url, headers=headers, json={"metodo": metodo})


def situacao(loja, pedido_id):
    with loja.pool.connection() as c:
        return {
            "status": c.execute(
                "select status from vendas.pedidos where id=%s", (pedido_id,)
            ).fetchone()[0],
            "pagamentos": c.execute(
                "select metodo, status, valor from vendas.pagamentos where pedido_id=%s",
                (pedido_id,),
            ).fetchall(),
            "chaves": sorted(
                linha[0]
                for linha in c.execute(
                    "select c.status from catalogo.chaves c join vendas.itens_pedido i"
                    " on i.chave_id=c.id where i.pedido_id=%s",
                    (pedido_id,),
                ).fetchall()
            ),
        }


def test_pagamento_entrega_as_chaves_e_registra_o_pagamento(loja):
    """Cenário 1 da GK-16: o pedido fica Entregue e o cliente vê suas chaves."""
    _, headers = loja.cliente()
    jogo = loja.jogo_fisico(3)
    pedido_id = loja.pedido_reservado(headers, jogo, 2)
    resposta = pagar(loja, headers, pedido_id)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["status"] == "entregue"
    assert dados["valor_total"] == "39.80"
    assert dados["itens"] == [
        {
            "jogo_id": jogo,
            "nome": "Jogo Carrinho",
            "quantidade": 2,
            "preco_unitario": "19.90",
            "subtotal": "39.80",
        }
    ]
    assert len(dados["chaves"]) == 2
    assert len({chave["codigo"] for chave in dados["chaves"]}) == 2
    assert all(chave["codigo"].startswith("QA-SEM-VALOR-") for chave in dados["chaves"])
    assert situacao(loja, pedido_id) == {
        "status": "entregue",
        "pagamentos": [("pix", "aprovado", Decimal("39.80"))],
        "chaves": ["vendida", "vendida"],
    }
    # A chave vendida não volta ao estoque: sobra 1 das 3.
    assert loja.conferir()["estoques"] == [(1, 1)]
    assert loja.api.get(f"/pedidos/{pedido_id}", headers=headers).json() == dados


def test_consulta_antes_da_entrega_nao_mostra_codigos(loja):
    """Cenário 2 da GK-16: antes da entrega o código das chaves não aparece."""
    _, headers = loja.cliente()
    pedido_id = loja.pedido_reservado(headers, loja.jogo_fisico(2))
    resposta = loja.api.get(f"/pedidos/{pedido_id}", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "aguardando_pagamento"
    assert resposta.json()["chaves"] == []
    assert "QA-SEM-VALOR" not in resposta.text


def test_valor_pago_e_o_gravado_no_pedido_mesmo_com_preco_novo_no_catalogo(loja):
    """GK-47 / DA-CON-I2-02: o preço do pedido não acompanha o catálogo."""
    _, headers = loja.cliente()
    jogo = loja.jogo_fisico(1, preco=Decimal("50.00"))
    pedido_id = loja.pedido_reservado(headers, jogo)
    with loja.pool.connection() as c:
        c.execute("update catalogo.jogos set preco=70.00 where id=%s", (jogo,))
    dados = pagar(loja, headers, pedido_id).json()
    assert dados["valor_total"] == "50.00"
    assert dados["itens"][0]["preco_unitario"] == "50.00"
    assert situacao(loja, pedido_id)["pagamentos"] == [("pix", "aprovado", Decimal("50.00"))]


def test_repetir_o_pagamento_devolve_o_mesmo_pedido_sem_cobrar_de_novo(loja):
    _, headers = loja.cliente()
    pedido_id = loja.pedido_reservado(headers, loja.jogo_fisico(1))
    primeira = pagar(loja, headers, pedido_id, "cartao")
    segunda = pagar(loja, headers, pedido_id, "boleto")
    assert primeira.status_code == segunda.status_code == 200
    assert segunda.json() == primeira.json()
    assert situacao(loja, pedido_id)["pagamentos"] == [("cartao", "aprovado", Decimal("19.90"))]


def test_dois_pagamentos_simultaneos_geram_um_pagamento_e_a_mesma_entrega(loja):
    _, headers = loja.cliente()
    pedido_id = loja.pedido_reservado(headers, loja.jogo_fisico(2), 2)
    largada = Barrier(4)

    def tentar(_):
        largada.wait(timeout=10)
        return pagar(loja, headers, pedido_id)

    with ThreadPoolExecutor(max_workers=4) as executor:
        respostas = list(executor.map(tentar, range(4)))
    assert [r.status_code for r in respostas] == [200] * 4
    assert all(r.json() == respostas[0].json() for r in respostas)
    assert len(situacao(loja, pedido_id)["pagamentos"]) == 1


def test_pedido_de_outro_cliente_nao_e_pago_nem_consultado(loja):
    _, dono = loja.cliente()
    _, outro = loja.cliente()
    pedido_id = loja.pedido_reservado(dono, loja.jogo_fisico(1))
    assert pagar(loja, outro, pedido_id).status_code == 404
    assert loja.api.get(f"/pedidos/{pedido_id}", headers=outro).status_code == 404
    assert situacao(loja, pedido_id) == {
        "status": "aguardando_pagamento",
        "pagamentos": [],
        "chaves": ["reservada"],
    }


def test_pedido_cancelado_nao_pode_ser_pago(loja):
    _, headers = loja.cliente()
    pedido_id = loja.pedido_reservado(headers, loja.jogo_fisico(1))
    with loja.pool.connection() as c:
        c.execute("update vendas.pedidos set status='cancelado' where id=%s", (pedido_id,))
    resposta = pagar(loja, headers, pedido_id)
    assert resposta.status_code == 409
    assert resposta.json() == {"detail": "Este pedido não está aguardando pagamento."}
    assert situacao(loja, pedido_id)["pagamentos"] == []


def test_chave_fora_de_reservada_desfaz_o_pagamento_inteiro(loja):
    _, headers = loja.cliente()
    pedido_id = loja.pedido_reservado(headers, loja.jogo_fisico(2), 2)
    with loja.pool.connection() as c:
        c.execute(
            "update catalogo.chaves set status='invalidada' where id = (select min(chave_id)"
            " from vendas.itens_pedido where pedido_id=%s)",
            (pedido_id,),
        )
    with pytest.raises(RuntimeError, match="inconsistente"):
        pagar(loja, headers, pedido_id)
    assert situacao(loja, pedido_id) == {
        "status": "aguardando_pagamento",
        "pagamentos": [],
        "chaves": ["invalidada", "reservada"],
    }


def test_administrador_nao_paga_pedido(loja):
    _, cliente = loja.cliente()
    _, administrador = loja.cliente(perfil="administrador")
    pedido_id = loja.pedido_reservado(cliente, loja.jogo_fisico(1))
    assert pagar(loja, administrador, pedido_id).status_code == 403
    assert loja.api.get(f"/pedidos/{pedido_id}", headers=administrador).status_code == 403
