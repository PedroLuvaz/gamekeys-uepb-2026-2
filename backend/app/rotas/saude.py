import os
import re

import psycopg
from fastapi import APIRouter, HTTPException

from app.db import BancoNaoConfigurado, verificar_banco
from app.esquemas.saude import Saude, SaudeBanco

router = APIRouter(prefix="/saude", tags=["saúde"])


@router.get("", response_model=Saude)
def saude() -> Saude:
    """Verificação de saúde usada pelo CI e, depois, pelo deploy."""
    return Saude(status="ok")


@router.get("/versao")
def versao() -> dict[str, str]:
    """Identifica o código publicado, sem consultar o banco ou expor configuração."""
    commit = os.getenv("GAMEKEYS_COMMIT") or os.getenv("VERCEL_GIT_COMMIT_SHA", "")
    return {"commit": commit if re.fullmatch(r"[0-9a-f]{40}", commit) else "desenvolvimento"}


@router.get("/banco", response_model=SaudeBanco)
def saude_banco() -> SaudeBanco:
    """Confirma que a API consegue consultar o PostgreSQL."""
    try:
        return SaudeBanco(status="ok", **verificar_banco())
    except BancoNaoConfigurado as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except psycopg.Error as erro:
        # Mensagem fixa: o erro do driver pode trazer host, usuário ou trechos da URL.
        raise HTTPException(status_code=503, detail="banco indisponível") from erro
