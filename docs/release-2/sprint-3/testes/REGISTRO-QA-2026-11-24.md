# REGISTRO QA — Release 2 / Sprint 3 — 24/11/2026

Responsável: Rodrigo Almeida Gomes (QA). Escopo desta execução: GK-136, GK-14,
GK-73, GK-77 e preparação da Q-05 para a Review de 26/11/2026. Este registro
separa testes executados nesta auditoria, evidências anteriores consultadas e
aceites ainda pendentes.

Conferência para publicação em GK-144, ainda em 24/11: esta é uma fotografia
dos testes executados em `bcd143c`. A `main` avançou para `acdb062e` após os
PRs #68–#70; o [CI 45440918782](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/45440918782)
e a [Homologação 45441545482](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/45441545482)
dessa versão passaram, mas os testes locais abaixo não foram repetidos nela.
No Jira, GK-14, GK-73 e GK-136 passaram a
`Concluído`; GK-77 permanece `Em revisão`. O status não substitui o registro
expresso do aceite do PO. Os resultados finais da Sprint 3 dependem da Review
de 26/11 e não são antecipados neste documento.

## Git e isolamento

- Repositório: `PedroLuvaz/gamekeys-uepb-2026-2`; branch local `main` durante
  os testes descritos abaixo.
- `HEAD`, `origin/main` local e `main` consultada no GitHub:
  `bcd143cda532d2e1449b5f0273f3f1e9aeeb8f68` (PR #67). `git status`
  estava limpo antes desta execução; não foi necessário atualizar a branch.
- Nenhum código de produção, commit, push ou merge foi feito durante a
  auditoria. Este relatório é a única alteração versionável resultante daquela
  execução; relatórios e capturas gerados ficam sob caminhos ignorados pelo Git.
- Testes com escrita usaram somente um contêiner novo `postgres:18-alpine`,
  banco `gamekeys_teste`, publicado em `127.0.0.1:55439`, com volume anônimo e
  remoção automática. Antes dos testes, foram verificados programaticamente
  nome do contêiner, estado `healthy`, bind de loopback, porta, nome do banco,
  URL de teste e uma conexão de leitura. As variáveis de conexão foram
  substituídas no processo, com `PYTHON_DOTENV_DISABLED=1`; nenhum valor de
  credencial é reproduzido aqui. O contêiner foi encerrado e removido ao fim.

## GK-136 — Homologação técnica

O [CI 45417624163](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/45417624163)
e a [Homologação 45418172612](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/45418172612)
terminaram com sucesso para o mesmo SHA testado (`bcd143c`). O job `publicar`
e sua etapa de conferência, preparo e promoção passaram. O artefato de Homologação
[14933551011](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/45418172612/artifacts/14933551011)
está disponível; seus metadados foram conferidos nesta auditoria,
mas o ZIP não foi aberto. O comentário atualizado da
[GK-136](https://pedrolucas0721.atlassian.net/browse/GK-136) registra sua
conferência pela equipe.

Seis GETs públicos, sem autenticação nem escrita, foram executados nesta
auditoria. Resultado esperado: HTTP 200, saúde `ok`, banco `gamekeys` e o mesmo
SHA completo na API, no site e no proxy.

| Destino                   | HTTP | Resultado observado                        |
| ------------------------- | ---: | ------------------------------------------ |
| API `/saude`              |  200 | `status=ok`                                |
| API `/saude/banco`        |  200 | `status=ok`, `banco=gamekeys`              |
| API `/saude/versao`       |  200 | `bcd143cda532d2e1449b5f0273f3f1e9aeeb8f68` |
| Site `/versao.json`       |  200 | mesmo SHA                                  |
| Proxy `/api/saude/versao` |  200 | mesmo SHA                                  |
| Proxy `/api/saude/banco`  |  200 | `status=ok`, `banco=gamekeys`              |

No navegador, catálogo, detalhe de jogo, página vazia, login e cadastro
renderizaram conteúdo e não produziram erros de console observáveis. O
catálogo mostrou 23 jogos; a página `?pagina=999` mostrou mensagem de lista
vazia e retorno ao catálogo. Não houve login nem compra na homologação.

A evidência versionada
[`GK-136-publicacao-2026-11-24.json`](../evidencias/GK-136-publicacao-2026-11-24.json)
é a fotografia da publicação anterior (`7572ce5`); não representa a execução
posterior `45418172612`. O comentário mais recente do Jira e os GETs atuais
apontam para `bcd143c`, sem divergência observada. A evidência nova e
sanitizada está em `backend/relatorios/qa-r2-s3/GK-136-get-publico.json`.

**Conclusão GK-136:** validação técnica da publicação aprovada nesta
auditoria. Validação funcional do fluxo autenticado e rollback real não foram
executados; o aceite explícito de Wagner (PO) não foi identificado nos
registros consultados. A história está `Concluído` na consulta de publicação.

## GK-14 — Finalização da compra

Referência: [roteiro GK-14](GK-14-checkout.md) e
[Jira GK-14](https://pedrolucas0721.atlassian.net/browse/GK-14), em
`Em revisão` durante os testes e `Concluído` na consulta de publicação. O
build de produção local (`pnpm build`) passou. No preview
local, seis specs Cypress com API simulada passaram: **65/65 cenários**,
incluindo os **18/18 de `checkout.feature`** e os estados usados pela GK-77.

Na integração real, `checkout-real.cy.ts` passou **3/3** contra Vite, API e
PostgreSQL local isolado:

| Critério ou risco           | Esperado                                                                             | Obtido                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Carrinho com item           | Um pedido `aguardando_pagamento`, preço gravado, uma chave reservada e código oculto | Passou; pedido e tela exibiram R$ 19,90 antes do pagamento, sem código                             |
| Preço posterior do catálogo | Pedido e pagamento conservam preço da compra                                         | Passou; alteração fictícia do catálogo no banco de teste não mudou os R$ 19,90 do pedido/pagamento |
| Carrinho vazio              | Recusa, sem criar pedido                                                             | Passou; API retornou 409; payload adulterado 422 e ausência de autenticação 401                    |
| Confirmação perdida         | Repetir a mesma operação sem duplicar pedido/chave                                   | Passou; após recarga e recuperação houve um pedido e uma chave reservada                           |
| Entrega                     | Código só depois do pagamento simulado                                               | Passou; uma chave ficou visível somente após pagar                                                 |
| Acesso de outro cliente     | Pedido alheio não fica acessível                                                     | Passou; consulta e pagamento alheios retornaram 404                                                |

O Cypress mockado também cobriu clique duplo, timeout/5xx, botão de
recuperação, sessão expirada e layout de 320 px. O teste real gerou a captura
`backend/relatorios/qa-r2-s3/GK-14-compra-real-concluida.png`. Uma consulta
final no banco descartável encontrou **zero** usuários remanescentes dos
prefixos fictícios GK-11/GK-14.

**Ocorrências de ambiente, preservadas como evidência:** a primeira execução
real falhou 3/3 antes do checkout porque o segredo JWT fictício fornecido à
API local tinha menos de 32 bytes; o login respondeu 503. A configuração
temporária foi corrigida e a repetição passou 3/3. Depois, duas repetições
de `checkout.feature` passaram 17/18: no cenário mobile, as asserções de
largura e não sobreposição foram satisfeitas, mas `cy.screenshot()` excedeu
30 segundos. A primeira execução de 65/65 havia aprovado esse cenário. Uma
tentativa adicional com Chrome encerrou antes de executar cenários, com erro
do runner `* is not a valid URL`. A captura da falha do Electron está em
`backend/relatorios/qa-r2-s3/GK-14-mobile-falha.png`; ela não substitui uma
captura aprovada do cenário. Essas ocorrências não demonstram defeito no
checkout, mas limitam a estabilidade da evidência mobile nesta máquina.

**Conclusão GK-14:** critérios e riscos citados passaram nos testes
automatizados locais, inclusive 3 integrações com banco real isolado. Falta
registrar a validação funcional formal em ambiente autorizado e o aceite de
Wagner; o status atual é `Concluído`, sem aceite expresso localizado.

## GK-73 — Preço congelado no pedido

Referência: [roteiro GK-73](GK-73-preco-congelado.md) e
[Jira GK-73](https://pedrolucas0721.atlassian.net/browse/GK-73), `Em revisão`
durante os testes e `Concluído` na consulta de publicação.
O teste parametrizado de `test_pagamentos_banco.py` executou API, JWT,
serviços e PostgreSQL reais. Somente a mudança administrativa de preço foi
simulada com SQL no banco descartável; a R2 não tem tela administrativa de
preços. **4/4 cenários passaram**; o JUnit local está em
`backend/relatorios/qa-r2-s3-gk73.xml`.

| Pedido antigo | Mudança do catálogo | Esperado para o antigo | Encontrado no teste | Compra nova esperada/encontrada |
| ------------- | ------------------- | ---------------------: | ------------------: | ------------------------------: |
| Pendente      | Aumento             |              R$ 121,75 |           R$ 121,75 |                        R$ 81,00 |
| Pago          | Aumento             |              R$ 121,75 |           R$ 121,75 |                        R$ 81,00 |
| Pendente      | Redução             |              R$ 121,75 |           R$ 121,75 |                        R$ 45,15 |
| Pago          | Redução             |              R$ 121,75 |           R$ 121,75 |                        R$ 45,15 |

O pedido antigo conserva preços unitários, subtotais e total; o pagamento
posterior também usa R$ 121,75. As quatro compras novas usam e pagam os
valores atualizados. O percentual 4/4 mede apenas este experimento.

**Conclusão GK-73:** medida automatizada aprovada no ambiente isolado. Não
houve teste manual de administração nem aceite explícito do PO identificado;
o status atual é `Concluído`.

## GK-77 — Estados das telas

Referência: [registro GK-77](GK-77-registro-qa.md) e
[Jira GK-77](https://pedrolucas0721.atlassian.net/browse/GK-77), `Em revisão`.
As cinco specs de estados no preview local passaram **47/47** (subconjunto
dos 65 cenários acima). Usaram `cy.intercept` para atraso, falha de rede/HTTP
e recuperação, cobrindo indicador em até 1.000 ms, vazio/ausente, opção
“Tentar novamente” e ausência de tela completamente em branco. A medição
real anterior de Pedro no catálogo publicado está documentada no Jira;
esta auditoria não refez uma medição temporal independente na rede pública.

Nesta auditoria, a navegação pública confirmou carregamento e conteúdo no
catálogo e no detalhe, além da mensagem adequada para a página vazia, sem
erro de console observado. Não foi desligada a API de homologação. O estado
de indisponibilidade real da API continua **não executado no ambiente
publicado** e não deve ser confundido com a simulação Cypress.

**Conclusão GK-77:** regressão simulada local aprovada; parte observável das
páginas públicas sem tela em branco. Falta decidir com Wagner se exige
ensaio real de indisponibilidade em ambiente isolado e obter seu aceite.

## Q-05 — roteiro para cinco participantes reais

O [XLSX antigo de usabilidade](https://drive.google.com/file/d/178amBRRsfMGTgtJUXilBpZetpAb-lGB8/view)
cobre apenas catálogo e carrinho, sem checkout, pagamento ou reserva; é um
estudo complementar. A aba
[Protocolo da planilha Q-05 da Sprint 3](https://docs.google.com/spreadsheets/d/1Dyd0CsbbBjptbA_l8vQDX28BNNL9vCR0KZZ_4YN7PGw/edit#gid=533534898)
já prevê a **compra completa**, do catálogo à entrega simulada da chave.
Falta confirmar com Wagner (PO) a aplicação do protocolo atual em ambiente
de teste com contas, pagamento simulado e chaves fictícias. Nenhuma sessão
foi realizada nesta auditoria.

Roteiro do protocolo atual: convidar cinco voluntários diferentes,
identificados apenas como P01–P05, cada um em sessão própria com dados
fictícios controlados. Ler a instrução padrão: “Conclua a compra de teste
usando apenas o que vê na tela. Não darei instruções durante a tarefa.”
Tarefas: (1) encontrar um jogo, (2) adicionar ao carrinho, (3) finalizar o
pedido e (4) confirmar o pagamento simulado e visualizar a chave. Iniciar o
cronômetro antes da tarefa 1; parar ao concluir a tarefa 4 ou atingir 300 s.
Sucesso individual exige as quatro tarefas, sem ajuda, em até 300 s. Meta do
estudo: **ao menos 4/5 participantes**. Se a entrega não estiver funcional,
registrar a sessão como não executada. Não registrar nome, e-mail, senha ou
outros dados pessoais nas evidências.

| ID  | Data/ambiente | Quatro tarefas? | Sem ajuda? | Tempo (s) | Dificuldades/erros | Evidência anônima | Resultado     |
| --- | ------------- | --------------- | ---------- | --------: | ------------------ | ----------------- | ------------- |
| P01 | —             | —               | —          |         — | —                  | —                 | Não executado |
| P02 | —             | —               | —          |         — | —                  | —                 | Não executado |
| P03 | —             | —               | —          |         — | —                  | —                 | Não executado |
| P04 | —             | —               | —          |         — | —                  | —                 | Não executado |
| P05 | —             | —               | —          |         — | —                  | —                 | Não executado |

**Conclusão Q-05:** 0/5 sessões reais executadas; nenhuma taxa de sucesso
pode ser declarada. O XLSX antigo não substitui o protocolo atual de compra
completa. A confirmação do PO para aplicá-lo continua pendente.

## Comandos, relatórios e próximos passos

Comandos de teste executados (sempre com variáveis de conexão apontando ao
alvo local validado quando o teste usava banco):

```text
git status --short --branch; git rev-parse HEAD origin/main
docker run --rm -d --name gamekeys-qa-20261124 -p 127.0.0.1:55439:5432 ... postgres:18-alpine
docker inspect gamekeys-qa-20261124; docker exec gamekeys-qa-20261124 psql ...
pnpm build
node --test scripts/versao.test.mjs
python -m pytest tests/test_homologacao.py -q --junitxml=relatorios/qa-r2-s3-gk136.xml
python -m pytest tests/test_pagamentos_banco.py::test_valor_pago_e_o_gravado_no_pedido_mesmo_com_preco_novo_no_catalogo -v --junitxml=relatorios/qa-r2-s3-gk73.xml
pnpm preview
pnpm exec cypress run --spec cypress/e2e/checkout.feature,cypress/e2e/listagem-jogos.feature,cypress/e2e/detalhe-jogo.feature,cypress/e2e/alterar-remover-carrinho.feature,cypress/e2e/pagamento-pedido.feature,cypress/e2e/telas-sem-branco.feature
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pnpm dev
pnpm test:integracao --spec cypress/integracao/checkout-real.cy.ts
pnpm exec cypress run --spec cypress/e2e/checkout.feature
pnpm exec cypress run --env tags=@mobile --spec cypress/e2e/checkout.feature
pnpm exec cypress run --browser chrome --spec cypress/e2e/checkout.feature
docker stop gamekeys-qa-20261124
```

Resultados adicionais: `test_homologacao.py` passou **42/42** no banco local;
antes, a execução sem `TEST_DATABASE_URL` teve 39 aprovados e três pulados.
`node --test` passou **1/1**. O build, os três jobs do CI e a Homologação
de `bcd143c` passaram. Não foram executados rollback real, nova
publicação, compras na homologação compartilhada ou teste com cinco pessoas.

Evidências locais de execução (ignoradas pelo Git e não anexadas ao PR):

- `backend/relatorios/qa-r2-s3/GK-136-get-publico.json` — seis GETs e SHA.
- `backend/relatorios/qa-r2-s3-gk136.xml` e
  `backend/relatorios/qa-r2-s3-gk73.xml` — testes Python.
- `backend/relatorios/qa-r2-s3/GK-14-GK-77-mock-*.xml` (seis arquivos) e
  `GK-14-GK-77-cucumber.json` — 65 cenários simulados, zero falhas.
- `backend/relatorios/qa-r2-s3/GK-14-integracao-real.xml` e
  `GK-14-compra-real-concluida.png` — três integrações aprovadas; a captura
  exibe uma chave fictícia gerada para o teste local.
- `backend/relatorios/qa-r2-s3/GK-14-integracao-primeira-tentativa.xml`,
  `GK-14-checkout-repeticao-falha.xml`,
  `GK-14-checkout-repeticao2-falha.xml` e `GK-14-mobile-falha.png` —
  ocorrências locais descritas acima, sem valores de credenciais.

Para a Review, Rodrigo registra estes resultados e os limites das
simulações no Jira, Plano de Qualidade, Riscos e DoD. Wagner decide os
aceites de GK-14, GK-73, GK-77 e GK-136 e o escopo da Q-05. Pedro mantém a
evidência da publicação `45418172612` acessível e coordena, se aprovado,
as cinco sessões com participantes reais e ambiente de teste adequado.
