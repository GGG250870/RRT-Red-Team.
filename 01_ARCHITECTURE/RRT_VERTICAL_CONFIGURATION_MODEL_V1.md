---
type: architecture-decision-record
version: v1
status: accepted
updated: 2026-08-25
---

# RRT Vertical Configuration Model V1

## Context

RRT started from the dental pilot, but dental is not the product boundary.

The product is a vertical-adaptable external commercial Red Team. The core method must stay common while each vertical defines its own customer path, evidence sources, comparator logic and safe client language.

## Decision

Introduce explicit vertical profiles under:

- `03_RULES/vertical_profiles/vertical_profile_schema_v1.json`
- `03_RULES/vertical_profiles/dentale.v1.json`
- `03_RULES/vertical_profiles/ristorazione.blank.v1.json`

The profiles are configuration/contract artifacts first. They do not replace the existing pre-screen code yet. They define what must be true before a vertical can generate serious RRT artifacts.

## Current Architecture Inventory

### Core/Common

These are product-level and vertical-agnostic:

- Product North Star: [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
- Entity resolution before scoring.
- Evidence provenance and source states.
- Cheap-first pre-screen.
- Human selection before expensive work.
- Comparator selection before decision-gap claims.
- Red Team falsification before Signal promotion.
- Signal state machine: `NO_SIGNAL`, `WATCHLIST`, `OPPORTUNITY_SIGNAL_CANDIDATE`, `OPPORTUNITY_SIGNAL`, `VALIDATED_SIGNAL`.
- Cost ledger and consent boundary.
- Dashboard as control surface, not product output.

### Vertical-Specific

These must come from a vertical profile:

- Target segments.
- Required and allowed public sources.
- Entity/identity rules.
- Observable customer-path signals.
- Comparator fit rules.
- Red Team falsification prompts.
- Client-facing language constraints.
- Contact-script framing.
- Signal promotion rules.

### Dental-Specific Today

Dental-specific behavior currently exists in:

- `00_PRE_SCREEN/pre_screen.py` category profile `dentale`.
- `00_PRE_SCREEN/build_batch.py` discovery/source settings for `dentale`.
- [[03_RULES/RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1]]
- Zecca-Cohen artifacts under prospects, evidence, Signal, Red Team and reports.

This is now referenced by `03_RULES/vertical_profiles/dentale.v1.json`.

## Vertical Profile Contract

Every profile must define:

- `profile_id`
- `status`: `active`, `draft` or `disabled`
- `vertical`
- `target_segments`
- `source_policy`
- `entity_identity_rules`
- `observable_customer_path_signals`
- `comparator_rules`
- `red_team_falsification_prompts`
- `client_language_constraints`
- `contact_script_framing`
- `signal_promotion_rules`
- `dashboard_contract`

Validation is performed by:

```bash
python3 03_RULES/validate_vertical_profiles.py
```

## Status Semantics

`active`:
Can support operational pilots when an active gate/checklist is linked.

`draft`:
Can support design and dashboard planning only. It cannot certify a Signal or generate client-facing claims.

`disabled`:
Must not be selectable for operational work.

## Options Considered

### Option A: Keep vertical logic implicit in scripts

Pros:

- No new files.
- Fast for prototypes.

Cons:

- Dental assumptions leak into other verticals.
- Dashboard cannot explain why one vertical is ready and another is draft.
- Client language and Red Team prompts become inconsistent.

### Option B: Full plugin/runtime abstraction now

Pros:

- Cleaner long-term architecture.
- Strong runtime separation.

Cons:

- Too much refactor before the product shape is proven.
- Higher risk of breaking current pilots.

### Option C: Minimal profile contract now

Pros:

- Makes the product multi-vertical explicitly.
- Keeps existing flows working.
- Lets a second vertical be designed without fake evidence.
- Gives dashboard a stable boundary.

Cons:

- Pre-screen still contains duplicated category dictionaries.
- Runtime adapter loading remains a later refactor.

## Decision Outcome

Adopt Option C.

## Consequences

- Dental is now an active vertical profile, not the whole product.
- Ristorazione has a blank draft adapter/template, not a live pilot.
- Dashboard work must consume gate/profile state and must not present lists or scores as Signals.
- Future verticals can be added by profile first, then gate, then pilot.

## Next Implementation Step

Move pre-screen dictionaries gradually behind the profile contract only after two or more active profiles prove the required fields are stable.

## Related

- [[01_ARCHITECTURE/RRT_DASHBOARD_VERTICAL_DATA_CONTRACT_V1]]
- [[03_RULES/Rules Index]]
- [[03_RULES/RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1]]
- [[03_RULES/RRT_PMI_CLIMATIZZAZIONE_SAVONA_LEAD_TRUST_GATE_V1]]
