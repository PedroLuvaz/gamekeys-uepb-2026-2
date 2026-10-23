"""Contrato público compartilhado pela listagem e pelo detalhe dos jogos."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class Disponibilidade(StrEnum):
    DISPONIVEL = "Disponível"
    ESGOTADO = "Esgotado"


class JogoNoCatalogo(BaseModel):
    id: int
    nome: str
    capa_url: str | None
    preco: Decimal
    disponibilidade: Disponibilidade


class PaginaDeJogos(BaseModel):
    itens: list[JogoNoCatalogo]
    pagina: int
    por_pagina: int
    total: int
    total_paginas: int


class DetalheDoJogo(JogoNoCatalogo):
    descricao: str
    genero: str
    plataforma: str
    classificacao: str
