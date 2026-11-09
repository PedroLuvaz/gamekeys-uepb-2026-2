# GK-140 — Roteiro de smoke no ambiente publicado

## Objetivo e limite de segurança

Verificar se os fluxos públicos essenciais do GameKeys estão acessíveis em
`https://gamekeys-web.vercel.app/`, sem criar ou alterar dados no Neon compartilhado.

Este roteiro permite somente navegação anônima e requisições HTTP `GET`. Cadastro, login com
credenciais reais, inclusão ou alteração de carrinho, reserva, pedido, pagamento e exclusão ficam
fora desta execução. Nenhuma requisição `POST`, `PATCH`, `PUT` ou `DELETE` foi enviada.

Na continuidade de 09/11/2026 houve autorização para usar conta fictícia e chaves de
demonstração. A execução autenticada, porém, continuou condicionada à existência prévia da conta
e a uma regra de limpeza das reservas. Como essas duas pré-condições não estavam definidas, as
operações que poderiam persistir dados permaneceram bloqueadas.

## Roteiro

| ID | Verificação segura | Resultado esperado | Evidência a registrar |
| --- | --- | --- | --- |
| GK140-SM-01 | Abrir a página inicial | catálogo renderiza e a navegação pública está visível | URL, título e captura/observação visual |
| GK140-SM-02 | Consultar `GET /api/saude` | HTTP 200 e estado `ok` | status e corpo da resposta |
| GK140-SM-03 | Consultar `GET /api/saude/banco` | HTTP 200, banco acessível e sem credenciais expostas | status e corpo da resposta |
| GK140-SM-04 | Navegar pelas páginas do catálogo | itens, paginação, preço e disponibilidade são exibidos | totais e itens observados |
| GK140-SM-05 | Abrir o detalhe de um jogo | dados do jogo e ação compatível com sessão anônima | título, preço, plataforma e CTA |
| GK140-SM-06 | Abrir login e cadastro sem enviar formulários | campos e ações são renderizados em português | URL, título e campos observados |
| GK140-SM-07 | Acessar o carrinho sem autenticação | redirecionamento para login preserva o retorno | URL final observada |
| GK140-SM-08 | Conferir o console durante a navegação | nenhum erro ou aviso de aplicação | contagem do console |

## Execução observada em 09/11/2026

Ambiente: Vercel publicado, navegador em sessão anônima e requisições GET pelo PowerShell.

| ID | Resultado efetivamente observado | Estado |
| --- | --- | --- |
| GK140-SM-01 | `GET /` respondeu HTTP 200; a página renderizou com título `Catálogo \| GameKeys`, menu Catálogo/Criar conta/Entrar e 20 jogos na primeira página | passou |
| GK140-SM-02 | `GET /api/saude` respondeu HTTP 200 com `{"status":"ok"}` | passou |
| GK140-SM-03 | `GET /api/saude/banco` respondeu HTTP 200 com banco `gamekeys` e PostgreSQL `18.6 (ac70818)`; nenhuma credencial foi exibida | passou |
| GK140-SM-04 | a API informou 23 jogos, 20 por página e 2 páginas; a segunda página exibiu os itens 21–23 e distinguiu jogo disponível de esgotado | passou |
| GK140-SM-05 | `/jogos/19?origem=1` exibiu `Asfalto Quente`, PC, Corrida, classificação 10 anos, preço R$ 159,90, disponibilidade e CTA `Entrar para adicionar ao carrinho` | passou |
| GK140-SM-06 | `/login` e `/cadastro` renderizaram títulos, campos e botões esperados; nenhum formulário foi enviado | passou |
| GK140-SM-07 | `/carrinho` redirecionou para `/login?retorno=%2Fcarrinho` | passou |
| GK140-SM-08 | não foram observados erros nem avisos no console durante o roteiro | passou |

## Continuidade dos fluxos autenticados em 09/11/2026

Ambiente: frontend `https://gamekeys-web.vercel.app/`, proxy `/api` do frontend e API
`https://gamekeys-api.vercel.app/`. O arquivo `frontend/vercel.json` direciona `/api/:caminho*`
para essa API; `GET /api/saude/banco` e `GET /saude/banco` responderam com o mesmo conteúdo.
Esta tabela preserva a primeira tentativa; as pré-condições superadas e o estado atual estão na
seção de finalização abaixo.

| Data | Ambiente | Caso | Resultado esperado | Resultado obtido | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| 09/11/2026 | Vercel publicado | GK140-AUTH-00 — acesso e roteamento | frontend, proxy e API respondem no ambiente esperado | frontend HTTP 200; saúde pelo proxy e pela API HTTP 200, com respostas idênticas; banco `gamekeys`, PostgreSQL 18.6 | respostas HTTP sanitizadas, sem URL de banco ou credencial | passou |
| 09/11/2026 | frontend publicado | GK140-AUTH-01 — login inválido | mensagem uniforme, sem criar sessão ou revelar se a conta existe | a interface exibiu `E-mail ou senha incorretos.` e permaneceu em `/login`; nenhum erro ou aviso foi observado no console | navegador, com credenciais fictícias inexistentes não registradas na evidência | passou |
| 09/11/2026 | proxy `/api` publicado | GK140-AUTH-02 — carrinho sem sessão | HTTP 401 antes de consultar ou alterar o carrinho | `GET /api/carrinho` respondeu HTTP 401 com a mensagem de autenticação prevista | status e corpo sanitizado da resposta | passou |
| 09/11/2026 | proxy `/api` publicado | GK140-AUTH-03 — reserva sem sessão | HTTP 401 antes de iniciar a transação ou persistir o UUID | `POST /api/pedidos/reservas` respondeu HTTP 401 com a mensagem de autenticação prevista | status e corpo sanitizado; UUID aleatório não registrado | passou |
| 09/11/2026 | frontend publicado | GK140-AUTH-04 — login válido | criar sessão para uma conta fictícia ativa já destinada à homologação | não executado: a carga de demonstração possui somente conta técnica inativa e não foi fornecida outra conta ativa | `backend/carga/demonstracao.sql` e contrato GK-15 | bloqueado por pré-condição |
| 09/11/2026 | frontend e API publicados | GK140-AUTH-05 — carrinho vazio autenticado | HTTP 200, nenhum item e total `0.00` | não executado: depende da conta fictícia ativa | contrato `GET /carrinho` | bloqueado por pré-condição |
| 09/11/2026 | frontend e API publicados | GK140-AUTH-06 — adicionar jogo | jogo autorizado entra com a quantidade solicitada | não executado: não foi indicado o jogo/chave reservado para homologação e não há conta ativa | contrato `POST /carrinho/itens` | bloqueado por pré-condição |
| 09/11/2026 | frontend e API publicados | GK140-AUTH-07 — aumentar quantidade | quantidade, subtotal e total aumentam após confirmação da API | não executado | contrato `PATCH /carrinho/itens/{jogo_id}` | bloqueado por pré-condição |
| 09/11/2026 | frontend e API publicados | GK140-AUTH-08 — diminuir quantidade | quantidade, subtotal e total diminuem após confirmação da API | não executado | contrato `PATCH /carrinho/itens/{jogo_id}` | bloqueado por pré-condição |
| 09/11/2026 | frontend e API publicados | GK140-AUTH-09 — quantidade acima do estoque | HTTP 409 e valores anteriores preservados | não executado | contrato do carrinho | bloqueado por pré-condição |
| 09/11/2026 | frontend e API publicados | GK140-AUTH-10 — remover item | item removido; último item deixa carrinho vazio e total `0.00` | não executado | contrato `DELETE /carrinho/itens/{jogo_id}` | bloqueado por pré-condição |
| 09/11/2026 | API publicada | GK140-AUTH-11 — reservar chave de demonstração | um pedido `aguardando_pagamento`, sem expor código da chave | não executado: a reserva não possui cancelamento, expiração ou limpeza publicada | contrato `POST /pedidos/reservas` | bloqueado por limpeza ausente |
| 09/11/2026 | API publicada | GK140-AUTH-12 — repetir o mesmo UUID | recuperar o mesmo pedido, sem novo pedido ou nova chave | não executado | contrato de idempotência da GK-15 | bloqueado por limpeza ausente |
| 09/11/2026 | API publicada | GK140-AUTH-13 — estado e carrinho após reserva | pedido `aguardando_pagamento` e carrinho vazio na mesma transação | não executado | contrato da GK-15 | bloqueado por limpeza ausente |

Nenhum cliente, carrinho, item, pedido ou reserva foi criado nesta continuidade. O e-mail
inexistente usado no teste negativo não foi cadastrado. A chamada anônima de reserva foi recusada
na autenticação e não persistiu o UUID.

## Finalização do carrinho autenticado em 09/11/2026

Ambiente: interface publicada no Vercel, API pelo proxy `/api` e PostgreSQL Neon de homologação.
Versão funcional: a `main` `29922ab` difere da referência homologada `51dc797` somente nos
documentos de QA. A estratégia de identificação e limpeza seguiu a
[evidência do Wagner na GK-15](https://pedrolucas0721.atlassian.net/browse/GK-15?focusedCommentId=10248):
namespace exclusivo, consultas restritas e exclusão somente pelos identificadores exatos.

| Data | Caso | Resultado esperado | Resultado obtido | Evidência | Estado |
| --- | --- | --- | --- | --- | --- |
| 09/11/2026 | GK140-AUTH-04 — cadastro e login válido | conta fictícia ativa, login e área protegida | conta exclusiva criada; login levou à área protegida como Cliente | nome `QA GK-140 1794233356537`; e-mail `qa.gk140.1794233356537.1a72dfb8@example.com`; senha e JWT omitidos | passou |
| 09/11/2026 | GK140-AUTH-05 — carrinho vazio autenticado | nenhum item e total `0.00` | a interface exibiu `Seu carrinho está vazio`; o total literal não é renderizado no estado vazio | observação visual da rota `/carrinho` | parcial: vazio comprovado; total não observável pela interface |
| 09/11/2026 | GK140-AUTH-06 — adicionar jogo | item com preço, quantidade e subtotal corretos | `Reino de Cristal`, 1 unidade, preço unitário e subtotal de R$ 129,90 | confirmação na ficha e listagem no carrinho | passou |
| 09/11/2026 | GK140-AUTH-07 — aumentar quantidade | quantidade 2 e valores recalculados | quantidade 2; subtotal e total R$ 259,80 | resposta confirmada pela interface | passou |
| 09/11/2026 | GK140-AUTH-08 — diminuir quantidade | voltar à quantidade 1 e aos valores iniciais | quantidade 1; subtotal e total R$ 129,90 | resposta confirmada pela interface | passou |
| 09/11/2026 | GK140-AUTH-09 — acima do estoque | recusa e preservação do valor anterior | após chegar sequencialmente a 12, a tentativa de 13 mostrou `Estoque insuficiente para a quantidade solicitada.`; quantidade permaneceu 12 e subtotal/total permaneceram R$ 1.558,80 | mensagem e valores visíveis após a recusa | passou |
| 09/11/2026 | GK140-AUTH-10 — remover último item | carrinho vazio e total `0.00` | a interface confirmou a remoção e exibiu o estado vazio; o resumo com o total deixa de ser renderizado | mensagem `Reino de Cristal foi removido do carrinho.` e estado vazio | parcial: remoção/vazio comprovados; total não observável pela interface |
| 09/11/2026 | GK140-AUTH-14 — recarregar o carrinho | estado vazio persiste no servidor | após recarregar `/carrinho`, a interface continuou vazia | nova carga autenticada da rota | passou |
| 09/11/2026 | GK140-AUTH-15 — logout e proteção | encerrar sessão e exigir novo login | `Sair` levou a `/login`; acessar `/carrinho` redirecionou para `/login?retorno=%2Fcarrinho` | URL e menu anônimo observados | passou |
| 09/11/2026 | GK140-AUTH-16 — limpeza restrita | remover somente os registros desta execução | pré-consulta encontrou usuário `12`, 1 carrinho vazio, 0 itens, 0 pedidos, 0 itens de pedido e 0 chaves; a transação removeu exatamente o carrinho e o usuário; verificação posterior retornou 0 resíduos | contagens sanitizadas antes/depois, sem URL, senha, JWT ou código de ativação | passou |

Não foram executados reserva, repetição de UUID, pagamento ou entrega de chave. A reserva
autenticada publicada já está coberta pelo comentário 10248 da GK-15 e não foi repetida.

Consultas GET reproduzíveis:

```powershell
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/saude'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/saude/banco'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/jogos?pagina=1'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/jogos?pagina=2'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/jogos/19'
```

## Pendências após a finalização

- O estado vazio não mostra o resumo, portanto o total literal `R$ 0,00` não foi observável pela
  interface. O carrinho vazio e sua persistência após recarga foram comprovados.
- GK140-AUTH-11 a GK140-AUTH-13 não foram repetidos nesta execução. A reserva autenticada foi
  executada por Wagner na GK-15; checkout visual, pagamento e entrega continuam fora do escopo.
- DoD e aceite de negócio não são inferidos deste roteiro.

## Problemas encontrados

Nenhum defeito dos critérios de aceite da GK-12 foi reproduzido. A ausência do total visível no
estado vazio limita a evidência solicitada, mas não contradiz os critérios registrados na GK-12,
que exigem recálculo ao alterar quantidade e recusa acima do estoque. Nenhum Bug foi aberto.

## Ligações

- [GK-140](https://pedrolucas0721.atlassian.net/browse/GK-140)
- [GK-116](https://pedrolucas0721.atlassian.net/browse/GK-116)
- [Execução consolidada da `main`](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/42617543511)
