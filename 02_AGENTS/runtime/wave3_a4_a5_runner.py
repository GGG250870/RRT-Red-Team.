import argparse
import json
import time
from pathlib import Path

from orchestrator import Orchestrator


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
    payload = {
        "case_id": args.case_id,
        "purpose": "controlled Wave 3 evidence audit and target match",
        "audited_input": latest_a3,
        "constraints": [
            "A4 may PASS, DOWNGRADE or REJECT but cannot add new evidence",
            "A5 must use only audited/persisted evidence",
            "no benchmark selection",
            "no economic inference",
            "preserve unresolved and contradiction states",
        ],
    }

    orch.enqueue_agent_task(args.case_id, "A4_EVIDENCE_AUDITOR", "EVIDENCE_AUDIT", payload)
    orch.enqueue_agent_task(args.case_id, "A5_TARGET_MATCH", "TARGET_MATCH", payload)
    result = orch.run_agents_parallel(["A4_EVIDENCE_AUDITOR", "A5_TARGET_MATCH"], live=args.live, case_id=args.case_id)

    agents = {}
    all_ok = True
    for aid in ["A4_EVIDENCE_AUDITOR", "A5_TARGET_MATCH"]:
        wr = result.get(aid, {})
        try:
            parsed = json.loads(wr.get("stdout") or "{}")
        except Exception:
            parsed = {"status": "UNPARSEABLE"}
        ok = wr.get("returncode") == 0 and parsed.get("status") == "PASS"
        all_ok = all_ok and ok
        agents[aid] = {"returncode": wr.get("returncode"), "status": parsed.get("status")}

    print(json.dumps({
        "case_id": args.case_id,
        "run_started_at": started_at,
        "current_run_status": {"status": "PASS" if all_ok else "BLOCKED", "agents": agents},
        "result": result,
        "historical_store_status": orch.status(),
    }, ensure_ascii=False, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
