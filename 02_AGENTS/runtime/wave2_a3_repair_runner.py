import argparse
import json
import time
from pathlib import Path

from orchestrator import Orchestrator


def load_deep_scan_spec(repo_root: Path):
    path = repo_root / "03_RULES" / "RRT_TARGET_SPECIFIC_DEEP_SCAN_SPEC_V1_1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def latest_agent_output(store, case_id, agent_id):
    outputs = store.outputs_for_case(case_id)
    matches = [o for o in outputs if o.get("agent_id") == agent_id]
    return matches[-1] if matches else None


def parse_worker_stdout(worker_result):
    raw = (worker_result or {}).get("stdout") or ""
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "UNPARSEABLE", "raw": raw}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--official-domain", required=True)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    runtime = Path(__file__).resolve().parent
    repo_root = runtime.parents[1]
    spec = load_deep_scan_spec(repo_root)
    orch = Orchestrator(runtime)
    started_at = time.time()

    prior_a3 = latest_agent_output(orch.store, args.case_id, "A3_DEEP_SCAN")
    prior_a4 = latest_agent_output(orch.store, args.case_id, "A4_EVIDENCE_AUDITOR")
    if not prior_a3 or not prior_a4:
        print(json.dumps({"case_id": args.case_id, "status": "BLOCKED", "reason": "MISSING_A3_OR_A4_OUTPUT"}, ensure_ascii=False, indent=2))
        return 2

    a4_output = (prior_a4.get("output") or {})
    downgraded = a4_output.get("downgraded_evidence_ids") or []
    unresolved = a4_output.get("unresolved") or []

    payload = {
        "company": args.company,
        "official_domain": args.official_domain,
        "purpose": "targeted A3 repair after A4 downgrade",
        "prior_a3": prior_a3,
        "a4_audit": prior_a4,
        "repair_scope": {
            "downgraded_evidence_ids": downgraded,
            "unresolved_items": unresolved,
            "dimensions": ["D3", "D4", "D5"]
        },
        "target_terms": spec.get("target_terms", {}),
        "saturation_strategy": spec.get("saturation_strategy", []),
        "saturation_pass_conditions": spec.get("saturation_pass_conditions", []),
        "adaptive_query_budget": spec.get("adaptive_query_budget", {}),
        "output_contract": {
            "compact": True,
            "required_shape": {
                "overall_state": "PASS|INSUFFICIENT|COLLECTION_RESTRICTED|CONTRADICTORY",
                "repaired_evidence": [],
                "still_unresolved": [],
                "execution_trace": {"pages_checked": [], "queries": [], "negative_results": []},
                "saturation_state": "SATURATED|PARTIALLY_SATURATED|UNDERCOVERED|BLOCKED"
            }
        },
        "constraints": [
            "repair only downgraded or unresolved evidence",
            "prefer direct official-page acquisition over search snippets",
            "do not claim a repaired evidence item unless page content is acquired with URL and locator",
            "record pages checked, queries executed and negative results needed for saturation",
            "do not infer page freshness from collection time",
            "do not re-litigate already certified D1 and D2 unless contradiction is found",
            "no benchmark selection",
            "no commercial signal",
            "return complete valid JSON before optional detail"
        ]
    }

    orch.enqueue_agent_task(args.case_id, "A3_DEEP_SCAN", "DEEP_SCAN_REPAIR", payload)
    result = orch.run_agents_parallel(["A3_DEEP_SCAN"], live=args.live, case_id=args.case_id)
    worker = result.get("A3_DEEP_SCAN", {})
    parsed = parse_worker_stdout(worker)
    ok = worker.get("returncode") == 0 and parsed.get("status") == "PASS"

    print(json.dumps({
        "case_id": args.case_id,
        "run_started_at": started_at,
        "current_run_status": {"status": "PASS" if ok else "BLOCKED", "agent": "A3_DEEP_SCAN", "worker_status": parsed.get("status")},
        "repair_scope": {"downgraded_evidence_ids": downgraded, "unresolved": unresolved},
        "result": result,
        "historical_store_status": orch.status()
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
