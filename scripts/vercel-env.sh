#!/usr/bin/env bash
# vercel-env.sh - envia ao Vercel as variáveis que a API precisa, lidas do .env.local.
# Precisa do login (npx vercel login) e do vínculo (npx vercel link) feitos antes.
# Uso: scripts/vercel-env.sh [ORIGENS_DO_FRONT]
#   ORIGENS_DO_FRONT: endereços do front-end separados por vírgula (vira CORS_ORIGENS).
#   Sem ele, o CORS fica com o padrão de desenvolvimento até o front ter endereço.
set -euo pipefail

die() { echo "erro: $*" >&2; exit 1; }

RAIZ=$(git rev-parse --show-toplevel 2>/dev/null) || die "rode dentro do repositório"
cd "$RAIZ"
[[ -f .env.local ]] || die "crie o .env.local a partir do .env.example"
[[ -f .vercel/project.json ]] || die "projeto não vinculado. Rode: npx vercel link"

set -a
# shellcheck disable=SC1091
source .env.local
set +a
[[ -n "${DATABASE_URL:-}" ]] || die "DATABASE_URL vazia no .env.local"

VERCEL=(npx -y vercel@65.2.0)

# Valor pelo stdin para não aparecer na lista de processos. --force sobrescreve o que já existe.
enviar() {
  local nome=$1 valor=$2 ambiente=$3 tipo=$4 saida
  # A CLI escreve tudo no stderr: só mostra a saída dela quando falha.
  if ! saida=$(printf '%s' "$valor" | "${VERCEL[@]}" env add "$nome" \
      --environment "$ambiente" "--$tipo" --force --yes 2>&1); then
    echo "$saida" >&2
    die "não consegui enviar $nome ($ambiente)"
  fi
  echo "  $nome ($ambiente)"
}

# Só o que a API usa em execução. Migrações continuam rodando do CI ou da máquina local
# com DATABASE_URL_UNPOOLED; TEST_DATABASE_URL e PG* ficam fora do deploy.
for ambiente in production preview; do
  # Preview mostra /docs para a equipe testar; produção desliga.
  [[ $ambiente == production ]] && modo=producao || modo=desenvolvimento
  enviar DATABASE_URL "$DATABASE_URL" "$ambiente" sensitive
  enviar AMBIENTE "$modo" "$ambiente" no-sensitive
  enviar BANCO_TIMEOUT_SEGUNDOS "${BANCO_TIMEOUT_SEGUNDOS:-5}" "$ambiente" no-sensitive
  if [[ -n "${1:-}" ]]; then
    enviar CORS_ORIGENS "$1" "$ambiente" no-sensitive
  fi
done

echo "Pronto. Confira com: npx vercel env ls"
