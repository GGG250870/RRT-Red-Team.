import argparse
import json
import time
from pathlib import Path

from orchestrator import Orchestrator


def parse_worker_stdout(worker_result):
    raw = (worker_result or {}).get("stdout") or ""
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "UNPARSEABLE", "raw": raw}


def load_deep_scan_spec(repo_root: Path):
    path = repo_root / "03_RULES" / "RRT_TARGET_SPECIFIC_DEEP_SCAN_SPEC_V1_1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def extract_a3_output(record):
    return (((record or {}).get("result") or {}).get("output") or {})


def is_repair_output(record):
    out = extract_a3_output(record)
    return bool(out.get("repaired_evidence") or out.get("execution_trace") or out.get("still_unresolved"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    runtime = Path(__file__).resolve().parent
    repo_root = runtime.parents[1]
    spec = load_deep_scan_spec(repo_root)
    orch = Orchestrator(runtime)
    started_at = time.time()

    prior_outputs = orch.store.outputs_for_case(args.case_id)
    a3_outputs = [o for o in prior_outputs if o.get("agent_id") == "A3_DEEP_SCAN"]
    if not a3_outputs:
        print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "reason": "NO_A3_OUTPUT"}}, ensure_ascii=False, indent=2))
        return 2

    baseline_candidates = [o for o in a3_outputs if not is_repair_output(o)]
    repair_candidates = [o for o in a3_outputs if is_repair_output(o)]
    baseline_a3 = baseline_candidates[-1] if baseline_candidates else a3_outputs[0]
    latest_repair = repair_candidates[-1] if repair_candidates else None

    audited_input = {
        "baseline_deep_scan": baseline_a3,
        "repair_overlay": latest_repair,
        "merge_rule": "Audit baseline D1-D5 plus latest repair. Repair overrides only evidence IDs and dimensions it explicitly repairs; baseline evidence remains valid unless explicitly downgraded, contradicted, or superseded. COLLECTION_RESTRICTED in repair must remain restricted and must not erase unrelated baseline PASS evidence."
    }

    a4_payload = {
        "case_id": args.case_id,
        "purpose": "controlled Wave 3 evidence audit",
        "audited_input": audited_input,
        "target_terms": spec.get("target_terms", {}),
        "saturation_strategy": spec.get("saturation_strategy", []),
        "saturation_pass_conditions": spec.get("saturation_pass_conditions", []),
        "adaptive_query_budget": spec.get("adaptive_query_budget", {}),
        "freshness_context": {
            "audit_run_started_at": started_at,
            "collection_is_current_runtime_run": True,
            "rule": "Collection time is not page freshness."
        },
        "output_contract": {
            "format": "compact_json_only",
            "required_keys": ["verdict", "overall_state", "dimensions", "downgraded_evidence_ids", "unresolved", "reason"],
            "dimensions_shape": "D1-D5 => PASS|DOWNGRADE|REJECT|UNRESOLVED|COLLECTION_RESTRICTED",
            "reason_max_words": 80,
            "per_dimension_notes_max_words": 18,
            "forbidden": ["long prose", "repeat evidence claims", "repeat source URLs", "narrative restatement of input"]
        },
        "constraints": [
            "A4 may PASS, DOWNGRADE or REJECT but cannot add new evidence",
            "preserve unresolved and contradiction states",
            "audit baseline and repair together using the supplied merge_rule",
            "do not mark D1 or D2 unresolved merely because the repair overlay does not repeat them",
            "evaluate D1-D5 against supplied target terms and pass conditions",
            "search-result snippets are weaker than acquired page content and may be downgraded",
            "do not certify SATURATED unless supplied trace demonstrates the protocol",
            "return compact JSON only",
            "list downgraded evidence IDs once, without repeating their claims",
            "no benchmark selection",
            "no economic inference"
        ]
    }

    orch.enqueue_agent_task(args.case_id, "A4_EVIDENCE_AUDITOR", "EVIDENCE_AUDIT", a4_payload)
    a4_result = orch.run_agents_parallel(["A4_EVIDENCE_AUDITOR"], live=args.live, case_id=args.case_id)
    a4_worker = a4_result.get("A4_EVIDENCE_AUDITOR", {})
    a4_parsed = parse_worker_stdout(a4_worker)
    a4_ok = a4_worker.get("returncode") == 0 and a4_parsed.get("status") == "PASS"

    if not a4_ok:
        print(json.dumps({
            "case_id": args.case_id,
            "run_started_at": started_at,
            "current_run_status": {"status": "BLOCKED", "reason": "A4_GATE_FAILED", "agents": {"A4_EVIDENCE_AUDITOR": {"returncode": a4_worker.get("returncode"), "status": a4_parsed.get("status")}}},
            "result": a4_result,
            "historical_store_status": orch.status()
        }, ensure_ascii=False, indent=2))
        return 1

    a4_output = ((a4_parsed.get("result") or {}).get("output") or {})
    a4_verdict = a4_output.get("verdict")
    a4_state = a4_output.get("overall_state") or a4_output.get("final_saturation_state")
    audit_gate_pass = a4_verdict == "PASS" and a4_state == "PASS"

    if args.live and not audit_gate_pass:
        print(json.dumps({
            "case_id": args.case_id,
            "run_started_at": started_at,
            "current_run_status": {
                "status": "BLOCKED",
                "reason": "A4_AUDIT_NOT_CERTIFIED",
                "required_action": "REOPEN_A3_ON_DOWNGRADED_OR_UNRESOLVED_EVIDENCE",
                "a4_verdict": a4_verdict,
                "a4_state": a4_state,
                "downgraded_evidence_ids": a4_output.get("downgraded_evidence_ids", []),
                "unresolved": a4_output.get("unresolved", []),
                "agents": {"A4_EVIDENCE_AUDITOR": {"returncode": a4_worker.get("returncode"), "status": a4_parsed.get("status")}}
            },
            "result": a4_result,
            "historical_store_status": orch.status()
        }, ensure_ascii=False, indent=2))
        return 4

    latest_outputs = orch.store.outputs_for_case(args.case_id)
    a4_outputs = [o for o in latest_outputs if o.get("agent_id") == "A4_EVIDENCE_AUDITOR"]
    if not a4_outputs:
        print(json.dumps({"case_id": args.case_id, "current_run_status": {"status": "BLOCKED", "reason": "A4_OUTPUT_NOT_PERSISTED"}}, ensure_ascii=False, indent=2))
        return 3

    latest_a4 = a4_outputs[-1]
    a5_payload = {
        "case_id": args.case_id,
        "purpose": "controlled Wave 3 target match after certified evidence audit",
        "audited_input": latest_a4,
        "target_terms": spec.get("target_terms", {}),
        "constraints": [
            "A5 must use only A4-audited persisted evidence",
            "do not resurrect evidence downgraded or rejected by A4",
            "map only against supplied D1-D5 target definitions",
            "no benchmark selection",
            "no economic inference",
            "preserve unresolved and contradiction states"
        ]
    }

    orch.enqueue_agent_task(args.case_id, "A5_TARGET_MATCH", "TARGET_MATCH", a5_payload)
    a5_result = orch.run_agents_parallel(["A5_TARGET_MATCH"], live=args.live, case_id=args.case_id)
    a5_worker = a5_result.get("A5_TARGET_MATCH", {})
    a5_parsed = parse_worker_stdout(a5_worker)
    a5_ok = a5_worker.get("returncode") == 0 and a5_parsed.get("status") == "PASS"

    combined = {}
    combined.update(a4_result)
    combined.update(a5_result)

    print(json.dumps({
        "case_id": args.case_id,
        "run_started_at": started_at,
        "current_run_status": {
            "status": "PASS" if a5_ok else "BLOCKED",
            "agents": {
                "A4_EVIDENCE_AUDITOR": {"returncode": a4_worker.get("returncode"), "status": a4_parsed.get("status")},
                "A5_TARGET_MATCH": {"returncode": a5_worker.get("returncode"), "status": a5_parsed.get("status")}
            }
        },
        "result": combined,
        "historical_store_status": orch.status()
    }, ensure_ascii=False, indent=2))
    return 0 if a5_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
