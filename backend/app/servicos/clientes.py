"""Regras de cadastro e persistência de clientes (GK-78)."""

import bcrypt
from psycopg.rows import class_row

from app.db import obter_pool
from app.esquemas.clientes import CadastroDeCliente, ClienteCadastrado

CUSTO_BCRYPT = 12


def gerar_hash(senha: str) -> str:
    """Transforma a senha em bcrypt antes de qualquer acesso ao banco."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=CUSTO_BCRYPT)).decode("ascii")


def cadastrar(dados: CadastroDeCliente) -> ClienteCadastrado:
    senha_hash = gerar_hash(dados.senha)
    with (
        obter_pool().connection() as conexao,
        conexao.cursor(row_factory=class_row(ClienteCadastrado)) as cursor,
    ):
        return cursor.execute(
            "insert into core.usuarios (nome, email, senha_hash, data_nascimento)"
            " values (%s, %s, %s, %s)"
            " returning id, nome, email, data_nascimento, perfil",
            (dados.nome, dados.email, senha_hash, dados.data_nascimento),
        ).fetchone()
