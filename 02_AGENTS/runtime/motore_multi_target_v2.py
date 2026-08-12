from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

ALLOWED_LEVELS = {0, 1, 2, 3}
SCORABLE_STATES = {
    "VERIFICATO", "VERIFICATO_WEB", "PUBBLICO",
    "NOT_FOUND_AFTER_PROTOCOL"
}
BLOCKING_STATES = {
    "COLLECTION_RESTRICTED", "INSUFFICIENT", "CONTRADICTORY",
    "ENTITY_AMBIGUOUS", "UNRESOLVED"
}

@dataclass
class Observation:
    dimension: str
    level: int
    evidence: str
    source_url: str
    data_state: str
    observed_at: str
    scope: str
    source_ref: Optional[str] = None

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.level not in ALLOWED_LEVELS:
            errors.append("Livello non ammesso")
        if not self.dimension.strip():
            errors.append("Dimensione mancante")
        if not self.evidence.strip():
            errors.append("Ogni osservazione deve avere evidenza o trace di assenza")
        if not self.source_url.startswith(("http://", "https://")):
            errors.append("Ogni osservazione deve avere una fonte URL valida")
        if not self.data_state.strip():
            errors.append("Ogni osservazione deve avere stato del dato")
        if not self.scope.strip():
            errors.append("Ogni osservazione deve avere scope")
        if self.level == 0 and self.data_state != "NOT_FOUND_AFTER_PROTOCOL":
            errors.append("Livello 0 ammesso solo con NOT_FOUND_AFTER_PROTOCOL")
        if self.level > 0 and self.data_state in BLOCKING_STATES:
            errors.append(f"Stato {self.data_state} non scorable con livello positivo")
        return errors


def evaluate_path(
    company: str,
    target: str,
    observations: List[Observation],
    expected_dimensions: List[str],
) -> Dict[str, Any]:
    issues: List[str] = []
    for idx, obs in enumerate(observations):
        for err in obs.validate():
            issues.append(f"observation[{idx}] {obs.dimension}: {err}")

    observed_dimensions = [o.dimension for o in observations]
    duplicates = sorted({d for d in observed_dimensions if observed_dimensions.count(d) > 1})
    missing = [d for d in expected_dimensions if d not in observed_dimensions]
    unexpected = [d for d in observed_dimensions if d not in expected_dimensions]

    if duplicates:
        issues.append(f"Dimensioni duplicate: {duplicates}")
    if unexpected:
        issues.append(f"Dimensioni inattese: {unexpected}")

    coverage_ratio = round(
        (len(expected_dimensions) - len(missing)) / max(len(expected_dimensions), 1), 3
    )

    blocking_states = sorted({o.data_state for o in observations if o.data_state in BLOCKING_STATES})
    score_allowed = not issues and not missing and not blocking_states

    levels = [o.level for o in observations if o.dimension in expected_dimensions]
    score = round(sum(levels) / (len(expected_dimensions) * 3) * 100) if score_allowed else None

    return {
        "company": company,
        "target": target,
        "status": "PASS" if score_allowed else "BLOCKED",
        "observations": [asdict(o) for o in observations],
        "expected_dimensions": expected_dimensions,
        "missing_dimensions": missing,
        "duplicate_dimensions": duplicates,
        "unexpected_dimensions": unexpected,
        "blocking_states": blocking_states,
        "coverage_ratio": coverage_ratio,
        "normalized_0_100": score,
        "issues": issues,
        "rule": (
            "Score ammesso solo con tutte le dimensioni terminali, scope valido e "
            "livello 0 accompagnato da NOT_FOUND_AFTER_PROTOCOL."
        ),
        "note": "Non misura qualità clinica, vendite reali, conversione o ROI."
    }
