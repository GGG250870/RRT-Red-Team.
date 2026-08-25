---
type: pilot-triage-report
market: Savona
category: pmi
target_segment: climatizzazione_impianti
gate: RRT_PMI_CLIMATIZZAZIONE_SAVONA_LEAD_TRUST_GATE_V1
status: completed
updated: 2026-08-18
cost_eur: 0.0000
---

# Savona PMI Climatizzazione - Gate Triage

## Scope

Prima passata operativa su PMI e imprese tecniche di climatizzazione a Savona/provincia.

Input creato:

- `00_PRE_SCREEN/savona_pmi_climatizzazione_seed_2026-08-18.csv`

Output generati:

- `00_PRE_SCREEN/savona_pmi_climatizzazione_results_2026-08-18.csv`
- `11_DASHBOARD/out/savona_pmi_climatizzazione_2026-08-18/index.html`
- `11_DASHBOARD/out/savona_pmi_climatizzazione_2026-08-18/shortlist.csv`
- `11_DASHBOARD/out/savona_pmi_climatizzazione_2026-08-18/prospects.xlsx`
- `11_DASHBOARD/out/savona_pmi_climatizzazione_2026-08-18/batch_report.docx`

## Executive outcome

No full Opportunity Signal is certified in this first pass.

Operational outcome:

- 6 public entities seeded;
- 5 `ESCALATE` for human selection;
- 1 `COLLECTION_RESTRICTED` due local fetch `HTTP_403`, not due weak public evidence;
- 2 watchlist prospect notes created;
- cost: `EUR 0.0000`;
- agent team: `AGENT_TEAM_LOCKED`.

This is the right first result: climatizzazione shows many commercially rich candidates, but a Signal requires Google/review/company layer and comparator evidence before client-facing claims.

## Triage matrix

| Candidate | City | Public path evidence | Pre-screen | Gate result | Reason |
|---|---|---|---:|---|---|
| RB Clima Srl | Savona / Toirano | Official site shows Savona/Toirano locations, phone, mobile, email, review link, service-select quote form, P.IVA and societa trasparente note. | COLLECTION_RESTRICTED local fetch | BENCHMARK_REFERENCE | Strong lead path; local fetch restriction is technical, not business evidence. Useful comparator. |
| LD Tecnoimpianti Snc | Savona | Official site shows preventivo/sopralluogo, WhatsApp, two mobile numbers, email, address, services and partners. | ESCALATE 95 | NO_SIGNAL / BENCHMARK_LIGHT | Strong contact path; no specific gap survives yet. |
| Pernorio Termotecnica Srl | Savona | Official site targets aziende/PA, ISO, FGAS, SOA, MEPA, realizzazioni, phone/email/address. | ESCALATE 74 | WATCHLIST | Strong trust proof; possible B2B request-path finding needs comparator and Google/review/company checks. |
| Gigatech Impianti | Vado Ligure | Official page shows central heating systems, climatizzazione, assistance, ISO, Riello/Hoval, 24h support, phone/email/address/P.IVA. | ESCALATE 76 | WATCHLIST | Possible gap: high-value assistance/third-responsible offer may not have a guided lead path. Needs falsification. |
| Climatica Albenga | Albenga | Official page shows condizionamento, pompe di calore, VMC, form, mobile numbers, email, P.IVA. | ESCALATE 95 | NO_SIGNAL / PROVINCIAL_REFERENCE | Strong request form and contact path; good provincial comparator. |
| Fratelli Zanti Srl | Cairo Montenotte | Official page shows WhatsApp, phone, email, address, P.IVA, condizionamento/pompe di calore content. | ESCALATE 74 | NO_SIGNAL / PROVINCIAL_REFERENCE | Good contactability and service content; no specific gap yet. |

## Strongest watchlist cases

### 1. Gigatech Impianti

Potential angle:

> route from technical trust and 24h maintenance/assistance promise to a guided lead request.

Why considered:

- high-value B2B/condominium/centralized systems context;
- ISO and authorized assistance signals;
- 24h assistance statement;
- clear phone/email but no structured route observed in the public page.

Why not promoted:

- phone-first workflow may be intentional;
- no Google/review evidence recorded yet;
- no screenshoted mobile path;
- no comparator proof that the missing structured route is decision-relevant.

### 2. Pernorio Termotecnica

Potential angle:

> strong procurement proof exists, but the B2B/PA decision route may be less structured than the credibility material.

Why considered:

- aziende/PA positioning;
- certifications and public-sector procurement signals;
- realizzazioni with named public/enterprise contexts.

Why not promoted:

- site already exposes contact and information request path;
- generic "professional email/domain" critique would be too weak;
- no verified review/company layer yet;
- no behavioral or economic evidence.

## Source notes

Public sources checked on 2026-08-18:

- RB Clima: https://rbclima.com/
- LD Tecnoimpianti: https://www.ldtecnoimpianti.it/
- Pernorio Termotecnica: https://www.pernorioriscaldamento.it/
- Gigatech Impianti: https://www.gigatechimpanti.it/gigatech-impianti
- Climatica Albenga: https://www.climaticaalbenga.com/Impianti-condizionamento
- Fratelli Zanti: https://zanti.it/impianti-di-condizionamento/

## Next required checks before Signal

For each watchlist case:

1. manually verify Google profile, rating, review count and site link;
2. check review portals/directory pages without scraping massivo;
3. open Registro Imprese search link and record only free/publicly visible facts;
4. capture mobile path screenshots for homepage, contact/preventivo/assistenza;
5. compare against RB Clima, Climatica and LD as lead-path references;
6. run Red Team before any mini-audit or first-contact script.

## Related

- [[03_RULES/RRT_PMI_CLIMATIZZAZIONE_SAVONA_LEAD_TRUST_GATE_V1]]
- [[04_PROSPECTS/SAV-PMI-CLIMA-01 - Gigatech Impianti]]
- [[04_PROSPECTS/SAV-PMI-CLIMA-02 - Pernorio Termotecnica]]
- [[08_RED_TEAM/SAVONA_PMI_CLIMATIZZAZIONE_RED_TEAM_REVIEW_2026-08-18]]
- [[07_SIGNALS/SAVONA_PMI_CLIMATIZZAZIONE_SIGNAL_OUTCOME_2026-08-18]]
