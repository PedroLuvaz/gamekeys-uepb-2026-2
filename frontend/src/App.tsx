import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import type { FormEvent, MouseEvent, ReactNode } from "react";
import ArteJogo from "./ArteJogo";
import {
  cadastrarCliente,
  consultarUsuario,
  encerrarSessao,
  entrar,
  ErroDaApi,
  guardarSessao,
  lerSessao,
  precoEmReais,
  useConsulta,
} from "./api";
import type {
  ClienteCadastrado,
  DetalheDoJogo,
  Jogo,
  PaginaDeJogos,
  SessaoLocal,
} from "./api";

function irPara(endereco: string, substituir = false) {
  if (`${location.pathname}${location.search}` === endereco) return;
  history[substituir ? "replaceState" : "pushState"]({}, "", endereco);
  dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0 });
}

function navegar(evento: MouseEvent<HTMLAnchorElement>, endereco: string) {
  if (
    evento.button !== 0 ||
    evento.ctrlKey ||
    evento.metaKey ||
    evento.shiftKey ||
    evento.altKey
  )
    return;
  evento.preventDefault();
  irPara(endereco);
}

function Link({
  href,
  children,
  ...props
}: React.AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string;
  children: ReactNode;
}) {
  return (
    <a {...props} href={href} onClick={(e) => navegar(e, href)}>
      {children}
    </a>
  );
}

function assinar(avisar: () => void) {
  window.addEventListener("popstate", avisar);
  return () => window.removeEventListener("popstate", avisar);
}

function Controle({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 44 34"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 5h20c4 0 6 3 7 7l3 14c1 5-4 8-7 4l-7-8H16l-7 8c-3 4-8 1-7-4l3-14c1-4 3-7 7-7Z"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path d="M12 10v10m-5-5h10" stroke="currentColor" strokeWidth="2.5" />
      <circle cx="29" cy="12" r="2" fill="currentColor" />
      <circle cx="34" cy="17" r="2" fill="currentColor" />
    </svg>
  );
}

function EstadoDaTela({
  titulo,
  children,
  erro = false,
}: {
  titulo: string;
  children: ReactNode;
  erro?: boolean;
}) {
  return (
    <section
      className="estado-tela"
      role={erro ? "alert" : "status"}
      data-cy={erro ? "erro" : "estado-vazio"}
    >
      <span className="estado-icone" aria-hidden="true">
        {erro ? "!" : "◇"}
      </span>
      <h2>{titulo}</h2>
      {children}
    </section>
  );
}

function Falha({
  tentarNovamente,
  detalhe = false,
}: {
  tentarNovamente: () => void;
  detalhe?: boolean;
}) {
  return (
    <EstadoDaTela
      erro
      titulo={
        detalhe
          ? "Não foi possível carregar o jogo"
          : "Não foi possível carregar os jogos"
      }
    >
      <p>
        {detalhe
          ? "A consulta aos detalhes falhou."
          : "A conexão com o catálogo falhou."}{" "}
        Tente novamente em instantes.
      </p>
      <button
        className="botao"
        onClick={tentarNovamente}
        data-cy="tentar-novamente"
      >
        Tentar novamente <span aria-hidden="true">↻</span>
      </button>
    </EstadoDaTela>
  );
}

function Card({ jogo, pagina }: { jogo: Jogo; pagina: number }) {
  const esgotado = jogo.disponibilidade === "Esgotado";
  return (
    <article className="card-jogo" data-cy="jogo" data-jogo-id={jogo.id}>
      <Link
        href={`/jogos/${jogo.id}?origem=${pagina}`}
        className="card-link"
        aria-label={`Ver detalhes de ${jogo.nome}. ${precoEmReais(jogo.preco)}. ${jogo.disponibilidade}.`}
      >
        <div className="capa">
          <ArteJogo jogo={jogo} />
          <span
            className={`selo${esgotado ? " selo-esgotado" : ""}`}
            data-cy="disponibilidade"
          >
            <span />
            {jogo.disponibilidade}
          </span>
        </div>
        <div className="card-conteudo">
          <span className="tipo-produto">CHAVE DIGITAL</span>
          <h3>{jogo.nome}</h3>
          <div className="card-rodape">
            <strong data-cy="preco">{precoEmReais(jogo.preco)}</strong>
            <span className="abrir-jogo" aria-hidden="true">
              ↗
            </span>
          </div>
        </div>
      </Link>
    </article>
  );
}

function Paginacao({ pagina, total }: { pagina: number; total: number }) {
  if (total <= 1) return null;
  const paginas = Array.from(
    new Set([1, pagina - 1, pagina, pagina + 1, total]),
  )
    .filter((n) => n >= 1 && n <= total)
    .sort((a, b) => a - b);
  return (
    <nav
      className="paginacao"
      aria-label="Páginas do catálogo"
      data-cy="paginacao"
    >
      {pagina > 1 ? (
        <Link
          href={`/?pagina=${pagina - 1}`}
          className="pagina-direcao"
          data-cy="pagina-anterior"
        >
          ← <span>Anterior</span>
        </Link>
      ) : (
        <span className="pagina-direcao desabilitada" aria-disabled="true">
          ← <span>Anterior</span>
        </span>
      )}
      <div className="numeros-pagina">
        {paginas.map((n, indice) => (
          <span key={n} className="numero-grupo">
            {indice > 0 && n - paginas[indice - 1] > 1 && (
              <span className="reticencias">…</span>
            )}
            <Link
              href={`/?pagina=${n}`}
              className={`numero-pagina${n === pagina ? " atual" : ""}`}
              aria-label={`Página ${n}`}
              aria-current={n === pagina ? "page" : undefined}
            >
              {n}
            </Link>
          </span>
        ))}
      </div>
      {pagina < total ? (
        <Link
          href={`/?pagina=${pagina + 1}`}
          className="pagina-direcao"
          data-cy="proxima-pagina"
        >
          <span>Próxima</span> →
        </Link>
      ) : (
        <span className="pagina-direcao desabilitada" aria-disabled="true">
          <span>Próxima</span> →
        </span>
      )}
    </nav>
  );
}

function Catalogo({ pagina }: { pagina: number }) {
  const { estado, tentarNovamente } = useConsulta<PaginaDeJogos>(
    `/jogos?pagina=${pagina}`,
  );
  useEffect(() => {
    document.title = `Catálogo${pagina > 1 ? ` · Página ${pagina}` : ""} | GameKeys`;
  }, [pagina]);
  return (
    <>
      <section className="hero">
        <div className="hero-texto">
          <span className="sobretitulo">
            <span /> PARA O SEU PRÓXIMO PLAY
          </span>
          <h1>
            Grandes histórias.
            <br />
            <em>Novos mundos.</em>
          </h1>
          <p>
            Encontre seu próximo jogo. Explore o catálogo
            <br className="quebra-desktop" /> e escolha a sua próxima aventura.
          </p>
        </div>
        <div className="hero-arte" aria-hidden="true">
          <span className="orbita orbita-1" />
          <span className="orbita orbita-2" />
          <span className="estrela estrela-1">✦</span>
          <span className="estrela estrela-2">✦</span>
          <div className="controle-hero">
            <Controle />
          </div>
          <span className="hero-tag">UM NOVO MUNDO A CADA JOGO</span>
        </div>
      </section>
      <section
        className="catalogo"
        aria-labelledby="catalogo-titulo"
        aria-busy={estado.status === "carregando"}
      >
        <div className="titulo-catalogo">
          <div>
            <span className="sobretitulo pequeno">EXPLORE O CATÁLOGO</span>
            <h2 id="catalogo-titulo">
              Todos os jogos<span className="ponto">.</span>
            </h2>
          </div>
          <p className="contagem" aria-live="polite">
            {estado.status === "pronto" ? (
              <>
                <strong>{estado.dados.total} jogos</strong>
                <span>20 por página</span>
              </>
            ) : estado.status === "carregando" ? (
              "Consultando catálogo…"
            ) : (
              "Catálogo indisponível"
            )}
          </p>
        </div>
        {estado.status === "carregando" ? (
          <div
            className="grade-jogos"
            role="status"
            aria-label="Carregando jogos"
            data-cy="carregando"
          >
            {Array.from({ length: 8 }, (_, i) => (
              <div className="esqueleto" key={i}>
                <div />
                <span />
                <span />
              </div>
            ))}
          </div>
        ) : estado.status === "erro" ? (
          <Falha tentarNovamente={tentarNovamente} />
        ) : estado.dados.itens.length === 0 ? (
          <EstadoDaTela
            titulo={
              estado.dados.total === 0
                ? "Novas aventuras estão chegando"
                : "Esta página não tem jogos"
            }
          >
            <p>
              {estado.dados.total === 0
                ? "Não há jogos disponíveis no catálogo neste momento. Volte em breve."
                : "Volte à primeira página para continuar explorando o catálogo."}
            </p>
            {estado.dados.total > 0 && (
              <Link className="botao" href="/">
                Voltar ao catálogo →
              </Link>
            )}
          </EstadoDaTela>
        ) : (
          <>
            <div className="grade-jogos" data-cy="catalogo">
              {estado.dados.itens.map((jogo) => (
                <Card jogo={jogo} pagina={pagina} key={jogo.id} />
              ))}
            </div>
            <div className="rodape-resultados">
              <p data-cy="intervalo">
                Mostrando{" "}
                <strong>
                  {(pagina - 1) * estado.dados.por_pagina + 1}–
                  {Math.min(
                    pagina * estado.dados.por_pagina,
                    estado.dados.total,
                  )}
                </strong>{" "}
                de {estado.dados.total} jogos
              </p>
              <Paginacao pagina={pagina} total={estado.dados.total_paginas} />
            </div>
          </>
        )}
      </section>
    </>
  );
}

function Detalhe({ id, origem }: { id: string; origem: number }) {
  const { estado, tentarNovamente } = useConsulta<DetalheDoJogo>(
    `/jogos/${id}`,
  );
  const voltar = origem > 1 ? `/?pagina=${origem}` : "/";
  useEffect(() => {
    const titulo =
      estado.status === "pronto"
        ? estado.dados.nome
        : estado.status === "erro" && estado.naoEncontrado
          ? "Jogo não encontrado"
          : "Detalhe do jogo";
    document.title = `${titulo} | GameKeys`;
  }, [estado]);
  return (
    <section
      className="detalhe"
      data-cy="detalhe"
      aria-busy={estado.status === "carregando"}
    >
      <Link href={voltar} className="voltar" data-cy="voltar-catalogo">
        ← Voltar ao catálogo
      </Link>
      {estado.status === "carregando" ? (
        <div
          className="detalhe-carregando"
          role="status"
          data-cy="carregando-detalhe"
        >
          Carregando jogo…
        </div>
      ) : estado.status === "erro" ? (
        estado.naoEncontrado ? (
          <EstadoDaTela titulo="Jogo não encontrado">
            <p>Este jogo não está disponível no catálogo.</p>
            <Link href={voltar} className="botao">
              Explorar outros jogos →
            </Link>
          </EstadoDaTela>
        ) : (
          <Falha tentarNovamente={tentarNovamente} detalhe />
        )
      ) : (
        <div className="grade-detalhe">
          <ArteJogo jogo={estado.dados} grande />
          <div className="conteudo-detalhe">
            <span className="sobretitulo pequeno">
              {estado.dados.genero} · {estado.dados.plataforma}
            </span>
            <h1>{estado.dados.nome}</h1>
            <p className="descricao-jogo" data-cy="descricao-jogo">
              {estado.dados.descricao}
            </p>
            <dl className="ficha">
              <div>
                <dt>Plataforma</dt>
                <dd data-cy="plataforma-jogo">{estado.dados.plataforma}</dd>
              </div>
              <div>
                <dt>Gênero</dt>
                <dd data-cy="genero-jogo">{estado.dados.genero}</dd>
              </div>
              <div>
                <dt>Classificação</dt>
                <dd data-cy="classificacao-jogo">
                  {estado.dados.classificacao === "L"
                    ? "Livre"
                    : `${estado.dados.classificacao} anos`}
                </dd>
              </div>
            </dl>
            <div className="preco-detalhe">
              <strong data-cy="preco-jogo">
                {precoEmReais(estado.dados.preco)}
              </strong>
              <span
                data-cy="disponibilidade-jogo"
                className={
                  estado.dados.disponibilidade === "Esgotado"
                    ? "texto-esgotado"
                    : "texto-disponivel"
                }
              >
                ● {estado.dados.disponibilidade}
              </span>
            </div>
            <p className="aviso-compra">
              Explore os jogos disponíveis. As compras serão habilitadas em
              breve.
            </p>
          </div>
        </div>
      )}
    </section>
  );
}

type EstadoCadastro =
  | { tipo: "inicial" }
  | { tipo: "enviando" }
  | { tipo: "sucesso"; nome: string }
  | { tipo: "erro"; mensagem: string };

function Cadastro() {
  const [estado, setEstado] = useState<EstadoCadastro>({ tipo: "inicial" });
  const [dados, setDados] = useState({
    nome: "",
    email: "",
    data_nascimento: "",
    senha: "",
  });
  useEffect(() => {
    document.title = "Criar conta | GameKeys";
  }, []);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (dados.senha.length < 8) {
      setEstado({
        tipo: "erro",
        mensagem: "A senha deve ter pelo menos 8 caracteres.",
      });
      return;
    }
    setEstado({ tipo: "enviando" });
    try {
      const cliente = await cadastrarCliente(dados);
      setDados((atual) => ({ ...atual, senha: "" }));
      setEstado({ tipo: "sucesso", nome: cliente.nome });
    } catch (erro) {
      setEstado({
        tipo: "erro",
        mensagem:
          erro instanceof Error
            ? erro.message
            : "Não foi possível concluir o cadastro. Tente novamente.",
      });
    }
  }

  const alterar = (campo: keyof typeof dados, valor: string) => {
    setDados((atual) => ({ ...atual, [campo]: valor }));
    if (estado.tipo === "erro") setEstado({ tipo: "inicial" });
  };

  return (
    <section className="acesso" aria-labelledby="cadastro-titulo">
      <div className="acesso-apresentacao">
        <span className="sobretitulo pequeno">SUA CONTA GAMEKEYS</span>
        <h1 id="cadastro-titulo">
          Comece sua próxima <em>aventura.</em>
        </h1>
        <p>
          Crie sua conta de cliente para preparar suas próximas compras de jogos
          digitais.
        </p>
        <Link href="/" className="voltar-catalogo-acesso">
          ← Continuar explorando o catálogo
        </Link>
      </div>
      <div className="painel-acesso">
        <h2>Criar conta</h2>
        <p className="instrucao-formulario">
          Preencha seus dados para se cadastrar.
        </p>
        {estado.tipo === "sucesso" ? (
          <div
            className="cadastro-sucesso"
            role="status"
            data-cy="cadastro-sucesso"
          >
            <span aria-hidden="true">✓</span>
            <h3>Conta criada com sucesso</h3>
            <p>{estado.nome}, seu cadastro como Cliente foi concluído.</p>
            <Link href="/login" className="botao">
              Entrar na minha conta →
            </Link>
          </div>
        ) : (
          <form onSubmit={enviar} data-cy="formulario-cadastro">
            <label>
              Nome
              <input
                name="nome"
                autoComplete="name"
                value={dados.nome}
                onChange={(e) => alterar("nome", e.target.value)}
                minLength={2}
                maxLength={120}
                required
              />
            </label>
            <label>
              E-mail
              <input
                name="email"
                type="email"
                autoComplete="email"
                value={dados.email}
                onChange={(e) => alterar("email", e.target.value)}
                required
              />
            </label>
            <label>
              Data de nascimento
              <input
                name="data_nascimento"
                type="date"
                autoComplete="bday"
                max={new Date().toISOString().slice(0, 10)}
                value={dados.data_nascimento}
                onChange={(e) => alterar("data_nascimento", e.target.value)}
                required
              />
            </label>
            <label>
              Senha
              <input
                name="senha"
                type="password"
                autoComplete="new-password"
                value={dados.senha}
                onChange={(e) => alterar("senha", e.target.value)}
                aria-describedby="ajuda-senha"
                required
              />
              <small id="ajuda-senha">Use pelo menos 8 caracteres.</small>
            </label>
            {estado.tipo === "erro" && (
              <p
                className="erro-formulario"
                role="alert"
                data-cy="erro-cadastro"
              >
                {estado.mensagem}
              </p>
            )}
            <button
              className="botao botao-formulario"
              disabled={estado.tipo === "enviando"}
              data-cy="enviar-cadastro"
            >
              {estado.tipo === "enviando"
                ? "Criando conta…"
                : "Criar minha conta"}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

type EstadoLogin =
  | { tipo: "inicial" }
  | { tipo: "enviando" }
  | { tipo: "erro"; mensagem: string };

function Login({ aoEntrar }: { aoEntrar: (sessao: SessaoLocal) => void }) {
  const [estado, setEstado] = useState<EstadoLogin>({ tipo: "inicial" });
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const sessaoExpirada = new URL(location.href).searchParams.has("expirada");
  useEffect(() => {
    document.title = "Entrar | GameKeys";
  }, []);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setEstado({ tipo: "enviando" });
    try {
      const criada = await entrar(email, senha);
      aoEntrar(guardarSessao(criada));
    } catch (erro) {
      setEstado({
        tipo: "erro",
        mensagem:
          erro instanceof Error
            ? erro.message
            : "Não foi possível entrar. Tente novamente.",
      });
    }
  }

  return (
    <section className="acesso" aria-labelledby="login-titulo">
      <div className="acesso-apresentacao">
        <span className="sobretitulo pequeno">BEM-VINDO DE VOLTA</span>
        <h1 id="login-titulo">
          Continue sua próxima <em>aventura.</em>
        </h1>
        <p>Entre com sua conta para acessar sua área protegida.</p>
        <Link href="/" className="voltar-catalogo-acesso">
          ← Continuar explorando o catálogo
        </Link>
      </div>
      <div className="painel-acesso">
        <h2>Entrar</h2>
        <p className="instrucao-formulario">
          Use o e-mail e a senha informados no cadastro.
        </p>
        {sessaoExpirada && estado.tipo !== "erro" && (
          <p className="aviso-sessao" role="status" data-cy="sessao-expirada">
            Sua sessão expirou. Entre novamente para continuar.
          </p>
        )}
        <form onSubmit={enviar} data-cy="formulario-login">
          <label>
            E-mail
            <input
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (estado.tipo === "erro") setEstado({ tipo: "inicial" });
              }}
              required
            />
          </label>
          <label>
            Senha
            <input
              name="senha"
              type="password"
              autoComplete="current-password"
              value={senha}
              onChange={(e) => {
                setSenha(e.target.value);
                if (estado.tipo === "erro") setEstado({ tipo: "inicial" });
              }}
              required
            />
          </label>
          {estado.tipo === "erro" && (
            <p className="erro-formulario" role="alert" data-cy="erro-login">
              {estado.mensagem}
            </p>
          )}
          <button
            className="botao botao-formulario"
            disabled={estado.tipo === "enviando"}
            data-cy="enviar-login"
          >
            {estado.tipo === "enviando" ? "Entrando…" : "Entrar"}
          </button>
        </form>
        <p className="alternativa-acesso">
          Ainda não tem conta? <Link href="/cadastro">Cadastre-se</Link>
        </p>
      </div>
    </section>
  );
}

type EstadoConta =
  | { tipo: "carregando" }
  | { tipo: "pronto"; usuario: ClienteCadastrado }
  | { tipo: "erro"; mensagem: string };

function Conta({
  sessao,
  aoExpirar,
  aoSair,
}: {
  sessao: SessaoLocal;
  aoExpirar: () => void;
  aoSair: () => void;
}) {
  const [tentativa, setTentativa] = useState(0);
  const [estado, setEstado] = useState<EstadoConta>({ tipo: "carregando" });
  useEffect(() => {
    document.title = "Minha conta | GameKeys";
    let ativa = true;
    setEstado({ tipo: "carregando" });
    consultarUsuario(sessao.token)
      .then((usuario) => {
        if (ativa) setEstado({ tipo: "pronto", usuario });
      })
      .catch((erro) => {
        if (!ativa) return;
        if (erro instanceof ErroDaApi && erro.status === 401) {
          aoExpirar();
          return;
        }
        setEstado({
          tipo: "erro",
          mensagem:
            erro instanceof Error
              ? erro.message
              : "Não foi possível carregar sua conta.",
        });
      });
    return () => {
      ativa = false;
    };
  }, [sessao.token, tentativa, aoExpirar]);

  return (
    <section className="conta" data-cy="conta-protegida">
      {estado.tipo === "carregando" ? (
        <div className="detalhe-carregando" role="status">
          Validando sua sessão…
        </div>
      ) : estado.tipo === "erro" ? (
        <EstadoDaTela erro titulo="Não foi possível carregar sua conta">
          <p>{estado.mensagem}</p>
          <button className="botao" onClick={() => setTentativa((n) => n + 1)}>
            Tentar novamente
          </button>
        </EstadoDaTela>
      ) : (
        <div className="painel-conta">
          <span className="sobretitulo pequeno">ÁREA PROTEGIDA</span>
          <h1>Olá, {estado.usuario.nome}</h1>
          <p>Sua sessão está autenticada como Cliente.</p>
          <dl>
            <div>
              <dt>E-mail</dt>
              <dd>{estado.usuario.email}</dd>
            </div>
            <div>
              <dt>Data de nascimento</dt>
              <dd>
                {new Date(
                  `${estado.usuario.data_nascimento}T00:00:00`,
                ).toLocaleDateString("pt-BR")}
              </dd>
            </div>
          </dl>
          <div className="acoes-conta">
            <Link href="/" className="botao">
              Explorar catálogo
            </Link>
            <button
              className="botao botao-secundario"
              onClick={aoSair}
              data-cy="sair"
            >
              Sair
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

function RedirecionarParaLogin() {
  useEffect(() => {
    irPara("/login", true);
  }, []);
  return <div className="detalhe-carregando">Redirecionando para o login…</div>;
}

export default function App() {
  const endereco = useSyncExternalStore(
    assinar,
    () => `${location.pathname}${location.search}`,
  );
  const [sessao, setSessao] = useState<SessaoLocal | null>(() => lerSessao());
  const url = new URL(endereco, location.origin);
  const paginaValida = (valor: string | null) =>
    valor &&
    /^\d+$/.test(valor) &&
    Number(valor) >= 1 &&
    Number(valor) <= 2147483647
      ? Number(valor)
      : 1;
  const detalhe = url.pathname.match(/^\/jogos\/(\d+)\/?$/);
  const ehCatalogo = url.pathname === "/" || url.pathname === "/catalogo";
  const ehCadastro = url.pathname === "/cadastro";
  const ehLogin = url.pathname === "/login";
  const ehConta = url.pathname === "/conta";

  const expirarSessao = useCallback(() => {
    encerrarSessao();
    setSessao(null);
    irPara("/login?expirada=1", true);
  }, []);
  const sair = useCallback(() => {
    encerrarSessao();
    setSessao(null);
    irPara("/login", true);
  }, []);

  useEffect(() => {
    if (!sessao) return;
    const restante = sessao.expiraEm - Date.now();
    if (restante <= 0) {
      if (location.pathname === "/conta") expirarSessao();
      else {
        encerrarSessao();
        setSessao(null);
      }
      return;
    }
    const temporizador = window.setTimeout(() => {
      if (location.pathname === "/conta") expirarSessao();
      else {
        encerrarSessao();
        setSessao(null);
      }
    }, restante);
    return () => clearTimeout(temporizador);
  }, [sessao, expirarSessao]);
  useEffect(() => {
    document.getElementById("conteudo")?.focus({ preventScroll: true });
  }, [endereco]);

  return (
    <>
      <a className="pular" href="#conteudo">
        Pular para o conteúdo
      </a>
      <header className="cabecalho">
        <div className="largura cabecalho-conteudo">
          <Link href="/" className="marca" aria-label="GameKeys, início">
            <span className="marca-icone">
              <Controle />
            </span>
            <span>
              Game<span className="marca-keys">Keys</span>
              <span className="marca-ponto">.</span>
            </span>
          </Link>
          <nav className="navegacao-principal" aria-label="Menu principal">
            <Link
              href="/"
              className="nav-catalogo"
              aria-current={ehCatalogo ? "page" : undefined}
            >
              Catálogo
            </Link>
            {!sessao && (
              <Link
                href="/cadastro"
                className="nav-cadastro"
                aria-current={ehCadastro ? "page" : undefined}
              >
                Criar conta
              </Link>
            )}
            {sessao ? (
              <>
                <Link
                  href="/conta"
                  className="nav-acesso"
                  aria-current={ehConta ? "page" : undefined}
                >
                  Minha conta
                </Link>
                <button className="nav-sair" onClick={sair}>
                  Sair
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="nav-acesso"
                aria-current={ehLogin ? "page" : undefined}
              >
                Entrar
              </Link>
            )}
          </nav>
          <span className="cabecalho-nota">
            <span /> Jogos digitais, novas possibilidades
          </span>
        </div>
      </header>
      <main id="conteudo" className="largura" tabIndex={-1}>
        {ehCadastro ? (
          <Cadastro />
        ) : ehLogin ? (
          <Login
            aoEntrar={(novaSessao) => {
              setSessao(novaSessao);
              irPara("/conta", true);
            }}
          />
        ) : ehConta ? (
          sessao ? (
            <Conta sessao={sessao} aoExpirar={expirarSessao} aoSair={sair} />
          ) : (
            <RedirecionarParaLogin />
          )
        ) : detalhe ? (
          <Detalhe
            key={detalhe[1]}
            id={detalhe[1]}
            origem={paginaValida(url.searchParams.get("origem"))}
          />
        ) : ehCatalogo ? (
          <Catalogo pagina={paginaValida(url.searchParams.get("pagina"))} />
        ) : (
          <EstadoDaTela titulo="Página não encontrada">
            <p>Continue explorando os jogos do GameKeys.</p>
            <Link href="/" className="botao">
              Ir para o catálogo →
            </Link>
          </EstadoDaTela>
        )}
      </main>
      <footer className="rodape">
        <div className="largura rodape-conteudo">
          <span className="marca-rodape">
            GameKeys<span>.</span>
          </span>
          <p>Seu próximo jogo começa aqui.</p>
          <span className="projeto">Projeto acadêmico · UEPB 2026.2</span>
        </div>
      </footer>
    </>
  );
}
