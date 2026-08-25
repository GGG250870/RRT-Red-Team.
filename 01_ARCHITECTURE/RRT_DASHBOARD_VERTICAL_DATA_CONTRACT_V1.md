---
type: dashboard-data-contract
version: v1
status: active
updated: 2026-08-25
---

# RRT Dashboard Vertical Data Contract V1

## Purpose

Define the boundary for the future multi-vertical dashboard.

The dashboard must help the user choose vertical, city, target segment, prospect and report depth. It must show evidence coverage, gate state and cost. It must not convert generic scores or a prospect list into an Opportunity Signal.

## Dashboard Responsibilities

The dashboard may:

- select vertical, city and target segment;
- load the matching vertical profile;
- show profile status: `active`, `draft`, `disabled`;
- show required/allowed source coverage;
- show entity resolution state;
- show gate state;
- show cost and consent state;
- export CSV/XLSX/JSON/MD/DOCX/PDF artifacts;
- generate Passaggio 1 and Passaggio 2 non-agentic reports;
- show Passaggio 3 as locked until explicit approval and budget.

The dashboard must not:

- certify Opportunity Signals;
- treat `ESCALATE`, `SHORTLIST` or high score as a Signal;
- hide missing evidence;
- claim revenue loss, clinical quality, food quality or technical competence;
- scrape prohibited sources;
- submit contact forms or contact businesses.

## Minimum Input Columns

Every dashboard-compatible row should include:

- `company`
- `domain`
- `city`
- `vertical`
- `target_segment`
- `phone`
- `mobile_phone`
- `email`
- `address`
- `source_url`
- `official_domain_state`
- `entity_resolution_state`
- `decision`
- `preliminary_score`
- `signal_gate_state`
- `profile_id`
- `profile_status`
- `operation_cost_eur`

Missing values remain missing. They must not be inferred silently.

## Gate State Values

Allowed values:

- `NOT_EVALUATED`
- `DRAFT_PROFILE`
- `ENTITY_UNRESOLVED`
- `COLLECTION_RESTRICTED`
- `NO_SIGNAL`
- `WATCHLIST`
- `OPPORTUNITY_SIGNAL_CANDIDATE`
- `OPPORTUNITY_SIGNAL`
- `VALIDATED_SIGNAL`

Only `OPPORTUNITY_SIGNAL` and `VALIDATED_SIGNAL` can be treated as product outcomes, and only if linked to evidence, comparator and Red Team artifacts.

## Dashboard Payload Additions

The dashboard payload should expose:

```json
{
  "vertical_profile": {
    "profile_id": "dentale.v1",
    "status": "active",
    "vertical": "dentale",
    "target_segment": "first_visit_path"
  },
  "gate_summary": {
    "not_evaluated": 0,
    "watchlist": 0,
    "opportunity_signal_candidate": 0,
    "opportunity_signal": 0
  },
  "source_requirements": {
    "required": [],
    "allowed": [],
    "missing_required_by_prospect": {}
  }
}
```

This is a contract for the next dashboard phase, not a requirement to build the polished dashboard now.

## Artifact Boundary

Dashboard-generated artifacts are operational:

- seed list;
- pre-screen results;
- source coverage matrix;
- shortlist;
- cost ledger;
- Passaggio 1 report;
- Passaggio 2 guided report;
- Passaggio 3 locked request template.

Signal artifacts remain separate:

- evidence pack;
- Signal dossier;
- Red Team review;
- client mini-audit;
- first-contact script.

## Related

- [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]
- [[01_ARCHITECTURE/RRT_FINAL_DASHBOARD_PRODUCT_SPEC_V1]]
- [[11_DASHBOARD/README]]
