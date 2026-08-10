import argparse
import json
from pathlib import Path

from orchestrator import Orchestrator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--official-domain", required=True)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    runtime = Path(__file__).resolve().parent
    orch = Orchestrator(runtime)
    payload = {
        "company": args.company,
        "official_domain": args.official_domain,
        "purpose": "controlled canary for A1 Discovery and A2 Entity Scope only",
        "constraints": [
            "no scoring",
            "no benchmark selection",
            "no commercial conclusion",
            "do not invent missing facts",
        ],
    }
    orch.enqueue_case(args.case_id, payload)
    result = orch.run_agents_parallel(["A1_DISCOVERY", "A2_ENTITY_SCOPE"], live=args.live, case_id=args.case_id)
    print(json.dumps({"case_id": args.case_id, "result": result, "status": orch.status()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
