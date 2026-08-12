import os
from dataclasses import dataclass
from typing import Optional


DEFAULT_MODEL_PRICES = {
    "gpt-5.6-luna": {"input_per_m": 1.0, "output_per_m": 6.0},
    "gpt-5.6-terra": {"input_per_m": 2.5, "output_per_m": 15.0},
    "gpt-5.6-sol": {"input_per_m": 5.0, "output_per_m": 30.0},
}


@dataclass
class BudgetPolicy:
    per_call_usd: float = float(os.getenv("RRT_BUDGET_PER_CALL_USD", "0.25"))
    per_case_usd: float = float(os.getenv("RRT_BUDGET_PER_CASE_USD", "2.00"))
    per_run_usd: float = float(os.getenv("RRT_BUDGET_PER_RUN_USD", "10.00"))


def usd_to_eur(usd: float) -> float:
    rate = float(os.getenv("RRT_USD_EUR_RATE", "1.00"))
    return round(max(usd or 0.0, 0.0) * rate, 6)


def format_eur(usd: float) -> str:
    return f"EUR {usd_to_eur(usd):.4f}"


def estimate_cost_usd(model: str, input_tokens: int = 0, output_tokens: int = 0) -> float:
    price = DEFAULT_MODEL_PRICES.get(model)
    if not price:
        return 0.0
    return (
        (max(input_tokens or 0, 0) / 1_000_000.0) * price["input_per_m"]
        + (max(output_tokens or 0, 0) / 1_000_000.0) * price["output_per_m"]
    )


def check_call_budget(estimated_usd: float, policy: Optional[BudgetPolicy] = None):
    policy = policy or BudgetPolicy()
    if estimated_usd > policy.per_call_usd:
        return False, f"Estimated call cost ${estimated_usd:.4f} exceeds per-call budget ${policy.per_call_usd:.4f}"
    return True, "PASS"
