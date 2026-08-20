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

USER_AGENT = "Mozilla/5.0 (compatible; RRT-PreScreen/1.2; +public-web-research)"
TIMEOUT = 8
MAX_BYTES = 750_000

CATEGORY_PROFILES = {
    "dentale": {
        "aliases": {"dentale", "dental", "odontoiatria", "dentista"},
        "dimensions": {
            "D1": [r"sedazion", r"odontofob", r"ansia", r"paura", r"senza dolore", r"indolor", r"anestes", r"anestesiolog"],
            "D2": [r"finanzi", r"rate", r"rateizz", r"pagament", r"dilazion", r"costo", r"prezzo", r"preventivo"],
            "D3": [r"implantolog", r"impiant", r"tac", r"cbct", r"scanner", r"3d", r"chirurgia guidata", r"digitale", r"specialist", r"team", r"garanzia"],
            "D4": [r"carico immediato", r"24\s*ore", r"in un giorno", r"stessa giornata", r"same day", r"provvisor", r"all[- ]on[- ]4", r"all[- ]on[- ]four"],
            "D5": [r"perch[eé] scegliere", r"vantagg", r"testimonianz", r"recension", r"faq", r"garanzia", r"esperienza", r"dicono di noi"],
        },
        "high_value_patterns": [
            r"implantolog", r"all[- ]on[- ]4", r"carico immediato", r"ortodonzia invisibile",
            r"invisalign", r"faccette", r"estetica dentale", r"riabilitazione completa", r"chirurgia orale"
        ],
        "structure_patterns": [
            r"\b3\s+(riuniti|sale|poltrone|studi)\b", r"\b4\s+(riuniti|sale|poltrone|studi)\b",
            r"\b5\s+(riuniti|sale|poltrone|studi)\b", r"team", r"equipe", r"staff", r"specialisti",
            r"odontoiatri", r"medici", r"igienist"
        ],
        "commercial_gap_patterns": {
            "no_financing_signal": [r"finanzi", r"rate", r"rateizz", r"pagament", r"dilazion", r"costo", r"prezzo", r"preventivo"],
            "no_fear_reassurance_signal": [r"sedazion", r"odontofob", r"ansia", r"paura", r"senza dolore", r"indolor", r"anestes", r"anestesiolog"],
            "no_social_proof_signal": [r"testimonianz", r"recension", r"dicono di noi"],
            "no_faq_signal": [r"faq", r"domande frequenti"],
            "no_guarantee_signal": [r"garanzia", r"garantito"],
        },
        "page_hints": ["implant", "servizi", "trattamenti", "tecnolog", "chi-siamo", "studio", "team", "faq", "recension", "testimon", "contatti", "sedaz", "finanzi", "invisalign", "faccette"],
        "escalate_requires_high_value": True,
    },
    "ristorazione": {
        "aliases": {"ristorazione", "ristorante", "restaurant", "food", "horeca"},
        "dimensions": {
            "D1": [r"prenota", r"prenotazione", r"riserva", r"tavolo", r"contatt", r"telefono", r"whatsapp"],
            "D2": [r"men[uù]", r"carta", r"prezz", r"coperto", r"degustazione", r"asporto", r"delivery"],
            "D3": [r"cucina", r"chef", r"specialit", r"ingredient", r"territorio", r"stagional", r"cantina", r"vini"],
            "D4": [r"orari", r"aperto", r"chiuso", r"pranzo", r"cena", r"giorni", r"turno"],
            "D5": [r"recension", r"tripadvisor", r"thefork", r"michelin", r"gambero rosso", r"guida", r"storia", r"esperienza", r"gallery"],
        },
        "high_value_patterns": [
            r"degustazione", r"chef", r"cantina", r"vini", r"eventi", r"cerimonie", r"catering",
            r"delivery", r"asporto", r"michelin", r"gambero rosso", r"territorio"
        ],
        "structure_patterns": [
            r"team", r"staff", r"brigata", r"sala", r"cucina", r"chef", r"sommelier", r"cantina", r"posti", r"coperti"
        ],
        "commercial_gap_patterns": {
            "no_booking_signal": [r"prenota", r"prenotazione", r"riserva", r"tavolo"],
            "no_menu_price_signal": [r"men[uù]", r"prezz", r"carta"],
            "no_social_proof_signal": [r"recension", r"tripadvisor", r"thefork", r"guida"],
            "no_hours_signal": [r"orari", r"aperto", r"chiuso", r"pranzo", r"cena"],
            "no_differentiation_signal": [r"chef", r"specialit", r"territorio", r"stagional", r"cantina"],
        },
        "page_hints": ["menu", "carta", "prenot", "contatti", "orari", "chef", "cucina", "cantina", "vini", "eventi", "gallery", "recension", "storia"],
        "escalate_requires_high_value": False,
    },
    "pmi": {
        "aliases": {"pmi", "sme", "azienda", "aziende", "impresa", "imprese", "b2b", "200"},
        "dimensions": {
            "D1": [r"contatt", r"richiedi", r"preventivo", r"consulenza", r"telefono", r"email", r"whatsapp"],
            "D2": [r"servizi", r"soluzioni", r"prodotti", r"catalogo", r"settori", r"applicazioni"],
            "D3": [r"certificat", r"qualit", r"iso", r"partner", r"referenze", r"clienti", r"case stud"],
            "D4": [r"team", r"azienda", r"chi siamo", r"stabilimento", r"produzione", r"laboratorio", r"sedi"],
            "D5": [r"innovazione", r"digital", r"automazione", r"sostenibil", r"export", r"internazionale", r"assistenza"],
        },
        "high_value_patterns": [
            r"b2b", r"su misura", r"custom", r"certificat", r"iso", r"industria 4\.0", r"automazione",
            r"export", r"internazionale", r"assistenza", r"manutenzione", r"partner"
        ],
        "structure_patterns": [
            r"team", r"staff", r"dipendenti", r"collaboratori", r"sedi", r"stabilimento", r"reparto",
            r"produzione", r"laboratorio", r"magazzino", r"ufficio tecnico"
        ],
        "commercial_gap_patterns": {
            "no_contact_signal": [r"contatt", r"telefono", r"email", r"preventivo", r"consulenza"],
            "no_solution_signal": [r"servizi", r"soluzioni", r"prodotti", r"catalogo"],
            "no_proof_signal": [r"referenze", r"clienti", r"case stud", r"certificat"],
            "no_company_scale_signal": [r"team", r"sedi", r"stabilimento", r"produzione", r"laboratorio"],
            "no_differentiation_signal": [r"su misura", r"innovazione", r"qualit", r"partner"],
        },
        "page_hints": ["servizi", "soluzioni", "prodotti", "catalogo", "settori", "azienda", "chi-siamo", "team", "certific", "referenze", "clienti", "contatti", "preventivo"],
        "escalate_requires_high_value": False,
    },
    "hospitality": {
        "aliases": {"hospitality", "hotel", "albergo", "b&b", "beb", "agriturismo", "ricettivo"},
        "dimensions": {
            "D1": [r"prenota", r"booking", r"disponibil", r"camera", r"suite", r"contatt"],
            "D2": [r"prezz", r"tariffe", r"offerte", r"pacchetti", r"promozion", r"gift"],
            "D3": [r"servizi", r"colazione", r"spa", r"piscina", r"parcheggio", r"ristorante", r"wifi"],
            "D4": [r"posizione", r"centro", r"mare", r"montagna", r"aeroporto", r"stazione", r"territorio"],
            "D5": [r"recension", r"tripadvisor", r"booking\.com", r"gallery", r"esperienza", r"famiglie", r"business"],
        },
        "high_value_patterns": [
            r"suite", r"spa", r"wellness", r"meeting", r"eventi", r"pacchetti", r"esperienze",
            r"ristorante", r"business", r"pet friendly"
        ],
        "structure_patterns": [r"camere", r"suite", r"reception", r"staff", r"servizi", r"sale meeting", r"ristorante"],
        "commercial_gap_patterns": {
            "no_booking_signal": [r"prenota", r"booking", r"disponibil"],
            "no_rate_signal": [r"prezz", r"tariffe", r"offerte", r"pacchetti"],
            "no_service_signal": [r"servizi", r"colazione", r"spa", r"parcheggio"],
            "no_location_signal": [r"posizione", r"centro", r"territorio"],
            "no_social_proof_signal": [r"recension", r"tripadvisor", r"booking\.com"],
        },
        "page_hints": ["camere", "suite", "prenota", "booking", "offerte", "servizi", "spa", "meeting", "gallery", "dove-siamo", "contatti"],
        "escalate_requires_high_value": False,
    },
    "benessere_estetica": {
        "aliases": {"benessere", "estetica", "wellness", "spa", "centro estetico", "beauty", "parrucchiere", "barber"},
        "dimensions": {
            "D1": [r"prenota", r"appuntamento", r"contatt", r"whatsapp", r"telefono"],
            "D2": [r"trattamenti", r"servizi", r"listino", r"prezz", r"pacchetti", r"abbonament"],
            "D3": [r"laser", r"viso", r"corpo", r"massaggi", r"epilazione", r"antiage", r"prodotti"],
            "D4": [r"orari", r"aperto", r"giorni", r"sede", r"centro", r"cabine"],
            "D5": [r"recension", r"risultati", r"prima e dopo", r"gallery", r"team", r"esperienza"],
        },
        "high_value_patterns": [
            r"laser", r"epilazione", r"antiage", r"viso", r"corpo", r"pacchetti", r"abbonament",
            r"consulenza", r"risultati", r"prima e dopo"
        ],
        "structure_patterns": [r"team", r"staff", r"cabine", r"centro", r"sede", r"operatori", r"specialist"],
        "commercial_gap_patterns": {
            "no_booking_signal": [r"prenota", r"appuntamento", r"whatsapp"],
            "no_price_signal": [r"listino", r"prezz", r"pacchetti", r"abbonament"],
            "no_treatment_signal": [r"trattamenti", r"servizi", r"laser", r"viso", r"corpo"],
            "no_social_proof_signal": [r"recension", r"risultati", r"prima e dopo"],
            "no_hours_signal": [r"orari", r"aperto", r"giorni"],
        },
        "page_hints": ["trattamenti", "servizi", "listino", "prezzi", "prenota", "appuntamento", "team", "gallery", "risultati", "contatti"],
        "escalate_requires_high_value": False,
    },
    "servizi_casa": {
        "aliases": {"servizi_casa", "casa", "impianti", "serramenti", "fotovoltaico", "edilizia", "ristrutturazioni", "climatizzazione", "condizionamento"},
        "dimensions": {
            "D1": [r"preventivo", r"sopralluogo", r"contatt", r"telefono", r"urgenz", r"assistenza"],
            "D2": [r"servizi", r"installazione", r"manutenzione", r"riparazione", r"ristrutturazione", r"fornitura"],
            "D3": [r"certificat", r"garanzia", r"detrazion", r"bonus", r"finanzi", r"chiavi in mano"],
            "D4": [r"zone servite", r"provincia", r"intervento", r"tempi", r"24\s*ore", r"emergenza"],
            "D5": [r"recension", r"lavori", r"realizzazioni", r"portfolio", r"prima e dopo", r"esperienza"],
        },
        "high_value_patterns": [
            r"fotovoltaico", r"pompa di calore", r"serramenti", r"ristrutturazione", r"chiavi in mano",
            r"detrazion", r"bonus", r"garanzia", r"manutenzione", r"assistenza"
        ],
        "structure_patterns": [r"tecnici", r"squadra", r"team", r"installatori", r"certificat", r"magazzino", r"sede"],
        "commercial_gap_patterns": {
            "no_quote_signal": [r"preventivo", r"sopralluogo", r"contatt"],
            "no_service_signal": [r"servizi", r"installazione", r"manutenzione", r"riparazione"],
            "no_trust_signal": [r"certificat", r"garanzia", r"detrazion", r"bonus"],
            "no_area_signal": [r"zone servite", r"provincia", r"intervento"],
            "no_work_proof_signal": [r"realizzazioni", r"portfolio", r"recension", r"lavori"],
        },
        "page_hints": ["servizi", "installazione", "manutenzione", "preventivo", "sopralluogo", "realizzazioni", "portfolio", "garanzia", "contatti"],
        "escalate_requires_high_value": False,
    },
    "formazione": {
        "aliases": {"formazione", "corsi", "academy", "scuola", "training", "education"},
        "dimensions": {
            "D1": [r"iscriv", r"richiedi informazioni", r"contatt", r"open day", r"colloquio"],
            "D2": [r"corsi", r"programma", r"calendario", r"lezioni", r"online", r"in aula"],
            "D3": [r"certificat", r"attestato", r"docenti", r"tutor", r"placement", r"stage"],
            "D4": [r"durata", r"ore", r"date", r"prezz", r"finanzi", r"rate"],
            "D5": [r"recension", r"testimonianz", r"studenti", r"aziende partner", r"success story"],
        },
        "high_value_patterns": [
            r"certificat", r"attestato", r"placement", r"stage", r"aziende partner", r"finanzi",
            r"rate", r"online", r"in aula", r"tutor"
        ],
        "structure_patterns": [r"docenti", r"tutor", r"aule", r"sedi", r"academy", r"staff", r"partner"],
        "commercial_gap_patterns": {
            "no_enrollment_signal": [r"iscriv", r"richiedi informazioni", r"open day", r"colloquio"],
            "no_program_signal": [r"corsi", r"programma", r"calendario", r"lezioni"],
            "no_price_signal": [r"prezz", r"finanzi", r"rate"],
            "no_outcome_signal": [r"placement", r"stage", r"attestato", r"certificat"],
            "no_social_proof_signal": [r"recension", r"testimonianz", r"studenti"],
        },
        "page_hints": ["corsi", "programma", "calendario", "iscriv", "docenti", "placement", "stage", "prezzi", "contatti", "open-day"],
        "escalate_requires_high_value": False,
    },
    "generic": {
        "aliases": {"generic", "generico", "altro", "other"},
        "dimensions": {
            "D1": [r"contatt", r"telefono", r"email", r"whatsapp", r"prenota", r"richiedi"],
            "D2": [r"prezz", r"costo", r"preventivo", r"pagament", r"finanzi", r"offerta"],
            "D3": [r"servizi", r"prodotti", r"soluzioni", r"specialist", r"team", r"qualit"],
            "D4": [r"tempi", r"consegna", r"orari", r"aperto", r"processo", r"fasi"],
            "D5": [r"recension", r"testimonianz", r"case stud", r"portfolio", r"esperienza", r"perch[eé] scegliere"],
        },
        "high_value_patterns": [r"premium", r"specialist", r"su misura", r"certificat", r"esperienza", r"garanzia"],
        "structure_patterns": [r"team", r"staff", r"sedi", r"filiali", r"partner", r"certificat"],
        "commercial_gap_patterns": {
            "no_contact_signal": [r"contatt", r"telefono", r"email", r"whatsapp"],
            "no_price_signal": [r"prezz", r"costo", r"preventivo"],
            "no_service_signal": [r"servizi", r"prodotti", r"soluzioni"],
            "no_social_proof_signal": [r"recension", r"testimonianz", r"portfolio"],
            "no_differentiation_signal": [r"perch[eé] scegliere", r"vantagg", r"specialist"],
        },
        "page_hints": ["servizi", "prodotti", "soluzioni", "chi-siamo", "team", "portfolio", "recension", "contatti", "prezzi", "preventivo", "faq"],
        "escalate_requires_high_value": False,
    },
}

PROFILE_ALIASES = {
    alias: name
    for name, profile in CATEGORY_PROFILES.items()
    for alias in profile["aliases"]
}

SOCIAL_DOMAINS = {
    "facebook": ["facebook.com", "fb.com"],
    "instagram": ["instagram.com"],
    "linkedin": ["linkedin.com"],
    "tiktok": ["tiktok.com"],
}

SOCIAL_REPUTATION_PATTERNS = {
    "facebook": [r"recension", r"raccomand", r"recommend", r"rating", r"valutaz"],
    "instagram": [r"testimonianz", r"recension", r"dicono di noi", r"feedback", r"pazient"],
    "linkedin": [r"testimonianz", r"recension", r"recommend", r"feedback", r"pazient"],
    "tiktok": [r"testimonianz", r"recension", r"feedback", r"pazient"],
}

YOUTH_GROWTH_PATTERNS = [
    r"nuovo studio", r"nuova sede", r"inaugurat", r"dal 20(1[8-9]|2[0-6])", r"fondat[oa] nel 20(1[8-9]|2[0-6])",
    r"ampliament", r"crescita", r"innovazione", r"tecnologia", r"digitale", r"nuova generazione"
]

CONTACT_PATTERNS = [
    re.compile(r"mailto:", re.I),
    re.compile(r"tel:", re.I),
    re.compile(r"whatsapp|wa\.me", re.I),
    re.compile(r"prenota|contattaci|richiedi.*appuntamento|appuntamento", re.I),
]

TARGET_SEGMENTS_BY_VERTICAL = {
    "pmi": {
        "climatizzazione_impianti": [
            r"climatizzazione", r"condizionamento", r"pompa di calore", r"pompe di calore",
            r"impianti termici", r"termoidraulica", r"ventilazione", r"vmc",
            r"f-gas", r"fgas", r"iso 9001", r"terzo responsabile", r"mepa", r"soa"
        ],
    },
    "servizi_casa": {
        "climatizzazione_impianti": [
            r"climatizzazione", r"condizionamento", r"pompa di calore", r"pompe di calore",
            r"impianti termici", r"termoidraulica", r"ventilazione", r"vmc",
            r"installazione", r"manutenzione", r"assistenza", r"detrazion", r"bonus"
        ],
    },
    "ristorazione": {
        "fine_dining": [r"fine dining", r"stell", r"michelin", r"degustazione", r"chef", r"gourmet", r"alta cucina"],
        "pizzeria": [r"pizzeria", r"pizza", r"forno a legna", r"impasto", r"lievitazione"],
        "trattoria_osteria": [r"trattoria", r"osteria", r"cucina tradizionale", r"cucina romana", r"cucina tipica"],
        "sushi_etnico": [r"sushi", r"giapponese", r"cinese", r"thai", r"indiano", r"fusion", r"poke"],
        "delivery_asporto": [r"delivery", r"asporto", r"take away", r"ordina online", r"consegna"],
        "eventi_catering": [r"eventi", r"cerimonie", r"catering", r"banchetti", r"matrimoni", r"feste private"],
        "enoteca_wine_bar": [r"enoteca", r"wine bar", r"cantina", r"vini", r"sommelier"],
        "bar_cafe": [r"\bbar\b", r"caff[eè]", r"colazioni", r"aperitivo", r"cocktail"],
    },
    "generic": {},
}


def profile_for(vertical):
    name = normalize_vertical(vertical)
    profile = dict(CATEGORY_PROFILES[name])
    profile["name"] = name
    return profile


def normalize_vertical(vertical):
    key = (vertical or "dentale").strip().lower()
    return PROFILE_ALIASES.get(key, "generic")


def normalize_domain(value):
    value = (value or "").strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    p = urllib.parse.urlparse(value)
    host = (p.netloc or p.path).strip().lower()
    host = host.split("@")[-1].split(":")[0]
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


def extract_internal_links(html, current_url, domain, profile):
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
        score = sum(1 for hint in profile["page_hints"] if hint in path)
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


def extract_social_links(html):
    found = {name: "" for name in SOCIAL_DOMAINS}
    for href in re.findall(r'(?i)href=["\']([^"\']+)', html or ""):
        href = unescape(href.strip())
        host = normalize_domain(href)
        if not host:
            continue
        for name, domains in SOCIAL_DOMAINS.items():
            if any(host == d or host.endswith("." + d) for d in domains):
                found[name] = href
    return found


def social_reputation_from_text(text):
    return {name: count_hits(text, pats) for name, pats in SOCIAL_REPUTATION_PATTERNS.items()}


def count_hits(text, patterns):
    text = (text or "").lower()
    return sum(1 for p in patterns if re.search(p, text, re.I))


def infer_target_segment(vertical, text):
    segments = TARGET_SEGMENTS_BY_VERTICAL.get(vertical) or {}
    if not segments:
        return vertical
    scored = [(name, count_hits(text, patterns)) for name, patterns in segments.items()]
    scored = [(name, score) for name, score in scored if score > 0]
    if not scored:
        return "ristorazione_generic" if vertical == "ristorazione" else vertical
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored[0][0]


def scan(domain, profile):
    empty_social = {name: "" for name in SOCIAL_DOMAINS}
    empty_rep = {name: 0 for name in SOCIAL_DOMAINS}
    dimensions = profile["dimensions"]
    if not domain:
        return {"website_live": 0, "fetch_state": "NO_DOMAIN", "pages_found": 0, "contactability": 0, "hits": {d: 0 for d in dimensions}, "high_value_hits": 0, "structure_hits": 0, "youth_growth_hits": 0, "commercial_gap_count": 0, "social_links": empty_social, "social_reputation_hits": empty_rep, "target_segment": infer_target_segment(profile["name"], "")}

    homepage = base_url(domain)
    final_url, html, state = fetch(homepage)
    if state != "OK":
        final_url, html, state2 = fetch("http://" + domain)
        state = state2
    if state != "OK" or not html:
        return {"website_live": 0, "fetch_state": state, "pages_found": 0, "contactability": 0, "hits": {d: 0 for d in dimensions}, "high_value_hits": 0, "structure_hits": 0, "youth_growth_hits": 0, "commercial_gap_count": 0, "social_links": empty_social, "social_reputation_hits": empty_rep, "target_segment": infer_target_segment(profile["name"], "")}

    pages = [(final_url, html)]
    for url in extract_internal_links(html, final_url, domain, profile):
        fetched_url, page_html, page_state = fetch(url)
        if page_state == "OK" and page_html:
            pages.append((fetched_url, page_html))

    combined_html = " ".join(p[1] for p in pages)
    text = strip_html(combined_html)
    hits = {d: count_hits(text, pats) for d, pats in dimensions.items()}
    contactability = sum(1 for p in CONTACT_PATTERNS if p.search(combined_html))
    high_value_hits = count_hits(text, profile["high_value_patterns"])
    structure_hits = count_hits(text, profile["structure_patterns"])
    youth_growth_hits = count_hits(text, YOUTH_GROWTH_PATTERNS)
    commercial_gap_count = sum(1 for pats in profile["commercial_gap_patterns"].values() if count_hits(text, pats) == 0)
    social_links = extract_social_links(combined_html)
    social_reputation_hits = social_reputation_from_text(text)

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
        "social_links": social_links,
        "social_reputation_hits": social_reputation_hits,
        "target_segment": infer_target_segment(profile["name"], text),
    }


def score_row(result):
    if not result["website_live"]:
        return 0
    hits = result["hits"]
    observed_dims = sum(1 for v in hits.values() if v > 0)
    total_hits = sum(min(v, 5) for v in hits.values())
    social_presence_count = sum(1 for v in result["social_links"].values() if v)
    social_rep_count = sum(1 for v in result["social_reputation_hits"].values() if v > 0)
    score = 10
    score += min(result["pages_found"], 6) * 2
    score += observed_dims * 5
    score += min(total_hits, 12)
    score += min(result["high_value_hits"], 5) * 5
    score += min(result["structure_hits"], 4) * 4
    score += min(result["youth_growth_hits"], 4) * 5
    score += min(result["commercial_gap_count"], 4) * 3
    score += 8 if result["contactability"] >= 2 else 4 if result["contactability"] == 1 else 0
    score += min(social_presence_count, 4) * 2
    score += min(social_rep_count, 4) * 2
    return min(score, 100)


def decision(score, website_live, observed_dims, fetch_state, high_value_hits, structure_hits, profile):
    if not website_live:
        if fetch_state in {"NO_OFFICIAL_DOMAIN", "PORTAL_ONLY"}:
            return "COLLECTION_RESTRICTED"
        if fetch_state == "NO_DOMAIN":
            return "REJECT"
        return "COLLECTION_RESTRICTED"
    high_value_ok = high_value_hits >= 1 or not profile["escalate_requires_high_value"]
    if score >= 70 and high_value_ok and (structure_hits >= 1 or observed_dims >= 3):
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
        "company", "domain", "source_url", "official_domain_state", "official_domain_source", "city", "vertical", "target_segment", "website_live", "fetch_state", "pages_found",
        "phone", "mobile_phone", "email", "address", "google_maps_search_url", "registroimprese_url",
        "D1_hits", "D2_hits", "D3_hits", "D4_hits", "D5_hits", "contactability", "observed_dimensions",
        "high_value_hits", "structure_hits", "youth_growth_hits", "commercial_gap_count",
        "facebook_url", "instagram_url", "linkedin_url", "tiktok_url",
        "facebook_reputation_hits", "instagram_reputation_hits", "linkedin_reputation_hits", "tiktok_reputation_hits",
        "social_presence_count", "social_reputation_channels",
        "preliminary_score", "decision"
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for idx, row in enumerate(rows, 1):
            company = (row.get("company") or row.get("name") or "").strip()
            domain = normalize_domain(row.get("domain") or row.get("website") or row.get("official_domain"))
            source_url = (row.get("source_url") or "").strip()
            official_domain_state = (row.get("official_domain_state") or "").strip()
            official_domain_source = (row.get("official_domain_source") or "").strip()
            city = (row.get("city") or "").strip()
            phone = (row.get("phone") or "").strip()
            mobile_phone = (row.get("mobile_phone") or row.get("mobile") or row.get("whatsapp") or "").strip()
            email = (row.get("email") or "").strip()
            address = (row.get("address") or "").strip()
            google_maps_search_url = (row.get("google_maps_search_url") or row.get("google_url") or "").strip()
            registroimprese_url = (row.get("registroimprese_url") or "").strip()
            vertical = normalize_vertical(row.get("vertical"))
            profile = profile_for(vertical)
            result = scan(domain, profile)
            target_segment = (row.get("target_segment") or row.get("segment") or result["target_segment"]).strip()
            if not domain and source_url:
                result["fetch_state"] = "NO_OFFICIAL_DOMAIN"
            hits = result["hits"]
            observed_dims = sum(1 for v in hits.values() if v > 0)
            social_presence_count = sum(1 for v in result["social_links"].values() if v)
            social_reputation_channels = sum(1 for v in result["social_reputation_hits"].values() if v > 0)
            score = score_row(result)
            gate = decision(score, result["website_live"], observed_dims, result["fetch_state"], result["high_value_hits"], result["structure_hits"], profile)
            writer.writerow({
                "company": company,
                "domain": domain,
                "source_url": source_url,
                "official_domain_state": official_domain_state,
                "official_domain_source": official_domain_source,
                "city": city,
                "vertical": vertical,
                "target_segment": target_segment,
                "website_live": result["website_live"],
                "fetch_state": result["fetch_state"],
                "pages_found": result["pages_found"],
                "phone": phone,
                "mobile_phone": mobile_phone,
                "email": email,
                "address": address,
                "google_maps_search_url": google_maps_search_url,
                "registroimprese_url": registroimprese_url,
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
                "facebook_url": result["social_links"]["facebook"],
                "instagram_url": result["social_links"]["instagram"],
                "linkedin_url": result["social_links"]["linkedin"],
                "tiktok_url": result["social_links"]["tiktok"],
                "facebook_reputation_hits": result["social_reputation_hits"]["facebook"],
                "instagram_reputation_hits": result["social_reputation_hits"]["instagram"],
                "linkedin_reputation_hits": result["social_reputation_hits"]["linkedin"],
                "tiktok_reputation_hits": result["social_reputation_hits"]["tiktok"],
                "social_presence_count": social_presence_count,
                "social_reputation_channels": social_reputation_channels,
                "preliminary_score": score,
                "decision": gate,
            })
            print(f"[{idx}/{len(rows)}] {company or domain}: {gate} ({score}) HV={result['high_value_hits']} STR={result['structure_hits']} YG={result['youth_growth_hits']} GAP={result['commercial_gap_count']} SOC={social_presence_count}/{social_reputation_channels}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
