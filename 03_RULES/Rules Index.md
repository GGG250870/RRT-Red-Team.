---
type: rules-index
status: active
---

# Rules Index

## Core rules
- Evidence provenance obbligatoria
- Entity integrity prima di ogni scoring
- `NOT_FOUND` solo dopo protocollo target-specifico
- SATURATED_MULTI_TARGET vietato se esiste un target UNRESOLVED
- Benchmark scelto prima del Decision Loss
- Red Team obbligatorio prima di Signal
- Nessuna stima di perdita economica senza evidenza L3/L4
- Human Review obbligatoria per Opportunity Signal

## Validation targets
- Claim attribution accuracy ≥ 98%
- Entity integrity ≥ 99%
- Saturation gate precision ≥ 98%
- False signal rate ≤ 2%
- Overclaim rate ≤ 1%
- Human/model agreement ≥ 90%

## Related
- [[01_ARCHITECTURE/Architecture Overview]]
- [[09_VALIDATION/Validation Dashboard]]
