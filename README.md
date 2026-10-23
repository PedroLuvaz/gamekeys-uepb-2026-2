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
- `/docs`: documentação automática dos endpoints (desligada com `AMBIENTE=producao`)

O front-end em `http://localhost:5173` já pode chamar a API; outras origens entram em `CORS_ORIGENS`.

O código fica em `backend/app/`: `rotas/` (endpoints), `esquemas/` (validação com Pydantic), `servicos/` (regras de negócio), `db.py` (acesso ao banco) e `config.py` (variáveis de ambiente).

### Testes e CI

- `pytest` roda tudo (é a regressão). `pytest -m smoke` roda só a verificação rápida: API no ar, banco alcançável e front-end liberado pelo CORS. Os testes de banco usam só `TEST_DATABASE_URL` (banco `gamekeys_teste`) e são pulados quando ela não está definida.
- A cada push e pull request, o GitHub Actions sobe o PostgreSQL pelo `docker-compose.yml`, aplica migrações e carga, roda ruff, o smoke e depois a suíte completa, e confere que os dados continuam no banco depois de reiniciá-lo.
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

### Alternativa local: Docker Compose

Para rodar o PostgreSQL na própria máquina (é o mesmo banco que o CI usa), com Docker instalado:

```bash
docker compose up -d --wait     # na raiz; cria gamekeys e gamekeys_teste na primeira vez
```

No `.env.local`, use as três URLs `localhost` comentadas no `.env.example`. Os dados ficam no volume `dados_postgres` e sobrevivem a `docker compose down` e a reinícios; só `docker compose down -v` apaga tudo. As credenciais `gamekeys`/`gamekeys` valem apenas para esse banco local.

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
