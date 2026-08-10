---
type: dashboard
project: RRT Red Team
status: active
updated: 2026-08-10
---

# RRT Red Team — Home

## Navigazione
- [[01_ARCHITECTURE/Architecture Overview]]
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
- Multi-agent architecture: 9 ruoli separati + runtime, SQLite state store e audit log.
- Provider live: adapter predisposto; i worker restano dry-run finché non è configurata una credenziale live.
- Batch 04 Calibration: 50 prospect congelati; Entity Resolution chiusa in stati terminali; Deep Scan in corso per tranche.
- Ultimo avanzamento: Deep Scan Tranche D completata su 4 casi; 3 `SATURATED_MULTI_TARGET`, 1 `PARTIALLY_SATURATED`.
- Candidati al prossimo Saturation Evidence Re-Audit: B04-34 Centro Odontoiatrico Gioia, B04-37 Pietro Leone, B04-48 Savasta & Partners.
- Human review: obbligatorio per ogni Opportunity Signal.

## Ultimi artefatti
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

## Obiettivo validazione
Vedi [[09_VALIDATION/Validation Dashboard]] e `03_RULES/RRT_98_PERCENT_VALIDATION_FRAMEWORK_V1.json`.
