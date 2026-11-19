import { useCallback, useEffect, useRef, useState } from "react";
import ArteJogo from "./ArteJogo";
import {
  alterarQuantidadeDoCarrinho,
  consultarCarrinho,
  ErroDaApi,
  finalizarCompra,
  precoEmReais,
  removerDoCarrinho,
} from "./api";
import {
  lerFinalizacao,
  limparFinalizacao,
  prepararFinalizacao,
} from "./finalizacao";
import type {
  CarrinhoConsultado,
  ItemListadoNoCarrinho,
  SessaoLocal,
} from "./api";

type Estado =
  | { tipo: "carregando" }
  | { tipo: "pronto"; carrinho: CarrinhoConsultado }
  | { tipo: "erro"; mensagem: string };

type Finalizacao = "pronto" | "pendente" | "enviando" | "indisponivel";

export default function Carrinho({
  sessao,
  aoExpirar,
  aoConcluir,
}: {
  sessao: SessaoLocal;
  aoExpirar: () => void;
  aoConcluir: (pedidoId: number) => void;
}) {
  const [estado, setEstado] = useState<Estado>({ tipo: "carregando" });
  const [tentativa, setTentativa] = useState(0);
  const [operando, setOperando] = useState<number | null>(null);
  const [mensagem, setMensagem] = useState<{
    tipo: "sucesso" | "erro";
    texto: string;
  } | null>(null);
  const ativa = useRef(true);
  const emOperacao = useRef(false);
  const [finalizacao, setFinalizacao] = useState<Finalizacao>(() => {
    try {
      return lerFinalizacao(sessao.usuario.id) ? "pendente" : "pronto";
    } catch {
      return "indisponivel";
    }
  });

  useEffect(() => {
    document.title = "Meu carrinho | GameKeys";
  }, []);

  useEffect(() => {
    ativa.current = true;
    if (sessao.usuario.perfil !== "cliente") return;
    const controle = new AbortController();
    setEstado({ tipo: "carregando" });
    consultarCarrinho(sessao.token, controle.signal)
      .then((carrinho) => {
        if (ativa.current) setEstado({ tipo: "pronto", carrinho });
      })
      .catch((erro) => {
        if (!ativa.current || controle.signal.aborted) return;
        if (erro instanceof ErroDaApi && erro.status === 401) {
          aoExpirar();
          return;
        }
        setEstado({
          tipo: "erro",
          mensagem:
            erro instanceof Error
              ? erro.message
              : "Não foi possível carregar o carrinho.",
        });
      });
    return () => {
      ativa.current = false;
      controle.abort();
    };
  }, [sessao, aoExpirar, tentativa]);

  const executar = useCallback(
    async (
      jogoId: number,
      acao: () => Promise<CarrinhoConsultado>,
      sucesso: string,
    ) => {
      if (emOperacao.current || finalizacao !== "pronto") return;
      emOperacao.current = true;
      setOperando(jogoId);
      setMensagem(null);
      try {
        const carrinho = await acao();
        if (!ativa.current) return;
        setEstado({ tipo: "pronto", carrinho });
        setMensagem({ tipo: "sucesso", texto: sucesso });
      } catch (erro) {
        if (!ativa.current) return;
        if (erro instanceof ErroDaApi && erro.status === 401) {
          aoExpirar();
          return;
        }
        setMensagem({
          tipo: "erro",
          texto:
            erro instanceof Error
              ? erro.message
              : "Não foi possível atualizar o carrinho.",
        });
      } finally {
        emOperacao.current = false;
        if (ativa.current) setOperando(null);
      }
    },
    [aoExpirar, finalizacao],
  );

  async function finalizar() {
    if (emOperacao.current || finalizacao === "indisponivel") return;
    emOperacao.current = true;
    setMensagem(null);
    // Persistir antes do POST permite recuperar a mesma operação após recarga ou resposta perdida.
    try {
      const chave = prepararFinalizacao(sessao.usuario.id);
      setFinalizacao("enviando");
      try {
        const pedido = await finalizarCompra(sessao.token, chave);
        if (!ativa.current) return;
        try {
          limparFinalizacao(sessao.usuario.id);
        } catch {
          /* Mantém a recuperação se o navegador bloquear o armazenamento. */
        }
        aoConcluir(pedido.pedido_id);
      } catch (erro) {
        if (!ativa.current) return;
        if (erro instanceof ErroDaApi && erro.status === 401) {
          aoExpirar();
          return;
        }
        if (
          erro instanceof ErroDaApi &&
          [403, 404, 409, 422].includes(erro.status)
        ) {
          // Estas recusas acontecem antes do commit. Atualizar o carrinho mostra estoque/preço atuais.
          limparFinalizacao(sessao.usuario.id);
          setFinalizacao("pronto");
          setTentativa((valor) => valor + 1);
        } else {
          // Rede, timeout, 5xx e confirmação inválida podem esconder uma operação já efetivada.
          setFinalizacao("pendente");
        }
        setMensagem({
          tipo: "erro",
          texto:
            erro instanceof Error
              ? erro.message
              : "Não foi possível confirmar a finalização.",
        });
      }
    } catch {
      if (ativa.current) {
        setFinalizacao("indisponivel");
        setMensagem({
          tipo: "erro",
          texto:
            "Não foi possível preparar ou recuperar a finalização nesta sessão. Verifique o armazenamento do navegador e tente atualizar a página.",
        });
      }
    } finally {
      emOperacao.current = false;
    }
  }

  if (sessao.usuario.perfil !== "cliente")
    return (
      <section
        className="carrinho-pagina estado-tela"
        data-cy="carrinho-perfil-invalido"
      >
        <span className="estado-icone" aria-hidden="true">
          !
        </span>
        <h1>Carrinho indisponível</h1>
        <p>O carrinho é exclusivo de contas de cliente.</p>
        <a href="/" className="botao">
          Voltar ao catálogo →
        </a>
      </section>
    );

  return (
    <section className="carrinho-pagina" aria-labelledby="carrinho-titulo">
      <header className="carrinho-cabecalho">
        <div>
          <span className="sobretitulo pequeno">SUA SELEÇÃO</span>
          <h1 id="carrinho-titulo">
            Meu carrinho<span className="ponto">.</span>
          </h1>
          <p>Revise as quantidades antes de continuar.</p>
        </div>
        <a href="/" className="continuar-comprando">
          ← Continuar comprando
        </a>
      </header>

      {finalizacao === "pendente" && (
        <div
          className="aviso-finalizacao"
          role="status"
          data-cy="finalizacao-pendente"
        >
          <p>
            Há uma finalização aguardando confirmação. Verifique o resultado
            antes de alterar o carrinho ou iniciar outra compra.
          </p>
          <button
            type="button"
            className="botao"
            onClick={finalizar}
            data-cy="recuperar-finalizacao"
          >
            Verificar finalização
          </button>
        </div>
      )}
      {finalizacao === "indisponivel" && (
        <p
          className="mensagem-carrinho erro"
          role="alert"
          data-cy="finalizacao-indisponivel"
        >
          Não foi possível recuperar a finalização desta sessão. Verifique o
          armazenamento do navegador e atualize a página. Se uma compra estava
          em andamento, confira o resultado com a equipe.
        </p>
      )}
      {finalizacao === "enviando" && (
        <p role="status" data-cy="finalizacao-enviando">
          Finalizando sua compra… Aguarde a confirmação do pedido.
        </p>
      )}

      {mensagem && (
        <p
          className={`mensagem-carrinho ${mensagem.tipo}`}
          role={mensagem.tipo === "erro" ? "alert" : "status"}
          data-cy={`mensagem-carrinho-${mensagem.tipo}`}
        >
          {mensagem.texto}
        </p>
      )}

      {estado.tipo === "carregando" ? (
        <div
          className="carrinho-carregando"
          role="status"
          data-cy="carrinho-carregando"
        >
          <span aria-hidden="true" /> Carregando seu carrinho…
        </div>
      ) : estado.tipo === "erro" ? (
        <div
          className="estado-tela"
          role="alert"
          data-cy="erro-carrinho-pagina"
        >
          <span className="estado-icone" aria-hidden="true">
            !
          </span>
          <h2>Não foi possível carregar o carrinho</h2>
          <p>{estado.mensagem}</p>
          <button
            className="botao"
            onClick={() => setTentativa((valor) => valor + 1)}
          >
            Tentar novamente ↻
          </button>
        </div>
      ) : estado.carrinho.itens.length === 0 ? (
        <div className="estado-tela carrinho-vazio" data-cy="carrinho-vazio">
          <span className="estado-icone" aria-hidden="true">
            ◇
          </span>
          <h2>Seu carrinho está vazio</h2>
          <p>Explore o catálogo e escolha sua próxima aventura.</p>
          <p className="carrinho-vazio-total">
            Total{" "}
            <strong data-cy="total-carrinho">
              {precoEmReais(estado.carrinho.total)}
            </strong>
          </p>
          <a href="/" className="botao">
            Explorar jogos →
          </a>
        </div>
      ) : (
        <div
          className="carrinho-grade"
          aria-busy={operando !== null || finalizacao === "enviando"}
        >
          <div className="lista-carrinho" data-cy="itens-carrinho">
            {estado.carrinho.itens.map((item) => (
              <ItemCarrinho
                key={item.jogo_id}
                item={item}
                bloqueado={operando !== null || finalizacao !== "pronto"}
                processando={operando === item.jogo_id}
                aoAlterar={(quantidade) =>
                  executar(
                    item.jogo_id,
                    () =>
                      alterarQuantidadeDoCarrinho(
                        sessao.token,
                        item.jogo_id,
                        quantidade,
                      ),
                    "Quantidade atualizada com sucesso.",
                  )
                }
                aoRemover={() =>
                  executar(
                    item.jogo_id,
                    () => removerDoCarrinho(sessao.token, item.jogo_id),
                    `${item.nome} foi removido do carrinho.`,
                  )
                }
              />
            ))}
          </div>
          <aside className="resumo-carrinho" aria-label="Resumo do carrinho">
            <span>RESUMO</span>
            <div>
              <p>Total</p>
              <strong data-cy="total-carrinho">
                {precoEmReais(estado.carrinho.total)}
              </strong>
            </div>
            <p>
              {estado.carrinho.itens.length}{" "}
              {estado.carrinho.itens.length === 1 ? "jogo" : "jogos"}
            </p>
            <button
              className="botao"
              type="button"
              disabled={operando !== null || finalizacao !== "pronto"}
              onClick={finalizar}
              data-cy="finalizar-compra"
            >
              {finalizacao === "enviando" ? "Finalizando…" : "Finalizar compra"}
            </button>
            <small>
              Preços e disponibilidade são confirmados na finalização. O
              pagamento será confirmado na próxima tela.
            </small>
          </aside>
        </div>
      )}
    </section>
  );
}

function ItemCarrinho({
  item,
  bloqueado,
  processando,
  aoAlterar,
  aoRemover,
}: {
  item: ItemListadoNoCarrinho;
  bloqueado: boolean;
  processando: boolean;
  aoAlterar: (quantidade: number) => void;
  aoRemover: () => void;
}) {
  const jogo = {
    id: item.jogo_id,
    slug: item.slug,
    nome: item.nome,
    capa_url: item.capa_url,
    preco: item.preco_unitario,
    disponibilidade:
      item.estoque_disponivel > 0
        ? ("Disponível" as const)
        : ("Esgotado" as const),
  };
  return (
    <article
      className="item-carrinho"
      data-cy="item-carrinho"
      data-jogo-id={item.jogo_id}
    >
      <a
        href={`/jogos/${item.jogo_id}`}
        className="item-carrinho-arte"
        aria-label={`Ver ${item.nome}`}
      >
        <ArteJogo jogo={jogo} />
      </a>
      <div className="item-carrinho-dados">
        <span>CHAVE DIGITAL</span>
        <h2>{item.nome}</h2>
        <p>{precoEmReais(item.preco_unitario)} por unidade</p>
        <div
          className="seletor-quantidade"
          aria-label={`Quantidade de ${item.nome}`}
        >
          <button
            type="button"
            aria-label={`Diminuir quantidade de ${item.nome}`}
            disabled={bloqueado || item.quantidade <= 1}
            onClick={() => aoAlterar(item.quantidade - 1)}
            data-cy="diminuir-item"
          >
            −
          </button>
          <output aria-live="polite" data-cy="quantidade-item">
            {item.quantidade}
          </output>
          <button
            type="button"
            aria-label={`Aumentar quantidade de ${item.nome}`}
            disabled={bloqueado || item.quantidade >= 2147483647}
            onClick={() => aoAlterar(item.quantidade + 1)}
            data-cy="aumentar-item"
          >
            +
          </button>
        </div>
        <button
          type="button"
          className="remover-item"
          disabled={bloqueado}
          onClick={aoRemover}
          data-cy="remover-item"
        >
          Remover
        </button>
      </div>
      <div className="subtotal-item">
        <span>Subtotal</span>
        <strong data-cy="subtotal-item">{precoEmReais(item.subtotal)}</strong>
        {processando && <small role="status">Atualizando…</small>}
      </div>
    </article>
  );
}
