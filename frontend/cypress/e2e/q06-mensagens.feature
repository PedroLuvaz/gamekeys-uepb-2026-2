# language: pt
@Q-06 @R2 @regressao
Funcionalidade: Mensagens claras nos fluxos entregues
  As recusas de cadastro, autenticação e carrinho orientam o usuário em português.
  As respostas são controladas e não acessam o banco compartilhado.

  Cenário: Cadastro obrigatório ausente
    Quando envio o cadastro Q-06 sem preencher os dados
    Então a mensagem Q-06 é "Informe um nome entre 2 e 120 caracteres."

  Cenário: E-mail de cadastro inválido
    Quando envio o cadastro Q-06 com e-mail inválido
    Então a mensagem Q-06 é "Informe um e-mail válido."

  Cenário: Senha de cadastro curta
    Quando envio o cadastro Q-06 com senha curta
    Então a mensagem Q-06 é "A senha deve ter pelo menos 8 caracteres."

  Cenário: Data de nascimento inválida
    Quando envio o cadastro Q-06 com data inválida
    Então a mensagem Q-06 é "Informe uma data de nascimento válida."

  Cenário: Senha de cadastro acima do limite
    Quando envio o cadastro Q-06 com senha acima de 72 bytes
    Então a mensagem Q-06 é "A senha deve ter no máximo 72 bytes."

  Cenário: Conta duplicada
    Dado que o cadastro Q-06 é recusado como duplicado
    Quando envio dados válidos no cadastro Q-06
    Então a mensagem Q-06 é "Este e-mail já está em uso."

  Cenário: Cadastro temporariamente indisponível
    Dado que o cadastro Q-06 é recusado por indisponibilidade
    Quando envio dados válidos no cadastro Q-06
    Então a mensagem Q-06 é "Não foi possível concluir o cadastro. Tente novamente mais tarde."

  Cenário: Falha de rede no cadastro
    Dado que a rede Q-06 falha no cadastro
    Quando envio dados válidos no cadastro Q-06
    Então a mensagem Q-06 é "Não foi possível falar com o servidor. Tente novamente."

  Cenário: Resposta de erro sem detalhe no cadastro
    Dado que o cadastro Q-06 é recusado sem detalhe
    Quando envio dados válidos no cadastro Q-06
    Então a mensagem Q-06 é "Não foi possível concluir o cadastro. Tente novamente."

  Cenário: E-mail inválido no login
    Quando envio o login Q-06 com e-mail inválido
    Então a mensagem de login Q-06 é "Informe um e-mail válido."

  Cenário: Senha ausente no login
    Quando envio o login Q-06 sem senha
    Então a mensagem de login Q-06 é "Informe sua senha."

  Cenário: Login incorreto
    Dado que o login Q-06 é recusado por credenciais
    Quando envio credenciais no login Q-06
    Então a mensagem de login Q-06 é "E-mail ou senha incorretos."

  Cenário: Autenticação temporariamente indisponível
    Dado que o login Q-06 é recusado por indisponibilidade
    Quando envio credenciais no login Q-06
    Então a mensagem de login Q-06 é "Autenticação temporariamente indisponível."

  Cenário: Resposta de erro sem detalhe no login
    Dado que o login Q-06 é recusado sem detalhe
    Quando envio credenciais no login Q-06
    Então a mensagem de login Q-06 é "Não foi possível entrar. Tente novamente."

  Cenário: Token expirado
    Dado que a sessão Q-06 expirou no servidor
    Quando abro a conta protegida Q-06
    Então vejo o aviso Q-06 de sessão expirada

  Cenário: Falha de rede ao validar a sessão
    Dado que a rede Q-06 falha ao validar a sessão
    Quando abro a conta protegida Q-06
    Então a conta Q-06 informa "Não foi possível validar sua sessão. Tente novamente."

  Cenário: Resposta sem detalhe ao validar a sessão
    Dado que a validação Q-06 da sessão falha sem detalhe
    Quando abro a conta protegida Q-06
    Então a conta Q-06 informa "Não foi possível validar sua sessão."

  Cenário: Carrinho sem autenticação
    Quando abro o carrinho Q-06 sem sessão
    Então o carrinho Q-06 exige login e preserva o retorno

  Cenário: Carrinho recusado para administrador
    Quando abro o carrinho Q-06 com perfil administrador
    Então o carrinho Q-06 informa "O carrinho é exclusivo de contas de cliente."

  Cenário: Quantidade inválida
    Dado que preparo a ficha Q-06 com resposta de sucesso
    Quando adiciono a quantidade Q-06 "0"
    Então a mensagem do carrinho Q-06 é "Informe uma quantidade inteira maior que zero."

  Esquema do Cenário: Recusas de negócio no carrinho
    Dado que preparo a ficha Q-06 com status <status> e mensagem "<mensagem>"
    Quando adiciono a quantidade Q-06 "1"
    Então a mensagem do carrinho Q-06 é "<mensagem>"

    Exemplos:
      | status | mensagem                                                        |
      | 409    | Estoque insuficiente para a quantidade solicitada.               |
      | 404    | Jogo não encontrado.                                            |
      | 403    | Sua idade não permite adicionar este jogo ao carrinho.           |

  Cenário: Item inexistente ao alterar o carrinho
    Dado que a alteração Q-06 do carrinho falha com status 404 e mensagem "Item não encontrado no carrinho."
    Quando aumento o item no carrinho Q-06
    Então a atualização Q-06 informa "Item não encontrado no carrinho."

  Cenário: Resposta sem detalhe ao alterar o carrinho
    Dado que a alteração Q-06 do carrinho falha sem detalhe
    Quando aumento o item no carrinho Q-06
    Então a atualização Q-06 informa "Não foi possível atualizar o carrinho."

  Cenário: Resposta inválida ao consultar o carrinho
    Dado que a consulta Q-06 do carrinho retorna dados inválidos
    Quando abro o carrinho autenticado Q-06
    Então a consulta Q-06 informa "O servidor retornou um carrinho inválido. Tente novamente."

  Cenário: Servidor indisponível
    Dado que o servidor Q-06 está indisponível no login
    Quando envio credenciais no login Q-06
    Então a mensagem de login Q-06 é "Não foi possível falar com o servidor. Tente novamente."

  Cenário: Field required do Pydantic não chega à tela
    Dado que o cadastro Q-06 recebe Field required
    Quando envio dados válidos no cadastro Q-06
    Então a mensagem Q-06 é "Informe um nome entre 2 e 120 caracteres."
    E a tela Q-06 não exibe mensagens padrão em inglês

  Cenário: Input should be do Pydantic não chega à tela
    Dado que preparo a ficha Q-06 com validação em inglês
    Quando adiciono a quantidade Q-06 "1"
    Então a mensagem do carrinho Q-06 é "Informe uma quantidade inteira maior que zero."
    E a tela Q-06 não exibe mensagens padrão em inglês
