"""Provas reais de transação e concorrência para GK-110/GK-116."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest
from psycopg_pool import ConnectionPool

from qa.gk110_concorrencia import (
    BancoDeTesteInseguro,
    FalhaReservaExperimental,
    consultar_integridade,
    criar_estrutura,
    excluir_estrutura,
    executar_estresse,
    preparar_ultima_chave,
    reservar_ultima_chave,
)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://usuario:segredo@exemplo.neon.tech/gamekeys_teste",
        "postgresql://gamekeys:gamekeys@127.0.0.1:5433/outro_banco",
    ],
)
def test_experimento_recusa_neon_e_outro_banco_sem_expor_url(url):
    with pytest.raises(BancoDeTesteInseguro) as capturada:
        criar_estrutura(url)

    mensagem = str(capturada.value)
    assert "segredo" not in mensagem
    assert "neon.tech" not in mensagem


@pytest.fixture
def ambiente_concorrencia(banco):
    criar_estrutura(banco)
    yield banco
    excluir_estrutura(banco)


@pytest.fixture
def pool_concorrencia(ambiente_concorrencia):
    with ConnectionPool(
        ambiente_concorrencia,
        min_size=2,
        max_size=2,
        timeout=10,
        kwargs={"prepare_threshold": None},
        open=True,
    ) as pool:
        pool.wait(timeout=20)
        yield pool


@pytest.mark.concorrencia
def test_skip_locked_nao_espera_transacao_que_bloqueou_a_ultima_chave(
    ambiente_concorrencia,
    pool_concorrencia,
):
    jogo_id = preparar_ultima_chave(ambiente_concorrencia)
    bloqueou = Event()
    liberar = Event()

    def segurar_bloqueio():
        bloqueou.set()
        assert liberar.wait(timeout=10)

    with ThreadPoolExecutor(max_workers=2) as executor:
        primeira = executor.submit(
            reservar_ultima_chave,
            pool_concorrencia,
            jogo_id=jogo_id,
            pedido_id=1,
            cliente_id=1,
            ao_bloquear=segurar_bloqueio,
        )
        assert bloqueou.wait(timeout=10)
        segunda = executor.submit(
            reservar_ultima_chave,
            pool_concorrencia,
            jogo_id=jogo_id,
            pedido_id=2,
            cliente_id=2,
        )
        resultado_segunda = segunda.result(timeout=5)
        liberar.set()
        resultado_primeira = primeira.result(timeout=10)

    assert resultado_primeira.status == "reservada"
    assert resultado_primeira.isolamento == "read committed"
    assert resultado_segunda.status == "esgotado"
    assert consultar_integridade(ambiente_concorrencia) == {
        "pedidos": 1,
        "itens_pedido": 1,
        "chaves_disponiveis": 0,
        "chaves_duplicadas": 0,
    }


@pytest.mark.concorrencia
def test_falha_antes_do_commit_desfaz_pedido_e_reserva(
    ambiente_concorrencia,
    pool_concorrencia,
):
    jogo_id = preparar_ultima_chave(ambiente_concorrencia)

    with pytest.raises(FalhaReservaExperimental, match="antes do commit"):
        reservar_ultima_chave(
            pool_concorrencia,
            jogo_id=jogo_id,
            pedido_id=1,
            cliente_id=1,
            falhar_apos_reserva=True,
        )

    assert consultar_integridade(ambiente_concorrencia) == {
        "pedidos": 0,
        "itens_pedido": 0,
        "chaves_disponiveis": 1,
        "chaves_duplicadas": 0,
    }
    recuperada = reservar_ultima_chave(
        pool_concorrencia,
        jogo_id=jogo_id,
        pedido_id=2,
        cliente_id=2,
    )
    assert recuperada.status == "reservada"


@pytest.mark.concorrencia
def test_vinte_compras_da_ultima_chave_em_cem_rodadas(ambiente_concorrencia):
    relatorio = executar_estresse(
        ambiente_concorrencia,
        rodadas=100,
        concorrentes=20,
    )

    assert relatorio["tentativas"] == 2_000
    assert relatorio["resultados"] == {"reservada": 100, "esgotado": 1_900}
    assert relatorio["rodadas_com_falha"] == 0
    assert relatorio["falhas"] == []
