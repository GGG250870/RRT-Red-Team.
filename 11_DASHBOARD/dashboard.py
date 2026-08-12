#!/usr/bin/env python3
import argparse
import csv
import json
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path


DECISION_ORDER = ["ESCALATE", "SHORTLIST", "COLLECTION_RESTRICTED", "REJECT"]
SOURCE_COLUMNS = {
    "official_website": ["domain", "website_live"],
    "contacts": ["phone", "telefono", "mobile_phone", "mobile", "cellulare", "whatsapp", "email", "mail", "address", "indirizzo"],
    "google": ["google_url", "google_rating", "google_review_count", "google_place_id"],
    "review_portals": ["source_url", "review_source", "review_portal_url"],
    "social": ["facebook_url", "instagram_url", "linkedin_url", "tiktok_url"],
    "public_financials": ["financial_source_url", "balance_sheet_url", "registroimprese_url", "vat_id", "piva"],
}
EXPORT_COLUMNS = [
    "rank", "company", "domain", "city", "vertical", "target_segment", "decision",
    "phone", "mobile_phone", "email", "address",
    "preliminary_score", "fetch_state", "online_enrichment_state", "google_state",
    "google_rating", "google_review_count", "social_presence_count",
    "public_financials_state", "next_best_action", "operation_cost_eur",
]


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


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def xml_escape(value):
    return escape(str(value or ""), quote=True)


def norm(value):
    return (value or "").strip()


def as_int(value):
    try:
        return int(float(norm(value) or "0"))
    except ValueError:
        return 0


def as_score(value):
    return max(0, min(100, as_int(value)))


def eur(value=0.0):
    return f"EUR {value:.4f}"


def row_id(row, index):
    raw = norm(row.get("company")) or norm(row.get("domain")) or f"prospect-{index}"
    clean = "".join(ch.lower() if ch.isalnum() else "-" for ch in raw)
    clean = "-".join(part for part in clean.split("-") if part)
    return clean[:70] or f"prospect-{index}"


def source_state(row, columns):
    found = False
    restricted = norm(row.get("fetch_state")) in {"COLLECTION_RESTRICTED", "URL_ERROR", "TIMEOUT", "HTTP_403", "HTTP_429"}
    for col in columns:
        value = norm(row.get(col))
        if value and value not in {"0", "NO", "UNRESOLVED"}:
            found = True
            break
    if found:
        return "FOUND"
    if restricted and "website_live" in columns:
        return "COLLECTION_RESTRICTED"
    return "NOT_CHECKED"


def source_coverage(row):
    return {name: source_state(row, columns) for name, columns in SOURCE_COLUMNS.items()}


CONTACT_ALIASES = {
    "phone": ["phone", "telefono", "telephone", "tel"],
    "mobile_phone": ["mobile_phone", "mobile", "cellulare", "whatsapp", "whatsapp_phone"],
    "email": ["email", "mail", "e_mail"],
    "address": ["address", "indirizzo", "street_address", "sede", "location"],
}


def contact_value(row, key):
    for column in CONTACT_ALIASES[key]:
        value = norm(row.get(column))
        if value:
            return value
    return ""


def contact_summary_lines(row):
    values = {
        "Telefono": contact_value(row, "phone") or "NON_TROVATO",
        "Cellulare/WhatsApp": contact_value(row, "mobile_phone") or "NON_TROVATO",
        "Email": contact_value(row, "email") or "NON_TROVATA",
        "Indirizzo": contact_value(row, "address") or "NON_TROVATO",
    }
    return [f"- {label}: {value}" for label, value in values.items()]


def contact_html(row):
    values = [
        ("Telefono", contact_value(row, "phone") or "NON_TROVATO"),
        ("Cellulare/WhatsApp", contact_value(row, "mobile_phone") or "NON_TROVATO"),
        ("Email", contact_value(row, "email") or "NON_TROVATA"),
        ("Indirizzo", contact_value(row, "address") or "NON_TROVATO"),
    ]
    return "".join(f"<span>{escape(label)}: {escape(value)}</span>" for label, value in values)


def explainable_scores(row):
    dims = [as_int(row.get(f"D{i}_hits")) for i in range(1, 6)]
    observed = as_int(row.get("observed_dimensions"))
    preliminary = as_score(row.get("preliminary_score"))
    review_volume = as_int(row.get("google_review_count"))
    rating = 0
    try:
        rating = float(norm(row.get("google_rating")) or "0")
    except ValueError:
        rating = 0
    coverage = source_coverage(row)
    found_sources = sum(1 for state in coverage.values() if state == "FOUND")
    social_presence = as_int(row.get("social_presence_count"))
    financial_found = 1 if coverage["public_financials"] == "FOUND" else 0
    return {
        "category_fit_score": min(100, observed * 20),
        "commercial_gap_score": min(100, as_int(row.get("commercial_gap_count")) * 20 + max(dims or [0]) * 5),
        "reputation_score": min(100, int(rating * 12) + min(review_volume, 200) // 5),
        "social_presence_score": min(100, social_presence * 25),
        "financial_capacity_score": 100 if financial_found else 0,
        "contactability_score": min(100, as_int(row.get("contactability")) * 35),
        "data_quality_score": min(100, found_sources * 20),
        "preliminary_score": preliminary,
        "cost_to_validate_eur": eur(0.0),
    }


def next_best_action(row):
    decision = norm(row.get("decision"))
    coverage = source_coverage(row)
    if not norm(row.get("domain")):
        return "Trovare dominio ufficiale prima di qualunque analisi."
    if decision == "COLLECTION_RESTRICTED":
        return "Riprova acquisizione gratuita e controlla fonte alternativa ufficiale."
    if coverage["google"] != "FOUND":
        return "Completare scheda Google/recensioni prima di spendere."
    if coverage["public_financials"] != "FOUND":
        return "Verificare bilanci pubblici se il target e una societa."
    if decision == "ESCALATE":
        return "Pronto per selezione umana; A1-A9 resta bloccato finche non autorizzato."
    if decision == "SHORTLIST":
        return "Valutare manualmente e completare coverage fonti gratuite."
    return "Non prioritario: conservare come scarto auditabile."


def summarize(rows):
    decisions = Counter(norm(r.get("decision")) or "UNKNOWN" for r in rows)
    verticals = Counter(norm(r.get("vertical")) or "unknown" for r in rows)
    target_segments = Counter(norm(r.get("target_segment")) or "unknown" for r in rows)
    cities = Counter(norm(r.get("city")) or norm(r.get("area")) or "unknown" for r in rows)
    avg_score = round(sum(as_score(r.get("preliminary_score")) for r in rows) / len(rows), 1) if rows else 0
    source_counts = Counter()
    for row in rows:
        for source, state in source_coverage(row).items():
            if state == "FOUND":
                source_counts[source] += 1
    return {
        "total": len(rows),
        "decisions": dict(decisions),
        "verticals": dict(verticals),
        "target_segments": dict(target_segments),
        "cities": dict(cities),
        "avg_preliminary_score": avg_score,
        "source_counts": dict(source_counts),
        "agent_team_status": "AGENT_TEAM_LOCKED",
        "free_operation_cost_eur": eur(0.0),
    }


def ranked_rows(rows):
    rank = {"ESCALATE": 0, "SHORTLIST": 1, "COLLECTION_RESTRICTED": 2, "REJECT": 3}
    return sorted(
        rows,
        key=lambda r: (
            rank.get(norm(r.get("decision")), 9),
            -as_score(r.get("preliminary_score")),
            norm(r.get("company")).lower(),
        ),
    )


def build_dashboard_payload(rows):
    items = []
    for idx, row in enumerate(ranked_rows(rows), 1):
        item = dict(row)
        item["_rank"] = idx
        item["_id"] = row_id(row, idx)
        item["_source_coverage"] = source_coverage(row)
        item["_explainable_scores"] = explainable_scores(row)
        item["_next_best_action"] = next_best_action(row)
        item["_operation_cost_eur"] = eur(0.0)
        items.append(item)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "zero_llm_dashboard",
        "golden_rule": "free_first_never_invent_agent_team_locked",
        "summary": summarize(rows),
        "items": items,
    }


def css_class(value):
    return "state-" + (norm(value).lower().replace("_", "-") or "unknown")


def meter(label, value):
    value = max(0, min(100, int(value)))
    return (
        f'<div class="meter"><div class="meter-top"><span>{escape(label)}</span>'
        f'<strong>{value}</strong></div><div class="bar"><span style="width:{value}%"></span></div></div>'
    )


def render_html(payload):
    summary = payload["summary"]
    items = payload["items"]
    decision_counts = summary["decisions"]
    source_counts = summary["source_counts"]
    rows_html = []
    cards_html = []
    for item in items:
        scores = item["_explainable_scores"]
        coverage = item["_source_coverage"]
        coverage_html = "".join(
            f'<span class="pill {css_class(state)}">{escape(source)}: {escape(state)}</span>'
            for source, state in coverage.items()
        )
        score_html = "".join(
            meter(label.replace("_", " "), value)
            for label, value in scores.items()
            if label.endswith("_score") or label == "preliminary_score"
        )
        company = norm(item.get("company")) or norm(item.get("domain")) or "Prospect"
        decision = norm(item.get("decision")) or "UNKNOWN"
        domain = norm(item.get("domain"))
        domain_html = f'<a href="https://{escape(domain)}" target="_blank" rel="noreferrer">{escape(domain)}</a>' if domain else "NEEDS_OFFICIAL_DOMAIN"
        rows_html.append(
            "<tr>"
            f"<td>{item['_rank']}</td>"
            f"<td>{escape(company)}</td>"
            f"<td>{escape(norm(item.get('vertical')))}</td>"
            f"<td>{escape(norm(item.get('target_segment')))}</td>"
            f"<td>{escape(norm(item.get('city')) or norm(item.get('area')))}</td>"
            f"<td><span class=\"decision {css_class(decision)}\">{escape(decision)}</span></td>"
            f"<td>{escape(norm(item.get('preliminary_score')) or '0')}</td>"
            f"<td>{domain_html}</td>"
            f"<td>{escape(item['_next_best_action'])}</td>"
            "</tr>"
        )
        cards_html.append(
            f'<section class="prospect" id="{escape(item["_id"])}">'
            f'<div class="prospect-head"><h3>{escape(company)}</h3>'
            f'<span class="decision {css_class(decision)}">{escape(decision)}</span></div>'
            f'<div class="meta"><span>{escape(norm(item.get("vertical")) or "unknown")}</span>'
            f'<span>{escape(norm(item.get("target_segment")) or "unknown")}</span>'
            f'<span>{escape(norm(item.get("city")) or norm(item.get("area")) or "unknown")}</span>'
            f'<span>{escape(item["_operation_cost_eur"])}</span></div>'
            f'<div class="contact">{contact_html(item)}</div>'
            f'<div class="coverage">{coverage_html}</div>'
            f'<div class="score-grid">{score_html}</div>'
            f'<p class="next">{escape(item["_next_best_action"])}</p>'
            '</section>'
        )
    decision_html = "".join(
        f'<div class="kpi"><span>{escape(decision)}</span><strong>{decision_counts.get(decision, 0)}</strong></div>'
        for decision in DECISION_ORDER
    )
    source_html = "".join(
        f'<div class="kpi small"><span>{escape(source)}</span><strong>{count}</strong></div>'
        for source, count in sorted(source_counts.items())
    )
    city_options = "".join(f'<option value="{escape(city)}">{escape(city)}</option>' for city in sorted(summary["cities"]))
    vertical_options = "".join(f'<option value="{escape(v)}">{escape(v)}</option>' for v in sorted(summary["verticals"]))
    target_options = "".join(f'<option value="{escape(s)}">{escape(s)}</option>' for s in sorted(summary["target_segments"]))
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RRT Opportunity Dashboard</title>
  <style>
    :root {{
      --ink: #202124;
      --muted: #5f6368;
      --line: #d7dce2;
      --bg: #f7f9fb;
      --panel: #ffffff;
      --accent: #0b6bcb;
      --good: #137333;
      --warn: #b06000;
      --bad: #b3261e;
      --hold: #5f6368;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }}
    header {{ background: #13212f; color: white; padding: 22px 28px; }}
    header h1 {{ margin: 0 0 6px; font-size: 24px; letter-spacing: 0; }}
    header p {{ margin: 0; color: #cbd5df; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 20px 24px 44px; }}
    .toolbar, .band, .prospect {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }}
    .toolbar {{ display: grid; grid-template-columns: repeat(6, minmax(140px, 1fr)); gap: 12px; padding: 14px; margin-bottom: 16px; }}
    label {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 4px; }}
    select, input {{ width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 8px; background: white; color: var(--ink); }}
    .band {{ padding: 16px; margin-bottom: 16px; }}
    .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
    .kpi {{ border-left: 4px solid var(--accent); background: #f8fbff; padding: 10px 12px; min-height: 64px; }}
    .kpi span {{ display: block; color: var(--muted); font-size: 12px; }}
    .kpi strong {{ font-size: 24px; }}
    .kpi.small strong {{ font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ font-size: 12px; color: var(--muted); background: #f3f6f9; position: sticky; top: 0; }}
    tr[hidden], .prospect[hidden] {{ display: none; }}
    .decision, .pill {{ display: inline-block; border-radius: 999px; padding: 3px 8px; font-size: 12px; font-weight: 700; }}
    .state-escalate, .state-found {{ background: #e6f4ea; color: var(--good); }}
    .state-shortlist {{ background: #e8f0fe; color: var(--accent); }}
    .state-collection-restricted, .state-not-checked {{ background: #f1f3f4; color: var(--hold); }}
    .state-reject, .state-conflict {{ background: #fce8e6; color: var(--bad); }}
    .state-stale {{ background: #fef7e0; color: var(--warn); }}
    .prospects {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 12px; }}
    .prospect {{ padding: 14px; }}
    .prospect-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    .prospect h3 {{ margin: 0; font-size: 16px; }}
    .meta, .coverage {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; color: var(--muted); }}
    .contact {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; margin-top: 10px; color: var(--muted); font-size: 12px; }}
    .meta span {{ border: 1px solid var(--line); border-radius: 6px; padding: 3px 7px; background: #fafafa; }}
    .contact span {{ border: 1px solid var(--line); border-radius: 6px; padding: 4px 7px; background: #fff; overflow-wrap: anywhere; }}
    .score-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }}
    .meter-top {{ display: flex; justify-content: space-between; gap: 8px; font-size: 12px; color: var(--muted); }}
    .bar {{ height: 8px; background: #e8edf3; border-radius: 99px; overflow: hidden; margin-top: 3px; }}
    .bar span {{ display: block; height: 100%; background: var(--accent); }}
    .next {{ margin: 12px 0 0; color: var(--ink); }}
    .note {{ color: var(--muted); margin-top: 8px; }}
    .exports a {{ margin-right: 12px; }}
    @media (max-width: 760px) {{
      .toolbar {{ grid-template-columns: 1fr; }}
      .score-grid {{ grid-template-columns: 1fr; }}
      .contact {{ grid-template-columns: 1fr; }}
      table {{ font-size: 12px; }}
      main {{ padding: 12px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>RRT Opportunity Dashboard</h1>
    <p>Free-first, no invented data, agent team locked. Generated {escape(payload["generated_at"])}.</p>
  </header>
  <main>
    <section class="toolbar" aria-label="Filtri">
      <div><label for="filter-decision">Decisione</label><select id="filter-decision"><option value="">Tutte</option>{"".join(f'<option value="{d}">{d}</option>' for d in DECISION_ORDER)}</select></div>
      <div><label for="filter-vertical">Categoria</label><select id="filter-vertical"><option value="">Tutte</option>{vertical_options}</select></div>
      <div><label for="filter-target">Target</label><select id="filter-target"><option value="">Tutti</option>{target_options}</select></div>
      <div><label for="filter-city">Citta</label><select id="filter-city"><option value="">Tutte</option>{city_options}</select></div>
      <div><label for="filter-search">Cerca</label><input id="filter-search" type="search" placeholder="azienda o dominio"></div>
      <div><label>Agent team</label><input value="{escape(summary["agent_team_status"])}" readonly></div>
    </section>

    <section class="band">
      <h2>Opportunity Cockpit</h2>
      <div class="kpis">
        <div class="kpi"><span>Prospect</span><strong>{summary["total"]}</strong></div>
        <div class="kpi"><span>Score medio</span><strong>{summary["avg_preliminary_score"]}</strong></div>
        <div class="kpi"><span>Costo operazioni gratuite</span><strong>{summary["free_operation_cost_eur"]}</strong></div>
        {decision_html}
      </div>
      <p class="note">Google, recensioni, social e bilanci pubblici sono fonti di intelligence. Non sostituiscono il dominio ufficiale e non certificano Opportunity Signal.</p>
    </section>

    <section class="band">
      <h2>Source Coverage Matrix</h2>
      <div class="kpis">{source_html}</div>
    </section>

    <section class="band exports">
      <h2>Export</h2>
      <a href="dashboard_payload.json">JSON standardizzato</a>
      <a href="shortlist.csv">Shortlist CSV</a>
      <a href="prospects.xlsx">XLSX editabile</a>
      <a href="batch_report.md">Report batch Markdown</a>
      <a href="batch_report.docx">DOCX editabile</a>
      <a href="print_report.html">HTML stampa/PDF</a>
      <a href="reports/">Report rapidi</a>
      <a href="guided_reports/">Report guidati</a>
      <a href="full_rrt_locked/">A1-A9 locked</a>
    </section>

    <section class="band">
      <h2>Lista Operativa</h2>
      <table id="prospect-table">
        <thead><tr><th>#</th><th>Azienda</th><th>Categoria</th><th>Target</th><th>Citta</th><th>Decisione</th><th>Score</th><th>Dominio</th><th>Prossima azione</th></tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
      </table>
    </section>

    <section>
      <h2>Report Rapidi</h2>
      <div class="prospects">{''.join(cards_html)}</div>
    </section>
  </main>
  <script>
    const filters = {{
      decision: document.getElementById('filter-decision'),
      vertical: document.getElementById('filter-vertical'),
      target: document.getElementById('filter-target'),
      city: document.getElementById('filter-city'),
      search: document.getElementById('filter-search')
    }};
    const rows = Array.from(document.querySelectorAll('#prospect-table tbody tr'));
    const cards = Array.from(document.querySelectorAll('.prospect'));
    function applyFilters() {{
      const d = filters.decision.value.toLowerCase();
      const v = filters.vertical.value.toLowerCase();
      const t = filters.target.value.toLowerCase();
      const c = filters.city.value.toLowerCase();
      const s = filters.search.value.toLowerCase();
      rows.forEach((row, i) => {{
        const text = row.textContent.toLowerCase();
        const visible = (!d || text.includes(d)) && (!v || text.includes(v)) && (!t || text.includes(t)) && (!c || text.includes(c)) && (!s || text.includes(s));
        row.hidden = !visible;
        if (cards[i]) cards[i].hidden = !visible;
      }});
    }}
    Object.values(filters).forEach(el => el.addEventListener('input', applyFilters));
  </script>
</body>
</html>
"""


def render_batch_report(payload):
    summary = payload["summary"]
    lines = [
        "# RRT Dashboard Batch Report",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Total prospect: {summary['total']}",
        f"- Agent team: {summary['agent_team_status']}",
        f"- Free operation cost: {summary['free_operation_cost_eur']}",
        f"- Average preliminary score: {summary['avg_preliminary_score']}",
        "",
        "## Decisions",
    ]
    for decision in DECISION_ORDER:
        lines.append(f"- {decision}: {summary['decisions'].get(decision, 0)}")
    lines.extend(["", "## Priority List"])
    for item in payload["items"]:
        lines.append(
            f"- {item['_rank']}. {norm(item.get('company')) or norm(item.get('domain'))} "
            f"[{norm(item.get('vertical'))}] {norm(item.get('decision'))} "
            f"score={norm(item.get('preliminary_score')) or '0'} - {item['_next_best_action']}"
        )
    lines.extend([
        "",
        "## Method Note",
        "This is a zero-LLM operational dashboard. It does not certify Opportunity Signals and does not use the agent team.",
    ])
    return "\n".join(lines) + "\n"


def render_single_report(item):
    coverage = item["_source_coverage"]
    scores = item["_explainable_scores"]
    company = norm(item.get("company")) or norm(item.get("domain")) or "Prospect"
    lines = [
        f"# Passaggio 1 - RRT Rapid Report - {company}",
        "",
        "Livello: rapido gratuito, zero-LLM, utile per shortlist iniziale.",
        "",
        f"- Category: {norm(item.get('vertical')) or 'unknown'}",
        f"- Target segment: {norm(item.get('target_segment')) or 'unknown'}",
        f"- City: {norm(item.get('city')) or norm(item.get('area')) or 'unknown'}",
        f"- Decision: {norm(item.get('decision')) or 'UNKNOWN'}",
        f"- Preliminary score: {norm(item.get('preliminary_score')) or '0'}",
        f"- Cost: {item['_operation_cost_eur']}",
        f"- Agent team: AGENT_TEAM_LOCKED",
        "",
        "## Contatti",
    ]
    lines.extend(contact_summary_lines(item))
    lines.extend([
        "",
        "## Source Coverage",
    ])
    for source, state in coverage.items():
        lines.append(f"- {source}: {state}")
    lines.extend(["", "## Explainable Scores"])
    for name, value in scores.items():
        lines.append(f"- {name}: {value}")
    lines.extend([
        "",
        "## Next Best Action",
        item["_next_best_action"],
        "",
        "## Guardrail",
        "Report rapido zero-LLM. Non inventa dati, non certifica Opportunity Signal e non avvia A1-A9.",
    ])
    return "\n".join(lines) + "\n"


def missing_coverage_items(item):
    coverage = item["_source_coverage"]
    return [source for source, state in coverage.items() if state != "FOUND"]


def guided_questions(item):
    vertical = norm(item.get("vertical"))
    target = norm(item.get("target_segment"))
    questions = [
        "Il dominio ufficiale corrisponde alla stessa entita visibile su Google, social e portali review?",
        "Quali recensioni pubbliche confermano o smentiscono i gap osservati dal sito?",
        "Quale prova gratuita manca prima di autorizzare un report costoso?",
    ]
    if vertical == "ristorazione":
        questions.extend([
            f"Il target `{target or 'ristorazione_generic'}` e coerente con menu, recensioni e portali?",
            "TripAdvisor/TheFork/RestaurantGuru mostrano attriti ricorrenti su prenotazione, servizio, prezzo o posizionamento?",
            "Il menu e la proposta sono abbastanza chiari per sostenere il posizionamento dichiarato?",
        ])
    elif vertical == "pmi":
        questions.extend([
            "La ragione sociale e recuperabile da fonti pubbliche senza ambiguita?",
            "Bilanci o documenti pubblici indicano dimensione e continuita coerenti col target PMI?",
        ])
    return questions


def render_guided_report(item):
    company = norm(item.get("company")) or norm(item.get("domain")) or "Prospect"
    scores = item["_explainable_scores"]
    missing = missing_coverage_items(item)
    lines = [
        f"# Passaggio 2 - RRT Guided Opportunity Report - {company}",
        "",
        "Livello: analisi guidata crescente, non-agentica, basata su fonti gratuite e verificabili.",
        "",
        "Status: NON_AGENTIC_GUIDED_REPORT",
        f"Cost: {item['_operation_cost_eur']}",
        "Agent team: AGENT_TEAM_LOCKED",
        "",
        "## Decision Context",
        f"- Category: {norm(item.get('vertical')) or 'unknown'}",
        f"- Target segment: {norm(item.get('target_segment')) or 'unknown'}",
        f"- City: {norm(item.get('city')) or norm(item.get('area')) or 'unknown'}",
        f"- Decision: {norm(item.get('decision')) or 'UNKNOWN'}",
        f"- Preliminary score: {norm(item.get('preliminary_score')) or '0'}",
        "",
        "## Contatti",
    ]
    lines.extend(contact_summary_lines(item))
    lines.extend([
        "",
        "## Opportunity Hypothesis",
        "This is a working hypothesis from free public signals only. It must be confirmed before any commercial claim.",
        f"- Current next action: {item['_next_best_action']}",
        f"- Strongest free signal bucket: {max((k for k in scores if k.endswith('_score')), key=lambda k: scores[k], default='unresolved')}",
        "",
        "## Missing Free Checks",
    ])
    if missing:
        lines.extend(f"- {source}" for source in missing)
    else:
        lines.append("- None from the configured coverage matrix.")
    lines.extend(["", "## Questions Before Spending"])
    lines.extend(f"- {question}" for question in guided_questions(item))
    lines.extend([
        "",
        "## Allowed Next Steps",
        "- Complete missing free coverage manually or through legal public enrichment.",
        "- Export this report for human review.",
        "- Request cost estimate before any A1-A9 run.",
        "",
        "## Guardrail",
        "No Opportunity Signal is certified here. No paid API, document purchase, or agent team run was used.",
    ])
    return "\n".join(lines) + "\n"


def render_full_rrt_locked_report(item):
    company = norm(item.get("company")) or norm(item.get("domain")) or "Prospect"
    lines = [
        f"# Passaggio 3 - RRT Full A1-A9 Report Request - {company}",
        "",
        "Livello: report completo massimo, bloccato finche non autorizzi budget e agent team.",
        "",
        "Status: AGENT_TEAM_LOCKED",
        "Cost estimate: REQUIRED_BEFORE_RUN",
        "Required approval: RRT_AGENT_TEAM_APPROVAL=I_APPROVE_AGENT_TEAM_LIVE_RUN",
        "",
        "## Current Inputs",
        f"- Category: {norm(item.get('vertical')) or 'unknown'}",
        f"- Target segment: {norm(item.get('target_segment')) or 'unknown'}",
        f"- City: {norm(item.get('city')) or norm(item.get('area')) or 'unknown'}",
        f"- Domain: {norm(item.get('domain')) or 'NEEDS_OFFICIAL_DOMAIN'}",
        f"- Decision: {norm(item.get('decision')) or 'UNKNOWN'}",
        "",
        "## Contatti",
    ]
    lines.extend(contact_summary_lines(item))
    lines.extend([
        "",
        "## Required Before Unlock",
        "- Explicit user approval for this entrepreneur or batch.",
        "- EUR budget cap.",
        "- Source coverage review.",
        "- Confirmation that free checks have been maximized.",
        "",
        "## Planned Agent Stages After Approval",
        "- A1 Discovery",
        "- A2 Entity Scope",
        "- A3 Deep Scan",
        "- A4 Evidence Audit",
        "- A5 Target Match",
        "- A6 Benchmark",
        "- A7 Red Team",
        "- A8 Commercial Gate",
        "- A9 QA Orchestrator",
        "",
        "## Guardrail",
        "This file is a locked request template, not an executed A1-A9 report.",
    ])
    return "\n".join(lines) + "\n"


def export_row(item):
    return {
        "rank": item["_rank"],
        "company": norm(item.get("company")) or norm(item.get("domain")),
        "domain": norm(item.get("domain")),
        "city": norm(item.get("city")) or norm(item.get("area")),
        "vertical": norm(item.get("vertical")),
        "target_segment": norm(item.get("target_segment")),
        "decision": norm(item.get("decision")) or "UNKNOWN",
        "phone": contact_value(item, "phone"),
        "mobile_phone": contact_value(item, "mobile_phone"),
        "email": contact_value(item, "email"),
        "address": contact_value(item, "address"),
        "preliminary_score": norm(item.get("preliminary_score")) or "0",
        "fetch_state": norm(item.get("fetch_state")),
        "online_enrichment_state": norm(item.get("online_enrichment_state")),
        "google_state": norm(item.get("google_state")),
        "google_rating": norm(item.get("google_rating")),
        "google_review_count": norm(item.get("google_review_count")),
        "social_presence_count": norm(item.get("social_presence_count")),
        "public_financials_state": norm(item.get("public_financials_state")),
        "next_best_action": item["_next_best_action"],
        "operation_cost_eur": item["_operation_cost_eur"],
    }


def cell_ref(col_idx, row_idx):
    name = ""
    col = col_idx
    while col:
        col, rem = divmod(col - 1, 26)
        name = chr(65 + rem) + name
    return f"{name}{row_idx}"


def sheet_xml(rows):
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    out.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>')
    for row_idx, row in enumerate(rows, 1):
        out.append(f'<row r="{row_idx}">')
        for col_idx, value in enumerate(row, 1):
            ref = cell_ref(col_idx, row_idx)
            out.append(f'<c r="{ref}" t="inlineStr"><is><t>{xml_escape(value)}</t></is></c>')
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def write_xlsx(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    summary_rows = [
        ["Metric", "Value"],
        ["Generated", payload["generated_at"]],
        ["Total prospect", summary["total"]],
        ["Agent team", summary["agent_team_status"]],
        ["Free operation cost", summary["free_operation_cost_eur"]],
        ["Average preliminary score", summary["avg_preliminary_score"]],
    ]
    for decision in DECISION_ORDER:
        summary_rows.append([decision, summary["decisions"].get(decision, 0)])
    data_rows = [EXPORT_COLUMNS]
    data_rows.extend([list(export_row(item).values()) for item in payload["items"]])
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""")
        z.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""")
        z.writestr("xl/workbook.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="Prospects" sheetId="1" r:id="rId1"/>
<sheet name="Summary" sheetId="2" r:id="rId2"/>
</sheets>
</workbook>""")
        z.writestr("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
</Relationships>""")
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml(data_rows))
        z.writestr("xl/worksheets/sheet2.xml", sheet_xml(summary_rows))


def docx_paragraph(text, style=None):
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{style_xml}<w:r><w:t>{xml_escape(text)}</w:t></w:r></w:p>"


def write_docx(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    body = [
        docx_paragraph("RRT Dashboard Batch Report", "Title"),
        docx_paragraph(f"Generated: {payload['generated_at']}"),
        docx_paragraph(f"Total prospect: {summary['total']}"),
        docx_paragraph(f"Agent team: {summary['agent_team_status']}"),
        docx_paragraph(f"Free operation cost: {summary['free_operation_cost_eur']}"),
        docx_paragraph("Decisions", "Heading1"),
    ]
    for decision in DECISION_ORDER:
        body.append(docx_paragraph(f"{decision}: {summary['decisions'].get(decision, 0)}"))
    body.append(docx_paragraph("Priority List", "Heading1"))
    for item in payload["items"]:
        row = export_row(item)
        body.append(docx_paragraph(
            f"{row['rank']}. {row['company']} | {row['vertical']} | {row['target_segment']} | "
            f"{row['decision']} | score {row['preliminary_score']} | {row['next_best_action']}"
        ))
    body.append(docx_paragraph("Method Note", "Heading1"))
    body.append(docx_paragraph("Report zero-LLM editabile. Non inventa dati, non certifica Opportunity Signal e non avvia A1-A9."))
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>{''.join(body)}<w:sectPr/></w:body>
</w:document>"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        z.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        z.writestr("word/document.xml", document)


def render_print_report(payload):
    return render_html(payload).replace(
        "</style>",
        "@media print { header { background: white; color: #202124; border-bottom: 1px solid #d7dce2; } "
        ".toolbar, .exports { display: none; } .band, .prospect { break-inside: avoid; } }</style>",
    )


def build_dashboard(input_csv, output_dir):
    rows = read_csv(input_csv)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    payload = build_dashboard_payload(rows)
    write_json(output / "dashboard_payload.json", payload)
    write_text(output / "index.html", render_html(payload))
    write_text(output / "print_report.html", render_print_report(payload))
    write_text(output / "batch_report.md", render_batch_report(payload))
    write_xlsx(output / "prospects.xlsx", payload)
    write_docx(output / "batch_report.docx", payload)
    shortlist = [row for row in rows if norm(row.get("decision")) in {"SHORTLIST", "ESCALATE"}]
    write_csv(output / "shortlist.csv", shortlist, fieldnames=list(rows[0].keys()) if rows else [])
    reports_dir = output / "reports"
    guided_dir = output / "guided_reports"
    locked_dir = output / "full_rrt_locked"
    reports_dir.mkdir(exist_ok=True)
    guided_dir.mkdir(exist_ok=True)
    locked_dir.mkdir(exist_ok=True)
    for item in payload["items"]:
        if norm(item.get("decision")) in {"SHORTLIST", "ESCALATE"}:
            write_text(reports_dir / f"{item['_id']}.md", render_single_report(item))
            write_text(guided_dir / f"{item['_id']}.md", render_guided_report(item))
            write_text(locked_dir / f"{item['_id']}.md", render_full_rrt_locked_report(item))
    return payload


def main():
    ap = argparse.ArgumentParser(description="Generate a zero-LLM RRT dashboard from a pre-screen CSV")
    ap.add_argument("input_csv")
    ap.add_argument("output_dir")
    args = ap.parse_args()
    payload = build_dashboard(args.input_csv, args.output_dir)
    print(json.dumps({
        "status": "PASS",
        "dashboard": str(Path(args.output_dir) / "index.html"),
        "total": payload["summary"]["total"],
        "agent_team_status": payload["summary"]["agent_team_status"],
        "cost_eur": payload["summary"]["free_operation_cost_eur"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
