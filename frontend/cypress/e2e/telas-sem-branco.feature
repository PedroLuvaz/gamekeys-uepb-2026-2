# language: pt
@US-48 @GK-48 @GK-77 @R2 @regressao
Funcionalidade: Nenhuma tela fica em branco
  Além de carregando, lista vazia e erro de conexão (cobertos nos cenários de
  catálogo, ficha, carrinho e pedido), uma falha inesperada ao desenhar a tela
  também precisa mostrar uma saída ao cliente.

  @excecao
  Cenário: Falha inesperada ao desenhar a tela mostra uma saída
    Dado que o catálogo responde, mas a tela falha ao formatar os preços
    Quando abro o catálogo com a falha de desenho
    Então vejo o aviso de falha inesperada com as opções de recarregar e voltar ao catálogo
    E o menu principal continua na tela

  @excecao
  Cenário: Voltar ao catálogo depois da falha restaura a navegação
    Dado que o catálogo responde, mas a tela falha ao formatar os preços
    Quando abro o catálogo com a falha de desenho
    E escolho voltar ao catálogo pelo aviso de falha
    Então volto a ver os cartões do catálogo
