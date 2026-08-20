#!/usr/bin/env python3
import csv
import json
import tempfile
from pathlib import Path

import entity_resolution


def write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    seed = [
        {
            "company": "Pizzeria da Marco",
            "city": "Genova",
            "address": "Via Vincenzo Maculano 35r",
            "vertical": "ristorazione",
        },
        {
            "company": "Ristorante Agueta",
            "city": "Genova",
            "address": "",
            "vertical": "ristorazione",
        },
        {
            "company": "Terra e fuoco",
            "city": "Genova",
            "address": "",
            "vertical": "ristorazione",
        },
    ]
    links = [
        {
            "company": "Pizzeria da Marco",
            "city": "Genova",
            "address": "Via Vincenzo Maculano 35r",
            "source": "restaurantguru",
            "source_url": "https://restaurantguru.it/Pizzeria-da-Marco-Genoa",
        },
        {
            "company": "L'Agueta du Sciria",
            "city": "Arenzano",
            "address": "",
            "source": "tripadvisor",
            "source_url": "https://www.tripadvisor.it/Restaurant_Review-g780707-d2018231-Reviews-L_Agueta_du_Sciria-Arenzano_Italian_Riviera_Liguria.html",
        },
    ]
    resolved = entity_resolution.resolve_rows(seed, links)
    by_company = {row["company"]: row for row in resolved}
    assert by_company["Pizzeria da Marco"]["entity_resolution_state"] == "MATCH_CONFIRMED"
    assert by_company["Ristorante Agueta"]["entity_resolution_state"] in {
        "OUT_OF_AREA_OR_ENTITY_CONFLICT",
        "NEEDS_REVIEW_LINKS",
    }
    assert by_company["Terra e fuoco"]["entity_resolution_state"] == "NEEDS_REVIEW_LINKS"
    assert by_company["Pizzeria da Marco"]["restaurantguru_verified_url"].startswith("https://restaurantguru.it/")
    assert by_company["Terra e fuoco"]["google_search_url"].startswith("https://www.google.com/maps/search/")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed_csv = root / "seed.csv"
        links_csv = root / "links.csv"
        out_csv = root / "resolved.csv"
        write_rows(seed_csv, seed)
        write_rows(links_csv, links)
        entity_resolution.main.__globals__["__name__"]
        rows = entity_resolution.resolve_rows(entity_resolution.read_csv(seed_csv), entity_resolution.read_csv(links_csv))
        entity_resolution.write_csv(out_csv, rows)
        assert out_csv.exists()
    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
