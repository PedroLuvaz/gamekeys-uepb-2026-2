interface FixtureCheckout {
  chave: string;
  jogoId: number;
  emailAdulto: string;
  emailMenor: string;
  senha: string;
}

interface EstadoCheckout {
  quantidade: number;
  estoque: number;
  pedidos: number;
  totalPedidos: string;
  reservadas: number;
  vendidas: number;
  pagamentos: number;
  valorPago: string;
}

describe("GK-14 — finalização com API e PostgreSQL reais", () => {
  let fixture: FixtureCheckout | null = null;

  beforeEach(() => {
    fixture = null;
    cy.request("/api/saude/banco")
      .its("body.banco")
      .should("eq", "gamekeys_teste");
    cy.task<FixtureCheckout>("checkout:preparar", null, { log: false }).then(
      (dados) => {
        fixture = dados;
      },
    );
  });

  afterEach(() => {
    if (fixture)
      cy.task("checkout:limpar", { chave: fixture.chave }, { log: false });
  });

  function entrar() {
    cy.then(() => {
      cy.visit(
        `/login?retorno=${encodeURIComponent(`/jogos/${fixture!.jogoId}`)}`,
      );
      cy.get('input[name="email"]').type(fixture!.emailAdulto);
      cy.get('input[name="senha"]').type(fixture!.senha, { log: false });
      cy.get('[data-cy="enviar-login"]').click();
      cy.get('[data-cy="adicionar-carrinho"]').should("be.enabled");
    });
  }

  function adicionar() {
    cy.get('[data-cy="adicionar-carrinho"]').click();
    cy.get('[data-cy="resultado-carrinho"]').should("be.visible");
    cy.visit("/carrinho");
    cy.get('[data-cy="total-carrinho"]').should("contain.text", "19,90");
  }

  function conferir(esperado: Partial<EstadoCheckout>) {
    cy.then(() =>
      cy.task<EstadoCheckout>(
        "checkout:estado",
        { chave: fixture!.chave },
        { log: false },
      ),
    ).then((estado) => expect(estado).to.include(esperado));
  }

  function token() {
    return cy
      .window({ log: false })
      .then(
        (win) =>
          JSON.parse(win.sessionStorage.getItem("gamekeys.sessao")!)
            .token as string,
      );
  }

  it("cria o pedido, congela o preço e entrega somente após pagar o valor gravado", () => {
    entrar();
    adicionar();
    cy.intercept("POST", "**/api/pedidos/reservas").as("reservaReal");
    cy.get('[data-cy="finalizar-compra"]').click();
    cy.wait("@reservaReal").then(({ request, response }) => {
      expect(Object.keys(request.body)).to.deep.eq(["chave_idempotencia"]);
      expect(response!.statusCode).to.eq(200);
      expect(response!.body).not.to.have.property("chaves");
      expect(response!.body.itens[0]).not.to.have.property("codigo");
    });
    cy.location("pathname").should("match", /^\/pedidos\/\d+$/);
    cy.get('[data-cy="total-pedido"]').should("contain.text", "19,90");
    cy.get('[data-cy="chave-entregue"]').should("not.exist");
    conferir({
      pedidos: 1,
      quantidade: 0,
      estoque: 2,
      reservadas: 1,
      vendidas: 0,
      pagamentos: 0,
    });
    cy.then(() =>
      cy.task(
        "checkout:alterar-preco",
        { chave: fixture!.chave },
        { log: false },
      ),
    );
    cy.reload();
    cy.get('[data-cy="total-pedido"]').should("contain.text", "19,90");
    cy.get('[data-cy="itens-pedido"]').should("contain.text", "19,90");
    cy.get('[data-cy="confirmar-pagamento"]').click();
    cy.get('[data-cy="chave-entregue"]').should("have.length", 1);
    cy.get('[data-cy="total-pedido"]').should("contain.text", "19,90");
    conferir({
      pedidos: 1,
      totalPedidos: "19.90",
      reservadas: 0,
      vendidas: 1,
      pagamentos: 1,
      valorPago: "19.90",
    });
    cy.screenshot("GK-14-compra-real-concluida");
  });

  it("recupera após confirmação perdida e recarga sem duplicar pedido nem apagar um novo carrinho", () => {
    entrar();
    adicionar();
    const identidades: string[] = [];
    let pedidoId = 0;
    cy.intercept("POST", "**/api/pedidos/reservas", (req) => {
      identidades.push(req.body.chave_idempotencia);
      // O servidor efetiva a transação real; somente a primeira confirmação é truncada.
      req.continue((res) => {
        expect(res.statusCode).to.eq(200);
        if (!pedidoId) {
          pedidoId = res.body.pedido_id;
          res.send({ statusCode: 200, body: { pedido_id: pedidoId } });
        } else expect(res.body.pedido_id).to.eq(pedidoId);
      });
    }).as("recuperacaoReal");
    cy.get('[data-cy="finalizar-compra"]').click();
    cy.get('[data-cy="finalizacao-pendente"]').should("be.visible");
    conferir({ pedidos: 1, quantidade: 0, estoque: 2, reservadas: 1 });
    cy.reload();
    cy.get('[data-cy="carrinho-vazio"]').should("be.visible");
    cy.get('[data-cy="recuperar-finalizacao"]').should("be.enabled");
    cy.then(() => expect(identidades).to.have.length(1));
    // Simula outro dispositivo enchendo o carrinho após a primeira compra.
    token().then((valor) =>
      cy.request({
        method: "POST",
        url: "/api/carrinho/itens",
        headers: { Authorization: `Bearer ${valor}` },
        body: { jogo_id: fixture!.jogoId, quantidade: 1 },
        log: false,
      }),
    );
    cy.get('[data-cy="recuperar-finalizacao"]').click();
    cy.location("pathname").should("match", /^\/pedidos\/\d+$/);
    cy.then(() => {
      expect(identidades).to.have.length(2);
      expect(identidades[0]).to.eq(identidades[1]);
      cy.location("pathname").should("eq", `/pedidos/${pedidoId}`);
    });
    conferir({ pedidos: 1, quantidade: 1, estoque: 2, reservadas: 1 });
  });

  it("recusa carrinho vazio, adulteração e acesso de outro cliente ao pedido", () => {
    entrar();
    token().then((valor) => {
      const base = {
        method: "POST" as const,
        url: "/api/pedidos/reservas",
        headers: { Authorization: `Bearer ${valor}` },
        failOnStatusCode: false,
        log: false,
      };
      cy.request({ ...base, body: { chave_idempotencia: crypto.randomUUID() } })
        .its("status")
        .should("eq", 409);
      cy.request({
        ...base,
        body: {
          chave_idempotencia: crypto.randomUUID(),
          valor_total: "0.01",
          usuario_id: 1,
        },
      })
        .its("status")
        .should("eq", 422);
      cy.request({
        ...base,
        headers: {},
        body: { chave_idempotencia: crypto.randomUUID() },
      })
        .its("status")
        .should("eq", 401);
    });
    conferir({ pedidos: 0, reservadas: 0, estoque: 3 });
    adicionar();
    cy.get('[data-cy="finalizar-compra"]').click();
    cy.location("pathname")
      .should("match", /^\/pedidos\/\d+$/)
      .then((pedidoPath) => {
        cy.request({
          method: "POST",
          url: "/api/auth/login",
          body: { email: fixture!.emailMenor, senha: fixture!.senha },
          log: false,
        }).then(({ body }) => {
          const headers = { Authorization: `Bearer ${body.access_token}` };
          cy.request({
            url: `/api${pedidoPath}`,
            headers,
            failOnStatusCode: false,
            log: false,
          })
            .its("status")
            .should("eq", 404);
          cy.request({
            method: "POST",
            url: `/api${pedidoPath}/pagamento`,
            headers,
            body: { metodo: "pix" },
            failOnStatusCode: false,
            log: false,
          })
            .its("status")
            .should("eq", 404);
        });
      });
    conferir({ pedidos: 1, reservadas: 1, vendidas: 0, pagamentos: 0 });
  });
});
