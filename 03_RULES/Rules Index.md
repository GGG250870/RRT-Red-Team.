---
type: rules-index
status: active
---

# Rules Index

## Core rules
- Product North Star obbligatoria: ogni sviluppo deve aumentare la probabilita di produrre Opportunity Signal forti, non ovvi, falsificati e auditabili. Vedi [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
- Evidence provenance obbligatoria
- Entity integrity prima di ogni scoring
- `NOT_FOUND` solo dopo protocollo target-specifico
- SATURATED_MULTI_TARGET vietato se esiste un target UNRESOLVED
- Benchmark scelto prima del Decision Loss
- Red Team obbligatorio prima di Signal
- Nessuna stima di perdita economica senza evidenza L3/L4
- Human Review obbligatoria per Opportunity Signal
- AI gratuite esterne solo come assistenza non autoritativa: [[03_RULES/RRT_FREE_AI_ASSISTANCE_POLICY_V1]]
- Vertical profile obbligatorio prima di dichiarare operativo un nuovo verticale: [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]
- Gate dentale Savona discovery-to-first-visit riusabile: [[03_RULES/RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1]]
- Gate PMI climatizzazione Savona lead-trust riusabile: [[03_RULES/RRT_PMI_CLIMATIZZAZIONE_SAVONA_LEAD_TRUST_GATE_V1]]
- Dashboard, scoring e runtime sono infrastruttura: non vanno confusi con il prodotto vendibile se non portano a Signal commercialmente potenti.

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
- Product relevance: ogni Opportunity Signal deve dimostrare perche puo influenzare una decisione del cliente, non solo migliorare igiene SEO o completezza informativa.
- Surprise threshold: un report vendibile deve contenere almeno un finding che l'imprenditore probabilmente non stava gia considerando.
- Profile readiness: un verticale `draft` puo produrre solo pianificazione/template, non mini-audit cliente o Signal.

## Related
- [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
- [[01_ARCHITECTURE/Architecture Overview]]
- [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]
- [[01_ARCHITECTURE/RRT_DASHBOARD_VERTICAL_DATA_CONTRACT_V1]]
- [[01_ARCHITECTURE/Knowledge Graph Flow]]
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Scoring Integrity V2]]
- [[03_RULES/RRT_FREE_AI_ASSISTANCE_POLICY_V1]]
- [[03_RULES/RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1]]
- [[03_RULES/RRT_PMI_CLIMATIZZAZIONE_SAVONA_LEAD_TRUST_GATE_V1]]
