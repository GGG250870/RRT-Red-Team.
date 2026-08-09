---
type: migration-index
status: active
updated: 2026-08-09
---

# RRT — Migration Index

## Migrato nel vault
### Architettura
- [[01_ARCHITECTURE/Architecture Overview]]

### Multi-Agent
- [[02_AGENTS/Multi-Agent System]]
- `02_AGENTS/RRT_MULTI_AGENT_ROLES_V1.json`
- `02_AGENTS/RRT_MULTI_AGENT_ORCHESTRATION_V1.json`
- `02_AGENTS/runtime/orchestrator.py`
- `02_AGENTS/runtime/state_store.py`
- `02_AGENTS/runtime/llm_provider.py`

### Regole core
- `03_RULES/RRT_98_PERCENT_VALIDATION_FRAMEWORK_V1.json`
- `03_RULES/RRT_EXTERNAL_ONLY_COMMERCIAL_SIGNAL_POLICY_V1.json`
- `03_RULES/RRT_TARGET_SPECIFIC_DEEP_SCAN_SPEC_V1_1.json`

### Case reference
- [[08_RED_TEAM/U03 Oberholtzer Martini - Opportunity Signal Candidate]]

### Validation
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Batch 04 National Calibration]]

## Seconda ondata da migrare
1. Provenance & Audit Engine.
2. Competitor Selection Engine.
3. Target Match Engine.
4. Commercial Relevance Gate.
5. Saturation Evidence Re-Audit + consistency rules.
6. U03 Red-Team / Discoverability / Behavior Proxy / Human Review packet.
7. Batch 03 learning history.
8. Batch 04 machine ledgers e tranche JSON.
9. Marketing Pressure / Ads / AI Visibility modules.
10. PMF validation e business model.

## Regola
I file macchina restano JSON/Python. Le decisioni e i learning vengono affiancati da note Markdown Obsidian con backlink.
