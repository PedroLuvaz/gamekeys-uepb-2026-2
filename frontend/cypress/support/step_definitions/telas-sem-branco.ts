import {
  Before,
  Given,
  Then,
  When,
} from "@badeball/cypress-cucumber-preprocessor";
import {
  confirmarEmAteUmSegundo,
  medirAteAparecer,
} from "../medir-carregamento.js";

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

// GK-48: Minha conta e "Tentar novamente" do carrinho, lacunas do levantamento de 16/11.
const usuario = {
  id: 48,
  nome: "Cliente Estados",
  email: "gk48@example.com",
  data_nascimento: "1990-05-10",
  perfil: "cliente",
};
let conta = "sucesso";
let carrinho = "sucesso";

Before({ tags: "@US-48" }, () => {
  conta = "sucesso";
  carrinho = "sucesso";
  cy.intercept("GET", "**/api/auth/me", (pedido) => {
    if (conta === "rede") {
      pedido.reply({ forceNetworkError: true });
      return;
    }
    pedido.reply({
      body: conta === "incompleta" ? { id: 48 } : usuario,
      delay: conta === "demora" ? 1500 : 0,
    });
  }).as("contaGk48");
  cy.intercept("GET", "**/api/carrinho", (pedido) => {
    if (carrinho === "rede") {
      pedido.reply({ forceNetworkError: true });
      return;
    }
    pedido.reply({
      itens: [
        {
          jogo_id: 7,
          slug: "jogo-estados",
          nome: "Jogo dos Estados",
          capa_url: null,
          quantidade: 1,
          estoque_disponivel: 4,
          preco_unitario: "29.90",
          subtotal: "29.90",
        },
      ],
      total: "29.90",
    });
  }).as("carrinhoGk48");
});

function abrirComSessao(caminho: string) {
  cy.visit(caminho, {
    onBeforeLoad(janela) {
      if (caminho === "/conta") {
        medirAteAparecer(
          janela,
          "conta",
          '[data-cy="conta-protegida"] [role="status"]',
        );
      }
      janela.sessionStorage.setItem(
        "gamekeys.sessao",
        JSON.stringify({
          token: "token-gk48",
          expiraEm: Date.now() + 3600000,
          usuario,
        }),
      );
    },
  });
}

Given("que a validação da minha conta demora", () => {
  conta = "demora";
});
Given("que a conexão cai ao validar minha conta", () => {
  conta = "rede";
});
Given("que o servidor devolve uma conta incompleta", () => {
  conta = "incompleta";
});
Given("que a conexão cai ao abrir o carrinho", () => {
  carrinho = "rede";
});

When("abro a página Minha conta", () => abrirComSessao("/conta"));
When("abro o carrinho para conferir os estados", () =>
  abrirComSessao("/carrinho"),
);
When("a conexão da conta volta e tento novamente", () => {
  conta = "sucesso";
  cy.get("[data-cy=conta-protegida] [data-cy=erro]")
    .contains("button", "Tentar novamente")
    .click();
});
When("a conexão do carrinho volta e tento novamente", () => {
  carrinho = "sucesso";
  cy.window().then((janela) => {
    // Marca a janela antes do clique: se a página recarregar, a marca some.
    (janela as unknown as { semRecarga?: boolean }).semRecarga = true;
  });
  cy.get('[data-cy="erro-carrinho-pagina"]')
    .contains("button", "Tentar novamente")
    .click();
});

Then("vejo o aviso de carregamento da conta em até 1 segundo", () => {
  cy.get("[data-cy=conta-protegida] [role=status]")
    .should("be.visible")
    .and("contain.text", "Validando sua sessão");
  confirmarEmAteUmSegundo("conta");
});
Then("depois vejo os dados da minha conta", () => {
  cy.get("[data-cy=conta-protegida]")
    .should("contain.text", "Olá, Cliente Estados")
    .and("contain.text", "gk48@example.com")
    .and("contain.text", "10/05/1990");
  cy.get("[data-cy=conta-protegida] [data-cy=erro]").should("not.exist");
});
Then("vejo o erro da conta com a opção de tentar novamente", () => {
  cy.get("[data-cy=conta-protegida] [data-cy=erro]")
    .should("be.visible")
    .and("have.attr", "role", "alert")
    .and("contain.text", "Não foi possível carregar sua conta")
    .and(
      "contain.text",
      "Não foi possível validar sua sessão. Tente novamente.",
    )
    .contains("button", "Tentar novamente");
});
Then("vejo o erro da conta com a mensagem {string}", (mensagem: string) => {
  cy.get("[data-cy=conta-protegida] [data-cy=erro]")
    .should("have.attr", "role", "alert")
    .and("contain.text", mensagem);
});
Then('a tela não mostra "undefined" nem "Invalid Date"', () => {
  cy.get("main")
    .should("not.contain.text", "undefined")
    .and("not.contain.text", "Invalid Date");
});
Then("vejo o erro de conexão do carrinho", () => {
  cy.get('[data-cy="erro-carrinho-pagina"]')
    .should("have.attr", "role", "alert")
    .and("contain.text", "Não foi possível conectar ao carrinho");
});
Then("vejo os itens do carrinho sem recarregar a página", () => {
  cy.get('[data-cy="erro-carrinho-pagina"]').should("not.exist");
  cy.get('[data-cy="item-carrinho"]')
    .should("have.length", 1)
    .and("contain.text", "Jogo dos Estados");
  cy.window().its("semRecarga").should("eq", true);
});
