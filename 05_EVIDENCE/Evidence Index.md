---
type: evidence-index
status: active
updated: 2026-08-12
---

# Evidence Index

Ogni Evidence Pack deve conservare:
- source_id
- evidence_id
- URL
- observed_at
- channel
- entity_scope
- confidence
- claim
- data_state
- audit_ref

Nessun finding può esistere senza evidence_id valido.

## Evidence Pack attivi
- [[05_EVIDENCE/SAV-DENT-01 - Zecca-Cohen Evidence Pack]] — Savona dental pilot; evidence pack per Signal Google profile -> sito ufficiale -> prima visita.
- [[05_EVIDENCE/B04-34 - Evidence Pack]] — pre-reaudit.
- [[05_EVIDENCE/B04-37 - Evidence Pack]] — audited / pipeline A1→A9 READY.
- [[05_EVIDENCE/B04-48 - Evidence Pack]] — pre-reaudit.

## Gate collegati
- [[09_VALIDATION/Saturation Evidence Re-Audit - Tranche D]]
- [[09_VALIDATION/Scoring Integrity V2]]
- [[09_VALIDATION/Legacy Zero Repair Queue]]

## Regole
- Missing ≠ zero.
- `NOT_FOUND` richiede `NOT_FOUND_AFTER_PROTOCOL`.
- Un Evidence Pack preliminare non autorizza benchmark o Signal.
- Il re-audit può confermare, retrocedere o bloccare; non può aggiungere prove inesistenti.

## Related
- [[04_PROSPECTS/Prospects Index]]
- [[08_RED_TEAM/Red Team Index]]
- [[09_VALIDATION/Validation Dashboard]]
