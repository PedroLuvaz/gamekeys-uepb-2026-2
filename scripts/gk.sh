#!/usr/bin/env bash
# gk.sh - parte git/gh do fluxo Jira + GitHub do GameKeys.
# Não fala com o Jira e não guarda token: usa só git e o login do próprio gh.
# Uso: scripts/gk.sh ajuda
set -euo pipefail

REPO_SLUG="PedroLuvaz/gamekeys-uepb-2026-2"
JIRA_BASE="https://pedrolucas0721.atlassian.net"
TIPOS_BRANCH="feature fix docs chore refactor test"

die() { echo "erro: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "'$1' não encontrado. Rode: scripts/gk.sh doctor"; }
valida_chave() { [[ "$1" =~ ^GK-[0-9]+$ ]] || die "chave inválida '$1' (esperado GK-N, ex.: GK-12)"; }

repo_root() { git rev-parse --show-toplevel 2>/dev/null || die "rode dentro do repositório"; }

base_branch() {
  local ref
  ref=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  echo "${ref#origin/}" | sed -E 's/^$/main/'
}

# Troca letra a letra (s///g) em vez de "sed y": o "y" com acentos falha quando o terminal
# não está em UTF-8 (ex.: Git Bash sem LANG), e s///g compara bytes, então funciona em qualquer locale.
SED_ACENTOS=""
for par in ÁA ÀA ÂA ÃA ÄA áa àa âa ãa äa ÉE ÈE ÊE ËE ée èe êe ëe ÍI ÌI ÎI ÏI íi ìi îi ïi \
           ÓO ÒO ÔO ÕO ÖO óo òo ôo õo öo ÚU ÙU ÛU ÜU úu ùu ûu üu ÇC çc ÑN ñn; do
  SED_ACENTOS+="s/${par%?}/${par: -1}/g;"
done

slugify() {
  printf '%s' "$1" \
    | sed -e "$SED_ACENTOS" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' \
    | cut -c1-50 | sed -E 's/-+$//'
}

# feature -> feat, demais tipos iguais
tipo_commit() { [[ "$1" == "feature" ]] && echo "feat" || echo "$1"; }

cmd_ajuda() {
  cat <<'EOF'
gk.sh - fluxo git/gh do GameKeys

  branch <GK-N> <tipo> "<descrição>" [--dry-run]
      Cria <tipo>/GK-N-descricao a partir de origin/<base>. Tipos: feature fix docs chore refactor test.
  pr <GK-N> "<descrição>" [--issue N] [--draft] [--base B] [--dry-run]
      Faz push da branch atual e abre o PR com a chave no título e no corpo.
  dod <GK-N | nº do PR>
      Mostra os itens de DoD que vêm do GitHub (merge, revisão, CI, commit, testes, README).
  find-pr <GK-N>
      Lista PRs ligados à chave.
  install-hooks
      Ativa scripts/hooks (commit-msg exige "tipo: GK-N descrição"). Uma vez por clone.
  doctor
      Confere git, gh, jq, login e hooks.
EOF
}

cmd_branch() {
  local key="${1:-}" tipo="${2:-}" desc="${3:-}" dry=0
  [[ $# -ge 3 ]] || die "uso: gk.sh branch GK-N <tipo> \"<descrição>\" [--dry-run]"
  shift 3
  for a in "$@"; do [[ "$a" == "--dry-run" ]] && dry=1 || die "opção desconhecida: $a"; done
  valida_chave "$key"
  [[ " $TIPOS_BRANCH " == *" $tipo "* ]] || die "tipo '$tipo' inválido. Use: $TIPOS_BRANCH"
  local slug name base
  slug=$(slugify "$desc"); [[ -n "$slug" ]] || die "descrição vazia"
  name="$tipo/$key-$slug"
  base=$(base_branch)
  echo "branch: $name"
  echo "base:   origin/$base"
  if [[ $dry -eq 1 ]]; then echo "(dry-run: nada foi criado)"; return 0; fi
  repo_root >/dev/null
  git show-ref --verify --quiet "refs/heads/$name" && die "a branch $name já existe"
  git fetch origin "$base" --quiet
  git ls-remote --exit-code --heads origin "$name" >/dev/null 2>&1 && die "a branch $name já existe no remoto"
  git switch -c "$name" --no-track "origin/$base"
  echo "criada e ativa: $name"
}

# monta o corpo do PR a partir do template do repo
corpo_pr() {
  local key="$1" issue="${2:-}" root tpl
  root=$(repo_root); tpl="$root/.github/pull_request_template.md"
  if [[ -f "$tpl" ]]; then
    # sub(\r) porque no Windows com autocrlf o template vem com CRLF e "GK-" nunca bateria
    awk -v linha="$key - $JIRA_BASE/browse/$key" '{sub(/\r$/, "")} $0=="GK-" {print linha; next} {print}' "$tpl"
  else
    printf '## Chave no Jira\n\n%s - %s/browse/%s\n' "$key" "$JIRA_BASE" "$key"
  fi
  if [[ -n "$issue" ]]; then printf '\nCloses #%s\n' "$issue"; fi
}

cmd_pr() {
  local key="${1:-}" desc="${2:-}" issue="" draft=0 dry=0 base=""
  [[ $# -ge 2 ]] || die "uso: gk.sh pr GK-N \"<descrição>\" [--issue N] [--draft] [--base B] [--dry-run]"
  shift 2
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --issue) issue="${2:-}"; [[ "$issue" =~ ^[0-9]+$ ]] || die "--issue pede um número"; shift 2 ;;
      --base)  base="${2:-}"; [[ -n "$base" ]] || die "--base pede um nome de branch"; shift 2 ;;
      --draft) draft=1; shift ;;
      --dry-run) dry=1; shift ;;
      *) die "opção desconhecida: $1" ;;
    esac
  done
  valida_chave "$key"
  [[ -n "${desc// }" ]] || die "descrição vazia"
  local branch prefixo titulo body
  branch=$(git rev-parse --abbrev-ref HEAD)
  [[ "$branch" == *"$key"* ]] || die "a branch atual ($branch) não contém $key"
  prefixo="${branch%%/*}"
  [[ " $TIPOS_BRANCH " == *" $prefixo "* ]] || die "prefixo '$prefixo' da branch fora do padrão ($TIPOS_BRANCH)"
  [[ -n "$base" ]] || base=$(base_branch)
  titulo="$(tipo_commit "$prefixo"): $key $desc"
  body=$(corpo_pr "$key" "$issue")
  echo "branch: $branch -> $base"
  echo "título: $titulo"
  echo "--- corpo ---"; echo "$body"; echo "-------------"
  if [[ $dry -eq 1 ]]; then echo "(dry-run: nada foi enviado)"; return 0; fi
  need gh
  local existente
  existente=$(gh pr list --head "$branch" --state open --json url --jq '.[0].url // empty')
  [[ -z "$existente" ]] || die "já existe PR aberto para $branch: $existente"
  git push -u origin "$branch"
  local args=(pr create --base "$base" --head "$branch" --title "$titulo" --body "$body")
  [[ $draft -eq 1 ]] && args+=(--draft)
  gh "${args[@]}"
}

# acha o número do PR a partir da chave ou do número
resolve_pr() {
  local alvo="$1"
  if [[ "$alvo" =~ ^[0-9]+$ ]]; then echo "$alvo"; return; fi
  valida_chave "$alvo"
  gh pr list --state all --limit 100 --json number,title,headRefName \
    --jq "[.[] | select((.title | contains(\"$alvo\")) or (.headRefName | contains(\"$alvo\")))] | sort_by(-.number) | .[0].number // empty"
}

cmd_find_pr() {
  local key="${1:-}"; valida_chave "$key"; need gh
  gh pr list --state all --limit 100 --json number,title,headRefName,state,url \
    --jq ".[] | select((.title | contains(\"$key\")) or (.headRefName | contains(\"$key\"))) | \"#\(.number) [\(.state)] \(.title) \(.url)\""
}

ok_falta() { if [[ "$1" == "1" ]]; then echo "OK    $2"; else echo "FALTA $2"; fi; }

cmd_dod() {
  local alvo="${1:-}"; [[ -n "$alvo" ]] || die "uso: gk.sh dod <GK-N | nº do PR>"
  need gh; need jq
  local pr key=""
  [[ "$alvo" =~ ^GK- ]] && key="$alvo"
  pr=$(resolve_pr "$alvo"); [[ -n "$pr" ]] || die "nenhum PR encontrado para $alvo"
  local json
  json=$(gh pr view "$pr" --json number,url,title,state,mergedAt,author,reviews,statusCheckRollup,commits,files,headRefName)
  [[ -n "$key" ]] || key=$(jq -r '(.title + " " + .headRefName) | capture("(?<k>GK-[0-9]+)").k // empty' <<<"$json")
  echo "PR #$pr $(jq -r '.url' <<<"$json")"
  echo "título: $(jq -r '.title' <<<"$json")  estado: $(jq -r '.state' <<<"$json")  autor: $(jq -r '.author.login' <<<"$json")"
  echo "chave:  ${key:-não identificada}"
  echo
  local merged revisores ci_total ci_ruins ci_pend commits_chave testes readme
  merged=$(jq -r 'if .mergedAt then 1 else 0 end' <<<"$json")
  ok_falta "$merged" "PR mesclado na main"
  local autor; autor=$(jq -r '.author.login' <<<"$json")
  revisores=$(jq -r --arg a "$autor" '[.reviews[] | select(.state=="APPROVED" and .author.login != $a) | .author.login] | unique | join(", ")' <<<"$json")
  ok_falta "$([[ -n "$revisores" ]] && echo 1 || echo 0)" "revisado e aprovado por outro integrante ${revisores:+($revisores)}"
  if [[ -n "$key" ]]; then
    commits_chave=$(jq -r --arg k "$key" '[.commits[] | select((.messageHeadline + " " + (.messageBody // "")) | contains($k))] | length' <<<"$json")
    ok_falta "$([[ "$commits_chave" -gt 0 ]] && echo 1 || echo 0)" "commit cita $key ($commits_chave de $(jq '.commits|length' <<<"$json") commits)"
  else
    ok_falta 0 "commit cita a chave Jira (chave não identificada)"
  fi
  ci_total=$(jq '[.statusCheckRollup[]?] | length' <<<"$json")
  ci_ruins=$(jq '[.statusCheckRollup[]? | (.conclusion // .state // "") | select(. == "FAILURE" or . == "ERROR" or . == "CANCELLED" or . == "TIMED_OUT" or . == "ACTION_REQUIRED")] | length' <<<"$json")
  ci_pend=$(jq '[.statusCheckRollup[]? | select((.status // "COMPLETED") != "COMPLETED" or .state == "PENDING")] | length' <<<"$json")
  if [[ "$ci_total" -eq 0 ]]; then
    ok_falta 0 "CI verde (nenhum check encontrado no PR)"
  else
    ok_falta "$([[ "$ci_ruins" -eq 0 && "$ci_pend" -eq 0 ]] && echo 1 || echo 0)" "CI verde ($ci_total checks, $ci_ruins com falha, $ci_pend pendentes)"
  fi
  # [.] em vez de \\. : barra invertida se perde ao passar argumento para jq.exe no Windows
  testes=$(jq -r '[.files[].path | select(test("(^|/)(tests?|__tests__|cypress)/|test_.*[.]py$|[.](test|spec)[.][jt]sx?$|[.]feature$"))] | length' <<<"$json")
  ok_falta "$([[ "$testes" -gt 0 ]] && echo 1 || echo 0)" "testes adicionados ou alterados no PR ($testes arquivos)"
  readme=$(jq -r '[.files[].path | select(test("(^|/)README[.]md$"))] | length' <<<"$json")
  echo "INFO  README tocado no PR: $([[ "$readme" -gt 0 ]] && echo sim || echo não) (só é exigido se mudou a forma de rodar o projeto)"
  echo
  echo "Não verificáveis aqui (confirmar com o papel responsável): cenários testados pelo QA, aceite do PO, homologação."
}

cmd_install_hooks() {
  local root; root=$(repo_root)
  [[ -d "$root/scripts/hooks" ]] || die "scripts/hooks não existe"
  chmod +x "$root"/scripts/hooks/* "$root/scripts/gk.sh" 2>/dev/null || true
  git config core.hooksPath scripts/hooks
  echo "hooks ativos (core.hooksPath=scripts/hooks). Para desativar: git config --unset core.hooksPath"
}

cmd_doctor() {
  local falhas=0
  chk() { if "${@:2}" >/dev/null 2>&1; then echo "OK    $1"; else echo "FALTA $1"; falhas=1; fi; }
  chk "git instalado" command -v git
  chk "jq instalado (necessário para 'dod')" command -v jq
  chk "gh instalado (https://cli.github.com)" command -v gh
  if command -v gh >/dev/null 2>&1; then chk "gh autenticado (gh auth login)" gh auth status; fi
  chk "remoto origin configurado" git remote get-url origin
  if [[ "$(git config --get core.hooksPath 2>/dev/null || true)" == "scripts/hooks" ]]; then
    echo "OK    hooks ativos"
  else
    echo "FALTA hooks ativos (rode: scripts/gk.sh install-hooks)"; falhas=1
  fi
  [[ $falhas -eq 0 ]] && echo "tudo certo" || echo "há pendências acima"
  return 0
}

main() {
  local cmd="${1:-ajuda}"; shift || true
  case "$cmd" in
    branch) cmd_branch "$@" ;;
    pr) cmd_pr "$@" ;;
    dod) cmd_dod "$@" ;;
    find-pr) cmd_find_pr "$@" ;;
    install-hooks) cmd_install_hooks ;;
    doctor) cmd_doctor ;;
    ajuda|-h|--help|help) cmd_ajuda ;;
    *) die "comando desconhecido: $cmd (veja: gk.sh ajuda)" ;;
  esac
}

main "$@"
