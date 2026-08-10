import json
import tempfile
from pathlib import Path

from cost_control import BudgetPolicy, check_call_budget, estimate_cost_usd
from granularity_loop import LoopPolicy, should_continue
from llm_provider import LLMProvider
from state_store import StateStore


def test_cost_control():
    assert estimate_cost_usd("gpt-5.6-luna", 1_000_000, 0) == 1.0
    ok, _ = check_call_budget(0.01, BudgetPolicy(per_call_usd=0.25, per_case_usd=2.0, per_run_usd=10.0))
    assert ok
    ok, _ = check_call_budget(0.30, BudgetPolicy(per_call_usd=0.25, per_case_usd=2.0, per_run_usd=10.0))
    assert not ok


def test_loop_controller():
    cont, reason = should_continue(3, False, 4, 2, LoopPolicy(max_iterations=3))
    assert cont is False and reason == "MAX_ITERATIONS"
    cont, reason = should_continue(1, True, 2, 1)
    assert cont is False and reason == "TERMINAL_STATE"
    cont, reason = should_continue(1, False, 0, 0)
    assert cont is False and reason == "DIMINISHING_RETURNS"


def test_state_store_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "test.sqlite"
        s = StateStore(db)
        task = {
            "task_id": "T1",
            "case_id": "C1",
            "agent_id": "A1_DISCOVERY",
            "stage": "DISCOVERY",
            "payload": {"x": 1},
            "status": "PENDING",
        }
        s.enqueue(task)
        claimed = s.claim_next("A1_DISCOVERY")
        assert claimed and claimed["task_id"] == "T1"
        s.complete("T1", "A1_DISCOVERY", "C1", {"ok": True})
        outputs = s.outputs_for_case("C1")
        assert outputs == [{"ok": True}]
        assert s.stats().get("PASS") == 1


def test_web_tool_routing():
    p = LLMProvider(dry_run=True)
    tools = p._tools_for_agent("A1_DISCOVERY", {"official_domain": "https://www.example.com/"})
    assert tools and tools[0]["type"] == "web_search"
    assert tools[0]["filters"]["allowed_domains"] == ["example.com"]
    assert p._tools_for_agent("A7_RED_TEAM", {"official_domain": "https://www.example.com/"}) == []


def main():
    test_cost_control()
    test_loop_controller()
    test_state_store_roundtrip()
    test_web_tool_routing()
    print(json.dumps({"status": "PASS", "tests": 4}))


if __name__ == "__main__":
    main()
