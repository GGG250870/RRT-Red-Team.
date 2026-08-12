---
type: calibration-batch
batch: 04
sample_size: 50
status: deep-scan-in-progress
selection: unbiased-neutral
updated: 2026-08-12
---

# Batch 04 — National Calibration

## Disegno
- 50 prospect nazionali.
- Selezione congelata prima del Deep Scan.
- Query di selezione neutrali `dentista + città`.
- Vietata la sostituzione post-freeze per qualità sito o risultato scomodo.

## Entity Resolution — stato terminale
- **47/50** `VERIFIED_OFFICIAL_DOMAIN`
- **1/50** `VERIFIED_ENTITY_NO_OFFICIAL_DOMAIN`
- **2/50** `IDENTITY_UNRESOLVED`
- **0 pending**

Solo `VERIFIED_OFFICIAL_DOMAIN` può entrare nel Deep Scan ufficiale.

## Deep Scan
Il lavoro procede per tranche. Ogni target deve chiudere in uno stato terminale e nessun `UNRESOLVED` viene trasformato automaticamente in zero.

### Regola introdotta dal re-audit
`SATURATED_MULTI_TARGET` è vietato quando esiste anche un solo target ancora `UNRESOLVED`.

### Tranche B — learning
Frustagli e Antonio Scala erano stati inizialmente marcati saturated ma sono stati retrocessi dal re-audit perché D2 prezzi/finanziamenti non era dimostrato. Questo caso ha generato la [[03_RULES/Rules Index|regola di coerenza Saturation]].

### Tranche C
- Perugia Dent: partial, forte su D2/D3/D4/D5; D1 irrisolto.
- Gervasi Pedroni: partial.
- Gennaro Salvatore: partial.
- diversi casi undercovered nel pass corrente.

### Tranche D
- [[04_PROSPECTS/B04-34 - Centro Odontoiatrico Gioia]] — re-audit PASS; benchmark freeze parziale; `NO_SIGNAL_PROVISIONAL`.
- [[04_PROSPECTS/B04-37 - Studio Dentistico Pietro Leone]] — caso di riferimento end-to-end, A9 `READY`, `WATCHLIST`.
- [[04_PROSPECTS/B04-48 - Savasta & Partners]] — re-audit PASS; benchmark freeze parziale; `NO_SIGNAL_PROVISIONAL`.

Evidence Pack:
- [[05_EVIDENCE/B04-34 - Evidence Pack]]
- [[05_EVIDENCE/B04-37 - Evidence Pack]]
- [[05_EVIDENCE/B04-48 - Evidence Pack]]

Gate dedicato: [[09_VALIDATION/Saturation Evidence Re-Audit - Tranche D]] — PASS 3/3.

Nota conservativa: il Red Team/Commercial Gate Tranche D registra `NO_SIGNAL_PROVISIONAL` per B04-34 e B04-48 finché P1-P8 non è completato. Nessun caso Tranche D viene forzato verso Opportunity Signal.

## Scoring Integrity V2
Il nuovo QA è documentato in [[09_VALIDATION/Scoring Integrity V2]].
L'applicazione retrospettiva ha aperto [[09_VALIDATION/Legacy Zero Repair Queue]] con 15 zeri legacy da ri-validare.

## Integrità
Un conteggio conversazionale precedente sullo stato Entity Resolution non coincideva con il ledger persistito. È stato corretto: da allora i progressi vengono calcolati esclusivamente dal ledger autorevole.

## Obiettivo del batch
Stimare error modes e calibrare i gate prima del campione Validation da 100 prospect.

## Related
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Saturation Evidence Re-Audit - Tranche D]]
- [[09_VALIDATION/Scoring Integrity V2]]
- [[09_VALIDATION/Legacy Zero Repair Queue]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/Evidence Index]]
- [[03_RULES/Rules Index]]
- [[02_AGENTS/Multi-Agent System]]
- [[01_ARCHITECTURE/Knowledge Graph Flow]]
