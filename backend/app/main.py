from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException

from app.db import BancoNaoConfigurado, fechar_pool, verificar_banco


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    yield
    fechar_pool()


app = FastAPI(title="GameKeys API", version="0.1.0", lifespan=ciclo_de_vida)


@app.get("/saude")
def saude() -> dict[str, str]:
    """Verificação de saúde usada pelo CI e, depois, pelo deploy."""
    return {"status": "ok"}


@app.get("/saude/banco")
def saude_banco() -> dict[str, str]:
    """Confirma que a API consegue consultar o PostgreSQL."""
    try:
        return {"status": "ok", **verificar_banco()}
    except BancoNaoConfigurado as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except psycopg.Error as erro:
        raise HTTPException(status_code=503, detail="banco indisponível") from erro
