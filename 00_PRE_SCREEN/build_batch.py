#!/usr/bin/env python3
import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; RRT-BatchBuilder/2.0; +public-web-research)"
OPEN_DATA_USER_AGENT = "RRT-BatchBuilder/2.0 public-web-research"
TIMEOUT = 8
OPEN_DATA_TIMEOUT = 30
MAX_BYTES = 1_000_000
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
DEFAULT_BBOX_CACHE = "00_PRE_SCREEN/open_data_city_bbox_cache.json"

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

OPEN_DATA_VERTICALS = {"ristorazione", "hospitality", "benessere_estetica", "servizi_casa", "formazione", "pmi"}
OSM_TAG_QUERIES = {
    "ristorazione": [
        '["amenity"~"restaurant|cafe|bar|fast_food|pub|ice_cream"]',
    ],
    "hospitality": [
        '["tourism"~"hotel|guest_house|hostel|apartment|chalet|camp_site|agritourism"]',
    ],
    "benessere_estetica": [
        '["shop"~"beauty|hairdresser|massage"]',
        '["leisure"="spa"]',
    ],
    "servizi_casa": [
        '["shop"~"hardware|doityourself|paint|furniture|kitchen|bathroom_furnishing"]',
        '["craft"~"electrician|plumber|carpenter|roofer|painter|builder|glaziery"]',
    ],
    "formazione": [
        '["amenity"~"school|college|university|music_school|driving_school|language_school"]',
        '["office"="educational_institution"]',
    ],
    "pmi": [
        '["office"~"company|it|consulting|accountant|architect|engineer"]',
        '["craft"]',
        '["industrial"]',
    ],
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
        "review_portals": ["paginegialle.it", "trustpilot.com", "kompass.com", "europages.it", "prontopro.it", "habitissimo.it"],
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
    "pmi": {
        "climatizzazione_impianti": {
            "aliases": {"climatizzazione", "condizionamento", "clima", "impianti_clima", "impianti_termici", "hvac", "pompe_calore"},
            "review_portals": ["google.com", "paginegialle.it", "prontopro.it", "habitissimo.it", "kompass.com", "europages.it"],
            "hints": ["climatizzazione", "condizionamento", "pompa di calore", "pompe di calore", "impianti termici", "termoidraulica", "vmc", "fgas"],
        },
    },
    "servizi_casa": {
        "climatizzazione_impianti": {
            "aliases": {"climatizzazione", "condizionamento", "clima", "impianti_clima", "impianti_termici", "hvac", "pompe_calore"},
            "review_portals": ["google.com", "paginegialle.it", "prontopro.it", "habitissimo.it", "trustpilot.com"],
            "hints": ["climatizzazione", "condizionamento", "pompa di calore", "pompe di calore", "impianti termici", "termoidraulica", "vmc", "fgas"],
        },
    },
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


def fetch_json(url, data=None, retries=1):
    headers = {"User-Agent": OPEN_DATA_USER_AGENT}
    if data is None:
        headers["Accept"] = "application/json"
    if data is not None:
        data = data.encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "*/*"
    req = urllib.request.Request(url, data=data, headers=headers)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=OPEN_DATA_TIMEOUT) as resp:
                raw = resp.read(MAX_BYTES)
                charset = resp.headers.get_content_charset() or "utf-8"
                return json.loads(raw.decode(charset, errors="replace"))
        except Exception:
            if attempt < retries:
                time.sleep(0.6 * (attempt + 1))
    return None


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


def first_tag(tags, *names):
    for name in names:
        value = clean_text(tags.get(name, ""))
        if value:
            return value
    return ""


def compose_address(tags, fallback_city):
    parts = [
        first_tag(tags, "addr:street"),
        first_tag(tags, "addr:housenumber"),
        first_tag(tags, "addr:postcode"),
        first_tag(tags, "addr:city") or fallback_city,
    ]
    return clean_text(" ".join(part for part in parts if part))


def osm_object_url(element):
    osm_type = element.get("type", "")
    osm_id = element.get("id", "")
    if not osm_type or not osm_id:
        return ""
    return f"https://www.openstreetmap.org/{osm_type}/{osm_id}"


def element_lat_lon(element):
    if "lat" in element and "lon" in element:
        return str(element["lat"]), str(element["lon"])
    center = element.get("center") or {}
    return str(center.get("lat", "")), str(center.get("lon", ""))


def parse_bbox(value, label="manual_bbox"):
    if not value:
        return None
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise ValueError("--bbox richiede formato south,west,north,east")
    south, west, north, east = parts
    for part in parts:
        float(part)
    return {"south": south, "west": west, "north": north, "east": east, "display_name": label}


def load_bbox_cache(path):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_bbox_cache(path, data):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def resolve_city_bbox(area, bbox_cache_path=None, bbox_override=None):
    if bbox_override:
        return dict(bbox_override)
    cache_key = area.strip().lower()
    cache = load_bbox_cache(bbox_cache_path)
    if cache_key in cache:
        return cache[cache_key]
    query = urllib.parse.urlencode({
        "city": area,
        "country": "Italia",
        "format": "json",
        "limit": "3",
        "addressdetails": "1",
        "featureType": "city",
    })
    data = fetch_json(f"{NOMINATIM_URL}?{query}", retries=1)
    if not data:
        return None
    chosen = data[0]
    for candidate in data:
        address = candidate.get("address") or {}
        if (address.get("city") or address.get("town") or address.get("municipality") or "").lower() == area.lower():
            chosen = candidate
            break
    bbox = chosen.get("boundingbox") or []
    if len(bbox) != 4:
        return None
    south, north, west, east = bbox
    bbox = {
        "south": south,
        "north": north,
        "west": west,
        "east": east,
        "display_name": chosen.get("display_name", area),
    }
    if bbox_cache_path:
        cache[cache_key] = bbox
        save_bbox_cache(bbox_cache_path, cache)
    return bbox


def osm_target_filter(target_segment):
    if target_segment == "pizzeria":
        return ['["cuisine"~"pizza|italian",i]', '["name"~"pizzeria|pizza",i]']
    if target_segment == "bar_cafe":
        return ['["amenity"~"cafe|bar|pub"]']
    if target_segment == "sushi_etnico":
        return ['["cuisine"~"sushi|japanese|chinese|thai|indian|asian|fusion|poke",i]']
    if target_segment == "trattoria_osteria":
        return ['["name"~"trattoria|osteria",i]', '["cuisine"~"regional|italian",i]']
    if target_segment == "enoteca_wine_bar":
        return ['["amenity"~"bar|pub"]', '["name"~"enoteca|wine",i]']
    return []


def overpass_query(vertical, target_segment, bbox, limit):
    selectors = OSM_TAG_QUERIES.get(vertical, [])
    bbox_expr = f'({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]})'
    blocks = []
    for selector in selectors:
        blocks.extend([
            f"node{selector}{bbox_expr};",
            f"way{selector}{bbox_expr};",
        ])
    return "[out:json][timeout:20];(" + "".join(blocks) + f");out center tags qt {max(limit * 8, 80)};"


def row_matches_target(row, tags, vertical, target_segment):
    if target_segment in {"", "auto", vertical, "ristorazione_generic"}:
        return True
    hay = " ".join([
        row.get("company", ""),
        row.get("address", ""),
        tags.get("cuisine", ""),
        tags.get("amenity", ""),
        tags.get("shop", ""),
        tags.get("craft", ""),
        tags.get("office", ""),
        tags.get("industrial", ""),
        tags.get("description", ""),
        tags.get("service", ""),
    ]).lower()
    target = TARGET_SEGMENTS_BY_VERTICAL.get(vertical, {}).get(target_segment, {})
    hints = target.get("hints", [])
    return any(hint.lower() in hay for hint in hints)


def row_matches_area(tags, area):
    tagged_city = first_tag(tags, "addr:city", "is_in:city")
    if not tagged_city:
        return True
    return tagged_city.lower() == area.lower()


def osm_row_from_element(element, area, vertical, target_segment, bbox):
    tags = element.get("tags") or {}
    company = first_tag(tags, "name", "operator", "brand")
    if not company:
        return None
    website = first_tag(tags, "website", "contact:website", "url")
    domain = normalize_domain(website)
    lat, lon = element_lat_lon(element)
    source_url = osm_object_url(element)
    search_query = " ".join(p for p in [company, area] if p)
    return {
        "company": company,
        "domain": domain,
        "source_url": source_url,
        "area": area,
        "city": first_tag(tags, "addr:city") or area,
        "country": "IT",
        "vertical": vertical,
        "target_segment": target_segment,
        "phone": first_tag(tags, "phone", "contact:phone"),
        "mobile_phone": first_tag(tags, "mobile", "contact:mobile", "contact:whatsapp"),
        "email": first_tag(tags, "email", "contact:email"),
        "address": compose_address(tags, area),
        "latitude": lat,
        "longitude": lon,
        "discovery_source": "open_data_city",
        "review_source": "open_data_map",
        "discovery_query": bbox.get("display_name", area),
        "official_domain_state": "RESOLVED_FROM_OPEN_DATA_WEBSITE" if domain else "UNRESOLVED",
        "official_domain_source": website,
        "google_url": "https://www.google.com/maps/search/" + urllib.parse.quote_plus(search_query),
        "google_maps_search_url": "https://www.google.com/maps/search/" + urllib.parse.quote_plus(search_query),
        "tripadvisor_search_url": "https://www.tripadvisor.it/Search?q=" + urllib.parse.quote_plus(search_query),
        "registroimprese_url": "https://www.registroimprese.it/ricerca-libera?p_p_id=ricercalibera&search=" + urllib.parse.quote_plus(company),
    }


def discover_open_data_area(area, vertical, target_segment, limit, bbox_override=None, bbox_cache_path=DEFAULT_BBOX_CACHE):
    bbox = resolve_city_bbox(area, bbox_cache_path=bbox_cache_path, bbox_override=bbox_override)
    time.sleep(1.1)
    if not bbox:
        print(f"[OPEN_DATA] {area} | geocode=FAIL")
        return []
    query = overpass_query(vertical, target_segment, bbox, limit)
    data = None
    used_endpoint = ""
    for endpoint in OVERPASS_URLS:
        data = fetch_json(endpoint, data=urllib.parse.urlencode({"data": query}), retries=1)
        if data:
            used_endpoint = endpoint
            break
    if not data:
        print(f"[OPEN_DATA] {area} | overpass=FAIL")
        return []
    rows = []
    seen = set()
    for element in data.get("elements", []):
        tags = element.get("tags") or {}
        if not row_matches_area(tags, area):
            continue
        row = osm_row_from_element(element, area, vertical, target_segment, bbox)
        if not row:
            continue
        if not row_matches_target(row, tags, vertical, target_segment):
            continue
        key = (company_key(row["company"]), row.get("address"), row.get("source_url"))
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
        if len(rows) >= limit:
            break
    print(f"[OPEN_DATA] {area} | source=open_data_city | endpoint=public_map_api | accepted={len(rows)}")
    return rows


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


def discover_area_auto(area, vertical, target_segment, limit, bbox_override=None, bbox_cache_path=DEFAULT_BBOX_CACHE):
    if vertical in OPEN_DATA_VERTICALS:
        rows = discover_open_data_area(area, vertical, target_segment, limit, bbox_override=bbox_override, bbox_cache_path=bbox_cache_path)
        if rows:
            return rows
    return discover_area(area, vertical, target_segment, limit)


def main():
    ap = argparse.ArgumentParser(description="RRT Italy-only portal-first batch builder")
    ap.add_argument("output_csv")
    ap.add_argument("--areas", required=True)
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--vertical", default="dentale")
    ap.add_argument("--target-segment", default="auto")
    ap.add_argument("--bbox", help="Manual area bounding box in south,west,north,east format; valid only with one area")
    ap.add_argument("--bbox-cache", default=DEFAULT_BBOX_CACHE, help="JSON cache for city bounding boxes")
    args = ap.parse_args()
    vertical = normalize_vertical(args.vertical)
    target_segment = normalize_target_segment(vertical, args.target_segment)

    areas = [a.strip() for a in args.areas.split(",") if a.strip()]
    if not areas:
        print("Nessuna area specificata")
        return 2
    if args.bbox and len(areas) != 1:
        print("--bbox puo essere usato solo con una singola area")
        return 2
    try:
        bbox_override = parse_bbox(args.bbox, label=f"manual_bbox:{areas[0]}") if args.bbox else None
    except ValueError as exc:
        print(str(exc))
        return 2

    print("COUNTRY_SCOPE: ITALIA ONLY")
    print("DISCOVERY_MODE: OPEN_DATA_FIRST" if vertical in OPEN_DATA_VERTICALS else "DISCOVERY_MODE: PORTAL_FIRST")
    primary = PRIMARY_PORTALS_BY_VERTICAL.get(vertical, [])
    print("VERTICAL: " + vertical)
    print("TARGET_SEGMENT: " + target_segment)
    print("Primary portals: " + (" | ".join(p for p, _ in primary) if primary else "none validated"))
    if vertical in OPEN_DATA_VERTICALS:
        print("Open data primary discovery: public city map data via bounding box")
        print("Open data bbox cache: " + (args.bbox_cache or "disabled"))
        if bbox_override:
            print("Open data manual bbox: " + args.bbox)
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
        for row in discover_area_auto(area, vertical, target_segment, per_area * 3, bbox_override=bbox_override, bbox_cache_path=args.bbox_cache):
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
    fields = [
        "company", "domain", "source_url", "area", "city", "country", "vertical", "target_segment",
        "phone", "mobile_phone", "email", "address", "latitude", "longitude",
        "google_url", "google_maps_search_url", "tripadvisor_search_url", "registroimprese_url",
        "discovery_source", "review_source", "discovery_query", "official_domain_state", "official_domain_source",
    ]
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
