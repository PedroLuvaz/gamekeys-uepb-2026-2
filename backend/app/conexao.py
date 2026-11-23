"""Erros de conexão PostgreSQL sem URLs, senhas ou diagnósticos do servidor."""

import re
from typing import Self

import psycopg
from psycopg.conninfo import conninfo_to_dict


def parametros_conexao(url: str) -> dict[str, str]:
    """Valida a configuração antes de iniciar conexões ou workers do pool."""
    __tracebackhide__ = True
    try:
        return conninfo_to_dict(url)
    except (psycopg.Error, ValueError):
        # O parser pode incluir a própria senha ao explicar um percent-encoding inválido.
        raise psycopg.ProgrammingError("Configuração da conexão PostgreSQL inválida.") from None


class ConexaoPostgres(psycopg.Connection):
    """Preserva a classe/SQLSTATE do erro, sem repassar sua mensagem ao log do pool."""

    @classmethod
    def connect(cls, conninfo: str = "", **kwargs) -> Self:
        __tracebackhide__ = True
        try:
            return super().connect(conninfo, **kwargs)
        except (psycopg.Error, ValueError) as erro:
            estado = getattr(erro, "sqlstate", None)
            estado = (
                estado if isinstance(estado, str) and re.fullmatch(r"[0-9A-Z]{5}", estado) else None
            )
            mensagem = "Falha ao conectar ao PostgreSQL."
            if estado:
                mensagem += f" SQLSTATE {estado}."
            classe = type(erro) if isinstance(erro, psycopg.Error) else psycopg.ProgrammingError
            falha = classe(mensagem)
            falha.sqlstate = estado
            # Não carregar diag/pgconn nem encadear a exceção original: podem conter segredos.
            raise falha from None
