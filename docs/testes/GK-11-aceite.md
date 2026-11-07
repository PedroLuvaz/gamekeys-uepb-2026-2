# Aceite da GK-11 Adicionar jogo ao carrinho

Esta entrega reúne o endpoint da GK-118, a ação na ficha da GK-119 e os testes da
GK-120. A API usa o cliente autenticado, verifica a idade e o estoque acumulado e
retorna o item persistido. A tela mostra esse resultado, sem manter um carrinho
paralelo no navegador. Adicionar não reserva chaves; consulta, alteração e remoção
do carrinho pertencem à GK-12 e a reserva pertence à GK-15/GK-46.

## Critérios e evidências

| Critério da US                                                         | Casos do plano GK-116 | Automação                                                                                                               |
| ---------------------------------------------------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Logado e com estoque, o jogo entra; se já estava, aumenta a quantidade | QA-R2-001 e QA-R2-002 | Pytest de carrinho; `carrinho.feature`; primeiro teste de `carrinho-real.cy.ts`, com consulta ao banco após cada clique |
| Quantidade acima do disponível é recusada com aviso                    | QA-R2-003             | Pytest de estoque inicial/acumulado; cenário Gherkin; segundo teste real, confirmando nenhuma linha gravada             |
| Classificação acima da idade é recusada com motivo                     | QA-R2-004             | Pytest de idade/aniversário; cenário Gherkin; terceiro teste real, autenticando uma conta menor de idade                |

`frontend/cypress/e2e/carrinho.feature` tem 16 cenários com tags `@US-11`,
`@GK-11`, `@GK-119`, `@GK-120`, `@R2`, `@regressao`, `@smoke` e `@excecao`.
Além dos critérios, cobrem quantidade escolhida, login com retorno interno,
expiração da sessão, esgotado, indisponibilidade, falha de rede, envio duplicado,
quantidade inválida, perfil de administrador e celular de 320 pixels.

As respostas simuladas demonstram o comportamento da interface. A prova integrada
está em `frontend/cypress/integracao/carrinho-real.cy.ts`, que usa o formulário de
login, JWT, API e PostgreSQL reais, sem interceptar as respostas. A fixture cria
um jogo com estoque 3 e classificação 18, um adulto e um menor. No sucesso, a
consulta confirma uma única linha e quantidades 1 e 2; nas recusas, confirma 0
itens. O estoque continua 3, pois a adição não é reserva.

## Ambiente isolado e execução

Todos os testes com gravação usam `gamekeys_teste` em PostgreSQL local. O compose
principal publica a API e a interface usando a configuração do Neon; ele não sobe
o banco de testes. Se necessário, crie um PostgreSQL temporário separado:

```powershell
docker run --rm --name gamekeys-qa-local -e POSTGRES_USER=gamekeys -e POSTGRES_PASSWORD=gamekeys -e POSTGRES_DB=gamekeys_teste -p 5433:5432 -d postgres:18-alpine
```

No terminal da API, a partir da raiz do repositório, configure os valores exclusivos
do teste local. Ajuste a porta se já estiver ocupada:

```powershell
$env:TEST_DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys_teste"
$env:DATABASE_URL = $env:TEST_DATABASE_URL
$env:DATABASE_URL_UNPOOLED = $env:TEST_DATABASE_URL
$env:JWT_SECRET = "gk11-chave-exclusiva-para-teste-local-com-32-bytes"
cd backend
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m app.migrar --carga
.venv\Scripts\python.exe -m pytest -v --junitxml=relatorios/pytest.xml
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

O pytest recria os schemas e precisa terminar antes de iniciar a API para o teste
de navegador. Não altere o `.env.local` compartilhado com essas configurações.

Em outro terminal, dentro de `frontend/`, instale as dependências e execute
`pnpm dev`. Em um terceiro terminal, a partir da raiz:

```powershell
$env:TEST_DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys_teste"
$env:GAMEKEYS_JOGO_INATIVO_ID = (docker exec gamekeys-qa-local psql -U gamekeys -d gamekeys_teste -tAc "select id from catalogo.jogos where not ativo order by id limit 1").Trim()
cd frontend
pnpm build
pnpm test:e2e
pnpm test:integracao
```

Para executar somente os novos cenários, use
`pnpm test:e2e --spec cypress/e2e/carrinho.feature` e
`pnpm test:integracao --spec cypress/integracao/carrinho-real.cy.ts`.

A configuração usa o Python da `.venv` no Windows e `python` no Linux/CI.
`GAMEKEYS_PYTHON` pode definir outro executável. Essa variável fica no processo de
testes, não no bundle do navegador. O suporte da suíte real verifica que a API
aponta para `gamekeys_teste` antes de qualquer cadastro. As tasks executam
`qa.gk11_carrinho`, que recusa URLs remotas antes de conectar, usa UUID por cenário
e remove apenas os registros fictícios correspondentes. Não limpa tabelas inteiras,
não migra o banco e não retorna URL de conexão ou JWT ao navegador.

No CI, a API dos testes reais também aponta para `TEST_DATABASE_URL`; os demais
jobs continuam com PostgreSQL efêmero, relatórios e verificação das imagens Docker.

## Comportamento em falhas

- Duplo clique e dois eventos de envio no mesmo instante geram apenas um POST.
- Cada clique posterior ao sucesso é uma nova adição incremental e explícita.
- Resposta 401 encerra a sessão e volta ao login com retorno para o mesmo jogo.
- Estoque e idade são decisões do servidor; a tela exibe os motivos recebidos.
- Se a conexão cair depois do envio, pode ter havido commit. A tela informa que
  não conseguiu confirmar e não repete automaticamente. Cancelar a requisição ao
  sair da ficha não implica desfazer o que o servidor já gravou.
- A quantidade e o subtotal de sucesso vêm da resposta do banco, sem contagem
  otimista ou soma monetária em ponto flutuante na aplicação.

## Validação para a Review

1. Faça login, abra um jogo disponível, adicione e repita. Confira quantidade e
   subtotal do item confirmados pela API.
2. Informe quantidade acima do estoque e confira aviso sem alteração persistida.
3. Entre com uma conta fictícia menor que a classificação do jogo e confira o motivo.
4. Confira carregamento, esgotado e celular. Teste a volta à ficha após login.
5. Relacione o resultado por cenário à execução do CI e ao PR da GK-11 na GK-116.

As evidências automatizadas não substituem a revisão independente nem a conferência
formal de QA. A US não deve ser marcada Concluída antes de revisão, merge, migração
e publicação no ambiente aplicável, validação de QA e aceite do PO conforme a DoD.
