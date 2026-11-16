# GK-47 — Preço congelado no pedido

Auditoria e regressão executadas em 16/11/2026 sobre a `main` no commit
`b8f8232`, com a complementação de teste na branch
`test/GK-47-preco-congelado-pedido`.

O banco autorizado para esta verificação é exclusivamente o PostgreSQL local
isolado `gamekeys_teste`, na porta 5433. Durante as execuções,
`PYTHON_DOTENV_DISABLED=1` e `TEST_DATABASE_URL`, `DATABASE_URL` e
`DATABASE_URL_UNPOOLED` apontaram explicitamente para esse banco local. Nenhum teste
ou migração foi executado no Neon compartilhado.

## Relação entre os itens

| Item | Papel no fluxo verificado |
| --- | --- |
| GK-14 | Finaliza a compra e exige que cada item do pedido grave o preço garantido ao cliente. |
| GK-47 | Exige que mudanças posteriores no catálogo não alterem pedidos já feitos. |
| GK-73 | Driver de confiabilidade que mede 100% dos pedidos inalterados após a mudança de preço. |
| GK-16 | Consulta o pedido e registra o pagamento simulado usando os valores persistidos. |

## Auditoria do fluxo real

1. `POST /pedidos/reservas` bloqueia o carrinho e os jogos na mesma transação.
   O serviço calcula o total com o preço corrente, grava esse total em
   `vendas.pedidos.valor_total` e grava uma cópia do preço em cada linha de
   `vendas.itens_pedido.preco_unitario`.
2. `GET /pedidos/{id}` lê `valor_total` do pedido e calcula quantidade e subtotal
   somando `itens_pedido.preco_unitario`. O preço atual de `catalogo.jogos` não
   participa desses valores.
3. `POST /pedidos/{id}/pagamento` bloqueia o pedido, lê o `valor_total` persistido e
   copia exatamente esse valor para `vendas.pagamentos.valor`. O pagamento não
   consulta o preço atual do catálogo.
4. A resposta do pagamento e a consulta posterior continuam detalhando os itens a
   partir do preço gravado no pedido.

Não foi encontrada necessidade de alterar a implementação. A migração
`0004_reserva_chaves.sql` já separa o preço do item do preço do catálogo, e os
serviços de reserva, consulta e pagamento já respeitam essa separação.

## Cobertura e complementação

O teste existente
`test_valor_pago_e_o_gravado_no_pedido_mesmo_com_preco_novo_no_catalogo` já
provava um jogo de R$ 50,00 alterado para R$ 70,00 e o pagamento de R$ 50,00.
Ele foi ampliado, sem criar outro fluxo de teste, para cobrir as lacunas abaixo:

| Verificação | Dados e resultado esperado | Cobertura |
| --- | --- | --- |
| Pedido antigo após mudança | pedido reservado antes de alterar os dois preços; consulta feita depois da alteração | coberta |
| Valores unitários | R$ 50,00 e R$ 7,25 permanecem no pedido após o catálogo mudar para R$ 70,00 e R$ 11,00 | coberta |
| Quantidades | duas unidades do primeiro jogo e três do segundo | coberta |
| Subtotais | R$ 100,00 e R$ 21,75 | coberta |
| Total do pedido | R$ 121,75 antes e depois do pagamento | coberta |
| Valor pago | uma linha aprovada de R$ 121,75 em `vendas.pagamentos` | coberta |
| Consulta posterior | pedido entregue preserva itens, subtotais e total | coberta |

Os testes já existentes continuam responsáveis pelas demais regras da GK-16 e da
reserva: entrega das chaves, ocultação antes da entrega, idempotência, concorrência,
isolamento entre clientes, recusas e rollback. Essas funcionalidades não foram
duplicadas na GK-47.

## Evidências locais

| Verificação | Ambiente | Resultado |
| --- | --- | --- |
| Teste GK-47 antes da complementação | PostgreSQL local `gamekeys_teste` | 1 passou |
| Teste GK-47 ampliado | mesmo banco local | 1 passou em 1,63 s |
| Regressão completa do backend (`pytest -q`) | mesmo banco local | 274 passaram em 48,58 s; um aviso de depreciação não bloqueante do `TestClient` |
| Análise estática (`ruff check .`) | código da branch | todos os checks passaram |

## Situação da DoD

Esta evidência comprova os critérios funcionais automatizados e a regressão local,
mas não conclui a DoD. Permanecem obrigatórios: CI verde do PR, revisão e aprovação
independentes, integração por PR, atualização das evidências com o resultado do CI,
homologação quando exigida pela Release 2 e aceite do PO. Nenhuma dessas etapas deve
ser inferida a partir dos testes locais.
