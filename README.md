# GameKeys

Loja web de jogos digitais vendidos por chave de ativação.
Disciplina Gerência de Projeto — UEPB, 2026.2 — Prof.ª Ana Isabella Muniz Leite.

## Problema

Quem vende chaves de ativação precisa garantir que a mesma chave nunca seja entregue a dois compradores.
O GameKeys controla o estoque de chaves, os pedidos e a entrega, mantendo separados os dados de cada usuário.

## Perfis

- **Visitante:** navega e busca no catálogo.
- **Cliente:** compra (pagamento simulado) e acessa suas chaves.
- **Administrador:** cadastra jogos e chaves e acompanha os pedidos.

## Equipe

| Integrante | Papel na Release 1 (até 29/10) | Papel na Release 2 (03/11 a 26/11) |
|---|---|---|
| Pedro Lucas Vaz de Andrade | Product Owner e DevOps | Scrum Master |
| Wagner Tiburcio da Silva Junior | QA | Product Owner e DevOps |
| Rodrigo Almeida Gomes | Scrum Master | QA |

Os papéis mudam ao fim de cada release. Quem é PO também é DevOps.

Passagem de bastão para a Release 2:

- **PO e DevOps (Pedro → Wagner):** backlog da Release 2 priorizado no épico GK-3, com as histórias GK-11 a GK-16 prontas pela DoR; Release Notes R1; pipeline de CI, PostgreSQL local isolado para testes e o README como guia do ambiente.
- **Scrum Master (Rodrigo → Pedro):** board 34 do Jira, calendário de cerimônias, atas da Sprint 1, planilha de riscos e DoD; a exigência de 1 aprovação antes do merge (Q-11) está ativa na `main` desde 03/11.
- **QA (Wagner → Rodrigo):** Plano de Teste com os 30 casos da Release 1, Plano de Qualidade com o Resultado R1 e Relatório de Qualidade R1; próximos casos: carrinho, reserva de chaves e teste de concorrência (Q-03).

## Responsabilidades

- **PO:** responsável pelo produto. Cadastra e prioriza o backlog, define o objetivo de cada sprint, aceita ou recusa as entregas e apresenta o produto.
- **Scrum Master:** cuida do processo. Organiza as cerimônias, mantém o Jira em dia, registra atas e riscos e garante que os documentos estejam acessíveis.
- **QA:** cuida da qualidade. Planeja e executa os testes, registra bugs e confere se cada história atende aos critérios de aceite e à Definition of Done.
- **DevOps:** cuida do repositório, do pipeline de CI e do ambiente de desenvolvimento.

## Releases

| Release | Até | O que será entregue |
|---|---|---|
| 1 | 29/10 | Cadastro, login e catálogo navegável |
| 2 | 26/11 | Compra completa: carrinho, pagamento simulado e entrega da chave |
| 3 | 22/12 | Biblioteca, cancelamento, busca e administração de jogos e chaves |
| 4 | 18/02 | Painel de pedidos, indicadores, avaliações e apresentação final |

## Gestão

O backlog, as sprints e as releases ficam no Jira.

## Documentos

Pasta no Google Drive: https://drive.google.com/drive/folders/1m_lYvzaFOp2JcKruRJZfTtRMfyEVXKPt

- [Proposta](https://docs.google.com/document/d/1cvCfppfFUyMrlR5vKW8kzUz7ld3SvadsuaLUz4l3nRc/edit)
- [Plano da Sprint 1](https://docs.google.com/document/d/1e_3jWniPo1ayAMduJLj30WU7ZRu9x5FYl6XWfpK0WSM/edit)
- [Registro de Riscos](https://docs.google.com/document/d/1oSEonzAulY87ssaz6TzGdNFTCswyxCbSTtn1_LtVj8g/edit)
- [Drivers Arquiteturais](https://docs.google.com/document/d/10U9jLK5_RB2MYaO2PXomXmlro3rJidd3Zxs0wIVX7TE/edit)
- DER do banco de dados (v1.0, 21/10/2026): fonte editável em `docs/banco/DER-GameKeys-v1.0.dbml` (abre no [dbdiagram.io](https://dbdiagram.io)); a imagem vigente fica anexada na GK-103

Uma cópia em .docx de cada um fica na pasta `docs/`.

Documentos nos templates da disciplina (no Drive, em `docs/` e anexados no Jira):

- [DoD de Sprint e Release](https://drive.google.com/file/d/1Mr-6oT0po8POyaRGD75hCEQjqA-TzI4Q/view): Definition of Done de sprint e de release (anexo da GK-38)
- [Análise de Riscos Baseada em Defeitos](https://drive.google.com/file/d/1-V-hE9YR3ZEPaU3jr15yCcHHMzlV64ej/view): 9 riscos, 3 atributos de qualidade × 3 integrantes (anexo do épico GK-64)
- [Plano de Qualidade (planilha)](https://drive.google.com/file/d/1oFIoArPRYugK9tnwQFsLC75rlv7r4TiK/view): itens de qualidade com métrica, meta, forma de medição e responsável (anexo da GK-36)
- [Plano de Teste](https://drive.google.com/file/d/1qXmh7E59SYTYdfxeKzZtY5n8A1jDZK6s/view): escopo, estratégia, casos de teste ligados às US e cronograma (anexo da GK-36)

A DoR e a DoD de cada história ficam no modelo de US, dentro de cada história no Jira.

### Release 1

Pasta no Google Drive: https://drive.google.com/drive/folders/1-i4Zd4ZaVWxmGvYyZZ6l0CUkpCabpcS_

| Papel | Documento | Repositório |
|---|---|---|
| PO | [Priorização do Backlog](https://docs.google.com/document/d/1-9X8xE_vmyZ47UAf6DgMhwGcjfvX8AQvYJW3GNoyOS4/edit) | `docs/Priorizacao-do-Backlog.docx` |
| PO | [Release Notes R1](https://docs.google.com/document/d/1fcYhN3Gz5_ouf-Y2WeDExkwL5hiK4jlDpD2BKmWn540/edit) | `docs/releases/Release-Notes-R1.docx` |
| SM | [Acordos de Trabalho](https://docs.google.com/document/d/1CO2iIvXooNwmv-CcWwO7DyfjftbdqBhwOOCTPrOlC5E/edit) | `docs/Acordos-de-Trabalho.docx` |
| SM | [Calendário de Cerimônias](https://docs.google.com/document/d/15UhShju2BnJhqKQdNeibDtrFzNYf21lOQsWoyZ11Fxk/edit) | `docs/Calendario-de-Cerimonias.docx` |
| SM | [Ata da Planning - Sprint 1](https://docs.google.com/document/d/1hwVokPlaJRHPcZ4we1T5Tba_V03W7w-JIe5R7KzRTzs/edit) | `docs/sprints/Ata-Planning-Sprint-1.docx` |
| SM | [Ata da Review - Sprint 1](https://docs.google.com/document/d/14WsdO6MioIEIuydI2a04Q3-Ks5UtHVC-GCf9q-Mp8tI/edit) | `docs/sprints/Ata-Review-Sprint-1.docx` |
| SM | [Ata da Retrospectiva - Sprint 1](https://docs.google.com/document/d/1ULUe4oHA-BC-EaJZ31KRAFLJCQisLzr0dLJJMXIGi0w/edit) | `docs/sprints/Ata-Retrospectiva-Sprint-1.docx` |
| DevOps | [Ambiente de Desenvolvimento](https://docs.google.com/document/d/1OaaMgqvrrhDVbRpNBJA_hqpPTlLmJIo1WBjJm8YpTtM/edit) | `docs/Ambiente-de-Desenvolvimento.docx` |
| QA | [Relatório de Qualidade R1](https://docs.google.com/document/d/1Q_8t9bU_Arh-kA1wIgAJGgsuEEVXl4R-o76b3t-cHr8/edit) | `docs/releases/Relatorio-de-Qualidade-R1.docx` |
| SM | [Relatório de Métricas R1](https://drive.google.com/file/d/14o1IOR7zsJshv1nD8OGk2PereJsrKMon/view) (velocity, burndown e impedimentos) | `docs/releases/Relatorio-de-Metricas-R1.docx` |
| DevOps | [Relatório do Pipeline R1](https://drive.google.com/file/d/182Bwdq4Eo_4UzFWKuPhSx3FgqF18Cww5/view) | `docs/releases/Relatorio-do-Pipeline-R1.docx` |

O que vale é a versão do Drive, onde a equipe preenche. A cópia em `docs/` é atualizada no fim da sprint.

### Release 2

Pasta no Google Drive: https://drive.google.com/drive/folders/1qQqakLyFIfm1JvByRFdmTL7EWpluAjH_

| Papel | Documento | Repositório |
|---|---|---|
| PO | [Plano da Release 2](https://docs.google.com/document/d/1TBzpeiyrZG81ur2l_uoBKzavjskJAV71tsItetSN9JM/edit) (objetivo, papéis, escopo por sprint, capacidade e riscos) | `docs/releases/Plano-da-Release-2.docx` |
| QA | [Plano de Qualidade e Testes da Release 2](https://docs.google.com/document/d/1IFobma41GfA1SwybH1yJDNPN8vf76YyoLbZQ1Cg2DC4/edit) (metas, matriz de testes, riscos e DoD) | `docs/qualidade/Plano-de-Qualidade-e-Testes-Release-2.md` |
| QA | [Acompanhamento QA R2](https://docs.google.com/spreadsheets/d/1ZJsomiV2_mLoEhCEVhpdOIKnlsPTkwyq43jIpFViLOQ/edit) (planilha de métricas, testes e riscos) | só no Drive |
| DevOps | [Relatório do Pipeline R2](https://docs.google.com/document/d/1ytrAHueI3WjsGOLkoqxo27KSbnhg9-GlQYWEpLBQHkk/edit) (versão preliminar: CI, proteção da main, homologação e deploy automático) | `docs/releases/Relatorio-do-Pipeline-R2.docx` |
| SM | [Ata da Planning - Sprint 2](https://docs.google.com/document/d/12tAuNdJ9sn_yyHmyuh9Re8GtH_yCdZkFoKyMBKi-_Os/edit) | `docs/sprints/Ata-Planning-Sprint-2.docx` |
| SM | [Acompanhamento e Resultados - Sprint 2](https://docs.google.com/document/d/1DIxA-qxKtHKApLr_6_mDT_uOIiEZB6XLZDsJqB_MHRM/edit) (burndown, impedimentos e ações da retrospectiva) | `docs/sprints/Acompanhamento-e-Resultados-Sprint-2.docx` |
| SM | [Ata da Review - Sprint 2](https://docs.google.com/document/d/1gyfrCYCxlZWo0QXTiQoJCjdM14S0L2QC86thOHos050/edit) (preparada; fecha em 11/11) | `docs/sprints/Ata-Review-Sprint-2.docx` |
| SM | [Ata da Retrospectiva - Sprint 2](https://docs.google.com/document/d/1ua2jBNA6pN14VCUleeQQtx-I4qR6f38pqwLZd4B6Enk/edit) (preparada; fecha em 11/11) | `docs/sprints/Ata-Retrospectiva-Sprint-2.docx` |
| SM | [Roteiro da Review - Sprint 2](https://docs.google.com/document/d/1zOg6w2A7CTPVeKA4-dJuWBJACM0FmHPrrR8MTqMzJgI/edit) (checklist da véspera, ordem da demonstração e plano B) | `docs/sprints/Roteiro-Review-Sprint-2.docx` |

As cópias do repositório foram sincronizadas com o Drive em 08/11/2026. Os demais documentos da Release 2 entram nesta tabela conforme forem criados.

## Tecnologias

Python 3.12 com FastAPI, PostgreSQL, React com TypeScript e GitHub Actions.

## Como rodar o back-end

1. Crie o `.env.local` na raiz a partir do `.env.example` (veja [Banco de dados](#banco-de-dados)).
2. Instale, prepare o banco, teste e suba a API:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # no Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
python -m app.migrar --carga
pytest
uvicorn app.main:app --reload
```

A API sobe em http://127.0.0.1:8000:

- `/saude`: a API está no ar
- `/saude/banco`: a API alcança o PostgreSQL (503 se não alcançar, sem expor a conexão)
- `POST /clientes`: cadastra uma conta Cliente com senha protegida por bcrypt
- `POST /auth/login`: valida as credenciais e cria um JWT com duração configurável
- `GET /auth/me`: devolve o cliente da sessão quando recebe um Bearer token válido
- `/docs`: documentação automática dos endpoints (desligada com `AMBIENTE=producao`)

O front-end em `http://localhost:5173` já pode chamar a API; outras origens entram em `CORS_ORIGENS`.

O código fica em `backend/app/`: `rotas/` (endpoints), `esquemas/` (validação com Pydantic), `servicos/` (regras de negócio), `db.py` (acesso ao banco) e `config.py` (variáveis de ambiente).

## Adicionar ao carrinho (GK-11 / GK-118)

`POST /carrinho/itens`, com Bearer token do login, recebe `jogo_id` e
`quantidade` (padrão 1). Adiciona ao carrinho do cliente autenticado ou soma ao
item existente, recusando estoque insuficiente e classificação acima da idade.
Retorna HTTP 200 com o item e sua quantidade final, preço unitário e subtotal
decimais. Adicionar ao carrinho não reserva chaves nem consome estoque.

Requer a migração `backend/migracoes/0003_carrinho.sql`, aplicada pelo responsável
pelo banco antes da publicação. A ficha do jogo permite escolher a quantidade,
adicionar e conferir o resultado confirmado pela API. Visitantes entram no login
e retornam à ficha, sem adição automática. A ação informa carregamento, sucesso,
estoque insuficiente e restrição etária; esgotados ficam desabilitados.
Consulte o [contrato e o guia de integração com a GK-12](docs/api/GK-11-carrinho.md)
para exemplos, erros, concorrência, testes e orientações para alterar/remover itens.
O [roteiro de aceite da GK-11](docs/testes/GK-11-aceite.md) cobre as subtarefas
GK-118, GK-119 e GK-120. A listagem/alteração/remoção do carrinho continua na GK-12.

## Tela do catálogo e detalhe de jogos

O front-end fica em `frontend/`, com React, TypeScript e Vite. Use Node.js 24 e pnpm
11.25 (a versão está fixada no `package.json`). A configuração do banco continua somente
no `.env.local` da raiz; não copie esse arquivo para o front-end.

Com a API já configurada, abra dois terminais:

```powershell
# Terminal 1: API (na pasta do repositório)
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2: interface (na pasta do repositório)
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Abra `http://127.0.0.1:5173`. A opção **Criar conta** abre o formulário de cadastro. O
catálogo consulta os dados reais pela API: 20 jogos por
página, preços em reais e indicação de disponibilidade. Os cartões abrem a ficha com
descrição, gênero, plataforma e classificação; voltar ao catálogo preserva a página de
origem. Os botões voltar/avançar do navegador e endereços diretos também funcionam.

Quando a capa estiver ausente ou falhar, a interface mostra uma arte ilustrativa local,
sem alterar o cadastro do jogo. Carregamento, catálogo vazio, página inexistente, jogo
inativo/inexistente e falha de conexão possuem mensagens e ações apropriadas. A tela se
adapta a celular e desktop. Compra e carrinho continuam fora desta entrega.

O Vite encaminha `/api` para `http://127.0.0.1:8000` durante o desenvolvimento. Para outro
ambiente, configure apenas o endereço público em `frontend/.env.local` seguindo
`frontend/.env.example` e providencie o encaminhamento da API. Nunca use credenciais de
banco em variáveis `VITE_*`.

### Testes de interface

Dentro de `frontend/`, com `pnpm dev` em execução:

```powershell
pnpm build            # confere TypeScript da aplicação/testes e gera dist/
pnpm test:e2e         # Cypress/Cucumber com API simulada
pnpm test:integracao  # tela + API + PostgreSQL locais, com dados fictícios isolados
pnpm test:abrir       # opcional: interface do Cypress
```

A suíte completa `test:integracao` exige API e `TEST_DATABASE_URL` apontando para
PostgreSQL **local isolado**, banco `gamekeys_teste`. Ela cria contas fictícias e
valida adições ao carrinho, além das consultas do catálogo. Um hook verifica o
banco da API antes dos cenários; as fixtures do carrinho recusam hosts remotos e
removem somente seus próprios dados. Nunca execute essa suíte contra o Neon.
O roteiro da GK-11 mostra como configurar a execução local. O proxy do Vite usa
`127.0.0.1:8000` por padrão; `GAMEKEYS_PROXY_API` permite apontar um servidor local
de testes em outra porta, sem expor variáveis do banco ao navegador.

Os 61 cenários em `cypress/e2e/` cobrem adição ao carrinho, estoque, classificação,
cadastro, login, sessão, paginação, esgotado,
navegação ao detalhe e retorno, lista vazia, falha e nova tentativa, carregamento, página
além da última, celular, jogo não encontrado, histórico do navegador, recarga e capa
indisponível. Usam respostas simuladas na rede: não
acessam nem recriam o banco do Neon. A base pode ser reaproveitada nos testes de cadastro
e login. Relatórios JUnit e Cucumber ficam em `frontend/cypress/reports/`; capturas de
falhas ficam em `frontend/cypress/screenshots/`. Esses arquivos são ignorados pelo Git.

Os 12 testes em `cypress/integracao/` usam a API em execução e o PostgreSQL local isolado sem simular
respostas. Os testes de cadastro e login criam contas fictícias com e-mail único para provar
persistência, autenticação e mensagens seguras. Os de carrinho conferem a gravação ou
recusa diretamente no banco; os de catálogo e detalhe consultam a carga de demonstração.
Execute esta suíte somente com o banco `gamekeys_teste` criado por
`docker-compose.test.yml`. No CI, ela usa o PostgreSQL efêmero do próprio job, com API e
interface iniciadas nele. A proteção da GK-106 recusa o Neon e qualquer outro host remoto.

### Cadastro de cliente (GK-7)

`POST /clientes` recebe `nome`, `email`, `data_nascimento` e `senha`. O e-mail é normalizado
para minúsculas e deve ser único; a senha precisa ter pelo menos oito caracteres e é persistida
somente como hash bcrypt. O perfil inicial é `cliente`. A resposta HTTP 201 contém apenas
`id`, `nome`, `email`, `data_nascimento` e `perfil` — nunca senha ou hash.

E-mail repetido recebe HTTP 409 com mensagem genérica em português. Dados inválidos recebem
HTTP 422 e indisponibilidade do banco recebe HTTP 503 sem detalhes internos. A tela
`/cadastro` trata validação, envio, sucesso, duplicidade e falha de comunicação. Os testes
unitários e de banco ficam em `backend/tests/test_clientes*.py`; os três cenários de aceite
ficam em `frontend/cypress/e2e/cadastro.feature` e a integração real em
`frontend/cypress/integracao/cadastro-real.cy.ts`.

### Login e sessão (GK-8)

`POST /auth/login` recebe `email` e `senha`, consulta o cliente persistido e compara o hash
bcrypt. E-mail inexistente e senha incorreta recebem a mesma resposta HTTP 401, evitando
confirmar se uma conta existe. Em caso de sucesso, a API emite um JWT HS256 com emissor e
expiração; a duração padrão é 60 minutos e pode ser alterada por
`JWT_DURACAO_MINUTOS`. Defina `JWT_SECRET` com um segredo forte fora do repositório.

A interface `/login` guarda o token apenas em `sessionStorage`, valida a sessão em
`GET /auth/me` antes de exibir `/conta`, remove o token no logout e também quando o prazo local
expira ou a API responde 401. Assim, a sessão não sobrevive ao fechamento da aba. Esta escolha
mantém o JWT no cliente e, portanto, exige a prevenção de XSS; a migração para cookie
`HttpOnly`, `Secure` e `SameSite` fica como endurecimento posterior, pois muda o contrato de
autenticação e precisa de validação da equipe. Catálogo e detalhe permanecem públicos.

Os testes unitários e de banco ficam em `backend/tests/test_autenticacao*.py`; os quatro
cenários de aceite ficam em `frontend/cypress/e2e/login.feature` e os dois testes com API e
PostgreSQL reais em `frontend/cypress/integracao/login-real.cy.ts`.

### Detalhe do jogo (GK-10)

A GK-87 reutiliza `GET /jogos/{id}` e a mesma regra de disponibilidade da listagem:
um jogo ativo sem chaves continua consultável como **Esgotado**. A GK-88 permite
abrir a ficha pelo catálogo ou pelo endereço direto, com os seis dados do aceite
(descrição, gênero, plataforma, classificação, preço e disponibilidade), recarga e
retorno à página de origem. Inativo e inexistente recebem a mesma mensagem de não
encontrado. Falha de comunicação permite tentar novamente.

A GK-89 tem nove cenários isolados em `cypress/e2e/detalhe-jogo.feature`, com tags
`@US-10`, `@GK-10`, `@R1`, `@smoke`, `@regressao` e `@excecao`. São executados
junto ao catálogo por `pnpm test:e2e`, usando os dados fictícios de
`cypress/fixtures/detalhe-jogo.json`. A integração real em
`cypress/integracao/detalhe-real.cy.ts` compara os seis campos com a API e verifica
um inativo cujo ID é consultado previamente no banco local. Ela exige
`GAMEKEYS_JOGO_INATIVO_ID` no terminal que executa `pnpm test:integracao`; o CI
prepara esse valor automaticamente, sem expor credenciais no navegador.

Consulte [o roteiro da US-10](docs/testes/US-10-detalhe-do-jogo.md) para executar
as verificações com PostgreSQL local e conferir a cobertura de cada subtask.

### Consulta pública do catálogo (GK-84)

`GET /jogos?pagina=1` retorna até 20 jogos ativos, em ordem de nome e, em caso de empate,
identificador. Não exige login. O parâmetro `pagina` começa em 1 e aceita inteiros até
2.147.483.647; valores fora desse intervalo ou não inteiros recebem HTTP 422.

```json
{
  "itens": [
    {
      "id": 1,
      "nome": "Lâmina do Sertão",
      "capa_url": null,
      "preco": "149.90",
      "disponibilidade": "Disponível"
    }
  ],
  "pagina": 1,
  "por_pagina": 20,
  "total": 23,
  "total_paginas": 2
}
```

O exemplo abrevia a lista de itens. O preço é uma string decimal para preservar centavos;
`capa_url` pode ser nula (a carga de demonstração ainda não inclui capas). Jogos com zero
chaves aparecem como `Esgotado`; inativos não aparecem nem entram no total. Uma página após a
última retorna `itens: []` mantendo os totais; sem jogos ativos, ambos os totais são zero.
Se o banco estiver indisponível, a API retorna HTTP 503 com uma mensagem em português.

Para conferir pelo navegador: `http://127.0.0.1:8000/jogos` e
`http://127.0.0.1:8000/jogos?pagina=2`. Os testes de integração em `test_catalogo_banco.py`
usam o banco de testes, como o restante da suíte. Localmente esse banco é o `gamekeys_teste`
isolado na porta 5433; o pytest recusa URLs do Neon antes de abrir a conexão e recria apenas
a estrutura desse contêiner local.

`GET /jogos/{id}` retorna os mesmos campos do cartão, mais `descricao`, `genero`,
`plataforma` e `classificacao`. Jogo inexistente ou inativo recebe HTTP 404 com a mesma
mensagem de não encontrado; falha de banco recebe HTTP 503 sem expor dados da conexão.

### Testes e CI

- Em `backend/`, com `TEST_DATABASE_URL` local (`gamekeys_teste`) e migrações aplicadas: `psql "$TEST_DATABASE_URL" -f qa/sql/chave_em_mais_de_um_pedido.sql` consulta duplicidades (GK-128); `python -m qa.gk129_reserva_concorrente --rodadas 100 --concorrentes 20` testa a reserva real e imprime o relatório JSON (GK-129).
- `pytest` roda tudo (é a regressão). `pytest -m smoke` roda só a verificação rápida: API no ar, banco alcançável e front-end liberado pelo CORS. Os testes de banco usam só `TEST_DATABASE_URL` (banco local `gamekeys_teste`) e são pulados quando ela não está definida. Por segurança, a suíte interrompe a execução antes da primeira conexão se o host não for `localhost`, `127.0.0.1` ou `::1`.
- A cada push e pull request, o GitHub Actions sobe um PostgreSQL próprio do job (serviço `postgres`), aplica migrações e carga, roda ruff, o smoke e depois a suíte completa, e confere que os dados continuam no banco depois de reiniciá-lo.
- O job de interface compila o front-end e executa os 27 cenários com API simulada. O job de back-end também executa os nove testes reais da tela integrada à API e ao PostgreSQL local. Relatórios e capturas de falhas são guardados como artefatos separados.
- O job `imagens Docker` gera as imagens da API e do front-end com `docker compose build`, para o `Dockerfile` não quebrar sem ninguém ver.
- Os relatórios JUnit (`smoke.xml` e `pytest.xml`) ficam no artefato `relatorios-de-teste` de cada execução, na aba Actions, mesmo quando algum teste falha. É a evidência para anexar no Jira.

### Deploy (Vercel)

A API roda no Vercel como uma função Python: com o preset FastAPI, o Vercel acha o `app` em `backend/app/main.py`. O `backend/vercel.json` fixa a região `cle1` (Ohio), a mesma do Neon (`us-east-2`), e o `backend/.python-version` fixa o Python 3.12 do CI.

Preparação (uma vez, na raiz do repositório):

```bash
vercel login                    # o script usa o CLI instalado, que é onde fica o login
vercel link --project gamekeys-api
scripts/vercel-env.sh           # envia DATABASE_URL, JWT_SECRET, AMBIENTE, BANCO_TIMEOUT_SEGUNDOS e JWT_DURACAO_MINUTOS
```

- No projeto do Vercel, o diretório raiz é `backend` e o preset de framework é **FastAPI**. Sem o preset o build termina vazio e todas as rotas respondem 404.
- O `JWT_SECRET` do `.env.local` precisa ter pelo menos 32 caracteres (`openssl rand -hex 32`); o script recusa o valor de exemplo.
- Produção usa `AMBIENTE=producao` (sem `/docs`); preview usa `desenvolvimento`.
- Para liberar as origens do front-end publicado, rode de novo com o endereço dele: `scripts/vercel-env.sh https://gamekeys-web.vercel.app`.
- Migrações não rodam no deploy: aplique com `python -m app.migrar` antes de publicar uma versão que mude o banco.
- Depois do deploy, `/saude/banco` confirma que a API alcança o Neon.

#### Ambiente de homologação (Release 2)

A partir da Release 2, a Sprint Review é feita sobre a versão publicada em homologação (GK-135 e GK-136).

| Item | Situação |
|---|---|
| Conta | Vercel Hobby do Pedro (`pedro-andrades-projects-abe06b11`). O plano Hobby não aceita membros; o acesso da equipe é decidido no estudo da GK-137 |
| API | Projeto `gamekeys-api`, diretório raiz `backend`, preset FastAPI, Python 3.12, região `cle1`. Endereço: https://gamekeys-api.vercel.app |
| Front-end | Projeto `gamekeys-web`, diretório raiz `frontend`, preset Vite. Endereço: https://gamekeys-web.vercel.app. O `frontend/vercel.json` repassa `/api/*` para a API (o mesmo papel do `nginx.conf` no Docker) e manda as demais rotas para `index.html`, então não precisa de `VITE_API_URL` nem de `CORS_ORIGENS` |
| Variáveis | Todas enviadas em 06/11 com `scripts/vercel-env.sh`, em produção e preview: `DATABASE_URL` (banco `gamekeys`, pooler, role `gamekeys_equipe`), `JWT_SECRET`, `AMBIENTE`, `BANCO_TIMEOUT_SEGUNDOS` e `JWT_DURACAO_MINUTOS`. Quem envia é quem tem as credenciais |
| Proteção | Deployment Protection padrão: os endereços de produção (`gamekeys-api.vercel.app` e `gamekeys-web.vercel.app`) abrem sem login, conferido em 07/11; as URLs de cada deploy pedem login do Vercel |
| Verificação (06/11) | `/saude` e `/saude/banco` respondem 200 (banco `gamekeys`, PostgreSQL 18); `/jogos` lista o catálogo; `/auth/login` com credencial errada responde 401 |

Com a proteção ligada, a verificação usa o próprio CLI, que passa pela proteção:

```bash
vercel curl /saude/banco --deployment gamekeys-api.vercel.app
```

Para publicar uma versão nova da API, na raiz do repositório vinculada ao `gamekeys-api`:

```bash
vercel deploy --prod
```

## Banco de dados

PostgreSQL no Neon (projeto `weathered-shadow-77764238`, branch `production`) para desenvolvimento e demonstração. Testes destrutivos usam outro PostgreSQL, local e descartável:

| Banco | Uso |
|---|---|
| `gamekeys` | desenvolvimento e demonstração |
| `gamekeys_teste` no Neon | legado compartilhado; proibido para execução do pytest |
| `gamekeys_teste` local, porta 5433 | testes automáticos; o pytest apaga e recria somente esta estrutura isolada |

### PostgreSQL local isolado para testes

Na raiz do repositório:

```powershell
docker compose -f docker-compose.test.yml up -d --wait
$env:TEST_DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys_teste?sslmode=disable"
cd backend
.venv\Scripts\python.exe -m pytest
```

Para a integração da interface, defina também `DATABASE_URL` e
`DATABASE_URL_UNPOOLED` com a mesma URL apenas no terminal dos testes. Ao terminar:

```powershell
docker compose -f docker-compose.test.yml down
```

O arquivo de teste não lê credenciais do Neon. SSL continua obrigatório nas URLs de
desenvolvimento e produção do Neon; `sslmode=disable` só é usado no loopback local.

### Conectar

1. Peça o arquivo de conexão ao DevOps e salve como `.env.local` na raiz do repositório (o modelo está em `.env.example`). Esse arquivo é ignorado pelo git: não commite e não poste em grupo.
2. A API lê `DATABASE_URL` (com pool). Migrações e cliente gráfico usam `DATABASE_URL_UNPOOLED` (direta).
3. Em cliente gráfico (DBeaver, Database Client do VS Code), use os campos `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD` do arquivo e ligue o SSL.

O usuário da equipe (`gamekeys_equipe`) lê e grava dados, mas não cria nem altera tabelas: mudança de estrutura entra por migração em `backend/migracoes/`, aplicada pelo DevOps.

### Rodar com Docker (API e front-end)

O banco continua no Neon: o Docker sobe só a API e o front-end, lendo o `.env.local` da raiz. Com Docker instalado:

```bash
docker compose up --build -d    # API em http://localhost:8000 e loja em http://localhost:8080
docker compose logs -f api      # acompanha a API
docker compose down             # para os dois
```

O front-end é o build do Vite servido pelo nginx, que repassa `/api` para a API, como o proxy do Vite faz em desenvolvimento. Para aplicar migrações pelo contêiner: `docker compose run --rm api python -m app.migrar`. O usuário da equipe não altera tabelas, então isso cabe ao DevOps.

### Estrutura (Sprint 1)

| Schema | Tabela | Destaques |
|---|---|---|
| `core` | `usuarios` | e-mail único (sem diferenciar maiúsculas), senha só como hash bcrypt, data de nascimento, perfil `cliente` por padrão |
| `catalogo` | `categorias` | nome e slug únicos |
| `catalogo` | `jogos` | categoria obrigatória, preço ≥ 0, plataforma, classificação (L a 18), `chaves_disponiveis` (0 = Esgotado), `ativo` |

Sempre escreva o schema no SQL (`catalogo.jogos`, não só `jogos`): pelo pool do Neon o `search_path` não se mantém entre transações. Compra, pedidos e chaves entram depois, no schema `vendas`.

### Comandos (dentro de `backend/`)

```bash
python -m app.migrar            # aplica migrações pendentes
python -m app.migrar --carga    # migrações + jogos e chaves fictícias de demonstração (não duplica)
pytest                          # inclui os testes de estrutura, contra gamekeys_teste
```

## Reserva de chaves (GK-15 / GK-124)

`POST /pedidos/reservas`, autenticado, recebe somente `chave_idempotencia` (UUID).
Reserva todo o carrinho, grava o pedido aguardando pagamento e limpa o carrinho
em uma transação. Repetir o UUID recupera o mesmo pedido. Preços são persistidos;
códigos de ativação ficam ocultos até a entrega da GK-16. O checkout visual segue
na GK-14. Há limites de 100 jogos, 1.000 unidades e R$ 99.999.999,99 por pedido.

A migração `0004_reserva_chaves.sql` cria chaves/pedidos/itens e **zera o estoque
legado**, que ainda não representa códigos físicos. O responsável do banco precisa
planejar a carga de chaves válidas antes de publicar. A aplicação mantém o contador
por trigger conforme o estado das chaves; não altere o contador diretamente.
`--carga` gera apenas códigos fictícios `GK-DEMO-SEM-VALOR-...` e conta técnica
inativa. Repetir a carga não libera códigos já reservados ou vendidos. Nenhuma
alteração no Neon foi executada no desenvolvimento desta entrega.

Veja o [contrato e integração com GK-126/GK-14](docs/api/GK-15-reserva.md), o
[roteiro de testes locais](docs/testes/GK-124-reserva.md) e o
[DER v1.1](docs/banco/DER-GameKeys-v1.1.dbml). Testes e migrações destrutivas de QA
usam exclusivamente PostgreSQL local isolado `gamekeys_teste`.

## Commits e branches

- Branch: `<tipo>/GK-<número>-descricao-curta` (ex.: `feature/GK-12-carrinho-alterar-itens`)
- Commit: `tipo: GK-<número> descrição` (ex.: `feat: GK-12 cadastro de cliente`). O hook `scripts/hooks/commit-msg` confere o formato; ative com `scripts/gk.sh install-hooks`
- Branch e PR podem ser abertos com `scripts/gk.sh` (veja `scripts/gk.sh ajuda`) ou pela skill do Claude Code em `.claude/skills/jira-gamekeys/`
- Toda mudança entra por pull request revisado por outro integrante. A `main` tem um ruleset (Settings > Rules) que exige PR com 1 aprovação de quem não fez o último push e os checks `frontend`, `backend` e `imagens Docker` verdes; não há bypass nem force push. Se um job do `ci.yml` mudar de nome, ajuste o ruleset junto.
