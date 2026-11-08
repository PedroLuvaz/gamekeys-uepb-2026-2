"""Contrato da reserva GK-124. Códigos de ativação pertencem à entrega da GK-16."""

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SolicitacaoReserva(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chave_idempotencia: UUID


class ItemReservado(BaseModel):
    jogo_id: int
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class PedidoReservado(BaseModel):
    pedido_id: int
    status: Literal["aguardando_pagamento", "pago", "cancelado"]
    valor_total: Decimal
    itens: list[ItemReservado]
