import json
import sys
from pathlib import Path

from llm_provider import LLMProvider


def main():
    runtime = Path(__file__).resolve().parent
    checks = {
        "worker_exists": (runtime / "worker.py").exists(),
        "registry_exists": (runtime / "agent_registry.json").exists(),
        "state_store_exists": (runtime / "state_store.py").exists(),
        "provider_exists": (runtime / "llm_provider.py").exists(),
        "cost_control_exists": (runtime / "cost_control.py").exists(),
        "granularity_loop_exists": (runtime / "granularity_loop.py").exists(),
    }

    readiness = LLMProvider(dry_run=False).readiness()
    checks.update(readiness)

    try:
        registry = json.loads((runtime / "agent_registry.json").read_text(encoding="utf-8"))
        agents = registry.get("agents") or registry.get("roles") or {}
        checks["registry_has_9_agents"] = len(agents) == 9
    except Exception:
        checks["registry_has_9_agents"] = False

    status = "PASS" if all(bool(v) for v in checks.values()) else "BLOCKED"
    print(json.dumps({"status": status, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
