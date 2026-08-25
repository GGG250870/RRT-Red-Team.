import argparse
import json
import time
from pathlib import Path

from orchestrator import Orchestrator

SEQUENCE = [
    ("A6_BENCHMARK", "BENCHMARK"),
    ("A7_RED_TEAM", "RED_TEAM"),
    ("A8_COMMERCIAL_GATE", "COMMERCIAL_GATE"),
    ("A9_QA_ORCHESTRATOR", "QA_ORCHESTRATION"),
]


def parse_worker_stdout(worker_result):
    raw = (worker_result or {}).get("stdout") or ""
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "UNPARSEABLE", "raw": raw}


def provider_output(record):
    record = record or {}
    if isinstance(record.get("output"), dict):
        return record.get("output") or {}
    nested = record.get("result") or {}
    if isinstance(nested, dict) and isinstance(nested.get("output"), dict):
        return nested.get("output") or {}
    return {}


def latest_agent_output(store, case_id, agent_id):
    rows = [o for o in store.outputs_for_case(case_id) if o.get("agent_id") == agent_id]
    return rows[-1] if rows else None


def latest_a5(store, case_id):
    return latest_agent_output(store, case_id, "A5_TARGET_MATCH")


def stage_gate(agent_id, output):
    if not output:
        return False, "EMPTY_OUTPUT"

    contradictions = output.get("contradictions") or []
    if contradictions:
        return False, "CONTRADICTIONS_PRESENT"

    if agent_id == "A6_BENCHMARK":
        state = output.get("overall_state") or output.get("state") or output.get("benchmark_state") or output.get("benchmark_selection_state")
        benchmarks = output.get("benchmarks") or output.get("comparables") or output.get("top_comparables") or output.get("frozen_benchmarks") or []
        fit_basis = output.get("fit_basis") or output.get("benchmark_fit_summary") or []
        if state in {"BLOCKED", "REJECT", "CONTRADICTORY", "UNRESOLVED", "COLLECTION_RESTRICTED"}:
            return False, f"A6_{state}"
        if not benchmarks:
            return False, "A6_NO_BENCHMARKS"
        if not fit_basis:
            fit_basis = [b.get("fit_basis") for b in benchmarks if isinstance(b, dict) and b.get("fit_basis")]
        if not fit_basis:
            return False, "A6_NO_FIT_BASIS"
        return True, "PASS"

    if agent_id == "A7_RED_TEAM":
        verdict = output.get("verdict") or output.get("outcome") or output.get("state")
        if verdict == "FALSIFIED":
            return False, "A7_FALSIFIED"
        if verdict not in {"SURVIVES", "WEAK_SURVIVAL"}:
            return False, "A7_UNCERTIFIED"
        return True, verdict

    if agent_id == "A8_COMMERCIAL_GATE":
        signal = output.get("signal_class") or output.get("classification") or output.get("state")
        allowed = {"NO_SIGNAL", "WATCHLIST", "OPPORTUNITY_SIGNAL_CANDIDATE"}
        if signal not in allowed:
            return False, "A8_INVALID_SIGNAL_CLASS"
        return True, signal

    if agent_id == "A9_QA_ORCHESTRATOR":
        verdict = output.get("verdict") or output.get("state") or output.get("overall_state")
        return (verdict in {"READY", "READY_FOR_HUMAN_REVIEW"}), (verdict or "A9_UNCERTIFIED")

    return False, "UNKNOWN_AGENT"


def build_payload(agent_id, case_id, upstream, a5_record):
    a5_output = provider_output(a5_record)
    common = {
        "case_id": case_id,
        "source_of_truth": "persisted_agent_outputs",
        "constraints": [
            "Never invent missing facts.",
            "Preserve COLLECTION_RESTRICTED, UNRESOLVED, CONTRADICTORY and rejected evidence states.",
            "Do not resurrect E08 or E11 as positive evidence for B04-34 unless a later audited source explicitly supersedes their restriction.",
            "Do not infer ROI, lost revenue, lost leads, conversion loss or economic causality without explicit audited evidence.",
            "Return compact JSON only."
        ]
    }

    if agent_id == "A6_BENCHMARK":
        return {
            **common,
            "purpose": "discover and freeze defensible comparable benchmark before gap evaluation",
            "target_match": a5_output,
            "output_contract": {
                "required_keys": ["case_id", "state", "frozen_benchmarks", "benchmark_fit_summary", "candidate_gaps", "scope_warnings", "rejected_candidates", "search_trace"],
                "max_frozen_benchmarks": 3,
                "max_rejected_candidates": 3,
                "max_candidate_gaps": 3,
                "per_note_max_words": 20,
                "forbidden": ["long prose", "duplicate target terms", "duplicate evidence text", "marketing copy", "economic inference"]
            },
            "requirements": [
                "Actively discover a candidate benchmark universe using web_search before declaring UNRESOLVED.",
                "Use same vertical, same geography when practical, and same decision job.",
                "Prefer official domains and public verifiable pages for each candidate.",
                "Collect at least 2 candidate comparables when available; retain only candidates with verifiable fit.",
                "For each retained comparable include only name, official_domain, covered_dimensions, concise fit_basis and concise source_provenance.",
                "Freeze benchmark selection before interpreting any gap.",
                "Formulate at most 3 explicit benchmark-relative candidate_gaps for A7 to falsify; each gap must identify target dimension, target evidence basis, benchmark basis and unresolved caveats.",
                "Do not choose the competitor that maximizes the gap.",
                "If no defensible comparable survives discovery, return UNRESOLVED and concise search_trace; downstream must stop.",
                "Do not repeat full claims, URLs more than once per benchmark, or the complete A5 packet."
            ]
        }

    if agent_id == "A7_RED_TEAM":
        return {
            **common,
            "purpose": "attempt to falsify candidate gaps before commercial use",
            "target_match": a5_output,
            "benchmark_output": provider_output(upstream["A6_BENCHMARK"]),
            "requirements": [
                "Act independently from benchmark selection.",
                "Falsify only explicitly formulated candidate_gaps from A6; never invent a generic gap.",
                "Search for alternative explanations, scope errors, prominence/discoverability confusion and overclaim.",
                "No web tool: falsify only from persisted audited material and frozen benchmark packet.",
                "Return one of FALSIFIED, SURVIVES, WEAK_SURVIVAL plus concise reasons and unresolved items."
            ]
        }

    if agent_id == "A8_COMMERCIAL_GATE":
        return {
            **common,
            "purpose": "classify commercial signal conservatively after red-team",
            "target_match": a5_output,
            "benchmark_output": provider_output(upstream["A6_BENCHMARK"]),
            "red_team_output": provider_output(upstream["A7_RED_TEAM"]),
            "requirements": [
                "Allowed classes only: NO_SIGNAL, WATCHLIST, OPPORTUNITY_SIGNAL_CANDIDATE.",
                "Do not promote a falsified finding.",
                "Do not convert COLLECTION_RESTRICTED evidence into a positive signal.",
                "Separate observable evidence, hypothesis and commercial question."
            ]
        }

    if agent_id == "A9_QA_ORCHESTRATOR":
        return {
            **common,
            "purpose": "final cross-agent consistency and provenance QA",
            "a5_target_match": a5_output,
            "a6_benchmark": provider_output(upstream["A6_BENCHMARK"]),
            "a7_red_team": provider_output(upstream["A7_RED_TEAM"]),
            "a8_commercial_gate": provider_output(upstream["A8_COMMERCIAL_GATE"]),
            "output_contract": {
                "required_keys": ["case_id", "verdict", "conflict_ledger", "unresolved_states", "qa_checks", "release_checklist"],
                "verdict_values": ["READY_FOR_HUMAN_REVIEW", "BLOCKED"],
                "max_conflicts": 5,
                "max_unresolved": 5,
                "per_note_max_words": 18,
                "forbidden": ["long prose", "restating full upstream outputs", "new findings", "new commercial inference", "human approval simulation"]
            },
            "requirements": [
                "Return READY_FOR_HUMAN_REVIEW or BLOCKED only.",
                "Do not silently rewrite upstream outputs.",
                "Do not certify Opportunity Signal or approve outreach for use.",
                "Check only provenance continuity, restricted-evidence resurrection, unsupported economic inference, cross-agent contradictions and allowed state transitions.",
                "Emit compact conflict_ledger and unresolved_states; do not repeat upstream evidence text.",
                "READY_FOR_HUMAN_REVIEW is allowed with nonblocking unresolved states if they are explicitly preserved and do not support the commercial signal.",
                "BLOCK only on a material QA failure, not merely because unresolved states exist."
            ]
        }

    raise ValueError(agent_id)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    runtime = Path(__file__).resolve().parent
    orch = Orchestrator(runtime)
    started_at = time.time()

    a5_record = latest_a5(orch.store, args.case_id)
    if not a5_record:
        print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "reason": "NO_A5_OUTPUT"}}, ensure_ascii=False, indent=2))
        return 2

    upstream = {}
    stage_results = {}

    for agent_id, stage in SEQUENCE:
        if args.resume:
            existing = latest_agent_output(orch.store, args.case_id, agent_id)
            existing_output = provider_output(existing) if existing else {}
            ok, reason = stage_gate(agent_id, existing_output) if existing else (False, "NO_EXISTING_OUTPUT")
            if existing and ok:
                upstream[agent_id] = existing
                stage_results[agent_id] = {"status": "REUSED", "gate_reason": reason}
                continue

        payload = build_payload(agent_id, args.case_id, upstream, a5_record)
        orch.enqueue_agent_task(args.case_id, agent_id, stage, payload)
        result = orch.run_agents_parallel([agent_id], live=args.live, case_id=args.case_id)
        worker = result.get(agent_id, {})
        parsed = parse_worker_stdout(worker)
        technical_ok = worker.get("returncode") == 0 and parsed.get("status") == "PASS"
        if not technical_ok:
            print(json.dumps({
                "case_id": args.case_id,
                "run_started_at": started_at,
                "current_run_status": {"status": "BLOCKED", "stage": agent_id, "reason": "TECHNICAL_STAGE_FAILURE"},
                "result": result,
                "historical_store_status": orch.status()
            }, ensure_ascii=False, indent=2))
            return 3

        persisted = latest_agent_output(orch.store, args.case_id, agent_id)
        output = provider_output(persisted)
        gate_ok, gate_reason = stage_gate(agent_id, output)
        stage_results[agent_id] = {"status": "PASS" if gate_ok else "BLOCKED", "gate_reason": gate_reason, "worker": result.get(agent_id)}
        upstream[agent_id] = persisted

        if not gate_ok:
            print(json.dumps({
                "case_id": args.case_id,
                "run_started_at": started_at,
                "current_run_status": {"status": "BLOCKED", "stage": agent_id, "reason": gate_reason},
                "stages": stage_results,
                "historical_store_status": orch.status()
            }, ensure_ascii=False, indent=2))
            return 4

    print(json.dumps({
        "case_id": args.case_id,
        "run_started_at": started_at,
        "current_run_status": {"status": "READY_FOR_HUMAN_REVIEW", "final_stage": "A9_QA_ORCHESTRATOR", "qa_state": stage_results.get("A9_QA_ORCHESTRATOR", {}).get("gate_reason")},
        "stages": stage_results,
        "historical_store_status": orch.status()
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
