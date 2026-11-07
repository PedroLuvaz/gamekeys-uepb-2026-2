"""Endpoint autenticado de adição ao carrinho (GK-11/GK-118)."""

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.db import BancoNaoConfigurado
from app.esquemas.carrinho import AdicaoAoCarrinho, ItemDoCarrinho
from app.esquemas.clientes import ClienteCadastrado
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho

router = APIRouter(prefix="/carrinho", tags=["carrinho"])


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
    except carrinho.ClienteNaoPermitido as erro:
        raise HTTPException(status_code=403, detail="O carrinho é exclusivo de clientes.") from erro
    except carrinho.JogoNaoEncontrado as erro:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.") from erro
    except carrinho.EstoqueInsuficiente as erro:
        raise HTTPException(
            status_code=409, detail="Estoque insuficiente para a quantidade solicitada."
        ) from erro
    except carrinho.ClassificacaoNaoPermitida as erro:
        raise HTTPException(
            status_code=403, detail="Sua idade não permite adicionar este jogo ao carrinho."
        ) from erro
    except (BancoNaoConfigurado, psycopg.Error) as erro:
        raise HTTPException(
            status_code=503,
            detail="Carrinho temporariamente indisponível. Tente novamente em instantes.",
        ) from erro
