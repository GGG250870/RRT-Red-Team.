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

    provider = LLMProvider(dry_run=False)
    readiness = provider.readiness()
    checks.update(readiness)

    try:
        registry = json.loads((runtime / "agent_registry.json").read_text(encoding="utf-8"))
        agents = registry.get("agents") or registry.get("roles") or {}
        checks["registry_has_9_agents"] = len(agents) == 9
    except Exception:
        checks["registry_has_9_agents"] = False

    try:
        web_tools = provider._tools_for_agent("A1_DISCOVERY", {"official_domain": "https://example.com/"})
        checks["web_search_routing_ready"] = bool(web_tools and web_tools[0].get("type") == "web_search")
        checks["web_domain_filter_ready"] = bool(web_tools and web_tools[0].get("filters",{}).get("allowed_domains") == ["example.com"])
    except Exception:
        checks["web_search_routing_ready"] = False
        checks["web_domain_filter_ready"] = False

    status = "PASS" if all(bool(v) for v in checks.values()) else "BLOCKED"
    print(json.dumps({"status": status, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
