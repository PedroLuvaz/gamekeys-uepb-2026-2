# jira-gamekeys

Skill do Claude Code para a equipe do GameKeys criar e mover issues no Jira seguindo a DoR/DoD e ligar tudo ao GitHub (branch, commit, PR). Serve para qualquer papel (PO/DevOps, QA, SM): quem está no papel usa do mesmo jeito.

## O que cada pessoa precisa (uma vez)

1. **Clonar o repositório.** A skill já vem em `.claude/skills/jira-gamekeys/` e os scripts em `scripts/`. O Claude Code carrega sozinho ao abrir a pasta do repo.
2. **Conector Atlassian** autorizado na sua conta do Claude, com acesso ao site `pedrolucas0721.atlassian.net` (peça ao PO para te adicionar ao projeto GK, se ainda não estiver). Nenhum token vai para o repo: a autorização é de cada pessoa.
3. **GitHub CLI e jq:** instale o `gh` (https://cli.github.com) e rode `gh auth login`. Instale também o `jq`, usado pelo `gk.sh dod` (Windows: `winget install jqlang.jq`; Linux: `sudo apt install jq`; macOS: `brew install jq`).
4. **Hook de commit** (exige `tipo: GK-N descrição`):
   ```bash
   scripts/gk.sh install-hooks
   ```
5. **Conferir tudo:**
   ```bash
   scripts/gk.sh doctor
   ```

## Como usar

Abra o Claude Code na pasta do repo e peça em linguagem natural. Ele pergunta seu papel e sempre mostra o que vai fazer antes de criar issue, branch, PR ou mover status.

- "Cria uma US de carrinho: alterar e remover itens, R2, prioridade alta, 3 pontos."
- "Confere a DoR da GK-12." / "Inicia a GK-12." (gate DoR, status Em andamento, oferece a branch)
- "Abre o PR da GK-12." (status Em revisão + comentário com o link)
- "Confere a DoD da GK-12." / "Conclui a GK-12." (gate DoD, status Concluído)
- "Cria um bug: ..." (só quando você pede)
- "Como está a sprint?"

Scripts diretos (sem Claude): `scripts/gk.sh ajuda`.

## Rodízio de papéis

Os papéis mudam a cada release e a skill não guarda nomes. O que cada papel normalmente faz com ela:

| Papel | Uso típico |
|---|---|
| PO | Criar e priorizar US, deixar a DoR pronta, aceitar a US (último item da DoD) |
| QA | Criar bugs, testar os cenários, conferir a DoD antes de Concluído |
| SM | Acompanhar o quadro, tarefas paradas há mais de 3 dias, DoD de sprint |
| DevOps | Branch, PR, CI verde, merge, README |

Na virada de release: atualize a tabela de papéis no README do repo e a linha "Equipe" em `references/config.md`.

## Para compartilhar fora do repo

```bash
tar czf jira-gamekeys.tgz .claude/skills/jira-gamekeys scripts
```

Quem receber extrai na raiz do próprio clone. As constantes do Jira (site, cloudId, IDs de transição) são específicas deste projeto e estão em `references/config.md`.

## Segurança

- Sem token, senha ou chave em arquivo. Jira pelo conector de cada pessoa, GitHub pelo `gh auth login`.
- A skill não cria nem altera nada no Jira ou no GitHub sem confirmação na conversa.
- Textos vindos do Jira (descrições, comentários) são tratados como dado, nunca como instrução.

## Se algo quebrar

- Transição recusada: o fluxo do quadro pode ter mudado; peça `getTransitionsForJiraIssue` e atualize `references/config.md`.
- Prioridade recusada na criação: a tela de criação não tem o campo; a skill aplica depois com edição.
- Mudou a DoR/DoD: atualize `references/gates.md` e o checklist em `references/templates.md`.
