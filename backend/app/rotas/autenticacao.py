"""Login e rota protegida da sessão (GK-81/GK-71)."""

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import BancoNaoConfigurado
from app.esquemas.autenticacao import Credenciais, SessaoCriada
from app.esquemas.clientes import ClienteCadastrado
from app.servicos import autenticacao

router = APIRouter(prefix="/auth", tags=["autenticação"])
portador = HTTPBearer(auto_error=False)


def erro_nao_autorizado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/login", response_model=SessaoCriada)
def login(credenciais: Credenciais) -> SessaoCriada:
    try:
        usuario = autenticacao.autenticar(credenciais.email, credenciais.senha)
        if usuario is None:
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
        token, duracao = autenticacao.criar_token(usuario)
        return SessaoCriada(
            access_token=token,
            expires_in=duracao,
            usuario=usuario.publico(),
        )
    except HTTPException:
        raise
    except autenticacao.JwtNaoConfigurado as erro:
        raise HTTPException(
            status_code=503, detail="Autenticação temporariamente indisponível."
        ) from erro
    except (BancoNaoConfigurado, psycopg.Error) as erro:
        raise HTTPException(
            status_code=503, detail="Autenticação temporariamente indisponível."
        ) from erro


def usuario_atual(
    credencial: Annotated[HTTPAuthorizationCredentials | None, Depends(portador)],
) -> ClienteCadastrado:
    if credencial is None or credencial.scheme.lower() != "bearer":
        raise erro_nao_autorizado()
    try:
        usuario_id = autenticacao.id_do_token(credencial.credentials)
        usuario = autenticacao.buscar_ativo_por_id(usuario_id)
    except (autenticacao.TokenInvalido, autenticacao.JwtNaoConfigurado):
        raise erro_nao_autorizado() from None
    except (BancoNaoConfigurado, psycopg.Error) as erro:
        raise HTTPException(
            status_code=503, detail="Autenticação temporariamente indisponível."
        ) from erro
    if usuario is None:
        raise erro_nao_autorizado()
    return usuario.publico()


@router.get("/me", response_model=ClienteCadastrado)
def consultar_sessao(
    usuario: Annotated[ClienteCadastrado, Depends(usuario_atual)],
) -> ClienteCadastrado:
    return usuario
