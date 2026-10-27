import {
  Before,
  Given,
  When,
  Then,
} from "@badeball/cypress-cucumber-preprocessor";

interface JogoDetalhado {
  id: number;
  slug: string;
  nome: string;
  capa_url: string | null;
  descricao: string;
  genero: string;
  plataforma: string;
  classificacao: string;
  preco: string;
  disponibilidade: string;
}

let dados: { ativo: JogoDetalhado; esgotado: JogoDetalhado };
let jogoEmTeste: JogoDetalhado;
let idConsultado: number;
let recuperarDetalhe = () => {};
let redeInterrompida = false;

Before({ tags: "@US-10" }, () => {
  cy.fixture("detalhe-jogo").then((fixture) => {
    dados = fixture;
    jogoEmTeste = dados.ativo;
    idConsultado = jogoEmTeste.id;
    recuperarDetalhe = () => {};
    redeInterrompida = false;
  });
});

function simularLista() {
  const jogos = Array.from({ length: 23 }, (_, indice) => ({
    ...dados.ativo,
    id: 101 + indice,
    nome: indice === 0 ? dados.ativo.nome : `Jogo de teste ${indice + 1}`,
  }));
  jogos[22] = dados.esgotado;
  cy.intercept("GET", "**/api/jogos?*", (pedido) => {
    const pagina = Number(new URL(pedido.url).searchParams.get("pagina") || 1);
    pedido.reply({
      itens: jogos.slice((pagina - 1) * 20, pagina * 20),
      pagina,
      por_pagina: 20,
      total: 23,
      total_paginas: 2,
    });
  }).as("listaDoDetalhe");
}

function simularDetalhe(
  opcoes: { atraso?: number; falha?: "servico" | "rede" } = {},
) {
  let falhando = Boolean(opcoes.falha);
  redeInterrompida = opcoes.falha === "rede";
  recuperarDetalhe = () => {
    falhando = false;
    redeInterrompida = false;
  };
  cy.intercept("GET", `**/api/jogos/${idConsultado}`, (pedido) => {
    if (falhando && opcoes.falha === "servico") {
      pedido.reply({
        statusCode: 503,
        body: { detail: "Catálogo indisponível." },
      });
    } else pedido.reply({ body: jogoEmTeste, delay: opcoes.atraso || 0 });
  }).as("consultaDoDetalhe");
  simularLista();
}

Given("que a API de detalhe contém um jogo ativo", () => simularDetalhe());
Given("que a API de detalhe contém um jogo esgotado", () => {
  jogoEmTeste = dados.esgotado;
  idConsultado = jogoEmTeste.id;
  simularDetalhe();
});
Given("que o jogo consultado no detalhe está {word}", (situacao: string) => {
  idConsultado = situacao === "inativo" ? 124 : 99999;
  cy.intercept("GET", `**/api/jogos/${idConsultado}`, {
    statusCode: 404,
    body: { detail: "Jogo não encontrado." },
  }).as("consultaDoDetalhe");
  simularLista();
});
Given("que a consulta do detalhe falha com resposta 503", () =>
  simularDetalhe({ falha: "servico" }),
);
Given("que a consulta do detalhe falha por interrupção da rede", () =>
  simularDetalhe({ falha: "rede" }),
);
Given("que a API de detalhe demora para responder", () =>
  simularDetalhe({ atraso: 1200 }),
);
Given("uso uma tela de 320 pixels no detalhe", () => cy.viewport(320, 740));

When("abro esse jogo pelo catálogo", () => {
  cy.visit("/");
  cy.get(`[data-jogo-id="${idConsultado}"] a`).click();
});
When("abro esse jogo na segunda página do catálogo", () => {
  cy.visit("/?pagina=2");
  cy.get(`[data-jogo-id="${idConsultado}"] a`).click();
});
When("acesso o endereço direto do jogo em teste", () => {
  cy.visit(`/jogos/${idConsultado}`, {
    onBeforeLoad(janela) {
      if (!redeInterrompida) return;
      const consultar = janela.fetch.bind(janela);
      // Rejeita no limite do fetch, evitando as novas tentativas internas do navegador.
      cy.stub(janela, "fetch").callsFake(
        (entrada: RequestInfo | URL, opcoes?: RequestInit) => {
          if (
            redeInterrompida &&
            String(entrada).includes(`/api/jogos/${idConsultado}`)
          ) {
            return Promise.reject(new TypeError("Falha de rede simulada"));
          }
          return consultar(entrada, opcoes);
        },
      );
    },
  });
});
When("a API se recupera e tento carregar o detalhe novamente", () => {
  recuperarDetalhe();
  cy.get('[data-cy="tentar-novamente"]').click();
});
When("exploro outros jogos pela mensagem de não encontrado", () =>
  cy.contains("a", "Explorar outros jogos").click(),
);

Then("os seis dados do detalhe correspondem à resposta da API", () => {
  cy.get("h1").should("have.text", jogoEmTeste.nome);
  cy.get('[data-cy="descricao-jogo"]').should(
    "have.text",
    jogoEmTeste.descricao,
  );
  cy.get('[data-cy="genero-jogo"]').should("have.text", jogoEmTeste.genero);
  cy.get('[data-cy="plataforma-jogo"]').should(
    "have.text",
    jogoEmTeste.plataforma,
  );
  cy.get('[data-cy="classificacao-jogo"]').should(
    "have.text",
    jogoEmTeste.classificacao === "L"
      ? "Livre"
      : `${jogoEmTeste.classificacao} anos`,
  );
  cy.get('[data-cy="preco-jogo"]')
    .invoke("text")
    .then((texto) => {
      expect(texto.replace(/\s/g, " ")).to.equal(
        `R$ ${Number(jogoEmTeste.preco).toFixed(2).replace(".", ",")}`,
      );
    });
  cy.get('[data-cy="disponibilidade-jogo"]').should(
    "contain.text",
    jogoEmTeste.disponibilidade,
  );
  cy.get('[data-cy="detalhe"]').should("have.attr", "aria-busy", "false");
});
Then("o título da página identifica esse jogo", () => {
  cy.title().should("eq", `${jogoEmTeste.nome} | GameKeys`);
});
Then("vejo a classificação de 14 anos e a disponibilidade Esgotado", () => {
  cy.get('[data-cy="classificacao-jogo"]').should("have.text", "14 anos");
  cy.get('[data-cy="disponibilidade-jogo"]').should("contain.text", "Esgotado");
});
Then("o detalhe informa jogo não encontrado sem exibir seus dados", () => {
  cy.get('[data-cy="estado-vazio"]').should(
    "contain.text",
    "Jogo não encontrado",
  );
  cy.get(
    '[data-cy="descricao-jogo"], [data-cy="preco-jogo"], .ficha, .arte-grande',
  ).should("not.exist");
  cy.get('[data-cy="tentar-novamente"]').should("not.exist");
  cy.title().should("eq", "Jogo não encontrado | GameKeys");
});
Then(
  "vejo uma falha de comunicação no detalhe com opção de tentar novamente",
  () => {
    cy.get('[data-cy="erro"]').should(
      "contain.text",
      "Não foi possível carregar o jogo",
    );
    cy.get('[data-cy="tentar-novamente"]').should("be.visible");
    cy.contains("Jogo não encontrado").should("not.exist");
    cy.get('[data-cy="descricao-jogo"]').should("not.exist");
  },
);
Then("o detalhe informa carregamento antes de exibir os dados", () => {
  cy.get('[data-cy="detalhe"]').should("have.attr", "aria-busy", "true");
  cy.get('[data-cy="carregando-detalhe"]').should("be.visible");
  cy.get('[data-cy="descricao-jogo"]').should("not.exist");
});
Then("retorno à primeira página do catálogo do detalhe", () => {
  cy.location("pathname").should("eq", "/");
  cy.location("search").should("eq", "");
  cy.get('[data-cy="jogo"]').should("have.length", 20);
});
Then("retorno à segunda página do catálogo do detalhe", () => {
  cy.location("search").should("eq", "?pagina=2");
  cy.get('[data-cy="jogo"]').should("have.length", 3);
});
Then("a ficha do jogo cabe na largura do celular", () => {
  cy.document().then((doc) =>
    expect(doc.documentElement.scrollWidth).to.be.at.most(320),
  );
});
