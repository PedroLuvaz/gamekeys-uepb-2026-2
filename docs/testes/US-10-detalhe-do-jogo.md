# Verificação da US-10 Detalhe do jogo

A US-10 permite ao visitante consultar um jogo antes de decidir pela compra.
Reutiliza a API e a ficha inicial entregues no PR #7 (GK-9), sem alterar tabelas.
Esta entrega completa as mensagens e a validação do detalhe. Compra, carrinho e
edição de jogos permanecem fora do escopo.

## Rastreabilidade

| Subtask                                                    | Comportamento                                                                 | Evidência automatizada                                                                        |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| [GK-87](https://pedrolucas0721.atlassian.net/browse/GK-87) | Seis campos de um jogo ativo; disponibilidade igual à listagem                | `backend/tests/test_detalhe_jogo.py`, `test_detalhe_jogo_banco.py` e `test_catalogo_banco.py` |
| GK-87                                                      | Inexistente e inativo respondem HTTP 404 sem expor dados                      | Testes com PostgreSQL isolado, incluindo jogo desativado depois da listagem                   |
| [GK-88](https://pedrolucas0721.atlassian.net/browse/GK-88) | Catálogo, endereço direto, recarga e retorno à página de origem               | `frontend/cypress/e2e/detalhe-jogo.feature`                                                   |
| GK-88                                                      | Carregamento, falha com nova tentativa, classificação Livre/14 anos e celular | Cenários de detalhe e conferência de largura em 320 pixels                                    |
| [GK-89](https://pedrolucas0721.atlassian.net/browse/GK-89) | Critérios de aceite de ativo, inexistente e inativo em Gherkin                | Nove cenários em `detalhe-jogo.feature`, incluindo dois exemplos de não encontrado            |
| GK-89                                                      | Tela, API e PostgreSQL funcionando juntos                                     | `frontend/cypress/integracao/detalhe-real.cy.ts`; ID do inativo obtido no banco local         |

Os cenários usam as tags do Plano de Teste: `@US-10`, `@R1`, `@smoke`,
`@regressao`, `@excecao` e `@mobile`. `@GK-10` e `@GK-89` facilitam a ligação
com o Jira. Os dados simulados vêm de `frontend/cypress/fixtures/detalhe-jogo.json`;
a integração real usa a carga fictícia existente da GK-57.

## Execução com banco local

Requer Docker, Python 3.12+, Node.js 24 e pnpm 11.25. As variáveis abaixo valem
somente para o terminal atual e apontam para o PostgreSQL local do projeto.
O pytest recria a estrutura de `gamekeys_teste`; não use o banco compartilhado
para esta execução.

Terminal 1, na raiz do repositório:

```powershell
docker compose up -d --wait
$env:DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5432/gamekeys"
$env:DATABASE_URL_UNPOOLED = $env:DATABASE_URL
$env:TEST_DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5432/gamekeys_teste"
cd backend
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m app.migrar --carga
.venv\Scripts\python.exe -m pytest --junitxml=relatorios/pytest.xml
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2, na raiz do repositório:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Terminal 3, na raiz do repositório:

```powershell
$env:GAMEKEYS_JOGO_INATIVO_ID = (docker compose exec -T postgres psql -U gamekeys -d gamekeys -tAc "select id from catalogo.jogos where not ativo order by id limit 1").Trim()
cd frontend
pnpm build
pnpm test:e2e
pnpm test:integracao
```

Para executar somente os cenários Gherkin da US-10:

```powershell
pnpm test:e2e --spec cypress/e2e/detalhe-jogo.feature
```

O CI executa o catálogo e o detalhe nos dois jobs existentes. O job `frontend`
confere TypeScript/build e os cenários com API simulada. O job `backend` confere
Ruff, pytest, integração real com PostgreSQL local e persistência da carga após
reiniciar o banco. Os relatórios JUnit/Cucumber e as capturas ficam nos artefatos
`relatorios-de-teste`, `relatorios-de-interface` e `relatorios-de-integracao-real`.

## Conferência manual para QA e PO

1. Em `http://127.0.0.1:5173`, abra um jogo e compare descrição, gênero,
   plataforma, classificação, preço e disponibilidade com `GET /jogos/{id}`.
2. Copie o endereço da ficha para uma nova aba e recarregue a página.
3. Na segunda página do catálogo, abra o jogo esgotado: ele continua tendo
   detalhes. Volte pelo link da ficha e confira a segunda página.
4. Abra `/jogos/9223372036854775807` e o endereço do ID inativo obtido no
   banco local. Ambos devem mostrar “Jogo não encontrado”, sem dados da ficha.
5. Confira a ficha no celular. Com a API desligada, confira a mensagem de falha;
   inicie a API novamente e use “Tentar novamente”.

A evidência automatizada não substitui a revisão de outro integrante nem o aceite
do PO. A US e as subtasks só devem ser concluídas conforme a DoD da equipe.
