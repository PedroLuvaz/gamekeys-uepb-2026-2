import {
  Before,
  Given,
  Then,
  When,
} from "@badeball/cypress-cucumber-preprocessor";

const cliente = {
  id: 16,
  nome: "Cliente Pagamento",
  email: "gk16@example.com",
  data_nascimento: "1990-01-01",
  perfil: "cliente",
};
const itens = [
  {
    jogo_id: 101,
    nome: "Caminhos de Aurora",
    quantidade: 2,
    preco_unitario: "19.90",
    subtotal: "39.80",
  },
];
const chaves = [
  { jogo_id: 101, nome: "Caminhos de Aurora", codigo: "TESTE-AAAA-0001" },
  { jogo_id: 101, nome: "Caminhos de Aurora", codigo: "TESTE-BBBB-0002" },
];

type Status = "aguardando_pagamento" | "entregue" | "cancelado";
let status: Status = "aguardando_pagamento";
let consulta = "sucesso";
let pagamento = "sucesso";
let perfil = "cliente";
let pagamentosEnviados: string[] = [];

function pedido(semChaves = false) {
  return {
    pedido_id: 7,
    status,
    valor_total: "39.80",
    itens,
    chaves: status === "entregue" && !semChaves ? chaves : [],
  };
}

Before({ tags: "@US-16" }, () => {
  status = "aguardando_pagamento";
  consulta = "sucesso";
  pagamento = "sucesso";
  perfil = "cliente";
  pagamentosEnviados = [];
  cy.intercept("GET", "**/api/pedidos/7", (requisicao) => {
    expect(requisicao.headers.authorization).to.eq("Bearer token-gk16");
    if (consulta === "rede") {
      requisicao.reply({ forceNetworkError: true });
      return;
    }
    if (consulta === "sessao") {
      requisicao.reply({
        statusCode: 401,
        body: { detail: "Não foi possível autenticar. Entre novamente." },
      });
      return;
    }
    if (consulta === "inexistente") {
      requisicao.reply({
        statusCode: 404,
        body: { detail: "Pedido não encontrado." },
      });
      return;
    }
    // Atraso nativo do Cypress, como nos cenários do carrinho.
    requisicao.reply({
      body: pedido(consulta === "invalida"),
      delay: consulta === "demora" ? 1500 : 0,
    });
  }).as("consultarPedido");
  cy.intercept("POST", "**/api/pedidos/7/pagamento", (requisicao) => {
    expect(requisicao.headers.authorization).to.eq("Bearer token-gk16");
    expect(Object.keys(requisicao.body)).to.deep.equal(["metodo"]);
    pagamentosEnviados.push(requisicao.body.metodo);
    if (pagamento === "rede") {
      requisicao.reply({ forceNetworkError: true });
      return;
    }
    if (pagamento === "recusado") {
      requisicao.reply({
        statusCode: 409,
        body: { detail: "Este pedido não está aguardando pagamento." },
      });
      return;
    }
    status = "entregue";
    requisicao.reply({
      body: pedido(),
      delay: pagamento === "demora" ? 1500 : 0,
    });
  }).as("pagarPedido");
});

function abrir(comSessao = true) {
  cy.visit("/pedidos/7", {
    onBeforeLoad(janela) {
      if (!comSessao) return;
      janela.sessionStorage.setItem(
        "gamekeys.sessao",
        JSON.stringify({
          token: "token-gk16",
          expiraEm: Date.now() + 3600000,
          usuario: { ...cliente, perfil },
        }),
      );
    },
  });
}

Given("que tenho um pedido aguardando pagamento", () => {});
Given("que meu pedido já foi entregue", () => {
  status = "entregue";
});
Given("que meu pedido foi cancelado", () => {
  status = "cancelado";
});
Given("que a consulta do pedido demora", () => {
  consulta = "demora";
});
Given("que a confirmação do pagamento demora", () => {
  pagamento = "demora";
});
Given("que a conexão com o pedido está indisponível", () => {
  consulta = "rede";
});
Given("que o pedido não existe para a minha conta", () => {
  consulta = "inexistente";
});
Given("que o pedido não está mais aguardando pagamento no servidor", () => {
  pagamento = "recusado";
});
Given("que a conexão cai ao confirmar o pagamento", () => {
  pagamento = "rede";
});
Given("que o servidor recusa a sessão ao consultar o pedido", () => {
  consulta = "sessao";
});
Given("que o servidor devolve um pedido entregue sem chaves", () => {
  status = "entregue";
  consulta = "invalida";
});
Given("que estou usando uma conta de administrador no pedido", () => {
  perfil = "administrador";
});
Given("uso uma tela de 320 pixels no pedido", () => {
  cy.viewport(320, 640);
});

When("abro a página do pedido", () => abrir());
When("abro a página do pedido sem sessão", () => abrir(false));
When("escolho pagar com cartão", () =>
  cy.get('[data-cy="metodo-cartao"]').check(),
);
When("confirmo o pagamento", () =>
  cy.get('[data-cy="confirmar-pagamento"]').click(),
);
When("confirmo o pagamento duas vezes seguidas", () => {
  cy.get('[data-cy="formulario-pagamento"]').then(($formulario) => {
    const formulario = $formulario[0] as HTMLFormElement;
    formulario.requestSubmit();
    formulario.requestSubmit();
  });
});
When("a conexão volta e tento carregar o pedido de novo", () => {
  consulta = "sucesso";
  cy.get('[data-cy="erro-pedido-pagina"]')
    .contains("button", "Tentar novamente")
    .click();
});
When("a conexão volta", () => {
  pagamento = "sucesso";
});

Then(
  "vejo o pedido aguardando pagamento com total de {string}",
  (total: string) => {
    cy.get('[data-cy="status-pedido"]').should(
      "have.text",
      "Aguardando pagamento",
    );
    cy.get('[data-cy="total-pedido"]').should(
      "contain.text",
      total.replace("R$ ", ""),
    );
    cy.get('[data-cy="item-pedido"]').should("have.length", 1);
    cy.get('[data-cy="confirmar-pagamento"]').should("be.enabled");
  },
);
Then("nenhuma chave aparece na tela", () => {
  cy.get('[data-cy="chaves-entregues"]').should("not.exist");
  cy.get("body").should("not.contain.text", "TESTE-AAAA-0001");
});
Then("o pedido fica entregue e vejo {int} chaves", (quantidade: number) => {
  cy.get('[data-cy="status-pedido"]').should("have.text", "Entregue");
  cy.get('[data-cy="chave-entregue"]').should("have.length", quantidade);
  cy.get('[data-cy="chaves-entregues"]')
    .should("contain.text", "TESTE-AAAA-0001")
    .and("contain.text", "TESTE-BBBB-0002");
  cy.get('[data-cy="formulario-pagamento"]').should("not.exist");
});
Then(
  "o pagamento foi enviado uma vez com o método {string}",
  (metodo: string) => {
    cy.wrap(null).should(() => {
      expect(pagamentosEnviados).to.deep.equal([metodo]);
    });
  },
);
Then("não há formulário de pagamento", () => {
  cy.get('[data-cy="formulario-pagamento"]').should("not.exist");
});
Then("vejo o aviso de carregamento do pedido", () => {
  cy.get('[data-cy="pedido-carregando"]')
    .should("be.visible")
    .and("have.attr", "role", "status");
});
Then("a tela informa que está confirmando o pagamento", () => {
  cy.get('[data-cy="confirmar-pagamento"]')
    .should("be.disabled")
    .and("contain.text", "Confirmando pagamento");
});
Then("vejo o erro do pedido com a opção de tentar novamente", () => {
  cy.get('[data-cy="erro-pedido-pagina"]')
    .should("be.visible")
    .and("have.attr", "role", "alert")
    .contains("button", "Tentar novamente");
  cy.get('[data-cy="chaves-entregues"]').should("not.exist");
});
Then("vejo que o pedido não foi encontrado", () => {
  cy.get('[data-cy="pedido-nao-encontrado"]')
    .should("be.visible")
    .and("contain.text", "Pedido não encontrado");
});
Then("vejo a mensagem de pagamento {string}", (mensagem: string) => {
  cy.get('[data-cy="mensagem-pedido-erro"]')
    .should("have.attr", "role", "alert")
    .and("have.text", mensagem);
  cy.get('[data-cy="confirmar-pagamento"]').should("be.enabled");
});
Then("vou ao login com retorno para o pedido", () => {
  cy.location("pathname").should("eq", "/login");
  cy.location("search").should("contain", "retorno=%2Fpedidos%2F7");
});
Then("vejo que o pedido foi cancelado", () => {
  cy.get('[data-cy="status-pedido"]').should("have.text", "Cancelado");
  cy.get('[data-cy="pedido-cancelado"]').should("be.visible");
});
Then("vejo que os pedidos são exclusivos de clientes", () => {
  cy.get('[data-cy="pedido-perfil-invalido"]').should(
    "contain.text",
    "exclusivos de contas de cliente",
  );
  cy.get("@consultarPedido.all").should("have.length", 0);
});
Then("a página do pedido cabe na largura do celular", () => {
  cy.document().then((documento) => {
    expect(documento.documentElement.scrollWidth).to.be.at.most(320);
  });
});
