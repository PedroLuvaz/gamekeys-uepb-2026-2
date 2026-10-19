# Configuração do GameKeys no Jira

Levantada em 19/10/2026 direto do Jira. Se algo falhar, confira de novo (`getJiraProjectIssueTypesMetadata`, `getTransitionsForJiraIssue`) e atualize este arquivo.

| Item | Valor |
|---|---|
| Site | `pedrolucas0721.atlassian.net` |
| cloudId | `0fc843c8-8aad-4b5d-bca9-00b455a162f1` |
| Projeto | `GK` (GameKeys-2026-2, id 10033), quadro 34 |
| Repositório | `PedroLuvaz/gamekeys-uepb-2026-2` |

Cada pessoa precisa do conector Atlassian autorizado na própria conta e com acesso ao site acima.

## Tipos de item

| Nome | id | Uso |
|---|---|---|
| História (Story) | 10043 | US, RF, RNF e Task (Task também é US) |
| Bug | 10044 | Só sob pedido do usuário |
| Epic | 10042 | Não criar sem pedido |
| Tarefa | 10045 | Legado da Sprint 0 (parent GK-6). Não usar para trabalho novo |
| Subtask | 10041 | Opcional, dentro de uma US |

## Campos

| Campo | Chave | Observação |
|---|---|---|
| Pontos | `customfield_10016` | número |
| Sprint | `customfield_10020` | id numérico da sprint (Sprint 0 = 35, Sprint 1 = 36). Para outras, leia de uma issue da sprint por JQL |
| Release | `fixVersions` | por nome: "Release 1" a "Release 4" (ids 10000 a 10003) |
| Épico | `parent` | chave do épico |
| Prioridade | `priority` | `{"name": "Medium"}` em `additional_fields` funcionou na criação (GK-65). Se algum dia recusar, use `editJiraIssue` |
| Labels | `labels` | ver abaixo |

## Prioridade

| Termo na equipe | Prioridade Jira | Label |
|---|---|---|
| Muito alta | Highest | `prioridade-muitoalta` |
| Alta | High | `prioridade-alta` |
| Média | Medium | `prioridade-media` |
| Baixa | Low | `prioridade-baixa` |

O modelo de US tem só Alta, Média e Baixa, mas o backlog usa Muito alta nas US críticas (ex.: GK-7, GK-8). Na descrição escreva o termo da equipe.

## Labels

- Sempre na US: `user-story`, `RF` ou `RNF`, `release-N`, `prioridade-*`.
- Sprint (quando já planejada): `sprint-N`.
- Atributo de qualidade (RNF): `seguranca`, `confiabilidade`, `usabilidade`.
- Outras em uso: `banco`, `infra`, `backend`, `documentação`, `tech-debt`, `avaliacao`, `risco`.
- Bug: `bug`, `release-N`, `sprint-N`. A severidade vai na descrição e na label `severidade-critica|alta|media|baixa` (convenção desta skill; ainda não existia no Jira, proponha ao SM adotar).

## Épicos

GK-1 Conta e acesso, GK-2 Catálogo, GK-3 Carrinho e pedido, GK-4 Administração, GK-5 Avaliações, GK-6 Gestão e infraestrutura, GK-40 Segurança, GK-41 Confiabilidade, GK-42 Usabilidade (RNFs), GK-59 Infraestrutura do Banco de Dados, GK-62 Documentação, GK-64 Risco.

## Fluxo de status

`Backlog → Pronto para a Sprint → Em andamento → Em revisão → Concluído`

| Destino | id da transição | Gate |
|---|---|---|
| Backlog | 11 (aparece como "A fazer") | nenhum |
| Pronto para a Sprint | 2 | DoR (Planning) |
| Em andamento | 21 | DoR + branch criada |
| Em revisão | 31 | PR aberto |
| Concluído | 41 (aparece como "Feito") | DoD |

As transições são globais (qualquer status para qualquer outro). Confirme os ids com `getTransitionsForJiraIssue` antes de usar.

## Consultas úteis (JQL)

- Sprint atual: `project = GK AND sprint in openSprints() ORDER BY status, key`
- Sprint 1: `project = GK AND sprint = 36 ORDER BY key`
- Bugs críticos/altos abertos: `project = GK AND issuetype = Bug AND labels in (severidade-critica, severidade-alta) AND statusCategory != Done`
- Parados em andamento: `project = GK AND status = "Em andamento" AND updated <= -3d` (regra do risco R01: tarefa parada há mais de 3 dias é redistribuída)
- Última chave: `project = GK ORDER BY key DESC` com `maxResults=1`

Respostas de busca grandes estouram o limite: peça só os campos necessários (`summary, status, issuetype, priority, labels, parent, customfield_10016, customfield_10020`).

## Equipe

Pedro Lucas Vaz de Andrade (@PedroLuvaz), Wagner Tiburcio da Silva Junior (@Wagnerxxdd), Rodrigo Almeida Gomes. Papéis da Release 1: Pedro PO e DevOps, Wagner QA, Rodrigo SM. Papéis mudam a cada release; a fonte é a tabela do README.
