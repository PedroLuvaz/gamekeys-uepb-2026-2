"""GK-129: disputa da última chave pelo serviço real, só em gamekeys_teste local.

Exige migrações aplicadas. Cada rodada cria e remove somente seus próprios dados.
TEST_DATABASE_URL é validada antes de importar a aplicação ou abrir conexões.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, date, datetime
from threading import Barrier
from uuid import uuid4

from psycopg import Connection
from psycopg_pool import ConnectionPool

from qa.duplicidade import chaves_em_mais_de_um_pedido, chaves_inconsistentes
from qa.gk110_concorrencia import validar_url_local


@dataclass(frozen=True)
class Rodada:
    categoria_id: int
    jogo_id: int
    administrador_id: int
    clientes: list[dict]


def preparar_rodada(conexao: Connection, concorrentes: int) -> Rodada:
    """Cria um jogo, uma chave fictícia e um carrinho por cliente, sem reserva."""
    identificador = uuid4().hex
    categoria_id = conexao.execute(
        "insert into catalogo.categorias (nome, slug) values (%s, %s) returning id",
        ("GK-129 " + identificador, "gk129-" + identificador),
    ).fetchone()[0]
    usuarios = []
    for indice in range(concorrentes + 1):
        perfil = "administrador" if indice == 0 else "cliente"
        email = f"gk129-{identificador}-{indice}@example.com"
        usuario_id = conexao.execute(
            "insert into core.usuarios (nome, email, senha_hash, data_nascimento, perfil)"
            " values ('Cliente GK-129', %s, %s, %s, %s) returning id",
            (email, "$2b$12$" + "b" * 53, date(1990, 1, 1), perfil),
        ).fetchone()[0]
        usuarios.append(
            dict(
                id=usuario_id,
                nome="Cliente GK-129",
                email=email,
                data_nascimento=date(1990, 1, 1),
                perfil=perfil,
            )
        )
    administrador_id = usuarios[0]["id"]
    jogo_id = conexao.execute(
        "insert into catalogo.jogos"
        " (categoria_id, slug, nome, descricao, preco, plataforma, classificacao)"
        " values (%s, %s, 'Jogo GK-129', 'Disputa da última chave fictícia', 19.90, 'PC', 'L')"
        " returning id",
        (categoria_id, "gk129-" + identificador),
    ).fetchone()[0]
    conexao.execute(
        "insert into catalogo.chaves (jogo_id, codigo, cadastrada_por) values (%s, %s, %s)",
        (jogo_id, "GK-TESTE-" + identificador, administrador_id),
    )
    for usuario in usuarios[1:]:
        carrinho_id = conexao.execute(
            "insert into vendas.carrinhos (usuario_id) values (%s) returning id",
            (usuario["id"],),
        ).fetchone()[0]
        conexao.execute(
            "insert into vendas.itens_carrinho (carrinho_id, jogo_id, quantidade)"
            " values (%s, %s, 1)",
            (carrinho_id, jogo_id),
        )
    return Rodada(categoria_id, jogo_id, administrador_id, usuarios[1:])


def limpar_rodada(conexao: Connection, rodada: Rodada) -> None:
    """Remove pedidos, chaves e contas criados exclusivamente nesta rodada."""
    usuarios = [cliente["id"] for cliente in rodada.clientes] + [rodada.administrador_id]
    conexao.execute("delete from vendas.itens_pedido where jogo_id = %s", (rodada.jogo_id,))
    conexao.execute("delete from vendas.pedidos where usuario_id = any(%s)", (usuarios,))
    conexao.execute("delete from vendas.carrinhos where usuario_id = any(%s)", (usuarios,))
    conexao.execute("delete from catalogo.chaves where jogo_id = %s", (rodada.jogo_id,))
    conexao.execute("delete from catalogo.jogos where id = %s", (rodada.jogo_id,))
    conexao.execute("delete from catalogo.categorias where id = %s", (rodada.categoria_id,))
    conexao.execute("delete from core.usuarios where id = any(%s)", (usuarios,))


def tentar_reserva(
    pool: ConnectionPool, cliente: dict, barreira: Barrier
) -> tuple[str, str | None]:
    # Importação tardia: o CLI já validou a URL e desabilitou a leitura de arquivos dotenv.
    from app.esquemas.clientes import ClienteCadastrado
    from app.servicos.carrinho import EstoqueInsuficiente
    from app.servicos.reservas import reservar_na_conexao

    try:
        with pool.connection() as conexao:
            barreira.wait(timeout=15)
            with conexao.transaction():
                conexao.execute("set transaction isolation level read committed")
                reservar_na_conexao(conexao, ClienteCadastrado(**cliente), uuid4())
        return "reservada", None
    except EstoqueInsuficiente:
        return "esgotado", None
    except Exception as erro:
        # O JSON registra o tipo, sem URLs, senhas ou códigos de ativação do traceback.
        return "erro", type(erro).__name__


def consultar_integridade(conexao: Connection, rodada: Rodada) -> dict:
    usuarios = [cliente["id"] for cliente in rodada.clientes]
    pedidos = conexao.execute(
        "select count(*) from vendas.pedidos where usuario_id = any(%s)", (usuarios,)
    ).fetchone()[0]
    itens = conexao.execute(
        "select count(*) from vendas.itens_pedido where jogo_id = %s", (rodada.jogo_id,)
    ).fetchone()[0]
    reservadas, disponiveis = conexao.execute(
        "select count(*) filter (where status = 'reservada'),"
        " count(*) filter (where status = 'disponivel')"
        " from catalogo.chaves where jogo_id = %s",
        (rodada.jogo_id,),
    ).fetchone()
    inconsistencias = [
        chave for chave in chaves_inconsistentes(conexao) if chave["jogo_id"] == rodada.jogo_id
    ]
    return {
        "pedidos": pedidos,
        "itens_pedido": itens,
        "chaves_reservadas": reservadas,
        "chaves_disponiveis": disponiveis,
        "inconsistencias": inconsistencias,
    }


def executar_estresse(url: str, *, rodadas: int = 100, concorrentes: int = 20) -> dict:
    """Uma reserva efetivada e concorrentes-1 recusas de estoque por rodada."""
    url = validar_url_local(url)
    if rodadas < 1 or concorrentes < 2:
        raise ValueError("use ao menos 1 rodada e 2 concorrentes")
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    inicio = time.perf_counter()
    totais: Counter[str] = Counter()
    falhas: list[dict] = []
    duplicidades = 0
    with ConnectionPool(
        url,
        min_size=concorrentes,
        max_size=concorrentes,
        timeout=15,
        kwargs={"prepare_threshold": None},
    ) as pool:
        pool.wait(timeout=30)
        for numero in range(1, rodadas + 1):
            with pool.connection() as conexao:
                rodada = preparar_rodada(conexao, concorrentes)
            try:
                barreira = Barrier(concorrentes)
                with ThreadPoolExecutor(max_workers=concorrentes) as executor:
                    futuros = [
                        executor.submit(tentar_reserva, pool, cliente, barreira)
                        for cliente in rodada.clientes
                    ]
                    resultados = [futuro.result(timeout=30) for futuro in futuros]
                contagem = Counter(status for status, _ in resultados)
                totais.update(contagem)
                with pool.connection() as conexao:
                    repetidas = chaves_em_mais_de_um_pedido(conexao)
                    integridade = consultar_integridade(conexao, rodada)
                duplicidades += len(repetidas)
                if (
                    contagem != {"reservada": 1, "esgotado": concorrentes - 1}
                    or repetidas
                    or integridade
                    != {
                        "pedidos": 1,
                        "itens_pedido": 1,
                        "chaves_reservadas": 1,
                        "chaves_disponiveis": 0,
                        "inconsistencias": [],
                    }
                ):
                    falhas.append(
                        {
                            "rodada": numero,
                            "resultados": dict(contagem),
                            "integridade": integridade,
                            "duplicidades": repetidas,
                            "erros": [erro for _, erro in resultados if erro],
                        }
                    )
            finally:
                with pool.connection() as conexao:
                    limpar_rodada(conexao, rodada)
    return {
        "experimento": "GK-128/GK-129 (reserva real GK-15)",
        "executado_em_utc": datetime.now(UTC).isoformat(),
        "banco": "gamekeys_teste local",
        "isolamento": "read committed",
        "rodadas": rodadas,
        "concorrentes_por_rodada": concorrentes,
        "tentativas": rodadas * concorrentes,
        "resultados": dict(totais),
        "rodadas_com_falha": len(falhas),
        "falhas": falhas,
        "duplicidades": duplicidades,
        "duracao_segundos": round(time.perf_counter() - inicio, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rodadas", type=int, default=100)
    parser.add_argument("--concorrentes", type=int, default=20)
    args = parser.parse_args()
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        parser.error("defina TEST_DATABASE_URL para o gamekeys_teste local")
    relatorio = executar_estresse(url, rodadas=args.rodadas, concorrentes=args.concorrentes)
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return 1 if relatorio["rodadas_com_falha"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
