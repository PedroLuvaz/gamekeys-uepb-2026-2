# GK-15 / GK-124 — Reserva de chaves

## Entrega e fronteiras

A reserva usa o carrinho persistido do cliente autenticado, grava um pedido
`aguardando_pagamento` e associa uma linha de `vendas.itens_pedido` a cada chave.
Se tudo der certo, esvazia o carrinho na mesma transação. Se faltar uma chave ou
ocorrer falha, desfaz pedido, itens, estados das chaves, contador e limpeza do carrinho.

Esta entrega prepara o serviço usado pelo fechamento da GK-14. A tela de checkout,
pagamento, entrega dos códigos (GK-16), expiração e cancelamento não são implementados
aqui. A reserva não tem liberação automática: as chaves permanecem reservadas até
uma transição explícita futura. Nenhum código aparece no contrato HTTP ou nos logs.

## Endpoint

`POST /pedidos/reservas`, com `Authorization: Bearer <token>`.

```json
{"chave_idempotencia":"80b16ad3-8687-4bdd-8254-07d3d59d7895"}
```

O UUID identifica uma intenção de reserva. O cliente deve guardá-lo enquanto não
souber o resultado. Repetir esse UUID com o mesmo usuário recupera o pedido
persistido, mesmo que o carrinho esteja vazio ou tenha sido preenchido novamente.
O novo carrinho não é apagado nessa recuperação. Um UUID novo representa outra
intenção. Usuários distintos podem usar o mesmo UUID e nunca recuperam o pedido alheio.
Erros com rollback não gravam o UUID nem um pedido parcial.

O corpo recusa campos adicionais. Comprador, jogos, quantidades e preços vêm da
sessão e do banco. A aplicação não recebe preço, ID de outro usuário ou chave de ativação.

Resposta HTTP 200, tanto na criação quanto na recuperação:

```json
{
  "pedido_id": 7,
  "status": "aguardando_pagamento",
  "valor_total": "39.80",
  "itens": [
    {"jogo_id": 3, "quantidade": 2, "preco_unitario": "19.90", "subtotal": "39.80"}
  ]
}
```

Preços são decimais persistidos no momento da reserva. Uma mudança posterior no
catálogo não altera essa resposta. Não existe endpoint público de consulta de
pedido nem entrega de código nesta subtarefa.

| HTTP | Motivo |
| --- | --- |
| 401 | JWT ausente, inválido ou expirado |
| 403 | Perfil diferente de cliente ou classificação etária acima da idade |
| 404 | Jogo do carrinho inexistente ou inativo |
| 409 | Carrinho vazio ou não há chaves livres suficientes para reservar tudo |
| 422 | UUID/entrada inválida ou limite operacional/monetário excedido |
| 503 | Banco indisponível, pool esgotado ou tempo limite de bloqueio/consulta |

Limites operacionais desta API: até 100 jogos distintos e 1.000 unidades por
pedido. Valor máximo R$ 99.999.999,99, conforme `numeric(10,2)` do DER. A validação
ocorre antes de alocar chaves. Esses limites evitam requisições com trabalho sem
limite, inclusive quando o carrinho legado aceita quantidades maiores.

## Transação e uso pela GK-126/GK-14

O wrapper `app.servicos.reservas.reservar_carrinho(cliente, uuid)` obtém a conexão
do pool e controla commit/rollback. O serviço
`reservar_na_conexao(conexao, cliente, uuid)` permite compor o fluxo da GK-14
na mesma transação. Ele recusa conexão sem uma transação externa ativa.
Um savepoint interno desfaz toda a operação se houver recusa, inclusive se o
chamador tratar a exceção e efetivar outras operações na transação externa.

`app.servicos.reserva_chaves.reservar_chaves(conexao, jogo_id, quantidade)` é a
primitiva reutilizável pela GK-126: seleciona IDs livres com
`FOR UPDATE SKIP LOCKED`, exige a quantidade integral e muda o estado para
`reservada`. Não abre pool, não faz commit e não lê códigos. O chamador deve
propagar falhas para desfazer a transação inteira, incluindo jogos já processados.

Ordem comum a todos os escritores:

1. Bloquear o carrinho do próprio cliente com `bloquear_carrinho` da GK-11/GK-12.
2. Bloquear os jogos em ordem crescente de ID com `FOR NO KEY UPDATE`.
3. Selecionar e bloquear as chaves em ordem crescente de ID.
4. Gravar pedido/itens, limpar carrinho e efetivar uma única transação.

O bloqueio do jogo mantém preço e contador estáveis durante a reserva. Reservas
do mesmo jogo são serializadas brevemente; jogos independentes continuam em paralelo.
`NO KEY UPDATE` permite os bloqueios de FK `KEY SHARE` de outros clientes.
Não há bloqueio global nem estado de reserva em memória do servidor.

Os limites locais são `lock_timeout=2s` e `statement_timeout=5s` por instrução,
compatíveis com PgBouncer em modo transação. Timeout é 503 e causa rollback.
`SKIP LOCKED` trata chaves momentaneamente bloqueadas como indisponíveis nessa
tentativa; não implica que estejam definitivamente vendidas. Não há retentativa
automática dentro da transação.

Índices: chaves disponíveis por `(jogo_id,id)`, itens por pedido/jogo e unicidade
de `(usuario_id,chave_idempotencia)`. O banco também impõe `UNIQUE(chave_id)` e
FK composta `(chave_id,jogo_id)`: uma chave não pode aparecer em dois itens nem
ser associada ao jogo errado. Busca de metadados é em lote; inserção de itens usa
`unnest` por jogo, com trabalho limitado pelos limites acima.

## Migração e estoque

`backend/migracoes/0004_reserva_chaves.sql` cria as tabelas físicas do DER,
acrescenta idempotência e mantém `catalogo.jogos.chaves_disponiveis` por trigger
nas inserções, exclusões e transições de status das chaves. Apenas `disponivel`
conta como estoque. Reservar diminui o contador; rollback o restaura. Mudar o
jogo de uma chave existente é recusado.

**A migração zera os contadores legados**, pois eles ainda não representam chaves
físicas. Sem cadastrar chaves, os jogos ficam esgotados. O responsável do banco
deve planejar a migração e a carga de chaves válidas antes da publicação. Rotas
não executam DDL. O usuário `gamekeys_equipe` mantém DML, sem criar tabelas.

Novos fluxos de administração/importação devem bloquear os jogos em ordem antes
de alterar chaves, seguindo a ordem acima. Não escrever diretamente no contador:
ele é mantido pelo trigger. Acesso SQL que desrespeite a ordem pode sofrer deadlock
e rollback; não deve ser usado como fluxo concorrente da aplicação.

`python -m app.migrar --carga` é explicitamente uma **carga de demonstração**:
gera códigos `GK-DEMO-SEM-VALOR-...` e uma conta técnica inativa, que não permite
login. Repetir a carga não reativa chaves reservadas, vendidas ou invalidadas,
nem duplica códigos. Não usar essa carga como estoque comercial.

O [DER v1.1](../banco/DER-GameKeys-v1.1.dbml) registra a estrutura implementada;
o v1.0 permanece preservado. Nenhuma migração ou escrita no Neon foi feita
durante o desenvolvimento desta entrega.

## Validação

O [roteiro local](../../release-2/sprint-2/testes/GK-124-reserva.md) relaciona as evidências automatizadas.
Os testes não substituem a validação independente da GK-125, da GK-127 ou do QA.
A GK-72 ainda deve ser verificada no fluxo final de compra ao integrar GK-14/GK-16.

Referências técnicas: [bloqueios e SKIP LOCKED no PostgreSQL 18](https://www.postgresql.org/docs/18/sql-select.html)
e [transações do psycopg](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).
