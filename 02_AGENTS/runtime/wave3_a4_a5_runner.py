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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    runtime = Path(__file__).resolve().parent
    orch = Orchestrator(runtime)
    started_at = time.time()

    prior_outputs = orch.store.outputs_for_case(args.case_id)
    a3_outputs = [o for o in prior_outputs if o.get("agent_id") == "A3_DEEP_SCAN"]
    if not a3_outputs:
        print(json.dumps({
            "case_id": args.case_id,
            "current_run_status": {"status": "BLOCKED", "reason": "NO_A3_OUTPUT"}
        }, ensure_ascii=False, indent=2))
        return 2

    latest_a3 = a3_outputs[-1]
    a4_payload = {
        "case_id": args.case_id,
        "purpose": "controlled Wave 3 evidence audit",
        "audited_input": latest_a3,
        "constraints": [
            "A4 may PASS, DOWNGRADE or REJECT but cannot add new evidence",
            "preserve unresolved and contradiction states",
            "no benchmark selection",
            "no economic inference",
        ],
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
            "current_run_status": {
                "status": "BLOCKED",
                "reason": "A4_GATE_FAILED",
                "agents": {"A4_EVIDENCE_AUDITOR": {"returncode": a4_worker.get("returncode"), "status": a4_parsed.get("status")}}
            },
            "result": a4_result,
            "historical_store_status": orch.status(),
        }, ensure_ascii=False, indent=2))
        return 1

    latest_outputs = orch.store.outputs_for_case(args.case_id)
    a4_outputs = [o for o in latest_outputs if o.get("agent_id") == "A4_EVIDENCE_AUDITOR"]
    if not a4_outputs:
        print(json.dumps({
            "case_id": args.case_id,
            "current_run_status": {"status": "BLOCKED", "reason": "A4_OUTPUT_NOT_PERSISTED"}
        }, ensure_ascii=False, indent=2))
        return 3

    latest_a4 = a4_outputs[-1]
    a5_payload = {
        "case_id": args.case_id,
        "purpose": "controlled Wave 3 target match after evidence audit",
        "audited_input": latest_a4,
        "constraints": [
            "A5 must use only A4-audited persisted evidence",
            "do not resurrect evidence downgraded or rejected by A4",
            "no benchmark selection",
            "no economic inference",
            "preserve unresolved and contradiction states",
        ],
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
                "A5_TARGET_MATCH": {"returncode": a5_worker.get("returncode"), "status": a5_parsed.get("status")},
            },
        },
        "result": combined,
        "historical_store_status": orch.status(),
    }, ensure_ascii=False, indent=2))
    return 0 if a5_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
