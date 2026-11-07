import {
  Before,
  Given,
  When,
  Then,
} from "@badeball/cypress-cucumber-preprocessor";

interface JogoDoCarrinho {
  id: number;
  nome: string;
  preco: string;
}

const usuario = {
  id: 9,
  nome: "Cliente Login",
  email: "cliente@example.com",
  data_nascimento: "2000-01-01",
  perfil: "cliente",
};
const token = "token-valido";
let jogos: { ativo: JogoDoCarrinho; esgotado: JogoDoCarrinho };
let jogo: JogoDoCarrinho;
let autenticado: boolean;
let total: number;
let demora: boolean;
let liberarAdicao: (() => void) | null;
let falhaDeRede: boolean;
let recusa: { statusCode: number; body: unknown } | null;

Before({ tags: "@GK-119-UI" }, () => {
  cy.fixture("detalhe-jogo").then((fixture) => {
    jogos = fixture;
    jogo = jogos.ativo;
    autenticado = false;
    total = 0;
    demora = false;
    liberarAdicao = null;
    falhaDeRede = false;
    recusa = null;
  });
});

Given("que há um jogo disponível para adicionar ao carrinho", () => {
  cy.intercept("GET", "**/api/jogos/*", (pedido) => pedido.reply(jogo)).as(
    "jogoDoCarrinho",
  );
  cy.intercept("GET", "**/api/auth/me", usuario);
  cy.intercept("POST", "**/api/carrinho/itens", (pedido) => {
    if (recusa) {
      pedido.reply(recusa);
      return;
    }
    total += pedido.body.quantidade;
    const resposta = {
      body: {
        carrinho_id: 4,
        jogo_id: jogo.id,
        nome: jogo.nome,
        quantidade: total,
        preco_unitario: jogo.preco,
        subtotal: (Number(jogo.preco) * total).toFixed(2),
      },
    };
    if (demora)
      return new Promise<void>((resolve) => {
        liberarAdicao = () => {
          pedido.reply(resposta);
          resolve();
        };
      });
    pedido.reply(resposta);
  }).as("adicaoCarrinho");
});

Given("que tenho uma sessão para adicionar ao carrinho", () => {
  autenticado = true;
});
Given(
  "que o carrinho já contém {int} unidades deste jogo",
  (quantidade: number) => {
    total = quantidade;
  },
);
Given(
  "que a adição ao carrinho é recusada com {int} e {string}",
  (statusCode: number, detail: string) => {
    recusa = { statusCode, body: { detail } };
  },
);
Given(
  "que a adição ao carrinho recebe um detalhe de validação estruturado",
  () => {
    recusa = {
      statusCode: 422,
      body: { detail: [{ msg: "Value error, Quantidade fora do limite." }] },
    };
  },
);
Given("que a adição ao carrinho recebe uma recusa sem detalhe", () => {
  recusa = { statusCode: 503, body: {} };
});
Given("que o jogo para adicionar ao carrinho está esgotado", () => {
  jogo = jogos.esgotado;
});
Given("que a API demora para adicionar ao carrinho", () => {
  demora = true;
});
Given("que a conexão falha ao adicionar ao carrinho", () => {
  falhaDeRede = true;
});

When("abro o detalhe para adicionar ao carrinho", () => {
  cy.visit(`/jogos/${jogo.id}`, {
    onBeforeLoad(janela) {
      janela.sessionStorage.clear();
      if (autenticado) {
        janela.sessionStorage.setItem(
          "gamekeys.sessao",
          JSON.stringify({ token, expiraEm: Date.now() + 3_600_000, usuario }),
        );
      }
      if (!falhaDeRede) return;
      const consultar = janela.fetch.bind(janela);
      const falhar = cy
        .stub()
        .as("conexaoCarrinho")
        .rejects(new TypeError("Falha de rede simulada"));
      cy.stub(janela, "fetch").callsFake(
        (entrada: RequestInfo | URL, opcoes?: RequestInit) => {
          if (
            String(entrada).endsWith("/api/carrinho/itens") &&
            opcoes?.method === "POST"
          ) {
            return falhar();
          }
          return consultar(entrada, opcoes);
        },
      );
    },
  });
  cy.wait("@jogoDoCarrinho");
  cy.get('[data-cy="detalhe"]').should("have.attr", "aria-busy", "false");
});
When("escolho {int} unidades para adicionar", (quantidade: number) => {
  cy.get('[data-cy="quantidade-carrinho"]').clear().type(String(quantidade));
});
When("preencho a quantidade do carrinho com {string}", (quantidade: string) => {
  cy.get('[data-cy="quantidade-carrinho"]').clear();
  if (quantidade) cy.get('[data-cy="quantidade-carrinho"]').type(quantidade);
});
When("adiciono o jogo ao carrinho", () => {
  cy.get('[data-cy="adicionar-carrinho"]').click();
});
When("tento repetir o envio pendente do carrinho", () => {
  cy.get('[data-cy="adicionar-carrinho"]').dblclick({ force: true });
  cy.get(".formulario-carrinho").then(([formulario]) => {
    for (let tentativa = 0; tentativa < 2; tentativa++) {
      formulario.dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true }),
      );
    }
  });
  cy.wrap(null)
    .should(() => expect(liberarAdicao).to.be.a("function"))
    .then(() => liberarAdicao!());
  cy.wait("@adicaoCarrinho").its("response.statusCode").should("eq", 200);
});

Then(
  "o pedido do carrinho envia {int} unidades do jogo com o token da sessão",
  (quantidade: number) => {
    cy.wait("@adicaoCarrinho").then(({ request }) => {
      expect(request.body).to.deep.equal({ jogo_id: jogo.id, quantidade });
      expect(request.headers.authorization).to.equal(`Bearer ${token}`);
      expect(request.headers["content-type"]).to.equal("application/json");
    });
  },
);
Then("a quantidade inicial do carrinho é 1", () => {
  cy.get('[data-cy="quantidade-carrinho"]').should("have.value", "1");
});
Then(
  "a confirmação do carrinho informa {int} unidade(s)",
  (quantidade: number) => {
    cy.get('[data-cy="resultado-carrinho"]')
      .should("have.attr", "role", "status")
      .and(
        "contain.text",
        `Adicionado ao carrinho. Você tem ${quantidade} ${quantidade === 1 ? "unidade" : "unidades"} deste jogo.`,
      );
    cy.get('[data-cy="erro-carrinho"]').should("not.exist");
    cy.get('[data-cy="adicionar-carrinho"]').should("be.enabled");
  },
);
Then("o alerta do carrinho mostra {string}", (mensagem: string) => {
  cy.get('[data-cy="erro-carrinho"]')
    .should("have.attr", "role", "alert")
    .and("have.text", mensagem);
  cy.get('[data-cy="resultado-carrinho"]').should("not.exist");
  cy.get('[data-cy="adicionar-carrinho"]').should("be.enabled");
});
Then(
  "foram feitos {int} pedidos de adição ao carrinho",
  (quantidade: number) => {
    cy.get("@adicaoCarrinho.all").should("have.length", quantidade);
  },
);
Then("vejo o link para entrar e adicionar ao carrinho", () => {
  cy.get('[data-cy="entrar-para-adicionar"]')
    .should("have.text", "Entrar para adicionar ao carrinho")
    .and(
      "have.attr",
      "href",
      `/login?retorno=${encodeURIComponent(`/jogos/${jogo.id}`)}`,
    );
  cy.get(
    '[data-cy="quantidade-carrinho"], [data-cy="adicionar-carrinho"]',
  ).should("not.exist");
  cy.get('[data-cy="entrar-para-adicionar"]').click();
  cy.location("pathname").should("eq", "/login");
});
Then("a ação do carrinho está desabilitada como Esgotado", () => {
  cy.get('[data-cy="adicionar-carrinho"]')
    .should("be.disabled")
    .and("have.text", "Esgotado")
    .click({ force: true });
  cy.get('[data-cy="quantidade-carrinho"]').should("not.exist");
});
Then("a adição redireciona ao login com a sessão expirada", () => {
  cy.wait("@adicaoCarrinho");
  cy.location("pathname").should("eq", "/login");
  cy.location("search").should(
    "eq",
    `?expirada=1&retorno=${encodeURIComponent(`/jogos/${jogo.id}`)}`,
  );
  cy.get('[data-cy="sessao-expirada"]').should("be.visible");
  cy.window()
    .its("sessionStorage")
    .invoke("getItem", "gamekeys.sessao")
    .should("be.null");
});
Then("a ação do carrinho informa progresso e impede novo envio", () => {
  cy.get('[data-cy="adicionar-carrinho"]')
    .should("be.disabled")
    .and("have.text", "Adicionando…");
  cy.get('[data-cy="quantidade-carrinho"]').should("be.disabled");
  cy.get(".formulario-carrinho").should("have.attr", "aria-busy", "true");
});
Then("a conexão do carrinho foi tentada uma única vez", () => {
  cy.get("@conexaoCarrinho").should("have.been.calledOnce");
});
Then("a quantidade do carrinho é inválida", () => {
  cy.get('[data-cy="quantidade-carrinho"]').should("match", ":invalid");
  cy.get('[data-cy="resultado-carrinho"]').should("not.exist");
});
