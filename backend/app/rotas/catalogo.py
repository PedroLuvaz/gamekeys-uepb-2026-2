from typing import Annotated

import psycopg
from fastapi import APIRouter, HTTPException, Path, Query

from app.db import BancoNaoConfigurado
from app.esquemas.catalogo import DetalheDoJogo, PaginaDeJogos
from app.servicos import catalogo

router = APIRouter(prefix="/jogos", tags=["catálogo"])


@router.get("", response_model=PaginaDeJogos)
def listar_jogos(
    pagina: Annotated[int, Query(ge=1, le=2_147_483_647, description="Página, a partir de 1")] = 1,
) -> PaginaDeJogos:
    """Lista jogos ativos, em páginas de 20, ordenados por nome e identificador."""
    try:
        return catalogo.listar_jogos(pagina)
    except (BancoNaoConfigurado, psycopg.Error) as erro:
        # Não devolver erros do driver: podem conter dados da conexão ou SQL.
        raise HTTPException(
            status_code=503, detail="Catálogo indisponível. Tente novamente mais tarde."
        ) from erro


@router.get("/{jogo_id}", response_model=DetalheDoJogo)
def detalhe_do_jogo(
    jogo_id: Annotated[int, Path(ge=1, le=9_223_372_036_854_775_807)],
) -> DetalheDoJogo:
    """Consulta um jogo ativo pelo identificador, com a mesma disponibilidade da listagem."""
    try:
        jogo = catalogo.consultar_jogo(jogo_id)
    except (BancoNaoConfigurado, psycopg.Error) as erro:
        raise HTTPException(
            status_code=503, detail="Catálogo indisponível. Tente novamente mais tarde."
        ) from erro
    if jogo is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    return jogo
