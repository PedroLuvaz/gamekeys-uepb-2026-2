# GK-13 — Histórico de status do pedido

A migração `0006_historico_status_pedido.sql` cria a trilha com pedido, status
anterior, novo status, responsável e data/hora. A criação do pedido registra
`NULL → aguardando_pagamento`; mudanças posteriores registram o usuário autenticado
que executou a operação.

A migração não inventa autor ou horário para mudanças anteriores à `0006`. Antes da
homologação, a equipe deve decidir se o histórico será apenas prospectivo ou se os
pedidos existentes receberão um marco inicial identificado como migração.

O serviço aceita somente a transição já confirmada pelo fluxo atual:
`aguardando_pagamento → entregue`. A mudança do pedido e o registro do histórico
usam a mesma transação do pagamento e da entrega das chaves. Repetições devolvem o
pedido entregue sem criar outro pagamento ou evento de histórico.

Continuam pendentes de decisão da equipe: etapa intermediária `pago`, regras de
cancelamento e endpoint administrativo para consultar ou alterar status. A GK-13 não
antecipa essas regras.
