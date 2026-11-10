# Documentos do GameKeys

A versão que vale é a do Google Drive, onde a equipe preenche. As cópias desta pasta (.docx, .xlsx e .md) são atualizadas no fim de cada sprint. A tabela de documentos com os links do Drive está no [README da raiz](../README.md).

## Como a pasta está organizada

| Pasta | O que guarda |
| --- | --- |
| `projeto/` | Documentos que valem para as quatro releases: proposta, acordos de trabalho, ambiente de desenvolvimento, calendário de cerimônias, priorização do backlog e registro de riscos |
| `qualidade/` | Planos e planilhas que evoluem a cada release: Plano de Qualidade, Plano de Teste, Análise de Riscos e DoD de sprint e release |
| `tecnico/api/` | Contratos de API e guias de integração (carrinho, reserva) |
| `tecnico/banco/` | DER do banco em formato editável (DBML) |
| `release-1/` | Relatórios e Release Notes da Release 1 |
| `release-1/sprint-1/` | Plano, atas (Planning, Review e Retrospectiva), acompanhamento e roteiros de teste da Sprint 1 |
| `release-2/` | Plano da Release 2, Plano de Qualidade e Testes da R2 e Relatório do Pipeline R2 |
| `release-2/sprint-2/` | Atas, acompanhamento e roteiro da Review da Sprint 2 |
| `release-2/sprint-2/testes/` | Roteiros, evidências e experimentos de teste da Sprint 2 (GK-11, GK-110, GK-116, GK-124 e GK-140) |

## Onde colocar um documento novo

- Vale para o projeto inteiro e quase não muda: `projeto/`.
- Plano ou planilha que o QA atualiza a cada release: `qualidade/`.
- Contrato de API ou DER: `tecnico/`.
- Relatório ou Release Notes de uma release: `release-N/`.
- Ata, acompanhamento, roteiro ou evidência de uma sprint: `release-N/sprint-N/`.

Para a Release 3, crie `release-3/` com `sprint-4/` e `sprint-5/` dentro, seguindo o mesmo padrão. Os nomes dos arquivos seguem o padrão `Tipo-do-Documento-Sprint-N.docx` ou `Tipo-do-Documento-RN.docx`.
