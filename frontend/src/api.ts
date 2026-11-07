import { useEffect, useState } from "react";

export interface Jogo {
  id: number;
  slug: string;
  nome: string;
  capa_url: string | null;
  preco: string;
  disponibilidade: "Disponível" | "Esgotado";
}

export interface PaginaDeJogos {
  itens: Jogo[];
  pagina: number;
  por_pagina: number;
  total: number;
  total_paginas: number;
}

export interface DetalheDoJogo extends Jogo {
  descricao: string;
  genero: string;
  plataforma: string;
  classificacao: string;
}

export interface DadosDeCadastro {
  nome: string;
  email: string;
  data_nascimento: string;
  senha: string;
}

export interface ClienteCadastrado {
  id: number;
  nome: string;
  email: string;
  data_nascimento: string;
  perfil: "cliente" | "administrador";
}

export interface SessaoCriada {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  usuario: ClienteCadastrado;
}

export interface SessaoLocal {
  token: string;
  expiraEm: number;
  usuario: ClienteCadastrado;
}

export interface ItemDoCarrinho {
  carrinho_id: number;
  jogo_id: number;
  nome: string;
  quantidade: number;
  preco_unitario: string;
  subtotal: string;
}

export interface ItemListadoNoCarrinho {
  jogo_id: number;
  slug: string;
  nome: string;
  capa_url: string | null;
  quantidade: number;
  estoque_disponivel: number;
  preco_unitario: string;
  subtotal: string;
}

export interface CarrinhoConsultado {
  itens: ItemListadoNoCarrinho[];
  total: string;
}

export function destinoAposLogin(retorno: string | null) {
  // Só permite voltar para rotas internas conhecidas; nunca para endereço externo.
  return retorno &&
    (retorno === "/carrinho" ||
      /^\/jogos\/\d+\/?(?:\?origem=\d+)?$/.test(retorno))
    ? retorno
    : "/conta";
}

const CHAVE_DA_SESSAO = "gamekeys.sessao";

export class ErroDaApi extends Error {
  constructor(
    mensagem: string,
    readonly status: number,
  ) {
    super(mensagem);
  }
}

type Estado<T> =
  | { chave: string; status: "carregando" }
  | { chave: string; status: "pronto"; dados: T }
  | { chave: string; status: "erro"; naoEncontrado: boolean };

const baseDaApi = (import.meta.env.VITE_API_URL || "/api").replace(/\/$/, "");

function mensagemDaApi(corpo: unknown) {
  if (!corpo || typeof corpo !== "object" || !("detail" in corpo)) return null;
  const detalhe = corpo.detail;
  if (typeof detalhe === "string") return detalhe;
  if (Array.isArray(detalhe) && typeof detalhe[0]?.msg === "string")
    return detalhe[0].msg.replace(/^Value error, /, "");
  return null;
}

export async function cadastrarCliente(
  dados: DadosDeCadastro,
): Promise<ClienteCadastrado> {
  let resposta: Response;
  try {
    resposta = await fetch(`${baseDaApi}/clientes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
  } catch {
    throw new Error("Não foi possível falar com o servidor. Tente novamente.");
  }
  const corpo = (await resposta.json().catch(() => null)) as unknown;
  if (!resposta.ok)
    throw new Error(
      mensagemDaApi(corpo) ||
        "Não foi possível concluir o cadastro. Tente novamente.",
    );
  return corpo as ClienteCadastrado;
}

export async function entrar(
  email: string,
  senha: string,
): Promise<SessaoCriada> {
  let resposta: Response;
  try {
    resposta = await fetch(`${baseDaApi}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, senha }),
    });
  } catch {
    throw new ErroDaApi(
      "Não foi possível falar com o servidor. Tente novamente.",
      0,
    );
  }
  const corpo = (await resposta.json().catch(() => null)) as unknown;
  if (!resposta.ok)
    throw new ErroDaApi(
      mensagemDaApi(corpo) || "Não foi possível entrar. Tente novamente.",
      resposta.status,
    );
  return corpo as SessaoCriada;
}

export async function consultarUsuario(
  token: string,
): Promise<ClienteCadastrado> {
  let resposta: Response;
  try {
    resposta = await fetch(`${baseDaApi}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch {
    throw new ErroDaApi(
      "Não foi possível validar sua sessão. Tente novamente.",
      0,
    );
  }
  const corpo = (await resposta.json().catch(() => null)) as unknown;
  if (!resposta.ok)
    throw new ErroDaApi(
      mensagemDaApi(corpo) || "Não foi possível validar sua sessão.",
      resposta.status,
    );
  return corpo as ClienteCadastrado;
}

export async function adicionarAoCarrinho(
  token: string,
  jogoId: number,
  quantidade: number,
  signal?: AbortSignal,
): Promise<ItemDoCarrinho> {
  let resposta: Response;
  try {
    resposta = await fetch(`${baseDaApi}/carrinho/itens`, {
      method: "POST",
      signal,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ jogo_id: jogoId, quantidade }),
    });
  } catch {
    throw new ErroDaApi(
      "Não foi possível confirmar a adição. Evite repetir para não duplicar a quantidade.",
      0,
    );
  }
  const corpo = (await resposta.json().catch(() => null)) as unknown;
  if (!resposta.ok)
    throw new ErroDaApi(
      mensagemDaApi(corpo) || "Não foi possível adicionar o jogo ao carrinho.",
      resposta.status,
    );
  if (
    !corpo ||
    typeof corpo !== "object" ||
    !("jogo_id" in corpo) ||
    corpo.jogo_id !== jogoId ||
    !("carrinho_id" in corpo) ||
    typeof corpo.carrinho_id !== "number" ||
    corpo.carrinho_id < 1 ||
    !("nome" in corpo) ||
    typeof corpo.nome !== "string" ||
    !("quantidade" in corpo) ||
    typeof corpo.quantidade !== "number" ||
    !Number.isInteger(corpo.quantidade) ||
    corpo.quantidade < 1 ||
    !("preco_unitario" in corpo) ||
    typeof corpo.preco_unitario !== "string" ||
    !/^\d+\.\d{2}$/.test(corpo.preco_unitario) ||
    !("subtotal" in corpo) ||
    typeof corpo.subtotal !== "string" ||
    !/^\d+\.\d{2}$/.test(corpo.subtotal)
  ) {
    throw new ErroDaApi(
      "Não foi possível confirmar a adição. Evite repetir para não duplicar a quantidade.",
      0,
    );
  }
  return corpo as ItemDoCarrinho;
}

function carrinhoValido(corpo: unknown): corpo is CarrinhoConsultado {
  if (
    !corpo ||
    typeof corpo !== "object" ||
    !("itens" in corpo) ||
    !Array.isArray(corpo.itens) ||
    !("total" in corpo) ||
    typeof corpo.total !== "string" ||
    !/^\d+\.\d{2}$/.test(corpo.total)
  )
    return false;
  return corpo.itens.every(
    (item) =>
      item &&
      typeof item === "object" &&
      "jogo_id" in item &&
      typeof item.jogo_id === "number" &&
      Number.isInteger(item.jogo_id) &&
      item.jogo_id > 0 &&
      "slug" in item &&
      typeof item.slug === "string" &&
      "nome" in item &&
      typeof item.nome === "string" &&
      "capa_url" in item &&
      (item.capa_url === null || typeof item.capa_url === "string") &&
      "quantidade" in item &&
      typeof item.quantidade === "number" &&
      Number.isInteger(item.quantidade) &&
      item.quantidade > 0 &&
      "estoque_disponivel" in item &&
      typeof item.estoque_disponivel === "number" &&
      Number.isInteger(item.estoque_disponivel) &&
      item.estoque_disponivel >= 0 &&
      "preco_unitario" in item &&
      typeof item.preco_unitario === "string" &&
      /^\d+\.\d{2}$/.test(item.preco_unitario) &&
      "subtotal" in item &&
      typeof item.subtotal === "string" &&
      /^\d+\.\d{2}$/.test(item.subtotal),
  );
}

async function requisicaoDoCarrinho(
  token: string,
  caminho = "",
  opcoes: RequestInit = {},
): Promise<CarrinhoConsultado> {
  let resposta: Response;
  try {
    resposta = await fetch(`${baseDaApi}/carrinho${caminho}`, {
      ...opcoes,
      headers: {
        ...(opcoes.body ? { "Content-Type": "application/json" } : {}),
        Authorization: `Bearer ${token}`,
        ...opcoes.headers,
      },
    });
  } catch {
    throw new ErroDaApi(
      "Não foi possível conectar ao carrinho. Verifique sua conexão e tente novamente.",
      0,
    );
  }
  const corpo = (await resposta.json().catch(() => null)) as unknown;
  if (!resposta.ok)
    throw new ErroDaApi(
      mensagemDaApi(corpo) || "Não foi possível atualizar o carrinho.",
      resposta.status,
    );
  if (!carrinhoValido(corpo))
    throw new ErroDaApi(
      "O servidor retornou um carrinho inválido. Tente novamente.",
      0,
    );
  return corpo;
}

export function consultarCarrinho(token: string, signal?: AbortSignal) {
  return requisicaoDoCarrinho(token, "", { signal });
}

export function alterarQuantidadeDoCarrinho(
  token: string,
  jogoId: number,
  quantidade: number,
) {
  return requisicaoDoCarrinho(token, `/itens/${jogoId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantidade }),
  });
}

export function removerDoCarrinho(token: string, jogoId: number) {
  return requisicaoDoCarrinho(token, `/itens/${jogoId}`, { method: "DELETE" });
}

export function guardarSessao(sessao: SessaoCriada): SessaoLocal {
  const local = {
    token: sessao.access_token,
    expiraEm: Date.now() + sessao.expires_in * 1000,
    usuario: sessao.usuario,
  };
  sessionStorage.setItem(CHAVE_DA_SESSAO, JSON.stringify(local));
  return local;
}

export function lerSessao(): SessaoLocal | null {
  try {
    const valor = sessionStorage.getItem(CHAVE_DA_SESSAO);
    if (!valor) return null;
    const sessao = JSON.parse(valor) as SessaoLocal;
    if (!sessao.token || !sessao.usuario || sessao.expiraEm <= Date.now()) {
      encerrarSessao();
      return null;
    }
    return sessao;
  } catch {
    encerrarSessao();
    return null;
  }
}

export function encerrarSessao() {
  sessionStorage.removeItem(CHAVE_DA_SESSAO);
}

export function useConsulta<T>(caminho: string) {
  const [tentativa, setTentativa] = useState(0);
  const chave = `${caminho}:${tentativa}`;
  const [estado, setEstado] = useState<Estado<T>>({
    chave,
    status: "carregando",
  });

  useEffect(() => {
    const controle = new AbortController();
    setEstado({ chave, status: "carregando" });
    fetch(`${baseDaApi}${caminho}`, { signal: controle.signal })
      .then(async (resposta) => {
        if (!resposta.ok) {
          if (!controle.signal.aborted) {
            setEstado({
              chave,
              status: "erro",
              naoEncontrado: resposta.status === 404,
            });
          }
          return;
        }
        const dados = (await resposta.json()) as T;
        if (!controle.signal.aborted)
          setEstado({ chave, status: "pronto", dados });
      })
      .catch(() => {
        if (!controle.signal.aborted)
          setEstado({ chave, status: "erro", naoEncontrado: false });
      });
    return () => controle.abort();
  }, [caminho, chave]);

  return {
    estado:
      estado.chave === chave
        ? estado
        : ({ chave, status: "carregando" } as Estado<T>),
    tentarNovamente: () => setTentativa((valor) => valor + 1),
  };
}

export function precoEmReais(preco: string) {
  // A API devolve decimal com duas casas. BigInt mantém centavos em subtotais
  // grandes, sem converter o valor monetário inteiro em ponto flutuante.
  const [reais, centavos = "00"] = preco.split(".");
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })
    .formatToParts(BigInt(reais))
    .map((parte) =>
      parte.type === "fraction" ? centavos.padEnd(2, "0") : parte.value,
    )
    .join("");
}
