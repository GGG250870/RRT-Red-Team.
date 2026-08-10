#!/usr/bin/env python3
import argparse
import csv
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; RRT-BatchBuilder/1.1; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 500_000


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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


def extract_search_results(html):
    results = []
    for m in re.finditer(r'(?is)<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html or ""):
        href, title_html = m.groups()
        title = clean_title(re.sub(r"(?s)<[^>]+>", " ", title_html))
        href = unescape(href)
        p = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(p.query)
        if "uddg" in qs:
            href = qs["uddg"][0]
        results.append((title, href))
    return results


def discover_area(area, limit, vertical):
    vertical_terms = {
        "dentale": ["studio dentistico", "implantologia dentale", "centro odontoiatrico"],
    }
    terms = vertical_terms.get(vertical, [vertical])
    queries = [f"{term} {area}" for term in terms]
    out, seen = [], set()
    for query in queries:
        qurl = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)
        _, html = fetch(qurl)
        for title, url in extract_search_results(html):
            domain = normalize_domain(url)
            if not domain or domain in seen:
                continue
            if any(x in domain for x in ["facebook.com", "instagram.com", "linkedin.com", "youtube.com", "paginegialle.it", "miodottore.it", "doctolib.it"]):
                continue
            seen.add(domain)
            out.append({"company": title or domain, "domain": domain, "area": area, "vertical": vertical})
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
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company", "domain", "area", "vertical"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Creati {len(rows)} prospect in {path}")
    print("Aree richieste: " + " | ".join(areas))
    if len(rows) < args.target:
        print("ATTENZIONE: target non raggiunto. Aggiungere aree/query o una fonte discovery alternativa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
