import {
  Before,
  Given,
  Then,
  When,
} from "@badeball/cypress-cucumber-preprocessor";

const usuario = {
  id: 606,
  nome: "Cliente Q-06",
  email: "q06@example.com",
  data_nascimento: "1990-01-01",
  perfil: "cliente",
};
const jogo = {
  id: 606,
  slug: "jogo-q06",
  nome: "Jogo Q-06",
  capa_url: null,
  preco: "19.90",
  disponibilidade: "Disponível",
  descricao: "Jogo usado apenas nas respostas controladas da auditoria.",
  genero: "Aventura",
  plataforma: "PC",
  classificacao: "Livre",
};

let respostaCarrinho: { statusCode: number; body: unknown };

function preencherCadastro() {
  cy.get('input[name="nome"]').type("Cliente Q-06");
  cy.get('input[name="email"]').type("q06@example.com");
  cy.get('input[name="data_nascimento"]').type("1990-01-01");
  cy.get('input[name="senha"]').type("segredo123");
}

function guardarSessao(janela: Window) {
  janela.sessionStorage.setItem(
    "gamekeys.sessao",
    JSON.stringify({
      token: "token-q06",
      expiraEm: Date.now() + 3_600_000,
      usuario,
    }),
  );
}

function prepararFicha() {
  cy.intercept("GET", "**/api/jogos/606", jogo).as("jogoQ06");
  cy.intercept("POST", "**/api/carrinho/itens", respostaCarrinho).as(
    "carrinhoQ06",
  );
  cy.visit("/jogos/606", { onBeforeLoad: guardarSessao });
  cy.wait("@jogoQ06");
}

Before({ tags: "@Q-06" }, () => {
  respostaCarrinho = {
    statusCode: 200,
    body: {
      carrinho_id: 606,
      jogo_id: 606,
      nome: jogo.nome,
      quantidade: 1,
      preco_unitario: "19.90",
      subtotal: "19.90",
    },
  };
});

When("envio o cadastro Q-06 sem preencher os dados", () => {
  cy.visit("/cadastro");
  cy.get('[data-cy="enviar-cadastro"]').click();
});

When("envio o cadastro Q-06 com e-mail inválido", () => {
  cy.visit("/cadastro");
  preencherCadastro();
  cy.get('input[name="email"]').clear().type("email-invalido");
  cy.get('[data-cy="enviar-cadastro"]').click();
});

When("envio o cadastro Q-06 com senha curta", () => {
  cy.visit("/cadastro");
  preencherCadastro();
  cy.get('input[name="senha"]').clear().type("1234567");
  cy.get('[data-cy="enviar-cadastro"]').click();
});

When("envio o cadastro Q-06 com data inválida", () => {
  cy.visit("/cadastro");
  preencherCadastro();
  cy.get('input[name="data_nascimento"]').clear().type("1899-12-31");
  cy.get('[data-cy="enviar-cadastro"]').click();
});

When("envio o cadastro Q-06 com senha acima de 72 bytes", () => {
  cy.visit("/cadastro");
  preencherCadastro();
  cy.get('input[name="senha"]').clear().type("a".repeat(73));
  cy.get('[data-cy="enviar-cadastro"]').click();
});

Given("que o cadastro Q-06 é recusado como duplicado", () => {
  cy.intercept("POST", "**/api/clientes", {
    statusCode: 409,
    body: { detail: "Este e-mail já está em uso." },
  }).as("cadastroQ06");
});

Given("que o cadastro Q-06 é recusado por indisponibilidade", () => {
  cy.intercept("POST", "**/api/clientes", {
    statusCode: 503,
    body: {
      detail: "Não foi possível concluir o cadastro. Tente novamente mais tarde.",
    },
  }).as("cadastroQ06");
});

Given("que a rede Q-06 falha no cadastro", () => {
  cy.intercept("POST", "**/api/clientes", { forceNetworkError: true }).as(
    "cadastroQ06",
  );
});

Given("que o cadastro Q-06 é recusado sem detalhe", () => {
  cy.intercept("POST", "**/api/clientes", {
    statusCode: 500,
    body: {},
  }).as("cadastroQ06");
});

Given("que o cadastro Q-06 recebe Field required", () => {
  cy.intercept("POST", "**/api/clientes", {
    statusCode: 422,
    body: {
      detail: [
        {
          type: "missing",
          loc: ["body", "nome"],
          msg: "Field required",
          input: {},
        },
      ],
    },
  }).as("cadastroQ06");
});

When("envio dados válidos no cadastro Q-06", () => {
  cy.visit("/cadastro");
  preencherCadastro();
  cy.get('[data-cy="enviar-cadastro"]').click();
  cy.wait("@cadastroQ06");
});

Then("a mensagem Q-06 é {string}", (mensagem: string) => {
  cy.get('[data-cy="erro-cadastro"]').should("have.text", mensagem);
});

Given("que o login Q-06 é recusado por credenciais", () => {
  cy.intercept("POST", "**/api/auth/login", {
    statusCode: 401,
    body: { detail: "E-mail ou senha incorretos." },
  }).as("loginQ06");
});

Given("que o login Q-06 é recusado por indisponibilidade", () => {
  cy.intercept("POST", "**/api/auth/login", {
    statusCode: 503,
    body: { detail: "Autenticação temporariamente indisponível." },
  }).as("loginQ06");
});

Given("que o login Q-06 é recusado sem detalhe", () => {
  cy.intercept("POST", "**/api/auth/login", {
    statusCode: 500,
    body: {},
  }).as("loginQ06");
});

Given("que o servidor Q-06 está indisponível no login", () => {
  cy.intercept("POST", "**/api/auth/login", { forceNetworkError: true }).as(
    "loginQ06",
  );
});

When("envio credenciais no login Q-06", () => {
  cy.visit("/login");
  cy.get('input[name="email"]').type("q06@example.com");
  cy.get('input[name="senha"]').type("segredo123");
  cy.get('[data-cy="enviar-login"]').click();
  cy.wait("@loginQ06");
});

When("envio o login Q-06 com e-mail inválido", () => {
  cy.visit("/login");
  cy.get('input[name="email"]').type("email-invalido");
  cy.get('input[name="senha"]').type("segredo123");
  cy.get('[data-cy="enviar-login"]').click();
});

When("envio o login Q-06 sem senha", () => {
  cy.visit("/login");
  cy.get('input[name="email"]').type("q06@example.com");
  cy.get('[data-cy="enviar-login"]').click();
});

Then("a mensagem de login Q-06 é {string}", (mensagem: string) => {
  cy.get('[data-cy="erro-login"]').should("have.text", mensagem);
});

Given("que a sessão Q-06 expirou no servidor", () => {
  cy.intercept("GET", "**/api/auth/me", {
    statusCode: 401,
    body: { detail: "Não foi possível autenticar. Entre novamente." },
  }).as("sessaoQ06");
});

Given("que a rede Q-06 falha ao validar a sessão", () => {
  cy.intercept("GET", "**/api/auth/me", { forceNetworkError: true }).as(
    "sessaoQ06",
  );
});

Given("que a validação Q-06 da sessão falha sem detalhe", () => {
  cy.intercept("GET", "**/api/auth/me", {
    statusCode: 503,
    body: {},
  }).as("sessaoQ06");
});

When("abro a conta protegida Q-06", () => {
  cy.visit("/conta", { onBeforeLoad: guardarSessao });
});

Then("vejo o aviso Q-06 de sessão expirada", () => {
  cy.wait("@sessaoQ06");
  cy.location("pathname").should("eq", "/login");
  cy.get('[data-cy="sessao-expirada"]').should(
    "contain.text",
    "Sua sessão expirou. Entre novamente para continuar.",
  );
});

Then("a conta Q-06 informa {string}", (mensagem: string) => {
  cy.wait("@sessaoQ06");
  cy.get('[data-cy="erro"]').should("contain.text", mensagem);
});

When("abro o carrinho Q-06 sem sessão", () => {
  cy.visit("/carrinho", {
    onBeforeLoad(janela) {
      janela.sessionStorage.clear();
    },
  });
});

Then("o carrinho Q-06 exige login e preserva o retorno", () => {
  cy.location("pathname").should("eq", "/login");
  cy.location("search").should("eq", `?retorno=${encodeURIComponent("/carrinho")}`);
  cy.get('[data-cy="formulario-login"]').should("be.visible");
});

When("abro o carrinho Q-06 com perfil administrador", () => {
  cy.visit("/carrinho", {
    onBeforeLoad(janela) {
      guardarSessao(janela);
      const sessao = JSON.parse(
        janela.sessionStorage.getItem("gamekeys.sessao") || "{}",
      );
      sessao.usuario.perfil = "administrador";
      janela.sessionStorage.setItem("gamekeys.sessao", JSON.stringify(sessao));
    },
  });
});

Then("o carrinho Q-06 informa {string}", (mensagem: string) => {
  cy.get('[data-cy="carrinho-perfil-invalido"]').should(
    "contain.text",
    mensagem,
  );
});

Given("que preparo a ficha Q-06 com resposta de sucesso", () => {
  prepararFicha();
});

Given(
  "que preparo a ficha Q-06 com status {int} e mensagem {string}",
  (statusCode: number, mensagem: string) => {
    respostaCarrinho = { statusCode, body: { detail: mensagem } };
    prepararFicha();
  },
);

Given("que preparo a ficha Q-06 com validação em inglês", () => {
  respostaCarrinho = {
    statusCode: 422,
    body: {
      detail: [
        {
          type: "int_type",
          loc: ["body", "quantidade"],
          msg: "Input should be a valid integer",
          input: "uma",
        },
      ],
    },
  };
  prepararFicha();
});

When("adiciono a quantidade Q-06 {string}", (quantidade: string) => {
  cy.get('[data-cy="quantidade-carrinho"]').clear().type(quantidade);
  cy.get('[data-cy="adicionar-carrinho"]').click();
});

Then("a mensagem do carrinho Q-06 é {string}", (mensagem: string) => {
  cy.get('[data-cy="erro-carrinho"]').should("have.text", mensagem);
});

Given(
  "que a alteração Q-06 do carrinho falha com status {int} e mensagem {string}",
  (statusCode: number, mensagem: string) => {
    prepararPaginaCarrinho({ statusCode, body: { detail: mensagem } });
  },
);

Given("que a alteração Q-06 do carrinho falha sem detalhe", () => {
  prepararPaginaCarrinho({ statusCode: 500, body: {} });
});

function carrinhoComItem() {
  return {
    itens: [
      {
        jogo_id: 606,
        slug: jogo.slug,
        nome: jogo.nome,
        capa_url: null,
        quantidade: 1,
        estoque_disponivel: 3,
        preco_unitario: "19.90",
        subtotal: "19.90",
      },
    ],
    total: "19.90",
  };
}

function prepararPaginaCarrinho(respostaPatch: {
  statusCode: number;
  body: unknown;
}) {
  cy.intercept("GET", "**/api/carrinho", carrinhoComItem()).as(
    "consultaCarrinhoQ06",
  );
  cy.intercept("PATCH", "**/api/carrinho/itens/606", respostaPatch).as(
    "alteracaoCarrinhoQ06",
  );
  cy.visit("/carrinho", { onBeforeLoad: guardarSessao });
  cy.wait("@consultaCarrinhoQ06");
}

When("aumento o item no carrinho Q-06", () => {
  cy.get('[data-cy="aumentar-item"]').click();
  cy.wait("@alteracaoCarrinhoQ06");
});

Then("a atualização Q-06 informa {string}", (mensagem: string) => {
  cy.get('[data-cy="mensagem-carrinho-erro"]').should("have.text", mensagem);
});

Given("que a consulta Q-06 do carrinho retorna dados inválidos", () => {
  cy.intercept("GET", "**/api/carrinho", { itens: [], total: 0 }).as(
    "consultaCarrinhoQ06",
  );
});

When("abro o carrinho autenticado Q-06", () => {
  cy.visit("/carrinho", { onBeforeLoad: guardarSessao });
  cy.wait("@consultaCarrinhoQ06");
});

Then("a consulta Q-06 informa {string}", (mensagem: string) => {
  cy.get('[data-cy="erro-carrinho-pagina"]').should("contain.text", mensagem);
});

Then("a tela Q-06 não exibe mensagens padrão em inglês", () => {
  cy.get("body")
    .should("not.contain.text", "Field required")
    .and("not.contain.text", "Input should be");
});
