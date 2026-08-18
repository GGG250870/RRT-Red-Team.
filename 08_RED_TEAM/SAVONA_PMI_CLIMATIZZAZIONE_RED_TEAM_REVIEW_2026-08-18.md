---
type: batch-red-team-review
market: Savona
category: pmi
target_segment: climatizzazione_impianti
status: completed
updated: 2026-08-18
---

# Savona PMI Climatizzazione - Red Team Review

## Purpose

Attack the strongest possible findings before creating client-facing claims.

## Attack A - Any ESCALATE is a Signal

Potential finding:

> Five companies scored `ESCALATE`, therefore there are multiple Opportunity Signals.

Counter-evidence:

- pre-screen is only a cheap operational filter;
- high score can mean good public communication, not a gap;
- RB Clima, LD, Climatica and Zanti already expose direct contact/request paths;
- Google/review/company evidence is incomplete.

Verdict: **REJECTED.**

## Attack B - Gigatech has a lead-path gap

Potential finding:

> Gigatech communicates high-value assistance and certified maintenance but does not expose a structured request path.

Counter-evidence:

- phone and email are visible;
- for urgent technical support, phone-first may be the correct workflow;
- the public page explicitly invites contact/preventivo;
- no comparator screenshot proves decision friction yet.

Verdict: **SURVIVES_WEAKLY as WATCHLIST, not Signal.**

## Attack C - Pernorio has a B2B/procurement trust gap

Potential finding:

> Pernorio has strong PA/B2B proof but a less structured route from proof to qualified request.

Counter-evidence:

- the site has contact details and `Richiedi informazioni`;
- certifications, realizzazioni and procurement signals are already visible;
- email domain choice is not a decision gap by itself;
- B2B buyers may prefer direct phone/email.

Verdict: **SURVIVES_WEAKLY as WATCHLIST, not Signal.**

## Attack D - RB Clima is weak because local fetch returned HTTP_403

Potential finding:

> RB Clima should be downgraded because the local scanner could not fetch it.

Counter-evidence:

- public browser evidence shows a strong website, contacts, review link and quote form;
- `HTTP_403` is a collection limitation;
- collection limitation is not business weakness.

Verdict: **FALSIFIED. RB Clima is benchmark/reference.**

## Batch verdict

No certified Opportunity Signal yet.

The next phase should focus on one of:

- Gigatech: assistance/third-responsible guided lead path;
- Pernorio: B2B/PA trust-to-request path.

Promotion requires fresh Google/review/company checks and comparator screenshots.

## Related

- [[10_REPORTS/SAVONA_PMI_CLIMATIZZAZIONE_GATE_TRIAGE_2026-08-18]]
- [[07_SIGNALS/SAVONA_PMI_CLIMATIZZAZIONE_SIGNAL_OUTCOME_2026-08-18]]
