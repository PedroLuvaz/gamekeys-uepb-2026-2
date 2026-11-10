import { useId, useLayoutEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { adicionarAoCarrinho, ErroDaApi, precoEmReais } from "./api";
import type { DetalheDoJogo, ItemDoCarrinho, SessaoLocal } from "./api";

type Estado =
  | { tipo: "inicial" | "enviando" }
  | { tipo: "sucesso"; item: ItemDoCarrinho }
  | { tipo: "erro"; mensagem: string };

export default function AdicionarAoCarrinho({
  jogo,
  sessao,
  aoPedirLogin,
  aoExpirar,
}: {
  jogo: DetalheDoJogo;
  sessao: SessaoLocal | null;
  aoPedirLogin: () => void;
  aoExpirar: () => void;
}) {
  if (jogo.disponibilidade === "Esgotado")
    return (
      <div className="adicao-carrinho">
        <button
          className="botao botao-carrinho"
          disabled
          data-cy="adicionar-carrinho"
        >
          Esgotado
        </button>
        <p className="nota-carrinho">Este jogo está esgotado no momento.</p>
      </div>
    );

  if (!sessao)
    return (
      <div className="adicao-carrinho">
        <a
          className="botao botao-carrinho"
          href={`/login?retorno=${encodeURIComponent(`${location.pathname}${location.search}`)}`}
          onClick={(evento) => {
            evento.preventDefault();
            aoPedirLogin();
          }}
          data-cy="entrar-para-adicionar"
        >
          Entrar para adicionar ao carrinho
        </a>
        <p className="nota-carrinho">
          Entre na sua conta para escolher seus jogos.
        </p>
      </div>
    );

  if (sessao.usuario.perfil !== "cliente")
    return (
      <p className="nota-carrinho" data-cy="perfil-sem-carrinho">
        O carrinho é exclusivo de contas de cliente.
      </p>
    );

  return (
    <FormularioCarrinho
      jogo={jogo}
      token={sessao.token}
      aoExpirar={aoExpirar}
    />
  );
}

function FormularioCarrinho({
  jogo,
  token,
  aoExpirar,
}: {
  jogo: DetalheDoJogo;
  token: string;
  aoExpirar: () => void;
}) {
  const [quantidade, setQuantidade] = useState("1");
  const [estado, setEstado] = useState<Estado>({ tipo: "inicial" });
  const quantidadeId = useId();
  const enviando = useRef(false);
  const ativo = useRef(true);
  const requisicao = useRef<AbortController | null>(null);

  // Finalizar o ciclo de montagem antes de aceitar um envio imediato, inclusive em StrictMode.
  useLayoutEffect(() => {
    ativo.current = true;
    return () => {
      ativo.current = false;
      requisicao.current?.abort();
    };
  }, []);

  async function adicionar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    // O ref protege também dois envios no mesmo instante, antes do próximo render.
    if (enviando.current) return;
    const unidades = Number(quantidade);
    if (!Number.isInteger(unidades) || unidades < 1 || unidades > 2147483647) {
      setEstado({
        tipo: "erro",
        mensagem: "Informe uma quantidade inteira maior que zero.",
      });
      return;
    }
    enviando.current = true;
    setEstado({ tipo: "enviando" });
    const controle = new AbortController();
    requisicao.current = controle;
    try {
      const item = await adicionarAoCarrinho(
        token,
        jogo.id,
        unidades,
        controle.signal,
      );
      if (ativo.current) setEstado({ tipo: "sucesso", item });
    } catch (erro) {
      if (!ativo.current || controle.signal.aborted) return;
      if (erro instanceof ErroDaApi && erro.status === 401) {
        aoExpirar();
        return;
      }
      setEstado({
        tipo: "erro",
        mensagem:
          erro instanceof Error
            ? erro.message
            : "Não foi possível adicionar o jogo.",
      });
    } finally {
      enviando.current = false;
    }
  }

  return (
    <form
      className="formulario-carrinho adicao-carrinho"
      onSubmit={adicionar}
      noValidate
      aria-label="Adicionar jogo ao carrinho"
      aria-busy={estado.tipo === "enviando"}
      data-cy="formulario-carrinho"
    >
      <div className="controles-carrinho">
        <label className="quantidade-carrinho" htmlFor={quantidadeId}>
          Quantidade
          <input
            id={quantidadeId}
            name="quantidade"
            type="number"
            inputMode="numeric"
            min="1"
            max="2147483647"
            step="1"
            required
            value={quantidade}
            disabled={estado.tipo === "enviando"}
            data-cy="quantidade-carrinho"
            onChange={(evento) => {
              setQuantidade(evento.target.value);
              setEstado({ tipo: "inicial" });
            }}
          />
        </label>
        <button
          className="botao botao-carrinho"
          disabled={estado.tipo === "enviando"}
          data-cy="adicionar-carrinho"
        >
          {estado.tipo === "enviando"
            ? "Adicionando…"
            : "Adicionar ao carrinho"}
        </button>
      </div>
      {estado.tipo === "enviando" && (
        <p className="nota-carrinho" role="status">
          Adicionando o jogo ao seu carrinho…
        </p>
      )}
      {estado.tipo === "sucesso" && (
        <div
          className="resultado-carrinho"
          role="status"
          data-cy="resultado-carrinho"
        >
          <strong>
            Adicionado ao carrinho. Você tem {estado.item.quantidade}{" "}
            {estado.item.quantidade === 1 ? "unidade" : "unidades"} deste jogo.
          </strong>
          <span>Subtotal do item: {precoEmReais(estado.item.subtotal)}</span>
        </div>
      )}
      {estado.tipo === "erro" && (
        <p className="erro-formulario" role="alert" data-cy="erro-carrinho">
          {estado.mensagem}
        </p>
      )}
      <p className="nota-carrinho">
        A disponibilidade será confirmada na finalização.
      </p>
    </form>
  );
}
