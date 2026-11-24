# Documentos do GameKeys

A versão que vale é a do Google Drive, onde a equipe preenche. As cópias desta pasta (.docx, .xlsx e .md) são atualizadas no fim de cada sprint. A tabela de documentos com os links do Drive está no [README da raiz](../README.md).

## Como a pasta está organizada

| Pasta                        | O que guarda                                                                                                                                                                                                                                        |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `projeto/`                   | Documentos que valem para as quatro releases: proposta, acordos de trabalho, ambiente de desenvolvimento, calendário de cerimônias, priorização do backlog e registro de riscos                                                                     |
| `qualidade/`                 | Planos e planilhas que evoluem a cada release: Plano de Qualidade, Plano de Teste, Análise de Riscos e DoD de sprint e release                                                                                                                      |
| `tecnico/api/`               | Contratos de API e guias de integração (carrinho, reserva)                                                                                                                                                                                          |
| `tecnico/banco/`             | DER do banco em formato editável (DBML)                                                                                                                                                                                                             |
| `release-1/`                 | Relatórios e Release Notes da Release 1                                                                                                                                                                                                             |
| `release-1/sprint-1/`        | Plano, atas (Planning, Review e Retrospectiva), acompanhamento e roteiros de teste da Sprint 1                                                                                                                                                      |
| `release-2/`                 | Plano da Release 2, Release Notes R2 (prévia para a Review de 26/11), Plano de Qualidade e Testes da R2 e relatórios de Pipeline e Métricas R2                                                                                                      |
| `release-2/sprint-2/`        | Atas, acompanhamento e roteiro da Review da Sprint 2                                                                                                                                                                                                |
| `release-2/sprint-2/testes/` | Roteiros, evidências e experimentos de teste da Sprint 2 (GK-11, GK-110, GK-116, GK-124 e GK-140)                                                                                                                                                   |
| `release-2/sprint-3/`        | Ata da Planning (realizada em 17/11), Acompanhamento, roteiro e atas da Review e da Retrospectiva da Sprint 3, preparados antes das reuniões                                                                                                        |
| `release-2/sprint-3/testes/` | Roteiros e evidências de teste da Sprint 3, incluindo o [Registro QA de 24/11/2026](release-2/sprint-3/testes/REGISTRO-QA-2026-11-24.md) e o [Ensaio Q-05 automatizado](release-2/sprint-3/testes/REGISTRO-Q05-AUTOMACAO-2026-11-24.md) para GK-144 |

## Onde colocar um documento novo

A atualização de 24/11 da GK-147 está na seção 5 da [Priorização do Backlog](projeto/Priorizacao-do-Backlog.docx). Ela registra a sequência revisada da R3, os pendentes da R2 e as decisões para refinamento, preservando o histórico anterior. O [registro da GK-147](release-2/sprint-3/Repriorizacao-do-Backlog-GK-147.json) contém prioridades e Rank antes e depois da alteração, conferidos no Jira. O feedback da Review de 26/11 será incorporado após seu registro.

- Vale para o projeto inteiro e quase não muda: `projeto/`.
- Plano ou planilha que o QA atualiza a cada release: `qualidade/`.
- Contrato de API ou DER: `tecnico/`.
- Relatório ou Release Notes de uma release: `release-N/`.
- Ata, acompanhamento, roteiro ou evidência de uma sprint: `release-N/sprint-N/`.

Para a Release 3, crie `release-3/` com `sprint-4/` e `sprint-5/` dentro, seguindo o mesmo padrão. Os nomes dos arquivos seguem o padrão `Tipo-do-Documento-Sprint-N.docx` ou `Tipo-do-Documento-RN.docx`.

## No Drive

A pasta [GameKeys - Documentos](https://drive.google.com/drive/folders/1pbRMCUucJ_8y1VKreh51SlERl2sVnt4h) segue a mesma ideia:

- `Projeto` e `Qualidade`, com os documentos que valem para todas as releases.
- `GameKeys - Release 1` e `GameKeys - Release 2`, com as subpastas `Sprint 1` (na Release 1) e `Sprint 2` e `Sprint 3` (na Release 2), onde ficam atas, plano, acompanhamento e roteiros.
- `GameKeys - Sprint 0`, com o material que sobrou da preparação do projeto.

Mover um arquivo no Drive não muda o link dele, então os links do [README da raiz](../README.md) continuam valendo.
