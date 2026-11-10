# Q-06 — Auditoria de mensagens claras

## Escopo e resultado

Auditoria executada em 10/11/2026 nos fluxos entregues de cadastro, autenticação e
carrinho, além do contrato da API de reserva. Foram definidos 44 casos rastreáveis:

- 35 casos de mensagens ou proteções observáveis na interface;
- 9 casos do endpoint de reserva, ainda sem tela de checkout entregue.

Resultado comprovado: **44/44 casos passaram (100%)**. Para a parte efetivamente exibida ao
usuário, o resultado é **35/35 (100%)**. A reserva ficou registrada separadamente como contrato
de API; não foi apresentada como validação de uma interface que ainda não existe.

O defeito encontrado era a possibilidade de o frontend exibir mensagens padrão do Pydantic em
inglês, como `Field required` e `Input should be`. A correção preserva a estrutura HTTP 422,
traduz as mensagens na API e mantém uma proteção equivalente no cliente. Os contratos de sucesso
e as regras de negócio não foram alterados.

## Matriz da interface

Na coluna Evidência, `Q-06` significa o arquivo
`frontend/cypress/e2e/q06-mensagens.feature`; `regressão` significa os cenários preexistentes da
suíte Cypress, todos incluídos na execução final de 96/96.

| ID | Cenário | Mensagem/resultado esperado | Obtido | Resultado | Evidência |
| --- | --- | --- | --- | --- | --- |
| Q06-UI-01 | cadastro sem campos | Informe um nome entre 2 e 120 caracteres. | igual ao esperado | passou | Q-06: Cadastro obrigatório ausente |
| Q06-UI-02 | e-mail de cadastro inválido | Informe um e-mail válido. | igual ao esperado | passou | Q-06: E-mail de cadastro inválido |
| Q06-UI-03 | senha curta | A senha deve ter pelo menos 8 caracteres. | igual ao esperado | passou | Q-06: Senha de cadastro curta |
| Q06-UI-04 | data de nascimento inválida | Informe uma data de nascimento válida. | igual ao esperado | passou | Q-06: Data de nascimento inválida |
| Q06-UI-05 | senha acima de 72 bytes | A senha deve ter no máximo 72 bytes. | igual ao esperado | passou | Q-06: Senha acima do limite |
| Q06-UI-06 | conta duplicada | Este e-mail já está em uso. | igual ao esperado | passou | Q-06: Conta duplicada |
| Q06-UI-07 | banco indisponível no cadastro | Não foi possível concluir o cadastro. Tente novamente mais tarde. | igual ao esperado | passou | Q-06: Cadastro temporariamente indisponível |
| Q06-UI-08 | rede interrompida no cadastro | Não foi possível falar com o servidor. Tente novamente. | igual ao esperado | passou | Q-06: Falha de rede no cadastro |
| Q06-UI-09 | erro sem `detail` no cadastro | Não foi possível concluir o cadastro. Tente novamente. | igual ao esperado | passou | Q-06: Erro sem detalhe no cadastro |
| Q06-UI-10 | e-mail inválido no login | Informe um e-mail válido. | igual ao esperado | passou | Q-06: E-mail inválido no login |
| Q06-UI-11 | senha ausente no login | Informe sua senha. | igual ao esperado | passou | Q-06: Senha ausente no login |
| Q06-UI-12 | credenciais incorretas | E-mail ou senha incorretos. | igual ao esperado | passou | Q-06: Login incorreto |
| Q06-UI-13 | autenticação indisponível | Autenticação temporariamente indisponível. | igual ao esperado | passou | Q-06: Autenticação indisponível |
| Q06-UI-14 | erro sem `detail` no login | Não foi possível entrar. Tente novamente. | igual ao esperado | passou | Q-06: Erro sem detalhe no login |
| Q06-UI-15 | token expirado | Sua sessão expirou. Entre novamente para continuar. | igual ao esperado; token removido | passou | Q-06: Token expirado |
| Q06-UI-16 | rede interrompida ao validar sessão | Não foi possível validar sua sessão. Tente novamente. | igual ao esperado | passou | Q-06: Falha de rede na sessão |
| Q06-UI-17 | erro sem `detail` ao validar sessão | Não foi possível validar sua sessão. | igual ao esperado | passou | Q-06: Erro sem detalhe na sessão |
| Q06-UI-18 | carrinho sem autenticação | exigir login e preservar retorno `/carrinho` | redirecionou para login com retorno | passou | Q-06: Carrinho sem autenticação |
| Q06-UI-19 | carrinho com perfil administrador | O carrinho é exclusivo de contas de cliente. | igual ao esperado | passou | Q-06: Carrinho recusado para administrador |
| Q06-UI-20 | quantidade zero, vazia ou fracionária | Informe uma quantidade inteira maior que zero. | igual ao esperado; sem envio | passou | Q-06 + regressão `carrinho.feature` |
| Q06-UI-21 | quantidade acima do estoque | Estoque insuficiente para a quantidade solicitada. | igual ao esperado | passou | Q-06: recusa 409 |
| Q06-UI-22 | jogo inexistente/inativo ao adicionar | Jogo não encontrado. | igual ao esperado | passou | Q-06: recusa 404 |
| Q06-UI-23 | restrição de idade | Sua idade não permite adicionar este jogo ao carrinho. | igual ao esperado | passou | Q-06: recusa 403 |
| Q06-UI-24 | item inexistente ao alterar | Item não encontrado no carrinho. | igual ao esperado | passou | Q-06: Item inexistente |
| Q06-UI-25 | erro sem `detail` ao alterar | Não foi possível atualizar o carrinho. | igual ao esperado | passou | Q-06: Erro sem detalhe ao alterar |
| Q06-UI-26 | consulta retorna contrato inválido | O servidor retornou um carrinho inválido. Tente novamente. | igual ao esperado | passou | Q-06: Resposta inválida |
| Q06-UI-27 | servidor indisponível no login | Não foi possível falar com o servidor. Tente novamente. | igual ao esperado | passou | Q-06: Servidor indisponível |
| Q06-UI-28 | Pydantic retorna `Field required` | texto em português do campo; inglês ausente | Informe um nome entre 2 e 120 caracteres. | passou | Q-06: Field required não chega à tela |
| Q06-UI-29 | Pydantic retorna `Input should be` | texto em português do campo; inglês ausente | Informe uma quantidade inteira maior que zero. | passou | Q-06: Input should be não chega à tela |
| Q06-UI-30 | rede interrompida ao adicionar | Não foi possível confirmar a adição. Evite repetir para não duplicar a quantidade. | igual ao esperado | passou | regressão `adicionar-carrinho.feature` |
| Q06-UI-31 | recusa sem `detail` ao adicionar | Não foi possível adicionar o jogo ao carrinho. | igual ao esperado | passou | regressão `adicionar-carrinho.feature` |
| Q06-UI-32 | sucesso com resposta incompleta | não confirmar; orientar a evitar repetição | igual ao esperado | passou | regressão `carrinho.feature` |
| Q06-UI-33 | rede interrompida ao consultar carrinho | Não foi possível conectar ao carrinho. Verifique sua conexão e tente novamente. | igual ao esperado; ação de tentar novamente | passou | regressão `alterar-remover-carrinho.feature` |
| Q06-UI-34 | serviço de carrinho indisponível | Carrinho temporariamente indisponível. Tente novamente em instantes. | igual ao esperado | passou | regressão `carrinho.feature` |
| Q06-UI-35 | validação estruturada com mensagem de domínio | retirar apenas o prefixo `Value error, ` | Quantidade fora do limite. | passou | regressão `adicionar-carrinho.feature` |

## Matriz da reserva — contrato de API, sem tela entregue

Estes casos foram exercitados no `TestClient` e fazem parte dos 243 testes da regressão backend.
Eles não contam como evidência de checkout por navegador.

| ID | Cenário | Mensagem esperada | Obtido | Resultado | Evidência |
| --- | --- | --- | --- | --- | --- |
| Q06-API-01 | token ausente, inválido ou expirado | Não foi possível autenticar. Entre novamente. | igual ao esperado | passou | `test_autenticacao.py` e `test_reservas.py` |
| Q06-API-02 | UUID de idempotência inválido | Informe um identificador de reserva válido. | igual ao esperado | passou | `test_mensagens_q06.py` |
| Q06-API-03 | perfil não cliente | A reserva é exclusiva de clientes. | igual ao esperado | passou | `test_reservas.py` |
| Q06-API-04 | restrição de idade | Sua idade não permite reservar um dos jogos. | igual ao esperado | passou | `test_reservas.py` |
| Q06-API-05 | jogo indisponível | Um dos jogos não está disponível. | igual ao esperado | passou | `test_reservas.py` |
| Q06-API-06 | estoque insuficiente | Estoque insuficiente para reservar todos os jogos. | igual ao esperado | passou | `test_reservas.py` |
| Q06-API-07 | carrinho vazio | O carrinho está vazio. | igual ao esperado | passou | `test_reservas.py` |
| Q06-API-08 | limite operacional/monetário | O pedido excede o limite de itens, unidades ou valor. | igual ao esperado | passou | `test_reservas.py` |
| Q06-API-09 | reserva indisponível | Reserva temporariamente indisponível. | igual ao esperado | passou | `test_reservas.py` |

## Execuções e ambiente

O `.env.local` foi conferido antes dos testes e aponta para o Neon. Por isso, as execuções
destrutivas usaram variáveis de processo apontando exclusivamente para o contêiner temporário
PostgreSQL 18, banco `gamekeys_teste`, em loopback na porta 5435. O contêiner foi removido após
a regressão. Nenhuma escrita foi feita no Neon.

| Comando | Ambiente | Resultado |
| --- | --- | --- |
| `ruff check .` | Python 3.12.14 | passou |
| `ruff format --check .` | Python 3.12.14 | 55 arquivos já formatados |
| `pytest tests/test_mensagens_q06.py tests/test_clientes.py tests/test_autenticacao.py tests/test_carrinho.py tests/test_reservas.py -q` | TestClient, sem banco compartilhado | 97 passaram em 2,77 s |
| `pytest -q` | PostgreSQL 18 local `gamekeys_teste` | 243 passaram em 44,43 s; 1 aviso de depreciação do TestClient |
| `pnpm build` | Node 24, Vite 8.3.5 | passou |
| `cypress run --spec cypress/e2e/q06-mensagens.feature` | Cypress 16.2.0, respostas controladas | 29/29 passaram em 19 s |
| `pnpm test:e2e` | Cypress 16.2.0, API simulada | 96/96 passaram em 1 min 7 s |

Os relatórios JUnit foram gerados em `frontend/cypress/reports/`. O aviso do backend é a
depreciação já conhecida do `TestClient`; o Cypress também avisou que o Electron 146 será
descontinuado como navegador de teste. Nenhum aviso alterou os resultados.

## Limites

- Respostas controladas do Cypress comprovam o texto e o comportamento da interface, não a
  disponibilidade de serviços externos.
- A regressão backend usou o PostgreSQL local isolado para os casos de persistência.
- A tela de checkout/reserva ainda não existe; por isso, as nove mensagens de reserva são
  evidência de API, não de apresentação ao usuário.
- O resultado não representa aceite do PO, conclusão da DoD ou autorização de merge.
