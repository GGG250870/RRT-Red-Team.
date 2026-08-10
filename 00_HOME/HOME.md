---
type: dashboard
project: RRT Red Team
status: active
updated: 2026-08-10
---

# RRT Red Team — Home

## Navigazione
- [[01_ARCHITECTURE/Architecture Overview]]
- [[01_ARCHITECTURE/Integrated Knowledge Model]]
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
- [[10_REPORTS/Reports Index]]
- [[99_CHANGELOG/CHANGELOG]]

## Stato progetto
- Core metodologico: avanzato.
- Knowledge model integrato: il framework operativo persistito è stato unificato con le librerie consolidate di Problem, Pattern, Blind Spot, Question, Evidence e Insight/Revenue Trigger.
- Multi-agent architecture: 9 ruoli separati + orchestratore, SQLite state store, audit log e agent registry.
- Provider OpenAI live: **verificato con chiamata reale PASS** il 2026-08-10.
- Runtime multi-agent orchestrato: **BLOCKED** prima del canary live; `worker.py` è mancante e devono essere aggiunti cost ledger, budget guard e stop conditions dei loop.
- Audit architetturale/economico: `GO_WITH_BLOCKERS`; metodologia PASS, GitHub/Obsidian PASS, profittabilità reale `UNRESOLVED` finché non misurata su unit economics reali.
- Batch 04 Calibration: 50 prospect congelati; Entity Resolution chiusa in stati terminali; Deep Scan in corso per tranche.
- Tranche D: 3 casi passati al Saturation Re-Audit; Target Match e benchmark freeze completati; Commercial Gate resta provvisorio finché Prominence & Discoverability P1-P8 non sono completati.
- Human review: obbligatorio per ogni Opportunity Signal.

## Ultimi artefatti
- [[01_ARCHITECTURE/RRT_ARCHITECTURE_ECONOMIC_SUSTAINABILITY_AUDIT_V1]]
- [[01_ARCHITECTURE/Integrated Knowledge Model]]
- `03_RULES/RRT_PROMINENCE_DISCOVERABILITY_GATE_V1.json`
- `09_VALIDATION/RRT_BATCH_04_DEEP_SCAN_TRANCHE_D_V1.json`
- [[10_REPORTS/RRT_BATCH_04_DEEP_SCAN_TRANCHE_D_REPORT_V1]]

## Caso di riferimento
- [[08_RED_TEAM/U03 Oberholtzer Martini - Opportunity Signal Candidate]] — primo candidate arrivato a L2 Discoverability Proxy e gate umano senza claim economici non dimostrati.

## Principi
1. Nessun dato inventato.
2. Nessun `NOT_FOUND` senza Target-Specific Deep Scan.
3. Identità e scope prima dello scoring.
4. Benchmark congelato prima del Decision Loss.
5. Ogni finding deve sopravvivere a red-team.
6. Opportunity Signal ≠ perdita economica dimostrata.
7. Validated Signal richiede comportamento o dati economici verificabili.
8. `SATURATED_MULTI_TARGET` è vietato con target ancora `UNRESOLVED`.
9. I progressi operativi vengono letti dal ledger persistito, non da riepiloghi conversazionali.
10. Le librerie metodologiche conversazionali possono essere integrate solo se non contraddicono il repository e non introducono claim empirici non verificati.
11. Ogni loop di granularità deve avere stop condition e budget; nessun loop infinito.
12. Cheap-first, escalate-on-uncertainty: modelli più costosi solo quando il valore informativo lo giustifica.

## Obiettivo validazione
Vedi [[09_VALIDATION/Validation Dashboard]] e `03_RULES/RRT_98_PERCENT_VALIDATION_FRAMEWORK_V1.json`.
