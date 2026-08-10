#!/bin/zsh
set -u

CASE_ID="${1:-B04-34}"
MODE="${2:---live}"
MAX_ATTEMPTS="${RRT_LAUNCHER_MAX_ATTEMPTS:-3}"
RETRY_DELAY="${RRT_LAUNCHER_RETRY_SECONDS:-3}"

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Validation runs can legitimately exceed the normal $2/case guard because they
# include retries and benchmark discovery. Keep production defaults untouched;
# this launcher opts into a higher case ceiling unless the caller overrides it.
export RRT_BUDGET_PER_CASE_USD="${RRT_BUDGET_PER_CASE_USD:-3.00}"

printf '\n[RRT] Pull aggiornamenti...\n'
# Runtime state is intentionally local and ignored by Git. If only the launcher
# itself has local edits, preserve them automatically so Git can fast-forward.
local_changes="$(git status --porcelain --untracked-files=normal | grep -vE '^\?\? 02_AGENTS/runtime/state/' || true)"
if [[ -n "$local_changes" ]]; then
  non_launcher="$(printf '%s\n' "$local_changes" | grep -vE '^.. rrt_run\.sh$' || true)"
  if [[ -n "$non_launcher" ]]; then
    printf '[RRT] Modifiche locali fuori da rrt_run.sh: pull bloccato per sicurezza.\n'
    printf '%s\n' "$non_launcher"
    exit 19
  fi
  git stash push -m "rrt-launcher-autostash" -- rrt_run.sh >/dev/null
fi

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

  # Never retry budget or logical gate failures. These cannot heal by repetition.
  if grep -Eq 'CASE_BUDGET_EXCEEDED|BUDGET_BLOCK|A6_(UNRESOLVED|COLLECTION_RESTRICTED|NO_BENCHMARKS|NO_FIT_BASIS)|A7_(FALSIFIED|UNCERTIFIED)|A8_INVALID_SIGNAL_CLASS|CONTRADICTIONS_PRESENT' "$tmpfile"; then
    printf '\n[RRT] Blocco logico/budget: nessun retry automatico.\n'
    rm -f "$tmpfile"
    exit "$rc"
  fi

  # Retry only concrete transient/parse failures.
  if grep -Eq 'TRUNCATED_JSON|FAIL_JSON|Error code: 5(02|03|04|20)|retryable[^A-Za-z0-9]*(true|True)|rate limit|timeout|temporarily unavailable|connection error' "$tmpfile"; then
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

  printf '\n[RRT] Blocco non classificato: nessun retry automatico.\n'
  rm -f "$tmpfile"
  exit "$rc"
done
