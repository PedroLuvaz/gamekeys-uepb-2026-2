"""GK-124: reserva pela API/JWT/PostgreSQL reais, exclusivamente em gamekeys_teste local."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from test_carrinho_banco import adicionar, ambiente  # noqa: F401

from app.migrar import aplicar_carga
from app.servicos import carrinho, reservas
from app.servicos.reserva_chaves import reservar_chaves


@pytest.fixture
def reserva(ambiente, monkeypatch):  # noqa: F811 (fixture reutilizada do carrinho)
    monkeypatch.setattr(reservas, "obter_pool", lambda: ambiente.pool)
    usuarios, jogos = [], []

    def conta(**opcoes):
        usuario, headers = ambiente.conta(**opcoes)
        usuarios.append(usuario.id)
        return usuario, headers

    administrador, _ = conta(perfil="administrador")

    def jogo(estoque=3, **opcoes):
        jogo_id = ambiente.jogo(estoque=0, **opcoes)
        jogos.append(jogo_id)
        with ambiente.pool.connection() as c:
            c.execute(
                "insert into catalogo.chaves (jogo_id, codigo, cadastrada_por)"
                " select %s, %s || n, %s from generate_series(1,%s) n",
                (jogo_id, "QA-SEM-VALOR-" + uuid4().hex, administrador.id, estoque),
            )
        return jogo_id

    def estado():
        with ambiente.pool.connection() as c:
            return {
                "pedidos": c.execute(
                    "select count(*) from vendas.pedidos where usuario_id=any(%s)", (usuarios,)
                ).fetchone()[0],
                "reservadas": c.execute(
                    "select count(*) from catalogo.chaves"
                    " where jogo_id=any(%s) and status='reservada'",
                    (jogos,),
                ).fetchone()[0],
                "duplicadas": c.execute(
                    "select count(*) from (select chave_id from vendas.itens_pedido"
                    " group by chave_id having count(*)>1) d"
                ).fetchone()[0],
                "estoques": c.execute(
                    "select j.chaves_disponiveis, (select count(*)"
                    " from catalogo.chaves c where c.jogo_id=j.id and c.status='disponivel')"
                    " from catalogo.jogos j where j.id=any(%s) order by id",
                    (jogos,),
                ).fetchall(),
            }

    try:
        yield SimpleNamespace(
            **vars(ambiente),
            cliente=conta,
            jogo_fisico=jogo,
            conferir=estado,
            administrador=administrador,
        )
    finally:
        with ambiente.pool.connection() as c:
            c.execute(
                "delete from vendas.itens_pedido where pedido_id in"
                " (select id from vendas.pedidos where usuario_id=any(%s))",
                (usuarios,),
            )
            c.execute("delete from vendas.pedidos where usuario_id=any(%s)", (usuarios,))
            # Testes de estoque adulterado não podem prejudicar a própria limpeza.
            c.execute(
                "update catalogo.jogos j set chaves_disponiveis=(select count(*)"
                " from catalogo.chaves c where c.jogo_id=j.id and c.status='disponivel')"
                " where j.id=any(%s)",
                (jogos,),
            )
            c.execute("delete from catalogo.chaves where jogo_id=any(%s)", (jogos,))


def reservar(reserva, headers, chave=None):
    return reserva.api.post(
        "/pedidos/reservas", headers=headers, json={"chave_idempotencia": str(chave or uuid4())}
    )


def test_reserva_integral_persiste_precos_esvazia_carrinho_e_sincroniza_catalogo(reserva):
    _, headers = reserva.cliente()
    a, b = reserva.jogo_fisico(3), reserva.jogo_fisico(2, preco=Decimal("7.25"))
    assert adicionar(reserva, headers, a, 2).status_code == 200
    assert adicionar(reserva, headers, b).status_code == 200
    resposta = reservar(reserva, headers)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["status"] == "aguardando_pagamento"
    assert dados["valor_total"] == "47.05"
    assert [i["quantidade"] for i in dados["itens"]] == [2, 1]
    assert reserva.api.get("/carrinho", headers=headers).json()["itens"] == []
    assert reserva.conferir() == {
        "pedidos": 1,
        "reservadas": 3,
        "duplicadas": 0,
        "estoques": [(1, 1), (1, 1)],
    }
    assert all("codigo" not in i and "chave_id" not in i for i in dados["itens"])
    assert "QA-SEM-VALOR" not in resposta.text


def test_repeticao_recupera_pedido_sem_nova_reserva_nem_apagar_novo_carrinho(reserva):
    _, headers = reserva.cliente()
    jogo, chave = reserva.jogo_fisico(3), uuid4()
    adicionar(reserva, headers, jogo)
    primeira = reservar(reserva, headers, chave)
    assert primeira.status_code == 200
    adicionar(reserva, headers, jogo)
    with reserva.pool.connection() as c:
        c.execute("update catalogo.jogos set preco=99.99 where id=%s", (jogo,))
    segunda = reservar(reserva, headers, chave)
    assert segunda.json() == primeira.json()
    assert reserva.api.get("/carrinho", headers=headers).json()["itens"][0]["quantidade"] == 1
    assert reserva.conferir()["pedidos"] == reserva.conferir()["reservadas"] == 1


def test_mesmo_uuid_de_outro_cliente_nao_acessa_pedido_alheio(reserva):
    _, h1 = reserva.cliente()
    _, h2 = reserva.cliente()
    jogo, chave = reserva.jogo_fisico(2), uuid4()
    adicionar(reserva, h1, jogo)
    r1 = reservar(reserva, h1, chave)
    assert reservar(reserva, h2, chave).status_code == 409  # carrinho vazio do segundo cliente
    adicionar(reserva, h2, jogo)
    r2 = reservar(reserva, h2, chave)
    assert r1.json()["pedido_id"] != r2.json()["pedido_id"]
    assert reserva.conferir()["pedidos"] == 2


@pytest.mark.parametrize(
    "motivo,status",
    [
        ("vazio", 409),
        ("idade", 403),
        ("inativo", 404),
        ("estoque", 409),
        ("contador_sem_chave", 409),
    ],
)
def test_recusas_nao_deixam_pedido_e_preservam_carrinho(reserva, motivo, status):
    _, headers = reserva.cliente(
        nascimento=date(2016, 1, 1) if motivo == "idade" else date(1990, 1, 1)
    )
    jogo = reserva.jogo_fisico(1)
    if motivo != "vazio":
        assert adicionar(reserva, headers, jogo).status_code == 200
    with reserva.pool.connection() as c:
        if motivo == "idade":
            c.execute("update catalogo.jogos set classificacao='18' where id=%s", (jogo,))
        if motivo == "inativo":
            c.execute("update catalogo.jogos set ativo=false where id=%s", (jogo,))
        if motivo in ("estoque", "contador_sem_chave"):
            c.execute("update catalogo.chaves set status='invalidada' where jogo_id=%s", (jogo,))
        if motivo == "contador_sem_chave":
            c.execute("update catalogo.jogos set chaves_disponiveis=1 where id=%s", (jogo,))
    assert reservar(reserva, headers).status_code == status
    assert reserva.conferir()["pedidos"] == reserva.conferir()["reservadas"] == 0
    assert len(reserva.api.get("/carrinho", headers=headers).json()["itens"]) == (motivo != "vazio")


def test_falta_no_segundo_jogo_desfaz_reserva_do_primeiro(reserva):
    _, headers = reserva.cliente()
    a, b = reserva.jogo_fisico(1), reserva.jogo_fisico(1)
    for j in (a, b):
        adicionar(reserva, headers, j)
    with reserva.pool.connection() as c:
        c.execute("update catalogo.chaves set status='invalidada' where jogo_id=%s", (b,))
        c.execute("update catalogo.jogos set chaves_disponiveis=1 where id=%s", (b,))
    assert reservar(reserva, headers).status_code == 409
    assert reserva.conferir()["pedidos"] == reserva.conferir()["reservadas"] == 0
    assert reserva.conferir()["estoques"][0] == (1, 1)
    assert len(reserva.api.get("/carrinho", headers=headers).json()["itens"]) == 2


def test_falha_apos_gravacao_dos_itens_faz_rollback_e_pool_continua_utilizavel(
    reserva, monkeypatch
):
    _, headers = reserva.cliente()
    jogo = reserva.jogo_fisico(1)
    adicionar(reserva, headers, jogo)
    consultar = reservas._consultar_pedido

    def falhar(*_):
        raise psycopg.OperationalError("falha forçada antes do commit")

    monkeypatch.setattr(reservas, "_consultar_pedido", falhar)
    assert reservar(reserva, headers).status_code == 503
    assert reserva.conferir() == {
        "pedidos": 0,
        "reservadas": 0,
        "duplicadas": 0,
        "estoques": [(1, 1)],
    }
    assert len(reserva.api.get("/carrinho", headers=headers).json()["itens"]) == 1
    monkeypatch.setattr(reservas, "_consultar_pedido", consultar)
    assert reservar(reserva, headers).status_code == 200


@pytest.mark.concorrencia
def test_vinte_clientes_disputam_ultima_chave_sem_venda_duplicada(reserva):
    jogo = reserva.jogo_fisico(1)
    headers = [reserva.cliente()[1] for _ in range(20)]
    for h in headers:
        assert adicionar(reserva, h, jogo).status_code == 200
    barreira = Barrier(20)

    def tentar(h):
        barreira.wait(timeout=15)
        return reservar(reserva, h).status_code

    with ThreadPoolExecutor(max_workers=20) as executor:
        respostas = list(executor.map(tentar, headers))
    assert respostas.count(200) == 1 and respostas.count(409) == 19
    assert reserva.conferir() == {
        "pedidos": 1,
        "reservadas": 1,
        "duplicadas": 0,
        "estoques": [(0, 0)],
    }


def test_requisicoes_concorrentes_mesma_idempotencia_criam_so_um_pedido(reserva):
    _, headers = reserva.cliente()
    jogo, chave = reserva.jogo_fisico(3), uuid4()
    adicionar(reserva, headers, jogo)
    with ThreadPoolExecutor(max_workers=5) as executor:
        respostas = list(executor.map(lambda _: reservar(reserva, headers, chave), range(5)))
    assert all(r.status_code == 200 for r in respostas)
    assert len({r.json()["pedido_id"] for r in respostas}) == 1
    assert reserva.conferir()["reservadas"] == 1


def test_chave_bloqueada_e_pulada_sem_reserva_parcial(reserva):
    _, headers = reserva.cliente()
    jogo = reserva.jogo_fisico(1)
    adicionar(reserva, headers, jogo)
    with reserva.pool.connection() as controle, controle.transaction():
        controle.execute("select id from catalogo.chaves where jogo_id=%s for update", (jogo,))
        assert reservar(reserva, headers).status_code == 409
    assert reserva.conferir()["pedidos"] == 0
    assert reservar(reserva, headers).status_code == 200


def test_bloqueio_de_um_jogo_nao_impede_reserva_de_outro(reserva):
    _, h1 = reserva.cliente()
    _, h2 = reserva.cliente()
    a, b = reserva.jogo_fisico(1), reserva.jogo_fisico(1)
    adicionar(reserva, h1, a)
    adicionar(reserva, h2, b)
    with reserva.pool.connection() as c, c.transaction():
        c.execute("select id from catalogo.jogos where id=%s for no key update", (a,))
        assert reservar(reserva, h2).status_code == 200


def test_timeout_reverte_tudo_e_libera_pool(reserva):
    _, headers = reserva.cliente()
    jogo = reserva.jogo_fisico(1)
    adicionar(reserva, headers, jogo)
    with reserva.pool.connection() as c, c.transaction():
        c.execute("select id from catalogo.jogos where id=%s for no key update", (jogo,))
        assert reservar(reserva, headers).status_code == 503
    assert reserva.conferir()["pedidos"] == 0
    assert reservar(reserva, headers).status_code == 200


def test_reserva_reutilizavel_rollback_externo_e_autocommit_recusado(reserva):
    jogo = reserva.jogo_fisico(1)
    with reserva.pool.connection() as c:
        with c.transaction(force_rollback=True):
            c.execute("select id from catalogo.jogos where id=%s for no key update", (jogo,))
            assert len(reservar_chaves(c, jogo, 1)) == 1
        assert reserva.conferir()["estoques"] == [(1, 1)]
        with pytest.raises(RuntimeError, match="transação externa"):
            reservar_chaves(c, jogo, 1)


def test_limites_evitar_overflow_e_alocacao_sem_limite(reserva):
    usuario, headers = reserva.cliente()
    jogo = reserva.jogo_fisico(2, preco=Decimal("99999999.99"))
    adicionar(reserva, headers, jogo, 2)
    assert reservar(reserva, headers).status_code == 422
    with reserva.pool.connection() as c:
        c.execute(
            "update vendas.itens_carrinho set quantidade=2147483647 where carrinho_id in"
            " (select id from vendas.carrinhos where usuario_id=%s)",
            (usuario.id,),
        )
    assert reservar(reserva, headers).status_code == 422
    assert reserva.conferir()["pedidos"] == 0


def test_grants_e_constraints_do_modelo_real(reserva):
    _, headers = reserva.cliente()
    jogo, outro = reserva.jogo_fisico(1), reserva.jogo_fisico(1)
    adicionar(reserva, headers, jogo)
    pedido = reservar(reserva, headers).json()["pedido_id"]
    with reserva.pool.connection() as c:
        chave = c.execute(
            "select chave_id from vendas.itens_pedido where pedido_id=%s", (pedido,)
        ).fetchone()[0]
        with pytest.raises(psycopg.errors.UniqueViolation), c.transaction():
            c.execute(
                "insert into vendas.itens_pedido (pedido_id,jogo_id,chave_id,preco_unitario)"
                " values (%s,%s,%s,0)",
                (pedido, jogo, chave),
            )
        with pytest.raises(psycopg.errors.ForeignKeyViolation), c.transaction():
            c.execute(
                "insert into vendas.itens_pedido (pedido_id,jogo_id,chave_id,preco_unitario)"
                " select %s,%s,id,0 from catalogo.chaves where jogo_id=%s",
                (pedido, jogo, outro),
            )
        with c.transaction():
            c.execute("set local role gamekeys_equipe")
            assert (
                c.execute("select count(*) from vendas.pedidos where id=%s", (pedido,)).fetchone()[
                    0
                ]
                == 1
            )
            c.execute("update catalogo.chaves set status=status where jogo_id=%s", (jogo,))
        with pytest.raises(psycopg.errors.InsufficientPrivilege), c.transaction():
            c.execute("set local role gamekeys_equipe")
            c.execute("create table vendas.nao_permitida (id int)")


def test_papel_restrito_executa_a_reserva_completa(reserva):
    usuario, headers = reserva.cliente()
    jogo = reserva.jogo_fisico(2)
    adicionar(reserva, headers, jogo)
    with reserva.pool.connection() as c, c.transaction():
        c.execute("set local role gamekeys_equipe")
        pedido = reservas.reservar_na_conexao(c, usuario, uuid4())
        assert pedido.itens[0].quantidade == 1
    assert reserva.conferir()["estoques"] == [(1, 1)]


def test_trigger_mantem_contador_em_transicoes_e_exclusao_e_impede_mudar_jogo(reserva):
    a, b = reserva.jogo_fisico(2), reserva.jogo_fisico(0)
    with reserva.pool.connection() as c:
        chave = c.execute("select min(id) from catalogo.chaves where jogo_id=%s", (a,)).fetchone()[
            0
        ]
        for status, esperado in [("reservada", 1), ("vendida", 1), ("disponivel", 2)]:
            c.execute("update catalogo.chaves set status=%s where id=%s", (status, chave))
            assert (
                c.execute(
                    "select chaves_disponiveis from catalogo.jogos where id=%s", (a,)
                ).fetchone()[0]
                == esperado
            )
        with pytest.raises(psycopg.errors.RaiseException), c.transaction():
            c.execute("update catalogo.chaves set jogo_id=%s where id=%s", (b, chave))
        c.execute("delete from catalogo.chaves where id=%s", (chave,))
    assert reserva.conferir()["estoques"] == [(1, 1), (0, 0)]


def test_carga_demo_repetida_nao_libera_chaves_reservadas(conexao):
    jogo = conexao.execute(
        "select id from catalogo.jogos where slug='lamina-do-sertao'"
    ).fetchone()[0]
    chave = conexao.execute(
        "select min(id) from catalogo.chaves where jogo_id=%s", (jogo,)
    ).fetchone()[0]
    antes = conexao.execute("select count(*) from catalogo.chaves").fetchone()[0]
    conexao.execute("update catalogo.chaves set status='reservada' where id=%s", (chave,))
    aplicar_carga(conexao)
    assert conexao.execute("select count(*) from catalogo.chaves").fetchone()[0] == antes
    assert (
        conexao.execute("select status from catalogo.chaves where id=%s", (chave,)).fetchone()[0]
        == "reservada"
    )
    assert (
        conexao.execute(
            "select chaves_disponiveis from catalogo.jogos where id=%s", (jogo,)
        ).fetchone()[0]
        == 39
    )


def test_carrinho_e_pedido_nao_mudam_ao_recusar_conexao_sem_transacao(reserva):
    usuario, headers = reserva.cliente()
    jogo = reserva.jogo_fisico(1)
    adicionar(reserva, headers, jogo)
    with reserva.pool.connection() as c:
        c.autocommit = True
        try:
            with pytest.raises(RuntimeError, match="transação externa"):
                reservas.reservar_na_conexao(c, usuario, uuid4())
        finally:
            c.autocommit = False
    assert reserva.conferir()["pedidos"] == 0


def test_segunda_reserva_sequencial_da_ultima_chave_e_recusada(reserva):
    _, h1 = reserva.cliente()
    _, h2 = reserva.cliente()
    jogo = reserva.jogo_fisico(1)
    adicionar(reserva, h1, jogo)
    adicionar(reserva, h2, jogo)
    assert reservar(reserva, h1).status_code == 200
    assert reservar(reserva, h2).status_code == 409
    assert reserva.conferir()["pedidos"] == 1
    assert len(reserva.api.get("/carrinho", headers=h2).json()["itens"]) == 1


def test_migracao_do_catalogo_legado_nao_inventa_chaves(conexao):
    # Tudo fica na transação descartável da fixture; nenhuma alteração persiste no banco.
    backend = Path(__file__).resolve().parents[1]
    conexao.execute("drop schema vendas, catalogo, core cascade")
    for nome in ("0001_core_e_catalogo.sql", "0002_permissoes_equipe.sql", "0003_carrinho.sql"):
        conexao.execute((backend / "migracoes" / nome).read_text(encoding="utf-8"))
    carga_legada = (
        (backend / "carga/demonstracao.sql").read_text(encoding="utf-8").split("-- GK-124:")[0]
    )
    conexao.execute(carga_legada)
    assert conexao.execute("select sum(chaves_disponiveis) from catalogo.jogos").fetchone()[0] > 0
    conexao.execute((backend / "migracoes/0004_reserva_chaves.sql").read_text(encoding="utf-8"))
    assert conexao.execute(
        "select count(*), sum(chaves_disponiveis) from catalogo.jogos"
    ).fetchone() == (24, 0)
    assert conexao.execute("select count(*) from catalogo.chaves").fetchone()[0] == 0
    assert conexao.execute("select count(*) from core.usuarios").fetchone()[0] == 0


def test_chamador_que_trata_recusa_nao_efetiva_reserva_parcial(reserva):
    usuario, headers = reserva.cliente()
    a, b = reserva.jogo_fisico(1), reserva.jogo_fisico(1)
    for jogo in (a, b):
        adicionar(reserva, headers, jogo)
    with reserva.pool.connection() as c:
        c.execute("update catalogo.chaves set status='invalidada' where jogo_id=%s", (b,))
        c.execute("update catalogo.jogos set chaves_disponiveis=1 where id=%s", (b,))
    with reserva.pool.connection() as c, c.transaction():
        with pytest.raises(carrinho.EstoqueInsuficiente):
            reservas.reservar_na_conexao(c, usuario, uuid4())
        # Mesmo efetivando a transação externa, a reserva interna foi desfeita.
        assert c.execute("select 1").fetchone()[0] == 1
    assert reserva.conferir()["pedidos"] == reserva.conferir()["reservadas"] == 0
    assert reserva.conferir()["estoques"][0] == (1, 1)
