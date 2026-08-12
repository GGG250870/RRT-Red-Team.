import json
import sys
from pathlib import Path
from typing import Dict, Any, List

ALLOWED_LEVELS = {0, 1, 2, 3}
POSITIVE_STATES = {"VERIFICATO", "VERIFICATO_WEB", "PUBBLICO"}
ZERO_STATE = "NOT_FOUND_AFTER_PROTOCOL"
BLOCKING_STATES = {"COLLECTION_RESTRICTED", "INSUFFICIENT", "CONTRADICTORY", "ENTITY_AMBIGUOUS", "UNRESOLVED"}
REQUIRED = {"dimension", "level", "evidence", "source_url", "data_state", "scope", "observed_at"}


def validate_cell(company: str, target: str, cell: Dict[str, Any], expected_dimensions: List[str]):
    issues=[]
    obs=cell.get("observations", [])
    dims=[]
    levels=[]
    for idx,o in enumerate(obs):
        missing=REQUIRED-set(o)
        if missing:
            issues.append(("ERROR",company,target,f"observation[{idx}] missing={sorted(missing)}"))
        dim=o.get("dimension")
        if dim:
            dims.append(dim)
        level=o.get("level")
        state=o.get("data_state")
        if level not in ALLOWED_LEVELS:
            issues.append(("ERROR",company,target,f"observation[{idx}] invalid level"))
        else:
            levels.append(level)
        if level == 0 and state != ZERO_STATE:
            issues.append(("ERROR",company,target,f"{dim}: zero without {ZERO_STATE}"))
        if isinstance(level,int) and level > 0 and state not in POSITIVE_STATES:
            issues.append(("ERROR",company,target,f"{dim}: positive level with non-positive state {state}"))
        if state in BLOCKING_STATES:
            issues.append(("ERROR",company,target,f"{dim}: blocking state {state}"))
        if not str(o.get("source_url","")).startswith(("http://","https://")):
            issues.append(("ERROR",company,target,f"{dim}: invalid source_url"))
        if not str(o.get("scope","")).strip():
            issues.append(("ERROR",company,target,f"{dim}: missing scope"))

    duplicate=sorted({d for d in dims if dims.count(d)>1})
    missing_dims=[d for d in expected_dimensions if d not in dims]
    unexpected=[d for d in dims if d not in expected_dimensions]
    if duplicate:
        issues.append(("ERROR",company,target,f"duplicate dimensions={duplicate}"))
    if missing_dims:
        issues.append(("ERROR",company,target,f"missing dimensions={missing_dims}"))
    if unexpected:
        issues.append(("ERROR",company,target,f"unexpected dimensions={unexpected}"))

    pre_score_issues = list(issues)
    structurally_complete = not missing_dims and not duplicate and not unexpected and len(levels)==len(expected_dimensions)
    score_is_allowed = structurally_complete and not pre_score_issues
    if score_is_allowed:
        expected=round(sum(levels)/(len(expected_dimensions)*3)*100)
        if expected != cell.get("normalized_0_100"):
            issues.append(("ERROR",company,target,f"score mismatch {cell.get('normalized_0_100')} != {expected}"))
        if cell.get("status") not in (None, "PASS"):
            issues.append(("ERROR",company,target,f"status mismatch {cell.get('status')} != PASS"))
    else:
        if cell.get("normalized_0_100") is not None:
            issues.append(("ERROR",company,target,"blocked target must not produce normalized_0_100"))
        if cell.get("status") == "PASS":
            issues.append(("ERROR",company,target,"status PASS is invalid for blocked target"))

    expected_coverage=round((len(expected_dimensions)-len(missing_dims))/max(len(expected_dimensions),1),3)
    if "coverage_ratio" in cell and cell.get("coverage_ratio") != expected_coverage:
        issues.append(("ERROR",company,target,f"coverage mismatch {cell.get('coverage_ratio')} != {expected_coverage}"))
    return issues


def validate(path: str, target_master_path: str):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    target_master=json.loads(Path(target_master_path).read_text(encoding="utf-8"))
    issues=[]
    for company in data["companies"]:
        for target, cell in company["targets"].items():
            expected_dimensions=target_master[target]["dimensions"]
            issues.extend(validate_cell(company["company"],target,cell,expected_dimensions))
    return issues

if __name__=="__main__":
    issues=validate(sys.argv[1],sys.argv[2])
    for x in issues:
        print(*x,sep=" | ")
    sys.exit(1 if any(x[0]=="ERROR" for x in issues) else 0)
