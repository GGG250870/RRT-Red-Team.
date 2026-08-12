#!/usr/bin/env python3
import csv
import json
import tempfile
from pathlib import Path

import build_batch


def fake_fetch_json(url, data=None, retries=1):
    if "nominatim.openstreetmap.org" in url:
        assert "city=Milano" in url
        return [{
            "display_name": "Milano, Lombardia, Italia",
            "boundingbox": ["45.40", "45.55", "9.05", "9.30"],
            "address": {"city": "Milano"},
        }]
    if "overpass-api.de" in url:
        return {
            "elements": [
                {
                    "type": "node",
                    "id": 123,
                    "lat": 45.46,
                    "lon": 9.19,
                    "tags": {
                        "name": "Pizzeria Alpha",
                        "amenity": "restaurant",
                        "cuisine": "pizza",
                        "website": "https://pizzeria-alpha.example",
                        "phone": "+39021234567",
                        "contact:mobile": "+393331234567",
                        "email": "info@pizzeria-alpha.example",
                        "addr:street": "Via Roma",
                        "addr:housenumber": "10",
                        "addr:postcode": "20100",
                        "addr:city": "Milano",
                    },
                },
                {
                    "type": "node",
                    "id": 124,
                    "lat": 45.41,
                    "lon": 9.07,
                    "tags": {
                        "name": "Pizzeria Fuori Area",
                        "amenity": "restaurant",
                        "cuisine": "pizza",
                        "addr:city": "Trezzano sul Naviglio",
                    },
                }
            ]
        }
    return None


def main():
    original_fetch_json = build_batch.fetch_json
    original_sleep = build_batch.time.sleep
    build_batch.fetch_json = fake_fetch_json
    build_batch.time.sleep = lambda _seconds: None
    try:
        with tempfile.TemporaryDirectory() as cache_td:
            cache_path = Path(cache_td) / "bbox_cache.json"
            rows = build_batch.discover_area_auto("Milano", "ristorazione", "pizzeria", 10, bbox_cache_path=cache_path)
            assert cache_path.exists()
        assert len(rows) == 1
        row = rows[0]
        assert row["company"] == "Pizzeria Alpha"
        assert row["domain"] == "pizzeria-alpha.example"
        assert row["phone"] == "+39021234567"
        assert row["mobile_phone"] == "+393331234567"
        assert row["email"] == "info@pizzeria-alpha.example"
        assert row["address"] == "Via Roma 10 20100 Milano"
        assert row["official_domain_state"] == "RESOLVED_FROM_OSM_WEBSITE"
        assert row["google_url"].startswith("https://www.google.com/maps/search/")
        manual_bbox = build_batch.parse_bbox("45.40,9.05,45.55,9.30", label="manual_bbox:Milano")
        manual_rows = build_batch.discover_area_auto(
            "Milano", "ristorazione", "pizzeria", 10, bbox_override=manual_bbox, bbox_cache_path=None
        )
        assert len(manual_rows) == 1

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "batch.csv"
            fields = [
                "company", "domain", "source_url", "area", "city", "country", "vertical", "target_segment",
                "phone", "mobile_phone", "email", "address", "latitude", "longitude",
                "google_url", "registroimprese_url",
                "discovery_source", "review_source", "discovery_query", "official_domain_state", "official_domain_source",
            ]
            with output.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            assert output.exists()
    finally:
        build_batch.fetch_json = original_fetch_json
        build_batch.time.sleep = original_sleep
    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
