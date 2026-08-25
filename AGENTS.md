# RRT Codex Working Contract

## Canonical source

- GitHub `main` is the single authoritative state of RRT.
- Before starting work, fetch `origin` and branch from the current `origin/main`.
- Use one focused `agent/<scope>` branch per task and integrate through a pull request.
- Do not treat files outside this repository, chat artifacts, Library snapshots, or generated dashboard output as newer source unless they are deliberately imported and reviewed.
- Do not claim work is active unless a process or agent is actually running. Distinguish committed, pushed, merged, local-only, planned, and generated states.

## Required reading order

1. `00_HOME/HOME.md`
2. `01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1.md`
3. `01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1.md`
4. `02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1.md`
5. `02_AGENTS/RRT_AGENT_AUTHORIZATION_POLICY_V1.json`
6. `03_RULES/Rules Index.md`
7. `99_CHANGELOG/CHANGELOG.md`

## Product invariant

RRT is an external commercial Red Team. Prospect lists, scraping-like discovery, dashboards, scores and generic marketing reports are intermediate infrastructure. The sellable output is a small set of non-obvious, falsified, audit-ready Opportunity Signals that make the entrepreneur ask how they were visible from outside.

Preserve these invariants:

- missing evidence is not zero;
- `COLLECTION_RESTRICTED` is not absence;
- entity and scope resolution precede scoring;
- no Signal without provenance, comparator fit, Red Team, QA and human review;
- no lost-revenue, quality or causal claim without the required internal evidence;
- no contact, outreach release, paid API, live agent run or access bypass without the required explicit authorization.

## Agent and runtime integration

- Agent definitions, permissions and handoffs live in `02_AGENTS/`.
- Executable orchestration lives in `02_AGENTS/runtime/` and must follow the JSON contracts in `02_AGENTS/`.
- Obsidian Markdown is the human interface; it must describe the same machine states and must not override runtime ledgers.
- The dashboard in `11_DASHBOARD/` consumes pre-screen and evidence states; it must not promote its own score to an Opportunity Signal.
- Vertical behavior comes from explicit profiles in `03_RULES/vertical_profiles/`; do not hard-code dental assumptions into the common core.
- A1-A9 live execution remains locked unless `RRT_AGENT_TEAM_APPROVAL=I_APPROVE_AGENT_TEAM_LIVE_RUN` and the applicable budget controls are present.

## Required validation before push

Run the checks relevant to the changed area. For cross-cutting changes, run all of these from the repository root:

```bash
python3 03_RULES/validate_vertical_profiles.py
python3 02_AGENTS/validate_agent_authorization_policy.py
python3 11_DASHBOARD/test_entity_resolution.py
python3 11_DASHBOARD/test_review_intelligence.py
python3 11_DASHBOARD/test_dashboard.py
python3 00_PRE_SCREEN/test_open_data_discovery.py
python3 11_DASHBOARD/test_pilot_readiness.py
python3 11_DASHBOARD/test_public_enrichment.py
python3 00_PRE_SCREEN/test_category_segments.py
python3 02_AGENTS/runtime/test_runtime.py
python3 09_VALIDATION/test_scoring_integrity_v2.py
PYTHONPYCACHEPREFIX=/tmp/rrt_compile python3 -m compileall -q 00_PRE_SCREEN 02_AGENTS/runtime 09_VALIDATION 11_DASHBOARD
```

Report exact pass/fail results. Do not describe GitHub checks as passing when only local tests ran.

## Integration discipline

- Read file and current branch state before editing.
- Preserve unrelated user changes.
- Rebase or merge the latest `origin/main` before final validation.
- Resolve conflicts by preserving both valid knowledge lines unless one is demonstrably superseded.
- Update `99_CHANGELOG/CHANGELOG.md` for material product, rule, runtime or validation changes.
- After merge, tell the user what is now in `main`, what remains blocked and what Codex must fetch locally.

