from typing import Dict


def dq_score(flags: Dict[str, bool], weights: Dict[str, float]) -> float:
    score = 0.0
    total = sum(weights.values())
    if total == 0:
        return 0.0
    for name, weight in weights.items():
        score += (1.0 if flags.get(name, False) else 0.0) * weight
    return round(100.0 * score / total, 2)
