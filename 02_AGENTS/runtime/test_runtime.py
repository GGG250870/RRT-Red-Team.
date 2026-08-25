import json
import tempfile
from pathlib import Path

from cost_control import BudgetPolicy, check_call_budget, estimate_cost_usd, format_eur, usd_to_eur
from granularity_loop import LoopPolicy, should_continue
from llm_provider import LLMProvider, _normalize_url, MAX_OUTPUT_BY_AGENT
from state_store import StateStore
from wave2_a3_runner import load_deep_scan_spec
from wave3_a4_a5_runner import extract_a3_output, is_repair_output, audit_gate_decision
from wave4_7_runner import stage_gate


def test_cost_control():
    assert estimate_cost_usd("gpt-5.6-luna", 1_000_000, 0) == 1.0
    assert usd_to_eur(1.23) == 1.23
    assert format_eur(1.23) == "EUR 1.2300"
    ok, _ = check_call_budget(0.01, BudgetPolicy(per_call_usd=0.25, per_case_usd=2.0, per_run_usd=10.0))
    assert ok
    ok, _ = check_call_budget(0.30, BudgetPolicy(per_call_usd=0.25, per_case_usd=2.0, per_run_usd=10.0))
    assert not ok


def test_live_agent_team_requires_explicit_approval():
    from orchestrator import Orchestrator

    with tempfile.TemporaryDirectory() as td:
        runtime = Path(td)
        (runtime / "agent_registry.json").write_text('{"agents": {}}', encoding="utf-8")
        orch = Orchestrator(runtime)
        result = orch.run_agents_parallel([], live=True, case_id="C1")
        assert result["status"] == "BLOCKED"
        assert result["reason"] == "AGENT_TEAM_REQUIRES_EXPLICIT_USER_APPROVAL"


def test_prescreen_primary_intelligence_sources_cover_all_verticals():
    import importlib.util

    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "00_PRE_SCREEN" / "build_batch.py"
    spec = importlib.util.spec_from_file_location("build_batch", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    required_groups = {"google", "review_portals", "social", "public_financials"}
    for vertical in module.PRIMARY_PORTALS_BY_VERTICAL:
        sources = module.PRIMARY_INTELLIGENCE_SOURCES_BY_VERTICAL.get(vertical)
        assert sources, vertical
        assert required_groups.issubset(sources), vertical
        assert "google_business_profile" in sources["google"]
        assert "google_reviews" in sources["google"]
        assert "registroimprese.it" in sources["public_financials"]


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


def test_wave3_persisted_a3_extraction():
    baseline = {
        "agent_id": "A3_DEEP_SCAN",
        "output": {"dimensions": {"D1": {"state": "PASS"}}, "saturation_state": "SATURATED"},
    }
    repair = {
        "agent_id": "A3_DEEP_SCAN",
        "output": {"repaired_evidence": [{"target": "E05", "state": "FOUND"}], "execution_trace": {"pages_checked": []}},
    }
    assert extract_a3_output(baseline).get("dimensions", {}).get("D1", {}).get("state") == "PASS"
    assert not is_repair_output(baseline)
    assert is_repair_output(repair)


def test_wave3_nonblocking_restrictions_gate():
    a4 = {
        "verdict": "DOWNGRADE",
        "overall_state": "COLLECTION_RESTRICTED",
        "dimensions": {
            "D1": {"state": "PASS", "note": "supporto ufficiale"},
            "D2": {"state": "PASS", "note": "supporto ufficiale"},
            "D3": {"state": "PASS", "note": "supporto diretto"},
            "D4": {"state": "DOWNGRADE", "note": "Supporto generale diretto disponibile, E08 resta non verificabile."},
            "D5": {"state": "DOWNGRADE", "note": "E09-E10 restano validi; E11 resta limitata."},
        },
        "downgraded_evidence_ids": ["E08", "E11"],
        "unresolved": [{"item": "E08"}, {"item": "E11"}],
    }
    ok, reason = audit_gate_decision(a4)
    assert ok is True
    assert reason == "PASS_WITH_NONBLOCKING_COLLECTION_RESTRICTIONS"


def test_wave4_7_stage_gates():
    ok, reason = stage_gate("A6_BENCHMARK", {
        "overall_state": "PASS",
        "benchmarks": [{"id": "B1"}],
        "fit_basis": [{"benchmark_id": "B1", "basis": "same vertical and decision job"}],
        "contradictions": [],
    })
    assert ok and reason == "PASS"

    ok, reason = stage_gate("A6_BENCHMARK", {
        "overall_state": "UNRESOLVED",
        "benchmarks": [],
        "fit_basis": [],
        "contradictions": [],
    })
    assert not ok and reason == "A6_UNRESOLVED"

    ok, reason = stage_gate("A7_RED_TEAM", {"verdict": "FALSIFIED", "contradictions": []})
    assert not ok and reason == "A7_FALSIFIED"
    ok, reason = stage_gate("A7_RED_TEAM", {"verdict": "WEAK_SURVIVAL", "contradictions": []})
    assert ok and reason == "WEAK_SURVIVAL"
    ok, reason = stage_gate("A8_COMMERCIAL_GATE", {"signal_class": "WATCHLIST", "contradictions": []})
    assert ok and reason == "WATCHLIST"
    ok, reason = stage_gate("A8_COMMERCIAL_GATE", {"signal_class": "OPPORTUNITY_SIGNAL", "contradictions": []})
    assert not ok and reason == "A8_INVALID_SIGNAL_CLASS"
    ok, reason = stage_gate("A9_QA_ORCHESTRATOR", {"verdict": "READY_FOR_HUMAN_REVIEW", "contradictions": []})
    assert ok and reason == "READY_FOR_HUMAN_REVIEW"
    ok, reason = stage_gate("A9_QA_ORCHESTRATOR", {"verdict": "READY", "contradictions": []})
    assert ok and reason == "READY"


def test_agent_authorization_policy_contract():
    import importlib.util

    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "02_AGENTS" / "validate_agent_authorization_policy.py"
    spec = importlib.util.spec_from_file_location("validate_agent_authorization_policy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() == 0


def test_end_to_end_runner_contract():
    runtime = Path(__file__).resolve().parent
    runner = (runtime / "end_to_end_runner.py").read_text(encoding="utf-8")
    positions = [runner.index(token) for token in ["canary.py", "wave2_a3_runner.py", "wave3_a4_a5_runner.py", "wave4_7_runner.py"]]
    assert positions == sorted(positions)
    assert "--resume" in runner
    assert "current_run_status" in runner


def main():
    tests = [
        test_cost_control,
        test_live_agent_team_requires_explicit_approval,
        test_prescreen_primary_intelligence_sources_cover_all_verticals,
        test_loop_controller,
        test_state_store_roundtrip,
        test_web_tool_routing,
        test_url_normalization,
        test_output_policy,
        test_deep_scan_spec_loading,
        test_wave3_dependency_guard,
        test_wave3_persisted_a3_extraction,
        test_wave3_nonblocking_restrictions_gate,
        test_wave4_7_stage_gates,
        test_agent_authorization_policy_contract,
        test_end_to_end_runner_contract,
    ]
    for test in tests:
        test()
    print(json.dumps({"status": "PASS", "tests": len(tests)}))


if __name__ == "__main__":
    main()
