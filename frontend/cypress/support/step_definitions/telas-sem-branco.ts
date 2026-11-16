import { Given, Then, When } from "@badeball/cypress-cucumber-preprocessor";

const jogos = Array.from({ length: 3 }, (_, indice) => ({
  id: indice + 1,
  slug: `falha-${indice + 1}`,
  nome: `Jogo ${indice + 1}`,
  capa_url: null,
  preco: "49.90",
  disponibilidade: "Disponível",
}));

Given("que o catálogo responde, mas a tela falha ao formatar os preços", () => {
  cy.intercept("GET", "**/api/jogos?*", {
    itens: jogos,
    pagina: 1,
    por_pagina: 20,
    total: 3,
    total_paginas: 1,
  }).as("catalogo");
});

When("abro o catálogo com a falha de desenho", () => {
  cy.visit("/", {
    onBeforeLoad(janela) {
      // Simula um defeito de código: formatar um preço lança erro e derruba o desenho da tela.
      janela.Intl.NumberFormat.prototype.formatToParts = () => {
        throw new Error("falha simulada ao formatar o preço");
      };
    },
  });
});

When("escolho voltar ao catálogo pelo aviso de falha", () => {
  cy.get("[data-cy=erro-inesperado]")
    .contains("a", "Ir para o catálogo")
    .click();
});

Then(
  "vejo o aviso de falha inesperada com as opções de recarregar e voltar ao catálogo",
  () => {
    cy.get("[data-cy=erro-inesperado]")
      .should("be.visible")
      .and("have.attr", "role", "alert")
      .and("contain", "Algo deu errado nesta tela");
    cy.get("[data-cy=erro-inesperado]")
      .contains("button", "Recarregar a página")
      .should("be.visible");
    cy.get("[data-cy=erro-inesperado]")
      .contains("a", "Ir para o catálogo")
      .should("have.attr", "href", "/");
  },
);

Then("o menu principal continua na tela", () => {
  cy.get("nav[aria-label='Menu principal']").should("be.visible");
});

Then("volto a ver os cartões do catálogo", () => {
  cy.get("[data-cy=erro-inesperado]").should("not.exist");
  cy.get("[data-cy=jogo]").should("have.length", 3);
});
