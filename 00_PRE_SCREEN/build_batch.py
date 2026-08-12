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
    ],
    "ristorazione": [],
    "pmi": [],
    "hospitality": [],
    "benessere_estetica": [],
    "servizi_casa": [],
    "formazione": [],
    "generic": []
}

PRIMARY_INTELLIGENCE_SOURCES_BY_VERTICAL = {
    "dentale": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["miodottore.it", "paginegialle.it", "trustpilot.com", "yelp.it", "doctolib.it", "guidamedicina.it", "whatclinic.com"],
        "social": ["facebook.com", "instagram.com", "linkedin.com", "tiktok.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "ristorazione": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["thefork.it", "tripadvisor.it", "restaurantguru.it", "gamberorosso.it", "michelin.com", "yelp.it", "paginegialle.it"],
        "social": ["facebook.com", "instagram.com", "tiktok.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "pmi": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["paginegialle.it", "trustpilot.com", "kompass.com", "europages.it"],
        "social": ["linkedin.com", "facebook.com", "instagram.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "hospitality": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["booking.com", "tripadvisor.it", "trivago.it", "hotels.com", "paginegialle.it"],
        "social": ["facebook.com", "instagram.com", "tiktok.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "benessere_estetica": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["treatwell.it", "paginegialle.it", "trustpilot.com"],
        "social": ["facebook.com", "instagram.com", "tiktok.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "servizi_casa": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["paginegialle.it", "prontopro.it", "habitissimo.it", "trustpilot.com"],
        "social": ["facebook.com", "instagram.com", "linkedin.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "formazione": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["paginegialle.it", "trustpilot.com"],
        "social": ["linkedin.com", "facebook.com", "instagram.com", "tiktok.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
    "generic": {
        "google": ["google_business_profile", "google_reviews", "google_maps"],
        "review_portals": ["paginegialle.it", "trustpilot.com"],
        "social": ["linkedin.com", "facebook.com", "instagram.com", "tiktok.com"],
        "public_financials": ["registroimprese.it", "telemaco.infocamere.it", "company_official_financial_docs"],
    },
}

TARGET_SEGMENTS_BY_VERTICAL = {
    "ristorazione": {
        "ristorazione_generic": {
            "aliases": {"ristorazione", "generic", "generico", "ristorante"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "restaurantguru.it", "paginegialle.it"],
            "hints": ["ristor", "trattoria", "osteria", "pizzeria", "cucina", "menu"],
        },
        "fine_dining": {
            "aliases": {"fine_dining", "fine-dining", "gourmet", "alta_cucina", "stellato"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "michelin.com", "gamberorosso.it"],
            "hints": ["fine dining", "gourmet", "degustazione", "chef", "michelin", "alta cucina"],
        },
        "pizzeria": {
            "aliases": {"pizzeria", "pizza"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "restaurantguru.it", "paginegialle.it"],
            "hints": ["pizzeria", "pizza", "forno", "impasto"],
        },
        "trattoria_osteria": {
            "aliases": {"trattoria_osteria", "trattoria", "osteria", "tipico", "tradizionale"},
            "review_portals": ["google.com", "tripadvisor.it", "restaurantguru.it", "thefork.it", "paginegialle.it"],
            "hints": ["trattoria", "osteria", "tipica", "tradizionale"],
        },
        "sushi_etnico": {
            "aliases": {"sushi_etnico", "sushi", "etnico", "fusion", "giapponese", "cinese", "thai", "indiano"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "restaurantguru.it"],
            "hints": ["sushi", "giapponese", "fusion", "cinese", "thai", "indiano", "poke"],
        },
        "delivery_asporto": {
            "aliases": {"delivery_asporto", "delivery", "asporto", "takeaway", "take_away"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "restaurantguru.it"],
            "hints": ["delivery", "asporto", "take away", "ordina online", "consegna"],
        },
        "eventi_catering": {
            "aliases": {"eventi_catering", "eventi", "catering", "cerimonie", "banchetti"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "paginegialle.it"],
            "hints": ["eventi", "catering", "cerimonie", "banchetti", "matrimoni"],
        },
        "enoteca_wine_bar": {
            "aliases": {"enoteca_wine_bar", "enoteca", "wine_bar", "winebar"},
            "review_portals": ["google.com", "tripadvisor.it", "thefork.it", "gamberorosso.it"],
            "hints": ["enoteca", "wine bar", "cantina", "vini", "sommelier"],
        },
        "bar_cafe": {
            "aliases": {"bar_cafe", "bar", "cafe", "caffe", "caffetteria", "aperitivo"},
            "review_portals": ["google.com", "tripadvisor.it", "paginegialle.it", "restaurantguru.it"],
            "hints": ["bar", "caffe", "caffetteria", "colazioni", "aperitivo", "cocktail"],
        },
    },
}

DISABLED_PRIMARY_PORTALS_BY_VERTICAL = {
    "dentale": [
        ("dentisti-italia.it", "disabled: profile parser not release-safe"),
        ("docdental.it", "disabled: profile parser not release-safe"),
    ],
    "ristorazione": [
        ("thefork.it", "disabled: official-domain resolver not validated"),
        ("tripadvisor.it", "disabled: profile parser not release-safe")
    ],
    "pmi": [],
    "hospitality": [
        ("booking.com", "disabled: official-domain resolver not validated"),
        ("tripadvisor.it", "disabled: profile parser not release-safe")
    ],
    "benessere_estetica": [
        ("treatwell.it", "disabled: official-domain resolver not validated")
    ],
    "servizi_casa": [
        ("prontopro.it", "disabled: official-domain resolver not validated"),
        ("habitissimo.it", "disabled: profile parser not release-safe")
    ],
    "formazione": [],
    "generic": []
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
    "ristorazione": [
        "google.com",
        "thefork.it",
        "tripadvisor.it",
        "facebook.com",
        "instagram.com",
        "restaurantguru.it",
        "gamberorosso.it",
        "michelin.com",
        "yelp.it",
        "paginegialle.it",
    ],
    "pmi": [
        "google.com",
        "paginegialle.it",
        "linkedin.com",
        "facebook.com",
        "kompass.com",
        "europages.it",
        "registroimprese.it",
        "trustpilot.com",
    ],
    "hospitality": [
        "google.com",
        "booking.com",
        "tripadvisor.it",
        "facebook.com",
        "instagram.com",
        "trivago.it",
        "hotels.com",
        "paginegialle.it",
    ],
    "benessere_estetica": [
        "google.com",
        "treatwell.it",
        "facebook.com",
        "instagram.com",
        "paginegialle.it",
        "trustpilot.com",
    ],
    "servizi_casa": [
        "google.com",
        "paginegialle.it",
        "prontopro.it",
        "habitissimo.it",
        "facebook.com",
        "instagram.com",
        "trustpilot.com",
    ],
    "formazione": [
        "google.com",
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "paginegialle.it",
        "trustpilot.com",
    ],
    "generic": ["google.com", "facebook.com", "instagram.com", "linkedin.com", "paginegialle.it"],
}

PORTAL_DOMAINS = {
    "miodottore.it", "dentisti-italia.it", "docdental.it",
    "google.com", "paginegialle.it", "facebook.com", "fb.com",
    "instagram.com", "linkedin.com", "tiktok.com", "trustpilot.com",
    "yelp.it", "doctolib.it", "guidamedicina.it", "whatclinic.com",
    "docplanner.com", "pro.miodottore.it", "noa.ai",
    "thefork.it", "tripadvisor.it", "restaurantguru.it",
    "booking.com", "trivago.it", "hotels.com", "treatwell.it",
    "prontopro.it", "habitissimo.it", "kompass.com", "europages.it",
    "registroimprese.it",
}

VERTICAL_HINTS = {
    "dentale": ["dent", "odont", "implant", "ortodonz", "stomatolog", "dental"],
    "ristorazione": ["ristor", "trattoria", "osteria", "pizzeria", "cucina", "chef", "menu"],
    "pmi": ["azienda", "impresa", "produzione", "servizi", "soluzioni", "b2b", "certific"],
    "hospitality": ["hotel", "albergo", "camere", "suite", "agriturismo", "b&b", "booking"],
    "benessere_estetica": ["estetica", "benessere", "wellness", "spa", "trattamenti", "beauty"],
    "servizi_casa": ["impianti", "serramenti", "fotovoltaico", "ristruttur", "installazione", "manutenzione"],
    "formazione": ["formazione", "corsi", "academy", "scuola", "training", "docenti"],
    "generic": [],
}

VERTICAL_ALIASES = {
    "dentale": "dentale",
    "dental": "dentale",
    "odontoiatria": "dentale",
    "dentista": "dentale",
    "ristorazione": "ristorazione",
    "ristorante": "ristorazione",
    "restaurant": "ristorazione",
    "food": "ristorazione",
    "horeca": "ristorazione",
    "pmi": "pmi",
    "sme": "pmi",
    "azienda": "pmi",
    "aziende": "pmi",
    "impresa": "pmi",
    "imprese": "pmi",
    "b2b": "pmi",
    "hospitality": "hospitality",
    "hotel": "hospitality",
    "albergo": "hospitality",
    "b&b": "hospitality",
    "beb": "hospitality",
    "agriturismo": "hospitality",
    "ricettivo": "hospitality",
    "benessere": "benessere_estetica",
    "estetica": "benessere_estetica",
    "wellness": "benessere_estetica",
    "spa": "benessere_estetica",
    "beauty": "benessere_estetica",
    "parrucchiere": "benessere_estetica",
    "barber": "benessere_estetica",
    "servizi_casa": "servizi_casa",
    "casa": "servizi_casa",
    "impianti": "servizi_casa",
    "serramenti": "servizi_casa",
    "fotovoltaico": "servizi_casa",
    "edilizia": "servizi_casa",
    "ristrutturazioni": "servizi_casa",
    "formazione": "formazione",
    "corsi": "formazione",
    "academy": "formazione",
    "scuola": "formazione",
    "training": "formazione",
    "education": "formazione",
    "generic": "generic",
    "generico": "generic",
    "altro": "generic",
}

TARGET_SEGMENT_ALIASES = {
    vertical: {
        alias: segment
        for segment, spec in segments.items()
        for alias in spec["aliases"]
    }
    for vertical, segments in TARGET_SEGMENTS_BY_VERTICAL.items()
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
    host = (p.netloc or p.path).lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def clean_text(value):
    value = unescape(re.sub(r"(?s)<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def looks_vertical(text, vertical):
    hay = (text or "").lower()
    return any(h in hay for h in VERTICAL_HINTS.get(vertical, [vertical.lower()]))


def normalize_vertical(value):
    return VERTICAL_ALIASES.get((value or "dentale").strip().lower(), "generic")


def normalize_target_segment(vertical, value):
    vertical = normalize_vertical(vertical)
    raw = (value or "").strip().lower()
    if not raw or raw == "auto":
        return "ristorazione_generic" if vertical == "ristorazione" else vertical
    return TARGET_SEGMENT_ALIASES.get(vertical, {}).get(raw, raw)


def looks_target_segment(text, vertical, target_segment):
    if target_segment in {"", "auto", vertical, "ristorazione_generic"}:
        return True
    target = TARGET_SEGMENTS_BY_VERTICAL.get(vertical, {}).get(target_segment)
    if not target:
        return True
    hay = (text or "").lower()
    return any(h in hay for h in target["hints"])


def review_portals_for(vertical, target_segment):
    target = TARGET_SEGMENTS_BY_VERTICAL.get(vertical, {}).get(target_segment)
    if target:
        return target["review_portals"]
    return REVIEW_PORTALS_BY_VERTICAL.get(vertical, [])


def source_group_summary(vertical, group):
    sources = PRIMARY_INTELLIGENCE_SOURCES_BY_VERTICAL.get(vertical, PRIMARY_INTELLIGENCE_SOURCES_BY_VERTICAL["generic"])
    return " | ".join(sources.get(group, []))


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


def is_disallowed_official_domain(host):
    if not host:
        return True
    if host.startswith(("s3.", "pixel-", "static.")):
        return True
    return any(host == d or host.endswith("." + d) for d in PORTAL_DOMAINS)


def resolve_official_domain(profile_url, portal):
    final_url, html = fetch(profile_url)
    if not html:
        return "", "UNRESOLVED", ""
    for link, label in extract_links(html, final_url or profile_url):
        label_l = clean_text(label).lower()
        if "sito web" not in label_l and "website" not in label_l:
            continue
        host = normalize_domain(link)
        if is_disallowed_official_domain(host):
            continue
        return host, "RESOLVED_FROM_PORTAL_PROFILE", link
    return "", "UNRESOLVED", ""


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


def discover_portal(area, vertical, target_segment, portal, template, limit):
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
        if not looks_target_segment(hay, vertical, target_segment):
            continue
        official_domain, official_state, official_source = resolve_official_domain(link, portal)
        results.append({
            "company": clean_text(label),
            "domain": official_domain,
            "source_url": link,
            "area": area,
            "city": area,
            "country": "IT",
            "vertical": vertical,
            "target_segment": target_segment,
            "discovery_source": "portal_direct",
            "review_source": portal,
            "discovery_query": url,
            "official_domain_state": official_state,
            "official_domain_source": official_source,
        })
        if len(results) >= limit:
            break

    print(f"[PORTAL] {portal} | {area} | fetch=OK | accepted={len(results)}")
    return results


def discover_area(area, vertical, target_segment, limit):
    rows = []
    seen = set()
    portals = PRIMARY_PORTALS_BY_VERTICAL.get(vertical, [])
    for portal, template in portals:
        for row in discover_portal(area, vertical, target_segment, portal, template, limit):
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
    ap.add_argument("--target-segment", default="auto")
    args = ap.parse_args()
    vertical = normalize_vertical(args.vertical)
    target_segment = normalize_target_segment(vertical, args.target_segment)

    areas = [a.strip() for a in args.areas.split(",") if a.strip()]
    if not areas:
        print("Nessuna area specificata")
        return 2

    print("COUNTRY_SCOPE: ITALIA ONLY")
    print("DISCOVERY_MODE: PORTAL_FIRST")
    primary = PRIMARY_PORTALS_BY_VERTICAL.get(vertical, [])
    print("VERTICAL: " + vertical)
    print("TARGET_SEGMENT: " + target_segment)
    print("Primary portals: " + (" | ".join(p for p, _ in primary) if primary else "none validated"))
    print("Primary intelligence - Google: " + source_group_summary(vertical, "google"))
    print("Primary intelligence - reviews: " + source_group_summary(vertical, "review_portals"))
    print("Primary intelligence - social: " + source_group_summary(vertical, "social"))
    print("Primary intelligence - public financials: " + source_group_summary(vertical, "public_financials"))
    disabled = DISABLED_PRIMARY_PORTALS_BY_VERTICAL.get(vertical, [])
    if disabled:
        print("Disabled primary portals: " + " | ".join(f"{p} ({reason})" for p, reason in disabled))
    print("Review portals (max 10): " + " | ".join(review_portals_for(vertical, target_segment)[:10]))

    rows = []
    seen = set()
    per_area = max(5, (args.target + len(areas) - 1) // len(areas))
    for area in areas:
        for row in discover_area(area, vertical, target_segment, per_area * 3):
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
    fields = ["company", "domain", "source_url", "area", "city", "country", "vertical", "target_segment", "discovery_source", "review_source", "discovery_query", "official_domain_state", "official_domain_source"]
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
