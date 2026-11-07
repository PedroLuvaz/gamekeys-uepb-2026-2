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
| QA-R2-001 | Adicionar jogo ao carrinho | cliente autenticado; jogo ativo com estoque | item entra com quantidade 1 | resposta da API + consulta a `itens_carrinho` | Executado em 07/11: API, tela e banco local; conferência formal de QA pendente |
| QA-R2-002 | Adicionar novamente o mesmo jogo | QA-R2-001 concluído | quantidade aumenta sem duplicar linha | resposta + consulta por carrinho/jogo | Executado em 07/11: API, tela e banco local; conferência formal de QA pendente |
| QA-R2-003 | Adicionar acima do estoque | estoque menor que quantidade pedida | operação recusada; carrinho não muda | HTTP/mensagem + antes/depois no banco | Executado em 07/11: API, tela e banco local; conferência formal de QA pendente |
| QA-R2-004 | Bloquear por classificação etária | idade do cliente abaixo da classificação | operação recusada com motivo; carrinho não muda | HTTP/mensagem + consulta | Executado em 07/11: API, tela e banco local; conferência formal de QA pendente |
| QA-R2-005 | Aumentar quantidade | item existente e estoque suficiente | quantidade e total são recalculados | resposta + cálculo decimal no banco | Executado em 07/11: API, tela e PostgreSQL local |
| QA-R2-006 | Diminuir quantidade | item com quantidade maior que 1 | quantidade e total diminuem corretamente | resposta + consulta | Executado em 07/11: API, tela e PostgreSQL local |
| QA-R2-007 | Remover item | item existente | item some e total é recalculado | resposta + ausência no banco | Executado em 07/11: API, tela e PostgreSQL local |
| QA-R2-008 | Alterar acima do estoque | item existente; nova quantidade excessiva | alteração recusada; valor anterior preservado | HTTP/mensagem + antes/depois | Executado em 07/11: API, tela e PostgreSQL local |
| QA-R2-009 | Reservar chave disponível | cliente autenticado; pedido válido; chave livre | uma chave única fica associada ao pedido | API + `itens_pedido` sem mostrar código | Preparado/aguarda GK-15/GK-46 |
| QA-R2-010 | Segunda compra sequencial da mesma chave | QA-R2-009 concluído; nenhuma outra chave | segunda compra recebe esgotado e não cria item | API + consulta de unicidade | Preparado/aguarda GK-15/GK-46 |
| QA-R2-011 | Duas transações disputam a última chave | schema `qa_gk110`; 1 chave; 2 conexões | 1 reserva e 1 esgotado; segunda não espera o lock | pytest + consulta de integridade | Executado no experimento GK-110 |
| QA-R2-012 | Rollback após reservar e antes do commit | schema `qa_gk110`; falha injetada | 0 pedidos/itens; chave volta a disponível | pytest + consulta de integridade | Executado no experimento GK-110 |
| QA-R2-013 | 20 compras simultâneas × 100 rodadas | estado reiniciado a cada rodada; 1 chave | por rodada: 1 sucesso, 19 recusas, 0 duplicadas | JSON/JUnit + consulta SQL | Executado no experimento; checkout aguarda GK-15/GK-46 |
| QA-R2-014 | Integridade referencial do pedido | pedido concluído | todo item aponta para pedido e chave existentes | consulta de órfãos retorna 0 | Preparado/aguarda schema de vendas |
| QA-R2-015 | Estoque após sucesso | 1 chave antes da compra | estoque disponível passa a 0 uma única vez | consulta antes/depois | Preparado/aguarda GK-15 |
| QA-R2-016 | Falha do pedido não consome estoque | falha forçada antes do commit | chave e estoque permanecem disponíveis | API/log controlado + consulta | Preparado/aguarda GK-15/GK-46 |
| QA-R2-017 | JWT ausente | rota de carrinho/reserva protegida | HTTP 401; nenhuma alteração no banco | resposta + consulta | Carrinho executado em 07/11; reserva aguarda GK-15/GK-46 |
| QA-R2-018 | JWT inválido ou expirado | token adulterado/expirado | HTTP 401 uniforme; nenhuma alteração | resposta + consulta | Carrinho executado em 07/11; reserva aguarda GK-15/GK-46 |
| QA-R2-019 | Isolamento entre clientes | pedidos de clientes A e B | A não lê/reserva/recebe chave de B | respostas 403/404 + consulta por proprietário | Carrinho executado em 07/11; pedido/chave aguarda GK-15/GK-16 |
| QA-R1-001 | Saúde da API e banco | API e PostgreSQL local disponíveis | `/saude` e `/saude/banco` respondem sem segredo | pytest `smoke` | Executado na regressão backend 92/92 |
| QA-R1-002 | Cadastro e e-mail único | banco local migrado | cadastro válido persiste hash; duplicado é recusado | `test_clientes*.py` | Executado na regressão backend 92/92 |
| QA-R1-003 | Login e rota protegida | cliente local cadastrado | JWT válido funciona; credencial inválida recebe 401 | `test_autenticacao*.py` | Executado na regressão backend 92/92 |
| QA-R1-004 | Catálogo, paginação e esgotado | carga de demonstração | apenas ativos; totais e disponibilidade corretos | `test_catalogo*.py` | Executado na regressão backend 92/92 |
| QA-R1-005 | Detalhe do jogo | jogo ativo/inativo/inexistente | contrato completo ou 404 uniforme | `test_detalhe_jogo*.py` | Executado na regressão backend 92/92 |
| QA-R1-006 | Restrições e estrutura do banco | migrações aplicadas | constraints, índices, permissões e persistência válidos | testes de banco existentes | Executado na regressão backend 92/92 |

## Automação atual

Arquivo novo: `backend/tests/test_concorrencia_gk110.py`.

Ele executa PostgreSQL real e falha se houver resultado diferente do oráculo. Não usa mock,
SQLite nem contador em memória como prova de integridade. O teste 20 × 100 está na suíte normal,
marcado também com `concorrencia` para execução seletiva:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest -m concorrencia -v
.venv\Scripts\python.exe -m pytest -v
```

Não foram adicionados testes `skip` ou `xfail` para carrinho/checkout inexistentes. Esses estados
podem ocultar regressões futuras. Os contratos acima devem virar testes de API/banco no mesmo PR
que implementar cada rota, mantendo os mesmos IDs no nome/docstring ou em parametrização.

## Plano do stress 20 × 100

1. Recriar o estado da rodada com um jogo e uma chave.
2. Aquecer um pool com 20 conexões independentes.
3. Criar 20 clientes/pedidos distintos e sincronizar as threads por barreira.
4. Executar seleção bloqueante, criação de pedido e associação na mesma transação.
5. Contar resultados e consultar pedidos, itens, estoque e duplicidade.
6. Falhar imediatamente se a rodada não tiver exatamente 1 sucesso e 19 recusas.
7. Repetir 100 vezes, totalizando 2.000 tentativas.

Para o checkout real, a preparação deve também autenticar 20 clientes e chamar a API. O teste do
experimento não deve ser renomeado nem apresentado como aprovação de GK-15/GK-46.

## Evidência e registro de execução

| Execução | Comando | Ambiente | Resultado | Situação |
| --- | --- | --- | --- | --- |
| Lint/formatação | `ruff check .` e `ruff format --check .` | Python local, 04/11/2026 | passou | executado |
| Proteção do banco | seleção de testes `recusa or aceita` | sem conexão remota, 04/11/2026 | 11 passaram | executado |
| Concorrência GK-110 | `pytest tests/test_concorrencia_gk110.py -v` | Windows, Python 3.12.14, PostgreSQL 18 `gamekeys_teste`, 04/11/2026 | 5/5 passaram em 9,88 s | executado |
| Stress GK-110/GK-72 | módulo QA com 100 rodadas × 20 concorrentes | mesmo PostgreSQL local isolado, 04/11/2026 | 2.000 tentativas; 100 reservas; 1.900 recusas; 0 falhas; 9,001 s | executado no experimento isolado |
| Regressão backend | `pytest -v` | mesmo ambiente, 04/11/2026 | 92/92 passaram em 25,62 s; aviso de depreciação não bloqueante | executado |
| Build frontend | `pnpm build` | Node/pnpm local, 04/11/2026 | passou | executado |
| Regressão frontend | `pnpm test:e2e` | API simulada conforme R1 | não executada | aguarda CI |
| Integração R2 | casos QA-R2-001 a 019 | API + PostgreSQL local | não executada | depende das histórias indicadas |
| Lint/formatação GK-12 | `ruff check .` e `ruff format --check .` | Python local, 07/11/2026 | passou; 43 arquivos formatados | executado |
| Backend GK-12 | `pytest tests/test_carrinho.py tests/test_carrinho_banco.py -v` | PostgreSQL 18 local `gamekeys_teste`, 07/11/2026 | 76/76 passaram em 6,65 s | executado |
| Regressão backend GK-12 | `pytest -q` | mesmo PostgreSQL local, 07/11/2026 | 175/175 passaram em 30,71 s; aviso de depreciação do `TestClient` não bloqueante | executado |
| Interface GK-12 | `pnpm test:e2e` | Cypress 16.2.0, API controlada, 07/11/2026 | 67/67 passaram em 1 min 13 s; 6 cenários específicos da GK-12 | executado |
| Integração real GK-12/R1 | `pnpm test:integracao` | API real + PostgreSQL 18 local `gamekeys_teste`, 07/11/2026 | 14/14 passaram em 44 s; 5 cenários reais de carrinho | executado |
| Build frontend GK-12 | `pnpm build` | Node/pnpm local, 07/11/2026 | TypeScript e Vite passaram | executado |

Critério de relato: “passou” exige data, commit, comando e resultado. “Aguarda implementação” não
é aprovação, falha mascarada ou conclusão da DoD.

## Ligações

- [GK-116](https://pedrolucas0721.atlassian.net/browse/GK-116)
- [GK-11](https://pedrolucas0721.atlassian.net/browse/GK-11)
- [GK-12](https://pedrolucas0721.atlassian.net/browse/GK-12)
- [GK-15](https://pedrolucas0721.atlassian.net/browse/GK-15)
- [GK-46](https://pedrolucas0721.atlassian.net/browse/GK-46)
- [GK-72](https://pedrolucas0721.atlassian.net/browse/GK-72)

## Atualização GK-11 em 07/11/2026

A GK-118 entrega a API, a GK-119 integra a ficha e a GK-120 automatiza os casos QA-R2-001 a QA-R2-004. A suíte local passou com 151 testes de back-end, 34 cenários Gherkin do carrinho (18 da entrega do Pedro na GK-119 e 16 complementares da GK-120) e os 3 testes reais do carrinho, além da regressão. O roteiro reproduzível e a rastreabilidade estão em [GK-11-aceite.md](GK-11-aceite.md). Os testes integrados confirmam a quantidade e a ausência de alteração nas recusas diretamente no PostgreSQL local gamekeys_teste. Nenhuma escrita foi feita no Neon. A conferência formal do QA, a revisão independente e a integração do PR continuam pendentes.

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

A reserva de chave e a finalização do pedido não fazem parte da GK-12. Os casos QA-R2-009,
QA-R2-010 e QA-R2-014 a QA-R2-016 continuam aguardando GK-15/GK-46; as partes de reserva e
pedido de QA-R2-017 a QA-R2-019 também permanecem pendentes. A revisão independente, o merge e
a conclusão da DoD não foram realizados.
