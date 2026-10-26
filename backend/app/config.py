"""Configuração da API, lida de variáveis de ambiente.

Em desenvolvimento os valores vêm do .env.local na raiz do repositório (modelo em
.env.example). Variáveis já definidas no ambiente (CI, deploy) têm prioridade sobre o arquivo.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RAIZ_DO_REPO = Path(__file__).resolve().parents[2]

load_dotenv(RAIZ_DO_REPO / ".env.local")
load_dotenv(RAIZ_DO_REPO / ".env")

# Endereços do Vite (React) em desenvolvimento.
ORIGENS_PADRAO = "http://localhost:5173,http://127.0.0.1:5173"


@dataclass(frozen=True)
class Configuracoes:
    ambiente: str
    database_url: str | None
    origens_cors: tuple[str, ...]
    timeout_banco: float
    jwt_secret: str | None = None
    jwt_duracao_minutos: int = 60

    @property
    def em_producao(self) -> bool:
        return self.ambiente == "producao"


def carregar() -> Configuracoes:
    origens = os.getenv("CORS_ORIGENS", ORIGENS_PADRAO)
    return Configuracoes(
        ambiente=os.getenv("AMBIENTE", "desenvolvimento"),
        database_url=os.getenv("DATABASE_URL") or None,
        origens_cors=tuple(o.strip() for o in origens.split(",") if o.strip()),
        timeout_banco=float(os.getenv("BANCO_TIMEOUT_SEGUNDOS", "5")),
        jwt_secret=os.getenv("JWT_SECRET") or None,
        jwt_duracao_minutos=int(os.getenv("JWT_DURACAO_MINUTOS", "60")),
    )
