import {
  Before,
  Given,
  When,
  Then,
} from "@badeball/cypress-cucumber-preprocessor";

const cliente = {
  id: 14,
  nome: "Cliente Checkout",
  email: "gk14@example.com",
  data_nascimento: "1990-01-01",
  perfil: "cliente",
};
const item = {
  jogo_id: 101,
  slug: "caminhos-de-aurora",
  nome: "Caminhos de Aurora",
  capa_url: null,
  quantidade: 1,
  estoque_disponivel: 3,
  preco_unitario: "19.90",
  subtotal: "19.90",
};
const identidadeAlheia = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const chave = "gamekeys.finalizacao.14";
const reserva = {
  pedido_id: 14,
  status: "aguardando_pagamento",
  valor_total: "19.90",
  itens: [
    { jogo_id: 101, quantidade: 1, preco_unitario: "19.90", subtotal: "19.90" },
  ],
};
let modo = "sucesso";
let identidades: string[] = [];
let esvaziado = false;

Before({ tags: "@US-14" }, () => {
  modo = "sucesso";
  identidades = [];
  esvaziado = false;
  cy.intercept("GET", "**/api/carrinho", {
    body: { itens: [item], total: "19.90" },
  }).as("carrinhoCheckout");
  cy.intercept("POST", "**/api/pedidos/reservas", (req) => {
    expect(req.headers.authorization).to.eq("Bearer token-gk14");
    expect(Object.keys(req.body)).to.deep.eq(["chave_idempotencia"]);
    expect(req.body.chave_idempotencia).to.match(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    );
    identidades.push(req.body.chave_idempotencia);
    if (modo === "rede") return req.reply({ forceNetworkError: true });
    if (/^\d{3}$/.test(modo))
      return req.reply({
        statusCode: Number(modo),
        body: { detail: "Finalização recusada pelo servidor." },
      });
    if (modo === "confirmacao-perdida") esvaziado = true;
    if (["invalida", "confirmacao-perdida"].includes(modo))
      return req.reply({ body: { pedido_id: 14 } });
    if (modo === "id-inseguro")
      return req.reply({ body: { ...reserva, pedido_id: 9007199254740992 } });
    req.reply({
      body: reserva,
      delay: ["demora", "timeout"].includes(modo) ? 1500 : 0,
    });
  }).as("checkout");
  cy.intercept("GET", "**/api/pedidos/14", {
    body: {
      ...reserva,
      itens: [{ ...reserva.itens[0], nome: item.nome }],
      chaves: [],
    },
  }).as("pedidoCheckout");
  cy.intercept("PATCH", "**/api/carrinho/itens/101", {
    delay: 1500,
    body: {
      itens: [{ ...item, quantidade: 2, subtotal: "39.80" }],
      total: "39.80",
    },
  }).as("alteracaoCheckout");
});

Given("que a finalização responde no modo {string}", (valor: string) => {
  modo = valor;
  if (modo === "vazio")
    cy.intercept("GET", "**/api/carrinho", {
      body: { itens: [], total: "0.00" },
    });
});
Given("uso um celular para finalizar", () => cy.viewport(320, 640));
When("abro o carrinho para finalizar", () => {
  cy.visit("/carrinho", {
    onBeforeLoad(win) {
      win.sessionStorage.setItem(
        "gamekeys.sessao",
        JSON.stringify({
          token: "token-gk14",
          expiraEm: Date.now() + 3600000,
          usuario: cliente,
        }),
      );
      if (modo === "outro-cliente")
        win.sessionStorage.setItem("gamekeys.finalizacao.99", identidadeAlheia);
      if (modo === "corrompida") win.sessionStorage.setItem(chave, "invalida");
      if (modo === "armazenamento") {
        const original = win.Storage.prototype.setItem;
        cy.stub(win.Storage.prototype, "setItem").callsFake(function (
          this: Storage,
          nome: string,
          valor: string,
        ) {
          if (nome === chave) throw new Error("Armazenamento bloqueado");
          return original.call(this, nome, valor);
        });
      }
      if (modo === "timeout") {
        const original = win.AbortSignal.timeout;
        cy.stub(win.AbortSignal, "timeout").callsFake(() =>
          original.call(win.AbortSignal, 50),
        );
      }
    },
  });
  if (modo !== "vazio")
    cy.get('[data-cy="total-carrinho"]').should("contain.text", "19,90");
});
When("finalizo o carrinho", () =>
  cy.get('[data-cy="finalizar-compra"]').click(),
);
When("aciono a finalização duas vezes imediatamente", () => {
  cy.get('[data-cy="finalizar-compra"]').then(($botao) => {
    const botao = $botao[0] as HTMLButtonElement;
    botao.click();
    botao.click();
  });
});
Then("a finalização bloqueia alterações enquanto envia", () => {
  cy.get('[data-cy="finalizacao-enviando"]').should("be.visible");
  cy.get('[data-cy="finalizar-compra"]').should("be.disabled");
  cy.get(
    '[data-cy="aumentar-item"], [data-cy="diminuir-item"], [data-cy="remover-item"]',
  ).each(($botao) => cy.wrap($botao).should("be.disabled"));
});
Then("vejo o pedido criado pela finalização", () => {
  cy.location("pathname").should("eq", "/pedidos/14");
  cy.get('[data-cy="total-pedido"]').should("contain.text", "19,90");
  cy.get('[data-cy="formulario-pagamento"]').should("be.visible");
  cy.window().then(
    (win) => expect(win.sessionStorage.getItem(chave)).to.be.null,
  );
});
Then("somente uma solicitação de finalização foi enviada", () =>
  cy.then(() => expect(identidades).to.have.length(1)),
);
Then("não posso finalizar um carrinho vazio", () => {
  cy.get('[data-cy="carrinho-vazio"]').should("be.visible");
  cy.get('[data-cy="finalizar-compra"]').should("not.exist");
  cy.then(() => expect(identidades).to.have.length(0));
});
Then("vejo a recusa definitiva da finalização", () =>
  cy
    .get('[data-cy="mensagem-carrinho-erro"]')
    .should("contain.text", "Finalização recusada"),
);
Then("posso corrigir o carrinho antes de finalizar de novo", () => {
  cy.get('[data-cy="aumentar-item"]').should("be.enabled");
  cy.get('[data-cy="finalizar-compra"]').should("be.enabled");
  cy.get('[data-cy="finalizacao-pendente"]').should("not.exist");
  cy.window().then(
    (win) => expect(win.sessionStorage.getItem(chave)).to.be.null,
  );
});
Then("a finalização fica pendente e bloqueia alterações", () => {
  cy.get('[data-cy="finalizacao-pendente"]').should("be.visible");
  cy.get(
    '[data-cy="finalizar-compra"], [data-cy="aumentar-item"], [data-cy="remover-item"]',
  ).each(($botao) => cy.wrap($botao).should("be.disabled"));
  cy.location("pathname").should("eq", "/carrinho");
  cy.window().then((win) =>
    expect(win.sessionStorage.getItem(chave)).to.eq(identidades[0]),
  );
});
When("a confirmação volta e verifico a finalização", () => {
  cy.then(() => {
    modo = "sucesso";
  });
  cy.get('[data-cy="recuperar-finalizacao"]').click();
});
Then("todas as tentativas usam a mesma identidade de operação", () =>
  cy.then(() => {
    expect(identidades.length).to.be.at.least(2);
    expect(new Set(identidades).size).to.eq(1);
  }),
);
When("recarrego o carrinho depois da confirmação perdida", () => {
  cy.then(() => expect(esvaziado).to.eq(true));
  cy.intercept("GET", "**/api/carrinho", {
    body: { itens: [], total: "0.00" },
  });
  cy.reload();
});
Then("não há finalização automática ao recuperar a sessão", () => {
  cy.get('[data-cy="carrinho-vazio"]').should("be.visible");
  cy.get('[data-cy="recuperar-finalizacao"]').should("be.enabled");
  cy.then(() => expect(identidades).to.have.length(1));
});
Then("vou ao login com retorno ao carrinho e operação preservada", () => {
  cy.location("pathname").should("eq", "/login");
  cy.location("search").should("contain", "retorno=%2Fcarrinho");
  cy.window().then((win) =>
    expect(win.sessionStorage.getItem(chave)).to.eq(identidades[0]),
  );
});
Then("a finalização fica indisponível sem enviar pedido", () => {
  cy.get('[data-cy="finalizacao-indisponivel"]').should("be.visible");
  cy.get('[data-cy="finalizar-compra"]').should("be.disabled");
  cy.then(() => expect(identidades).to.have.length(0));
});
Then("a identidade de outro cliente não foi utilizada", () =>
  cy.then(() => expect(identidades[0]).not.to.eq(identidadeAlheia)),
);
When("aumento a quantidade antes de finalizar", () =>
  cy.get('[data-cy="aumentar-item"]').click(),
);
Then("a finalização espera a alteração do carrinho", () => {
  cy.get('[data-cy="finalizar-compra"]').should("be.disabled");
  cy.then(() => expect(identidades).to.have.length(0));
  cy.wait("@alteracaoCheckout");
  cy.get('[data-cy="total-carrinho"]').should("contain.text", "39,80");
  cy.get('[data-cy="finalizar-compra"]').should("be.enabled");
});
Then("a recuperação da finalização cabe na tela", () => {
  cy.document().then((doc) =>
    expect(doc.documentElement.scrollWidth).to.be.at.most(320),
  );
  cy.get('[data-cy="item-carrinho"]').then(($item) => {
    const arte = $item[0].querySelector(".arte-jogo")!.getBoundingClientRect();
    const elementoDados = $item[0].querySelector(".item-carrinho-dados")!;
    const dados = elementoDados.getBoundingClientRect();
    expect(
      elementoDados.scrollWidth,
      "Dados do jogo não ficam cortados",
    ).to.be.at.most(elementoDados.clientWidth);
    expect(
      arte.right <= dados.left || arte.bottom <= dados.top,
      "Capa e dados do jogo não se sobrepõem",
    ).to.eq(true);
  });
  cy.screenshot("GK-14-recuperacao-mobile");
});
