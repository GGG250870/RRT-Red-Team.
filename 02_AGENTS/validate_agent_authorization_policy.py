#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
POLICY_PATH = ROOT / "RRT_AGENT_AUTHORIZATION_POLICY_V1.json"
ROLES_PATH = ROOT / "RRT_MULTI_AGENT_ROLES_V1.json"
ORCH_PATH = ROOT / "RRT_MULTI_AGENT_ORCHESTRATION_V1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    policy = load(POLICY_PATH)
    roles = load(ROLES_PATH).get("roles", {})
    orchestration = load(ORCH_PATH)
    errors = []

    required_clusters = {
        "discovery_evidence_collection",
        "entity_resolution",
        "comparator_research",
        "red_team_challenger",
        "dossier_report_preparation",
        "human_approval_release",
    }
    clusters = policy.get("agent_clusters", {})
    missing_clusters = required_clusters - set(clusters)
    if missing_clusters:
        errors.append(f"missing clusters: {sorted(missing_clusters)}")

    for cluster_name, cluster in clusters.items():
        agents = cluster.get("agents", [])
        if not agents:
            errors.append(f"{cluster_name}: agents must be non-empty")
        for agent_id in agents:
            if agent_id not in roles:
                errors.append(f"{cluster_name}: unknown agent {agent_id}")
        if not cluster.get("must_output"):
            errors.append(f"{cluster_name}: must_output must be non-empty")
        if not cluster.get("forbidden"):
            errors.append(f"{cluster_name}: forbidden must be non-empty")

    handoff_fields = set(policy.get("handoff_required_fields", []))
    for required in ["case_id", "vertical_profile_id", "provenance_refs", "state", "cost_eur_actual", "requires_human_review"]:
        if required not in handoff_fields:
            errors.append(f"handoff missing required field {required}")

    forbidden = set(policy.get("global_forbidden_actions", []))
    for required in ["contact_business", "submit_forms", "browse_behind_login", "invent_evidence", "release_outreach_without_human_approval"]:
        if required not in forbidden:
            errors.append(f"global forbidden missing {required}")

    controls = policy.get("cost_consent_controls", {})
    if controls.get("live_agent_env_required") != "RRT_AGENT_TEAM_APPROVAL=I_APPROVE_AGENT_TEAM_LIVE_RUN":
        errors.append("live agent approval env mismatch")
    if controls.get("currency_for_user") != "EUR":
        errors.append("user currency must be EUR")

    release_rule = policy.get("signal_release_rule", [])
    for required in ["red_team_survives", "qa_ready_for_human_review", "explicit_human_approval"]:
        if required not in release_rule:
            errors.append(f"signal release rule missing {required}")

    if orchestration.get("human_review") != "Mandatory for Opportunity Signal Candidate.":
        errors.append("orchestration human review sentence changed unexpectedly")

    if errors:
        print("AGENT_AUTHORIZATION_POLICY_FAIL")
        for error in errors:
            print(error)
        return 1
    print(json.dumps({"status": "PASS", "clusters": len(clusters), "roles": len(roles)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
