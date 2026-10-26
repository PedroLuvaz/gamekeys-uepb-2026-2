"""Autenticação bcrypt, emissão e validação de JWT (GK-81/GK-71)."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import bcrypt
import jwt
from psycopg.rows import class_row

from app.config import carregar
from app.db import obter_pool
from app.esquemas.clientes import ClienteCadastrado
from app.servicos.clientes import CUSTO_BCRYPT

ALGORITMO_JWT = "HS256"
EMISSOR_JWT = "gamekeys"
HASH_FALSO = bcrypt.hashpw(b"usuario-inexistente", bcrypt.gensalt(rounds=CUSTO_BCRYPT))


class JwtNaoConfigurado(RuntimeError):
    """JWT_SECRET não foi definida no ambiente."""


class TokenInvalido(ValueError):
    """Token ausente, adulterado, expirado ou sem os campos esperados."""


@dataclass
class UsuarioPersistido:
    id: int
    nome: str
    email: str
    senha_hash: str
    data_nascimento: date
    perfil: str
    ativo: bool

    def publico(self) -> ClienteCadastrado:
        return ClienteCadastrado(
            id=self.id,
            nome=self.nome,
            email=self.email,
            data_nascimento=self.data_nascimento,
            perfil=self.perfil,
        )


def buscar_por_email(email: str) -> UsuarioPersistido | None:
    with (
        obter_pool().connection() as conexao,
        conexao.cursor(row_factory=class_row(UsuarioPersistido)) as cursor,
    ):
        return cursor.execute(
            "select id, nome, email, senha_hash, data_nascimento, perfil, ativo"
            " from core.usuarios where lower(email) = lower(%s)",
            (email,),
        ).fetchone()


def buscar_ativo_por_id(usuario_id: int) -> UsuarioPersistido | None:
    with (
        obter_pool().connection() as conexao,
        conexao.cursor(row_factory=class_row(UsuarioPersistido)) as cursor,
    ):
        return cursor.execute(
            "select id, nome, email, senha_hash, data_nascimento, perfil, ativo"
            " from core.usuarios where id = %s and ativo",
            (usuario_id,),
        ).fetchone()


def autenticar(email: str, senha: str) -> UsuarioPersistido | None:
    usuario = buscar_por_email(email)
    hash_verificado = usuario.senha_hash.encode("ascii") if usuario else HASH_FALSO
    senha_em_bytes = senha.encode("utf-8")
    if len(senha_em_bytes) > 72:
        # bcrypt 5 rejeita entradas maiores; ainda fazemos uma comparação para
        # manter este caminho próximo do custo de uma credencial inválida comum.
        bcrypt.checkpw(b"senha-invalida", HASH_FALSO)
        return None
    corresponde = bcrypt.checkpw(senha_em_bytes, hash_verificado)
    if usuario is None or not usuario.ativo or not corresponde:
        return None
    return usuario


def _segredo() -> str:
    segredo = carregar().jwt_secret
    if not segredo or len(segredo.encode("utf-8")) < 32:
        raise JwtNaoConfigurado("JWT_SECRET não definida")
    return segredo


def criar_token(
    usuario: UsuarioPersistido,
    *,
    agora: datetime | None = None,
    duracao_minutos: int | None = None,
) -> tuple[str, int]:
    config = carregar()
    agora = agora or datetime.now(UTC)
    minutos = duracao_minutos if duracao_minutos is not None else config.jwt_duracao_minutos
    expira_em = agora + timedelta(minutes=minutos)
    token = jwt.encode(
        {
            "sub": str(usuario.id),
            "perfil": usuario.perfil,
            "iat": agora,
            "exp": expira_em,
            "iss": EMISSOR_JWT,
        },
        _segredo(),
        algorithm=ALGORITMO_JWT,
    )
    return token, minutos * 60


def id_do_token(token: str) -> int:
    try:
        dados = jwt.decode(
            token,
            _segredo(),
            algorithms=[ALGORITMO_JWT],
            issuer=EMISSOR_JWT,
        )
        usuario_id = int(dados["sub"])
        if usuario_id < 1:
            raise ValueError
        return usuario_id
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as erro:
        raise TokenInvalido from erro
