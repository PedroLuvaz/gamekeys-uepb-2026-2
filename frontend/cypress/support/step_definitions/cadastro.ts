import { Given, When, Then } from "@badeball/cypress-cucumber-preprocessor";

let chamadas = 0;

Given("que a API aceita um novo cliente", () => {
  cy.intercept("POST", "**/api/clientes", {
    statusCode: 201,
    body: {
      id: 7,
      nome: "Ana Cliente",
      email: "ana@example.com",
      data_nascimento: "2000-05-20",
      perfil: "cliente",
    },
  }).as("cadastro");
});

Given("que a API informa que o e-mail já está em uso", () => {
  cy.intercept("POST", "**/api/clientes", {
    statusCode: 409,
    body: { detail: "Este e-mail já está em uso." },
  }).as("cadastro");
});

Given("que observo as chamadas de cadastro", () => {
  chamadas = 0;
  cy.intercept("POST", "**/api/clientes", (pedido) => {
    chamadas += 1;
    pedido.reply({ statusCode: 500 });
  });
});

When("abro o cadastro", () => cy.visit("/cadastro"));

When("preencho dados válidos", () => {
  cy.get('input[name="nome"]').type("Ana Cliente");
  cy.get('input[name="email"]').type("ana@example.com");
  cy.get('input[name="data_nascimento"]').type("2000-05-20");
  cy.get('input[name="senha"]').type("segredo123");
});

When("preencho uma senha com menos de 8 caracteres", () => {
  cy.get('input[name="nome"]').type("Ana Cliente");
  cy.get('input[name="email"]').type("ana@example.com");
  cy.get('input[name="data_nascimento"]').type("2000-05-20");
  cy.get('input[name="senha"]').type("1234567");
});

When("envio o cadastro", () => cy.get('[data-cy="enviar-cadastro"]').click());

Then("vejo a confirmação da conta Cliente", () => {
  cy.wait("@cadastro");
  cy.get('[data-cy="cadastro-sucesso"]')
    .should("contain.text", "Conta criada com sucesso")
    .and("contain.text", "Cliente");
});

Then("vejo o aviso de e-mail em uso", () => {
  cy.wait("@cadastro");
  cy.get('[data-cy="erro-cadastro"]').should(
    "contain.text",
    "Este e-mail já está em uso.",
  );
});

Then("o formulário continua disponível", () => {
  cy.get('[data-cy="formulario-cadastro"]').should("be.visible");
  cy.get('input[name="email"]').should("have.value", "ana@example.com");
});

Then("vejo o motivo da senha inválida", () => {
  cy.get('[data-cy="erro-cadastro"]').should(
    "contain.text",
    "A senha deve ter pelo menos 8 caracteres.",
  );
});

Then("nenhuma chamada de cadastro é enviada", () => {
  cy.then(() => expect(chamadas).to.equal(0));
});
