#!/bin/zsh
set -e
TARGET="${1:-100}"
AREAS="${2:-Milano Navigli,Roma Prati,Torino Crocetta,Genova Albaro,Bologna Centro}"
BATCH="${3:-00_PRE_SCREEN/batch_dentale.csv}"
RESULTS="${4:-00_PRE_SCREEN/batch_dentale_results.csv}"
SHORTLIST="${5:-00_PRE_SCREEN/batch_dentale_shortlist.csv}"

python3 00_PRE_SCREEN/build_batch.py "$BATCH" --target "$TARGET" --areas "$AREAS"
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
