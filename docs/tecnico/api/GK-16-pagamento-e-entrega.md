# GK-16 — Pagamento simulado e entrega da chave

## Entrega e fronteiras

O pagamento parte do pedido `aguardando_pagamento` criado pela reserva (GK-15,
`POST /pedidos/reservas`). Ao confirmar o pagamento simulado, a API grava o pagamento,
marca as chaves do pedido como `vendida` e passa o pedido para `entregue`, tudo na mesma
transação. Só então os códigos aparecem. Qualquer falha desfaz as três coisas.

Fora desta entrega: tela de checkout (GK-14), histórico e validação das transições de
status (GK-13), cancelamento e expiração da reserva (Release 3). O pagamento é simulado
e sempre aprovado; a coluna `status` de `vendas.pagamentos` já aceita `recusado` para
quando existir um cenário de recusa.

## Banco (migração 0005)

- `vendas.pedidos.status` passa a aceitar `entregue`, e a tabela ganha `entregue_em`.
- `vendas.pagamentos` é criada como no DER (`pedido_id` único, `metodo`, `status`, `valor`).
- A GK-13 também mexe em `vendas.pedidos`. Quem mesclar depois renumera a própria migração.

O DER em `docs/tecnico/banco/` ainda está na v1.1 e precisa da v1.2 com essas mudanças
e com a tabela de histórico da GK-13.

## Endpoints

Os dois exigem `Authorization: Bearer <token>` de uma conta de cliente.

### `POST /pedidos/{pedido_id}/pagamento`

```json
{"metodo": "pix"}
```

`metodo` aceita `cartao`, `pix` ou `boleto`. O corpo recusa campos adicionais: valor,
comprador e status vêm do banco, nunca do cliente.

Resposta HTTP 200:

```json
{
  "pedido_id": 7,
  "status": "entregue",
  "valor_total": "39.80",
  "itens": [
    {"jogo_id": 3, "nome": "Lenda Esquecida", "quantidade": 2, "preco_unitario": "19.90", "subtotal": "39.80"}
  ],
  "chaves": [
    {"jogo_id": 3, "nome": "Lenda Esquecida", "codigo": "XXXX-XXXX-XXXX"},
    {"jogo_id": 3, "nome": "Lenda Esquecida", "codigo": "YYYY-YYYY-YYYY"}
  ]
}
```

Repetir o pagamento de um pedido já entregue devolve a mesma resposta e não grava um
segundo pagamento (o método da primeira chamada é o que vale). Dois cliques simultâneos
são serializados pelo bloqueio da linha do pedido.

### `GET /pedidos/{pedido_id}`

Mesmo formato da resposta acima. Enquanto o pedido não está `entregue`, `chaves` vem
vazia e o código nem é lido do banco.

### Erros

| HTTP | Motivo |
| --- | --- |
| 401 | JWT ausente, inválido ou expirado |
| 403 | Perfil diferente de cliente |
| 404 | Pedido inexistente ou de outro cliente (a resposta é a mesma nos dois casos) |
| 409 | Pedido que não está aguardando pagamento (por exemplo, cancelado) |
| 422 | Método de pagamento ou identificador de pedido inválido |
| 503 | Banco indisponível, pool esgotado ou tempo limite de bloqueio/consulta |

## Tela

`/pedidos/{pedido_id}` no front-end (`frontend/src/Pedido.tsx`) mostra a situação, os itens
com o preço da compra e o total. Com o pedido aguardando pagamento, oferece a forma de
pagamento e o botão de confirmar; depois da entrega, lista as chaves. A tela sempre mostra
carregando, pedido não encontrado ou erro com "tentar novamente" (GK-48), bloqueia o envio
duplicado e volta ao login com retorno quando a sessão expira. A GK-14 leva o cliente a essa
rota depois de finalizar a compra. Cenários em `frontend/cypress/e2e/pagamento-pedido.feature`.

## Critérios de aceite e testes

| Cenário da GK-16 | Teste |
| --- | --- |
| 1. Pagamento: o pedido fica Entregue e vejo minhas chaves | `test_pagamento_entrega_as_chaves_e_registra_o_pagamento` |
| 2. Antes da entrega o código não aparece | `test_consulta_antes_da_entrega_nao_mostra_codigos` |

Também cobertos em `backend/tests/test_pagamentos_banco.py`: preço gravado no pedido
mesmo com preço novo no catálogo (GK-47 e DA-CON-I2-02), repetição e concorrência do
pagamento, pedido de outro cliente, pedido cancelado, administrador e desfazimento
quando uma chave do pedido não está mais reservada. O contrato HTTP e as mensagens
estão em `backend/tests/test_pagamentos.py`.

## Pendências para fechar a história

- Integrar a mudança de status com o histórico da GK-13 quando ela existir.
- Aplicar a migração 0005 no banco de homologação depois do merge.
- Evidência do QA nos dois cenários e aceite do PO registrado no Jira.
