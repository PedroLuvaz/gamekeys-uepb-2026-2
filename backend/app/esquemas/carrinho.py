"""Contratos do carrinho das histórias GK-11 e GK-12."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AdicaoAoCarrinho(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jogo_id: Annotated[int, Field(strict=True, ge=1, le=9_223_372_036_854_775_807)]
    quantidade: Annotated[int, Field(strict=True, ge=1, le=2_147_483_647)] = 1


class AlteracaoQuantidade(BaseModel):
    """A quantidade informada substitui a atual; identificadores vêm da rota e sessão."""

    model_config = ConfigDict(extra="forbid")

    quantidade: Annotated[int, Field(strict=True, ge=1, le=2_147_483_647)]


class ItemDoCarrinho(BaseModel):
    carrinho_id: int
    jogo_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class ItemListadoNoCarrinho(BaseModel):
    jogo_id: int
    slug: str
    nome: str
    capa_url: str | None
    quantidade: int
    estoque_disponivel: int
    preco_unitario: Decimal
    subtotal: Decimal


class CarrinhoConsultado(BaseModel):
    itens: list[ItemListadoNoCarrinho]
    total: Decimal
