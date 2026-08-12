---
type: validation-note
status: active
version: v2
related_engine: 02_AGENTS/runtime/motore_multi_target_v2.py
---

# Scoring Integrity V2

## Perché esiste
Il QA V2 ha corretto due difetti strutturali del motore multi-target:
- `coverage_ratio` poteva risultare 1.0 anche con dimensioni mancanti;
- uno `0` poteva essere accettato senza prova che il Target-Specific Deep Scan fosse arrivato a `NOT_FOUND_AFTER_PROTOCOL`.

## Regole operative
- Una dimensione mancante mantiene il target `UNRESOLVED`.
- `level = 0` è valido solo con stato `NOT_FOUND_AFTER_PROTOCOL`.
- `COLLECTION_RESTRICTED`, `CONTRADICTORY` e `UNRESOLVED` bloccano lo scoring.
- Dimensioni duplicate o inattese bloccano il QA.

## Test
La regression suite V2 passa **11/11**.

Copertura aggiunta:
- stati `UNRESOLVED`, `COLLECTION_RESTRICTED` e `CONTRADICTORY` bloccano lo score;
- dimensioni inattese bloccano il target;
- `SATURATED_MULTI_TARGET` è bloccato se almeno un target atteso non è terminale;
- il QA rifiuta target bloccati che espongono comunque `normalized_0_100` o `status = PASS`.

## Debito tecnico emerso
L'applicazione del nuovo QA alla matrice storica ha individuato **15 zeri legacy non sufficientemente dimostrati**.

Questi casi sono tracciati in [[09_VALIDATION/Legacy Zero Repair Queue]].

## Knowledge path
[[00_HOME/HOME]] → [[09_VALIDATION/Validation Dashboard]] → [[09_VALIDATION/Batch 04 National Calibration]] → **Scoring Integrity V2** → [[09_VALIDATION/Legacy Zero Repair Queue]]

## Related
- [[03_RULES/Rules Index]]
- [[02_AGENTS/Multi-Agent System]]
- [[09_VALIDATION/Validation Dashboard]]
