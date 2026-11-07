"""GK-118: API/JWT/PostgreSQL reais, inclusive concorrência, só em banco local isolado."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime
from decimal import Decimal
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg_pool import ConnectionPool

from app.main import criar_app
from app.servicos import autenticacao, carrinho, clientes

HASH_TESTE = "$2b$12$" + "b" * 53


@pytest.fixture
def ambiente(banco, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "segredo-local-gk118-com-mais-de-trinta-e-dois-bytes")
    usuarios, jogos = [], []
    with ConnectionPool(
        banco, min_size=1, max_size=5, timeout=10, kwargs={"prepare_threshold": None}
    ) as pool:
        pool.wait(timeout=15)
        for servico in (autenticacao, carrinho, clientes):
            monkeypatch.setattr(servico, "obter_pool", lambda: pool)
        with pool.connection() as conexao:
            categoria = conexao.execute(
                "insert into catalogo.categorias (nome, slug) values (%s, %s) returning id",
                ("Categoria " + uuid4().hex[:12], "teste-" + uuid4().hex),
            ).fetchone()[0]

        def conta(nascimento=date(1990, 1, 1), perfil="cliente", senha_hash=HASH_TESTE):
            email = uuid4().hex + "@example.com"
            with pool.connection() as conexao:
                usuario_id = conexao.execute(
                    "insert into core.usuarios (nome, email, senha_hash, data_nascimento, perfil)"
                    " values ('Cliente Carrinho', %s, %s, %s, %s) returning id",
                    (email, senha_hash, nascimento, perfil),
                ).fetchone()[0]
            usuarios.append(usuario_id)
            usuario = autenticacao.UsuarioPersistido(
                id=usuario_id,
                nome="Cliente Carrinho",
                email=email,
                senha_hash=senha_hash,
                data_nascimento=nascimento,
                perfil=perfil,
                ativo=True,
            )
            token, _ = autenticacao.criar_token(usuario)
            return usuario, {"Authorization": "Bearer " + token}

        def jogo(estoque=5, classificacao="L", ativo=True, preco=Decimal("19.90")):
            with pool.connection() as conexao:
                jogo_id = conexao.execute(
                    "insert into catalogo.jogos"
                    " (categoria_id, slug, nome, descricao, preco, plataforma, classificacao,"
                    " chaves_disponiveis, ativo) values (%s, %s, 'Jogo Carrinho', 'Teste',"
                    " %s, 'PC', %s, %s, %s) returning id",
                    (categoria, "jogo-" + uuid4().hex, preco, classificacao, estoque, ativo),
                ).fetchone()[0]
            jogos.append(jogo_id)
            return jogo_id

        def estado(usuario_id):
            with pool.connection() as conexao:
                return conexao.execute(
                    "select c.id, c.atualizado_em, i.jogo_id, i.quantidade from vendas.carrinhos c"
                    " left join vendas.itens_carrinho i on i.carrinho_id = c.id"
                    " where c.usuario_id = %s order by i.jogo_id",
                    (usuario_id,),
                ).fetchall()

        with TestClient(criar_app()) as api:
            try:
                yield SimpleNamespace(pool=pool, api=api, conta=conta, jogo=jogo, estado=estado)
            finally:
                with pool.connection() as conexao:
                    conexao.execute(
                        "delete from vendas.carrinhos where usuario_id = any(%s)", (usuarios,)
                    )
                    conexao.execute("delete from core.usuarios where id = any(%s)", (usuarios,))
                    conexao.execute("delete from catalogo.jogos where id = any(%s)", (jogos,))
                    conexao.execute("delete from catalogo.categorias where id = %s", (categoria,))


def adicionar(ambiente, headers, jogo_id, quantidade=1):
    return ambiente.api.post(
        "/carrinho/itens", headers=headers, json={"jogo_id": jogo_id, "quantidade": quantidade}
    )


def consultar(ambiente, headers):
    return ambiente.api.get("/carrinho", headers=headers)


def alterar(ambiente, headers, jogo_id, quantidade):
    return ambiente.api.patch(
        f"/carrinho/itens/{jogo_id}", headers=headers, json={"quantidade": quantidade}
    )


def remover(ambiente, headers, jogo_id):
    return ambiente.api.delete(f"/carrinho/itens/{jogo_id}", headers=headers)


def test_login_real_cria_item_persistente_e_nao_consume_estoque(ambiente):
    usuario, _ = ambiente.conta(senha_hash=clientes.gerar_hash("senha-local-teste"))
    login = ambiente.api.post(
        "/auth/login", json={"email": usuario.email, "senha": "senha-local-teste"}
    )
    assert login.status_code == 200
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    jogo = ambiente.jogo()

    resposta = adicionar(ambiente, headers, jogo, 3)

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados == {
        "carrinho_id": ambiente.estado(usuario.id)[0][0],
        "jogo_id": jogo,
        "nome": "Jogo Carrinho",
        "quantidade": 3,
        "preco_unitario": "19.90",
        "subtotal": "59.70",
    }
    assert ambiente.estado(usuario.id)[0][2:] == (jogo, 3)
    with ambiente.pool.connection() as conexao:
        assert (
            conexao.execute(
                "select chaves_disponiveis from catalogo.jogos where id=%s", (jogo,)
            ).fetchone()[0]
            == 5
        )


def test_repetir_jogo_soma_quantidade_sem_duplicar_linha(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo()
    assert adicionar(ambiente, headers, jogo, 2).status_code == 200

    resposta = adicionar(ambiente, headers, jogo, 3)

    assert resposta.status_code == 200
    assert resposta.json()["quantidade"] == 5
    assert resposta.json()["subtotal"] == "99.50"
    assert len(ambiente.estado(usuario.id)) == 1
    assert ambiente.estado(usuario.id)[0][3] == 5


@pytest.mark.parametrize("estoque,quantidade", [(0, 1), (5, 6)])
def test_estoque_insuficiente_na_primeira_adicao_nao_deixa_carrinho_vazio(
    ambiente, estoque, quantidade
):
    usuario, headers = ambiente.conta()
    resposta = adicionar(ambiente, headers, ambiente.jogo(estoque=estoque), quantidade)

    assert resposta.status_code == 409
    assert ambiente.estado(usuario.id) == []


def test_excesso_acumulado_desfaz_tambem_atualizacao_do_carrinho(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo()
    assert adicionar(ambiente, headers, jogo, 3).status_code == 200
    antes = ambiente.estado(usuario.id)

    resposta = adicionar(ambiente, headers, jogo, 3)

    assert resposta.status_code == 409
    assert ambiente.estado(usuario.id) == antes


@pytest.mark.parametrize("inativo", [False, True])
def test_inativo_e_inexistente_nao_criam_carrinho_nem_expoem_dados(ambiente, inativo):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo(ativo=False) if inativo else 9223372036854775807
    resposta = adicionar(ambiente, headers, jogo)

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Jogo não encontrado."}
    assert ambiente.estado(usuario.id) == []


@pytest.mark.parametrize(
    "anos,classificacao,status", [(17, "18", 403), (18, "18", 200), (5, "L", 200)]
)
def test_classificacao_usa_idade_real_do_cliente(ambiente, anos, classificacao, status):
    hoje = datetime.now(UTC).date()
    nascimento = date(hoje.year - anos, hoje.month, min(hoje.day, 28))
    usuario, headers = ambiente.conta(nascimento=nascimento)
    resposta = adicionar(ambiente, headers, ambiente.jogo(classificacao=classificacao))

    assert resposta.status_code == status
    if status == 403:
        assert resposta.json() == {
            "detail": "Sua idade não permite adicionar este jogo ao carrinho."
        }
        assert ambiente.estado(usuario.id) == []


def test_administrador_nao_pode_comprar_como_cliente(ambiente):
    usuario, headers = ambiente.conta(perfil="administrador")
    assert adicionar(ambiente, headers, ambiente.jogo()).status_code == 403
    assert ambiente.estado(usuario.id) == []


def test_token_valido_de_usuario_desativado_e_recusado(ambiente):
    usuario, headers = ambiente.conta()
    with ambiente.pool.connection() as conexao:
        conexao.execute("update core.usuarios set ativo=false where id=%s", (usuario.id,))

    assert adicionar(ambiente, headers, ambiente.jogo()).status_code == 401
    assert ambiente.estado(usuario.id) == []


def test_clientes_nao_escrevem_no_carrinho_um_do_outro_e_nao_reservam_a_ultima_chave(ambiente):
    a, headers_a = ambiente.conta()
    b, headers_b = ambiente.conta()
    jogo = ambiente.jogo(estoque=1)
    ra = adicionar(ambiente, headers_a, jogo)
    rb = adicionar(ambiente, headers_b, jogo)

    assert ra.status_code == rb.status_code == 200
    assert ra.json()["carrinho_id"] != rb.json()["carrinho_id"]
    assert ambiente.estado(a.id)[0][3] == ambiente.estado(b.id)[0][3] == 1
    adulterada = ambiente.api.post(
        "/carrinho/itens", headers=headers_a, json={"jogo_id": jogo, "usuario_id": b.id}
    )
    assert adulterada.status_code == 422


def test_soma_acima_do_integer_e_recusada_sem_overflow(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo(estoque=2147483647)
    assert adicionar(ambiente, headers, jogo, 2147483647).status_code == 200
    antes = ambiente.estado(usuario.id)

    assert adicionar(ambiente, headers, jogo).status_code == 409
    assert ambiente.estado(usuario.id) == antes


def test_revalida_estoque_reduzido_depois_da_primeira_adicao(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo()
    assert adicionar(ambiente, headers, jogo, 2).status_code == 200
    with ambiente.pool.connection() as conexao:
        conexao.execute("update catalogo.jogos set chaves_disponiveis=1 where id=%s", (jogo,))

    assert adicionar(ambiente, headers, jogo).status_code == 409
    assert ambiente.estado(usuario.id)[0][3] == 2


@pytest.mark.concorrencia
def test_vinte_adicoes_simultaneas_na_primeira_criacao_preservam_limite_e_quantidade(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo(estoque=7)
    barreira = Barrier(20)

    def requisitar(_):
        barreira.wait(timeout=15)
        return adicionar(ambiente, headers, jogo)

    with ThreadPoolExecutor(max_workers=20) as executor:
        respostas = list(executor.map(requisitar, range(20)))

    assert sorted(r.status_code for r in respostas) == [200] * 7 + [409] * 13
    assert sorted(r.json()["quantidade"] for r in respostas if r.status_code == 200) == list(
        range(1, 8)
    )
    assert len(ambiente.estado(usuario.id)) == 1
    assert ambiente.estado(usuario.id)[0][3] == 7


@pytest.mark.concorrencia
def test_primeira_criacao_com_dois_jogos_concorrentes_cria_um_carrinho(ambiente):
    usuario, headers = ambiente.conta()
    jogos = [ambiente.jogo(), ambiente.jogo()]
    barreira = Barrier(2)

    def requisitar(jogo):
        barreira.wait(timeout=10)
        return adicionar(ambiente, headers, jogo)

    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(requisitar, jogos))

    assert [r.status_code for r in respostas] == [200, 200]
    assert len({r.json()["carrinho_id"] for r in respostas}) == 1
    assert len(ambiente.estado(usuario.id)) == 2


def test_migracao_equipe_tem_dml_mas_nao_ddl(ambiente):
    usuario, _ = ambiente.conta()
    jogo = ambiente.jogo()
    with ambiente.pool.connection() as conexao, conexao.transaction():
        conexao.execute("set local role gamekeys_equipe")
        carrinho_id = carrinho.bloquear_carrinho(conexao, usuario.id)
        conexao.execute(
            "insert into vendas.itens_carrinho (carrinho_id,jogo_id) values (%s,%s)",
            (carrinho_id, jogo),
        )
        assert (
            conexao.execute(
                "select quantidade from vendas.itens_carrinho where carrinho_id=%s", (carrinho_id,)
            ).fetchone()[0]
            == 1
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conexao.transaction():
            conexao.execute("create table vendas.tabela_nao_permitida (id int)")


def test_timeout_de_bloqueio_desfaz_a_operacao_e_pool_continua_utilizavel(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo()
    with ambiente.pool.connection() as controle:
        controle.execute("select id from catalogo.jogos where id=%s for update", (jogo,))
        resposta = adicionar(ambiente, headers, jogo)

    assert resposta.status_code == 503
    assert resposta.json() == {
        "detail": "Carrinho temporariamente indisponível. Tente novamente em instantes."
    }
    assert ambiente.estado(usuario.id) == []
    assert adicionar(ambiente, headers, jogo).status_code == 200


def test_carrinho_bloqueado_nao_impede_outro_cliente_de_adicionar(ambiente):
    a, headers_a = ambiente.conta()
    b, headers_b = ambiente.conta()
    jogo = ambiente.jogo()
    resposta_a = adicionar(ambiente, headers_a, jogo)
    with ambiente.pool.connection() as controle:
        controle.execute(
            "select id from vendas.carrinhos where id=%s for update",
            (resposta_a.json()["carrinho_id"],),
        )
        resposta_b = adicionar(ambiente, headers_b, jogo)

    assert resposta_b.status_code == 200
    assert resposta_a.json()["carrinho_id"] != resposta_b.json()["carrinho_id"]
    assert ambiente.estado(a.id)[0][3] == ambiente.estado(b.id)[0][3] == 1


def test_falha_apos_insert_do_item_desfaz_toda_a_transacao(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo()
    with ambiente.pool.connection() as conexao:
        conexao.execute(
            "create function vendas.falha_controlada_gk118() returns trigger language plpgsql"
            " as $$ begin raise exception 'falha local controlada'; end; $$;"
            " create trigger falha_controlada_gk118 after insert on vendas.itens_carrinho"
            " for each row execute function vendas.falha_controlada_gk118()"
        )
    try:
        resposta = adicionar(ambiente, headers, jogo)
        assert resposta.status_code == 503
        assert "falha local controlada" not in resposta.text
        assert ambiente.estado(usuario.id) == []
    finally:
        with ambiente.pool.connection() as conexao:
            conexao.execute("drop trigger falha_controlada_gk118 on vendas.itens_carrinho")
            conexao.execute("drop function vendas.falha_controlada_gk118()")
    assert adicionar(ambiente, headers, jogo).status_code == 200


def test_consulta_carrinho_vazio_sem_criar_registro(ambiente):
    usuario, headers = ambiente.conta()

    resposta = consultar(ambiente, headers)

    assert resposta.status_code == 200
    assert resposta.json() == {"itens": [], "total": "0.00"}
    assert ambiente.estado(usuario.id) == []


def test_alteracao_substitui_quantidade_e_recalcula_subtotal_total_com_decimal(ambiente):
    usuario, headers = ambiente.conta()
    jogo_a = ambiente.jogo(estoque=10, preco=Decimal("0.10"))
    jogo_b = ambiente.jogo(estoque=10, preco=Decimal("0.20"))
    assert adicionar(ambiente, headers, jogo_a, 1).status_code == 200
    assert adicionar(ambiente, headers, jogo_b, 1).status_code == 200

    resposta = alterar(ambiente, headers, jogo_a, 3)

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total"] == "0.50"
    itens = {item["jogo_id"]: item for item in dados["itens"]}
    assert itens[jogo_a]["quantidade"] == 3
    assert itens[jogo_a]["subtotal"] == "0.30"
    assert itens[jogo_b]["subtotal"] == "0.20"
    assert {linha[2]: linha[3] for linha in ambiente.estado(usuario.id)} == {
        jogo_a: 3,
        jogo_b: 1,
    }


def test_alteracao_acima_do_estoque_e_recusada_sem_mudanca_parcial(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo(estoque=3)
    assert adicionar(ambiente, headers, jogo, 2).status_code == 200
    antes = ambiente.estado(usuario.id)

    resposta = alterar(ambiente, headers, jogo, 4)

    assert resposta.status_code == 409
    assert resposta.json() == {"detail": "Estoque insuficiente para a quantidade solicitada."}
    assert ambiente.estado(usuario.id) == antes


def test_remocao_exclui_item_e_recalcula_total(ambiente):
    usuario, headers = ambiente.conta()
    jogo_a = ambiente.jogo(preco=Decimal("19.90"))
    jogo_b = ambiente.jogo(preco=Decimal("10.05"))
    assert adicionar(ambiente, headers, jogo_a, 2).status_code == 200
    assert adicionar(ambiente, headers, jogo_b).status_code == 200

    resposta = remover(ambiente, headers, jogo_a)

    assert resposta.status_code == 200
    assert resposta.json()["total"] == "10.05"
    assert [item["jogo_id"] for item in resposta.json()["itens"]] == [jogo_b]
    assert [(linha[2], linha[3]) for linha in ambiente.estado(usuario.id)] == [(jogo_b, 1)]


def test_cliente_nao_altera_nem_remove_item_do_outro(ambiente):
    a, headers_a = ambiente.conta()
    b, headers_b = ambiente.conta()
    jogo = ambiente.jogo()
    assert adicionar(ambiente, headers_b, jogo, 2).status_code == 200
    estado_b = ambiente.estado(b.id)

    assert alterar(ambiente, headers_a, jogo, 3).status_code == 404
    assert remover(ambiente, headers_a, jogo).status_code == 404
    assert ambiente.estado(a.id) == []
    assert ambiente.estado(b.id) == estado_b
    assert consultar(ambiente, headers_a).json() == {"itens": [], "total": "0.00"}
    assert consultar(ambiente, headers_b).json()["itens"][0]["quantidade"] == 2


def test_falha_depois_do_update_desfaz_quantidade_e_total(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo()
    assert adicionar(ambiente, headers, jogo, 2).status_code == 200
    antes = ambiente.estado(usuario.id)
    with ambiente.pool.connection() as conexao:
        conexao.execute(
            "create function vendas.falha_controlada_gk12() returns trigger language plpgsql"
            " as $$ begin raise exception 'falha local controlada gk12'; end; $$;"
            " create trigger falha_controlada_gk12 after update on vendas.itens_carrinho"
            " for each row execute function vendas.falha_controlada_gk12()"
        )
    try:
        resposta = alterar(ambiente, headers, jogo, 3)
        assert resposta.status_code == 503
        assert "falha local controlada" not in resposta.text
        assert ambiente.estado(usuario.id) == antes
        assert consultar(ambiente, headers).json()["total"] == "39.80"
    finally:
        with ambiente.pool.connection() as conexao:
            conexao.execute("drop trigger falha_controlada_gk12 on vendas.itens_carrinho")
            conexao.execute("drop function vendas.falha_controlada_gk12()")


@pytest.mark.concorrencia
def test_alteracoes_concorrentes_ficam_serializadas_e_consistentes(ambiente):
    usuario, headers = ambiente.conta()
    jogo = ambiente.jogo(estoque=10, preco=Decimal("7.25"))
    assert adicionar(ambiente, headers, jogo).status_code == 200
    barreira = Barrier(2)

    def requisitar(quantidade):
        barreira.wait(timeout=10)
        return alterar(ambiente, headers, jogo, quantidade)

    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(requisitar, [4, 7]))

    assert [resposta.status_code for resposta in respostas] == [200, 200]
    final = consultar(ambiente, headers).json()
    assert final["itens"][0]["quantidade"] in {4, 7}
    assert final["total"] in {"29.00", "50.75"}
    assert final["total"] == final["itens"][0]["subtotal"]
    assert ambiente.estado(usuario.id)[0][3] == final["itens"][0]["quantidade"]
