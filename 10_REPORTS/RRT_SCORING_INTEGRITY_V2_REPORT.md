# RRT — Scoring Integrity v2

## Correzioni implementate

1. `coverage_ratio` non è più `len(observed)/len(observed)` (sempre 1.0). Ora misura davvero la copertura rispetto alle dimensioni attese del target.
2. Un target incompleto viene `BLOCKED` e non riceve score numerico.
3. Il livello `0` è ammesso solo con `data_state = NOT_FOUND_AFTER_PROTOCOL`.
4. Stati `COLLECTION_RESTRICTED`, `INSUFFICIENT`, `CONTRADICTORY`, `ENTITY_AMBIGUOUS`, `UNRESOLVED` bloccano lo scoring.
5. Dimensioni duplicate o inattese bloccano il target.
6. Il QA usa `target_master_v1.json` come fonte delle 5 dimensioni attese per D1-D5.
7. `SATURATED_MULTI_TARGET` è ammesso solo con tutti i target attesi in stato terminale.
8. Il QA rifiuta target bloccati che espongono comunque `status = PASS` o uno score numerico.

## Regression test

Suite `SCORING_INTEGRITY_V2`: **11/11 PASS**.

## Audit legacy

Applicando il nuovo QA alla matrice `matrice_5x5_compilata_v1_1.json` emergono **15 zeri legacy** che non hanno ancora prova `NOT_FOUND_AFTER_PROTOCOL`.

Questi record non vengono corretti automaticamente. Sono stati inseriti in una repair queue e richiedono un nuovo target-specific absence protocol.

## Implicazione

I precedenti score che dipendono da quegli zeri devono essere considerati **non release-safe** finché la repair queue non è chiusa.

## Collegamenti
- [[09_VALIDATION/RRT_LEGACY_ZERO_REPAIR_QUEUE_V2]]
- [[02_AGENTS/Multi-Agent System]]
- [[09_VALIDATION/Validation Dashboard]]
