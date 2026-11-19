# GK-14 — Finalizar compra

Implementação e validação local em 19/11/2026, na branch
`feature/GK-14-finalizar-compra`, criada da `origin/main` em `2fe6a7e`.
Registro da validação local revisada por Wagner, que autorizou o commit e a
abertura do PR em 19/11/2026. As evidências do CI ficam vinculadas ao último
commit na seção **Evidências do pipeline** do PR.

## Entrega e integração

O botão **Finalizar compra**, em `/carrinho`, passa a chamar
`POST /pedidos/reservas` e abrir `/pedidos/{id}` para o pagamento simulado.
A reserva transacional, o preço persistido, a consulta e o pagamento já existentes
na main são reutilizados. A GK-14 acrescenta a integração visual e sua recuperação
segura; não duplica serviços de reserva nem altera o schema.

| Critério da história | Evidência automatizada |
| --- | --- |
| Carrinho com itens cria pedido aguardando pagamento com preço gravado | navegador chama API real; banco confirma um pedido, carrinho vazio e uma chave reservada; tela abre o pedido sem revelar código |
| Alterar o catálogo não muda o pedido | jogo fictício muda de R$ 19,90 para R$ 70,00; recarga do pedido e pagamento permanecem em R$ 19,90 |
| Carrinho vazio é recusado | tela não oferece finalização; chamada autenticada direta recebe 409 e não cria pedido |

## Segurança da operação

- O navegador envia somente um UUID e o Bearer token. Cliente, jogos, quantidades
  e preços são determinados no servidor; payload com valor ou comprador extras
  recebe 422. Não há credenciais de banco na interface.
- Um bloqueio imediato impede dois envios no mesmo evento e impede finalizar
  durante alteração do carrinho. Enquanto a finalização aguarda confirmação,
  quantidade e remoção ficam bloqueadas.
- O UUID é persistido **antes** do POST, em `sessionStorage`, separado pelo ID do
  cliente. Falha de gravação ou UUID corrompido bloqueia o envio.
- Timeout de 15 segundos, falha de rede, 5xx ou resposta de sucesso inválida
  conservam o UUID e oferecem **Verificar finalização**. Recarregar a aba não
  dispara POST automaticamente. A repetição só ocorre por ação do cliente.
- A recuperação funciona mesmo com carrinho esvaziado e não apaga um novo
  carrinho preenchido após a compra. O teste real trunca a primeira confirmação
  depois do commit e confirma um único pedido e uma única chave reservada.
- A sessão expirada retorna ao login preservando a operação. Uma operação de
  outro cliente não é reutilizada. Consulta e pagamento de pedido alheio retornam
  404 na API real.
- Recusas de negócio 403, 404, 409 e 422 liberam a correção do carrinho após
  atualização. Uma confirmação bem-sucedida remove a pendência e usa o ID validado
  da resposta para a navegação interna.
- A reserva existente mantém autenticação, checagem de perfil/idade, transação,
  bloqueios de concorrência, rollback e limites de 100 jogos/1.000 unidades.
  Códigos de ativação só aparecem após o pagamento simulado concluir a entrega.
- A inspeção visual em 320 pixels identificou uma capa excedendo a coluna do
  carrinho. A largura foi limitada à coluna e telas de até 400 pixels empilham
  capa e dados. O cenário mobile confere também que a capa não se sobrepõe aos
  dados do jogo e que esses dados não ficam cortados.

A persistência é da aba atual, não uma garantia de recuperação após seu fechamento,
limpeza do armazenamento ou troca de dispositivo. A tela de histórico de pedidos
entre dispositivos não faz parte desta alteração.

## Testes e isolamento

Arquivos acrescentados:

- `frontend/cypress/e2e/checkout.feature`: 18 cenários Gherkin, incluindo timeout,
  rede, recusas, clique duplo, armazenamento indisponível, sessão expirada,
  recarga, identificação por cliente e celular de 320 pixels.
- `frontend/cypress/support/step_definitions/checkout.ts`: respostas controladas
  para os cenários de interface; toda solicitação deve conter apenas o UUID.
- `frontend/cypress/integracao/checkout-real.cy.ts`: 3 testes com login, interface,
  API e PostgreSQL reais; inclui preço congelado, pagamento, recuperação após
  commit e isolamento entre clientes.
- `backend/qa/gk14_checkout.py`: prepara dados fictícios identificados por UUID,
  cria três chaves sem valor e um administrador inativo, confere os efeitos no
  banco e remove somente os registros dessa fixture ao final de cada teste.

Na conferência final, o cenário antigo de rede da GK-12 mostrou uma espera
intermitente causada pelas retentativas automáticas de GET do Chromium após
`forceNetworkError`. Sua simulação passou a rejeitar o `fetch` da consulta do
carrinho, como já ocorre em outros cenários do projeto, preservando a verificação
da mensagem de erro e da ação de tentar novamente. A aplicação não ganhou uma
nova regra de rede por esse ajuste do teste.

O helper e o pytest recusam hosts remotos e banco diferente de `gamekeys_teste`.
Nesta verificação foi usado exclusivamente PostgreSQL local em
`127.0.0.1:55435/gamekeys_teste`. `PYTHON_DOTENV_DISABLED=1` e as três variáveis
`DATABASE_URL`, `DATABASE_URL_UNPOOLED` e `TEST_DATABASE_URL` foram definidas
explicitamente para esse alvo. A API de teste usou segredo JWT fictício.
Nenhuma migração, teste, reserva ou pagamento desta validação foi executado no Neon.

Para reproduzir, prepare um PostgreSQL **local descartável** `gamekeys_teste` e
essas variáveis nos terminais da API e dos testes. Execute primeiro `pytest -q`
em `backend` (ele recria os schemas desse banco); depois inicie a API nesse mesmo
banco e o Vite. Não execute pytest enquanto houver testes de navegador usando a
mesma instância. Em `frontend`:

```sh
pnpm build
pnpm exec cypress run --spec cypress/e2e/checkout.feature
pnpm test:integracao --spec cypress/integracao/checkout-real.cy.ts
```

Os padrões existentes de specs incluem os arquivos novos automaticamente no CI.
O CI utiliza seu próprio PostgreSQL efêmero e guarda os relatórios de integração.

## Evidências locais

| Verificação | Resultado |
| --- | --- |
| Compilação TypeScript da aplicação e dos testes + build Vite | passou |
| Regressão completa do backend | 277 passaram; um aviso de depreciação existente de `TestClient` |
| Cenários Gherkin específicos da GK-14 | 18 passaram |
| Integração real específica da GK-14 | 3 passaram |
| Regressão completa de integração real | 17 passaram, incluindo os 3 novos testes da GK-14 |
| Regressão completa Gherkin da interface | 135 passaram, incluindo os 18 novos cenários da GK-14 |
| Conferência após o ajuste visual de 320 pixels | 40 passaram: checkout, carrinho e alteração/remoção; captura inspecionada visualmente |
| Ruff e formatação Python | passaram; 62 arquivos conferidos |
| Prettier e verificação do diff | passaram |

Após a integração real, uma consulta somente de leitura confirmou zero usuários
restantes dos namespaces das fixtures GK-11/GK-14. Os relatórios gerados ficam em
`backend/relatorios/` e `frontend/cypress/reports/`, ignorados pelo Git. As capturas
do navegador também são geradas em `frontend/cypress/screenshots/`.

## Etapas para concluir a DoD

O commit e a abertura do PR foram autorizados por Wagner. Permanecem CI verde,
registro dos links das execuções e dos relatórios no PR, revisão e aprovação de outro integrante,
integração via PR, validação do QA, homologação quando exigida e aceite do PO.
Os testes locais não substituem essas etapas. A história não está sendo concluída
no Jira por este registro.
