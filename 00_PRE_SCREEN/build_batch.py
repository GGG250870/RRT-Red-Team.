#!/usr/bin/env python3
import argparse
import csv
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; RRT-BatchBuilder/2.0; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 1_000_000

PRIMARY_PORTALS_BY_VERTICAL = {
    "dentale": [
        ("miodottore.it", "https://www.miodottore.it/dentista/{area_slug}"),
        ("dentisti-italia.it", "https://www.dentisti-italia.it/dentista-liguria/dentista-{area_slug}/"),
        ("docdental.it", "https://docdental.it/cliniche-dentali/{area_slug}/"),
    ]
}

REVIEW_PORTALS_BY_VERTICAL = {
    "dentale": [
        "google.com",
        "miodottore.it",
        "paginegialle.it",
        "facebook.com",
        "trustpilot.com",
        "dentisti-italia.it",
        "yelp.it",
        "doctolib.it",
        "guidamedicina.it",
        "whatclinic.com",
    ],
}

VERTICAL_HINTS = {
    "dentale": ["dent", "odont", "implant", "ortodonz", "stomatolog", "dental"],
}

GENERIC_LABELS = {
    "", "login", "registrati gratis", "altro", "mappa", "avanti",
    "in che modo ordiniamo i risultati", "scarica gratuitamente la nostra app mobile",
}

PORTAL_PROFILE_RULES = {
    "miodottore.it": re.compile(r"^/profilo/[^/?#]+/?$", re.I),
    "dentisti-italia.it": re.compile(r"/dentista-[^/?#]+/[^/?#]+/?$", re.I),
    "docdental.it": re.compile(r"/(clinica|cliniche|dentista|studio)[^/?#]+", re.I),
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.geturl(), raw.decode(charset, errors="replace")
    except Exception:
        return None, None


def slugify_area(area):
    s = area.strip().lower()
    s = re.sub(r"[^a-z0-9à-ÿ]+", "-", s)
    return s.strip("-")


def normalize_domain(url):
    if not url:
        return ""
    p = urllib.parse.urlparse(url if re.match(r"^https?://", url, re.I) else "https://" + url)
    host = (p.netloc or p.path).lower().split("@")[ -1 ].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def clean_text(value):
    value = unescape(re.sub(r"(?s)<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def looks_vertical(text, vertical):
    hay = (text or "").lower()
    return any(h in hay for h in VERTICAL_HINTS.get(vertical, [vertical.lower()]))


def is_generic_label(label):
    text = clean_text(label).lower()
    if text in GENERIC_LABELS:
        return True
    if re.fullmatch(r"\d+", text):
        return True
    if re.search(r"\b(recension[ei]|dentisti a|carie|gengivite|malocclusione|pulpite)\b", text):
        return True
    return False


def is_portal_profile_link(link, portal):
    parsed = urllib.parse.urlparse(link)
    host = normalize_domain(link)
    if host != portal:
        return False
    rule = PORTAL_PROFILE_RULES.get(portal)
    if not rule:
        return False
    return bool(rule.search(parsed.path or ""))


def company_key(company):
    text = clean_text(company).lower()
    text = re.sub(r"\b(dott|dottssa|dott\.|dott\.ssa|dr|dr\.|prof|prof\.)\b", " ", text)
    text = re.sub(r"[^a-z0-9à-ÿ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_links(html, base_url):
    out = []
    seen = set()
    for href, label in re.findall(r'(?is)<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html or ""):
        url = urllib.parse.urljoin(base_url, unescape(href))
        text = clean_text(label)
        key = (url, text)
        if key not in seen:
            seen.add(key)
            out.append((url, text))
    return out


def discover_portal(area, vertical, portal, template, limit):
    slug = slugify_area(area)
    url = template.format(area_slug=slug)
    final_url, html = fetch(url)
    if not html:
        print(f"[PORTAL] {portal} | {area} | fetch=FAIL")
        return []

    results = []
    for link, label in extract_links(html, final_url or url):
        hay = f"{label} {link} {area}".lower()
        if is_generic_label(label):
            continue
        if not is_portal_profile_link(link, portal):
            continue
        if not looks_vertical(hay, vertical) and portal != "miodottore.it":
            continue
        results.append({
            "company": clean_text(label),
            "domain": "",
            "source_url": link,
            "area": area,
            "city": area,
            "country": "IT",
            "vertical": vertical,
            "discovery_source": "portal_direct",
            "review_source": portal,
            "discovery_query": url,
            "official_domain_state": "UNRESOLVED",
        })
        if len(results) >= limit:
            break

    print(f"[PORTAL] {portal} | {area} | fetch=OK | accepted={len(results)}")
    return results


def discover_area(area, vertical, limit):
    rows = []
    seen = set()
    portals = PRIMARY_PORTALS_BY_VERTICAL.get(vertical, [])
    for portal, template in portals:
        for row in discover_portal(area, vertical, portal, template, limit):
            key = (portal, company_key(row["company"]), row["source_url"].split("#", 1)[0])
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
            if len(rows) >= limit:
                return rows
    return rows


def main():
    ap = argparse.ArgumentParser(description="RRT Italy-only portal-first batch builder")
    ap.add_argument("output_csv")
    ap.add_argument("--areas", required=True)
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--vertical", default="dentale")
    args = ap.parse_args()

    areas = [a.strip() for a in args.areas.split(",") if a.strip()]
    if not areas:
        print("Nessuna area specificata")
        return 2

    print("COUNTRY_SCOPE: ITALIA ONLY")
    print("DISCOVERY_MODE: PORTAL_FIRST")
    print("Primary portals: " + " | ".join(p for p, _ in PRIMARY_PORTALS_BY_VERTICAL.get(args.vertical, [])))
    print("Review portals (max 10): " + " | ".join(REVIEW_PORTALS_BY_VERTICAL.get(args.vertical, [])[:10]))

    rows = []
    seen = set()
    per_area = max(5, (args.target + len(areas) - 1) // len(areas))
    for area in areas:
        for row in discover_area(area, args.vertical, per_area * 3):
            key = (row["review_source"], company_key(row["company"]), row["source_url"].split("#", 1)[0])
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
            print(f"[{len(rows)}/{args.target}] {area}: {row['company']} [{row['review_source']}]")
            if len(rows) >= args.target:
                break
        if len(rows) >= args.target:
            break

    path = Path(args.output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["company", "domain", "source_url", "area", "city", "country", "vertical", "discovery_source", "review_source", "discovery_query", "official_domain_state"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Creati {len(rows)} record-source ITALIA in {path}")
    if not rows:
        print("DISCOVERY_EMPTY: nessun portale primario ha restituito prospect utilizzabili.")
        return 3
    if len(rows) < args.target:
        print("ATTENZIONE: target non raggiunto; il batch parziale resta valido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
