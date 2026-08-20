#!/bin/zsh
set -e

INPUT="${1:-00_PRE_SCREEN/batch_dentale_results.csv}"
OUTPUT="${2:-11_DASHBOARD/out}"
ENRICH="${RRT_DASHBOARD_ENRICH:-1}"

if [[ "$ENRICH" == "1" ]]; then
  ENRICHED="$OUTPUT/enriched_input.csv"
  python3 11_DASHBOARD/enrich_public_sources.py "$INPUT" "$ENRICHED"
  INPUT="$ENRICHED"
fi

python3 11_DASHBOARD/dashboard.py "$INPUT" "$OUTPUT"
echo "Dashboard HTML: $OUTPUT/index.html"
