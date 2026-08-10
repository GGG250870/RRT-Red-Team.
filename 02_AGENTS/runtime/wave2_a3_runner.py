import argparse
import json
import time
from pathlib import Path

from orchestrator import Orchestrator


def load_deep_scan_spec(repo_root: Path):
    path = repo_root / "03_RULES" / "RRT_TARGET_SPECIFIC_DEEP_SCAN_SPEC_V1_1.json"
    return json.loads(path.read_text(encoding="utf-8"))


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

    payload = {
        "company": args.company,
        "official_domain": args.official_domain,
        "purpose": "controlled Wave 2 A3 target-specific deep scan",
        "target_terms": spec.get("target_terms", {}),
        "saturation_strategy": spec.get("saturation_strategy", []),
        "adaptive_query_budget": spec.get("adaptive_query_budget", {}),
        "saturation_pass_conditions": spec.get("saturation_pass_conditions", []),
        "allowed_states": spec.get("states", []),
        "output_contract": {
            "compact": True,
            "language": "it",
            "max_findings_per_dimension": 4,
            "max_evidence_per_finding": 1,
            "no_term_by_term_repetition": True,
            "required_shape": {
                "overall_state": "PASS|INSUFFICIENT|COLLECTION_RESTRICTED|CONTRADICTORY|ENTITY_AMBIGUOUS",
                "confidence": "0-100",
                "dimensions": {
                    "D1": {"state": "PASS|NOT_FOUND_AFTER_PROTOCOL|COLLECTION_RESTRICTED|INSUFFICIENT|CONTRADICTORY", "findings": []},
                    "D2": {"state": "...", "findings": []},
                    "D3": {"state": "...", "findings": []},
                    "D4": {"state": "...", "findings": []},
                    "D5": {"state": "...", "findings": []}
                },
                "unresolved": [],
                "collection_restrictions": [],
                "saturation_state": "SATURATED|PARTIALLY_SATURATED|UNDERCOVERED|BLOCKED"
            }
        },
        "constraints": [
            "official-domain-first",
            "no invented zeros",
            "NOT_FOUND only after target-specific protocol",
            "one evidence_id per material claim",
            "preserve provenance and search trace",
            "no benchmark selection",
            "no commercial signal",
            "compress repeated target terms into one material finding when they rely on the same evidence",
            "do not narrate the full browsing process",
            "keep each finding concise: evidence_id, claim, url/source_ref, locator only",
            "return complete valid JSON before adding optional detail"
        ],
    }

    orch.enqueue_agent_task(args.case_id, "A3_DEEP_SCAN", "DEEP_SCAN", payload)
    result = orch.run_agents_parallel(["A3_DEEP_SCAN"], live=args.live, case_id=args.case_id)
    parsed = parse_worker_stdout(result.get("A3_DEEP_SCAN", {}))
    ok = result.get("A3_DEEP_SCAN", {}).get("returncode") == 0 and parsed.get("status") == "PASS"

    output = {
        "case_id": args.case_id,
        "run_started_at": started_at,
        "current_run_status": {
            "status": "PASS" if ok else "BLOCKED",
            "agent": "A3_DEEP_SCAN",
            "returncode": result.get("A3_DEEP_SCAN", {}).get("returncode"),
            "worker_status": parsed.get("status"),
        },
        "result": result,
        "historical_store_status": orch.status(),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
