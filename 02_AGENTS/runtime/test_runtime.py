import json
import tempfile
from pathlib import Path

from cost_control import BudgetPolicy, check_call_budget, estimate_cost_usd
from granularity_loop import LoopPolicy, should_continue
from llm_provider import LLMProvider, _normalize_url, MAX_OUTPUT_BY_AGENT
from state_store import StateStore
from wave2_a3_runner import load_deep_scan_spec


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


def test_url_normalization():
    dirty = "[https://www.studio-gioia.it/](https://www.studio-gioia.it/)"
    assert _normalize_url(dirty) == "https://www.studio-gioia.it/"
    assert _normalize_url("https://www.studio-gioia.it/") == "https://www.studio-gioia.it/"


def test_output_policy():
    assert MAX_OUTPUT_BY_AGENT["A1_DISCOVERY"] >= 2000
    assert MAX_OUTPUT_BY_AGENT["A2_ENTITY_SCOPE"] >= 1500
    assert MAX_OUTPUT_BY_AGENT["A3_DEEP_SCAN"] >= 2000


def test_deep_scan_spec_loading():
    runtime = Path(__file__).resolve().parent
    repo_root = runtime.parents[1]
    spec = load_deep_scan_spec(repo_root)
    targets = spec.get("target_terms", {})
    assert set(targets.keys()) == {"D1", "D2", "D3", "D4", "D5"}
    assert spec.get("adaptive_query_budget")
    assert spec.get("saturation_pass_conditions")


def test_wave3_dependency_guard():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "test.sqlite"
        s = StateStore(db)
        assert [o for o in s.outputs_for_case("NOCASE") if o.get("agent_id") == "A3_DEEP_SCAN"] == []


def main():
    tests = [
        test_cost_control,
        test_loop_controller,
        test_state_store_roundtrip,
        test_web_tool_routing,
        test_url_normalization,
        test_output_policy,
        test_deep_scan_spec_loading,
        test_wave3_dependency_guard,
    ]
    for test in tests:
        test()
    print(json.dumps({"status": "PASS", "tests": len(tests)}))


if __name__ == "__main__":
    main()
