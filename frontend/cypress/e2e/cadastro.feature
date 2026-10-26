# language: pt
@GK-7 @R1 @regressao
Funcionalidade: Cadastrar cliente
  O visitante cria uma conta de Cliente com dados válidos e recebe erros claros.

  @smoke
  Cenário: Criar uma conta com dados válidos
    Dado que a API aceita um novo cliente
    Quando abro o cadastro
    E preencho dados válidos
    E envio o cadastro
    Então vejo a confirmação da conta Cliente

  @excecao
  Cenário: Recusar um e-mail já cadastrado
    Dado que a API informa que o e-mail já está em uso
    Quando abro o cadastro
    E preencho dados válidos
    E envio o cadastro
    Então vejo o aviso de e-mail em uso
    E o formulário continua disponível

  @excecao
  Cenário: Recusar uma senha curta antes de chamar a API
    Dado que observo as chamadas de cadastro
    Quando abro o cadastro
    E preencho uma senha com menos de 8 caracteres
    E envio o cadastro
    Então vejo o motivo da senha inválida
    E nenhuma chamada de cadastro é enviada
