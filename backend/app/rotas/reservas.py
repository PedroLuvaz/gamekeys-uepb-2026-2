"""GK-124: reserva autenticada. Pagamento e entrega seguem na GK-16."""

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException
from psycopg_pool import PoolTimeout

from app.db import BancoNaoConfigurado
from app.esquemas.clientes import ClienteCadastrado
from app.esquemas.reservas import PedidoReservado, SolicitacaoReserva
from app.rotas.autenticacao import usuario_atual
from app.servicos import carrinho, reservas

router = APIRouter(prefix="/pedidos", tags=["reservas"])


@router.post(
    "/reservas",
    response_model=PedidoReservado,
    responses={
        401: {"description": "Autenticação ausente, inválida ou expirada."},
        403: {"description": "Perfil ou classificação etária não permitidos."},
        404: {"description": "Jogo inexistente ou inativo."},
        409: {"description": "Carrinho vazio ou chaves insuficientes para reservar tudo."},
        422: {"description": "Entrada inválida ou limite operacional/monetário do pedido."},
        503: {"description": "Banco indisponível ou tempo limite excedido."},
    },
)
def reservar(
    dados: SolicitacaoReserva,
    cliente: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> PedidoReservado:
    """Reserva o próprio carrinho. Repita o mesmo UUID para recuperar o mesmo pedido.

    Preços, itens e comprador vêm do servidor. Não retorna códigos de ativação.
    A reserva bem-sucedida esvazia o carrinho na mesma transação.
    """
    try:
        return reservas.reservar_carrinho(cliente, dados.chave_idempotencia)
    except carrinho.ClienteNaoPermitido as erro:
        raise HTTPException(403, "A reserva é exclusiva de clientes.") from erro
    except carrinho.ClassificacaoNaoPermitida as erro:
        raise HTTPException(403, "Sua idade não permite reservar um dos jogos.") from erro
    except carrinho.JogoNaoEncontrado as erro:
        raise HTTPException(404, "Um dos jogos não está disponível.") from erro
    except carrinho.EstoqueInsuficiente as erro:
        raise HTTPException(409, "Estoque insuficiente para reservar todos os jogos.") from erro
    except reservas.CarrinhoVazio as erro:
        raise HTTPException(409, "O carrinho está vazio.") from erro
    except reservas.LimiteDoPedido as erro:
        raise HTTPException(422, "O pedido excede o limite de itens, unidades ou valor.") from erro
    except (BancoNaoConfigurado, psycopg.Error, PoolTimeout) as erro:
        raise HTTPException(503, "Reserva temporariamente indisponível.") from erro
