---
type: architecture-standard
version: v1.0
status: active
updated: 2026-08-10
---

# RRT Granular Traceability Standard v1

## Scopo
Portare RRT a granularità professionale verificabile senza aumentare rumore, duplicazioni o claim non dimostrati.

Ogni oggetto rilevante deve essere atomico, identificabile, versionabile e ricostruibile a ritroso.

## Catena canonica
PUNTO_ZERO
→ PROBLEM
→ PATTERN
→ BLIND_SPOT
→ EVIDENCE
→ TARGET
→ SATURATION
→ TARGET_MATCH
→ BENCHMARK
→ FINDING
→ RED_TEAM
→ COMMERCIAL_GATE
→ SIGNAL
→ HUMAN_REVIEW
→ VALIDATION

## Identificatori canonici
- Prospect: `PR-<batch>-<nn>`
- Problem: `PBxxxx`
- Pattern: `PTxxxx`
- Blind Spot: `BSxxxx`
- Evidence: `EV-<prospect>-<nnn>`
- Target: `TG-<prospect>-D<n>`
- Benchmark: `BM-<prospect>-D<n>-<nn>`
- Finding: `FD-<prospect>-D<n>-<nn>`
- Red Team: `RT-<finding>-<nn>`
- Commercial Gate: `CG-<finding>-<nn>`
- Signal: `SG-<prospect>-<nn>`
- Human Review: `HR-<signal>-<nn>`
- Validation event: `VA-<signal>-<nn>`

Gli ID non vengono riutilizzati dopo cancellazione o falsificazione.

## Oggetto Prospect
Campi minimi:
- prospect_id
- legal_name
- public_name
- city
- country
- official_domain
- entity_state
- scope_state
- source_of_identity
- observed_at
- batch_id
- owner_or_primary_decision_maker_state
- current_stage
- saturation_state
- signal_state
- human_review_state
- audit_refs

## Oggetto Evidence
Ogni evidence deve essere atomica: una singola osservazione o claim verificabile.

Campi minimi:
- evidence_id
- prospect_id
- source_id
- source_type
- url
- page_title
- observed_at
- collected_at
- collector
- entity_scope
- target_dimension
- evidence_level: `A_OBSERVABLE | B_DEDUCIBLE | C_INTERNAL_ONLY`
- raw_observation
- normalized_claim
- quotation_or_excerpt
- confidence
- data_state
- freshness_state
- content_hash_or_snapshot_ref
- contradiction_refs
- audit_ref

Regola: una pagina può generare più evidence_id, ma ogni evidence_id deve sostenere un solo claim materiale.

## Provenance
Per ogni evidence devono essere separati:
1. `source`: dove si trova il dato.
2. `observation`: cosa è effettivamente visibile.
3. `interpretation`: cosa si deduce.
4. `claim`: cosa può essere detto all'esterno.

Una deduzione non può essere salvata come osservazione.

## Evidence state machine
Stati ammessi:
- `FOUND`
- `UNRESOLVED`
- `NOT_FOUND_AFTER_PROTOCOL`
- `COLLECTION_RESTRICTED`
- `CONTRADICTORY`
- `BLOCKED`
- `STALE`
- `REJECTED_BY_AUDIT`

Mai convertire automaticamente uno stato non risolto in `0`.

## Evidence quality dimensions
Ogni evidence può essere valutata separatamente su:
- entity_fit
- source_authority
- directness
- specificity
- freshness
- reproducibility
- contradiction_risk

Questi valori sono quality metadata, non probabilità statistiche.

## Target object
Ogni target D1-D5 deve avere:
- target_id
- prospect_id
- target_code
- target_definition
- accepted_evidence_ids
- rejected_evidence_ids
- unresolved_questions
- search_trace_ids
- terminal_state
- auditor_state
- auditor_reason

Un target è downstream-eligible solo se terminale e auditabile.

## Search Trace
Ogni Deep Scan deve conservare:
- trace_id
- prospect_id
- target_id
- query_or_navigation_action
- source_domain
- executed_at
- result_state
- discovered_urls
- stop_reason

`NOT_FOUND_AFTER_PROTOCOL` richiede un search trace sufficiente a ricostruire il protocollo eseguito.

## Saturation gate
La saturazione deve essere calcolata per target, non solo per prospect.

Stati:
- `SATURATED`
- `PARTIALLY_SATURATED`
- `UNDERCOVERED`
- `BLOCKED`

`SATURATED_MULTI_TARGET` è ammesso solo quando tutti i target previsti sono terminali e l'Evidence Auditor non ha unresolved materiali.

## Target Match
Separare sempre:
- target dichiarato dal prospect;
- target osservato;
- target inferito;
- target non verificabile.

Ogni target match deve citare gli evidence_id che lo sostengono.

## Benchmark object
Campi minimi:
- benchmark_id
- prospect_id
- target_id
- competitor_entity_id
- competitor_scope
- geographic_fit
- offer_fit
- decision_job_fit
- evidence_coverage
- fit_score_heuristic
- frozen_at
- freeze_reason
- alternative_benchmarks
- audit_state

Il benchmark viene congelato prima di calcolare il gap.

## Finding object
Ogni finding deve avere:
- finding_id
- prospect_id
- target_id
- prospect_evidence_ids
- benchmark_ids
- factual_difference
- interpretation
- commercial_hypothesis
- evidence_level
- consequence_level
- contradictory_evidence_ids
- red_team_state
- wording_state

Mai fondere fatto, interpretazione e conseguenza in una sola frase non tracciata.

## Red Team packet
Ogni finding candidato deve avere un packet separato:
- red_team_id
- finding_id
- attack_hypotheses
- counterevidence_ids
- alternative_explanations
- entity_or_scope_risks
- benchmark_bias_risk
- causal_overclaim_risk
- economic_overclaim_risk
- outcome: `FALSIFIED | SURVIVES_WEAKLY | SURVIVES | REJECTED`
- rationale

## Commercial Gate
Il gate valuta soltanto ciò che ha superato audit e Red Team.

Campi:
- gate_id
- finding_id
- discoverability_level: `L0-L4`
- competitive_pressure_state
- actionable_dimension
- forbidden_claims
- safe_wording
- gate_state
- reviewer

## Signal object
Stati canonici:
- `NO_SIGNAL`
- `WATCHLIST`
- `OPPORTUNITY_SIGNAL_CANDIDATE`
- `OPPORTUNITY_SIGNAL`
- `VALIDATED_SIGNAL`

Ogni promozione richiede la catena di evidence_refs e gate_refs completa.

## Human Review
Campi minimi:
- review_id
- signal_id
- reviewer_identity_or_role
- blind_review: true/false
- reviewed_at
- verdict
- disagreement_reason
- adjudication_state

Una review non può riscrivere silenziosamente gli evidence pack.

## Validation
Ogni metrica del framework 98% deve mantenere:
- numerator
- denominator
- sample definition
- excluded cases
- adjudication method
- confidence interval quando statisticamente appropriato
- version of rules used

## Temporal integrity
Ogni oggetto sensibile al tempo deve contenere:
- observed_at
- collected_at
- last_verified_at
- freshness_policy

Una evidence obsoleta diventa `STALE`; non scompare e non viene riscritta retroattivamente.

## Contradiction ledger
Le contraddizioni non vengono risolte cancellando una delle fonti.

Ogni conflitto conserva:
- contradiction_id
- evidence_ids coinvolti
- tipo conflitto
- discovered_at
- resolution_state
- resolution_reason
- resolver

## Audit trail
Ogni decisione materiale deve registrare:
- event_id
- timestamp
- actor
- object_id
- previous_state
- new_state
- reason
- source_refs
- rule_version

## Obsidian layer
Le note `.md` devono privilegiare leggibilità umana e backlink.

Schema minimo per una nota prospect:
`[[Evidence]] → [[Target]] → [[Benchmark]] → [[Finding]] → [[Red Team]] → [[Signal]] → [[Validation]]`

I JSON macchina restano autoritativi per campi strutturati e ledger; il Markdown è la vista umana sincronizzata.

## Definition of Done per blocco
Un blocco è consolidato e può essere persistito solo se:
1. gli input sono identificati;
2. i dati mancanti hanno stato esplicito;
3. gli evidence_id sono tracciabili;
4. le deduzioni sono separate dai fatti;
5. le contraddizioni sono registrate;
6. il Red Team richiesto è chiuso;
7. l'output ha stato terminale o BLOCKED motivato;
8. il changelog registra ogni modifica metodologica o avanzamento operativo rilevante.

## Related
- [[01_ARCHITECTURE/Integrated Knowledge Model]]
- [[03_RULES/Rules Index]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/Evidence Index]]
- [[06_BENCHMARKS/Benchmarks Index]]
- [[08_RED_TEAM/Red Team Index]]
- [[09_VALIDATION/Validation Dashboard]]
