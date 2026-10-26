// Exercita formulário, API e PostgreSQL reais. O e-mail único evita dependência entre execuções.
describe("Cadastro com API real — GK-7", () => {
  it("persiste a conta e recusa o mesmo e-mail na tentativa seguinte", () => {
    const email = `cypress-${Date.now()}@example.com`;

    cy.visit("/cadastro");
    cy.get('input[name="nome"]').type("Cliente Cypress");
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="data_nascimento"]').type("2000-05-20");
    cy.get('input[name="senha"]').type("segredo123");
    cy.get('[data-cy="enviar-cadastro"]').click();
    cy.get('[data-cy="cadastro-sucesso"]')
      .should("contain.text", "Conta criada com sucesso")
      .and("contain.text", "Cliente Cypress");

    cy.visit("/cadastro");
    cy.get('input[name="nome"]').type("Cliente Repetido");
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="data_nascimento"]').type("2000-05-20");
    cy.get('input[name="senha"]').type("segredo123");
    cy.get('[data-cy="enviar-cadastro"]').click();
    cy.get('[data-cy="erro-cadastro"]').should(
      "contain.text",
      "Este e-mail já está em uso.",
    );
  });
});
