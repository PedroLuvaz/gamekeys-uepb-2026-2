import {
  Before,
  Given,
  When,
  Then,
} from "@badeball/cypress-cucumber-preprocessor";

const ficha = {
  id: 101,
  slug: "caminhos-de-aurora",
  nome: "Caminhos de Aurora",
  capa_url: null,
  descricao: "Explore novos mundos.",
  genero: "Aventura",
  plataforma: "PC",
  classificacao: "18",
  preco: "19.90",
  disponibilidade: "Disponível",
};
let usuario: {
  id: number;
  nome: string;
  email: string;
  data_nascimento: string;
  perfil: string;
};
let jogo = { ...ficha };
let autenticado = true;
let modo = "sucesso";
let quantidadeFinal = 0;
let envios = 0;
let liberarAdicao: (() => void) | null = null;
const origem = "/jogos/101?origem=2";

Before({ tags: "@US-11" }, () => {
  usuario = {
    id: 7,
    nome: "Cliente Carrinho",
    email: "carrinho@example.com",
    data_nascimento: "1990-01-01",
    perfil: "cliente",
  };
  jogo = { ...ficha };
  autenticado = true;
  modo = "sucesso";
  quantidadeFinal = 0;
  envios = 0;
  liberarAdicao = null;
  cy.intercept("GET", "**/api/jogos/101", (pedido) => pedido.reply(jogo));
  cy.intercept("GET", "**/api/auth/me", (pedido) => pedido.reply(usuario));
  cy.intercept("POST", "**/api/auth/login", (pedido) => {
    modo = "sucesso";
    pedido.reply({
      access_token: "token-carrinho",
      token_type: "bearer",
      expires_in: 3600,
      usuario,
    });
  }).as("loginCarrinho");
  cy.intercept("POST", "**/api/carrinho/itens", (pedido) => {
    envios++;
    if (modo === "incompleta") {
      pedido.reply({ quantidade: 1 });
      return;
    }
    expect(pedido.headers.authorization).to.eq("Bearer token-carrinho");
    expect(pedido.body).to.deep.equal({
      jogo_id: 101,
      quantidade: pedido.body.quantidade,
    });
    const erros: Record<string, [number, string]> = {
      estoque: [409, "Estoque insuficiente para a quantidade solicitada."],
      idade: [403, "Sua idade não permite adicionar este jogo ao carrinho."],
      sessao: [401, "Não foi possível autenticar. Entre novamente."],
      servico: [
        503,
        "Carrinho temporariamente indisponível. Tente novamente em instantes.",
      ],
    };
    if (erros[modo]) {
      pedido.reply({
        statusCode: erros[modo][0],
        body: { detail: erros[modo][1] },
      });
      return;
    }
    quantidadeFinal += pedido.body.quantidade;
    const resposta = {
      carrinho_id: 4,
      jogo_id: 101,
      nome: jogo.nome,
      quantidade: quantidadeFinal,
      preco_unitario: jogo.preco,
      subtotal:
        modo === "valor-grande"
          ? "214748364678525163.53"
          : (19.9 * quantidadeFinal).toFixed(2),
    };
    if (modo === "demora")
      return new Promise<void>((resolve) => {
        liberarAdicao = () => {
          pedido.reply({ body: resposta });
          resolve();
        };
      });
    pedido.reply({ body: resposta });
  }).as("adicaoCarrinho");
});

Given("que estou autenticado para adicionar um jogo disponível", () => {});
Given("que estou sem sessão ao escolher um jogo", () => {
  autenticado = false;
});
Given("que a adição é recusada por estoque insuficiente", () => {
  modo = "estoque";
});
Given("que a adição é recusada por classificação etária", () => {
  modo = "idade";
});
Given("que a adição demora para ser confirmada", () => {
  modo = "demora";
});
Given("que o servidor rejeita minha sessão ao adicionar", () => {
  modo = "sessao";
});
Given("que o jogo escolhido está esgotado", () => {
  jogo.disponibilidade = "Esgotado";
});
Given("que o serviço de carrinho está indisponível", () => {
  modo = "servico";
});
Given("que a conexão da ficha falha ao adicionar ao carrinho", () => {
  modo = "rede";
});
Given("que estou usando uma conta de administrador na ficha", () => {
  usuario.perfil = "administrador";
});
Given(
  "que a adição retorna um subtotal acima do limite seguro de ponto flutuante",
  () => {
    modo = "valor-grande";
    jogo.preco = "99999999.99";
  },
);
Given("que o carrinho retorna uma confirmação incompleta", () => {
  modo = "incompleta";
});

When("abro a ficha para adicionar ao carrinho", () => {
  cy.visit(origem, {
    onBeforeLoad(janela) {
      janela.sessionStorage.clear();
      if (autenticado)
        janela.sessionStorage.setItem(
          "gamekeys.sessao",
          JSON.stringify({
            token: "token-carrinho",
            expiraEm: Date.now() + 3600000,
            usuario,
          }),
        );
      if (modo === "rede") {
        const original = janela.fetch.bind(janela);
        cy.stub(janela, "fetch").callsFake(
          (entrada: RequestInfo | URL, opcoes?: RequestInit) => {
            if (String(entrada).includes("/carrinho/itens")) {
              envios++;
              return Promise.reject(new TypeError("Falha simulada de rede"));
            }
            return original(entrada, opcoes);
          },
        );
      }
    },
  });
});
When("adiciono o jogo pela ficha", () =>
  cy.get('[data-cy="adicionar-carrinho"]').click(),
);
When("escolho {int} unidades na ficha", (quantidade: number) =>
  cy.get('[data-cy="quantidade-carrinho"]').clear().type(String(quantidade)),
);
When("peço para entrar e adicionar ao carrinho", () =>
  cy.get('[data-cy="entrar-para-adicionar"]').click(),
);
When("concluo o login para retornar à ficha", () => {
  cy.get('input[name="email"]').type("carrinho@example.com");
  cy.get('input[name="senha"]').type("senha-ficticia", { log: false });
  cy.get('[data-cy="enviar-login"]').click();
  cy.wait("@loginCarrinho");
});
When("envio duas vezes o formulário imediatamente", () => {
  // Os dois eventos precisam ocorrer no mesmo turno, sem esperas de actionability do Cypress.
  cy.get('[data-cy="formulario-carrinho"]').then(($formulario) => {
    $formulario[0].dispatchEvent(
      new Event("submit", { bubbles: true, cancelable: true }),
    );
    $formulario[0].dispatchEvent(
      new Event("submit", { bubbles: true, cancelable: true }),
    );
  });
});
When("abro o login com um retorno externo", () =>
  cy.visit("/login?retorno=https%3A%2F%2Fexample.com"),
);

Then(
  "a ficha confirma {int} unidade(s) no carrinho e subtotal de {word}",
  (quantidade: number, subtotal: string) => {
    cy.get('[data-cy="resultado-carrinho"]')
      .should("contain.text", "Adicionado ao carrinho.")
      .and(
        "contain.text",
        `Você tem ${quantidade} ${quantidade === 1 ? "unidade" : "unidades"} deste jogo.`,
      )
      .and("contain.text", subtotal);
    cy.get('[data-cy="erro-carrinho"]').should("not.exist");
  },
);
Then("retorno ao mesmo jogo e à página de origem sem adição automática", () => {
  cy.location("pathname").should("eq", "/jogos/101");
  cy.location("search").should("eq", "?origem=2");
  cy.get('[data-cy="adicionar-carrinho"]').should("be.visible");
  cy.then(() => expect(envios).to.eq(0));
});
Then("vejo na ficha o motivo de estoque insuficiente", () =>
  cy
    .get('[data-cy="erro-carrinho"]')
    .should("contain.text", "Estoque insuficiente"),
);
Then("vejo na ficha o motivo de classificação etária", () =>
  cy
    .get('[data-cy="erro-carrinho"]')
    .should("contain.text", "Sua idade não permite"),
);
Then("a ficha informa que está adicionando e bloqueia novo envio", () => {
  cy.get('[data-cy="formulario-carrinho"]').should(
    "have.attr",
    "aria-busy",
    "true",
  );
  cy.get('[data-cy="adicionar-carrinho"]')
    .should("be.disabled")
    .and("contain.text", "Adicionando");
  cy.get('[data-cy="quantidade-carrinho"]').should("be.disabled");
  // A resposta só é liberada após verificar o carregamento, sem espera fixa.
  cy.wrap(null)
    .should(() => expect(liberarAdicao).to.be.a("function"))
    .then(() => liberarAdicao!());
  cy.wait("@adicaoCarrinho");
});
Then("somente uma adição foi enviada", () =>
  cy.then(() => expect(envios).to.eq(1)),
);
Then("nenhuma adição foi enviada", () =>
  cy.then(() => expect(envios).to.eq(0)),
);
Then("vou ao login do carrinho com sessão expirada e sem token local", () => {
  cy.location("pathname").should("eq", "/login");
  cy.get('[data-cy="sessao-expirada"]').should("be.visible");
  cy.window()
    .its("sessionStorage")
    .invoke("getItem", "gamekeys.sessao")
    .should("be.null");
});
Then("a ação de adicionar está desabilitada por esgotamento", () =>
  cy
    .get('[data-cy="adicionar-carrinho"]')
    .should("be.disabled")
    .and("contain.text", "Esgotado"),
);
Then("vejo na ficha a mensagem de carrinho indisponível", () =>
  cy
    .get('[data-cy="erro-carrinho"]')
    .should("contain.text", "Carrinho temporariamente indisponível"),
);
Then("sou informado de que não foi possível confirmar a adição", () => {
  cy.get('[data-cy="erro-carrinho"]').should(
    "contain.text",
    "Não foi possível confirmar",
  );
  cy.get('[data-cy="resultado-carrinho"]').should("not.exist");
});
Then("vejo que o carrinho é exclusivo de clientes", () => {
  cy.get('[data-cy="perfil-sem-carrinho"]').should(
    "contain.text",
    "exclusivo de contas de cliente",
  );
  cy.get('[data-cy="adicionar-carrinho"]').should("not.exist");
});
Then("a quantidade da ficha é inválida", () =>
  cy
    .get<HTMLInputElement>('[data-cy="quantidade-carrinho"]')
    .then(($input) => expect($input[0].validity.valid).to.eq(false)),
);
Then("o login mantém a navegação dentro do GameKeys", () => {
  cy.location("pathname").should("eq", "/conta");
  cy.get('[data-cy="conta-protegida"]').should("be.visible");
});
Then("vejo todos os centavos do subtotal grande", () =>
  cy
    .get('[data-cy="resultado-carrinho"]')
    .should("contain.text", "214.748.364.678.525.163,53"),
);
