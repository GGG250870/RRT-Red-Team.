---
type: batch-red-team-review
market: Savona
category: dentale
status: completed
updated: 2026-08-17
---

# Savona Dental Remaining Candidates — Red Team Review

## Purpose

Attack the strongest possible findings from the remaining Savona dental candidates before creating any new client-facing Opportunity Signal.

## Candidate attack set

### Attack A — Studio Vesalici has a first-visit continuity gap

Potential finding:

> Studio Vesalici may have less guided lead capture than comparator paths.

Counter-evidence:

- official site exposes phone, mobile, email, address and `Contattaci`;
- site explains services, team, technology and reasons to choose the practice;
- without fresh Google profile state, the key Zecca-Cohen-style gap cannot be verified.

Verdict: **SURVIVES_WEAKLY as WATCHLIST, not Signal.**

### Attack B — Studio Bianco is a strong Signal because a domain is under construction

Potential finding:

> An under-construction official site creates a discovery-to-first-visit gap.

Counter-evidence:

- entity resolution is not stable;
- public search returns `studio-bianco.it` under construction and another odontoiatria source on a different domain;
- wrong-entity risk is higher than finding strength.

Verdict: **FALSIFIED_FOR_SIGNAL / DEFER_ENTITY.**

### Attack C — Studio Orengo has an entity/contact gap due multiple addresses

Potential finding:

> Multiple address references create a decision gap.

Counter-evidence:

- official site exposes contact details and `Dove siamo`;
- agency source describes mobile-first site with call/WhatsApp micro-CTA;
- address/sede complexity may be legitimate multi-location structure.

Verdict: **REJECTED_AS_SIGNAL; monitor entity hygiene.**

### Attack D — Clear forms/WhatsApp still need improvement

Potential finding:

> Any studio without online booking has a conversion gap.

Counter-evidence:

- the gate does not require booking online;
- phone-first can be intentional;
- Soana Martinengo, Faucci, Bellini, Blasi and Garbasso expose form, WhatsApp, request appointment, or direct contact paths.

Verdict: **REJECTED.**

## Batch verdict

**No additional Opportunity Signal survives.**

The gate is working: it blocks generic digital-improvement observations and allows only specific, externally visible decision gaps.

## Related

- [[10_REPORTS/SAVONA_DENTAL_REMAINING_CANDIDATES_GATE_TRIAGE_2026-08-17]]
- [[07_SIGNALS/SAVONA_DENTAL_NO_ADDITIONAL_SIGNAL_OUTCOME_2026-08-17]]
