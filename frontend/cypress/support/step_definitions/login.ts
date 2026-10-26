import { Given, When, Then } from "@badeball/cypress-cucumber-preprocessor";

const usuario = {
  id: 9,
  nome: "Cliente Login",
  email: "cliente@example.com",
  data_nascimento: "2000-01-01",
  perfil: "cliente",
};

function guardarSessao(win: Window, token = "token-valido") {
  win.sessionStorage.setItem(
    "gamekeys.sessao",
    JSON.stringify({ token, expiraEm: Date.now() + 3_600_000, usuario }),
  );
}

Given("que a API autentica o cliente", () => {
  cy.intercept("POST", "**/api/auth/login", {
    access_token: "token-valido",
    token_type: "bearer",
    expires_in: 3600,
    usuario,
  }).as("login");
  cy.intercept("GET", "**/api/auth/me", usuario).as("sessao");
});

Given("que a API recusa as credenciais", () => {
  cy.intercept("POST", "**/api/auth/login", {
    statusCode: 401,
    body: { detail: "E-mail ou senha incorretos." },
  }).as("login");
});

Given("que tenho uma sessão local que o servidor considera inválida", () => {
  cy.intercept("GET", "**/api/auth/me", {
    statusCode: 401,
    body: { detail: "Não foi possível autenticar. Entre novamente." },
  }).as("sessao");
});

Given("que tenho uma sessão válida", () => {
  cy.intercept("GET", "**/api/auth/me", usuario).as("sessao");
});

When("abro o login", () => cy.visit("/login"));

When("informo credenciais válidas", () => {
  cy.get('input[name="email"]').type("cliente@example.com");
  cy.get('input[name="senha"]').type("segredo123");
});

When("informo credenciais inválidas", () => {
  cy.get('input[name="email"]').type("cliente@example.com");
  cy.get('input[name="senha"]').type("senha-errada");
});

When("envio o login", () => cy.get('[data-cy="enviar-login"]').click());

When("abro minha conta", () => {
  cy.visit("/conta", { onBeforeLoad: (win) => guardarSessao(win) });
});

When("encerro a sessão", () => {
  cy.wait("@sessao");
  cy.get('[data-cy="sair"]').click();
});

Then("vejo minha área protegida", () => {
  cy.wait("@login");
  cy.wait("@sessao");
  cy.location("pathname").should("eq", "/conta");
  cy.get('[data-cy="conta-protegida"]').should("contain.text", "Cliente Login");
});

Then("vejo uma mensagem genérica de credenciais incorretas", () => {
  cy.wait("@login");
  cy.get('[data-cy="erro-login"]')
    .should("contain.text", "E-mail ou senha incorretos.")
    .and("not.contain.text", "senha-errada");
});

Then("volto ao login com o aviso de sessão expirada", () => {
  cy.wait("@sessao");
  cy.location("pathname").should("eq", "/login");
  cy.location("search").should("contain", "expirada=1");
  cy.get('[data-cy="sessao-expirada"]').should("be.visible");
  cy.window()
    .its("sessionStorage")
    .invoke("getItem", "gamekeys.sessao")
    .should("be.null");
});

Then("volto ao login sem manter o token", () => {
  cy.location("pathname").should("eq", "/login");
  cy.window()
    .its("sessionStorage")
    .invoke("getItem", "gamekeys.sessao")
    .should("be.null");
});
