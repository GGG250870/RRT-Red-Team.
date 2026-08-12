#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


NEGATIVE_HINTS = {
    "attesa", "lento", "freddo", "caro", "prezzo", "scortese", "sporco",
    "rumore", "deluso", "deludente", "pessimo", "terribile", "mai piu",
    "servizio", "conto", "prenotazione", "fila", "qualita",
}
POSITIVE_HINTS = {
    "ottimo", "eccellente", "gentile", "consiglio", "qualita", "buono",
    "perfetto", "accogliente", "veloce", "fresco", "ritornero", "bravi",
}
SUPPORTED_SOURCES = {"google_maps_api_export", "tripadvisor_api_export", "manual_review_export"}


def norm(value):
    return (value or "").strip()


def as_float(value):
    try:
        return float(norm(value).replace(",", ".") or 0)
    except ValueError:
        return 0.0


def as_int(value):
    try:
        return int(float(norm(value) or 0))
    except ValueError:
        return 0


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = fieldnames or sorted({k for row in rows for k in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def company_key(row):
    raw = norm(row.get("company")) or norm(row.get("name")) or norm(row.get("business_name"))
    raw = raw.lower()
    return re.sub(r"[^a-z0-9à-ÿ]+", " ", raw).strip()


def review_text(row):
    return " ".join(norm(row.get(col)) for col in ["review_text", "review", "snippet", "title", "summary"] if norm(row.get(col)))


def hint_counts(text):
    hay = text.lower()
    return {
        "negative_hint_count": sum(1 for hint in NEGATIVE_HINTS if hint in hay),
        "positive_hint_count": sum(1 for hint in POSITIVE_HINTS if hint in hay),
    }


def normalize_review_row(row):
    source = norm(row.get("source_type")) or norm(row.get("source")) or "manual_review_export"
    if source not in SUPPORTED_SOURCES:
        source = "manual_review_export"
    text = review_text(row)
    hints = hint_counts(text)
    return {
        "company_key": company_key(row),
        "company": norm(row.get("company")) or norm(row.get("name")) or norm(row.get("business_name")),
        "city": norm(row.get("city")) or norm(row.get("area")),
        "source_type": source,
        "source_url": norm(row.get("source_url")) or norm(row.get("url")),
        "rating": as_float(row.get("rating")),
        "review_count": as_int(row.get("review_count")),
        "review_text": text[:800],
        "negative_hint_count": hints["negative_hint_count"],
        "positive_hint_count": hints["positive_hint_count"],
        "cost_eur": "EUR 0.0000" if source.endswith("_export") else "REQUIRED_BEFORE_RUN",
        "evidence_role": "REVIEW_INTELLIGENCE_NON_AUTHORITATIVE",
    }


def aggregate_reviews(rows):
    grouped = defaultdict(list)
    for row in rows:
        normalized = normalize_review_row(row)
        if normalized["company_key"]:
            grouped[normalized["company_key"]].append(normalized)
    out = []
    for key, items in sorted(grouped.items()):
        ratings = [item["rating"] for item in items if item["rating"]]
        review_counts = [item["review_count"] for item in items if item["review_count"]]
        source_counts = Counter(item["source_type"] for item in items)
        negative = sum(item["negative_hint_count"] for item in items)
        positive = sum(item["positive_hint_count"] for item in items)
        out.append({
            "company_key": key,
            "company": items[0]["company"],
            "city": items[0]["city"],
            "review_sources": " | ".join(sorted(source_counts)),
            "review_source_count": len(source_counts),
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else "",
            "max_review_count": max(review_counts) if review_counts else "",
            "negative_hint_count": negative,
            "positive_hint_count": positive,
            "review_risk_state": "REVIEW_FRICTION" if negative > positive and negative >= 2 else "REVIEW_CONTEXT_ONLY",
            "cost_eur": "EUR 0.0000",
            "policy": "authorized_export_or_manual_input_no_scraping",
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="Aggregate authorized Google/Tripadvisor/manual review exports without scraping")
    ap.add_argument("input_csv")
    ap.add_argument("output_csv")
    ap.add_argument("--output-json")
    args = ap.parse_args()
    rows = read_csv(args.input_csv)
    aggregated = aggregate_reviews(rows)
    fields = [
        "company_key", "company", "city", "review_sources", "review_source_count",
        "avg_rating", "max_review_count", "negative_hint_count", "positive_hint_count",
        "review_risk_state", "cost_eur", "policy",
    ]
    write_csv(args.output_csv, aggregated, fieldnames=fields)
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps({"rows": aggregated}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "rows": len(aggregated),
        "cost_eur": "EUR 0.0000",
        "policy": "authorized_export_or_manual_input_no_scraping",
    }, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
