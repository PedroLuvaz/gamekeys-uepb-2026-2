# GK-110 — Experimento de transações e concorrência no PostgreSQL

## Escopo e limite

Este experimento responde, em uma sessão de investigação, se transações concorrentes podem
reservar a mesma chave quando a seleção usa bloqueio de linha. Ele usa exclusivamente o banco
local descartável `gamekeys_teste` e o schema isolado `qa_gk110`.

O resultado orienta GK-15 e GK-46, mas **não comprova o checkout da aplicação**: carrinho,
pedido, autenticação do comprador e entrega da chave ainda precisam ser implementados e
testados no fluxo real. Nenhuma consulta destrutiva foi nem deve ser executada no Neon.

## Hipótese e desenho

Hipótese: com a seleção abaixo dentro da mesma transação que cria o pedido e associa a chave,
somente uma operação obtém a última linha disponível. As demais não esperam a linha bloqueada:
recebem resultado vazio e tratam o estoque como esgotado.

```sql
select id
  from qa_gk110.chaves
 where jogo_id = %s and estado = 'disponivel'
 order by id
 limit 1
   for update skip locked;
```

O experimento cria quatro tabelas descartáveis que espelham apenas as relações necessárias:
`jogos`, `chaves`, `pedidos` e `itens_pedido`. `itens_pedido.chave_id` possui restrição
`unique`, uma segunda defesa de integridade além do bloqueio. Não existem códigos de ativação
reais nessas tabelas.

## Decisões técnicas

- **`FOR UPDATE SKIP LOCKED`:** a linha obtida fica bloqueada para escrita até o fim da
  transação. Outra tentativa ignora a linha já bloqueada em vez de aguardar. O PostgreSQL
  adverte que isso produz uma visão inconsistente para consultas gerais; aqui é apropriado
  porque as chaves disponíveis funcionam como uma fila de recursos consumíveis.
- **Transação e rollback:** selecionar, criar pedido, marcar a chave e inserir o item ocorrem
  na mesma transação. Saída normal do contexto do psycopg faz commit; exceção provoca rollback.
  O teste injeta uma falha depois do `update` e antes do commit e confirma que não sobram pedido,
  item ou reserva parcial.
- **Isolamento:** o experimento fixa e verifica `read committed`, padrão do PostgreSQL. Cada
  comando enxerga dados confirmados antes do início daquele comando; o bloqueio explícito é o
  mecanismo que coordena o consumo da linha.
- **psycopg e threads:** cada thread recebe uma conexão própria de `ConnectionPool`. Compartilhar
  uma única conexão faria as threads compartilharem também a mesma transação e serializaria a
  execução, o que não representaria compradores independentes. `pool.wait()` valida as conexões
  antes de liberar a rodada.
- **Evidência de simultaneidade:** uma barreira libera as 20 threads juntas. Um teste menor segura
  propositalmente o bloqueio da primeira transação e prova que a segunda retorna `esgotado` antes
  da liberação, demonstrando o efeito de `SKIP LOCKED`.

## Local versus Neon

| Aspecto | PostgreSQL local do experimento | Neon da aplicação |
| --- | --- | --- |
| Banco | `gamekeys_teste`, loopback, porta 5433 | Banco remoto compartilhado |
| Segurança | o código recusa host remoto e outro nome de banco antes do DDL | não executar este experimento |
| Conexão | PostgreSQL direto, sem TLS, somente na máquina | TLS; URL com `-pooler` usa PgBouncer |
| Pool | 20 conexões reais no processo de teste | pool da aplicação deve ser dimensionado; pooler trabalha em modo transação |
| Estado de sessão | persiste durante a conexão local | não depender de estado de sessão entre transações no pooler |
| Prepared statements | desativados no harness para aproximar a configuração atual | a aplicação usa `prepare_threshold=None`; reavaliar com a versão do PgBouncer adotada |
| Migrações/DDL | schema de QA descartável | usar conexão direta e fluxo de migração aprovado, não o teste concorrente |

A semântica transacional do PostgreSQL é a mesma, mas latência, limites de conexão, pooler e
suspensão do compute alteram o comportamento operacional. Portanto, o resultado local valida a
integridade do algoritmo no PostgreSQL real, não o desempenho nem a capacidade do Neon.

## Como reproduzir

Na raiz do repositório, com Docker Desktop em execução:

```powershell
docker compose -f docker-compose.test.yml up -d --wait
$env:TEST_DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5433/gamekeys_teste?sslmode=disable"
cd backend
.venv\Scripts\python.exe -m pytest tests\test_concorrencia_gk110.py -v
.venv\Scripts\python.exe -m qa.gk110_concorrencia --rodadas 100 --concorrentes 20
```

O comando Python imprime JSON sem URL, senha, JWT ou código de ativação. O processo retorna
código diferente de zero se alguma rodada violar a expectativa. Para encerrar:

```powershell
cd ..
docker compose -f docker-compose.test.yml down
```

## Oráculos de integridade por rodada

- exatamente 1 resultado `reservada` e 19 resultados `esgotado`;
- exatamente 1 pedido e 1 item de pedido persistidos;
- 0 chaves disponíveis depois do sucesso;
- 0 valores de `chave_id` ligados a mais de um item;
- após falha injetada: 0 pedidos, 0 itens e 1 chave disponível;
- a mesma chave pode ser reservada normalmente por uma nova transação após o rollback.

Consulta de auditoria, sem expor o conteúdo da chave:

```sql
select chave_id, count(*)
  from qa_gk110.itens_pedido
 group by chave_id
having count(*) > 1;
```

## Execução registrada

Execução realizada por Rodrigo em 04/11/2026, no Git Bash do Windows, contra PostgreSQL 18
local e isolado. Ambiente Python 3.12.14; nenhuma operação destrutiva foi executada no Neon.

| Comando | Commit testado | Ambiente | Resultado | Duração |
| --- | --- | --- | --- | --- |
| `pytest tests/test_concorrencia_gk110.py -v` | `62eb852` | Windows, Python 3.12.14, PostgreSQL 18 `gamekeys_teste` | 5/5 passaram | 9,88 s |
| `python -m qa.gk110_concorrencia --rodadas 100 --concorrentes 20` | `62eb852` | mesmo PostgreSQL local isolado | 2.000 tentativas: 100 reservas, 1.900 recusas e 0 rodadas com falha | 9,001 s |
| `pytest -v` | `62eb852` | mesmo ambiente | 92/92 passaram; 1 aviso não bloqueante de depreciação do `TestClient` | 25,62 s |

O teste de stress confirmou, em cada uma das 100 rodadas, exatamente uma reserva, 19 recusas
por esgotamento e nenhuma chave duplicada. Esses números comprovam o experimento isolado da
GK-110; não representam execução do checkout real, que continua dependente de GK-15/GK-46.

## Limitações e próximos passos

- Integrar a mesma regra à implementação real de GK-15/GK-46, sem reutilizar o schema de QA.
- Executar os cenários de autenticação, propriedade do pedido, estoque e entrega na API real.
- Reexecutar 20 × 100 sobre o checkout quando GK-14/GK-16 disponibilizarem o fluxo.
- Revisar o tamanho do pool para produção; 20 conexões no harness são uma carga de teste, não uma
  recomendação de configuração.
- Obter revisão independente antes do merge. Este material não marca DoD, não aceita histórias e
  não substitui a decisão do PO.

## Referências

- [PostgreSQL — `SELECT` e `SKIP LOCKED`](https://www.postgresql.org/docs/current/sql-select.html)
- [PostgreSQL — isolamento de transações](https://www.postgresql.org/docs/current/transaction-iso.html)
- [psycopg 3 — transações](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)
- [psycopg 3 — concorrência](https://www.psycopg.org/psycopg3/docs/advanced/async.html)
- [psycopg 3 — pools de conexão](https://www.psycopg.org/psycopg3/docs/advanced/pool.html)
- [Neon — PgBouncer e prepared statements](https://neon.com/blog/pgbouncer-the-one-with-prepared-statements)
- [GK-110](https://pedrolucas0721.atlassian.net/browse/GK-110),
  [GK-15](https://pedrolucas0721.atlassian.net/browse/GK-15),
  [GK-46](https://pedrolucas0721.atlassian.net/browse/GK-46) e
  [GK-72](https://pedrolucas0721.atlassian.net/browse/GK-72)
