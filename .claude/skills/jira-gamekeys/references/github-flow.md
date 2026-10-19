# Fluxo Jira + GitHub

Chave do Jira (`GK-N`) em toda parte: branch, commit, título e corpo do PR. O Jira liga sozinho ao GitHub por essa chave, se o app GitHub for Jira estiver instalado.

## Convenções

| Item | Padrão | Exemplo |
|---|---|---|
| Branch | `<tipo>/GK-N-descricao-curta` | `feature/GK-12-carrinho-alterar-itens` |
| Tipos de branch | `feature` (História), `fix` (Bug), `docs`, `chore`, `refactor`, `test` | |
| Commit | `<tipo>: GK-N descrição no imperativo` (pt-BR, sem ponto final) | `feat: GK-7 valida e-mail repetido no cadastro` |
| Tipos de commit | `feat`, `fix`, `docs`, `chore`, `refactor`, `test` | |
| Título do PR | igual a um commit | `feat: GK-7 cadastro de cliente` |
| Corpo do PR | `.github/pull_request_template.md` preenchido | |

A branch `feature` usa `feat` nos commits. O histórico do repo já segue `docs: GK-35 ...`.

## Passo a passo

1. **Iniciar.** Gate DoR (gates.md). Pedido de confirmação mostra: `gk.sh branch GK-N <tipo> "<descrição>" --dry-run`. Com o sim, rode sem `--dry-run`. Depois mova o Jira para **Em andamento** e comente.
2. **Commitar.** O hook `scripts/hooks/commit-msg` recusa mensagem sem `GK-N` (ative com `scripts/gk.sh install-hooks`, uma vez por clone). Commits pequenos.
3. **Abrir PR.** `gk.sh pr GK-N "<descrição>" [--issue N] [--draft] --dry-run` mostra título e corpo. Com o sim, rode sem `--dry-run`. O script faz push da branch e `gh pr create`. Depois mova o Jira para **Em revisão** e comente com a URL.
   - `--issue N` adiciona `Closes #N` no corpo (só se existir uma issue no GitHub). A fonte oficial do backlog é o Jira, então o link principal é para o Jira.
4. **Revisar.** Outro integrante aprova o PR (regra do projeto). O QA testa os cenários.
5. **Mergear.** Só com CI verde e aprovação de outro integrante. `gh pr merge <pr> --squash --delete-branch` (ou o método que a equipe usar): peça confirmação ao usuário, é ação irreversível. A mensagem do squash deve conter `GK-N`.
6. **Concluir.** `gk.sh dod GK-N`, gate DoD (gates.md), mova para **Concluído** e comente.

## O que o script faz e o que fica com você

| `scripts/gk.sh` | Claude (conector Atlassian) |
|---|---|
| `branch`, `pr`, `dod`, `find-pr`, `install-hooks`, `doctor` | criar issue, transicionar, comentar, ler campos |

O script nunca fala com o Jira e não guarda token: usa só `git` e `gh` (login do próprio usuário).

## Falhas comuns

- `gh: command not found`: instale (https://cli.github.com) e rode `gh auth login`. `gk.sh doctor` diz o que falta.
- Remoto usa SSH (`git@github.com:...`): o `gh` funciona do mesmo jeito; só garanta `gh auth status`.
- Branch já existe: o script recusa; peça outro nome ou use a existente.
- CI vermelho: não mova para Concluído; abra a aba Actions e diga qual job falhou.
