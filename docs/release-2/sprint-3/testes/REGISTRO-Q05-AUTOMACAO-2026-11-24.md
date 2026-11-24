# Q-05 — preparo local e ensaio automatizado — 24/11/2026

Este registro separa o ensaio técnico da avaliação de usabilidade com pessoas. O
[Protocolo oficial da Sprint 3](https://docs.google.com/spreadsheets/d/1Dyd0CsbbBjptbA_l8vQDX28BNNL9vCR0KZZ_4YN7PGw/edit#gid=533534898)
prevê compra completa: encontrar um jogo, adicioná-lo ao carrinho, finalizar o
pedido, confirmar o pagamento simulado e visualizar a chave. O XLSX antigo de
catálogo/carrinho é complementar e não substitui esse protocolo.

## Ambiente e isolamento

- Ensaio executado localmente na branch `docs/GK-144-registro-qa-r2`, no
  commit `3206487`, sem alterações de código de produção durante os testes.
- PostgreSQL `postgres:18-alpine` em contêiner descartável
  `gamekeys-q05-20261124`, ligado somente a `127.0.0.1:55440`, banco
  `gamekeys_teste`. Nome, estado `healthy`, porta, banco e conexão de leitura
  foram conferidos antes das migrações.
- API local em `127.0.0.1:8001`; Vite em `127.0.0.1:5173`, com proxy `/api`
  somente para a API local. A rota `/api/saude/banco` confirmou
  `gamekeys_teste`. A API já existente na porta 8000 não foi utilizada.
- Migrações 0001–0007 e carga de demonstração: 23 jogos ativos, 770 chaves
  **fictícias** disponíveis antes das compras. Cinco contas fictícias de
  cliente foram criadas por API no banco novo; cada teste usou uma conta e
  uma sessão do navegador própria. Não houve transação na loja publicada,
  Neon, banco compartilhado ou chaves reais.
- O contêiner foi recriado entre uma tentativa inicial e a rodada final. A
  primeira tentativa ficou arquivada; seus dados não foram misturados aos
  cinco clientes da rodada final.

## Testes automatizados — cinco sessões independentes

O Cypress/Electron, em viewport de 1000 × 660 px, percorreu a interface do
catálogo ao pedido entregue. Em cada sessão, conferiu jogo disponível, nome,
preço e rótulo acessível do link de detalhes; botão de adição, confirmação de
carrinho e navegação; finalização e estado `Aguardando pagamento` sem chave
visível; aviso de pagamento simulado sem cobrança; e estado `Entregue` com
mensagem de sucesso e código prefixado `GK-DEMO-SEM-VALOR-`.

Os tempos abaixo são **tempos de automação**, medidos do início da visita ao
catálogo, após o login, até a chave ficar visível. Não incluem criação da
conta, login nem a captura final. São muito diferentes do tempo que uma
pessoa levaria e **não** entram na meta humana de 300 s.

| Sessão automática | Tempo do fluxo | Resultado | Falha controlada e recuperação                                                                 |
| ----------------- | -------------: | --------- | ---------------------------------------------------------------------------------------------- |
| A01               |        1,365 s | Passou    | Sem falha injetada                                                                             |
| A02               |        2,904 s | Passou    | Sem falha injetada                                                                             |
| A03               |        1,208 s | Passou    | GET do catálogo recebeu 503; mensagem e “Tentar novamente” levaram à lista                     |
| A04               |        0,988 s | Passou    | Primeiro POST de pagamento recebeu 503; mensagem orientou nova tentativa, que entregou a chave |
| A05               |        0,653 s | Passou    | Sem falha injetada                                                                             |

**Resultado da rodada final: 5/5 fluxos automatizados passaram.** O JUnit
registrou cinco testes, zero falhas e zero pulados. A leitura final do banco
local encontrou cinco contas Q-05, cinco pedidos `entregue`, cinco pagamentos
`aprovado`, cinco clientes distintos, cinco chaves vendidas e cinco chaves
distintas vinculadas aos pedidos: um pedido por conta.

O ensaio visual suplementar de erro e recuperação do catálogo passou **1/1**.
Ele não representa uma sexta sessão nem criou conta ou pedido. Na primeira
tentativa da suíte principal, **4/5** passaram: A03 parou antes da compra
porque o padrão de interceptação do teste não correspondeu à URL com
`?pagina=1`. A captura mostra o catálogo carregado, sem defeito demonstrado
no produto. O padrão foi corrigido; a rodada final ocorreu em banco novo.
O Cypress avisou que não conseguiu mover resultados de captura anteriores
para a lixeira do Windows; as capturas foram copiadas para pastas separadas.

### Observações técnicas e evidências locais

- Os rótulos “Adicionar ao carrinho”, “Finalizar compra” e “Confirmar
  pagamento”, a disponibilidade, o preço e a paginação ficaram visíveis no
  catálogo e no fluxo local. As cinco navegações chegaram ao pedido entregue.
- A falha de catálogo apresentou título, explicação e botão “Tentar
  novamente”; o diagnóstico visual registrou a página inteira e o catálogo
  recuperado. A falha simulada no pagamento manteve o pedido pendente,
  mostrou a mensagem “Tente novamente” e permitiu confirmar depois.
- Nas capturas inspecionadas em desktop não apareceu tela em branco,
  sobreposição evidente nem bloqueio de navegação. Não houve inspeção mobile,
  navegação só por teclado ou avaliação com tecnologia assistiva nesta rodada.
  Automação não mede se pessoas compreendem os botões ou encontram jogos com
  facilidade.
- As capturas finais exibem **códigos fictícios de teste** e permanecem em
  diretórios ignorados pelo Git; não integram o PR #71. Nenhum e-mail, senha,
  token ou código completo foi transcrito neste relato.

Evidências locais, todas ignoradas pelo Git e não incluídas no PR:

| Evidência                                                   | Caminho relativo à raiz do repositório                                                                                          |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Tempos e status da rodada final                             | `frontend/cypress/reports/q05-2026-11-24-sessoes.json`                                                                          |
| JUnit final 5/5                                             | `frontend/cypress/reports/q05-2026-11-24-752e6c9a1e78027efed6f8f8e13f154d.xml`                                                  |
| JUnit visual 1/1                                            | `frontend/cypress/reports/q05-2026-11-24-visual-*.xml`                                                                          |
| JUnit inicial 4/5                                           | `frontend/cypress/reports/q05-2026-11-24-a979f8dd5b71d4363d2174e51cdb5fd1.xml`                                                  |
| Cinco entregas, três capturas de erro e catálogo recuperado | `frontend/cypress/reports/q05-rodada-final-capturas/`                                                                           |
| Resultado inicial 4/5 e capturas                            | `frontend/cypress/reports/q05-2026-11-24-primeira-tentativa.json` e `frontend/cypress/reports/q05-primeira-tentativa-capturas/` |

## Testes de usabilidade com participantes reais — 0/5

Esta seção registra o estado **antes** da aplicação presencial. Os resultados posteriores de P01–P05 constam no [registro presencial de 24/11/2026](REGISTRO-Q05-PRESENCIAL-2026-11-24.md).

**Nenhum voluntário participou ainda.** Não há tempos humanos, opiniões,
taxa de sucesso ou feedback para preencher. Cinco automações aprovadas não
equivalem a cinco pessoas e não satisfazem a Q-05. A aplicação do protocolo
atual ainda requer a confirmação de Wagner (PO) quanto a ambiente e contas
de teste.

| Participante | Tempo humano | Quatro etapas sem ajuda? | Dificuldades observadas | Resultado     |
| ------------ | -----------: | ------------------------ | ----------------------- | ------------- |
| P01          |            — | —                        | —                       | Não executado |
| P02          |            — | —                        | —                       | Não executado |
| P03          |            — | —                        | —                       | Não executado |
| P04          |            — | —                        | —                       | Não executado |
| P05          |            — | —                        | —                       | Não executado |

### Roteiro para cinco voluntários

1. Confirmar com o PO o ambiente de teste. Preparar **cinco contas novas**,
   dados fictícios, pagamento simulado e chaves sem valor. Não usar Neon
   compartilhado nem a compra na loja publicada.
2. Identificar cada pessoa apenas como P01–P05. Em sessão separada, ler:
   “Conclua a compra de teste usando apenas o que vê na tela. Não darei
   instruções durante a tarefa.”
3. Iniciar o cronômetro antes de encontrar o jogo. Pedir as quatro etapas do
   protocolo: encontrar jogo, adicionar ao carrinho, finalizar pedido e
   confirmar pagamento simulado com visualização da chave. Parar na entrega
   ou aos **300 segundos**.
4. Registrar tempo real, conclusão das quatro etapas, ajuda recebida,
   dificuldades, erros e evidência anônima sem credenciais ou códigos. Se a
   entrega não estiver funcional, marcar como **não executado**.
5. Considerar sucesso individual apenas as quatro etapas **sem ajuda em até
   300 s**. A meta Q-05 é **ao menos 4/5 pessoas**. Consolidar resultados
   reais no Plano de Qualidade e na Review, sem preencher os campos antes das
   sessões.
