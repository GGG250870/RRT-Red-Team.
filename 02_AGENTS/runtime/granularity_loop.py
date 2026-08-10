from dataclasses import dataclass


@dataclass
class LoopPolicy:
    max_iterations: int = 3
    max_unresolved_material: int = 1
    stop_on_terminal: bool = True


def should_continue(iteration: int, terminal_state: bool, unresolved_material: int, new_material_evidence: int, policy: LoopPolicy | None = None):
    policy = policy or LoopPolicy()
    if policy.stop_on_terminal and terminal_state:
        return False, "TERMINAL_STATE"
    if iteration >= policy.max_iterations:
        return False, "MAX_ITERATIONS"
    if unresolved_material <= policy.max_unresolved_material and new_material_evidence == 0:
        return False, "DIMINISHING_RETURNS"
    return True, "CONTINUE"
