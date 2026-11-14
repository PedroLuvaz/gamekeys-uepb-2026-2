"""Contrato da GK-16: pagamento simulado, consulta do pedido e entrega das chaves."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

StatusDoPedido = Literal["aguardando_pagamento", "pago", "entregue", "cancelado"]


class SolicitacaoPagamento(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metodo: Literal["cartao", "pix", "boleto"]


class ItemDoPedido(BaseModel):
    jogo_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class ChaveEntregue(BaseModel):
    jogo_id: int
    nome: str
    codigo: str


class PedidoDetalhado(BaseModel):
    """``chaves`` só é preenchida depois da entrega; antes disso vem vazia."""

    pedido_id: int
    status: StatusDoPedido
    valor_total: Decimal
    itens: list[ItemDoPedido]
    chaves: list[ChaveEntregue]
