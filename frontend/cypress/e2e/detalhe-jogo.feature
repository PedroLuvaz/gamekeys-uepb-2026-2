# language: pt
@US-10 @GK-10 @GK-89 @R1 @regressao
Funcionalidade: Consultar o detalhe do jogo
  Como visitante, quero conhecer o jogo para decidir se vou comprar.
  Dados isolados em fixtures e respostas simuladas, sem acesso ao banco compartilhado.

  @smoke
  Cenário: Abrir o detalhe pelo catálogo e conferir os seis dados
    Dado que a API de detalhe contém um jogo ativo
    Quando abro esse jogo pelo catálogo
    Então os seis dados do detalhe correspondem à resposta da API
    E o título da página identifica esse jogo

  Cenário: Acessar e recarregar o endereço direto de um jogo
    Dado que a API de detalhe contém um jogo ativo
    Quando acesso o endereço direto do jogo em teste
    Então os seis dados do detalhe correspondem à resposta da API
    Quando recarrego a página
    Então os seis dados do detalhe correspondem à resposta da API
    Quando volto ao catálogo
    Então retorno à primeira página do catálogo do detalhe

  Cenário: Consultar um jogo esgotado e preservar a página de origem
    Dado que a API de detalhe contém um jogo esgotado
    Quando abro esse jogo na segunda página do catálogo
    Então os seis dados do detalhe correspondem à resposta da API
    E vejo a classificação de 14 anos e a disponibilidade Esgotado
    Quando recarrego a página
    E volto ao catálogo
    Então retorno à segunda página do catálogo do detalhe

  @excecao @smoke
  Esquema do Cenário: Não expor detalhes de um jogo indisponível no catálogo
    Dado que o jogo consultado no detalhe está <situacao>
    Quando acesso o endereço direto do jogo em teste
    Então o detalhe informa jogo não encontrado sem exibir seus dados
    Quando exploro outros jogos pela mensagem de não encontrado
    Então retorno à primeira página do catálogo do detalhe

    Exemplos:
      | situacao    |
      | inexistente |
      | inativo     |

  @excecao
  Cenário: Recuperar os detalhes após falha do serviço
    Dado que a consulta do detalhe falha com resposta 503
    Quando acesso o endereço direto do jogo em teste
    Então vejo uma falha de comunicação no detalhe com opção de tentar novamente
    Quando a API se recupera e tento carregar o detalhe novamente
    Então os seis dados do detalhe correspondem à resposta da API

  @excecao
  Cenário: Recuperar os detalhes após interrupção da conexão
    Dado que a consulta do detalhe falha por interrupção da rede
    Quando acesso o endereço direto do jogo em teste
    Então vejo uma falha de comunicação no detalhe com opção de tentar novamente
    Quando a API se recupera e tento carregar o detalhe novamente
    Então os seis dados do detalhe correspondem à resposta da API

  Cenário: Informar carregamento enquanto aguarda a consulta
    Dado que a API de detalhe demora para responder
    Quando acesso o endereço direto do jogo em teste
    Então o detalhe informa carregamento antes de exibir os dados
    E os seis dados do detalhe correspondem à resposta da API

  @mobile @smoke
  Cenário: Consultar a ficha completa em um celular estreito
    Dado que a API de detalhe contém um jogo ativo
    E uso uma tela de 320 pixels no detalhe
    Quando acesso o endereço direto do jogo em teste
    Então os seis dados do detalhe correspondem à resposta da API
    E a ficha do jogo cabe na largura do celular
