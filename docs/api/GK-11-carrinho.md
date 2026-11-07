# Adicionar jogo ao carrinho — GK-11 e GK-118

Contrato para a ação de adicionar da GK-119 e para a continuação do carrinho na
GK-12. A API exige a sessão da GK-8 e usa o cliente autenticado para identificar o
carrinho. O corpo não aceita identificador do cliente/carrinho, preço nem idade.

A GK-119 está implementada na ficha: quantidade, carregamento, confirmação da
quantidade acumulada e mensagens do servidor. Quem está sem sessão entra e volta
à mesma ficha; o login não dispara a compra/adição sozinho. Sessão recusada é
removida e pede novo login. Envios duplicados ficam bloqueados durante a operação.
Veja o [roteiro de aceite da GK-11](../testes/GK-11-aceite.md) para os cenários da GK-120.

## Endpoint

`POST /carrinho/itens`

Cabeçalhos: `Authorization: Bearer <token da sessão>` e
`Content-Type: application/json`. O front usa o token do login existente; não
inclua credenciais de banco ou o segredo de assinatura JWT no navegador.

Corpo de exemplo:

```json
{ "jogo_id": 19, "quantidade": 2 }
```

`jogo_id` é um inteiro positivo até o limite de bigint do PostgreSQL.
`quantidade` é um inteiro de 1 a 2.147.483.647, opcional, com padrão 1. Strings,
booleanos, decimais e campos adicionais recebem HTTP 422. O identificador usado
precisa existir no ambiente; os valores deste exemplo são ilustrativos.

Sucesso: **HTTP 200** tanto ao criar o item quanto ao incrementar o existente.

```json
{
  "carrinho_id": 4,
  "jogo_id": 19,
  "nome": "Jogo de demonstração",
  "quantidade": 2,
  "preco_unitario": "19.90",
  "subtotal": "39.80"
}
```

O retorno contém somente o item afetado. `quantidade` é a quantidade **final** no
carrinho: enviar novamente quantidade 2 soma duas unidades ao mesmo item. O preço
vem do catálogo no momento da operação; subtotal e preço são strings decimais
para preservar centavos. Esta operação não fixa preço para um pedido futuro.

| HTTP | `detail`                                                             | Ação esperada do consumidor                                                       |
| ---- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 401  | Não foi possível autenticar. Entre novamente.                        | Solicitar login; token ausente, inválido, expirado ou usuário inativo.            |
| 403  | O carrinho é exclusivo de clientes.                                  | Não oferecer compra com perfil administrador.                                     |
| 403  | Sua idade não permite adicionar este jogo ao carrinho.               | Mostrar o motivo; idade vem da data de nascimento cadastrada.                     |
| 404  | Jogo não encontrado.                                                 | Jogo inexistente ou inativo, com resposta uniforme.                               |
| 409  | Estoque insuficiente para a quantidade solicitada.                   | Informar que a quantidade final excederia o estoque, inclusive ao repetir o item. |
| 422  | Erro de validação do FastAPI                                         | Corrigir a entrada; nenhuma adição é executada.                                   |
| 503  | Carrinho temporariamente indisponível. Tente novamente em instantes. | Exibir indisponibilidade; não repetir automaticamente o POST.                     |

Consulte `/docs` ou `/openapi.json` em desenvolvimento para o contrato completo.
A idade é calculada em anos completos na data UTC do servidor. Classificação
`L` não impõe idade mínima; nascidos em 29/02 completam anos em 01/03 nos anos
não bissextos. O jogo esgotado não é adicionável. Jogo inativo não expõe dados.

## Persistência e concorrência

A migração `0003_carrinho.sql` implementa a parte do DER v1.0 referente a:

- `vendas.carrinhos`: um carrinho persistente por `usuario_id`, com índice único.
- `vendas.itens_carrinho`: PK `(carrinho_id, jogo_id)` e quantidade maior que zero.
- Exclusão do carrinho remove seus itens por FK com cascade. A FK do jogo possui
  índice próprio; as consultas de itens por carrinho usam a PK composta.
- O papel existente `gamekeys_equipe` recebe DML e acesso às sequências desse
  schema, preservando a separação entre uso da API e mudanças de estrutura.

Cada adição executa uma transação curta. O UPSERT de `carrinhos` cria/obtém e
bloqueia apenas o carrinho do cliente, inclusive na primeira criação concorrente.
O jogo é consultado pela PK com `FOR SHARE`: clientes distintos podem ler o mesmo
jogo simultaneamente, enquanto uma alteração de estoque aguarda essa leitura
curta terminar. Um UPSERT protegido soma a quantidade somente se o acumulado
couber no estoque. Em caso de recusa, a transação desfaz inclusive a criação ou
atualização do carrinho.

O número de consultas não cresce com os itens já presentes: há configuração dos
limites da transação, UPSERT do carrinho, leitura do jogo e UPSERT do item. Não há
listagem completa nem consulta por item a cada adição. A operação usa o pool
existente, sem estado de carrinho ou bloqueio global em memória; assim, funciona
com múltiplos processos/instâncias da API. A capacidade do pool deve ser
dimensionada considerando a quantidade de instâncias, pois o limite atual de
cinco conexões é por processo, não um limite global do serviço.

`lock_timeout` de 2 segundos e `statement_timeout` de 5 segundos são locais à
transação, compatíveis com o pooler do Neon. Exceder o limite retorna HTTP 503 e
desfaz a operação, sem deixar o pool ocupado indefinidamente. São limites
operacionais iniciais; não constituem medição de capacidade de produção.

**Adicionar não reserva nem decrementa estoque.** Dois clientes podem ter o mesmo
último exemplar em seus carrinhos. A disputa pela chave ocorre na GK-15/GK-46,
que deve revalidar os itens e o estoque dentro da própria transação. Esta entrega
não cria pedidos, tabelas de chaves ou garantia de compra.

O POST é incremental e não é idempotente. Se a resposta se perder depois de um
commit, repetir a requisição pode somar novamente. Desabilite cliques repetidos
enquanto houver uma requisição pendente e evite retentativa automática. Uma
chave de idempotência é uma evolução possível, fora deste contrato inicial.

## Continuação da GK-12 pelo Rodrigo

1. Usar o cliente autenticado em todas as consultas, sem aceitar `usuario_id` do
   navegador. A chave do item é **carrinho + jogo**, sem ID artificial adicional.
2. Reutilizar `app.servicos.carrinho.bloquear_carrinho(conexao, usuario_id)`
   **dentro de uma transação externa** ao alterar/remover itens. O bloqueio só é
   útil enquanto essa transação estiver aberta.
3. Manter a mesma ordem de bloqueios em todas as operações: carrinho, jogos por
   ID e, quando houver reserva, chaves. Evitar ordens inversas entre operações.
4. Revalidar o estoque e calcular dinheiro com `Decimal`/`numeric`. Para a futura
   consulta do carrinho, buscar itens e preços em conjunto, evitando N+1.
5. Não reaproveitar cegamente a soma incremental para o endpoint de alterar:
   nessa operação a quantidade solicitada substitui a atual.

Consulta, alteração e remoção do carrinho serão implementadas pela GK-12. Rotas
como `GET /carrinho`, `PATCH /carrinho/itens/{jogo_id}` e
`DELETE /carrinho/itens/{jogo_id}` são propostas para alinhamento, não endpoints
entregues nesta subtarefa.

## Migração e testes

Aplicar com o responsável pelo banco e com o ambiente correto configurado:

```powershell
cd backend
.venv\Scripts\python.exe -m app.migrar
```

No Neon, isso precisa da conexão direta e das permissões de migração. A API não
cria tabelas ao receber uma requisição e o usuário da equipe não tem DDL. O código
deve ser publicado com a migração aplicada no ambiente antes de usar a nova rota.
Esta implementação prepara a migração; sua validação não a executa no Neon.

Com `TEST_DATABASE_URL` apontando para um PostgreSQL **local isolado** chamado
`gamekeys_teste`, execute:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest tests/test_carrinho.py tests/test_carrinho_banco.py -v
.venv\Scripts\python.exe -m pytest -v
```

A fixture recusa hosts remotos antes de recriar schemas e prepara no servidor
local o papel sem login usado para testar as permissões. O ambiente de teste
precisa permitir migração e preparação desse papel (o PostgreSQL local/CI do
projeto fornece o usuário administrador para essa finalidade).

Os testes exercitam autenticação real, isolamento de carrinhos, estoque,
classificação, centavos, rollback, limites de entrada, permissões do papel da API,
disputa na primeira criação e timeout. Em 20 adições simultâneas de um único
cliente a um jogo com estoque 7, o esperado é 7 sucessos, 13 recusas e uma linha
com quantidade 7. Esse cenário valida a concorrência de **adição ao carrinho**;
o teste de 20 compras por 100 rodadas do driver GK-72 continua sendo uma
verificação separada da reserva.
