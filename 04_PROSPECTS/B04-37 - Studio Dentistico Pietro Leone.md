---
type: prospect
id: B04-37
company: Studio Dentistico Dott. Pietro Leone
city: Napoli
official_domain: https://www.studiodentisticoleone.it/
entity_status: RESOLVED
saturation_state: SATURATED
target_match_state: OBSERVED
benchmark_state: PASS
red_team_state: WEAK_SURVIVAL
signal_state: WATCHLIST
qa_state: READY
human_review: pending
updated: 2026-08-12
---

# B04-37 — Studio Dentistico Dott. Pietro Leone

## Stato sintetico
Pipeline completa A1→A9 conclusa con `PASS`. QA finale A9: `READY`.

## Identità
- Studio Dentistico Leone.
- Dott. Pietro Leone.
- Napoli, Viale Antonio Gramsci 18.
- Dominio ufficiale: https://www.studiodentisticoleone.it/

## Evidence Pack
[[05_EVIDENCE/B04-37 - Evidence Pack]]

## Target match
- D1 paura/ansia/sedazione: OBSERVED.
- D2 pagamenti/rate: OBSERVED; nessun importo pubblico specifico osservato.
- D3 implantologia/3D/digitale/team: OBSERVED; garanzia esplicita non osservata.
- D4 carico immediato/stessa giornata: OBSERVED con condizionalità clinica.
- D5 recensioni/testimonianze/esperienza: OBSERVED; garanzia esplicita non osservata.

## Benchmark
A6 ha congelato benchmark comparabili nel verticale implantologia privata italiana. Nessuna inferenza economica o causale.

## Red Team
Esito: `WEAK_SURVIVAL`.
I gap sopravvivono solo come differenze documentali osservate; non sono dimostrate inferiorità commerciali, perdite di lead o ROI.

## Commercial Gate
`WATCHLIST`.
Nessun forcing verso Opportunity Signal Candidate.

## QA
A9: `READY`.
Questo caso è il riferimento positivo per una pipeline end-to-end completa e conservativa.

## Lezione di sistema
Durante la validazione B04-37 sono emersi e corretti:
- execution trace obbligatoria in A3;
- output A5 compattato per evitare truncation;
- isolamento task per `case_id` per evitare contaminazione tra prospect.

## Collegamenti
- [[00_HOME/SECOND_BRAIN]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/B04-37 - Evidence Pack]]
- [[06_BENCHMARKS/Benchmarks Index]]
- [[08_RED_TEAM/Red Team Index]]
- [[07_SIGNALS/Signals Index]]
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Batch 04 National Calibration]]
