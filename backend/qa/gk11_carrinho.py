"""Fixtures e conferência do E2E da GK-11, exclusivamente em PostgreSQL local de testes.

Não cria schema nem migra o banco. Cada execução usa dados fictícios com UUID e
remove somente esses registros. A URL nunca é retornada ao navegador.
"""

import argparse
import json
import os
import re
import sys
from datetime import UTC, date, datetime
from uuid import uuid4

import bcrypt
import psycopg

from qa.gk110_concorrencia import validar_url_local

SENHA_FICTICIA = "qa-carrinho-local-123"


def _url() -> str:
    return validar_url_local(os.getenv("TEST_DATABASE_URL", ""))


def _identidade(dados: dict) -> tuple[str, list[str]]:
    chave = dados.get("chave", "")
    if not isinstance(chave, str) or not re.fullmatch(r"[0-9a-f]{32}", chave):
        raise ValueError("Identificador de fixture inválido")
    emails = [f"qa-gk11-{perfil}-{chave}@example.com" for perfil in ("adulto", "menor")]
    return chave, emails


def preparar() -> dict:
    url = _url()  # Validar antes de qualquer conexão ou gravação.
    chave, emails = _identidade({"chave": uuid4().hex})
    hoje = datetime.now(UTC).date()
    senha_hash = bcrypt.hashpw(SENHA_FICTICIA.encode(), bcrypt.gensalt(rounds=12)).decode()
    with psycopg.connect(url, connect_timeout=5) as conexao:
        categoria_id = conexao.execute(
            "insert into catalogo.categorias (nome, slug) values (%s, %s) returning id",
            ("Categoria QA " + chave, "qa-gk11-" + chave),
        ).fetchone()[0]
        jogo_id = conexao.execute(
            "insert into catalogo.jogos (categoria_id, slug, nome, descricao, preco, plataforma,"
            " classificacao, chaves_disponiveis) values (%s, %s, 'Jogo QA Carrinho',"
            " 'Jogo fictício para teste do carrinho.', 19.90, 'PC', '18', 3) returning id",
            (categoria_id, "qa-gk11-" + chave),
        ).fetchone()[0]
        for email, nascimento in zip(
            emails, (date(1990, 1, 1), date(hoje.year - 10, 1, 1)), strict=True
        ):
            conexao.execute(
                "insert into core.usuarios (nome, email, senha_hash, data_nascimento)"
                " values ('Cliente QA Carrinho', %s, %s, %s)",
                (email, senha_hash, nascimento),
            )
    return {
        "chave": chave,
        "jogoId": jogo_id,
        "emailAdulto": emails[0],
        "emailMenor": emails[1],
        "senha": SENHA_FICTICIA,
    }


def estado(dados: dict) -> dict:
    url = _url()
    chave, emails = _identidade(dados)
    perfil = dados.get("perfil", "adulto")
    if perfil not in ("adulto", "menor"):
        raise ValueError("Perfil de fixture inválido")
    with psycopg.connect(url, connect_timeout=5) as conexao:
        conexao.read_only = True
        linhas, quantidade, subtotal = conexao.execute(
            "select count(i.jogo_id), coalesce(sum(i.quantidade),0),"
            " coalesce(sum(i.quantidade * j.preco),0) from core.usuarios u"
            " left join vendas.carrinhos c on c.usuario_id=u.id"
            " left join vendas.itens_carrinho i on i.carrinho_id=c.id"
            " left join catalogo.jogos j on j.id=i.jogo_id where u.email=%s",
            (emails[0 if perfil == "adulto" else 1],),
        ).fetchone()
        estoque = conexao.execute(
            "select chaves_disponiveis from catalogo.jogos where slug=%s",
            ("qa-gk11-" + chave,),
        ).fetchone()[0]
    return {
        "linhas": linhas,
        "quantidade": int(quantidade),
        "subtotal": str(subtotal),
        "estoque": estoque,
    }


def limpar(dados: dict) -> dict:
    url = _url()
    chave, emails = _identidade(dados)
    with psycopg.connect(url, connect_timeout=5) as conexao:
        conexao.execute(
            "delete from vendas.carrinhos where usuario_id in"
            " (select id from core.usuarios where email=any(%s))",
            (emails,),
        )
        conexao.execute("delete from core.usuarios where email=any(%s)", (emails,))
        conexao.execute("delete from catalogo.jogos where slug=%s", ("qa-gk11-" + chave,))
        conexao.execute("delete from catalogo.categorias where slug=%s", ("qa-gk11-" + chave,))
    return {"limpo": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("acao", choices=("preparar", "estado", "limpar"))
    args = parser.parse_args()
    try:
        dados = json.load(sys.stdin)
        resultado = (
            preparar()
            if args.acao == "preparar"
            else {"estado": estado, "limpar": limpar}[args.acao](dados)
        )
        print(json.dumps(resultado, ensure_ascii=False))
    except Exception as erro:
        # Não deixar URLs, códigos de ativação ou credenciais em traceback do Cypress.
        print(
            json.dumps(
                {
                    "erro": "Use PostgreSQL local gamekeys_teste para a fixture de carrinho.",
                    "tipo": type(erro).__name__,
                }
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
