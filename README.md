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

| Integrante | Papel na Release 1 |
|---|---|
| Pedro Lucas Vaz de Andrade | Product Owner e DevOps |
| Wagner Tiburcio da Silva Junior | QA |
| Rodrigo Almeida Gomes | Scrum Master |

Os papéis mudam ao fim de cada release. Quem é PO também é DevOps.

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

O que vale é a versão do Drive, onde a equipe preenche. A cópia em `docs/` é atualizada no fim da sprint.

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

Os 27 cenários em `cypress/e2e/` cobrem cadastro, login, sessão, paginação, esgotado,
navegação ao detalhe e retorno, lista vazia, falha e nova tentativa, carregamento, página
além da última, celular, jogo não encontrado, histórico do navegador, recarga e capa
indisponível. Usam respostas simuladas na rede: não
acessam nem recriam o banco do Neon. A base pode ser reaproveitada nos testes de cadastro
e login. Relatórios JUnit e Cucumber ficam em `frontend/cypress/reports/`; capturas de
falhas ficam em `frontend/cypress/screenshots/`. Esses arquivos são ignorados pelo Git.

Os nove testes em `cypress/integracao/` usam a API em execução e o PostgreSQL sem simular
respostas. Os testes de cadastro e login criam contas fictícias com e-mail único para provar
persistência, autenticação e mensagens seguras; os demais consultam a carga de demonstração.
Execute esta suíte somente
com os bancos `gamekeys` ou `gamekeys_teste`. No CI, ela usa o PostgreSQL efêmero do
próprio job, com API e interface iniciadas nele.

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
compartilhado do Neon: combine a execução com a equipe, porque o pytest recria a estrutura dele.

`GET /jogos/{id}` retorna os mesmos campos do cartão, mais `descricao`, `genero`,
`plataforma` e `classificacao`. Jogo inexistente ou inativo recebe HTTP 404 com a mesma
mensagem de não encontrado; falha de banco recebe HTTP 503 sem expor dados da conexão.

### Testes e CI

- `pytest` roda tudo (é a regressão). `pytest -m smoke` roda só a verificação rápida: API no ar, banco alcançável e front-end liberado pelo CORS. Os testes de banco usam só `TEST_DATABASE_URL` (banco `gamekeys_teste`) e são pulados quando ela não está definida.
- A cada push e pull request, o GitHub Actions sobe um PostgreSQL próprio do job (serviço `postgres`), aplica migrações e carga, roda ruff, o smoke e depois a suíte completa, e confere que os dados continuam no banco depois de reiniciá-lo.
- O job de interface compila o front-end e executa os 27 cenários com API simulada. O job de back-end também executa os nove testes reais da tela integrada à API e ao PostgreSQL local. Relatórios e capturas de falhas são guardados como artefatos separados.
- O job `imagens Docker` gera as imagens da API e do front-end com `docker compose build`, para o `Dockerfile` não quebrar sem ninguém ver.
- Os relatórios JUnit (`smoke.xml` e `pytest.xml`) ficam no artefato `relatorios-de-teste` de cada execução, na aba Actions, mesmo quando algum teste falha. É a evidência para anexar no Jira.

## Banco de dados

PostgreSQL no Neon (projeto `weathered-shadow-77764238`, branch `production`). São dois bancos:

| Banco | Uso |
|---|---|
| `gamekeys` | desenvolvimento e demonstração |
| `gamekeys_teste` | testes automáticos; o pytest apaga e recria a estrutura a cada execução |

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
python -m app.migrar --carga    # migrações + jogos de demonstração (pode repetir, não duplica)
pytest                          # inclui os testes de estrutura, contra gamekeys_teste
```

## Commits e branches

- Branch: `<tipo>/GK-<número>-descricao-curta` (ex.: `feature/GK-12-carrinho-alterar-itens`)
- Commit: `tipo: GK-<número> descrição` (ex.: `feat: GK-12 cadastro de cliente`). O hook `scripts/hooks/commit-msg` confere o formato; ative com `scripts/gk.sh install-hooks`
- Branch e PR podem ser abertos com `scripts/gk.sh` (veja `scripts/gk.sh ajuda`) ou pela skill do Claude Code em `.claude/skills/jira-gamekeys/`
- Toda mudança entra por pull request revisado por outro integrante.
