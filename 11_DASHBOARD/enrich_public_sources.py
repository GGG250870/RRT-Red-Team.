#!/usr/bin/env python3
import argparse
import csv
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html import unescape
from pathlib import Path


USER_AGENT = "Mozilla/5.0 (compatible; RRT-FreePublicEnrichment/1.0; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 750_000
DEFAULT_LIMIT = 200

SOCIAL_DOMAINS = {
    "facebook_url": ["facebook.com", "fb.com"],
    "instagram_url": ["instagram.com"],
    "linkedin_url": ["linkedin.com"],
    "tiktok_url": ["tiktok.com"],
}
REVIEW_DOMAINS = [
    "google.com",
    "g.page",
    "miodottore.it",
    "thefork.it",
    "tripadvisor.it",
    "restaurantguru.it",
    "trustpilot.com",
    "yelp.it",
    "paginegialle.it",
    "booking.com",
    "treatwell.it",
    "prontopro.it",
    "habitissimo.it",
]
RESTAURANT_REVIEW_PORTALS_BY_TARGET = {
    "ristorazione_generic": ["tripadvisor.it", "thefork.it", "restaurantguru.it", "paginegialle.it"],
    "fine_dining": ["tripadvisor.it", "thefork.it", "michelin.com", "gamberorosso.it"],
    "pizzeria": ["tripadvisor.it", "thefork.it", "restaurantguru.it", "paginegialle.it"],
    "trattoria_osteria": ["tripadvisor.it", "restaurantguru.it", "thefork.it", "paginegialle.it"],
    "sushi_etnico": ["tripadvisor.it", "thefork.it", "restaurantguru.it"],
    "delivery_asporto": ["tripadvisor.it", "thefork.it", "restaurantguru.it"],
    "eventi_catering": ["tripadvisor.it", "thefork.it", "paginegialle.it"],
    "enoteca_wine_bar": ["tripadvisor.it", "thefork.it", "gamberorosso.it"],
    "bar_cafe": ["tripadvisor.it", "restaurantguru.it", "paginegialle.it"],
}
FINANCIAL_HINTS = [
    "bilancio",
    "bilanci",
    "financial",
    "investor",
    "trasparenza",
    "registroimprese",
    "infocamere",
    "telemaco",
    "xbrl",
]


def norm(value):
    return (value or "").strip()


def normalize_url(value):
    value = norm(value)
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    return value


def normalize_domain(value):
    value = normalize_url(value)
    if not value:
        return ""
    parsed = urllib.parse.urlparse(value)
    host = (parsed.netloc or parsed.path).lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def same_or_subdomain(host, domain):
    return host == domain or host.endswith("." + domain)


def robots_allows(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False, "INVALID_URL"
    robots_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True, "ROBOTS_UNAVAILABLE_ASSUME_PUBLIC"
    try:
        return rp.can_fetch(USER_AGENT, url), "ROBOTS_CHECKED"
    except Exception:
        return True, "ROBOTS_CHECK_FAILED_ASSUME_PUBLIC"


def fetch(url):
    allowed, robots_state = robots_allows(url)
    if not allowed:
        return {"state": "ROBOTS_DISALLOWED", "url": url, "robots_state": robots_state}
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return {"state": "NON_HTML", "url": resp.geturl(), "robots_state": robots_state, "content_type": content_type}
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            return {
                "state": "OK",
                "url": resp.geturl(),
                "robots_state": robots_state,
                "html": raw.decode(charset, errors="replace"),
            }
    except urllib.error.HTTPError as e:
        return {"state": f"HTTP_{e.code}", "url": url, "robots_state": robots_state}
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", "")
        state = "TIMEOUT" if isinstance(reason, socket.timeout) else "URL_ERROR"
        return {"state": state, "url": url, "robots_state": robots_state}
    except Exception:
        return {"state": "ERROR", "url": url, "robots_state": robots_state}


def clean_text(value):
    value = unescape(re.sub(r"(?s)<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def extract_title(html):
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html or "")
    return clean_text(match.group(1))[:240] if match else ""


def extract_meta_description(html):
    match = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html or "")
    if not match:
        match = re.search(r'(?is)<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html or "")
    return clean_text(match.group(1))[:500] if match else ""


def extract_links(html, base_url):
    out = []
    seen = set()
    for href, label in re.findall(r'(?is)<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html or ""):
        url = urllib.parse.urljoin(base_url, unescape(href.strip()))
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))
        key = url.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"url": url, "label": clean_text(label)[:160], "host": normalize_domain(url)})
    return out


def pick_social_links(links):
    found = {}
    for link in links:
        host = link["host"]
        for column, domains in SOCIAL_DOMAINS.items():
            if column not in found and any(same_or_subdomain(host, d) for d in domains):
                found[column] = link["url"]
    return found


def pick_review_link(links):
    for link in links:
        host = link["host"]
        if any(same_or_subdomain(host, d) for d in REVIEW_DOMAINS):
            return link["url"]
    return ""


def pick_financial_link(links):
    for link in links:
        hay = f"{link['url']} {link['label']}".lower()
        if any(hint in hay for hint in FINANCIAL_HINTS):
            return link["url"]
    return ""


def public_search_refs(row):
    company = norm(row.get("company")) or norm(row.get("name"))
    city = norm(row.get("city")) or norm(row.get("area"))
    domain = norm(row.get("domain")) or norm(row.get("website")) or norm(row.get("official_domain"))
    query_base = " ".join(part for part in [company, city] if part) or domain
    refs = {}
    if query_base:
        refs["google_search_url"] = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query_base)
        refs["google_maps_search_url"] = "https://www.google.com/maps/search/" + urllib.parse.quote_plus(query_base)
        refs["registroimprese_search_url"] = "https://www.registroimprese.it/ricerca-libera?p_p_id=ricercalibera&search=" + urllib.parse.quote_plus(query_base)
        if norm(row.get("vertical")) == "ristorazione":
            target = norm(row.get("target_segment")) or "ristorazione_generic"
            portals = RESTAURANT_REVIEW_PORTALS_BY_TARGET.get(target, RESTAURANT_REVIEW_PORTALS_BY_TARGET["ristorazione_generic"])
            refs["restaurant_review_search_urls"] = {
                portal: "https://www.google.com/search?q=" + urllib.parse.quote_plus(f"site:{portal} {query_base}")
                for portal in portals
            }
    return refs


def enrich_row(row, fetch_extra_urls=False):
    out = dict(row)
    source_refs = []
    domain = normalize_domain(row.get("domain") or row.get("website") or row.get("official_domain"))
    if domain:
        out.setdefault("domain", domain)
    homepage = normalize_url(domain)
    if not homepage:
        out["online_enrichment_state"] = "NO_OFFICIAL_DOMAIN"
        out["google_state"] = "PUBLIC_SEARCH_REF_ONLY"
        out["public_financials_state"] = "PUBLIC_SEARCH_REF_ONLY"
        out["free_online_enrichment_cost_eur"] = "EUR 0.0000"
        out["source_refs_json"] = json.dumps(public_search_refs(row), ensure_ascii=False)
        return out

    fetched = fetch(homepage)
    out["online_enrichment_state"] = fetched["state"]
    out["online_enrichment_url"] = fetched.get("url", homepage)
    out["online_enrichment_robots_state"] = fetched.get("robots_state", "")
    refs = public_search_refs(row)
    refs["official_website_attempted"] = homepage
    refs["official_website_state"] = fetched["state"]
    if fetched["state"] == "OK":
        html = fetched.get("html", "")
        links = extract_links(html, fetched.get("url") or homepage)
        out["official_title"] = out.get("official_title") or extract_title(html)
        out["official_meta_description"] = out.get("official_meta_description") or extract_meta_description(html)
        out["official_links_checked"] = str(len(links))
        for column, url in pick_social_links(links).items():
            if not norm(out.get(column)):
                out[column] = url
        review_url = pick_review_link(links)
        if review_url and not norm(out.get("review_portal_url")):
            out["review_portal_url"] = review_url
        financial_url = pick_financial_link(links)
        if financial_url and not norm(out.get("financial_source_url")):
            out["financial_source_url"] = financial_url
            out["public_financials_state"] = "FOUND_ON_OFFICIAL_WEBSITE"
        else:
            out["public_financials_state"] = "PUBLIC_SEARCH_REF_ONLY"
        source_refs.append({"source": "official_website", "url": fetched.get("url") or homepage, "state": fetched["state"]})
        for link in links[:25]:
            source_refs.append({"source": "official_link", "url": link["url"], "label": link["label"]})
    else:
        out["public_financials_state"] = "PUBLIC_SEARCH_REF_ONLY"

    out["google_state"] = "PUBLIC_SEARCH_REF_ONLY"
    if norm(out.get("google_url")) or norm(out.get("google_place_id")):
        out["google_state"] = "FOUND_FROM_INPUT"
    if fetch_extra_urls:
        for col in ["google_url", "review_portal_url", "financial_source_url"]:
            url = normalize_url(out.get(col))
            if not url:
                continue
            extra = fetch(url)
            out[f"{col}_fetch_state"] = extra["state"]
            source_refs.append({"source": col, "url": extra.get("url") or url, "state": extra["state"]})
            time.sleep(0.2)
    out["free_online_enrichment_cost_eur"] = "EUR 0.0000"
    refs["source_refs"] = source_refs
    out["source_refs_json"] = json.dumps(refs, ensure_ascii=False)
    return out


def fieldnames_for(rows):
    preferred = [
        "company", "domain", "city", "vertical", "decision", "preliminary_score",
        "online_enrichment_state", "online_enrichment_url", "online_enrichment_robots_state",
        "official_title", "official_meta_description", "official_links_checked",
        "google_state", "google_url", "google_rating", "google_review_count", "google_place_id",
        "review_portal_url", "facebook_url", "instagram_url", "linkedin_url", "tiktok_url",
        "public_financials_state", "financial_source_url", "balance_sheet_url", "registroimprese_url",
        "free_online_enrichment_cost_eur", "source_refs_json",
    ]
    all_fields = []
    seen = set()
    for field in preferred + [k for row in rows for k in row]:
        if field not in seen:
            seen.add(field)
            all_fields.append(field)
    return all_fields


def enrich_csv(input_csv, output_csv, limit=DEFAULT_LIMIT, fetch_extra_urls=False):
    with Path(input_csv).open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out_rows = []
    for idx, row in enumerate(rows[:limit], 1):
        enriched = enrich_row(row, fetch_extra_urls=fetch_extra_urls)
        out_rows.append(enriched)
        print(f"[{idx}/{min(len(rows), limit)}] {norm(enriched.get('company')) or norm(enriched.get('domain'))}: {enriched.get('online_enrichment_state')} cost=EUR 0.0000")
    if len(rows) > limit:
        print(f"LIMIT_REACHED: processed {limit}/{len(rows)} rows", file=sys.stderr)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_for(out_rows or rows))
        writer.writeheader()
        writer.writerows(out_rows)
    return out_rows


def main():
    ap = argparse.ArgumentParser(description="Free/legal public web enrichment for RRT dashboard inputs")
    ap.add_argument("input_csv")
    ap.add_argument("output_csv")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    ap.add_argument("--fetch-extra-urls", action="store_true", help="Also fetch explicit google/review/financial URLs already present in the CSV")
    args = ap.parse_args()
    rows = enrich_csv(args.input_csv, args.output_csv, limit=args.limit, fetch_extra_urls=args.fetch_extra_urls)
    print(json.dumps({
        "status": "PASS",
        "rows": len(rows),
        "output_csv": args.output_csv,
        "cost_eur": "EUR 0.0000",
        "policy": "free_public_legal_no_bypass_no_invention",
    }, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
