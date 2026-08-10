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
    record = record or {}
    if isinstance(record.get("output"), dict):
        return record.get("output") or {}
    nested = record.get("result") or {}
    if isinstance(nested, dict) and isinstance(nested.get("output"), dict):
        return nested.get("output") or {}
    return {}


def is_repair_output(record):
    out = extract_a3_output(record)
    return bool(out.get("repaired_evidence") or out.get("execution_trace") or out.get("still_unresolved"))


def audit_gate_decision(a4_output):
    verdict = a4_output.get("verdict")
    state = a4_output.get("overall_state") or a4_output.get("final_saturation_state")
    dimensions = a4_output.get("dimensions") or {}
    unresolved = a4_output.get("unresolved") or []
    downgraded = set(a4_output.get("downgraded_evidence_ids") or [])

    allowed_restrictions = {"E08", "E11"}
    unresolved_items = {str((item or {}).get("item")) for item in unresolved}
    restricted_only = unresolved_items.issubset(allowed_restrictions) and downgraded.issubset(allowed_restrictions)

    if verdict == "PASS" and state == "PASS":
        return True, "PASS"

    blocking_dimension_states = {"REJECT", "UNRESOLVED", "CONTRADICTORY"}
    for dim_id, dim in dimensions.items():
        if (dim or {}).get("state") in blocking_dimension_states:
            return False, f"BLOCKING_DIMENSION_{dim_id}"

    if not restricted_only:
        if unresolved_items and not unresolved_items.issubset(allowed_restrictions):
            return False, "UNRESOLVED_OUTSIDE_NONBLOCKING_ALLOWLIST"
        if downgraded and not downgraded.issubset(allowed_restrictions):
            return False, "DOWNGRADED_OUTSIDE_NONBLOCKING_ALLOWLIST"
        return False, "AUDIT_RESTRICTIONS_NOT_NONBLOCKING"

    if state in {"COLLECTION_RESTRICTED", "PARTIALLY_SATURATED"} and verdict in {"PASS", "DOWNGRADE"}:
        required_pass = {"D1", "D2", "D3"}
        if not all((dimensions.get(d) or {}).get("state") == "PASS" for d in required_pass):
            return False, "CORE_DIMENSIONS_NOT_PASS"

        for dim_id in ("D4", "D5"):
            dim = dimensions.get(dim_id) or {}
            dim_state = dim.get("state")
            if dim_state not in {"PASS", "DOWNGRADE", "COLLECTION_RESTRICTED"}:
                return False, f"BLOCKING_DIMENSION_{dim_id}"
            note = str(dim.get("note") or "").lower()
            if dim_state != "PASS":
                positive_markers = ("supporto", "evidenz", "restano valid", "sufficiente", "copertura")
                if not any(marker in note for marker in positive_markers):
                    return False, f"NO_POSITIVE_SUPPORT_{dim_id}"

        return True, "PASS_WITH_NONBLOCKING_COLLECTION_RESTRICTIONS"

    if verdict not in {"PASS", "DOWNGRADE"}:
        return False, "AUDIT_VERDICT_NOT_PASS"
    if state not in {"PASS", "COLLECTION_RESTRICTED", "PARTIALLY_SATURATED"}:
        return False, "AUDIT_STATE_BLOCKING"
    return False, "AUDIT_NOT_CERTIFIED"


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

    baseline_output = extract_a3_output(baseline_a3)
    repair_output = extract_a3_output(latest_repair) if latest_repair else None

    audited_input = {
        "baseline_deep_scan": baseline_output,
        "repair_overlay": repair_output,
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
    audit_gate_pass, audit_gate_reason = audit_gate_decision(a4_output)

    if args.live and not audit_gate_pass:
        print(json.dumps({
            "case_id": args.case_id,
            "run_started_at": started_at,
            "current_run_status": {
                "status": "BLOCKED",
                "reason": "A4_AUDIT_NOT_CERTIFIED",
                "gate_reason": audit_gate_reason,
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

    a5_payload = {
        "case_id": args.case_id,
        "purpose": "controlled Wave 3 target match after certified evidence audit",
        "audited_input": {
            "a4_certification": a4_output,
            "baseline_deep_scan": baseline_output,
            "repair_overlay": repair_output,
            "exclusion_rule": "A4 is authoritative for admissibility. Exclude any evidence A4 downgraded, rejected, unresolved or collection-restricted."
        },
        "target_terms": spec.get("target_terms", {}),
        "audit_gate_reason": audit_gate_reason,
        "output_contract": {
            "format": "compact_json_only",
            "required_keys": ["overall_state", "confidence", "dimensions", "excluded_evidence_ids", "unresolved", "contradictions"],
            "dimension_shape": {
                "state": "OBSERVED|OBSERVED_WITH_UNRESOLVED_SPECIFICITY|NOT_FOUND_AFTER_PROTOCOL|UNRESOLVED|CONTRADICTORY",
                "matched_terms": "flat string list, max 6",
                "evidence_ids": "flat admissible evidence id list, max 5",
                "confidence": "0-100",
                "unresolved_specificity": "flat string list, max 3"
            },
            "forbidden": ["term-by-term objects", "per-term evidence maps", "long unmatched term lists", "repeated evidence ids", "economic inference", "benchmark selection"]
        },
        "constraints": [
            "A5 must treat A4 certification as authoritative",
            "use A3 only for granular term-to-evidence mapping",
            "never resurrect excluded evidence",
            "for each D1-D5 return one compact dimension object only",
            "matched_terms must be a flat list; evidence_ids must be a flat list",
            "do not enumerate every missing synonym; summarize unresolved specificity only when material",
            "map only supplied D1-D5 target definitions",
            "no benchmark selection",
            "no economic inference",
            "preserve unresolved and contradiction states",
            "return complete valid JSON before optional detail"
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
            "audit_gate_reason": audit_gate_reason,
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
