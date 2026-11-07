"""Contrato da adição ao carrinho (GK-11/GK-118), compartilhado com o front e GK-12."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AdicaoAoCarrinho(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jogo_id: Annotated[int, Field(strict=True, ge=1, le=9_223_372_036_854_775_807)]
    quantidade: Annotated[int, Field(strict=True, ge=1, le=2_147_483_647)] = 1


class ItemDoCarrinho(BaseModel):
    carrinho_id: int
    jogo_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal
