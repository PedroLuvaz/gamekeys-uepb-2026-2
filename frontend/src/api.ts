import { useEffect, useState } from "react";

export interface Jogo {
  id: number;
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
  perfil: "cliente";
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

export const precoEmReais = (preco: string) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
    Number(preco),
  );
