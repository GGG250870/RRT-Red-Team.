#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "vertical_profiles"
SCHEMA_PATH = PROFILE_DIR / "vertical_profile_schema_v1.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_non_empty_list(profile, key, errors):
    value = profile.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{profile.get('profile_id', '<unknown>')}: {key} must be a non-empty list")


def validate_profile(path, required_keys):
    profile = load_json(path)
    errors = []
    for key in required_keys:
        if key not in profile:
            errors.append(f"{path.name}: missing required key {key}")
    if profile.get("status") not in {"active", "draft", "disabled"}:
        errors.append(f"{path.name}: invalid status {profile.get('status')!r}")
    if profile.get("status") == "active" and not profile.get("existing_runtime_profile_keys", {}).get("active_gate"):
        errors.append(f"{path.name}: active profile must reference an active_gate")
    for key in [
        "target_segments",
        "entity_identity_rules",
        "observable_customer_path_signals",
        "comparator_rules",
        "red_team_falsification_prompts",
        "signal_promotion_rules",
    ]:
        assert_non_empty_list(profile, key, errors)
    source_policy = profile.get("source_policy", {})
    for key in ["required_sources", "allowed_sources", "disallowed_collection"]:
        if not isinstance(source_policy.get(key), list) or not source_policy.get(key):
            errors.append(f"{path.name}: source_policy.{key} must be a non-empty list")
    language = profile.get("client_language_constraints", {})
    if not language.get("safe_framing"):
        errors.append(f"{path.name}: client_language_constraints.safe_framing is required")
    if not isinstance(language.get("forbidden_phrases"), list) or not language.get("forbidden_phrases"):
        errors.append(f"{path.name}: client_language_constraints.forbidden_phrases must be non-empty")
    dashboard = profile.get("dashboard_contract", {})
    if "vertical" not in dashboard.get("required_columns", []):
        errors.append(f"{path.name}: dashboard_contract.required_columns must include vertical")
    if dashboard.get("default_gate_state") not in {"NOT_EVALUATED", "DRAFT_PROFILE"}:
        errors.append(f"{path.name}: dashboard_contract.default_gate_state must be NOT_EVALUATED or DRAFT_PROFILE")
    return errors


def main():
    schema = load_json(SCHEMA_PATH)
    required = schema["required_top_level_keys"]
    errors = []
    profiles = sorted(
        p for p in PROFILE_DIR.glob("*.json")
        if p.name != "vertical_profile_schema_v1.json"
    )
    if not profiles:
        errors.append("No vertical profile files found")
    for path in profiles:
        errors.extend(validate_profile(path, required))
    if errors:
        print("VERTICAL_PROFILE_VALIDATION_FAIL")
        for error in errors:
            print(error)
        return 1
    print(json.dumps({"status": "PASS", "profiles": len(profiles)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
