# language: pt
@GK-11 @GK-119 @GK-119-UI @regressao
Funcionalidade: Adicionar um jogo ao carrinho pelo detalhe
  Como cliente, quero adicionar unidades ao meu carrinho e conhecer o resultado.
  A API e a sessão são simuladas, sem acesso ao banco compartilhado.

  Contexto:
    Dado que há um jogo disponível para adicionar ao carrinho

  @smoke
  Cenário: Enviar a quantidade e mostrar o total devolvido pelo servidor
    Dado que tenho uma sessão para adicionar ao carrinho
    E que o carrinho já contém 3 unidades deste jogo
    Quando abro o detalhe para adicionar ao carrinho
    E escolho 2 unidades para adicionar
    E adiciono o jogo ao carrinho
    Então o pedido do carrinho envia 2 unidades do jogo com o token da sessão
    E a confirmação do carrinho informa 5 unidades

  Cenário: Somar uma nova adição ao mesmo item
    Dado que tenho uma sessão para adicionar ao carrinho
    Quando abro o detalhe para adicionar ao carrinho
    Então a quantidade inicial do carrinho é 1
    Quando adiciono o jogo ao carrinho
    Então a confirmação do carrinho informa 1 unidade
    Quando adiciono o jogo ao carrinho
    Então a confirmação do carrinho informa 2 unidades
    E foram feitos 2 pedidos de adição ao carrinho

  @excecao
  Esquema do Cenário: Mostrar o motivo de uma recusa sem confirmar a adição
    Dado que tenho uma sessão para adicionar ao carrinho
    E que a adição ao carrinho é recusada com <status> e "<motivo>"
    Quando abro o detalhe para adicionar ao carrinho
    E adiciono o jogo ao carrinho
    Então o alerta do carrinho mostra "<motivo>"
    E foram feitos 1 pedidos de adição ao carrinho

    Exemplos:
      | status | motivo                                                                |
      | 409    | Estoque insuficiente para a quantidade solicitada.                     |
      | 403    | Sua idade não permite adicionar este jogo ao carrinho.                 |
      | 404    | Jogo não encontrado.                                                  |
      | 422    | Quantidade inválida.                                                  |
      | 503    | Carrinho temporariamente indisponível. Tente novamente em instantes.   |

  Cenário: Mostrar o detalhe de validação estruturado da API
    Dado que tenho uma sessão para adicionar ao carrinho
    E que a adição ao carrinho recebe um detalhe de validação estruturado
    Quando abro o detalhe para adicionar ao carrinho
    E adiciono o jogo ao carrinho
    Então o alerta do carrinho mostra "Quantidade fora do limite."

  Cenário: Usar uma mensagem genérica quando a recusa não contém detail
    Dado que tenho uma sessão para adicionar ao carrinho
    E que a adição ao carrinho recebe uma recusa sem detalhe
    Quando abro o detalhe para adicionar ao carrinho
    E adiciono o jogo ao carrinho
    Então o alerta do carrinho mostra "Não foi possível adicionar o jogo ao carrinho."

  Cenário: Convidar o visitante a entrar sem enviar pedidos
    Quando abro o detalhe para adicionar ao carrinho
    Então vejo o link para entrar e adicionar ao carrinho
    E foram feitos 0 pedidos de adição ao carrinho

  Cenário: Impedir a adição de um jogo esgotado
    Dado que tenho uma sessão para adicionar ao carrinho
    E que o jogo para adicionar ao carrinho está esgotado
    Quando abro o detalhe para adicionar ao carrinho
    Então a ação do carrinho está desabilitada como Esgotado
    E foram feitos 0 pedidos de adição ao carrinho

  Cenário: Expirar a sessão quando a adição retorna 401
    Dado que tenho uma sessão para adicionar ao carrinho
    E que a adição ao carrinho é recusada com 401 e "Não foi possível autenticar. Entre novamente."
    Quando abro o detalhe para adicionar ao carrinho
    E adiciono o jogo ao carrinho
    Então a adição redireciona ao login com a sessão expirada

  Cenário: Bloquear cliques e envios repetidos enquanto a adição está pendente
    Dado que tenho uma sessão para adicionar ao carrinho
    E que a API demora para adicionar ao carrinho
    Quando abro o detalhe para adicionar ao carrinho
    E adiciono o jogo ao carrinho
    Então a ação do carrinho informa progresso e impede novo envio
    Quando tento repetir o envio pendente do carrinho
    Então a confirmação do carrinho informa 1 unidade
    E foram feitos 1 pedidos de adição ao carrinho

  Cenário: Informar falha de rede sem repetir automaticamente o envio
    Dado que tenho uma sessão para adicionar ao carrinho
    E que a conexão falha ao adicionar ao carrinho
    Quando abro o detalhe para adicionar ao carrinho
    E adiciono o jogo ao carrinho
    Então o alerta do carrinho mostra "Não foi possível confirmar a adição. Evite repetir para não duplicar a quantidade."
    E a conexão do carrinho foi tentada uma única vez

  Esquema do Cenário: Não enviar quantidade vazia, fracionária ou menor que um
    Dado que tenho uma sessão para adicionar ao carrinho
    Quando abro o detalhe para adicionar ao carrinho
    E preencho a quantidade do carrinho com "<quantidade>"
    E adiciono o jogo ao carrinho
    Então a quantidade do carrinho é inválida
    E foram feitos 0 pedidos de adição ao carrinho

    Exemplos:
      | quantidade |
      |            |
      | 0          |
      | -1         |
      | 1.5        |
