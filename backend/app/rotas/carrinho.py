"""Endpoints autenticados do carrinho (GK-11/GK-12)."""

from typing import Annotated, NoReturn

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Path

from app.db import BancoNaoConfigurado
from app.esquemas.carrinho import (
    AdicaoAoCarrinho,
    AlteracaoQuantidade,
    CarrinhoConsultado,
    ItemDoCarrinho,
)
from app.esquemas.clientes import ClienteCadastrado
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho

router = APIRouter(prefix="/carrinho", tags=["carrinho"])
JogoId = Annotated[int, Path(ge=1, le=9_223_372_036_854_775_807)]


def _traduzir_erro(erro: Exception) -> NoReturn:
    if isinstance(erro, carrinho.ClienteNaoPermitido):
        raise HTTPException(status_code=403, detail="O carrinho é exclusivo de clientes.") from erro
    if isinstance(erro, carrinho.ItemCarrinhoNaoEncontrado):
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho.") from erro
    if isinstance(erro, carrinho.JogoNaoEncontrado):
        raise HTTPException(status_code=404, detail="Jogo não encontrado.") from erro
    if isinstance(erro, carrinho.EstoqueInsuficiente):
        raise HTTPException(
            status_code=409, detail="Estoque insuficiente para a quantidade solicitada."
        ) from erro
    if isinstance(erro, carrinho.ClassificacaoNaoPermitida):
        raise HTTPException(
            status_code=403, detail="Sua idade não permite adicionar este jogo ao carrinho."
        ) from erro
    if isinstance(erro, (BancoNaoConfigurado, psycopg.Error)):
        raise HTTPException(
            status_code=503,
            detail="Carrinho temporariamente indisponível. Tente novamente em instantes.",
        ) from erro
    raise erro


@router.get(
    "",
    response_model=CarrinhoConsultado,
    responses={
        401: {"description": "Autenticação ausente, inválida ou expirada."},
        403: {"description": "Perfil não permitido."},
        503: {"description": "Banco indisponível."},
    },
)
def consultar_meu_carrinho(
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> CarrinhoConsultado:
    """Consulta somente o carrinho identificado pela sessão do cliente."""
    try:
        return carrinho.consultar_carrinho(cliente)
    except Exception as erro:
        _traduzir_erro(erro)


@router.post(
    "/itens",
    response_model=ItemDoCarrinho,
    responses={
        401: {"description": "Autenticação ausente, inválida ou expirada."},
        403: {"description": "Perfil não permitido ou classificação etária acima da idade."},
        404: {"description": "Jogo inexistente ou inativo."},
        409: {"description": "Quantidade acumulada acima do estoque disponível."},
        503: {"description": "Banco indisponível ou tempo limite de acesso/bloqueio excedido."},
    },
)
def adicionar_ao_carrinho(
    dados: AdicaoAoCarrinho,
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> ItemDoCarrinho:
    """Adiciona unidades ao próprio carrinho e retorna o item com a quantidade final.

    O cliente vem da sessão. Preço e disponibilidade vêm do banco. Adicionar novamente
    soma unidades; não reserva chaves. Valores monetários são strings decimais na resposta.
    """
    try:
        return carrinho.adicionar_item(cliente, dados)
    except Exception as erro:
        _traduzir_erro(erro)


@router.patch(
    "/itens/{jogo_id}",
    response_model=CarrinhoConsultado,
    responses={
        401: {"description": "Autenticação ausente, inválida ou expirada."},
        403: {"description": "Perfil não permitido."},
        404: {"description": "Item inexistente no carrinho do cliente."},
        409: {"description": "Nova quantidade acima do estoque disponível."},
        503: {"description": "Banco indisponível ou tempo limite excedido."},
    },
)
def alterar_item_do_carrinho(
    jogo_id: JogoId,
    dados: AlteracaoQuantidade,
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> CarrinhoConsultado:
    """Substitui a quantidade do item; não soma e não aceita IDs no corpo."""
    try:
        return carrinho.alterar_quantidade(cliente, jogo_id, dados)
    except Exception as erro:
        _traduzir_erro(erro)


@router.delete(
    "/itens/{jogo_id}",
    response_model=CarrinhoConsultado,
    responses={
        401: {"description": "Autenticação ausente, inválida ou expirada."},
        403: {"description": "Perfil não permitido."},
        404: {"description": "Item inexistente no carrinho do cliente."},
        503: {"description": "Banco indisponível ou tempo limite excedido."},
    },
)
def remover_item_do_carrinho(
    jogo_id: JogoId,
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> CarrinhoConsultado:
    """Remove o item somente do carrinho identificado pela sessão."""
    try:
        return carrinho.remover_item(cliente, jogo_id)
    except Exception as erro:
        _traduzir_erro(erro)
