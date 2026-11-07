import {
  Before,
  Given,
  Then,
  When,
} from "@badeball/cypress-cucumber-preprocessor";

const usuario = {
  id: 12,
  nome: "Cliente Carrinho",
  email: "gk12@example.com",
  data_nascimento: "1990-01-01",
  perfil: "cliente",
};
const itemBase = {
  jogo_id: 101,
  slug: "caminhos-de-aurora",
  nome: "Caminhos de Aurora",
  capa_url: null,
  quantidade: 1,
  estoque_disponivel: 3,
  preco_unitario: "19.90",
  subtotal: "19.90",
};

let quantidade = 1;
let modo = "sucesso";
let removido = false;
let liberarConsulta: (() => void) | null = null;

function respostaCarrinho() {
  if (removido) return { itens: [], total: "0.00" };
  const subtotal = (19.9 * quantidade).toFixed(2);
  return {
    itens: [{ ...itemBase, quantidade, subtotal }],
    total: subtotal,
  };
}

Before({ tags: "@US-12" }, () => {
  quantidade = 1;
  modo = "sucesso";
  removido = false;
  liberarConsulta = null;
  cy.intercept("GET", "**/api/carrinho", (pedido) => {
    expect(pedido.headers.authorization).to.eq("Bearer token-gk12");
    if (modo === "rede") {
      pedido.reply({ forceNetworkError: true });
      return;
    }
    if (modo === "sessao") {
      pedido.reply({
        statusCode: 401,
        body: { detail: "Não foi possível autenticar. Entre novamente." },
      });
      return;
    }
    if (modo === "demora")
      return new Promise<void>((resolve) => {
        liberarConsulta = () => {
          pedido.reply({ body: respostaCarrinho() });
          resolve();
        };
      });
    pedido.reply({ body: respostaCarrinho() });
  }).as("consultarCarrinhoGk12");
  cy.intercept("PATCH", "**/api/carrinho/itens/101", (pedido) => {
    expect(pedido.headers.authorization).to.eq("Bearer token-gk12");
    expect(pedido.body).to.deep.equal({ quantidade: pedido.body.quantidade });
    if (modo === "estoque" && pedido.body.quantidade > 1) {
      pedido.reply({
        statusCode: 409,
        body: { detail: "Estoque insuficiente para a quantidade solicitada." },
      });
      return;
    }
    quantidade = pedido.body.quantidade;
    pedido.reply({ body: respostaCarrinho() });
  }).as("alterarCarrinhoGk12");
  cy.intercept("DELETE", "**/api/carrinho/itens/101", (pedido) => {
    expect(pedido.headers.authorization).to.eq("Bearer token-gk12");
    expect(pedido.body).to.be.empty;
    removido = true;
    pedido.reply({ body: respostaCarrinho() });
  }).as("removerCarrinhoGk12");
});

Given("que meu carrinho tem uma unidade de um jogo", () => {});
Given("que o estoque recusa o aumento do item", () => {
  modo = "estoque";
});
Given("que a conexão com o carrinho está indisponível", () => {
  modo = "rede";
});
Given("que o servidor recusa a sessão do carrinho", () => {
  modo = "sessao";
});
Given("que a consulta do carrinho demora", () => {
  modo = "demora";
});

When("abro a página do carrinho da GK-12", () => {
  cy.visit("/carrinho", {
    onBeforeLoad(janela) {
      janela.sessionStorage.setItem(
        "gamekeys.sessao",
        JSON.stringify({
          token: "token-gk12",
          expiraEm: Date.now() + 3600000,
          usuario,
        }),
      );
    },
  });
});
When("aumento a quantidade do item", () =>
  cy.get('[data-cy="aumentar-item"]').click(),
);
When("diminuo a quantidade do item", () =>
  cy.get('[data-cy="diminuir-item"]').click(),
);
When("removo o item do carrinho", () =>
  cy.get('[data-cy="remover-item"]').click(),
);

Then("vejo uma unidade e total de {string}", (total: string) => {
  cy.get('[data-cy="quantidade-item"]').should("have.text", "1");
  cy.get('[data-cy="total-carrinho"]').should(
    "contain.text",
    total.replace(/^R\$\s?/, ""),
  );
});
Then("vejo duas unidades, subtotal e total de {string}", (total: string) => {
  cy.wait("@alterarCarrinhoGk12").then(({ request }) => {
    expect(request.body).to.deep.equal({ quantidade: 2 });
    expect(request.body).not.to.have.keys("usuario_id", "carrinho_id");
  });
  cy.get('[data-cy="quantidade-item"]').should("have.text", "2");
  cy.get('[data-cy="subtotal-item"]').should(
    "contain.text",
    total.replace(/^R\$\s?/, ""),
  );
  cy.get('[data-cy="total-carrinho"]').should(
    "contain.text",
    total.replace(/^R\$\s?/, ""),
  );
});
Then("vejo que meu carrinho está vazio", () => {
  cy.wait("@removerCarrinhoGk12");
  cy.get('[data-cy="carrinho-vazio"]').should("be.visible");
  cy.get('[data-cy="item-carrinho"]').should("not.exist");
});
Then("vejo a mensagem de estoque insuficiente no carrinho", () => {
  cy.wait("@alterarCarrinhoGk12").its("response.statusCode").should("eq", 409);
  cy.get('[data-cy="mensagem-carrinho-erro"]')
    .should("have.attr", "role", "alert")
    .and("contain.text", "Estoque insuficiente");
});
Then("vejo o erro de conexão e a ação de tentar novamente", () => {
  cy.get('[data-cy="erro-carrinho-pagina"]')
    .should("contain.text", "Não foi possível conectar ao carrinho")
    .and("contain.text", "Tentar novamente");
});
Then("sou direcionado ao login para retornar ao carrinho", () => {
  cy.location("pathname").should("eq", "/login");
  cy.location("search").should(
    "eq",
    `?expirada=1&retorno=${encodeURIComponent("/carrinho")}`,
  );
  cy.window()
    .its("sessionStorage")
    .invoke("getItem", "gamekeys.sessao")
    .should("be.null");
});
Then("vejo o carregamento do carrinho", () => {
  cy.get('[data-cy="carrinho-carregando"]')
    .should("have.attr", "role", "status")
    .and("contain.text", "Carregando seu carrinho");
});
Then("a consulta do carrinho pode terminar", () => {
  cy.wrap(null)
    .should(() => expect(liberarConsulta).to.be.a("function"))
    .then(() => liberarConsulta!());
  cy.wait("@consultarCarrinhoGk12");
  cy.get('[data-cy="item-carrinho"]').should("be.visible");
});
