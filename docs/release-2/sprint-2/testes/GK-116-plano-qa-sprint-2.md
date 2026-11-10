# GK-116 — Plano de QA da Sprint 2

## Objetivo e estado

Comprovar que carrinho, reserva e pedido preservam autenticação, estoque e exclusividade das
chaves, incluindo concorrência. O ambiente destrutivo autorizado é somente o PostgreSQL local
isolado `gamekeys_teste`.

Legenda de estado:

- **Automatizado:** teste implementado e executável no estado atual;
- **Regressão existente:** já coberto pela suíte da Release 1;
- **Preparado/aguarda:** cenário e oráculo definidos, mas o fluxo da história ainda não existe;
- **Executado:** usar apenas com comando, data e evidência registrados.

## Casos de teste

| ID | Cenário | Pré-condição | Resultado esperado | Evidência | Estado |
| --- | --- | --- | --- | --- | --- |
| QA-R2-001 | Adicionar jogo ao carrinho | cliente autenticado; jogo ativo com estoque | item entra com quantidade 1 | resposta da API + consulta a `itens_carrinho` | Executado em 07/11 e preservado na regressão da `main` em 09/11 |
| QA-R2-002 | Adicionar novamente o mesmo jogo | QA-R2-001 concluído | quantidade aumenta sem duplicar linha | resposta + consulta por carrinho/jogo | Executado em 07/11 e preservado na regressão da `main` em 09/11 |
| QA-R2-003 | Adicionar acima do estoque | estoque menor que quantidade pedida | operação recusada; carrinho não muda | HTTP/mensagem + antes/depois no banco | Executado em 07/11 e preservado na regressão da `main` em 09/11 |
| QA-R2-004 | Bloquear por classificação etária | idade do cliente abaixo da classificação | operação recusada com motivo; carrinho não muda | HTTP/mensagem + consulta | Executado em 07/11 e preservado na regressão da `main` em 09/11 |
| QA-R2-005 | Aumentar quantidade | item existente e estoque suficiente | quantidade e total são recalculados | resposta + cálculo decimal no banco | Executado; PR #30 aprovado, integrado e preservado na regressão da `main` |
| QA-R2-006 | Diminuir quantidade | item com quantidade maior que 1 | quantidade e total diminuem corretamente | resposta + consulta | Executado; PR #30 aprovado, integrado e preservado na regressão da `main` |
| QA-R2-007 | Remover item | item existente | item some e total é recalculado | resposta + ausência no banco | Executado; PR #30 aprovado, integrado e preservado na regressão da `main` |
| QA-R2-008 | Alterar acima do estoque | item existente; nova quantidade excessiva | alteração recusada; valor anterior preservado | HTTP/mensagem + antes/depois | Executado; PR #30 aprovado, integrado e preservado na regressão da `main` |
| QA-R2-009 | Reservar chave disponível | cliente autenticado; carrinho válido; chave livre | uma chave única fica associada ao pedido | API + `itens_pedido` sem mostrar código | Executado pela reserva real da GK-15; PR #33 integrado e regressão da `main` em 09/11 |
| QA-R2-010 | Segunda reserva sequencial da mesma chave | QA-R2-009 concluído; nenhuma outra chave | segunda tentativa recebe esgotado e não cria item | API + consulta de unicidade | Executado pela reserva real da GK-15; PR #33 integrado e regressão da `main` em 09/11 |
| QA-R2-011 | Duas transações disputam a última chave | schema `qa_gk110`; 1 chave; 2 conexões | 1 reserva e 1 esgotado; segunda não espera o lock | pytest + consulta de integridade | Executado no experimento GK-110 |
| QA-R2-012 | Rollback após reservar e antes do commit | falha injetada na transação | 0 pedidos/itens; chave volta a disponível | pytest + consulta de integridade | Executado no experimento GK-110 e na reserva real da GK-15 |
| QA-R2-013 | 20 reservas simultâneas × 100 rodadas | estado reiniciado a cada rodada; 1 chave | por rodada: 1 sucesso, 19 recusas, 0 duplicadas | JSON + consultas SQL | Executado com o serviço real de reserva da GK-15 em 09/11; checkout completo não coberto |
| QA-R2-014 | Integridade referencial do pedido reservado | reserva confirmada | todo item aponta para pedido e chave existentes | consulta de órfãos retorna 0 | Executado pela reserva real da GK-15; conclusão do checkout não coberta |
| QA-R2-015 | Estoque após reserva | 1 chave antes da reserva | estoque disponível passa a 0 uma única vez | consulta antes/depois | Executado pela reserva real da GK-15 e pela concorrência da GK-129 |
| QA-R2-016 | Falha da reserva não consome estoque | falha forçada antes do commit | chave e estoque permanecem disponíveis | API/log controlado + consulta | Executado pela reserva real da GK-15 |
| QA-R2-017 | JWT ausente | rota de carrinho/reserva protegida | HTTP 401; nenhuma alteração no banco | resposta + consulta | Executado no carrinho e na reserva real |
| QA-R2-018 | JWT inválido ou expirado | token adulterado/expirado | HTTP 401 uniforme; nenhuma alteração | resposta + consulta | Executado no carrinho e na reserva real |
| QA-R2-019 | Isolamento entre clientes | clientes A e B com dados distintos | A não lê/altera/reserva dados de B | respostas 403/404 + consulta por proprietário | Executado no carrinho e na reserva real; entrega de chave após checkout não coberta |
| QA-R1-001 | Saúde da API e banco | API e PostgreSQL local disponíveis | `/saude` e `/saude/banco` respondem sem segredo | pytest `smoke` | Executado na regressão da `main`: 233/233 em 09/11 |
| QA-R1-002 | Cadastro e e-mail único | banco local migrado | cadastro válido persiste hash; duplicado é recusado | `test_clientes*.py` | Executado na regressão da `main`: 233/233 em 09/11 |
| QA-R1-003 | Login e rota protegida | cliente local cadastrado | JWT válido funciona; credencial inválida recebe 401 | `test_autenticacao*.py` | Executado na regressão da `main`: 233/233 em 09/11 |
| QA-R1-004 | Catálogo, paginação e esgotado | carga de demonstração | apenas ativos; totais e disponibilidade corretos | `test_catalogo*.py` | Executado na regressão da `main`: 233/233 em 09/11 |
| QA-R1-005 | Detalhe do jogo | jogo ativo/inativo/inexistente | contrato completo ou 404 uniforme | `test_detalhe_jogo*.py` | Executado na regressão da `main`: 233/233 em 09/11 |
| QA-R1-006 | Restrições e estrutura do banco | migrações aplicadas | constraints, índices, permissões e persistência válidos | testes de banco existentes | Executado na regressão da `main`: 233/233 em 09/11 |

## Automação atual

O experimento isolado da GK-110 permanece em `backend/tests/test_concorrencia_gk110.py`. A prova
integrada pelas GK-128/GK-129 usa o serviço real de reserva da GK-15 e o PostgreSQL local; ela não
usa mock, SQLite nem contador em memória como prova de integridade. A regressão e o stress podem
ser reproduzidos com:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest -m concorrencia -v
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\python.exe -m qa.gk129_reserva_concorrente --rodadas 100 --concorrentes 20
```

Não foram adicionados testes `skip` ou `xfail` para os fluxos pendentes, pois esses estados podem
ocultar regressões futuras. Os contratos ainda não cobertos devem virar testes de API/banco no
mesmo PR que implementar cada rota, mantendo os mesmos IDs no nome/docstring ou em parametrização.

## Plano do stress 20 × 100

1. Recriar o estado da rodada com um jogo e uma chave.
2. Aquecer um pool com 20 conexões independentes.
3. Criar 20 clientes/pedidos distintos e sincronizar as threads por barreira.
4. Executar o serviço real de reserva da GK-15, com seleção bloqueante, criação do pedido e associação na mesma transação.
5. Contar resultados e consultar pedidos, itens, estoque e duplicidade.
6. Falhar imediatamente se a rodada não tiver exatamente 1 sucesso e 19 recusas.
7. Repetir 100 vezes, totalizando 2.000 tentativas.

O runner da GK-129 comprova a reserva real e transacional da GK-15 diretamente no serviço e no
PostgreSQL local. Ele não percorre o checkout completo pelo navegador, pagamento ou entrega da
chave. O experimento isolado da GK-110 também permanece identificado separadamente e não deve ser
apresentado como checkout aprovado.

## Evidência e registro de execução

| Execução | Comando | Ambiente | Resultado | Situação |
| --- | --- | --- | --- | --- |
| Lint/formatação | `ruff check .` e `ruff format --check .` | Python local, 04/11/2026 | passou | executado |
| Proteção do banco | seleção de testes `recusa or aceita` | sem conexão remota, 04/11/2026 | 11 passaram | executado |
| Concorrência GK-110 | `pytest tests/test_concorrencia_gk110.py -v` | Windows, Python 3.12.14, PostgreSQL 18 `gamekeys_teste`, 04/11/2026 | 5/5 passaram em 9,88 s | executado |
| Stress GK-110/GK-72 | módulo QA com 100 rodadas × 20 concorrentes | mesmo PostgreSQL local isolado, 04/11/2026 | 2.000 tentativas; 100 reservas; 1.900 recusas; 0 falhas; 9,001 s | executado no experimento isolado |
| Regressão backend | `pytest -v` | mesmo ambiente, 04/11/2026 | 92/92 passaram em 25,62 s; aviso de depreciação não bloqueante | executado |
| Build frontend | `pnpm build` | Node/pnpm local, 04/11/2026 | passou | executado |
| Regressão frontend | `pnpm test:e2e` | CI da `main`, API simulada, 09/11/2026 | 67/67 passaram em 34 s | executado; não substitui integração real |
| Auditoria Q-06 | `pytest -q`, `pnpm build` e `pnpm test:e2e` | Windows, Python 3.12.14, PostgreSQL 18 local `gamekeys_teste`, Node 24 e Cypress 16.2.0, 10/11/2026 | 243/243 backend e 96/96 interface passaram; matriz 44/44 | executado; 35 casos de UI e 9 contratos de reserva sem tela |
| Integração R2 | `pnpm test:integracao` | CI da `main`, API + PostgreSQL local, 09/11/2026 | 14/14 passaram em 28 s | executado; checkout completo não coberto |
| Lint/formatação GK-12 | `ruff check .` e `ruff format --check .` | Python local, 07/11/2026 | passou; 43 arquivos formatados | executado |
| Backend GK-12 | `pytest tests/test_carrinho.py tests/test_carrinho_banco.py -v` | PostgreSQL 18 local `gamekeys_teste`, 07/11/2026 | 76/76 passaram em 6,65 s | executado |
| Regressão backend GK-12 | `pytest -q` | mesmo PostgreSQL local, 07/11/2026 | 175/175 passaram em 30,71 s; aviso de depreciação do `TestClient` não bloqueante | executado |
| Interface GK-12 | `pnpm test:e2e` | Cypress 16.2.0, API controlada, 07/11/2026 | 67/67 passaram em 1 min 13 s; 6 cenários específicos da GK-12 | executado |
| Integração real GK-12/R1 | `pnpm test:integracao` | API real + PostgreSQL 18 local `gamekeys_teste`, 07/11/2026 | 14/14 passaram em 44 s; 5 cenários reais de carrinho | executado |
| Build frontend GK-12 | `pnpm build` | Node/pnpm local, 07/11/2026 | TypeScript e Vite passaram | executado |
| Regressão consolidada após PRs #30, #33 e #35 | `pytest -v` | GitHub Actions da `main`, PostgreSQL 18 local do CI, 09/11/2026 | 233/233 passaram em 21,56 s; 1 aviso não bloqueante do `TestClient` | executado |
| Reserva real concorrente GK-128/GK-129 | `python -m qa.gk129_reserva_concorrente --rodadas 100 --concorrentes 20` | GitHub Actions da `main`, PostgreSQL `gamekeys_teste`, isolamento `read committed`, 09/11/2026 | 2.000 tentativas; 100 reservas; 1.900 recusas; 0 rodadas com falha; 0 duplicidades; 9,04 s | executado com a reserva real da GK-15; não é checkout completo |
| Smoke publicado GK-140 | somente navegação e requisições GET | `https://gamekeys-web.vercel.app/`, 09/11/2026 | frontend, saúde, banco, catálogo, detalhe, login/cadastro e proteção do carrinho observados; sem erro no console | executado sem escrita; detalhes em [GK-140-smoke-homologacao.md](GK-140-smoke-homologacao.md) |
| Continuidade GK-140 | login inválido pela interface; saúde e proteção das rotas publicadas | Vercel publicado, proxy `/api` e API `gamekeys-api`, 09/11/2026 | acesso e roteamento HTTP 200; login inválido com mensagem uniforme; carrinho e reserva sem sessão responderam HTTP 401; nenhum erro no console | registro histórico sem persistência; pré-condições superadas na execução seguinte |
| Carrinho autenticado GK-140 | cadastro/login, vazio, adicionar, aumentar, diminuir, estoque, remover, recarregar e logout | Vercel publicado + Neon de homologação, 09/11/2026 | item de R$ 129,90; quantidade 2 = R$ 259,80; tentativa 13 recusada e preservou quantidade 12/total R$ 1.558,80; remoção, vazio persistente e proteção após logout | executado; total `R$ 0,00` não é renderizado no estado vazio; conta e carrinho fictícios removidos com 0 resíduos |

Critério de relato: “passou” exige data, commit, comando e resultado. “Aguarda implementação” não
é aprovação, falha mascarada ou conclusão da DoD.

## Ligações

- [GK-116](https://pedrolucas0721.atlassian.net/browse/GK-116)
- [GK-140](https://pedrolucas0721.atlassian.net/browse/GK-140)
- [GK-11](https://pedrolucas0721.atlassian.net/browse/GK-11)
- [GK-12](https://pedrolucas0721.atlassian.net/browse/GK-12)
- [GK-15](https://pedrolucas0721.atlassian.net/browse/GK-15)
- [GK-46](https://pedrolucas0721.atlassian.net/browse/GK-46)
- [GK-72](https://pedrolucas0721.atlassian.net/browse/GK-72)

## Atualização GK-11 em 07/11/2026

A GK-118 entrega a API, a GK-119 integra a ficha e a GK-120 automatiza os casos QA-R2-001 a QA-R2-004. A suíte local passou com 151 testes de back-end, 34 cenários Gherkin do carrinho (18 da entrega do Pedro na GK-119 e 16 complementares da GK-120) e os 3 testes reais do carrinho, além da regressão. O roteiro reproduzível e a rastreabilidade estão em [GK-11-aceite.md](GK-11-aceite.md). Os testes integrados confirmam a quantidade e a ausência de alteração nas recusas diretamente no PostgreSQL local `gamekeys_teste`. Nenhuma escrita foi feita no Neon. Este parágrafo preserva a evidência histórica de 07/11; o estado consolidado da `main` está registrado abaixo.

## Atualização GK-12 em 07/11/2026

Os casos QA-R2-005 a QA-R2-008 foram executados na API, na interface e diretamente no
PostgreSQL local `gamekeys_teste`. A cobertura também comprovou autenticação das novas rotas,
isolamento entre clientes, rollback após falha injetada, serialização de alterações concorrentes e
preservação do valor anterior quando o estoque é insuficiente. Os cálculos de subtotal e total
foram conferidos com `Decimal` no backend e com os valores devolvidos pela API na interface.

Os testes Cypress com API controlada não substituem a integração: a suíte real passou com a API e
o banco locais, incluindo alteração, redução, remoção e recusa por estoque. A primeira tentativa da
regressão real foi inválida por configuração local (segredo JWT curto e ausência do ID do jogo
inativo); depois de corrigidos somente esses parâmetros, os 14 testes passaram sem alteração dos
critérios. Nenhum teste destrutivo foi executado no Neon.

A reserva de chave e a finalização do pedido não fazem parte da GK-12. O PR #30 foi revisado por
Pedro, aprovado e integrado; depois, o PR #33 implementou a reserva real da GK-15. O checkout
completo, pagamento e entrega da chave continuam fora da evidência desta história. A conclusão da
DoD não é inferida destes resultados.

## Implementação da reserva GK-124 em 08/11/2026

A rota `POST /pedidos/reservas` agora usa carrinho, JWT e as tabelas reais
`catalogo.chaves`, `vendas.pedidos` e `vendas.itens_pedido`. A automação da GK-124
cobre QA-R2-009/010 (reserva e segunda tentativa), 014/015/016 (integridade,
estoque e rollback) e autenticação/isolamento da reserva em 017/018/019.
As provas são `backend/tests/test_reservas.py` e `test_reservas_banco.py`;
o roteiro está em [GK-124-reserva.md](GK-124-reserva.md).

O teste real de 20 clientes da GK-124 exige 1 reserva e 19 recusas, conferindo
pedido único, quantidade e nenhuma chave duplicada no PostgreSQL local isolado.
O teste de falha injeta erro depois de gravar itens e limpar o carrinho e exige
rollback integral. Essa evidência complementa o experimento da GK-110; não o
renomeia nem declara aprovado o teste de 100 rodadas do checkout final da GK-72.

A implementação foi revisada por Pedro, aprovada e integrada pelo PR #33. O PR #35 acrescentou a
prova concorrente com a mesma reserva real e também foi aprovado e integrado. Isso não comprova o
checkout completo, pagamento ou entrega da chave, nem atribui aceite formal do PO ou conclusão da
DoD.

## Consolidação na `main` em 09/11/2026

- [PR #30](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/pull/30): GK-12 revisada por Pedro, aprovada e integrada.
- [PR #33](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/pull/33): reserva real da GK-15 revisada por Pedro, aprovada e integrada.
- [PR #35](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/pull/35): prova de concorrência das GK-128/GK-129 aprovada e integrada.
- [GitHub Actions 42617543511](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/42617543511): frontend, backend e imagens Docker passaram; 233 testes backend, 14 testes de integração e 67 testes Cypress com API controlada passaram.
- A prova 100 × 20 usou a reserva real da GK-15 no PostgreSQL local `gamekeys_teste`: 100 reservas, 1.900 recusas, nenhuma rodada inválida e nenhuma chave duplicada.
- Essa prova termina na criação transacional do pedido em estado de espera de pagamento. Não percorre checkout completo, pagamento nem entrega da chave ao cliente.
