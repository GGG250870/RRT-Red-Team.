---
type: dashboard
project: RRT Red Team
status: active
updated: 2026-08-12
---

# RRT Red Team — Home

## Navigazione
- [[00_HOME/SECOND_BRAIN]]
- [[01_ARCHITECTURE/Architecture Overview]]
- [[01_ARCHITECTURE/Integrated Knowledge Model]]
- [[01_ARCHITECTURE/Knowledge Graph Flow]]
- [[01_ARCHITECTURE/RRT_ARCHITECTURE_ECONOMIC_SUSTAINABILITY_AUDIT_V1]]
- [[02_AGENTS/Multi-Agent System]]
- [[03_RULES/Rules Index]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/Evidence Index]]
- [[06_BENCHMARKS/Benchmarks Index]]
- [[07_SIGNALS/Signals Index]]
- [[08_RED_TEAM/Red Team Index]]
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Batch 04 National Calibration]]
- [[09_VALIDATION/Scoring Integrity V2]]
- [[09_VALIDATION/Legacy Zero Repair Queue]]
- [[10_REPORTS/Reports Index]]
- [[99_CHANGELOG/CHANGELOG]]

## Stato progetto
- Runtime A1→A9: **VALIDATO** su B04-37 con A9 `READY`.
- Runner end-to-end: `rrt_e2e.sh` + `02_AGENTS/runtime/end_to_end_runner.py` presenti in `main`.
- Auto-repair: **VALIDATO**. Se A4 blocca con `COLLECTION_RESTRICTED`, il runner esegue una sola volta A3 repair e A4/A5 re-audit.
- Isolation guard: i worker reclamano task per `case_id`; eliminata contaminazione tra prospect.
- Caso B04-37: pipeline completa PASS; A8 `WATCHLIST`; A9 `READY`.
- Caso ICO-01: auto-repair eseguito correttamente; esito finale `COLLECTION_RESTRICTED` su D1-D5 per insufficiente acquisizione ufficiale. Questo è uno stato valido, non un errore tecnico.
- Scoring Integrity V2: regression suite 11/11 PASS; individuati 15 zeri legacy da ri-validare.
- Human review: obbligatorio per ogni Opportunity Signal.
- GitHub: fonte persistente e auditabile.
- Obsidian: interfaccia umana del second brain e knowledge graph.

## Knowledge flow
PUNTO ZERO / PROBLEMA PERCEPITO → PATTERN → BLIND SPOT → EVIDENCE → TARGET → SATURATION → TARGET MATCH → BENCHMARK → FINDING → RED TEAM → COMMERCIAL GATE → SIGNAL → HUMAN REVIEW → VALIDATION.

Vedi [[01_ARCHITECTURE/Knowledge Graph Flow]] per la mappa navigabile.

## Regole chiave
1. Nessun dato inventato.
2. Nessun `NOT_FOUND` senza Target-Specific Deep Scan.
3. Identità e scope prima dello scoring.
4. A4 audita prima di A5.
5. Benchmark congelato prima del gap.
6. Red Team può falsificare il finding.
7. Opportunity Signal ≠ perdita economica dimostrata.
8. Missing ≠ zero.
9. `COLLECTION_RESTRICTED` è uno stato valido e non va forzato.
10. Ogni loop ha stop condition e budget.
11. Cheap-first, escalate-on-uncertainty.
12. Ogni finding deve mantenere la catena prospect → evidence → target → benchmark → red-team → commercial gate → validation.
13. `level = 0` è valido solo con `NOT_FOUND_AFTER_PROTOCOL`.

## Casi runtime di riferimento
- [[04_PROSPECTS/B04-37 - Studio Dentistico Pietro Leone]]
- [[04_PROSPECTS/ICO-01 - ICO Dental]]

## Obiettivo operativo
Usare [[00_HOME/SECOND_BRAIN]] come pannello quotidiano. Le note prospect diventano l'unità principale di navigazione umana; il runtime continua a vivere in `02_AGENTS/runtime/` senza dipendere da Obsidian.
