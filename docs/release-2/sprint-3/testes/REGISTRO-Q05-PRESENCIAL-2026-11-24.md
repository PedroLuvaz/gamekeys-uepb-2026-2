# Q-05 — teste de usabilidade presencial — 24/11/2026

## Objetivo e fonte

Registrar o resultado da Q-05 da Release 2 / Sprint 3: verificar se pelo menos quatro de cinco voluntários conseguem concluir a compra de teste, sem ajuda, em até 300 segundos. Os resultados abaixo foram transcritos da aba [Participantes da planilha oficial da Q-05](https://docs.google.com/spreadsheets/d/1Dyd0CsbbBjptbA_l8vQDX28BNNL9vCR0KZZ_4YN7PGw/edit#gid=1828528638), com a consolidação conferida na aba **Resumo**.

Este registro trata das sessões presenciais P01–P05. O [ensaio automatizado A01–A05](REGISTRO-Q05-AUTOMACAO-2026-11-24.md) ocorreu antes delas e não entra na meta de usabilidade. O resultado histórico de 0/5 participantes naquele ensaio descreve a situação **naquela etapa**, antes da aplicação presencial.

## Ambiente e método

A aba **Participantes** informa a aplicação em 24/11/2026 nos seguintes equipamentos: P01 em notebook Acer Nitro 5, P02 em notebook Dell, P03 em notebook Acer, P04 em notebook Lenovo e P05 em notebook Acer. Não há na planilha identificação de URL, banco de dados, contas, configuração do pagamento ou inventário de chaves usados em cada sessão; por isso, este relatório não atribui às sessões presenciais o ambiente do ensaio automatizado.

O [protocolo oficial](https://docs.google.com/spreadsheets/d/1Dyd0CsbbBjptbA_l8vQDX28BNNL9vCR0KZZ_4YN7PGw/edit#gid=533534898) define quatro tarefas: encontrar um jogo, adicioná-lo ao carrinho, finalizar o pedido e confirmar o pagamento simulado com visualização da chave de teste. A contagem termina na conclusão ou aos 300 segundos. O registro de “compra completa” na planilha é interpretado conforme esse fluxo; não há marcação individual de cada etapa nem observação detalhada anexada.

## Participantes anônimos e resultados

| Sessão | Tempo | Compra completa | Sem ajuda | Dificuldades registradas | Resultado na planilha |
| ------ | ----: | --------------- | --------- | ------------------------ | --------------------- |
| P01    | 203 s | Sim             | Sim       | Nenhuma                  | Aprovado              |
| P02    | 187 s | Sim             | Sim       | Nenhuma                  | Aprovado              |
| P03    | 140 s | Sim             | Sim       | Nenhuma                  | Aprovado              |
| P04    | 200 s | Sim             | Sim       | Nenhuma                  | Aprovado              |
| P05    | 203 s | Sim             | Sim       | Nenhuma                  | Aprovado              |

As cinco sessões estão marcadas como compra completa e sem ajuda, todas abaixo de 300 segundos. O tempo médio é **186,6 segundos** (933 segundos no total, divididos por cinco). O campo “Dificuldades observadas” está preenchido como “Nenhuma” para P01–P05; isso não equivale a depoimentos detalhados, que não foram registrados.

## Critério de aceitação

**Meta: pelo menos 4/5 participantes concluírem a compra completa sem ajuda em até 300 segundos. Resultado registrado: 5/5, ou 100%.** Assim, a meta da Q-05 foi atingida **conforme os registros do aplicador na planilha**. As cinco sessões humanas são distintas das cinco execuções automatizadas A01–A05 e seus tempos não foram combinados.

## Limitações e próximos passos

- A planilha não contém evidências anexadas, capturas nem depoimentos detalhados. Este relatório consolida seus campos, sem afirmar uma verificação independente de cada compra ou do ambiente usado.
- Segundo informação repassada à equipe de QA, Wagner, Product Owner, informou no grupo que conferiu os resultados. Ainda não consta aceite formal explícito no Jira ou na planilha; registrar essa ciência formal quando disponível.
- Se houver evidências complementares, revisar e anonimizar antes de anexá-las. Não publicar nomes, e-mails, senhas, tokens, códigos completos de chaves ou dados de banco de teste.
- Levar a consolidação da Q-05 à documentação de fechamento da Sprint 3 / Release 2, mantendo o ensaio automatizado e seus resultados históricos preservados.
