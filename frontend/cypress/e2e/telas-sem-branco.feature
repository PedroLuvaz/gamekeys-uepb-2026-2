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

  Cenário: Minha conta anuncia o carregamento em até 1 segundo
    Dado que a validação da minha conta demora
    Quando abro a página Minha conta
    Então vejo o aviso de carregamento da conta em até 1 segundo
    E depois vejo os dados da minha conta

  @excecao
  Cenário: Falha de conexão em Minha conta permite tentar de novo
    Dado que a conexão cai ao validar minha conta
    Quando abro a página Minha conta
    Então vejo o erro da conta com a opção de tentar novamente
    Quando a conexão da conta volta e tento novamente
    Então depois vejo os dados da minha conta

  @excecao
  Cenário: Resposta incompleta da conta não vira dados quebrados na tela
    Dado que o servidor devolve uma conta incompleta
    Quando abro a página Minha conta
    Então vejo o erro da conta com a mensagem "O servidor retornou dados de conta inválidos. Tente novamente."
    E a tela não mostra "undefined" nem "Invalid Date"

  @excecao
  Cenário: Tentar novamente no carrinho recupera os itens depois da falha
    Dado que a conexão cai ao abrir o carrinho
    Quando abro o carrinho para conferir os estados
    Então vejo o erro de conexão do carrinho
    Quando a conexão do carrinho volta e tento novamente
    Então vejo os itens do carrinho sem recarregar a página
