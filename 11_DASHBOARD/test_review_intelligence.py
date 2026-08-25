#!/usr/bin/env python3
import csv
import json
import tempfile
from pathlib import Path

import review_intelligence


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        input_csv = root / "reviews.csv"
        output_csv = root / "review_summary.csv"
        rows = [
            {
                "company": "Pizzeria Alpha",
                "city": "Genova",
                "source_type": "google_maps_api_export",
                "rating": "4.2",
                "review_count": "120",
                "review_text": "Ottimo impasto ma attesa lunga e servizio lento.",
            },
            {
                "company": "Pizzeria Alpha",
                "city": "Genova",
                "source_type": "tripadvisor_api_export",
                "rating": "4.0",
                "review_count": "80",
                "review_text": "Prezzo alto, prenotazione confusa, personale gentile.",
            },
        ]
        with input_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        aggregated = review_intelligence.aggregate_reviews(rows)
        assert len(aggregated) == 1
        assert aggregated[0]["review_source_count"] == 2
        assert aggregated[0]["avg_rating"] == 4.1
        assert aggregated[0]["review_risk_state"] == "REVIEW_FRICTION"
        review_intelligence.write_csv(output_csv, aggregated)
        assert output_csv.exists()
    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
