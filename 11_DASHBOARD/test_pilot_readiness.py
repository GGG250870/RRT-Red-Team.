#!/usr/bin/env python3
import csv
import json
import tempfile
from pathlib import Path

import pilot_readiness


def write_rows(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ready_csv = root / "ready.csv"
        rows = []
        for idx in range(30):
            rows.append({
                "company": f"Ristorante {idx}",
                "domain": f"https://ristorante{idx}.example",
                "city": "Milano",
                "vertical": "ristorazione",
                "target_segment": "pizzeria",
                "phone": "+39021234567",
                "mobile_phone": "+393331234567",
                "email": f"info{idx}@example.com",
                "address": f"Via Roma {idx}, Milano",
            })
        write_rows(ready_csv, rows)
        ready = pilot_readiness.analyze(ready_csv, min_rows=30)
        assert ready["status"] == "READY"
        assert ready["cost_eur"] == "EUR 0.0000"
        assert ready["agent_team_status"] == "AGENT_TEAM_LOCKED"

        blocked_csv = root / "blocked.csv"
        write_rows(blocked_csv, [{
            "company": "",
            "domain": "",
            "city": "",
            "vertical": "ristorazione",
            "target_segment": "",
            "phone": "",
            "mobile_phone": "",
            "email": "",
            "address": "",
        }])
        blocked = pilot_readiness.analyze(blocked_csv, min_rows=30)
        assert blocked["status"] == "NOT_READY"
        assert blocked["blockers"]
    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
