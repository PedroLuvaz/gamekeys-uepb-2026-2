// GK-10/GK-89: somente GET contra a API real. O CI fornece o ID de um inativo do banco local.
interface DetalheReal {
  id: number;
  nome: string;
  descricao: string;
  genero: string;
  plataforma: string;
  classificacao: string;
  preco: string;
  disponibilidade: string;
}

function conferirFicha(jogo: DetalheReal) {
  cy.get("h1").should("have.text", jogo.nome);
  cy.get('[data-cy="descricao-jogo"]').should("have.text", jogo.descricao);
  cy.get('[data-cy="genero-jogo"]').should("have.text", jogo.genero);
  cy.get('[data-cy="plataforma-jogo"]').should("have.text", jogo.plataforma);
  cy.get('[data-cy="classificacao-jogo"]').should(
    "have.text",
    jogo.classificacao === "L" ? "Livre" : `${jogo.classificacao} anos`,
  );
  cy.get('[data-cy="preco-jogo"]')
    .invoke("text")
    .then((texto) => {
      expect(texto.replace(/\s/g, " ")).to.equal(
        `R$ ${Number(jogo.preco).toFixed(2).replace(".", ",")}`,
      );
    });
  cy.get('[data-cy="disponibilidade-jogo"]').should(
    "contain.text",
    jogo.disponibilidade,
  );
}

describe("Detalhe com API e banco reais — GK-10", () => {
  for (const disponibilidade of ["Disponível", "Esgotado"]) {
    it(`confere os seis campos de um jogo ${disponibilidade.toLowerCase()} e o acesso direto`, () => {
      cy.request("/api/jogos?pagina=1").then(({ body: primeira }) => {
        cy.request("/api/jogos?pagina=2").then(({ body: segunda }) => {
          const jogo = [...primeira.itens, ...segunda.itens].find(
            (item) => item.disponibilidade === disponibilidade,
          );
          expect(jogo, `Carga de demonstração com jogo ${disponibilidade}`).to
            .exist;
          cy.request<DetalheReal>(`/api/jogos/${jogo.id}`).then(
            ({ body: detalhe }) => {
              cy.visit(`/jogos/${jogo.id}`);
              conferirFicha(detalhe);
              cy.reload();
              conferirFicha(detalhe);
            },
          );
        });
      });
    });
  }

  it("oculta um jogo comprovadamente inativo com a mesma resposta de um inexistente", () => {
    const id = Cypress.expose("jogoInativoId") as number;
    expect(
      id,
      "Defina GAMEKEYS_JOGO_INATIVO_ID com um ID consultado no banco de testes",
    ).to.be.greaterThan(0);
    cy.request({ url: `/api/jogos/${id}`, failOnStatusCode: false }).then(
      (inativo) => {
        expect(inativo.status).to.equal(404);
        expect(inativo.body).to.deep.equal({ detail: "Jogo não encontrado." });
        cy.request({
          url: "/api/jogos/9223372036854775807",
          failOnStatusCode: false,
        }).then((inexistente) => {
          expect(inexistente.status).to.equal(404);
          expect(inexistente.body).to.deep.equal(inativo.body);
        });
      },
    );
    cy.visit(`/jogos/${id}`);
    cy.get('[data-cy="estado-vazio"]').should(
      "contain.text",
      "Jogo não encontrado",
    );
    cy.get(
      '[data-cy="descricao-jogo"], [data-cy="preco-jogo"], .ficha, .arte-grande',
    ).should("not.exist");
    cy.get('[data-cy="voltar-catalogo"]').click();
    cy.get('[data-cy="jogo"]').should("have.length", 20);
  });
});
