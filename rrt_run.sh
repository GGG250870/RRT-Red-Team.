#!/bin/zsh
set -u

CASE_ID="${1:-B04-34}"
MODE="${2:---live}"
MAX_ATTEMPTS="${RRT_LAUNCHER_MAX_ATTEMPTS:-3}"
RETRY_DELAY="${RRT_LAUNCHER_RETRY_SECONDS:-3}"

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

printf '\n[RRT] Pull aggiornamenti...\n'
git pull --ff-only || exit 20

printf '\n[RRT] Test runtime...\n'
python3 02_AGENTS/runtime/test_runtime.py || exit 21

attempt=1
while (( attempt <= MAX_ATTEMPTS )); do
  printf '\n[RRT] Wave 4-7 con resume: %s (tentativo %d/%d)\n' "$CASE_ID" "$attempt" "$MAX_ATTEMPTS"

  tmpfile="$(mktemp -t rrt_wave47.XXXXXX)"
  python3 02_AGENTS/runtime/wave4_7_runner.py --case-id "$CASE_ID" "$MODE" --resume 2>&1 | tee "$tmpfile"
  rc=${pipestatus[1]}

  if (( rc == 0 )); then
    rm -f "$tmpfile"
    exit 0
  fi

  if grep -Eq 'TECHNICAL_STAGE_FAILURE|TRUNCATED_JSON|FAIL_JSON|Error code: 5(02|03|04|20)|retryable[^A-Za-z0-9]*(true|True)|rate limit|timeout|temporarily unavailable|connection error' "$tmpfile"; then
    if (( attempt < MAX_ATTEMPTS )); then
      printf '\n[RRT] Errore tecnico recuperabile. Riprovo dal checkpoint tra %ss...\n' "$RETRY_DELAY"
      rm -f "$tmpfile"
      sleep "$RETRY_DELAY"
      attempt=$((attempt + 1))
      continue
    fi
    printf '\n[RRT] Limite retry tecnici raggiunto. Mi fermo senza rifare gli stage già validi.\n'
    rm -f "$tmpfile"
    exit "$rc"
  fi

  printf '\n[RRT] Blocco logico/non recuperabile: nessun retry automatico.\n'
  rm -f "$tmpfile"
  exit "$rc"
done
