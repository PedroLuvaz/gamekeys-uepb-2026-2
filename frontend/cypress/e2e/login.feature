# language: pt
@GK-8 @R1 @regressao
Funcionalidade: Entrar e encerrar a sessão
  O cliente usa credenciais persistidas e perde o acesso quando a sessão é inválida.

  @smoke
  Cenário: Entrar com credenciais válidas
    Dado que a API autentica o cliente
    Quando abro o login
    E informo credenciais válidas
    E envio o login
    Então vejo minha área protegida

  @excecao
  Cenário: Mostrar mensagem genérica para credenciais incorretas
    Dado que a API recusa as credenciais
    Quando abro o login
    E informo credenciais inválidas
    E envio o login
    Então vejo uma mensagem genérica de credenciais incorretas

  @excecao
  Cenário: Redirecionar quando o servidor recusa a sessão
    Dado que tenho uma sessão local que o servidor considera inválida
    Quando abro minha conta
    Então volto ao login com o aviso de sessão expirada

  Cenário: Encerrar a sessão pelo botão sair
    Dado que tenho uma sessão válida
    Quando abro minha conta
    E encerro a sessão
    Então volto ao login sem manter o token
