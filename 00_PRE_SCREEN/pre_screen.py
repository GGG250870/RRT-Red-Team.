#!/usr/bin/env python3
import argparse
import csv
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; RRT-PreScreen/1.1; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 750_000

DIMENSIONS = {
    "D1": [r"sedazion", r"odontofob", r"ansia", r"paura", r"senza dolore", r"indolor", r"anestes", r"anestesiolog"],
    "D2": [r"finanzi", r"rate", r"rateizz", r"pagament", r"dilazion", r"costo", r"prezzo", r"preventivo"],
    "D3": [r"implantolog", r"impiant", r"tac", r"cbct", r"scanner", r"3d", r"chirurgia guidata", r"digitale", r"specialist", r"team", r"garanzia"],
    "D4": [r"carico immediato", r"24\s*ore", r"in un giorno", r"stessa giornata", r"same day", r"provvisor", r"all[- ]on[- ]4", r"all[- ]on[- ]four"],
    "D5": [r"perch[eé] scegliere", r"vantagg", r"testimonianz", r"recension", r"faq", r"garanzia", r"esperienza", r"dicono di noi"],
}

HIGH_VALUE_PATTERNS = [
    r"implantolog", r"all[- ]on[- ]4", r"carico immediato", r"ortodonzia invisibile",
    r"invisalign", r"faccette", r"estetica dentale", r"riabilitazione completa", r"chirurgia orale"
]

STRUCTURE_PATTERNS = [
    r"\b3\s+(riuniti|sale|poltrone|studi)\b", r"\b4\s+(riuniti|sale|poltrone|studi)\b",
    r"\b5\s+(riuniti|sale|poltrone|studi)\b", r"team", r"equipe", r"staff", r"specialisti",
    r"odontoiatri", r"medici", r"igienist"
]

YOUTH_GROWTH_PATTERNS = [
    r"nuovo studio", r"nuova sede", r"inaugurat", r"dal 20(1[8-9]|2[0-6])", r"fondat[oa] nel 20(1[8-9]|2[0-6])",
    r"ampliament", r"crescita", r"innovazione", r"tecnologia", r"digitale", r"nuova generazione"
]

COMMERCIAL_GAP_PATTERNS = {
    "no_financing_signal": DIMENSIONS["D2"],
    "no_fear_reassurance_signal": DIMENSIONS["D1"],
    "no_social_proof_signal": [r"testimonianz", r"recension", r"dicono di noi"],
    "no_faq_signal": [r"faq", r"domande frequenti"],
    "no_guarantee_signal": [r"garanzia", r"garantito"],
}

PAGE_HINTS = ["implant", "servizi", "trattamenti", "tecnolog", "chi-siamo", "studio", "team", "faq", "recension", "testimon", "contatti", "sedaz", "finanzi", "invisalign", "faccette"]

CONTACT_PATTERNS = [
    re.compile(r"mailto:", re.I),
    re.compile(r"tel:", re.I),
    re.compile(r"whatsapp|wa\.me", re.I),
    re.compile(r"prenota|contattaci|richiedi.*appuntamento|appuntamento", re.I),
]


def normalize_domain(value):
    value = (value or "").strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    p = urllib.parse.urlparse(value)
    host = (p.netloc or p.path).strip().lower()
    host = host.split("@")[ -1 ].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def base_url(domain):
    return "https://" + domain if domain else ""


def strip_html(html):
    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = unescape(html)
    return re.sub(r"\s+", " ", html).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return None, None, "NON_HTML"
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            return resp.geturl(), html, "OK"
    except urllib.error.HTTPError as e:
        return None, None, f"HTTP_{e.code}"
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", "URL_ERROR")
        if isinstance(reason, socket.timeout):
            return None, None, "TIMEOUT"
        return None, None, "URL_ERROR"
    except Exception:
        return None, None, "ERROR"


def extract_internal_links(html, current_url, domain):
    links = []
    for href in re.findall(r'(?i)href=["\']([^"\'#]+)', html or ""):
        href = unescape(href.strip())
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        url = urllib.parse.urljoin(current_url, href)
        p = urllib.parse.urlparse(url)
        host = (p.netloc or "").lower().split(":")[0]
        if host.startswith("www."):
            host = host[4:]
        if host != domain:
            continue
        path = (p.path or "/").lower()
        score = sum(1 for hint in PAGE_HINTS if hint in path)
        if score:
            clean = urllib.parse.urlunparse((p.scheme, p.netloc, p.path, "", "", ""))
            links.append((score, clean))
    out = []
    seen = set()
    for _, url in sorted(links, key=lambda x: (-x[0], len(x[1]))):
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out[:5]


def count_hits(text, patterns):
    text = (text or "").lower()
    return sum(1 for p in patterns if re.search(p, text, re.I))


def scan(domain):
    if not domain:
        return {"website_live": 0, "fetch_state": "NO_DOMAIN", "pages_found": 0, "contactability": 0, "hits": {d: 0 for d in DIMENSIONS}, "high_value_hits": 0, "structure_hits": 0, "youth_growth_hits": 0, "commercial_gap_count": 0}

    homepage = base_url(domain)
    final_url, html, state = fetch(homepage)
    if state != "OK":
        final_url, html, state2 = fetch("http://" + domain)
        state = state2
    if state != "OK" or not html:
        return {"website_live": 0, "fetch_state": state, "pages_found": 0, "contactability": 0, "hits": {d: 0 for d in DIMENSIONS}, "high_value_hits": 0, "structure_hits": 0, "youth_growth_hits": 0, "commercial_gap_count": 0}

    pages = [(final_url, html)]
    for url in extract_internal_links(html, final_url, domain):
        fetched_url, page_html, page_state = fetch(url)
        if page_state == "OK" and page_html:
            pages.append((fetched_url, page_html))

    combined_html = " ".join(p[1] for p in pages)
    text = strip_html(combined_html)
    hits = {d: count_hits(text, pats) for d, pats in DIMENSIONS.items()}
    contactability = sum(1 for p in CONTACT_PATTERNS if p.search(combined_html))
    high_value_hits = count_hits(text, HIGH_VALUE_PATTERNS)
    structure_hits = count_hits(text, STRUCTURE_PATTERNS)
    youth_growth_hits = count_hits(text, YOUTH_GROWTH_PATTERNS)
    commercial_gap_count = sum(1 for pats in COMMERCIAL_GAP_PATTERNS.values() if count_hits(text, pats) == 0)

    return {
        "website_live": 1,
        "fetch_state": "OK",
        "pages_found": len(pages),
        "contactability": contactability,
        "hits": hits,
        "high_value_hits": high_value_hits,
        "structure_hits": structure_hits,
        "youth_growth_hits": youth_growth_hits,
        "commercial_gap_count": commercial_gap_count,
    }


def score_row(result):
    if not result["website_live"]:
        return 0
    hits = result["hits"]
    observed_dims = sum(1 for v in hits.values() if v > 0)
    total_hits = sum(min(v, 5) for v in hits.values())
    score = 10
    score += min(result["pages_found"], 6) * 2
    score += observed_dims * 5
    score += min(total_hits, 12)
    score += min(result["high_value_hits"], 5) * 5
    score += min(result["structure_hits"], 4) * 4
    score += min(result["youth_growth_hits"], 4) * 5
    score += min(result["commercial_gap_count"], 4) * 3
    score += 8 if result["contactability"] >= 2 else 4 if result["contactability"] == 1 else 0
    return min(score, 100)


def decision(score, website_live, observed_dims, fetch_state, high_value_hits, structure_hits):
    if not website_live:
        if fetch_state == "NO_DOMAIN":
            return "REJECT"
        return "COLLECTION_RESTRICTED"
    if score >= 70 and high_value_hits >= 1 and (structure_hits >= 1 or observed_dims >= 3):
        return "ESCALATE"
    if score >= 45 and (high_value_hits >= 1 or observed_dims >= 2):
        return "SHORTLIST"
    return "REJECT"


def main():
    ap = argparse.ArgumentParser(description="RRT zero-LLM prospect pre-screen")
    ap.add_argument("input_csv")
    ap.add_argument("output_csv")
    args = ap.parse_args()

    input_path = Path(args.input_csv)
    output_path = Path(args.output_csv)
    if not input_path.exists():
        print(f"Input non trovato: {input_path}", file=sys.stderr)
        return 2

    with input_path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("CSV vuoto", file=sys.stderr)
        return 2

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "company", "domain", "city", "vertical", "website_live", "fetch_state", "pages_found",
        "D1_hits", "D2_hits", "D3_hits", "D4_hits", "D5_hits", "contactability", "observed_dimensions",
        "high_value_hits", "structure_hits", "youth_growth_hits", "commercial_gap_count",
        "preliminary_score", "decision"
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for idx, row in enumerate(rows, 1):
            company = (row.get("company") or row.get("name") or "").strip()
            domain = normalize_domain(row.get("domain") or row.get("website") or row.get("official_domain"))
            city = (row.get("city") or "").strip()
            vertical = (row.get("vertical") or "").strip()
            result = scan(domain)
            hits = result["hits"]
            observed_dims = sum(1 for v in hits.values() if v > 0)
            score = score_row(result)
            gate = decision(score, result["website_live"], observed_dims, result["fetch_state"], result["high_value_hits"], result["structure_hits"])
            writer.writerow({
                "company": company,
                "domain": domain,
                "city": city,
                "vertical": vertical,
                "website_live": result["website_live"],
                "fetch_state": result["fetch_state"],
                "pages_found": result["pages_found"],
                "D1_hits": hits["D1"],
                "D2_hits": hits["D2"],
                "D3_hits": hits["D3"],
                "D4_hits": hits["D4"],
                "D5_hits": hits["D5"],
                "contactability": result["contactability"],
                "observed_dimensions": observed_dims,
                "high_value_hits": result["high_value_hits"],
                "structure_hits": result["structure_hits"],
                "youth_growth_hits": result["youth_growth_hits"],
                "commercial_gap_count": result["commercial_gap_count"],
                "preliminary_score": score,
                "decision": gate,
            })
            print(f"[{idx}/{len(rows)}] {company or domain}: {gate} ({score}) HV={result['high_value_hits']} STR={result['structure_hits']} YG={result['youth_growth_hits']} GAP={result['commercial_gap_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
