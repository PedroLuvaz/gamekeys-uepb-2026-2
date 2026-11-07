// Antes de qualquer cadastro/adição da suíte real: exigir o banco descartável da API.
before(() => {
  cy.request("/api/saude/banco")
    .its("body.banco")
    .should("eq", "gamekeys_teste");
});
