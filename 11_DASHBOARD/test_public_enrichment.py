#!/usr/bin/env python3
import csv
import json
import tempfile
from pathlib import Path

import enrich_public_sources


HTML = """<!doctype html>
<html>
<head>
  <title>Alpha Impresa</title>
  <meta name="description" content="Soluzioni B2B certificate e assistenza.">
</head>
<body>
  <a href="https://www.facebook.com/alphaimpresa">Facebook</a>
  <a href="https://www.linkedin.com/company/alphaimpresa">LinkedIn</a>
  <a href="https://www.trustpilot.com/review/alpha.example">Trustpilot</a>
  <a href="/bilanci/alpha-bilancio-2025.pdf">Bilancio 2025</a>
</body>
</html>
"""


def fake_fetch(url):
    return {
        "state": "OK",
        "url": url,
        "robots_state": "TEST_ROBOTS_ALLOWED",
        "html": HTML,
    }


def write_fixture(path):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company", "domain", "city", "vertical", "target_segment"])
        writer.writeheader()
        writer.writerow({"company": "Alpha Impresa", "domain": "https://alpha.example/", "city": "Milano", "vertical": "ristorazione", "target_segment": "fine_dining"})


def main():
    original_fetch = enrich_public_sources.fetch
    enrich_public_sources.fetch = fake_fetch
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            input_csv = root / "input.csv"
            output_csv = root / "out.csv"
            write_fixture(input_csv)
            rows = enrich_public_sources.enrich_csv(input_csv, output_csv, limit=5)
            assert rows[0]["online_enrichment_state"] == "OK"
            assert rows[0]["official_title"] == "Alpha Impresa"
            assert rows[0]["facebook_url"] == "https://www.facebook.com/alphaimpresa"
            assert rows[0]["linkedin_url"] == "https://www.linkedin.com/company/alphaimpresa"
            assert rows[0]["review_portal_url"] == "https://www.trustpilot.com/review/alpha.example"
            assert rows[0]["financial_source_url"] == "https://alpha.example/bilanci/alpha-bilancio-2025.pdf"
            assert rows[0]["free_online_enrichment_cost_eur"] == "EUR 0.0000"
            refs = json.loads(rows[0]["source_refs_json"])
            assert refs["google_maps_search_url"].startswith("https://www.google.com/maps/search/")
            assert "tripadvisor.it" in refs["restaurant_review_search_urls"]
            assert "michelin.com" in refs["restaurant_review_search_urls"]
            assert output_csv.exists()
    finally:
        enrich_public_sources.fetch = original_fetch
    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
