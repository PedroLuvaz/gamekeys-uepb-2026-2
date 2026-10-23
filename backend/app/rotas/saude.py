import psycopg
from fastapi import APIRouter, HTTPException

from app.db import BancoNaoConfigurado, verificar_banco
from app.esquemas.saude import Saude, SaudeBanco

router = APIRouter(prefix="/saude", tags=["saúde"])


@router.get("", response_model=Saude)
def saude() -> Saude:
    """Verificação de saúde usada pelo CI e, depois, pelo deploy."""
    return Saude(status="ok")


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
