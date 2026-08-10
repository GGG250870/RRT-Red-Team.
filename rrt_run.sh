#!/bin/zsh
set -euo pipefail

CASE_ID="${1:-B04-34}"
MODE="${2:---live}"

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

printf '\n[RRT] Pull aggiornamenti...\n'
git pull --ff-only

printf '\n[RRT] Test runtime...\n'
python3 02_AGENTS/runtime/test_runtime.py

printf '\n[RRT] Wave 4-7 con resume: %s\n' "$CASE_ID"
python3 02_AGENTS/runtime/wave4_7_runner.py --case-id "$CASE_ID" "$MODE" --resume
