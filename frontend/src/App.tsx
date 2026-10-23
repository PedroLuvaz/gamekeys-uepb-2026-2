import { useEffect, useSyncExternalStore } from "react";
import type { MouseEvent, ReactNode } from "react";
import ArteJogo from "./ArteJogo";
import { precoEmReais, useConsulta } from "./api";
import type { DetalheDoJogo, Jogo, PaginaDeJogos } from "./api";

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
  if (`${location.pathname}${location.search}` === endereco) return;
  history.pushState({}, "", endereco);
  dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0 });
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

function Falha({ tentarNovamente }: { tentarNovamente: () => void }) {
  return (
    <EstadoDaTela erro titulo="Não foi possível carregar os jogos">
      <p>A conexão com o catálogo falhou. Tente novamente em instantes.</p>
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
    document.title = `${estado.status === "pronto" ? estado.dados.nome : "Detalhe do jogo"} | GameKeys`;
  }, [estado]);
  return (
    <section className="detalhe" data-cy="detalhe">
      <Link href={voltar} className="voltar" data-cy="voltar-catalogo">
        ← Voltar ao catálogo
      </Link>
      {estado.status === "carregando" ? (
        <div className="detalhe-carregando" role="status">
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
          <Falha tentarNovamente={tentarNovamente} />
        )
      ) : (
        <div className="grade-detalhe">
          <ArteJogo jogo={estado.dados} grande />
          <div className="conteudo-detalhe">
            <span className="sobretitulo pequeno">
              {estado.dados.genero} · {estado.dados.plataforma}
            </span>
            <h1>{estado.dados.nome}</h1>
            <p className="descricao-jogo">{estado.dados.descricao}</p>
            <dl className="ficha">
              <div>
                <dt>Plataforma</dt>
                <dd>{estado.dados.plataforma}</dd>
              </div>
              <div>
                <dt>Gênero</dt>
                <dd>{estado.dados.genero}</dd>
              </div>
              <div>
                <dt>Classificação</dt>
                <dd>
                  {estado.dados.classificacao === "L"
                    ? "Livre"
                    : `${estado.dados.classificacao} anos`}
                </dd>
              </div>
            </dl>
            <div className="preco-detalhe">
              <strong>{precoEmReais(estado.dados.preco)}</strong>
              <span
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

export default function App() {
  const endereco = useSyncExternalStore(
    assinar,
    () => `${location.pathname}${location.search}`,
  );
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
          <nav aria-label="Menu principal">
            <Link
              href="/"
              className="nav-catalogo"
              aria-current={ehCatalogo ? "page" : undefined}
            >
              Catálogo
            </Link>
          </nav>
          <span className="cabecalho-nota">
            <span /> Jogos digitais, novas possibilidades
          </span>
        </div>
      </header>
      <main id="conteudo" className="largura" tabIndex={-1}>
        {detalhe ? (
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
