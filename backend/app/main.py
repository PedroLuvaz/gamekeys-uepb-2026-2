"""Ponto de entrada da API.

Organização:
    config.py   variáveis de ambiente
    db.py       acesso ao banco (pool de conexões)
    esquemas/   validação de entrada e saída (Pydantic)
    servicos/   regras de negócio
    rotas/      endpoints HTTP
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Configuracoes, carregar
from app.db import fechar_pool
from app.rotas import catalogo, saude


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    yield
    fechar_pool()


def criar_app(config: Configuracoes | None = None) -> FastAPI:
    config = config or carregar()
    # Documentação automática só fora de produção.
    app = FastAPI(
        title="GameKeys API",
        version="0.1.0",
        lifespan=ciclo_de_vida,
        docs_url=None if config.em_producao else "/docs",
        redoc_url=None,
        openapi_url=None if config.em_producao else "/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.origens_cors),
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(saude.router)
    app.include_router(catalogo.router)
    return app


app = criar_app()
