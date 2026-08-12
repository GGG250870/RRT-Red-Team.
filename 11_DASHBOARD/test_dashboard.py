#!/usr/bin/env python3
import csv
import json
import tempfile
import zipfile
from pathlib import Path

from dashboard import build_dashboard


def write_fixture(path):
    rows = [
        {
            "company": "Alpha Dental",
            "domain": "alpha.example",
            "city": "Milano",
            "vertical": "dentale",
            "target_segment": "implantologia",
            "website_live": "1",
            "fetch_state": "OK",
            "D1_hits": "2",
            "D2_hits": "1",
            "D3_hits": "3",
            "D4_hits": "0",
            "D5_hits": "1",
            "contactability": "2",
            "observed_dimensions": "4",
            "high_value_hits": "2",
            "structure_hits": "1",
            "youth_growth_hits": "0",
            "commercial_gap_count": "2",
            "facebook_url": "https://facebook.com/alpha",
            "instagram_url": "",
            "linkedin_url": "",
            "tiktok_url": "",
            "social_presence_count": "1",
            "preliminary_score": "82",
            "decision": "ESCALATE",
            "google_rating": "4.7",
            "google_review_count": "120",
            "vat_id": "IT00000000000",
        },
        {
            "company": "Beta Food",
            "domain": "",
            "city": "Roma",
            "vertical": "ristorazione",
            "target_segment": "pizzeria",
            "website_live": "0",
            "fetch_state": "NO_OFFICIAL_DOMAIN",
            "D1_hits": "0",
            "D2_hits": "0",
            "D3_hits": "0",
            "D4_hits": "0",
            "D5_hits": "0",
            "contactability": "0",
            "observed_dimensions": "0",
            "high_value_hits": "0",
            "structure_hits": "0",
            "youth_growth_hits": "0",
            "commercial_gap_count": "0",
            "facebook_url": "",
            "instagram_url": "",
            "linkedin_url": "",
            "tiktok_url": "",
            "social_presence_count": "0",
            "preliminary_score": "0",
            "decision": "COLLECTION_RESTRICTED",
            "google_rating": "",
            "google_review_count": "",
            "vat_id": "",
        },
    ]
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        input_csv = root / "input.csv"
        output_dir = root / "dash"
        write_fixture(input_csv)
        payload = build_dashboard(input_csv, output_dir)
        assert payload["summary"]["total"] == 2
        assert payload["summary"]["agent_team_status"] == "AGENT_TEAM_LOCKED"
        assert payload["summary"]["target_segments"]["pizzeria"] == 1
        assert payload["summary"]["free_operation_cost_eur"] == "EUR 0.0000"
        assert (output_dir / "index.html").exists()
        assert (output_dir / "dashboard_payload.json").exists()
        assert (output_dir / "shortlist.csv").exists()
        assert (output_dir / "batch_report.md").exists()
        assert (output_dir / "batch_report.docx").exists()
        assert (output_dir / "prospects.xlsx").exists()
        assert (output_dir / "print_report.html").exists()
        assert list((output_dir / "reports").glob("*.md"))
        assert list((output_dir / "guided_reports").glob("*.md"))
        assert list((output_dir / "full_rrt_locked").glob("*.md"))
        locked = next((output_dir / "full_rrt_locked").glob("*.md")).read_text(encoding="utf-8")
        assert "AGENT_TEAM_LOCKED" in locked
        guided = next((output_dir / "guided_reports").glob("*.md")).read_text(encoding="utf-8")
        assert "NON_AGENTIC_GUIDED_REPORT" in guided
        with zipfile.ZipFile(output_dir / "prospects.xlsx") as z:
            assert "xl/worksheets/sheet1.xml" in z.namelist()
            assert "xl/worksheets/sheet2.xml" in z.namelist()
        with zipfile.ZipFile(output_dir / "batch_report.docx") as z:
            assert "word/document.xml" in z.namelist()
        data = json.loads((output_dir / "dashboard_payload.json").read_text(encoding="utf-8"))
        assert data["items"][0]["_source_coverage"]["google"] == "FOUND"
        assert data["items"][0]["_source_coverage"]["public_financials"] == "FOUND"
        assert "AGENT_TEAM_LOCKED" in (output_dir / "index.html").read_text(encoding="utf-8")
    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
