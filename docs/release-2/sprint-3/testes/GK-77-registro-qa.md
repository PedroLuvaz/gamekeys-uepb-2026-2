# REGISTRO QA — GK-77

- Data: 17/11/2026
- Branch: `test/GK-77-medicao-carregamento`
- Commit-base: `758a889` (`Merge pull request #52 from PedroLuvaz/test/GK-48-cobre-conta-e-tentar-novamente`)
- Escopo: driver de usabilidade da Release 2 / Sprint 3 e relação com a GK-48.

## Revisão no GitHub

- Commit: a registrar após o commit da branch.
- Pull Request para `main`: a registrar após a criação.
- Revisor do rodízio: Pedro Lucas Vaz Andrade (`PedroLuvaz`), a solicitar no PR.
- Jira: [GK-77 — Telas nunca ficam em branco](https://pedrolucas0721.atlassian.net/browse/GK-77).
- Plano: [Plano de Qualidade — Sprint 3](https://docs.google.com/spreadsheets/d/1hm9Pr2e0qJG6xL_IS4jypHbIdUdWqxD62SRvMdl-HWo/edit).
- CI: pendente da abertura do PR; não considerado aprovado neste ponto.

## Resultado

**Aprovado no escopo local com API simulada.** O produto já implementava os estados
necessários; nenhuma falha funcional foi reproduzida e nenhum componente de produção
foi alterado. A lacuna encontrada era de mensuração: os testes verificavam a presença
do carregamento durante uma resposta lenta, mas não falhavam explicitamente quando o
indicador levasse mais de 1 segundo para aparecer.

Essa lacuna foi fechada nos cenários existentes. O cronômetro começa em
`onBeforeLoad`, registra por `MutationObserver` a entrada do indicador no DOM e exige
tempo menor ou igual a 1.000 ms. Os cinco cenários quantitativos passaram.

## Relação GK-77 × GK-48

- A GK-48 fornece o comportamento-base: carregamento, vazio/não encontrado, erro
  recuperável e limite para exceção inesperada, evitando tela branca.
- A GK-77 é o driver mensurável desse comportamento: indicador em até 1 segundo e
  estados cobertos em todas as listagens aplicáveis.
- As listagens atualmente entregues são catálogo e carrinho: 2/2 possuem carregamento,
  vazio, indisponibilidade e recuperação cobertos. Detalhe, pedido e Minha conta também
  tiveram o tempo de carregamento medido como cobertura adicional.
- A lista de pedidos e a biblioteca de chaves ainda não existem na interface. O
  histórico de status da GK-13 está no back-end e ficou fora do escopo de alteração.

## Estados e cenários confirmados

| Tela                    | Carregamento / API lenta                      | Vazio ou ausente                                | API indisponível                     | Tentar novamente                    | Evidência Cypress                                              |
| ----------------------- | --------------------------------------------- | ----------------------------------------------- | ------------------------------------ | ----------------------------------- | -------------------------------------------------------------- |
| Catálogo                | atraso de 1.200 ms; indicador em até 1.000 ms | catálogo com zero jogos e página além da última | HTTP 503                             | recupera 20 cartões sem recarregar  | `listagem-jogos.feature`                                       |
| Detalhe                 | atraso de 1.200 ms; indicador em até 1.000 ms | jogo inexistente/inativo mostra não encontrado  | HTTP 503 e falha de rede             | recupera os seis dados              | `detalhe-jogo.feature`                                         |
| Carrinho                | atraso de 1.500 ms; indicador em até 1.000 ms | remoção do último item mostra vazio             | falha de rede                        | recupera itens sem recarregar       | `alterar-remover-carrinho.feature`, `telas-sem-branco.feature` |
| Pedido                  | atraso de 1.500 ms; indicador em até 1.000 ms | 404 mostra pedido não encontrado                | falha de rede                        | recupera pedido e total             | `pagamento-pedido.feature`                                     |
| Minha conta             | atraso de 1.500 ms; indicador em até 1.000 ms | não se aplica                                   | falha de rede                        | recupera os dados da conta          | `telas-sem-branco.feature`                                     |
| Exceção de renderização | não se aplica                                 | não se aplica                                   | falha forçada em `Intl.NumberFormat` | volta ao catálogo e restaura a rota | `telas-sem-branco.feature`                                     |

O total `R$ 0,00` no carrinho vazio não foi acrescentado nem removido: a decisão
continua reservada ao PO (QA-R2-007).

## Arquivos auditados sem alteração

- `frontend/src/App.tsx`
- `frontend/src/Carrinho.tsx`
- `frontend/src/Pedido.tsx`
- `frontend/src/LimiteDeErro.tsx`

## Arquivos alterados

- `frontend/cypress/support/medir-carregamento.ts` — instrumento compartilhado da
  medida de até 1 segundo.
- `frontend/cypress/support/step_definitions/catalogo.ts`
- `frontend/cypress/support/step_definitions/detalhe-jogo.ts`
- `frontend/cypress/support/step_definitions/carrinho-gk12.ts`
- `frontend/cypress/support/step_definitions/pagamento-pedido.ts`
- `frontend/cypress/support/step_definitions/telas-sem-branco.ts`
- `frontend/cypress/e2e/listagem-jogos.feature`
- `frontend/cypress/e2e/detalhe-jogo.feature`
- `frontend/cypress/e2e/alterar-remover-carrinho.feature`
- `frontend/cypress/e2e/pagamento-pedido.feature`
- `frontend/cypress/e2e/telas-sem-branco.feature`
- `docs/release-2/sprint-3/testes/GK-48-estados-de-tela.md`
- `docs/release-2/sprint-3/testes/GK-77-registro-qa.md`

## Comandos exatos e resultados

Executados a partir da raiz do repositório, exceto onde indicado:

| Comando                                                                                                                                                                                                                                                                                                                                                                                                                                        | Resultado                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `git fetch origin main`                                                                                                                                                                                                                                                                                                                                                                                                                        | passou; referência remota atualizada                                                       |
| `git merge --ff-only origin/main`                                                                                                                                                                                                                                                                                                                                                                                                              | passou; `Already up to date`                                                               |
| `pnpm build` (em `frontend`)                                                                                                                                                                                                                                                                                                                                                                                                                   | passou no baseline e após a instrumentação; TypeScript da aplicação e Cypress + build Vite |
| `pnpm exec cypress verify` (em `frontend`)                                                                                                                                                                                                                                                                                                                                                                                                     | não executou testes: binário 16.2.0 ausente                                                |
| `pnpm exec cypress install` (em `frontend`)                                                                                                                                                                                                                                                                                                                                                                                                    | passou; Cypress 16.2.0 instalado e verificado                                              |
| `pnpm test:e2e` (em `frontend`, primeira tentativa)                                                                                                                                                                                                                                                                                                                                                                                            | não executou cenários: o Cypress externo não alcançou o preview iniciado no sandbox        |
| `pnpm test:e2e` (em `frontend`, preview no mesmo contexto)                                                                                                                                                                                                                                                                                                                                                                                     | baseline passou: 117/117 em 10 specs, 1 min 22 s                                           |
| `pnpm exec cypress run --spec "cypress/e2e/listagem-jogos.feature,cypress/e2e/detalhe-jogo.feature,cypress/e2e/alterar-remover-carrinho.feature,cypress/e2e/pagamento-pedido.feature,cypress/e2e/telas-sem-branco.feature"`                                                                                                                                                                                                                    | passou após a mudança: 47/47 em 5 specs, 33 s                                              |
| `pnpm exec prettier --check cypress/support/medir-carregamento.ts cypress/support/step_definitions/catalogo.ts cypress/support/step_definitions/detalhe-jogo.ts cypress/support/step_definitions/carrinho-gk12.ts cypress/support/step_definitions/pagamento-pedido.ts cypress/support/step_definitions/telas-sem-branco.ts ../docs/release-2/sprint-3/testes/GK-48-estados-de-tela.md ../docs/release-2/sprint-3/testes/GK-77-registro-qa.md` | passou após a formatação                                                                   |
| `pnpm test:e2e` (em `frontend`, execução final)                                                                                                                                                                                                                                                                                                                                                                                                | passou: 117/117 em 10 specs, 1 min 24 s                                                    |
| `pnpm build` e o mesmo `prettier --check` (revisão pré-commit de 17/11)                                                                                                                                                                                                                                                                                                                                                                        | passaram                                                                                   |
| comando direcionado de cinco specs acima (revisão pré-commit de 17/11)                                                                                                                                                                                                                                                                                                                                                                         | passou: 47/47 em 5 specs, 1 min 02 s                                                       |
| `pnpm test:e2e` (revisão pré-commit de 17/11)                                                                                                                                                                                                                                                                                                                                                                                                  | passou: 117/117 em 10 specs, 2 min 51 s                                                    |

## Falhas e correções

- Nenhuma falha funcional foi reproduzida no produto.
- A primeira compilação da instrumentação falhou por extensões ESM ausentes
  nos imports e pela tipagem de `MutationObserver`. A falha de teste foi corrigida e o
  `pnpm build` posterior passou.
- A primeira tentativa da regressão Cypress foi uma falha de isolamento do ambiente,
  antes da coleta de qualquer cenário. Ela não foi contada como reprovação nem como
  aprovação funcional.

## Evidências

- JUnit local: `frontend/cypress/reports/catalogo-*.xml`.
- Relatório Cucumber consolidado: `frontend/cypress/reports/cucumber.json`.
- Cenários quantitativos marcados com `@GK-77` nos quatro fluxos especializados; a
  feature `telas-sem-branco.feature` já possui `@GK-77` no nível da funcionalidade.
- Resultado final: 10 specs, 117 testes, 117 passando, 0 falhando, 0 pendente,
  0 ignorado, em 1 min 24 s.
- Resultado direcionado: 5 specs, 47 testes, 47 passando, 0 falhando, 0 pendente,
  0 ignorado.

## Limitações e riscos restantes

- A lentidão, o HTTP 503 e a queda de rede foram simulados por `cy.intercept`; não
  houve desligamento de uma API real nem limitação real de banda nesta execução.
- `pnpm test:integracao` não foi executado: requer API local ativa e PostgreSQL
  descartável identificado como `gamekeys_teste`. Portanto, integração real não está
  aprovada por este registro.
- Homologação publicada, CI do futuro commit/PR e aceite do PO não foram executados.
- O Electron 146 usado pelo Cypress está marcado como obsoleto pela ferramenta; uma
  atualização futura deve selecionar Chrome ou outro navegador suportado.
- Novas listagens (histórico de pedidos e biblioteca) devem entrar na matriz da GK-77
  quando forem implementadas na interface.

## Próximos passos

1. Rodar a regressão completa no CI no commit/PR que levar esta evidência.
2. Em homologação, repetir catálogo, carrinho e pedido com rede lenta e API realmente
   indisponível; registrar tempos e capturas nas planilhas de Testes, Execuções e
   Métricas.
3. Vincular este registro e os relatórios JUnit/Cucumber à GK-77, Riscos e DoD da
   Sprint 3.
4. Manter QA-R2-007 aguardando a decisão do PO; não alterar o total do carrinho vazio
   antes dela.

O commit, o push e o PR serão registrados acima durante a preparação para revisão.
Nenhum merge automático será realizado.
