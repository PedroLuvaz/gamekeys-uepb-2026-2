"""Consulta pública de jogos ativos (GK-84), sem alterar dados do catálogo."""

from psycopg.rows import dict_row

from app.db import obter_pool
from app.esquemas.catalogo import DetalheDoJogo, Disponibilidade, JogoNoCatalogo, PaginaDeJogos

JOGOS_POR_PAGINA = 20

# Uma única consulta mantém o total e a página no mesmo retrato dos dados.
# O LEFT JOIN preserva o total mesmo com catálogo vazio ou página além da última.
CONSULTA_PAGINADA = """
    with pagina as (
        select id, nome, capa_url, preco, chaves_disponiveis
        from catalogo.jogos
        where ativo
        order by nome, id
        limit %s offset %s
    )
    select pagina.*, totais.total
    from (select count(*) as total from catalogo.jogos where ativo) as totais
    left join pagina on true
    order by pagina.nome, pagina.id
"""


def disponibilidade_do_jogo(chaves_disponiveis: int) -> Disponibilidade:
    """Regra da Sprint 1; reutilizar na consulta de detalhe da GK-10."""
    return Disponibilidade.DISPONIVEL if chaves_disponiveis > 0 else Disponibilidade.ESGOTADO


def listar_jogos(pagina: int = 1) -> PaginaDeJogos:
    deslocamento = (pagina - 1) * JOGOS_POR_PAGINA
    with obter_pool().connection() as conexao, conexao.cursor(row_factory=dict_row) as cursor:
        cursor.execute(CONSULTA_PAGINADA, (JOGOS_POR_PAGINA, deslocamento))
        linhas = cursor.fetchall()

    total = linhas[0]["total"]
    itens = [
        JogoNoCatalogo(
            id=linha["id"],
            nome=linha["nome"],
            capa_url=linha["capa_url"],
            preco=linha["preco"],
            disponibilidade=disponibilidade_do_jogo(linha["chaves_disponiveis"]),
        )
        for linha in linhas
        if linha["id"] is not None
    ]
    return PaginaDeJogos(
        itens=itens,
        pagina=pagina,
        por_pagina=JOGOS_POR_PAGINA,
        total=total,
        total_paginas=(total + JOGOS_POR_PAGINA - 1) // JOGOS_POR_PAGINA,
    )


def consultar_jogo(jogo_id: int) -> DetalheDoJogo | None:
    """Reutiliza os dados e a disponibilidade do catálogo, sem expor jogos inativos."""
    with obter_pool().connection() as conexao, conexao.cursor(row_factory=dict_row) as cursor:
        linha = cursor.execute(
            "select j.id, j.nome, j.capa_url, j.preco, j.chaves_disponiveis,"
            " j.descricao, c.nome as genero, j.plataforma, j.classificacao"
            " from catalogo.jogos j join catalogo.categorias c on c.id = j.categoria_id"
            " where j.id = %s and j.ativo",
            (jogo_id,),
        ).fetchone()
    if linha is None:
        return None
    return DetalheDoJogo(
        id=linha["id"],
        nome=linha["nome"],
        capa_url=linha["capa_url"],
        preco=linha["preco"],
        disponibilidade=disponibilidade_do_jogo(linha["chaves_disponiveis"]),
        descricao=linha["descricao"],
        genero=linha["genero"],
        plataforma=linha["plataforma"],
        classificacao=linha["classificacao"],
    )
