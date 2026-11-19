"""Dados fictícios da GK-14, exclusivamente no PostgreSQL local gamekeys_teste."""

import argparse
import json
import sys

import psycopg

from qa import gk11_carrinho as carrinho


def preparar() -> dict:
    dados = carrinho.preparar()  # Valida o alvo local antes de gravar qualquer registro.
    chave, emails = carrinho._identidade(dados)
    try:
        with psycopg.connect(carrinho._url(), connect_timeout=5) as conexao:
            # Administrador fictício sem login; nunca instala uma conta de suporte ativa.
            administrador = conexao.execute(
                "insert into core.usuarios"
                " (nome,email,senha_hash,data_nascimento,perfil,ativo)"
                " select 'Administrador QA Checkout',%s,senha_hash,'1990-01-01',"
                " 'administrador',false from core.usuarios where email=%s returning id",
                (f"qa-gk14-admin-{chave}@example.com", emails[0]),
            ).fetchone()[0]
            # A fixture do carrinho usa contador legado; aqui o estoque vem de chaves físicas.
            conexao.execute(
                "update catalogo.jogos set chaves_disponiveis=0 where slug=%s",
                ("qa-gk11-" + chave,),
            )
            for numero in range(3):
                conexao.execute(
                    "insert into catalogo.chaves (jogo_id,codigo,cadastrada_por) values (%s,%s,%s)",
                    (dados["jogoId"], f"FICTICIA-GK14-{chave}-{numero}", administrador),
                )
    except Exception:
        carrinho.limpar(dados)
        raise
    return dados


def estado(dados: dict) -> dict:
    chave, emails = carrinho._identidade(dados)
    with psycopg.connect(carrinho._url(), connect_timeout=5) as conexao:
        conexao.read_only = True
        pedidos, total = conexao.execute(
            "select count(*),coalesce(sum(valor_total),0) from vendas.pedidos"
            " where usuario_id in (select id from core.usuarios where email=any(%s))",
            (emails,),
        ).fetchone()
        reservadas, vendidas = conexao.execute(
            "select count(*) filter (where c.status='reservada'),"
            " count(*) filter (where c.status='vendida') from catalogo.chaves c"
            " join catalogo.jogos j on j.id=c.jogo_id where j.slug=%s",
            ("qa-gk11-" + chave,),
        ).fetchone()
        pagamentos, valor_pago = conexao.execute(
            "select count(*),coalesce(sum(g.valor),0) from vendas.pagamentos g"
            " join vendas.pedidos p on p.id=g.pedido_id"
            " join core.usuarios u on u.id=p.usuario_id where u.email=any(%s)",
            (emails,),
        ).fetchone()
    return {
        **carrinho.estado(dados),
        "pedidos": pedidos,
        "totalPedidos": str(total),
        "reservadas": reservadas,
        "vendidas": vendidas,
        "pagamentos": pagamentos,
        "valorPago": str(valor_pago),
    }


def alterar_preco(dados: dict) -> dict:
    chave, _ = carrinho._identidade(dados)
    with psycopg.connect(carrinho._url(), connect_timeout=5) as conexao:
        # Altera somente o jogo desta fixture, para um valor fixo e fictício.
        conexao.execute(
            "update catalogo.jogos set preco=70.00 where slug=%s", ("qa-gk11-" + chave,)
        )
    return {"alterado": True}


def limpar(dados: dict) -> dict:
    chave, emails = carrinho._identidade(dados)
    with psycopg.connect(carrinho._url(), connect_timeout=5) as conexao:
        for tabela in ("pagamentos", "itens_pedido"):
            # Nomes vêm apenas da constante interna; valores sempre parametrizados.
            conexao.execute(
                f"delete from vendas.{tabela} where pedido_id in"
                " (select p.id from vendas.pedidos p join core.usuarios u"
                " on u.id=p.usuario_id where u.email=any(%s))",
                (emails,),
            )
        conexao.execute(
            "delete from vendas.pedidos where usuario_id in"
            " (select id from core.usuarios where email=any(%s))",
            (emails,),
        )
        conexao.execute(
            "delete from catalogo.chaves where jogo_id in"
            " (select id from catalogo.jogos where slug=%s)",
            ("qa-gk11-" + chave,),
        )
        conexao.execute(
            "delete from core.usuarios where email=%s",
            (f"qa-gk14-admin-{chave}@example.com",),
        )
    return carrinho.limpar(dados)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    acoes = {"estado": estado, "alterar-preco": alterar_preco, "limpar": limpar}
    parser.add_argument("acao", choices=("preparar", *acoes))
    args = parser.parse_args()
    try:
        dados = json.load(sys.stdin)
        resultado = preparar() if args.acao == "preparar" else acoes[args.acao](dados)
        print(json.dumps(resultado, ensure_ascii=False))
    except Exception as erro:
        # Não incluir URL, dados de login nem códigos em relatórios do navegador.
        print(
            json.dumps(
                {
                    "erro": "Fixture GK-14 exige PostgreSQL local gamekeys_teste.",
                    "tipo": type(erro).__name__,
                }
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
