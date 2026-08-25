---
type: agent-operating-model
version: v1
status: active
updated: 2026-08-25
---

# RRT Agent Operating Model V1

## Purpose

The user authorized the use of agents integrated in RRT.

This authorization does not remove the product constraints. Agents are bounded workers inside the RRT Red Team system. They may help discover, verify, challenge and prepare artifacts, but they cannot certify a Signal, contact a business, submit forms, bypass access restrictions, invent evidence or release outreach material without a human gate.

## Vertical Neutrality

Agents operate across verticals through vertical profiles:

- [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]

Dental is the active example. Agent roles must not hard-code dental assumptions except when the active vertical profile is `dentale.v1`.

## Agent Role Clusters

### 1. Discovery / Evidence Collection

Mapped agents:

- `A1_DISCOVERY`
- `A3_DEEP_SCAN`

Permitted inputs:

- frozen prospect identity;
- active vertical profile;
- official domain or verified source URL;
- allowed-source list;
- target segment;
- prior evidence pack.

Permitted outputs:

- source candidates;
- page graph;
- query trace;
- observations;
- target evidence packs;
- collection state.

Required provenance:

- URL or source identifier;
- date/time of observation when available;
- source type;
- access state: `FOUND`, `NOT_FOUND_AFTER_PROTOCOL`, `COLLECTION_RESTRICTED`, `BLOCKED`, `UNRESOLVED`;
- quote/excerpt only when compliant and short.

Forbidden:

- broad scraping;
- contact form submission;
- login/paywall/captcha bypass;
- commercial conclusion;
- Signal promotion.

Stop conditions:

- no official domain/source;
- collection blocked by access restriction;
- source outside allowed policy;
- insufficient provenance;
- repeated zero-result loop.

### 2. Entity Resolution

Mapped agent:

- `A2_ENTITY_SCOPE`

Permitted inputs:

- prospect identity fields;
- official domain candidates;
- source candidates;
- review/profile links;
- public company identifiers.

Permitted outputs:

- entity state;
- accepted/rejected sources;
- scope map;
- conflict ledger.

Required provenance:

- evidence for each accepted or rejected source;
- exact reason for entity acceptance or rejection.

Forbidden:

- merging multiple entities because names are similar;
- treating a portal profile as official domain;
- advancing ambiguous entities.

Stop conditions:

- `ENTITY_CONFLICT`;
- `OUT_OF_SCOPE`;
- `ENTITY_UNRESOLVED`;
- contradictory address/domain/profile.

### 3. Comparator Research

Mapped agents:

- `A5_TARGET_MATCH`
- `A6_BENCHMARK`

Permitted inputs:

- audited prospect evidence;
- active vertical profile;
- target segment/customer job;
- local or category comparator candidates.

Permitted outputs:

- eligible target;
- benchmark candidates;
- comparator fit basis;
- unresolved comparator warnings.

Required provenance:

- why the comparator is comparable;
- what customer-path evidence is being compared;
- source URLs and observation state.

Forbidden:

- selecting the competitor that maximizes the gap;
- comparing across incompatible segments;
- implying superior clinical, food or technical quality;
- economic inference.

Stop conditions:

- no comparable benchmark;
- target segment unresolved;
- comparator evidence incomplete;
- scope conflict.

### 4. Red-Team Challenger

Mapped agent:

- `A7_RED_TEAM`

Permitted inputs:

- proposed finding;
- prospect evidence;
- comparator evidence;
- vertical profile falsification prompts;
- prior caveats.

Permitted outputs:

- `FALSIFIED`;
- `WEAK_SURVIVAL`;
- `SURVIVES`;
- counterevidence;
- residual caveats.

Required provenance:

- counterevidence sources;
- explicit alternative explanations;
- rejected assumptions.

Forbidden:

- defending the finding by default;
- adding unsupported claims;
- turning weak survival into Signal.

Stop conditions:

- finding falsified;
- evidence stale or ambiguous;
- comparator not fit;
- finding requires unsupported economic or quality claim.

### 5. Dossier / Report Preparation

Mapped agents:

- `A8_COMMERCIAL_GATE`
- report-preparation worker when present.

Permitted inputs:

- audited finding;
- Red Team verdict;
- vertical language constraints;
- contact details;
- source and caveat list.

Permitted outputs:

- `NO_SIGNAL`;
- `WATCHLIST`;
- `OPPORTUNITY_SIGNAL_CANDIDATE`;
- safe wording;
- draft dossier sections;
- draft mini-audit;
- draft first-contact script marked `HUMAN_REVIEW_REQUIRED`.

Required provenance:

- every claim points to evidence ID/source;
- every caveat remains visible;
- every missing source remains marked.

Forbidden:

- certifying `OPPORTUNITY_SIGNAL`;
- producing usable outreach without human approval;
- claiming revenue loss, conversion loss or quality deficiency;
- pressure wording.

Stop conditions:

- Red Team not run;
- Red Team `FALSIFIED`;
- missing source attribution;
- unsafe language detected;
- human approval missing.

### 6. Human Approval / Release

Mapped agent:

- `A9_QA_ORCHESTRATOR` prepares QA state only.
- Human reviewer certifies or blocks.

Permitted inputs:

- all agent outputs;
- evidence pack;
- Red Team review;
- safe/unsafe language checklist;
- cost ledger.

Permitted outputs:

- `READY_FOR_HUMAN_REVIEW`;
- `BLOCKED`;
- conflict ledger;
- audit hash;
- release checklist.

Human-only outputs:

- `OPPORTUNITY_SIGNAL`;
- `VALIDATED_SIGNAL`;
- outreach artifact approved for use.

Stop conditions:

- unresolved conflict;
- missing provenance;
- unsafe claim;
- cost/consent violation;
- vertical profile `draft`;
- human approval absent.

## Handoff Contract

Each agent handoff must include:

- `case_id`;
- `vertical_profile_id`;
- `target_segment`;
- `agent_id`;
- `stage`;
- `input_refs`;
- `output_refs`;
- `provenance_refs`;
- `state`;
- `blocking_conditions`;
- `cost_eur_estimated`;
- `cost_eur_actual`;
- `requires_human_review`.

If an agent cannot produce valid output, it must return a blocking state rather than filling gaps.

## Cost And Consent

Live agent-team runs remain blocked unless explicit approval and budget exist.

Required consent controls:

- `RRT_AGENT_TEAM_APPROVAL=I_APPROVE_AGENT_TEAM_LIVE_RUN`
- per-call budget;
- per-case budget;
- per-run budget;
- cost ledger in EUR;
- stop on budget exceedance.

Free/local/pre-screen work remains `EUR 0.0000` and does not unlock live agents.


### Per-run user notice

Paid/live agents are available, but every run requires a new notice before execution until the user changes this instruction.

The notice must state:

- prospect or batch scope;
- agents that will be used;
- planned activity;
- data and sources in scope;
- estimated maximum cost in EUR;
- stop conditions.

A prior authorization cannot be silently reused. The run starts only after the user approves that specific notice and the runtime approval/budget controls are present. Preparing free inputs, plans or estimates does not count as a paid/live agent run.

## Release Rule

No Signal or outreach artifact is usable until:

1. active vertical profile exists;
2. entity resolution passes;
3. evidence pack has provenance;
4. comparator is fit and frozen;
5. Red Team survives;
6. commercial wording is safe;
7. QA is `READY_FOR_HUMAN_REVIEW`;
8. human reviewer explicitly approves.

## Related

- [[02_AGENTS/Multi-Agent System]]
- [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]
- [[03_RULES/Rules Index]]
- [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
