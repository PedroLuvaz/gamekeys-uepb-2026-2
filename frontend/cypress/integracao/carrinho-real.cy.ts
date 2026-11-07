interface FixtureCarrinho {
  chave: string;
  jogoId: number;
  emailAdulto: string;
  emailMenor: string;
  senha: string;
}

describe("GK-11/GK-120 — tela, login, carrinho e PostgreSQL reais", () => {
  let fixture: FixtureCarrinho | null = null;

  beforeEach(() => {
    fixture = null;
    // Provar o alvo da API antes da preparação: nunca usar o Neon para estes testes.
    cy.request("/api/saude/banco")
      .its("body.banco")
      .should("eq", "gamekeys_teste");
    cy.task<FixtureCarrinho>("carrinho:preparar", null, { log: false }).then(
      (dados) => {
        fixture = dados;
      },
    );
  });

  afterEach(() => {
    if (fixture)
      cy.task("carrinho:limpar", { chave: fixture.chave }, { log: false });
  });

  function entrarComo(perfil: "adulto" | "menor") {
    cy.then(() => {
      const dados = fixture!;
      const retorno = `/jogos/${dados.jogoId}?origem=1`;
      cy.visit(`/login?retorno=${encodeURIComponent(retorno)}`);
      cy.get('input[name="email"]').type(
        perfil === "adulto" ? dados.emailAdulto : dados.emailMenor,
      );
      cy.get('input[name="senha"]').type(dados.senha, { log: false });
      cy.get('[data-cy="enviar-login"]').click();
      cy.location("pathname").should("eq", `/jogos/${dados.jogoId}`);
      cy.get('[data-cy="adicionar-carrinho"]').should("be.enabled");
    });
  }

  function conferirBanco(perfil: "adulto" | "menor", quantidade: number) {
    cy.then(() =>
      cy.task<{ linhas: number; quantidade: number; estoque: number }>(
        "carrinho:estado",
        { chave: fixture!.chave, perfil },
        { log: false },
      ),
    ).then((estado) => {
      expect(estado.quantidade).to.eq(quantidade);
      expect(estado.linhas).to.eq(quantidade ? 1 : 0);
      expect(estado.estoque, "Adicionar não reserva nem consome estoque").to.eq(
        3,
      );
    });
  }

  it("adiciona e incrementa o item persistido sem duplicar a linha", () => {
    entrarComo("adulto");
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="resultado-carrinho"]').should(
      "contain.text",
      "Você tem 1 unidade deste jogo.",
    );
    conferirBanco("adulto", 1);
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="resultado-carrinho"]')
      .should("contain.text", "Você tem 2 unidades deste jogo.")
      .and("contain.text", "39,80");
    conferirBanco("adulto", 2);
  });

  it("recusa estoque insuficiente e mantém o banco sem item", () => {
    entrarComo("adulto");
    cy.get('[data-cy="quantidade-carrinho"]').clear().type("4");
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="erro-carrinho"]').should(
      "contain.text",
      "Estoque insuficiente",
    );
    conferirBanco("adulto", 0);
  });

  it("recusa classificação etária usando a data do cliente autenticado", () => {
    entrarComo("menor");
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="erro-carrinho"]').should(
      "contain.text",
      "Sua idade não permite",
    );
    conferirBanco("menor", 0);
  });

  it("GK-12 altera, recalcula e remove o item no PostgreSQL real", () => {
    entrarComo("adulto");
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="resultado-carrinho"]').should("be.visible");
    cy.visit("/carrinho");
    cy.get('[data-cy="quantidade-item"]').should("have.text", "1");
    cy.get('[data-cy="aumentar-item"]').click();
    cy.get('[data-cy="quantidade-item"]').should("have.text", "2");
    cy.get('[data-cy="subtotal-item"]').should("contain.text", "39,80");
    cy.get('[data-cy="total-carrinho"]').should("contain.text", "39,80");
    conferirBanco("adulto", 2);
    cy.get('[data-cy="diminuir-item"]').click();
    cy.get('[data-cy="quantidade-item"]').should("have.text", "1");
    conferirBanco("adulto", 1);
    cy.get('[data-cy="remover-item"]').click();
    cy.get('[data-cy="carrinho-vazio"]').should("be.visible");
    conferirBanco("adulto", 0);
  });

  it("GK-12 recusa alteração acima do estoque sem mudar o banco", () => {
    entrarComo("adulto");
    cy.get('[data-cy="quantidade-carrinho"]').clear().type("3");
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="resultado-carrinho"]').should("be.visible");
    cy.visit("/carrinho");
    cy.get('[data-cy="aumentar-item"]').click();
    cy.get('[data-cy="mensagem-carrinho-erro"]').should(
      "contain.text",
      "Estoque insuficiente",
    );
    cy.get('[data-cy="quantidade-item"]').should("have.text", "3");
    conferirBanco("adulto", 3);
  });
});
