import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { consultarPedido, ErroDaApi, pagarPedido, precoEmReais } from "./api";
import type {
  MetodoDePagamento,
  PedidoDetalhado,
  SessaoLocal,
  StatusDoPedido,
} from "./api";

type Estado =
  | { tipo: "carregando" }
  | { tipo: "pronto"; pedido: PedidoDetalhado }
  | { tipo: "nao-encontrado" }
  | { tipo: "erro"; mensagem: string };

const NOME_DO_STATUS: Record<StatusDoPedido, string> = {
  aguardando_pagamento: "Aguardando pagamento",
  pago: "Pago",
  entregue: "Entregue",
  cancelado: "Cancelado",
};

const METODOS: { valor: MetodoDePagamento; nome: string }[] = [
  { valor: "pix", nome: "Pix" },
  { valor: "cartao", nome: "Cartão" },
  { valor: "boleto", nome: "Boleto" },
];

export default function Pedido({
  id,
  sessao,
  aoExpirar,
}: {
  id: number;
  sessao: SessaoLocal;
  aoExpirar: () => void;
}) {
  const [estado, setEstado] = useState<Estado>({ tipo: "carregando" });
  const [tentativa, setTentativa] = useState(0);
  const [metodo, setMetodo] = useState<MetodoDePagamento>("pix");
  const [pagando, setPagando] = useState(false);
  const [mensagem, setMensagem] = useState<{
    tipo: "sucesso" | "erro";
    texto: string;
  } | null>(null);
  const ativa = useRef(true);
  // O estado demora um ciclo para desabilitar o botão; a referência barra o segundo clique na hora.
  const enviando = useRef(false);

  useEffect(() => {
    document.title = `Pedido nº ${id} | GameKeys`;
  }, [id]);

  useEffect(() => {
    ativa.current = true;
    if (sessao.usuario.perfil !== "cliente") return;
    const controle = new AbortController();
    setEstado({ tipo: "carregando" });
    setMensagem(null);
    consultarPedido(sessao.token, id, controle.signal)
      .then((pedido) => {
        if (ativa.current) setEstado({ tipo: "pronto", pedido });
      })
      .catch((erro) => {
        if (!ativa.current || controle.signal.aborted) return;
        if (erro instanceof ErroDaApi && erro.status === 401) {
          aoExpirar();
          return;
        }
        if (erro instanceof ErroDaApi && erro.status === 404) {
          setEstado({ tipo: "nao-encontrado" });
          return;
        }
        setEstado({
          tipo: "erro",
          mensagem:
            erro instanceof Error
              ? erro.message
              : "Não foi possível carregar o pedido.",
        });
      });
    return () => {
      ativa.current = false;
      controle.abort();
    };
  }, [sessao, id, aoExpirar, tentativa]);

  async function pagar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviando.current) return;
    enviando.current = true;
    setPagando(true);
    setMensagem(null);
    try {
      const pedido = await pagarPedido(sessao.token, id, metodo);
      if (!ativa.current) return;
      setEstado({ tipo: "pronto", pedido });
      setMensagem({
        tipo: "sucesso",
        texto: "Pagamento confirmado. Suas chaves estão logo abaixo.",
      });
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
            : "Não foi possível confirmar o pagamento.",
      });
    } finally {
      enviando.current = false;
      if (ativa.current) setPagando(false);
    }
  }

  if (sessao.usuario.perfil !== "cliente")
    return (
      <section
        className="carrinho-pagina estado-tela"
        data-cy="pedido-perfil-invalido"
      >
        <span className="estado-icone" aria-hidden="true">
          !
        </span>
        <h1>Pedido indisponível</h1>
        <p>Os pedidos são exclusivos de contas de cliente.</p>
        <a href="/" className="botao">
          Voltar ao catálogo →
        </a>
      </section>
    );

  const pedido = estado.tipo === "pronto" ? estado.pedido : null;

  return (
    <section className="carrinho-pagina" aria-labelledby="pedido-titulo">
      <header className="carrinho-cabecalho">
        <div>
          <span className="sobretitulo pequeno">SEU PEDIDO</span>
          <h1 id="pedido-titulo">
            Pedido nº {id}
            <span className="ponto">.</span>
          </h1>
          {pedido && (
            <p>
              Situação:{" "}
              <strong
                className={`status-pedido ${pedido.status}`}
                data-cy="status-pedido"
              >
                {NOME_DO_STATUS[pedido.status]}
              </strong>
            </p>
          )}
        </div>
        <a href="/" className="continuar-comprando">
          ← Continuar comprando
        </a>
      </header>

      {mensagem && (
        <p
          className={`mensagem-carrinho ${mensagem.tipo}`}
          role={mensagem.tipo === "erro" ? "alert" : "status"}
          data-cy={`mensagem-pedido-${mensagem.tipo}`}
        >
          {mensagem.texto}
        </p>
      )}

      {estado.tipo === "carregando" ? (
        <div
          className="carrinho-carregando"
          role="status"
          data-cy="pedido-carregando"
        >
          <span aria-hidden="true" /> Carregando seu pedido…
        </div>
      ) : estado.tipo === "nao-encontrado" ? (
        <div className="estado-tela" data-cy="pedido-nao-encontrado">
          <span className="estado-icone" aria-hidden="true">
            ◇
          </span>
          <h2>Pedido não encontrado</h2>
          <p>Confira o número do pedido ou volte ao catálogo.</p>
          <a href="/" className="botao">
            Explorar jogos →
          </a>
        </div>
      ) : estado.tipo === "erro" ? (
        <div className="estado-tela" role="alert" data-cy="erro-pedido-pagina">
          <span className="estado-icone" aria-hidden="true">
            !
          </span>
          <h2>Não foi possível carregar o pedido</h2>
          <p>{estado.mensagem}</p>
          <button
            className="botao"
            onClick={() => setTentativa((valor) => valor + 1)}
          >
            Tentar novamente ↻
          </button>
        </div>
      ) : (
        <div className="carrinho-grade">
          <div className="pedido-conteudo">
            {estado.pedido.status === "entregue" && (
              <section
                className="chaves-entregues"
                aria-labelledby="chaves-titulo"
                data-cy="chaves-entregues"
              >
                <h2 id="chaves-titulo">Suas chaves</h2>
                <p>Guarde os códigos: cada um ativa uma cópia do jogo.</p>
                <ul>
                  {estado.pedido.chaves.map((chave) => (
                    <li key={chave.codigo} data-cy="chave-entregue">
                      <span>{chave.nome}</span>
                      <code>{chave.codigo}</code>
                    </li>
                  ))}
                </ul>
              </section>
            )}
            {estado.pedido.status === "cancelado" && (
              <p className="mensagem-carrinho erro" data-cy="pedido-cancelado">
                Este pedido foi cancelado e não pode ser pago.
              </p>
            )}
            {estado.pedido.status === "pago" && (
              <p className="mensagem-carrinho sucesso" data-cy="pedido-pago">
                Pagamento recebido. As chaves aparecem aqui assim que a entrega
                for concluída.
              </p>
            )}
            <table className="itens-pedido" data-cy="itens-pedido">
              <caption>Itens do pedido</caption>
              <thead>
                <tr>
                  <th scope="col">Jogo</th>
                  <th scope="col">Quantidade</th>
                  <th scope="col">Preço na compra</th>
                  <th scope="col">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {estado.pedido.itens.map((item) => (
                  <tr key={item.jogo_id} data-cy="item-pedido">
                    <td>
                      <a href={`/jogos/${item.jogo_id}`}>{item.nome}</a>
                    </td>
                    <td>{item.quantidade}</td>
                    <td>{precoEmReais(item.preco_unitario)}</td>
                    <td>{precoEmReais(item.subtotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <aside className="resumo-carrinho" aria-label="Resumo do pedido">
            <span>RESUMO</span>
            <div>
              <p>Total</p>
              <strong data-cy="total-pedido">
                {precoEmReais(estado.pedido.valor_total)}
              </strong>
            </div>
            {estado.pedido.status === "aguardando_pagamento" ? (
              <form
                className="pagamento"
                onSubmit={pagar}
                aria-busy={pagando}
                data-cy="formulario-pagamento"
              >
                <fieldset disabled={pagando}>
                  <legend>Forma de pagamento (simulado)</legend>
                  {METODOS.map((opcao) => (
                    <label key={opcao.valor}>
                      <input
                        type="radio"
                        name="metodo"
                        value={opcao.valor}
                        checked={metodo === opcao.valor}
                        onChange={() => setMetodo(opcao.valor)}
                        data-cy={`metodo-${opcao.valor}`}
                      />
                      {opcao.nome}
                    </label>
                  ))}
                </fieldset>
                <button
                  className="botao"
                  disabled={pagando}
                  data-cy="confirmar-pagamento"
                >
                  {pagando ? "Confirmando pagamento…" : "Confirmar pagamento"}
                </button>
                <small>
                  Nenhuma cobrança real é feita. As chaves aparecem depois da
                  confirmação.
                </small>
              </form>
            ) : (
              <small>
                {estado.pedido.status === "entregue"
                  ? "Pedido pago e entregue."
                  : "Não há pagamento pendente neste pedido."}
              </small>
            )}
          </aside>
        </div>
      )}
    </section>
  );
}
