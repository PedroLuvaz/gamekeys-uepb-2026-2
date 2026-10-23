import { Given, When, Then } from "@badeball/cypress-cucumber-preprocessor";

const jogos = Array.from({ length: 23 }, (_, indice) => ({
  id: indice + 1,
  nome: `Aventura ${String(indice + 1).padStart(2, "0")}`,
  capa_url: null,
  preco: "49.90",
  disponibilidade: indice === 22 ? "Esgotado" : "Disponível",
}));

let recuperarCatalogo = () => {};

const respostaDaPagina = (pagina: number) => ({
  itens: jogos.slice((pagina - 1) * 20, pagina * 20),
  pagina,
  por_pagina: 20,
  total: 23,
  total_paginas: 2,
});

function simularCatalogo(atraso = 0, capaIndisponivel = false) {
  cy.intercept("GET", "**/api/jogos?*", (pedido) => {
    const pagina = Number(new URL(pedido.url).searchParams.get("pagina") || 1);
    const resposta = respostaDaPagina(pagina);
    pedido.reply({
      body: capaIndisponivel
        ? {
            ...resposta,
            itens: resposta.itens.map((jogo) => ({
              ...jogo,
              capa_url: "/capa-indisponivel.png",
            })),
          }
        : resposta,
      delay: atraso,
    });
  }).as("catalogo");
  cy.intercept("GET", "**/api/jogos/23", {
    ...jogos[22],
    descricao: "Uma aventura em novos mundos.",
    genero: "Aventura",
    plataforma: "PC",
    classificacao: "12",
  }).as("detalhe");
}

Given("que o catálogo responde com 23 jogos ativos", () => simularCatalogo());
Given("que o catálogo está vazio", () => {
  cy.intercept("GET", "**/api/jogos?*", {
    itens: [],
    pagina: 1,
    por_pagina: 20,
    total: 0,
    total_paginas: 0,
  }).as("catalogo");
});
Given("que a primeira consulta ao catálogo falha", () => {
  let indisponivel = true;
  recuperarCatalogo = () => {
    indisponivel = false;
  };
  cy.intercept("GET", "**/api/jogos?*", (pedido) => {
    if (indisponivel) {
      pedido.reply({
        statusCode: 503,
        body: { detail: "Catálogo indisponível." },
      });
    } else pedido.reply({ body: respostaDaPagina(1) });
  }).as("catalogo");
});
Given("que a consulta ao catálogo demora para responder", () =>
  simularCatalogo(1200),
);
Given("uso uma tela de celular", () => cy.viewport(390, 844));
Given("que um jogo tem uma capa indisponível", () => {
  simularCatalogo(0, true);
  cy.intercept("GET", "**/capa-indisponivel.png", {
    statusCode: 404,
    body: "",
  });
});
Given("que a consulta de detalhe não encontra o jogo", () => {
  cy.intercept("GET", "**/api/jogos/99999", {
    statusCode: 404,
    body: { detail: "Jogo não encontrado." },
  }).as("detalhe");
});

When("abro o catálogo", () => cy.visit("/"));
When("abro a segunda página do catálogo", () => cy.visit("/?pagina=2"));
When("abro a terceira página do catálogo", () => cy.visit("/?pagina=3"));
When("avanço para a próxima página", () =>
  cy.get('[data-cy="proxima-pagina"]').click(),
);
When("abro a ficha do jogo esgotado", () =>
  cy.get('[data-jogo-id="23"] a').click(),
);
When("volto ao catálogo", () => cy.get('[data-cy="voltar-catalogo"]').click());
When("tento novamente", () => {
  recuperarCatalogo();
  cy.get('[data-cy="tentar-novamente"]').click();
});
When("abro o endereço direto desse jogo", () => cy.visit("/jogos/99999"));
When("uso o voltar do navegador", () => cy.go("back"));
When("uso o avançar do navegador", () => cy.go("forward"));
When("recarrego a página", () => cy.reload());

Then("vejo 20 cartões e os preços em reais", () => {
  cy.get('[data-cy="jogo"]').should("have.length", 20);
  cy.get('[data-cy="preco"]').first().should("contain.text", "49,90");
  cy.get('[data-cy="intervalo"]').should("contain.text", "1–20");
  cy.get('[data-cy="jogo"] h3').then(($nomes) => {
    expect([...$nomes].map((el) => el.textContent)).to.deep.equal(
      jogos.slice(0, 20).map((j) => j.nome),
    );
  });
});
Then("vejo os 3 jogos restantes e o intervalo correto", () => {
  cy.location("search").should("contain", "pagina=2");
  cy.get('[data-cy="jogo"]').should("have.length", 3);
  cy.get('[data-cy="intervalo"]').should("contain.text", "21–23");
  cy.get('[data-cy="jogo"] h3').then(($nomes) => {
    expect([...$nomes].map((el) => el.textContent)).to.deep.equal(
      jogos.slice(20).map((j) => j.nome),
    );
  });
});
Then("posso voltar para a primeira página", () => {
  cy.get('[data-cy="pagina-anterior"]').click();
  cy.get('[data-cy="jogo"]').should("have.length", 20);
  cy.get('[data-cy="intervalo"]').should("contain.text", "1–20");
});
Then("o jogo sem chaves aparece como esgotado", () => {
  cy.get('[data-jogo-id="23"]').should("contain.text", "Esgotado");
});
Then("vejo os dados e a disponibilidade do jogo", () => {
  cy.get("h1").should("have.text", "Aventura 23");
  cy.get('[data-cy="detalhe"]')
    .should("contain.text", "Esgotado")
    .and("contain.text", "PC")
    .and("contain.text", "12 anos");
});
Then("vejo uma mensagem de catálogo vazio", () => {
  cy.get('[data-cy="estado-vazio"]').should(
    "contain.text",
    "Novas aventuras estão chegando",
  );
  cy.get('[data-cy="jogo"]').should("not.exist");
});
Then("vejo uma mensagem de falha e a opção de tentar novamente", () => {
  cy.get('[data-cy="erro"]').should(
    "contain.text",
    "Não foi possível carregar os jogos",
  );
  cy.get('[data-cy="tentar-novamente"]').should("be.visible");
});
Then("vejo o estado de carregamento antes dos cartões", () => {
  cy.get('[data-cy="carregando"]').should("be.visible");
  cy.get('[data-cy="jogo"]').should("have.length", 20);
});
Then("posso retornar ao catálogo pela mensagem de página vazia", () => {
  cy.get('[data-cy="estado-vazio"]').should(
    "contain.text",
    "Esta página não tem jogos",
  );
  cy.contains("a", "Voltar ao catálogo").click();
  cy.get('[data-cy="jogo"]').should("have.length", 20);
});
Then("a página cabe na largura da tela", () => {
  cy.document().then((doc) =>
    expect(doc.documentElement.scrollWidth).to.be.at.most(390),
  );
});
Then("vejo a mensagem de jogo não encontrado", () => {
  cy.get('[data-cy="estado-vazio"]').should(
    "contain.text",
    "Jogo não encontrado",
  );
});
Then("vejo a ilustração de apoio no lugar da capa com falha", () => {
  cy.get('[data-jogo-id="1"] .arte-legenda').should("be.visible");
  cy.get('[data-jogo-id="1"] img').should("not.exist");
});
