#!/usr/bin/env python3
import argparse
import csv
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; RRT-BatchBuilder/1.2; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 750_000

BLOCKED_DOMAINS = {
    "facebook.com", "instagram.com", "linkedin.com", "youtube.com",
    "paginegialle.it", "miodottore.it", "doctolib.it", "yelp.it",
    "tripadvisor.it", "wikipedia.org"
}

VERTICAL_TERMS = {
    "dentale": [
        "studio dentistico",
        "dentista",
        "centro odontoiatrico",
        "clinica dentale",
        "implantologia dentale",
        "ortodonzia"
    ],
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml"
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.geturl(), raw.decode(charset, errors="replace")
    except Exception:
        return None, None


def normalize_domain(url):
    if not url:
        return ""
    p = urllib.parse.urlparse(url if re.match(r"^https?://", url, re.I) else "https://" + url)
    host = (p.netloc or p.path).lower().split("@")[ -1 ].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def clean_title(title):
    title = unescape(re.sub(r"\s+", " ", title or "")).strip(" -|–—")
    return title[:160]


def allowed_domain(domain):
    if not domain:
        return False
    return not any(domain == d or domain.endswith("." + d) for d in BLOCKED_DOMAINS)


def decode_ddg_href(href):
    href = unescape(href or "")
    p = urllib.parse.urlparse(href)
    qs = urllib.parse.parse_qs(p.query)
    if "uddg" in qs:
        return qs["uddg"][0]
    return href


def extract_ddg_results(html):
    results = []
    patterns = [
        r'(?is)<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        r"(?is)<a[^>]+class='[^']*result__a[^']*'[^>]+href='([^']+)'[^>]*>(.*?)</a>",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, html or ""):
            href, title_html = m.groups()
            title = clean_title(re.sub(r"(?s)<[^>]+>", " ", title_html))
            results.append((title, decode_ddg_href(href)))
    return results


def extract_bing_results(html):
    results = []
    for m in re.finditer(r'(?is)<li[^>]+class="[^"]*b_algo[^"]*"[^>]*>.*?<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html or ""):
        href, title_html = m.groups()
        title = clean_title(re.sub(r"(?s)<[^>]+>", " ", title_html))
        results.append((title, unescape(href)))
    return results


def search_query(query):
    attempts = [
        ("ddg_html", "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query), extract_ddg_results),
        ("ddg_lite", "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote_plus(query), extract_ddg_results),
        ("bing", "https://www.bing.com/search?q=" + urllib.parse.quote_plus(query), extract_bing_results),
    ]
    for source, url, parser in attempts:
        _, html = fetch(url)
        if not html:
            continue
        results = parser(html)
        if results:
            return source, results
    return "none", []


def discover_area(area, limit, vertical):
    terms = VERTICAL_TERMS.get(vertical, [vertical])
    queries = [f"{term} {area}" for term in terms]
    out, seen = [], set()
    for query in queries:
        source, results = search_query(query)
        print(f"[DISCOVERY] {area} | {query} | source={source} | results={len(results)}")
        for title, url in results:
            domain = normalize_domain(url)
            if not allowed_domain(domain) or domain in seen:
                continue
            seen.add(domain)
            out.append({
                "company": title or domain,
                "domain": domain,
                "area": area,
                "city": area,
                "vertical": vertical,
                "discovery_source": source,
                "discovery_query": query,
            })
            if len(out) >= limit:
                return out
    return out


def main():
    ap = argparse.ArgumentParser(description="RRT free batch builder with neighborhood-level targeting")
    ap.add_argument("output_csv")
    ap.add_argument("--areas", default="Milano Navigli,Roma Prati,Torino Crocetta,Genova Albaro,Bologna Centro")
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--vertical", default="dentale")
    args = ap.parse_args()

    areas = [a.strip() for a in args.areas.split(",") if a.strip()]
    if not areas:
        print("Nessuna area specificata")
        return 2

    per_area = max(5, (args.target + len(areas) - 1) // len(areas))
    rows, seen = [], set()
    for area in areas:
        for row in discover_area(area, per_area, args.vertical):
            if row["domain"] in seen:
                continue
            seen.add(row["domain"])
            rows.append(row)
            print(f"[{len(rows)}/{args.target}] {area}: {row['company']} -> {row['domain']}")
            if len(rows) >= args.target:
                break
        if len(rows) >= args.target:
            break

    path = Path(args.output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["company", "domain", "area", "city", "vertical", "discovery_source", "discovery_query"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Creati {len(rows)} prospect in {path}")
    print("Aree richieste: " + " | ".join(areas))
    if not rows:
        print("DISCOVERY_EMPTY: nessuna SERP gratuita ha restituito prospect utilizzabili. Non eseguire il pre-screen.")
        return 3
    if len(rows) < args.target:
        print("ATTENZIONE: target non raggiunto; il batch parziale resta comunque valido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
