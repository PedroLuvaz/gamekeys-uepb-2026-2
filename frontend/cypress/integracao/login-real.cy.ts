describe("Login com API real — GK-8", () => {
  it("autentica o cliente persistido, abre a conta e encerra a sessão", () => {
    const email = `login-${Date.now()}@example.com`;
    const senha = "segredo123";
    cy.request("POST", "/api/clientes", {
      nome: "Cliente Login Real",
      email,
      data_nascimento: "1995-07-10",
      senha,
    });

    cy.visit("/login");
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="senha"]').type(senha);
    cy.get('[data-cy="enviar-login"]').click();
    cy.location("pathname").should("eq", "/conta");
    cy.get('[data-cy="conta-protegida"]')
      .should("contain.text", "Cliente Login Real")
      .and("contain.text", email);
    cy.get('[data-cy="sair"]').click();
    cy.location("pathname").should("eq", "/login");
    cy.window()
      .its("sessionStorage")
      .invoke("getItem", "gamekeys.sessao")
      .should("be.null");
  });

  it("usa a mesma mensagem para e-mail inexistente e senha incorreta", () => {
    const emailPersistido = `login-incorreto-${Date.now()}@example.com`;
    cy.request("POST", "/api/clientes", {
      nome: "Cliente Senha Incorreta",
      email: emailPersistido,
      data_nascimento: "1990-03-15",
      senha: "segredo123",
    });

    const tentativas = [
      ["inexistente@example.com", "segredo123"],
      [emailPersistido, "senha-errada"],
    ];
    tentativas.forEach(([email, senha]) => {
      cy.visit("/login");
      cy.get('input[name="email"]').type(email);
      cy.get('input[name="senha"]').type(senha);
      cy.get('[data-cy="enviar-login"]').click();
      cy.get('[data-cy="erro-login"]').should(
        "contain.text",
        "E-mail ou senha incorretos.",
      );
    });
  });
});
