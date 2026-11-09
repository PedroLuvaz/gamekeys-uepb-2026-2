# GK-140 — Roteiro de smoke no ambiente publicado

## Objetivo e limite de segurança

Verificar se os fluxos públicos essenciais do GameKeys estão acessíveis em
`https://gamekeys-web.vercel.app/`, sem criar ou alterar dados no Neon compartilhado.

Este roteiro permite somente navegação anônima e requisições HTTP `GET`. Cadastro, login com
credenciais reais, inclusão ou alteração de carrinho, reserva, pedido, pagamento e exclusão ficam
fora desta execução. Nenhuma requisição `POST`, `PATCH`, `PUT` ou `DELETE` foi enviada.

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

Consultas GET reproduzíveis:

```powershell
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/saude'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/saude/banco'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/jogos?pagina=1'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/jogos?pagina=2'
Invoke-RestMethod -Method Get -Uri 'https://gamekeys-web.vercel.app/api/jogos/19'
```

## Verificações pendentes

As verificações abaixo não foram executadas e não devem ser consideradas aprovadas:

- login com credencial de homologação e expiração de sessão;
- cadastro, por gravar um cliente no Neon;
- inclusão, alteração e remoção de itens do carrinho;
- reserva e criação de pedido;
- checkout completo, pagamento e entrega de chave.

Elas exigem dados descartáveis previamente autorizados e uma estratégia de limpeza acordada. A
prova concorrente da GK-129 usa PostgreSQL local isolado e cobre a reserva real da GK-15, mas não
substitui esses fluxos publicados de ponta a ponta.

## Ligações

- [GK-140](https://pedrolucas0721.atlassian.net/browse/GK-140)
- [GK-116](https://pedrolucas0721.atlassian.net/browse/GK-116)
- [Execução consolidada da `main`](https://github.com/PedroLuvaz/gamekeys-uepb-2026-2/actions/runs/42617543511)
