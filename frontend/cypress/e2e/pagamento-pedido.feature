# language: pt
@US-16 @GK-16 @GK-48 @R2 @regressao
Funcionalidade: Pagar o pedido e receber as chaves
  Como cliente autenticado
  Quero confirmar o pagamento simulado do meu pedido
  Para receber as chaves dos jogos que comprei

  @smoke
  Cenário: Pagamento entrega as chaves
    Dado que tenho um pedido aguardando pagamento
    Quando abro a página do pedido
    Então vejo o pedido aguardando pagamento com total de "R$ 39,80"
    E nenhuma chave aparece na tela
    Quando escolho pagar com cartão
    E confirmo o pagamento
    Então o pedido fica entregue e vejo 2 chaves
    E o pagamento foi enviado uma vez com o método "cartao"

  Cenário: Antes da entrega o código das chaves não aparece
    Dado que tenho um pedido aguardando pagamento
    Quando abro a página do pedido
    Então vejo o pedido aguardando pagamento com total de "R$ 39,80"
    E nenhuma chave aparece na tela

  Cenário: Pedido já entregue mostra as chaves sem pedir pagamento
    Dado que meu pedido já foi entregue
    Quando abro a página do pedido
    Então o pedido fica entregue e vejo 2 chaves
    E não há formulário de pagamento

  Cenário: Carregamento do pedido é anunciado
    Dado que a consulta do pedido demora
    Quando abro a página do pedido
    Então vejo o aviso de carregamento do pedido
    E vejo o pedido aguardando pagamento com total de "R$ 39,80"

  Cenário: Envio duplicado do pagamento é bloqueado
    Dado que a confirmação do pagamento demora
    Quando abro a página do pedido
    E confirmo o pagamento duas vezes seguidas
    Então a tela informa que está confirmando o pagamento
    E o pedido fica entregue e vejo 2 chaves
    E o pagamento foi enviado uma vez com o método "pix"

  @excecao
  Cenário: Falha ao carregar permite tentar novamente
    Dado que a conexão com o pedido está indisponível
    Quando abro a página do pedido
    Então vejo o erro do pedido com a opção de tentar novamente
    Quando a conexão volta e tento carregar o pedido de novo
    Então vejo o pedido aguardando pagamento com total de "R$ 39,80"

  @excecao
  Cenário: Pedido inexistente ou de outro cliente
    Dado que o pedido não existe para a minha conta
    Quando abro a página do pedido
    Então vejo que o pedido não foi encontrado

  @excecao
  Cenário: Pagamento recusado mantém o pedido e mostra o motivo
    Dado que o pedido não está mais aguardando pagamento no servidor
    Quando abro a página do pedido
    E confirmo o pagamento
    Então vejo a mensagem de pagamento "Este pedido não está aguardando pagamento."
    E nenhuma chave aparece na tela

  @excecao
  Cenário: Falha de conexão no pagamento permite repetir
    Dado que a conexão cai ao confirmar o pagamento
    Quando abro a página do pedido
    E confirmo o pagamento
    Então vejo a mensagem de pagamento "Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente."
    Quando a conexão volta
    E confirmo o pagamento
    Então o pedido fica entregue e vejo 2 chaves

  @excecao
  Cenário: Sessão expirada volta ao login e retorna ao pedido
    Dado que o servidor recusa a sessão ao consultar o pedido
    Quando abro a página do pedido
    Então vou ao login com retorno para o pedido

  @excecao
  Cenário: Pedido cancelado não oferece pagamento
    Dado que meu pedido foi cancelado
    Quando abro a página do pedido
    Então vejo que o pedido foi cancelado
    E não há formulário de pagamento

  @excecao
  Cenário: Resposta inválida do servidor não é mostrada como pedido
    Dado que o servidor devolve um pedido entregue sem chaves
    Quando abro a página do pedido
    Então vejo o erro do pedido com a opção de tentar novamente

  @excecao
  Cenário: Administrador não acessa pedidos
    Dado que estou usando uma conta de administrador no pedido
    Quando abro a página do pedido
    Então vejo que os pedidos são exclusivos de clientes

  @excecao
  Cenário: Visitante é levado ao login
    Quando abro a página do pedido sem sessão
    Então vou ao login com retorno para o pedido

  @mobile
  Cenário: Pedido cabe na tela do celular
    Dado que meu pedido já foi entregue
    E uso uma tela de 320 pixels no pedido
    Quando abro a página do pedido
    Então o pedido fica entregue e vejo 2 chaves
    E a página do pedido cabe na largura do celular
