#!/usr/bin/env python3
import argparse
import base64
import csv
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; RRT-BatchBuilder/1.6; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 750_000

BLOCKED_DOMAINS = {
    "instagram.com", "linkedin.com", "youtube.com", "wikipedia.org",
    "bing.com", "zhihu.com", "treccani.it", "shopify.com", "salehoo.com",
    "fluentcart.com", "hostadvice.com", "avada.io"
}

ITALY_REVIEW_DOMAINS_BY_VERTICAL = {
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

VERTICAL_TERMS = {
    "dentale": [
        "studio dentistico",
        "dentista",
        "centro odontoiatrico",
        "clinica dentale",
        "implantologia dentale",
        "ortodonzia",
    ],
}

VERTICAL_HINTS = {
    "dentale": ["dent", "odont", "implant", "ortodonz", "stomatolog", "oral", "dental"],
}

ITALY_HINTS = [
    ".it", "italia", "italy", "liguria", "piemonte", "lombardia", "veneto", "toscana",
    "emilia", "romagna", "lazio", "campania", "puglia", "sicilia", "sardegna", "calabria",
    "abruzzo", "marche", "umbria", "molise", "basilicata", "friuli", "trentino", "alto adige",
    "valle d'aosta"
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
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


def decode_ddg_href(href):
    href = unescape(href or "")
    p = urllib.parse.urlparse(href)
    qs = urllib.parse.parse_qs(p.query)
    return qs.get("uddg", [href])[0]


def decode_bing_href(href):
    href = unescape(href or "")
    p = urllib.parse.urlparse(href)
    if "bing.com" not in (p.netloc or "").lower():
        return href
    raw = urllib.parse.parse_qs(p.query).get("u", [""])[0]
    if raw.startswith("a1"):
        token = raw[2:]
        try:
            token += "=" * (-len(token) % 4)
            decoded = base64.urlsafe_b64decode(token.encode()).decode("utf-8", errors="ignore")
            if decoded.startswith("http"):
                return decoded
        except Exception:
            pass
    return ""


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
        target = decode_bing_href(href)
        if target:
            title = clean_title(re.sub(r"(?s)<[^>]+>", " ", title_html))
            results.append((title, target))
    return results


def search_query(query):
    localized = query + " Italia"
    attempts = [
        ("ddg_html", "https://html.duckduckgo.com/html/?kl=it-it&q=" + urllib.parse.quote_plus(localized), extract_ddg_results),
        ("ddg_lite", "https://lite.duckduckgo.com/lite/?kl=it-it&q=" + urllib.parse.quote_plus(localized), extract_ddg_results),
        ("bing", "https://www.bing.com/search?cc=it&setlang=it&q=" + urllib.parse.quote_plus(localized), extract_bing_results),
    ]
    for source, url, parser in attempts:
        _, html = fetch(url)
        if not html:
            continue
        results = parser(html)
        if results:
            return source, results
    return "none", []


def review_domains(vertical):
    return ITALY_REVIEW_DOMAINS_BY_VERTICAL.get(vertical, [])[:10]


def infer_source(domain, vertical):
    for review_domain in review_domains(vertical):
        if domain == review_domain or domain.endswith("." + review_domain):
            return review_domain
    return "official_or_other"


def is_italy_candidate(title, url, domain, area, vertical, review_source):
    if not domain or any(domain == d or domain.endswith("." + d) for d in BLOCKED_DOMAINS):
        return False
    haystack = f"{title} {url} {domain} {area}".lower()
    area_tokens = [t for t in re.findall(r"[a-zà-ÿ]+", area.lower()) if len(t) >= 4]
    vertical_ok = any(h in haystack for h in VERTICAL_HINTS.get(vertical, [vertical.lower()]))
    area_ok = not area_tokens or any(t in haystack for t in area_tokens)
    if review_source != "official_or_other":
        return area_ok and vertical_ok
    italy_ok = domain.endswith(".it") or any(h in haystack for h in ITALY_HINTS) or area_ok
    return italy_ok and area_ok and vertical_ok


def review_queries(area, vertical):
    terms = VERTICAL_TERMS.get(vertical, [vertical])
    queries = []
    for term in terms:
        queries.append(f'{term} {area} recensioni')
        for domain in review_domains(vertical):
            queries.append(f'site:{domain} {term} {area}')
    return queries


def discover_area(area, limit, vertical):
    terms = VERTICAL_TERMS.get(vertical, [vertical])
    queries = [f"{term} {area}" for term in terms] + review_queries(area, vertical)
    out, seen_urls = [], set()
    for query in queries:
        source, results = search_query(query)
        accepted = 0
        for title, url in results:
            domain = normalize_domain(url)
            review_source = infer_source(domain, vertical)
            if not url or url in seen_urls or not is_italy_candidate(title, url, domain, area, vertical, review_source):
                continue
            seen_urls.add(url)
            out.append({
                "company": title or domain,
                "domain": domain,
                "source_url": url,
                "area": area,
                "city": area,
                "country": "IT",
                "vertical": vertical,
                "discovery_source": source,
                "review_source": review_source,
                "discovery_query": query,
            })
            accepted += 1
            if len(out) >= limit:
                break
        print(f"[DISCOVERY] {area} | {query} | source={source} | raw={len(results)} | accepted_it={accepted}")
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser(description="RRT Italy-only free batch builder")
    ap.add_argument("output_csv")
    ap.add_argument("--areas", default="Milano Navigli,Roma Prati,Torino Crocetta,Genova Albaro,Bologna Centro")
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--vertical", default="dentale")
    args = ap.parse_args()

    areas = [a.strip() for a in args.areas.split(",") if a.strip()]
    if not areas:
        print("Nessuna area specificata")
        return 2

    print("COUNTRY_SCOPE: ITALIA ONLY")
    print("Review portals (max 10): " + " | ".join(review_domains(args.vertical)))

    per_area = max(5, (args.target + len(areas) - 1) // len(areas))
    rows, seen = [], set()
    for area in areas:
        for row in discover_area(area, per_area * 4, args.vertical):
            key = (row["company"].lower(), row["domain"], row["review_source"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
            print(f"[{len(rows)}/{args.target}] {area}: {row['company']} -> {row['domain']} [{row['review_source']}]")
            if len(rows) >= args.target:
                break
        if len(rows) >= args.target:
            break

    path = Path(args.output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["company", "domain", "source_url", "area", "city", "country", "vertical", "discovery_source", "review_source", "discovery_query"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Creati {len(rows)} record-source ITALIA in {path}")
    print("Aree richieste: " + " | ".join(areas))
    if not rows:
        print("DISCOVERY_EMPTY: nessuna fonte italiana/pubblica ha restituito prospect utilizzabili.")
        return 3
    if len(rows) < args.target:
        print("ATTENZIONE: target non raggiunto; il batch parziale resta valido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
