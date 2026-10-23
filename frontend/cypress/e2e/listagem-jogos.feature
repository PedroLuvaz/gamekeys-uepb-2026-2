# language: pt
@GK-9 @R1 @regressao
Funcionalidade: Explorar o catálogo de jogos
  O visitante consulta jogos ativos e navega entre páginas e detalhes.
  Os dados destes cenários são simulados na rede, sem acesso ao Neon.

  @smoke
  Cenário: Navegar por 23 jogos sem repetir itens
    Dado que o catálogo responde com 23 jogos ativos
    Quando abro o catálogo
    Então vejo 20 cartões e os preços em reais
    Quando avanço para a próxima página
    Então vejo os 3 jogos restantes e o intervalo correto
    E posso voltar para a primeira página

  Cenário: Abrir um jogo esgotado e retornar à página de origem
    Dado que o catálogo responde com 23 jogos ativos
    Quando abro a segunda página do catálogo
    Então o jogo sem chaves aparece como esgotado
    Quando abro a ficha do jogo esgotado
    Então vejo os dados e a disponibilidade do jogo
    Quando volto ao catálogo
    Então vejo os 3 jogos restantes e o intervalo correto

  @excecao
  Cenário: Consultar um catálogo sem jogos
    Dado que o catálogo está vazio
    Quando abro o catálogo
    Então vejo uma mensagem de catálogo vazio

  @excecao
  Cenário: Recuperar a consulta depois de uma falha
    Dado que a primeira consulta ao catálogo falha
    Quando abro o catálogo
    Então vejo uma mensagem de falha e a opção de tentar novamente
    Quando tento novamente
    Então vejo 20 cartões e os preços em reais

  Cenário: Mostrar carregamento enquanto a consulta está em andamento
    Dado que a consulta ao catálogo demora para responder
    Quando abro o catálogo
    Então vejo o estado de carregamento antes dos cartões

  @excecao
  Cenário: Abrir uma página além da última
    Dado que o catálogo responde com 23 jogos ativos
    Quando abro a terceira página do catálogo
    Então posso retornar ao catálogo pela mensagem de página vazia

  @mobile @smoke
  Cenário: Explorar o catálogo no celular
    Dado que o catálogo responde com 23 jogos ativos
    E uso uma tela de celular
    Quando abro o catálogo
    Então vejo 20 cartões e os preços em reais
    E a página cabe na largura da tela

  @GK-10 @excecao
  Cenário: Acessar o endereço de um jogo não encontrado
    Dado que a consulta de detalhe não encontra o jogo
    Quando abro o endereço direto desse jogo
    Então vejo a mensagem de jogo não encontrado

  Cenário: Preservar a paginação no histórico do navegador
    Dado que o catálogo responde com 23 jogos ativos
    Quando abro o catálogo
    Então vejo 20 cartões e os preços em reais
    Quando avanço para a próxima página
    Então vejo os 3 jogos restantes e o intervalo correto
    Quando uso o voltar do navegador
    Então vejo 20 cartões e os preços em reais
    Quando uso o avançar do navegador
    Então vejo os 3 jogos restantes e o intervalo correto

  Cenário: Recarregar a segunda página pelo endereço
    Dado que o catálogo responde com 23 jogos ativos
    Quando abro a segunda página do catálogo
    Então vejo os 3 jogos restantes e o intervalo correto
    Quando recarrego a página
    Então vejo os 3 jogos restantes e o intervalo correto

  @excecao
  Cenário: Continuar exibindo o jogo quando a capa não carrega
    Dado que um jogo tem uma capa indisponível
    Quando abro o catálogo
    Então vejo a ilustração de apoio no lugar da capa com falha
    E vejo 20 cartões e os preços em reais
