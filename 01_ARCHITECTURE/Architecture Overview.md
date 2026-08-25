---
type: architecture
version: v3.2+
status: active
---

# Architecture Overview

## Product North Star

RRT is an external commercial Red Team for a company.

Its product outcome is not a scraper output, an SEO audit, or a generic marketing report. Its product outcome is 3-7 strong Opportunity Signals that make an entrepreneur think: how did they see this from the outside?

Every architecture decision must be evaluated against [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]].

## Pipeline
INPUT → GENERAL EVIDENCE → TARGET DISCOVERY → PROSPECT EVIDENCE SATURATION → TARGET MATCH → COMPETITOR FIT → BUYER SCORING → DECISION LOSS → COMMERCIAL RELEVANCE GATE → AUDIT → SIGNAL → HUMAN GATE

## Product Pipeline
COMPANY / PROSPECT LIST → ENTITY RESOLUTION → PUBLIC MARKET VIEW → TARGET-SPECIFIC EVIDENCE → COMPARABLE BENCHMARK → DECISION GAP → RED TEAM FALSIFICATION → OPPORTUNITY SIGNAL → HUMAN REVIEW → COMMERCIAL ENTRY POINT

## Core vs Vertical

RRT core is vertical-agnostic: entity resolution, evidence provenance, source states, comparator requirement, Red Team falsification, Signal state machine, cost/consent and human review.

Vertical-specific behavior must be declared in a vertical profile before it becomes operational: target segments, source policy, identity rules, observable customer path, comparator rules, falsification prompts, client language constraints and contact-script framing.

See [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]].

## Agent Boundary

Integrated agents can perform bounded discovery, entity resolution, comparator research, Red Team challenge and dossier/report preparation across verticals.

They cannot contact businesses, submit forms, bypass access controls, invent evidence, certify `OPPORTUNITY_SIGNAL`, approve outreach for use or bypass cost/consent controls. A9 can only produce `READY_FOR_HUMAN_REVIEW` or `BLOCKED`.

See [[02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1]].

## Validation layers
- Entity Resolution
- Scope Resolution
- Primary Intelligence Review: sito ufficiale, Google Business/Profile Reviews/Maps, portali recensioni, social e bilanci pubblici
- Target-Specific Deep Scan
- Saturation Evidence Re-Audit
- Target Match
- Benchmark Selection
- Adversarial Red Team
- Discoverability / Commercial Consequence Ladder
- Independent Human Review

## Signal classes
- NO_SIGNAL
- WATCHLIST
- OPPORTUNITY_SIGNAL_CANDIDATE
- OPPORTUNITY_SIGNAL
- VALIDATED_SIGNAL

## Related
- [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
- [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]
- [[01_ARCHITECTURE/RRT_DASHBOARD_VERTICAL_DATA_CONTRACT_V1]]
- [[01_ARCHITECTURE/RRT_FINAL_DASHBOARD_PRODUCT_SPEC_V1]]
- [[01_ARCHITECTURE/RRT_DASHBOARD_ONLINE_RESEARCH_NOTES_V1]]
- [[02_AGENTS/Multi-Agent System]]
- [[02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1]]
- [[03_RULES/Rules Index]]
- [[09_VALIDATION/Validation Dashboard]]
