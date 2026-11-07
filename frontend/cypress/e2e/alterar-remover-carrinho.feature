# language: pt
@US-12 @GK-12 @R2 @regressao
Funcionalidade: Alterar e remover itens do carrinho
  Como cliente autenticado
  Quero revisar quantidades e remover jogos
  Para manter no carrinho somente o que pretendo comprar

  Cenário: Aumentar e diminuir recalcula subtotal e total
    Dado que meu carrinho tem uma unidade de um jogo
    Quando abro a página do carrinho da GK-12
    Então vejo uma unidade e total de "R$ 19,90"
    Quando aumento a quantidade do item
    Então vejo duas unidades, subtotal e total de "R$ 39,80"
    Quando diminuo a quantidade do item
    Então vejo uma unidade e total de "R$ 19,90"

  Cenário: Remover o último jogo deixa o carrinho vazio
    Dado que meu carrinho tem uma unidade de um jogo
    Quando abro a página do carrinho da GK-12
    E removo o item do carrinho
    Então vejo que meu carrinho está vazio

  Cenário: Estoque insuficiente preserva a quantidade anterior
    Dado que o estoque recusa o aumento do item
    Quando abro a página do carrinho da GK-12
    E aumento a quantidade do item
    Então vejo a mensagem de estoque insuficiente no carrinho
    E vejo uma unidade e total de "R$ 19,90"

  Cenário: Falha de conexão permite tentar novamente
    Dado que a conexão com o carrinho está indisponível
    Quando abro a página do carrinho da GK-12
    Então vejo o erro de conexão e a ação de tentar novamente

  Cenário: Sessão expirada volta ao login
    Dado que o servidor recusa a sessão do carrinho
    Quando abro a página do carrinho da GK-12
    Então sou direcionado ao login para retornar ao carrinho

  Cenário: Carregamento é anunciado
    Dado que a consulta do carrinho demora
    Quando abro a página do carrinho da GK-12
    Então vejo o carregamento do carrinho
    E a consulta do carrinho pode terminar
