# GK-48 e GK-77 — Telas nunca ficam em branco

Regra (RNF GK-48, driver DA-USA-I3-03 / GK-77): toda tela mostra **carregando**,
**lista vazia** ou **erro com opção de tentar de novo**, nunca uma página em branco.
Medida do driver: indicador de carregando em até 1 segundo e 100% das listagens com
os três estados.

Levantamento de 16/11/2026, feito sobre o código da `main` (commit `aa0fdbe`) e os
cenários Cypress que já existiam. Os dados dos cenários são simulados na rede, sem
acesso ao Neon.

## Matriz tela × estado

| Tela | Carregando | Vazio | Erro com "tentar de novo" | Cenários Cypress |
| --- | --- | --- | --- | --- |
| Catálogo | Sim | Sim (catálogo e página além da última) | Sim | `listagem-jogos.feature` |
| Ficha do jogo | Sim | Jogo inexistente ou inativo mostra "não encontrado" | Sim (503 e queda de rede) | `detalhe-jogo.feature` |
| Carrinho | Sim | Sim ("Seu carrinho está vazio") | Sim | `alterar-remover-carrinho.feature` |
| Pedido e pagamento | Sim | Pedido inexistente ou de outro cliente mostra "não encontrado" | Sim, na consulta e no pagamento | `pagamento-pedido.feature` |
| Minha conta | Sim ("Validando sua sessão…") | Não se aplica | Sim | só o caso de sessão expirada (`login.feature`) |
| Login e cadastro | Botão em "enviando" | Não se aplica | Sim (mensagens da Q-06) | `login.feature`, `cadastro.feature`, `q06-mensagens.feature` |
| Rota desconhecida | Não se aplica | "Página não encontrada" com saída | Não se aplica | sem cenário dedicado (conferido no código de `App.tsx`) |
| Falha inesperada ao desenhar qualquer tela | Não se aplica | Não se aplica | **Novo:** aviso com "Recarregar a página" e "Ir para o catálogo" | `telas-sem-branco.feature` |

A biblioteca de chaves e a lista de pedidos do cliente ainda não existem (Release 3).
Quando entrarem, precisam dos três estados e de uma linha nesta matriz.

## O que a GK-48 acrescentou

- **Limite de erro** (`frontend/src/LimiteDeErro.tsx`, usado em `App.tsx` em volta do
  conteúdo das rotas). Antes, qualquer exceção ao desenhar uma tela deixava a página
  inteira em branco. Agora o cliente vê "Algo deu errado nesta tela", com as opções de
  recarregar e de voltar ao catálogo, o menu e o rodapé continuam na tela e a mensagem
  não mostra detalhe técnico (o erro vai só para o console do navegador). Navegar para
  outra rota limpa o aviso.
- O texto "Redirecionando para o login…" passou a ser anunciado a leitores de tela
  (`role="status"`).
- Dois cenários novos em `frontend/cypress/e2e/telas-sem-branco.feature`: o aviso
  aparece quando a formatação de preço lança erro e o link "Ir para o catálogo"
  restaura a navegação.

## Verificação feita em 16/11/2026

| Verificação | Resultado |
| --- | --- |
| `tsc --noEmit` (aplicação e Cypress) | Passou |
| Navegador (servidor de desenvolvimento), com a API simulada e a formatação de preço forçada a falhar | O aviso aparece no lugar do catálogo, com menu e rodapé; ir para "Criar conta" limpa o aviso; com a formatação restaurada, o catálogo volta com 3 cartões; o erro é registrado só no console |
| Cenários Cypress novos e regressão (`pnpm test:e2e`) | **Não executados nesta máquina:** o binário do Cypress não está instalado. Rodar no CI ou localmente com `npx cypress install` antes de pedir a revisão |

## Pendências

- **QA-R2-007** (total "R$ 0,00" ausente no carrinho vazio): decisão do PO na Planning
  de 17/11 — entra na GK-48 ou vira bug. Não foi alterado nada no carrinho.
- ~~Lacunas de teste automatizado: erro e carregamento de "Minha conta"; clique em
  "Tentar novamente" no carrinho.~~ Cobertas em 16/11/2026 (ver "Complemento de 16/11").
- Teste manual do driver (rede lenta e API desligada nas ferramentas do navegador): a
  executar pelo QA em cada tela de compra depois da GK-14 e da GK-13, para preencher o
  campo "Resultado obtido" da GK-77.

## Como reproduzir à mão

1. Abra o catálogo, o carrinho e um pedido com as ferramentas do navegador em "Rede →
   Lenta (3G)": o indicador de carregamento aparece de imediato.
2. Desligue a API (ou ponha a aba em "Offline") e recarregue: cada tela mostra a
   mensagem de erro e o botão de tentar de novo.
3. Com a API de volta, clique em "Tentar novamente": o conteúdo reaparece sem recarregar
   a página.

## Complemento de 16/11/2026

Fecha as duas lacunas de teste do levantamento e um defeito achado ao cobri-las.

- **Defeito:** se `/auth/me` respondesse 200 com um corpo incompleto, "Minha conta" mostrava
  "Olá," sem nome e "Invalid Date" no lugar da data. Agora `consultarUsuario`
  (`frontend/src/api.ts`) confere o corpo e, se faltar algum campo, a tela mostra "O servidor
  retornou dados de conta inválidos. Tente novamente." com o botão de tentar de novo.
- **Cenários novos** em `frontend/cypress/e2e/telas-sem-branco.feature`:
  carregamento de "Minha conta"; falha de conexão e "Tentar novamente" em "Minha conta";
  resposta incompleta da conta; "Tentar novamente" no carrinho recuperando os itens sem
  recarregar a página.
- Suíte de tela completa rodada localmente contra o build: 117 cenários, 117 passando.
