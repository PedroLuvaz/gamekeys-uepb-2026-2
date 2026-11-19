# language: pt
@US-14 @GK-14 @R2 @regressao
Funcionalidade: Finalizar o carrinho com segurança
  Como cliente autenticado
  Quero criar um pedido com os preços confirmados pelo servidor
  Para prosseguir ao pagamento sem duplicar a compra

  @smoke
  Cenário: Finalização bloqueia duplo clique e abre o pedido
    Dado que a finalização responde no modo "demora"
    Quando abro o carrinho para finalizar
    E aciono a finalização duas vezes imediatamente
    Então a finalização bloqueia alterações enquanto envia
    E vejo o pedido criado pela finalização
    E somente uma solicitação de finalização foi enviada

  Cenário: Carrinho vazio não oferece finalização
    Dado que a finalização responde no modo "vazio"
    Quando abro o carrinho para finalizar
    Então não posso finalizar um carrinho vazio

  Esquema do Cenário: Recusa confirmada permite corrigir o carrinho
    Dado que a finalização responde no modo "<modo>"
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então vejo a recusa definitiva da finalização
    E posso corrigir o carrinho antes de finalizar de novo
    Exemplos:
      | modo |
      | 403  |
      | 404  |
      | 409  |
      | 422  |

  Esquema do Cenário: Resultado incerto conserva a identidade da operação
    Dado que a finalização responde no modo "<modo>"
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então a finalização fica pendente e bloqueia alterações
    Quando a confirmação volta e verifico a finalização
    Então vejo o pedido criado pela finalização
    E todas as tentativas usam a mesma identidade de operação
    Exemplos:
      | modo         |
      | 503          |
      | rede         |
      | invalida     |
      | id-inseguro  |
      | timeout      |

  Cenário: Recarga recupera pedido mesmo com carrinho já esvaziado
    Dado que a finalização responde no modo "confirmacao-perdida"
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então a finalização fica pendente e bloqueia alterações
    Quando recarrego o carrinho depois da confirmação perdida
    Então não há finalização automática ao recuperar a sessão
    Quando a confirmação volta e verifico a finalização
    Então vejo o pedido criado pela finalização
    E todas as tentativas usam a mesma identidade de operação

  Cenário: Sessão expirada conserva a recuperação após novo login
    Dado que a finalização responde no modo "401"
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então vou ao login com retorno ao carrinho e operação preservada

  Cenário: Falha ao persistir a identidade impede envio inseguro
    Dado que a finalização responde no modo "armazenamento"
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então a finalização fica indisponível sem enviar pedido

  Cenário: Identidade corrompida não cria outra operação
    Dado que a finalização responde no modo "corrompida"
    Quando abro o carrinho para finalizar
    Então a finalização fica indisponível sem enviar pedido

  Cenário: Operação de outro cliente não é reutilizada
    Dado que a finalização responde no modo "outro-cliente"
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então vejo o pedido criado pela finalização
    E a identidade de outro cliente não foi utilizada

  Cenário: Alteração em andamento impede finalizar estado desatualizado
    Dado que a finalização responde no modo "alteracao"
    Quando abro o carrinho para finalizar
    E aumento a quantidade antes de finalizar
    Então a finalização espera a alteração do carrinho

  @mobile
  Cenário: Recuperação cabe em um celular de 320 pixels
    Dado que a finalização responde no modo "503"
    E uso um celular para finalizar
    Quando abro o carrinho para finalizar
    E finalizo o carrinho
    Então a finalização fica pendente e bloqueia alterações
    E a recuperação da finalização cabe na tela
