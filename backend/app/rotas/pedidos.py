"""GK-16: consulta do pedido e pagamento simulado com entrega das chaves."""

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Path
from psycopg_pool import PoolTimeout

from app.db import BancoNaoConfigurado
from app.esquemas.clientes import ClienteCadastrado
from app.esquemas.pedidos import PedidoDetalhado, SolicitacaoPagamento
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho, pagamentos

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

IdDoPedido = Annotated[int, Path(ge=1, le=9223372036854775807)]
RESPOSTAS = {
    401: {"description": "Autenticação ausente, inválida ou expirada."},
    403: {"description": "Perfil diferente de cliente."},
    404: {"description": "Pedido inexistente ou de outro cliente."},
    503: {"description": "Banco indisponível ou tempo limite excedido."},
}


@router.get("/{pedido_id}", response_model=PedidoDetalhado, responses=RESPOSTAS)
def consultar(
    pedido_id: IdDoPedido,
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> PedidoDetalhado:
    """Consulta o próprio pedido. Os códigos só aparecem depois da entrega."""
    try:
        return pagamentos.consultar_pedido(cliente, pedido_id)
    except carrinho.ClienteNaoPermitido as erro:
        raise HTTPException(403, "Os pedidos são exclusivos de clientes.") from erro
    except pagamentos.PedidoNaoEncontrado as erro:
        raise HTTPException(404, "Pedido não encontrado.") from erro
    except (BancoNaoConfigurado, psycopg.Error, PoolTimeout) as erro:
        raise HTTPException(503, "Pedido temporariamente indisponível.") from erro


@router.post(
    "/{pedido_id}/pagamento",
    response_model=PedidoDetalhado,
    responses={
        **RESPOSTAS,
        409: {"description": "O pedido não está aguardando pagamento."},
        422: {"description": "Método de pagamento inválido."},
    },
)
def pagar(
    pedido_id: IdDoPedido,
    dados: SolicitacaoPagamento,
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> PedidoDetalhado:
    """Confirma o pagamento simulado e entrega as chaves. Repetir devolve o mesmo pedido."""
    try:
        return pagamentos.pagar_pedido(cliente, pedido_id, dados.metodo)
    except carrinho.ClienteNaoPermitido as erro:
        raise HTTPException(403, "O pagamento é exclusivo de clientes.") from erro
    except pagamentos.PedidoNaoEncontrado as erro:
        raise HTTPException(404, "Pedido não encontrado.") from erro
    except pagamentos.PedidoNaoPagavel as erro:
        raise HTTPException(409, "Este pedido não está aguardando pagamento.") from erro
    except (BancoNaoConfigurado, psycopg.Error, PoolTimeout) as erro:
        raise HTTPException(503, "Pagamento temporariamente indisponível.") from erro
