#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ALIASES = {
    "company": ["company", "name", "business_name", "ragione_sociale"],
    "domain": ["domain", "website", "official_domain", "sito"],
    "city": ["city", "area", "citta", "comune"],
    "vertical": ["vertical", "category", "categoria"],
    "target_segment": ["target_segment", "segment", "target", "sottocategoria"],
    "phone": ["phone", "telefono", "telephone", "tel"],
    "mobile_phone": ["mobile_phone", "mobile", "cellulare", "whatsapp", "whatsapp_phone"],
    "email": ["email", "mail", "e_mail"],
    "address": ["address", "indirizzo", "street_address", "sede"],
}


def norm(value):
    return (value or "").strip()


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def first_value(row, key):
    for column in ALIASES[key]:
        value = norm(row.get(column))
        if value:
            return value
    return ""


def pct(part, total):
    return round((part / total) * 100, 1) if total else 0.0


def coverage(rows, key):
    count = sum(1 for row in rows if first_value(row, key))
    return {"count": count, "percent": pct(count, len(rows))}


def readiness_state(rows, min_rows):
    blockers = []
    warnings = []
    total = len(rows)
    cov = {key: coverage(rows, key) for key in ALIASES}
    if total == 0:
        blockers.append("CSV vuoto.")
    if total and total < min_rows:
        warnings.append(f"Righe sotto target pilot: {total}/{min_rows}.")
    for key, label in [("company", "azienda"), ("city", "citta"), ("vertical", "categoria")]:
        if cov[key]["percent"] < 95:
            blockers.append(f"Copertura {label} insufficiente: {cov[key]['percent']}%.")
    if cov["domain"]["percent"] < 30:
        blockers.append(f"Troppi domini ufficiali mancanti: copertura {cov['domain']['percent']}%.")
    elif cov["domain"]["percent"] < 70:
        warnings.append(f"Dominio ufficiale sotto soglia ideale: {cov['domain']['percent']}%.")
    if cov["target_segment"]["percent"] < 80 and any(first_value(row, "vertical") == "ristorazione" for row in rows):
        warnings.append(f"Target segment ristorazione incompleto: {cov['target_segment']['percent']}%.")
    if cov["phone"]["percent"] < 50:
        warnings.append(f"Telefono sotto copertura consigliata: {cov['phone']['percent']}%.")
    if cov["email"]["percent"] < 30:
        warnings.append(f"Email sotto copertura consigliata: {cov['email']['percent']}%.")
    if blockers:
        state = "NOT_READY"
    elif warnings:
        state = "USABLE_WITH_GAPS"
    else:
        state = "READY"
    return state, blockers, warnings, cov


def summarize_values(rows, key):
    values = Counter(first_value(row, key) or "MISSING" for row in rows)
    return dict(values.most_common(12))


def analyze(path, min_rows=30):
    rows = read_csv(path)
    state, blockers, warnings, cov = readiness_state(rows, min_rows)
    return {
        "status": state,
        "input_csv": str(path),
        "rows": len(rows),
        "min_rows": min_rows,
        "cost_eur": "EUR 0.0000",
        "agent_team_status": "AGENT_TEAM_LOCKED",
        "blockers": blockers,
        "warnings": warnings,
        "coverage": cov,
        "verticals": summarize_values(rows, "vertical"),
        "cities": summarize_values(rows, "city"),
        "target_segments": summarize_values(rows, "target_segment"),
        "next_action": next_action(state),
    }


def next_action(state):
    if state == "READY":
        return "Run pre-screen, enrichment and dashboard."
    if state == "USABLE_WITH_GAPS":
        return "Run dashboard, but prioritize filling warnings before interpreting shortlist."
    return "Fix blockers before pilot; do not use output as operational shortlist."


def main():
    ap = argparse.ArgumentParser(description="Check whether a manual prospect CSV is ready for an RRT dashboard pilot")
    ap.add_argument("input_csv")
    ap.add_argument("--min-rows", type=int, default=30)
    ap.add_argument("--output-json", help="Optional path for readiness JSON")
    args = ap.parse_args()
    result = analyze(args.input_csv, min_rows=args.min_rows)
    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"READY", "USABLE_WITH_GAPS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
