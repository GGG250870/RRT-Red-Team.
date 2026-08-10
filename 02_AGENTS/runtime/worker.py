import argparse
import json
import sys
from pathlib import Path

from llm_provider import LLMProvider
from state_store import StateStore


def load_registry(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Agent registry not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    agents = data.get("agents") or data.get("roles") or {}
    if not isinstance(agents, dict):
        raise ValueError("Registry must expose an 'agents' or 'roles' object")
    return agents


def build_system_prompt(agent_id: str, spec: dict):
    mission = spec.get("system_prompt") or spec.get("mission") or ""
    forbidden = spec.get("forbidden") or []
    outputs = spec.get("outputs") or []
    return (
        f"Agent: {agent_id}\n"
        f"Mission: {mission}\n"
        f"Forbidden: {json.dumps(forbidden, ensure_ascii=False)}\n"
        f"Expected outputs: {json.dumps(outputs, ensure_ascii=False)}\n"
        "Return JSON only. Never invent missing facts. Use explicit states such as "
        "UNRESOLVED, NOT_FOUND_AFTER_PROTOCOL, COLLECTION_RESTRICTED, CONTRADICTORY, BLOCKED."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    store = StateStore(args.db)
    agents = load_registry(args.registry)
    spec = agents.get(args.agent)
    if not spec:
        print(json.dumps({"status": "BLOCKED", "reason": f"Unknown agent {args.agent}"}))
        return 2

    task = store.claim_next(args.agent)
    if not task:
        print(json.dumps({"status": "IDLE", "agent_id": args.agent}))
        return 0

    try:
        payload = task.get("payload")
        if isinstance(payload, str):
            payload = json.loads(payload)
        provider = LLMProvider(dry_run=not args.live)
        result = provider.run(args.agent, build_system_prompt(args.agent, spec), payload or {})
        status = "PASS" if result.get("parse_status", "PASS") == "PASS" else "FAIL_JSON"
        store.complete(task["task_id"], args.agent, task["case_id"], result, status=status)
        print(json.dumps({"status": status, "agent_id": args.agent, "task_id": task["task_id"], "result": result}, ensure_ascii=False))
        return 0 if status == "PASS" else 3
    except Exception as e:
        store.fail(task["task_id"], args.agent, task["case_id"], str(e))
        print(json.dumps({"status": "FAIL", "agent_id": args.agent, "task_id": task["task_id"], "error": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
