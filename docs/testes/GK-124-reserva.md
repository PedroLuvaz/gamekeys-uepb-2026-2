# GK-124 — Verificação da reserva

Ambiente permitido para os testes destrutivos: PostgreSQL local efêmero
`gamekeys_teste`. A proteção de `tests/conftest.py` recusa Neon e hosts remotos
antes de limpar qualquer schema. Os códigos usados nos testes são fictícios.

## Cobertura automatizada

`backend/tests/test_reservas.py` verifica o contrato HTTP, validação, origem do
comprador na sessão, dinheiro decimal, perfil, autenticação e erros sanitizados.

`backend/tests/test_reservas_banco.py` usa FastAPI, JWT e PostgreSQL reais:

| Caso | Oráculo |
| --- | --- |
| Reserva de dois jogos e várias unidades | um pedido; um item por chave; preço total exato; carrinho vazio |
| Repetição do UUID, inclusive concorrente | mesmo pedido e preço; sem nova reserva; novo carrinho preservado |
| Mesmo UUID de outro usuário | não recupera pedido alheio; cada pedido pertence à própria sessão |
| Estoque, idade, inativo e carrinho vazio | recusa sem pedido parcial nem limpeza do carrinho |
| Contador adulterado, sem chave física | reserva recusada, mesmo que o contador indique estoque |
| Falta no segundo jogo | reserva do primeiro jogo e pedido desfeitos integralmente |
| Falha após itens e limpeza, antes do commit | rollback de pedido/itens/chaves/contador/carrinho; pool reutilizável |
| 20 clientes disputando a última chave | exatamente 1 HTTP 200 e 19 HTTP 409; 1 pedido e 0 duplicadas |
| Chave bloqueada por outra transação | é pulada; sem reserva parcial; nova tentativa após liberação funciona |
| Jogo independente | bloqueio em outro jogo não impede sua reserva |
| Timeout de bloqueio | HTTP 503, rollback e conexão reutilizável |
| Composição em transação externa | rollback externo restaura chave; autocommit é recusado antes de gravar |
| Limite operacional e overflow monetário | HTTP 422 antes de alocar chaves |
| Constraints e permissões | chave única, jogo correto, reserva funciona com DML; DDL recusado |
| Trigger de estoque | contador acompanha status e exclusão; chave não muda de jogo |
| Migração do catálogo legado | mantém os 24 jogos, zera contadores e não inventa códigos nem contas |
| Reaplicar carga | não duplica código nem libera chave já reservada |

## Reproduzir em PowerShell

Na raiz do repositório, com Docker disponível:

```powershell
docker run --rm --name gamekeys-gk124-local -e POSTGRES_USER=gamekeys -e POSTGRES_PASSWORD=gamekeys -e POSTGRES_DB=gamekeys_teste -p 5434:5432 -d postgres:18-alpine
$env:TEST_DATABASE_URL = "postgresql://gamekeys:gamekeys@127.0.0.1:5434/gamekeys_teste"
$env:DATABASE_URL = $env:TEST_DATABASE_URL
$env:DATABASE_URL_UNPOOLED = $env:TEST_DATABASE_URL
$env:JWT_SECRET = "gk124-chave-exclusiva-de-teste-local-com-mais-de-32-bytes"
cd backend
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest tests/test_reservas.py tests/test_reservas_banco.py -v --junitxml=relatorios/gk124.xml
.venv\Scripts\python.exe -m pytest -v --junitxml=relatorios/pytest.xml
```

Espere o PostgreSQL estar pronto antes de rodar. O pytest aplica as migrações e a
carga ao recriar o banco. Não iniciar navegador/API concorrendo com o reset do pytest.
Não editar `.env.local` para rodar testes. As variáveis do processo têm prioridade.

Após o pytest terminar, é possível iniciar a API nesse mesmo terminal com
`.venv\Scripts\python.exe -m uvicorn app.main:app --reload` e usar `/docs`.
Cadastre uma conta fictícia, faça login, adicione um jogo com estoque e execute
`POST /pedidos/reservas` com um UUID. Reenvie o mesmo UUID: o pedido não deve mudar.

## Evidências e limites do aceite

Os relatórios JUnit entram no job `backend` e em seus artefatos do CI existente.
A consulta de unicidade é `select chave_id from vendas.itens_pedido group by
chave_id having count(*) > 1`; o resultado esperado é vazio, sem selecionar códigos.

O teste de 20 concorrentes desta subtarefa roda uma disputa real da reserva. O
experimento existente de 100 rodadas da GK-110 continua separado. Não apresentar
o experimento como aprovação das 100 rodadas do checkout final da GK-72.

GK-125 e GK-127 mantêm sua validação independente. Revisão, merge, publicação,
conferência do QA e aceite do PO são etapas posteriores; este roteiro não as aprova.
