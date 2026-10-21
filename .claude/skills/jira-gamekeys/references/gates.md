# Gates: DoR e DoD

Fontes: `.github/ISSUE_TEMPLATE/user-story.yml` (DoR e DoD de US, iguais ao modelo de US do Jira), `.github/pull_request_template.md` e `docs/DoD-Sprint-e-Release.xlsx` (DoD de sprint e de release).

Cada item vira uma linha com **OK**, **FALTA** ou **NÃO VERIFICÁVEL**, mais a evidência. Nunca marque OK sem evidência.

## DoR (antes de Pronto para a Sprint e de Em andamento)

Leia a issue com `getJiraIssue` (fields: summary, description, labels, fixVersions, priority, parent, customfield_10016, issuelinks).

| # | Item | Como conferir |
|---|---|---|
| 1 | Formato "Eu como... preciso... de modo que..." | descrição tem a seção "História de usuário" com as três partes |
| 2 | Critérios Dado que / Quando / Então com 1 sucesso e 1 exceção | ao menos 2 cenários, um marcado (sucesso) e outro (exceção) |
| 3 | Estimada pela equipe e no máximo 5 pontos | `customfield_10016` preenchido e entre 1 e 5. Acima de 5: dividir |
| 4 | Prioridade e release preenchidas | `priority` definida e `fixVersions` com uma release |
| 5 | Épico (parent) definido | `parent` presente |
| 6 | Sem dependência pendente | links "é bloqueada por" ou menção a outra US na descrição: buscar o status; precisa estar Concluído. Se não há como saber, perguntar ao usuário |
| 7 | Sem dúvida aberta com o PO | perguntar ao usuário; não dá para inferir |
| 8 | Cabe em uma sprint | implicado por 3 |

Em andamento também exige: o usuário confirmou quem vai tocar (assignee) ou "a definir". Se a issue está em "Backlog", ofereça passar antes por "Pronto para a Sprint".

Papéis: o PO deixa a DoR pronta; a equipe confirma no Planning.

## DoD (antes de Concluído)

Itens de GitHub vêm de `scripts/gk.sh dod GK-N`. Itens de Jira você lê da issue e dos comentários.

| # | Item | Fonte | Quem |
|---|---|---|---|
| 1 | PR mesclado na `main` | `gk.sh dod` (`merged`) | DevOps |
| 2 | PR revisado por **outro** integrante | `gk.sh dod` (aprovação de quem não é o autor) | SM acompanha |
| 3 | Commit cita a chave `GK-N` | `gk.sh dod` | DevOps |
| 4 | CI verde | `gk.sh dod` (checks do PR) | DevOps |
| 5 | Testes escritos e passando | PR altera/adiciona testes (`gk.sh dod` lista arquivos de teste) + CI | QA |
| 6 | Cenários de aceite testados e passando | comentário do QA no Jira ou pergunta ao QA | QA |
| 7 | Homologação (só se a release exigir; hoje N/A na R1) | pergunta | DevOps |
| 8 | Documentação / README atualizado se mudou o jeito de rodar | `gk.sh dod` mostra se README foi tocado; se não, perguntar se era necessário | DevOps |
| 9 | Aceita pelo PO | comentário/confirmação do PO | PO |

Itens 6 e 9 não se provam por código: peça confirmação explícita do papel responsável e registre no comentário quem confirmou.

Depois de Concluído, ofereça marcar os checkboxes do DoR/DoD na descrição (`editJiraIssue` com a descrição atualizada), só com sim do usuário.

## DoD de sprint e de release (opcional)

Se o usuário pedir ("dod da sprint"), leia `docs/DoD-Sprint-e-Release.xlsx` e liste os critérios com quem verifica (QA, PO, SM, DevOps). Critérios que dá para conferir no Jira: board atualizado (todas as issues da sprint em status coerente), bugs críticos/altos sem plano, itens não concluídos de volta ao backlog, versão marcada como lançada. Os demais, pergunte.

## Modelos de comentário

Em andamento:
> Iniciado por <nome> (<papel>). Branch: `<branch>`. DoR conferida: OK.

Em revisão:
> PR aberto: <url>. CI: <estado>. Aguardando revisão de outro integrante e testes do QA.

Concluído:
> Concluído. PR <url> mesclado em <data>. DoD: PR revisado por <nome>, CI verde (<url do run>), testes passando, cenários validados pelo QA (<nome>), aceita pelo PO (<nome>).

Movido com pendência:
> Movido para <status> com pendência: <itens>. Responsável: <nome>. Avisar o SM.
