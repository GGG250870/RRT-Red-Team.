#!/bin/zsh
set -u

CASE_ID="${1:-}"
COMPANY="${2:-}"
OFFICIAL_DOMAIN="${3:-}"
MODE="${4:---live}"

if [[ -z "$CASE_ID" || -z "$COMPANY" || -z "$OFFICIAL_DOMAIN" ]]; then
  echo 'Uso: ./rrt_e2e.sh CASE_ID "Company" https://dominio.tld [--live]'
  exit 2
fi

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

export RRT_BUDGET_PER_CASE_USD="${RRT_BUDGET_PER_CASE_USD:-3.00}"

printf '\n[RRT:E2E] Test runtime...\n'
python3 02_AGENTS/runtime/test_runtime.py || exit 21

printf '\n[RRT:E2E] Avvio completo A1→A9: %s | %s\n' "$CASE_ID" "$COMPANY"
python3 02_AGENTS/runtime/end_to_end_runner.py --case-id "$CASE_ID" --company "$COMPANY" --official-domain "$OFFICIAL_DOMAIN" "$MODE"
