#!/bin/zsh
set -e
TARGET="${1:-100}"
AREAS="${2:-Milano,Roma,Torino,Genova,Bologna}"
VERTICAL="${VERTICAL:-dentale}"
TARGET_SEGMENT="${RRT_TARGET_SEGMENT:-auto}"
if [[ -n "${3:-}" && "${3}" != *.csv ]]; then
  VERTICAL="$3"
  if [[ -n "${4:-}" && "${4}" != *.csv ]]; then
    TARGET_SEGMENT="$4"
    BATCH="${5:-00_PRE_SCREEN/batch_${VERTICAL}_${TARGET_SEGMENT}.csv}"
    RESULTS="${6:-00_PRE_SCREEN/batch_${VERTICAL}_${TARGET_SEGMENT}_results.csv}"
    SHORTLIST="${7:-00_PRE_SCREEN/batch_${VERTICAL}_${TARGET_SEGMENT}_shortlist.csv}"
  else
    BATCH="${4:-00_PRE_SCREEN/batch_${VERTICAL}.csv}"
    RESULTS="${5:-00_PRE_SCREEN/batch_${VERTICAL}_results.csv}"
    SHORTLIST="${6:-00_PRE_SCREEN/batch_${VERTICAL}_shortlist.csv}"
  fi
else
  BATCH="${3:-00_PRE_SCREEN/batch_${VERTICAL}.csv}"
  RESULTS="${4:-00_PRE_SCREEN/batch_${VERTICAL}_results.csv}"
  SHORTLIST="${5:-00_PRE_SCREEN/batch_${VERTICAL}_shortlist.csv}"
fi

python3 00_PRE_SCREEN/build_batch.py "$BATCH" --target "$TARGET" --areas "$AREAS" --vertical "$VERTICAL" --target-segment "$TARGET_SEGMENT"
python3 00_PRE_SCREEN/pre_screen.py "$BATCH" "$RESULTS"
python3 - "$RESULTS" "$SHORTLIST" <<'PY'
import csv, sys
src, dst = sys.argv[1], sys.argv[2]
with open(src, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
keep = [r for r in rows if r.get('decision') in {'SHORTLIST','ESCALATE'}]
with open(dst, 'w', newline='', encoding='utf-8') as f:
    if rows:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(keep)
from collections import Counter
c = Counter(r.get('decision') for r in rows)
print('\n[RRT:PRE-SCREEN] SUMMARY')
for k in ['ESCALATE','SHORTLIST','COLLECTION_RESTRICTED','REJECT']:
    print(f'{k}: {c.get(k,0)}')
print(f'TOTAL: {len(rows)}')
print(f'SHORTLIST FILE: {dst} ({len(keep)} prospect)')
PY
