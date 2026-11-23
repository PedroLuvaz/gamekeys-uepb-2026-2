# GK-149 — Sigilo dos erros de conexão e rotação da credencial

Correção e verificação local em 22/11/2026, por Wagner (PO e DevOps), partindo da
`main` em `b0d0153`. A reprodução com senha fictícia confirmou exposição em erros
de conexão malformada. A correção elimina o marcador nos casos reproduzidos;
a identificação e a rotação da credencial do incidente original continuam
pendentes de execução coordenada com Pedro.

## Reprodução e correção

Uma senha com percent-encoding inválido na URL pode aparecer na mensagem do
parser do PostgreSQL. Antes da correção, essa mensagem era encadeada à recusa
genérica do pytest e dos comandos de QA. Na API, os workers do pool registravam
a mensagem original ao tentar abrir a conexão. O corpo HTTP continuava genérico;
a exposição observada nesse caminho estava no log interno.

`app/conexao.py` centraliza a leitura da configuração com erro fixo e sem
encadeamento da exceção original. O pool valida a configuração antes de iniciar
seus workers e usa `ConexaoPostgres`, que remove os detalhes sensíveis das falhas
de abertura de conexão, preservando a classe do erro e seu SQLSTATE válido. A
conexão bem-sucedida continua usando o driver existente, o mesmo pool e as mesmas
transações. A proteção não altera permissões, schema ou dados do banco.

Os validadores do pytest e do experimento GK-110 reutilizam a leitura protegida.
A GK-129 e as fixtures de carrinho/checkout continuam usando a mesma proteção
contra hosts remotos. A correção não libera o uso de pytest no Neon compartilhado.

## Evidências locais

| Verificação | Antes | Depois |
| --- | --- | --- |
| Recusa do pytest com URL malformada | marcador no traceback | marcador ausente |
| CLI `qa.gk110_concorrencia` com URL malformada | marcador no traceback | marcador ausente |
| CLI `qa.gk129_reserva_concorrente` com URL malformada | marcador no traceback | marcador ausente |
| API com URL malformada | marcador no log do pool; resposta genérica 503 | marcador ausente; resposta genérica 503 |
| Demais sondagens locais da auditoria | marcador ausente | marcador ausente |

- As mesmas dez verificações passaram de quatro exposições do marcador fictício
  para zero. A falha intencional de configuração continua sendo recusada.
- Os 14 novos testes de `tests/test_sigilo_conexoes.py` passaram. Cobrem URI e
  formato por palavras-chave, senha corretamente codificada, falhas de conexão,
  preservação de SQLSTATE, logs/respostas da API e subprocessos reais de
  pytest/GK-110/GK-129/carrinho/checkout.
- A regressão completa passou: **291 testes**, em PostgreSQL descartável local
  `127.0.0.1:55436/gamekeys_teste`. Um aviso de depreciação existente de `TestClient`
  não bloqueou a execução. Ruff e formatação passaram.
- `PYTHON_DOTENV_DISABLED=1` e as três variáveis de conexão foram definidas
  explicitamente para alvos fictícios ou o PostgreSQL local em cada execução.
  Os erros não foram provocados no ambiente compartilhado.

Relatórios locais, ignorados pelo Git: `backend/relatorios/gk149/antes-correcao/`,
`auditoria.json`, logs sanitizados, `sigilo.xml` e `backend-completo.xml`.
Os testes novos entram automaticamente no pytest do CI, cujo JUnit fica no
artefato `relatorios-de-teste`. O relatório do pipeline e os links dos artefatos
ficam na descrição do PR, associados ao commit efetivamente verificado.

Esta reprodução não identifica qual usuário teve sua credencial exposta no
traceback original de 04/11. Corrigir o código também não revoga uma credencial
que já tenha sido exposta.

## Acessos e consumidores

Wagner confirmou acesso **Editor** ao projeto Neon `gamekeys`, branch
`production`, em 22/11. Existem os usuários `gamekeys_equipe` e `neondb_owner`.
A configuração local utiliza `gamekeys_equipe` para `gamekeys` e `gamekeys_teste`;
as duas bases ficam na mesma branch, e a senha da role não é uma senha por banco.

Pedro registrou na GK-149, comentário 10325, que fará a atualização dos segredos e
o deploy dos projetos Vercel sob sua conta. A equipe manterá a divisão existente
de acesso, sem compartilhar login e sem exigir novo plano para esta ação.

| Consumidor | Responsável pela atualização |
| --- | --- |
| Role confirmada no Neon | Wagner, em horário combinado |
| `.env.local` de Wagner: URLs correspondentes e `PGPASSWORD` | Wagner |
| Ambientes locais dos demais integrantes, se afetados | Cada integrante, pelo canal restrito da equipe |
| `DATABASE_URL` da API `gamekeys-api`, Production e Preview | Pedro, somente se consumir a role da troca |
| Deploy da API com a variável atualizada | Pedro |
| PostgreSQL efêmero do CI | Independente da senha compartilhada do Neon |

Se o alvo for `neondb_owner`, mapear seus consumidores administrativos; não
substituir por padrão a conexão da API por uma role com mais privilégios.

## Roteiro do corte

1. **Wagner e Rodrigo:** identificar a role do incidente original, sem publicar
   senha ou traceback bruto. Confirmar os consumidores dessa role.
2. **Wagner:** obter aprovação independente da correção e sua integração. Conferir
   que a versão publicada contém a proteção antes de utilizar a credencial nova.
3. **Wagner e Pedro:** combinar uma janela em que ambos estejam disponíveis.
   O reset pode encerrar conexões e a configuração antiga deixa de autenticar em
   novas conexões. A etapa não será executada enquanto os consumidores não
   puderem ser atualizados.
4. **Wagner:** trocar somente a role confirmada no Neon, atualizar o próprio
   `.env.local` preservando demais variáveis e entregar a nova URL pooled da API
   a Pedro por canal restrito. Não colocar valores em Git, Jira, PR, relatório
   ou mensagem pública. Os demais integrantes atualizam os ambientes afetados.
5. **Pedro:** no projeto `gamekeys-api`, substituir somente `DATABASE_URL` nos
   ambientes Production e Preview afetados, preservando o tipo protegido e os
   escopos existentes. Verificar eventuais sobrescritas específicas de branch.
   Fazer o redeploy da API e do preview que estiver em uso. O frontend atual
   apenas encaminha `/api` para a API e não recebe a senha do banco.
6. **Wagner:** validar autenticação com a nova credencial em conexões novas,
   diretas e pooled, nos bancos efetivamente afetados. Comprovar a recusa da
   credencial anterior em novas autenticações; timeout ou falha de rede não
   comprovam revogação. Conferir saúde do banco e catálogo pelo proxy web, sem
   executar pytest, migrações ou compras de teste no banco compartilhado.
7. **Wagner:** registrar data, responsável, role, ambientes, versão/deploy e
   resultados na GK-149 e na GK-116. A revisão da correção e o CI verde não
   substituem essas evidências operacionais para concluir a GK-149.

Para esta troca isolada, atualizar somente a variável necessária. O script
`scripts/vercel-env.sh` configura também JWT e outras variáveis; não é necessário
reenviar toda a configuração. Caso a publicação falhe, corrigir a configuração
e republicar; não restaurar uma senha sabidamente exposta.

## Situação da entrega

Correção e regressão local concluídas. Permanecem revisão/integração da correção,
identificação do usuário do incidente, janela combinada, rotação, atualização dos
consumidores e validação posterior. Nenhuma senha foi trocada nesta entrega, e
a GK-149 permanece em andamento até a comprovação da revogação e dos consumidores.
