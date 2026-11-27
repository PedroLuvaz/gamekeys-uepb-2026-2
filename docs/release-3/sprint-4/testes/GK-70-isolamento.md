# GK-70 — Protocolo e evidências de isolamento de dados

Modelo inicial da Release 3 / Sprint 4, preparado em 27/11/2026. Responsável: Wagner. Validação independente: Pedro (QA). Fonte: [GK-70](https://pedrolucas0721.atlassian.net/browse/GK-70), driver DA-SEG-I2-01.

## Objetivo e escopo

Comprovar que cada cliente acessa apenas seus pedidos e chaves. A proteção é implementada na GK-49, nas rotas da biblioteca GK-17 e do histórico GK-23; este documento registra o experimento e a evidência do driver.

## Cenários e medida

Preparar dois clientes com pedidos pagos e testar acesso próprio, tentativas cruzadas por identificador e exploração da interface/API. Completar a matriz e os passos antes da execução.

Meta do card: 100% das tentativas indevidas recusadas com resposta 404 e nenhum dado de outro cliente exibido. Registrar o total de tentativas e de recusas, além das evidências. Não substituir a execução por uma declaração de atendimento.

## Ambiente e reprodução

| Campo | Registro |
| --- | --- |
| Data e executor | A preencher |
| Commit, versão e ambiente | A preencher |
| Preparação dos dados de teste | A preencher |
| Passos e comandos para repetir | A preencher |

## Resultado e evidências

A medir. Registrar resultado obtido, cálculo do indicador, links dos relatórios, limitações e falhas encontradas. Nenhuma execução é declarada neste modelo.

| Caso / sessão | Resultado esperado | Resultado obtido | Evidência |
| --- | --- | --- | --- |
| A preencher | A preencher | A medir | A preencher |

## Parecer e revisão

- Executor: a preencher.
- Revisão independente: a registrar pelo integrante indicado no card.
- Aceite do PO Rodrigo: a registrar após a verificação.
- PR, execução do CI e evidências: a preencher.
