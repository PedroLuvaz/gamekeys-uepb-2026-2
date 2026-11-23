# GK-73 — Driver DA-CON-I2-02: preço congelado no pedido

Complementação executada por Wagner Tiburcio da Silva Junior (PO e DevOps) em
23/11/2026, na branch `test/GK-73-preco-congelado`, a partir da `main`
`73f3af57239dba6301334d4b714ec924b6ae2ada`.

## Objetivo e entrega anterior

O driver exige que 100% dos pedidos existentes mantenham seus valores quando o
administrador altera o catálogo, tanto pendentes quanto pagos. Somente compras
novas devem usar o preço atualizado.

A implementação e a primeira prova já foram integradas pela GK-47 no
[PR #50](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/pull/50), com
[CI aprovado](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/43903764140).
A [evidência anterior](GK-47-preco-congelado.md) permanece como registro histórico.
Esta entrega amplia o mesmo teste, sem duplicar a implementação nem introduzir
outro fluxo de reserva ou pagamento.

## Auditoria da implementação

| Etapa | Garantia existente |
| --- | --- |
| Reserva | `backend/app/servicos/reservas.py` bloqueia os jogos por ID, lê o preço corrente com `FOR NO KEY UPDATE` e grava o total e o preço unitário na mesma transação. |
| Persistência | `vendas.pedidos.valor_total` e `vendas.itens_pedido.preco_unitario` guardam os valores da compra, separados de `catalogo.jogos.preco`. |
| Consulta | `backend/app/servicos/pagamentos.py` lê o total do pedido e agrupa os itens pelo preço persistido. O preço atual do catálogo não entra no cálculo. |
| Pagamento | O serviço usa o total gravado no pedido e o copia para `vendas.pagamentos.valor`; não recalcula o preço a partir do catálogo. |

Não foi necessária mudança no código de produção, no esquema ou nas dependências.
A complementação não adiciona consultas ao fluxo da aplicação nem altera seus
bloqueios, limites ou custos por compra.

## Cenários automatizados

Foi ampliado `test_valor_pago_e_o_gravado_no_pedido_mesmo_com_preco_novo_no_catalogo`,
em `backend/tests/test_pagamentos_banco.py`. Ele agora combina duas situações do
pedido antigo com duas alterações do catálogo:

| Pedido quando o catálogo muda | Alteração dos preços dos dois jogos | Total antigo preservado | Total da compra nova |
| --- | --- | --- | --- |
| Aguardando pagamento | R$ 50,00 → R$ 70,00; R$ 7,25 → R$ 11,00 | R$ 121,75 | R$ 81,00 |
| Já pago e entregue | mesmo aumento | R$ 121,75 | R$ 81,00 |
| Aguardando pagamento | R$ 50,00 → R$ 40,00; R$ 7,25 → R$ 5,15 | R$ 121,75 | R$ 45,15 |
| Já pago e entregue | mesma redução | R$ 121,75 | R$ 45,15 |

O pedido antigo tem duas unidades do primeiro jogo e três do segundo. O teste
confere os preços unitários, quantidades, subtotais, total, resposta da consulta
antes e depois da alteração e pagamento persistido de R$ 121,75. Cada cenário
também cria e paga outro pedido, com uma unidade de cada jogo, usando os dois
preços atualizados. A criação e o pagamento dessa compra não alteram o pedido
anterior.

A API, a autenticação JWT, os serviços e o PostgreSQL são reais. Apenas a edição
administrativa do catálogo é simulada por SQL parametrizado no banco de teste,
porque a tela e o endpoint de administração pertencem à GK-21 e não fazem parte
da Release 2. Não se usa simulação do preço ou da resposta dos pedidos.

## Ambiente e reprodução

Banco exclusivo desta validação: PostgreSQL local descartável `gamekeys_teste`,
escutando apenas em `127.0.0.1:55437`. As três variáveis de conexão foram
substituídas explicitamente, com `PYTHON_DOTENV_DISABLED=1`. Nenhum teste,
migração ou alteração de preço foi executado no Neon compartilhado.

Para repetir com o banco Docker já previsto no projeto:

1. Na raiz, execute `docker compose -f docker-compose.test.yml up -d --wait`.
2. Em PowerShell, entre em `backend` e configure o alvo local:

   ```powershell
   $env:PYTHON_DOTENV_DISABLED = '1'
   $env:TEST_DATABASE_URL = 'postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys_teste?sslmode=disable'
   $env:DATABASE_URL = $env:TEST_DATABASE_URL
   $env:DATABASE_URL_UNPOOLED = $env:TEST_DATABASE_URL
   ```

3. Execute o cenário e a regressão:

   ```powershell
   .venv/Scripts/python.exe -m pytest tests/test_pagamentos_banco.py::test_valor_pago_e_o_gravado_no_pedido_mesmo_com_preco_novo_no_catalogo -v --junitxml=relatorios/gk73/preco-congelado.xml
   .venv/Scripts/python.exe -m pytest -q --junitxml=relatorios/gk73/backend-completo.xml
   .venv/Scripts/python.exe -m ruff check .
   .venv/Scripts/python.exe -m ruff format --check .
   ```

O pytest recria os schemas desse banco local a cada execução; use uma instância
descartável. As fixtures removem os pedidos, pagamentos, chaves, jogos e contas
criados por cada cenário.

## Resultado e evidências

- Quatro cenários específicos aprovados em 1,48 s: **4/4 pedidos antigos (100%)**
  preservaram seus valores e **4/4 compras novas** usaram os preços atualizados.
- Relatório específico: `backend/relatorios/gk73/preco-congelado.xml` (gerado e
  ignorado pelo Git).
- A regressão completa é registrada em `backend/relatorios/gk73/backend-completo.xml`.
- Regressão completa local: **294 testes aprovados em 43,29 s**, sem falhas ou
  testes pulados. Ruff e conferência de formatação aprovados (64 arquivos).
  Permanece um aviso de depreciação já existente do `TestClient`, sem falha.
- O workflow `.github/workflows/ci.yml` já executa esse teste na regressão completa
  e publica o JUnit em `relatorios-de-teste`. O relatório individual do PR deve
  vincular o commit, as execuções e os artefatos daquele commit, conforme o modelo
  do repositório.

O percentual mede os pedidos deste experimento; não representa medição de pedidos
de produção. Testes automatizados e evidências não substituem a validação
independente do QA Rodrigo nem o aceite explícito do PO Wagner. A GK-73 permanece
em revisão até o cumprimento dessas etapas e a integração da complementação.
