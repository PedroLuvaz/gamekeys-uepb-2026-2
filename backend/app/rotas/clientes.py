"""Endpoint público de cadastro de clientes (GK-78)."""

import psycopg
from fastapi import APIRouter, HTTPException, status

from app.db import BancoNaoConfigurado
from app.esquemas.clientes import CadastroDeCliente, ClienteCadastrado
from app.servicos import clientes

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteCadastrado, status_code=status.HTTP_201_CREATED)
def cadastrar_cliente(dados: CadastroDeCliente) -> ClienteCadastrado:
    """Cria uma conta Cliente sem expor senha ou hash na resposta."""
    try:
        return clientes.cadastrar(dados)
    except psycopg.errors.UniqueViolation as erro:
        raise HTTPException(status_code=409, detail="Este e-mail já está em uso.") from erro
    except (BancoNaoConfigurado, psycopg.Error) as erro:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível concluir o cadastro. Tente novamente mais tarde.",
        ) from erro
