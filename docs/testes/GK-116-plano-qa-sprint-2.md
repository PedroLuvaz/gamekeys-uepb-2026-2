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
| QA-R2-005 | Aumentar quantidade | item existente e estoque suficiente | quantidade e total são recalculados | resposta + cálculo decimal no banco | Preparado/aguarda GK-12 |
| QA-R2-006 | Diminuir quantidade | item com quantidade maior que 1 | quantidade e total diminuem corretamente | resposta + consulta | Preparado/aguarda GK-12 |
| QA-R2-007 | Remover item | item existente | item some e total é recalculado | resposta + ausência no banco | Preparado/aguarda GK-12 |
| QA-R2-008 | Alterar acima do estoque | item existente; nova quantidade excessiva | alteração recusada; valor anterior preservado | HTTP/mensagem + antes/depois | Preparado/aguarda GK-12 |
| QA-R2-009 | Reservar chave disponível | cliente autenticado; pedido válido; chave livre | uma chave única fica associada ao pedido | API + `itens_pedido` sem mostrar código | Preparado/aguarda GK-15/GK-46 |
| QA-R2-010 | Segunda compra sequencial da mesma chave | QA-R2-009 concluído; nenhuma outra chave | segunda compra recebe esgotado e não cria item | API + consulta de unicidade | Preparado/aguarda GK-15/GK-46 |
| QA-R2-011 | Duas transações disputam a última chave | schema `qa_gk110`; 1 chave; 2 conexões | 1 reserva e 1 esgotado; segunda não espera o lock | pytest + consulta de integridade | Executado no experimento GK-110 |
| QA-R2-012 | Rollback após reservar e antes do commit | schema `qa_gk110`; falha injetada | 0 pedidos/itens; chave volta a disponível | pytest + consulta de integridade | Executado no experimento GK-110 |
| QA-R2-013 | 20 compras simultâneas × 100 rodadas | estado reiniciado a cada rodada; 1 chave | por rodada: 1 sucesso, 19 recusas, 0 duplicadas | JSON/JUnit + consulta SQL | Executado no experimento; checkout aguarda GK-15/GK-46 |
| QA-R2-014 | Integridade referencial do pedido | pedido concluído | todo item aponta para pedido e chave existentes | consulta de órfãos retorna 0 | Preparado/aguarda schema de vendas |
| QA-R2-015 | Estoque após sucesso | 1 chave antes da compra | estoque disponível passa a 0 uma única vez | consulta antes/depois | Preparado/aguarda GK-15 |
| QA-R2-016 | Falha do pedido não consome estoque | falha forçada antes do commit | chave e estoque permanecem disponíveis | API/log controlado + consulta | Preparado/aguarda GK-15/GK-46 |
| QA-R2-017 | JWT ausente | rota de carrinho/reserva protegida | HTTP 401; nenhuma alteração no banco | resposta + consulta | Preparado/aguarda rotas R2 |
| QA-R2-018 | JWT inválido ou expirado | token adulterado/expirado | HTTP 401 uniforme; nenhuma alteração | resposta + consulta | Preparado/aguarda rotas R2 |
| QA-R2-019 | Isolamento entre clientes | pedidos de clientes A e B | A não lê/reserva/recebe chave de B | respostas 403/404 + consulta por proprietário | Preparado/aguarda GK-15/GK-16 |
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

A GK-118 entrega a API, a GK-119 integra a ficha e a GK-120 automatiza os casos QA-R2-001 a QA-R2-004. A suíte local passou com 151 testes de back-end, 16 novos cenários Gherkin do carrinho e os 3 testes reais do carrinho, além da regressão. O roteiro reproduzível e a rastreabilidade estão em [GK-11-aceite.md](GK-11-aceite.md). Os testes integrados confirmam a quantidade e a ausência de alteração nas recusas diretamente no PostgreSQL local gamekeys_teste. Nenhuma escrita foi feita no Neon. A conferência formal do QA, a revisão independente e a integração do PR continuam pendentes.
