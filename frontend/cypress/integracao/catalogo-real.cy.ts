// Somente GET: verifica a integração da tela com a API em execução, sem alterar dados.
describe("Catálogo com API real — GK-9", () => {
  it("mostra os mesmos jogos e totais da API nas duas páginas", () => {
    cy.request("/api/jogos?pagina=1").then(({ body: primeira }) => {
      expect(primeira.total).to.be.greaterThan(20);
      cy.visit("/");
      cy.get('[data-cy="jogo"]').should("have.length", 20);
      cy.get('[data-cy="jogo"] h3').then(($titulos) => {
        expect([...$titulos].map((el) => el.textContent)).to.deep.equal(
          primeira.itens.map((jogo: { nome: string }) => jogo.nome),
        );
      });
      cy.get('[data-cy="proxima-pagina"]').click();
      cy.request("/api/jogos?pagina=2").then(({ body: segunda }) => {
        cy.get('[data-cy="jogo"]').should("have.length", segunda.itens.length);
        cy.get('[data-cy="jogo"] h3').then(($titulos) => {
          expect([...$titulos].map((el) => el.textContent)).to.deep.equal(
            segunda.itens.map((jogo: { nome: string }) => jogo.nome),
          );
        });
        cy.get('[data-cy="intervalo"]').should(
          "contain.text",
          `de ${primeira.total} jogos`,
        );
      });
    });
  });

  it("abre a ficha do esgotado a partir dos dados reais e retorna ao catálogo", () => {
    cy.request("/api/jogos?pagina=2").then(({ body }) => {
      const esgotado = body.itens.find(
        (jogo: { disponibilidade: string }) =>
          jogo.disponibilidade === "Esgotado",
      );
      expect(esgotado, "Jogo esgotado na carga de demonstração").to.exist;
      cy.visit("/?pagina=2");
      cy.get(`[data-jogo-id="${esgotado.id}"]`)
        .should("contain.text", "Esgotado")
        .find("a")
        .click();
      cy.get("h1").should("have.text", esgotado.nome);
      cy.get('[data-cy="detalhe"]').should("contain.text", "Esgotado");
      cy.get('[data-cy="voltar-catalogo"]').click();
      cy.location("search").should("contain", "pagina=2");
      cy.get('[data-cy="jogo"]').should("have.length", body.itens.length);
    });
  });

  it("trata identificador inexistente usando a resposta real da API", () => {
    cy.request({
      url: "/api/jogos/9223372036854775807",
      failOnStatusCode: false,
    })
      .its("status")
      .should("eq", 404);
    cy.visit("/jogos/9223372036854775807");
    cy.get('[data-cy="estado-vazio"]').should(
      "contain.text",
      "Jogo não encontrado",
    );
  });
});
