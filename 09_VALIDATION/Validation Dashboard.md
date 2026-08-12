---
type: validation-dashboard
status: active
---

# Validation Dashboard

## Obiettivo 98%
- Claim attribution accuracy ≥ 98%
- Entity integrity ≥ 99%
- Saturation gate precision ≥ 98%
- False signal rate ≤ 2%
- Overclaim rate ≤ 1%
- Human/model agreement ≥ 90%

## Fasi
- Pilot: 10 casi
- Calibration: 50 casi
- Validation: 100 casi
- Robustness: 250 casi

## Batch corrente
- [[09_VALIDATION/Batch 04 National Calibration]]
- 50 prospect congelati
- Entity resolution chiusa in stati terminali
- Deep Scan in corso per tranche

## Integrità scoring
- [[09_VALIDATION/Scoring Integrity V2]] — QA del motore multi-target e regression suite 11/11.
- [[09_VALIDATION/Legacy Zero Repair Queue]] — 15 zeri legacy da ri-validare con protocollo di assenza.

## Human review
Tutti gli Opportunity Signal richiedono blind review indipendente.
I NO_SIGNAL vengono campionati come negative controls.

## Navigazione
- [[01_ARCHITECTURE/Knowledge Graph Flow]]
- [[03_RULES/Rules Index]]
- [[07_SIGNALS/Signals Index]]
