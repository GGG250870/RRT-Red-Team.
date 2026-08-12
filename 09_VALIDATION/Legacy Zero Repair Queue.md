---
type: repair-queue
status: active
version: v2
machine_file: 09_VALIDATION/RRT_LEGACY_ZERO_REPAIR_QUEUE_V2.json
---

# Legacy Zero Repair Queue

## Stato
Il QA [[09_VALIDATION/Scoring Integrity V2]] ha individuato **15 zeri legacy** che non hanno ancora una prova sufficiente di `NOT_FOUND_AFTER_PROTOCOL`.

## Regola
Nessun valore viene corretto automaticamente.
Ogni caso deve rifare il protocollo Target-Specific Deep Scan sulla dimensione interessata.

## Esiti ammessi
- `FOUND`
- `NOT_FOUND_AFTER_PROTOCOL`
- `COLLECTION_RESTRICTED`
- `CONTRADICTORY`
- `UNRESOLVED`

Solo `FOUND` o `NOT_FOUND_AFTER_PROTOCOL` permettono di chiudere la dimensione ai fini dello scoring.

## Workflow
Repair Queue → [[05_EVIDENCE/Evidence Index]] → Target-Specific Deep Scan → Evidence Audit → Scoring Integrity V2 → Batch/Prospect.

## Obiettivo
Eliminare dal dataset storico gli zeri che derivavano da copertura incompleta anziché da assenza verificata.

## Related
- [[09_VALIDATION/Scoring Integrity V2]]
- [[09_VALIDATION/Batch 04 National Calibration]]
- [[03_RULES/Rules Index]]
