# language: pt
@US-11 @GK-11 @GK-119 @GK-120 @R2 @regressao
Funcionalidade: Adicionar um jogo ao carrinho pela ficha
  O cliente escolhe a quantidade e recebe o resultado confirmado pelo servidor.
  Esta suíte simula respostas; os cenários reais usam PostgreSQL local isolado.

  @smoke
  Cenário: Adicionar e repetir o mesmo jogo
    Dado que estou autenticado para adicionar um jogo disponível
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então a ficha confirma 1 unidade no carrinho e subtotal de 19,90
    Quando adiciono o jogo pela ficha
    Então a ficha confirma 2 unidades no carrinho e subtotal de 39,80

  Cenário: Escolher mais de uma unidade
    Dado que estou autenticado para adicionar um jogo disponível
    Quando abro a ficha para adicionar ao carrinho
    E escolho 3 unidades na ficha
    E adiciono o jogo pela ficha
    Então a ficha confirma 3 unidades no carrinho e subtotal de 59,70

  Cenário: Entrar e voltar ao jogo sem adicionar automaticamente
    Dado que estou sem sessão ao escolher um jogo
    Quando abro a ficha para adicionar ao carrinho
    E peço para entrar e adicionar ao carrinho
    E concluo o login para retornar à ficha
    Então retorno ao mesmo jogo e à página de origem sem adição automática
    Quando adiciono o jogo pela ficha
    Então a ficha confirma 1 unidade no carrinho e subtotal de 19,90

  @excecao
  Cenário: Recusar quantidade acima do estoque
    Dado que a adição é recusada por estoque insuficiente
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então vejo na ficha o motivo de estoque insuficiente

  @excecao
  Cenário: Recusar jogo com classificação acima da idade
    Dado que a adição é recusada por classificação etária
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então vejo na ficha o motivo de classificação etária

  Cenário: Impedir envio duplicado durante o carregamento
    Dado que a adição demora para ser confirmada
    Quando abro a ficha para adicionar ao carrinho
    E envio duas vezes o formulário imediatamente
    Então a ficha informa que está adicionando e bloqueia novo envio
    E a ficha confirma 1 unidade no carrinho e subtotal de 19,90
    E somente uma adição foi enviada

  @excecao
  Cenário: Renovar a sessão rejeitada pelo servidor
    Dado que o servidor rejeita minha sessão ao adicionar
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então vou ao login do carrinho com sessão expirada e sem token local
    Quando concluo o login para retornar à ficha
    Então somente uma adição foi enviada
    Quando adiciono o jogo pela ficha
    Então a ficha confirma 1 unidade no carrinho e subtotal de 19,90

  @excecao
  Cenário: Impedir adição de jogo esgotado
    Dado que o jogo escolhido está esgotado
    Quando abro a ficha para adicionar ao carrinho
    Então a ação de adicionar está desabilitada por esgotamento
    E nenhuma adição foi enviada

  @excecao
  Cenário: Informar indisponibilidade sem repetir a operação
    Dado que o serviço de carrinho está indisponível
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então vejo na ficha a mensagem de carrinho indisponível
    E somente uma adição foi enviada

  @excecao
  Cenário: Não confirmar sucesso quando a conexão falha
    Dado que a conexão da ficha falha ao adicionar ao carrinho
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então sou informado de que não foi possível confirmar a adição
    E somente uma adição foi enviada

  @mobile @smoke
  Cenário: Adicionar pelo celular
    Dado que estou autenticado para adicionar um jogo disponível
    E uso uma tela de 320 pixels no detalhe
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então a ficha confirma 1 unidade no carrinho e subtotal de 19,90
    E a ficha do jogo cabe na largura do celular

  @excecao
  Cenário: Não oferecer compra na conta de administrador
    Dado que estou usando uma conta de administrador na ficha
    Quando abro a ficha para adicionar ao carrinho
    Então vejo que o carrinho é exclusivo de clientes
    E nenhuma adição foi enviada

  @excecao
  Cenário: Recusar quantidade inválida antes de enviar
    Dado que estou autenticado para adicionar um jogo disponível
    Quando abro a ficha para adicionar ao carrinho
    E escolho 0 unidades na ficha
    E adiciono o jogo pela ficha
    Então a quantidade da ficha é inválida
    E nenhuma adição foi enviada

  @excecao
  Cenário: Ignorar endereço externo informado como retorno do login
    Dado que estou sem sessão ao escolher um jogo
    Quando abro o login com um retorno externo
    E concluo o login para retornar à ficha
    Então o login mantém a navegação dentro do GameKeys

  Cenário: Preservar centavos em um subtotal grande
    Dado que a adição retorna um subtotal acima do limite seguro de ponto flutuante
    Quando abro a ficha para adicionar ao carrinho
    E escolho 2147483647 unidades na ficha
    E adiciono o jogo pela ficha
    Então vejo todos os centavos do subtotal grande

  @excecao
  Cenário: Não confirmar uma resposta de sucesso incompleta
    Dado que o carrinho retorna uma confirmação incompleta
    Quando abro a ficha para adicionar ao carrinho
    E adiciono o jogo pela ficha
    Então sou informado de que não foi possível confirmar a adição
    E somente uma adição foi enviada
