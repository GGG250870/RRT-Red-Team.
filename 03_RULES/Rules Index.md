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
- AI gratuite esterne solo come assistenza non autoritativa: [[03_RULES/RRT_FREE_AI_ASSISTANCE_POLICY_V1]]

## Scoring Integrity V2
- Una dimensione mancante mantiene il target `UNRESOLVED`.
- `level = 0` è valido solo con `NOT_FOUND_AFTER_PROTOCOL`.
- `COLLECTION_RESTRICTED`, `CONTRADICTORY` e `UNRESOLVED` bloccano lo scoring.
- Il QA deve bloccare dimensioni duplicate o inattese.
- Gli zeri legacy non dimostrati passano in [[09_VALIDATION/Legacy Zero Repair Queue]], non vengono corretti automaticamente.

## Validation targets
- Claim attribution accuracy ≥ 98%
- Entity integrity ≥ 99%
- Saturation gate precision ≥ 98%
- False signal rate ≤ 2%
- Overclaim rate ≤ 1%
- Human/model agreement ≥ 90%

## Related
- [[01_ARCHITECTURE/Architecture Overview]]
- [[01_ARCHITECTURE/Knowledge Graph Flow]]
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Scoring Integrity V2]]
- [[03_RULES/RRT_FREE_AI_ASSISTANCE_POLICY_V1]]
