#!/usr/bin/env python3
import argparse
import csv
import json
import re
import urllib.parse
from pathlib import Path


REVIEW_SOURCE_ALIASES = {
    "google": "google",
    "google_maps": "google",
    "tripadvisor": "tripadvisor",
    "thefork": "thefork",
    "restaurantguru": "restaurantguru",
    "paginegialle": "paginegialle",
    "manual": "manual",
}


def norm(value):
    return (value or "").strip()


def slug(value):
    value = norm(value).lower()
    value = re.sub(r"[^a-z0-9à-ÿ]+", " ", value)
    return " ".join(value.split())


def token_set(value):
    stop = {"di", "da", "de", "del", "della", "degli", "la", "il", "lo", "le", "l", "al", "the"}
    return {token for token in slug(value).split() if len(token) > 1 and token not in stop}


def company_key(row):
    return slug(row.get("company") or row.get("name") or row.get("business_name"))


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


def as_source(value):
    raw = slug(value).replace(" ", "_")
    return REVIEW_SOURCE_ALIASES.get(raw, raw or "manual")


def search_url(company, city, source):
    query = urllib.parse.quote_plus(" ".join(part for part in [company, city] if part))
    if source == "google":
        return f"https://www.google.com/maps/search/{query}"
    if source == "tripadvisor":
        return f"https://www.tripadvisor.it/Search?q={query}"
    if source == "restaurantguru":
        return f"https://restaurantguru.it/search/{query}"
    if source == "thefork":
        return f"https://www.thefork.it/search?queryPlaceValueCity={urllib.parse.quote_plus(city)}&q={urllib.parse.quote_plus(company)}"
    if source == "paginegialle":
        return f"https://www.paginegialle.it/ricerca/{urllib.parse.quote_plus(company)}/{urllib.parse.quote_plus(city)}"
    return ""


def link_index(rows):
    indexed = {}
    for row in rows:
        key = company_key(row)
        if not key:
            continue
        indexed.setdefault(key, []).append(row)
    return indexed


def best_links(seed_row, manual_links):
    seed_key = company_key(seed_row)
    seed_tokens = token_set(seed_key)
    candidates = []
    for key, rows in manual_links.items():
        tokens = token_set(key)
        overlap = len(seed_tokens & tokens)
        union = len(seed_tokens | tokens) or 1
        score = overlap / union
        if seed_key == key:
            score = 1.0
        if score >= 0.45:
            candidates.extend((score, row) for row in rows)
    return [row for _, row in sorted(candidates, key=lambda item: item[0], reverse=True)]


def city_state(seed_city, link_city, source_url):
    seed_city_s = slug(seed_city)
    link_city_s = slug(link_city)
    url_s = slug(source_url)
    if link_city_s:
        return "CITY_MATCH" if seed_city_s and seed_city_s in link_city_s else "CITY_CONFLICT"
    if seed_city_s and seed_city_s in url_s:
        return "CITY_MATCH"
    return "CITY_NOT_PROVEN"


def address_state(seed_address, link_address):
    seed = token_set(seed_address)
    link = token_set(link_address)
    if not seed or not link:
        return "ADDRESS_NOT_PROVEN"
    overlap = len(seed & link)
    return "ADDRESS_MATCH" if overlap >= min(2, len(seed), len(link)) else "ADDRESS_CONFLICT"


def name_state(seed_company, link_company):
    seed = token_set(seed_company)
    link = token_set(link_company)
    if not link:
        return "NAME_NOT_PROVEN"
    overlap = len(seed & link)
    if slug(seed_company) == slug(link_company) or overlap >= min(2, len(seed), len(link)):
        return "NAME_MATCH"
    if overlap:
        return "NAME_PARTIAL"
    return "NAME_CONFLICT"


def resolution_state(row, links):
    if not links:
        return "NEEDS_REVIEW_LINKS"
    states = []
    for link in links:
        states.append({
            "name": name_state(row.get("company"), link.get("company") or link.get("name")),
            "city": city_state(row.get("city") or row.get("area"), link.get("city") or link.get("area"), link.get("source_url") or link.get("url")),
            "address": address_state(row.get("address") or row.get("indirizzo"), link.get("address") or link.get("indirizzo")),
        })
    if any(state["city"] == "CITY_CONFLICT" for state in states):
        return "OUT_OF_AREA_OR_ENTITY_CONFLICT"
    if any(state["name"] == "NAME_MATCH" and state["city"] == "CITY_MATCH" for state in states):
        return "MATCH_CONFIRMED"
    if any(state["name"] in {"NAME_MATCH", "NAME_PARTIAL"} for state in states):
        return "AMBIGUOUS_REVIEW_LINK"
    return "ENTITY_CONFLICT"


def resolve_rows(seed_rows, manual_rows=None, default_sources=None):
    manual_links = link_index(manual_rows or [])
    default_sources = default_sources or ["google", "tripadvisor", "restaurantguru"]
    resolved = []
    for row in seed_rows:
        company = norm(row.get("company") or row.get("name"))
        city = norm(row.get("city") or row.get("area"))
        links = best_links(row, manual_links)
        state = resolution_state(row, links)
        out = dict(row)
        out["entity_resolution_state"] = state
        out["entity_resolution_cost_eur"] = "EUR 0.0000"
        out["entity_resolution_policy"] = "public_link_verification_no_bulk_scraping"
        for source in default_sources:
            explicit = next((link for link in links if as_source(link.get("source") or link.get("source_type")) == source), {})
            out[f"{source}_verified_url"] = norm(explicit.get("source_url") or explicit.get("url"))
            out[f"{source}_search_url"] = norm(out.get(f"{source}_search_url")) or search_url(company, city, source)
        if links:
            out["matched_review_sources"] = " | ".join(
                f"{as_source(link.get('source') or link.get('source_type'))}:{norm(link.get('source_url') or link.get('url'))}"
                for link in links
                if norm(link.get("source_url") or link.get("url"))
            )
        else:
            out["matched_review_sources"] = ""
        resolved.append(out)
    return resolved


def main():
    ap = argparse.ArgumentParser(description="Resolve seed companies against manually verified public review/source links")
    ap.add_argument("seed_csv")
    ap.add_argument("output_csv")
    ap.add_argument("--manual-links-csv")
    ap.add_argument("--output-json")
    args = ap.parse_args()
    seed_rows = read_csv(args.seed_csv)
    manual_rows = read_csv(args.manual_links_csv) if args.manual_links_csv else []
    rows = resolve_rows(seed_rows, manual_rows)
    fields = list(dict.fromkeys([key for row in rows for key in row]))
    write_csv(args.output_csv, rows, fields)
    summary = {
        "status": "PASS",
        "rows": len(rows),
        "states": {state: sum(1 for row in rows if row["entity_resolution_state"] == state) for state in sorted({row["entity_resolution_state"] for row in rows})},
        "cost_eur": "EUR 0.0000",
        "policy": "public_link_verification_no_bulk_scraping",
    }
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
