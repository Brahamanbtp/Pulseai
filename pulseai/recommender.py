"""
PulseAI Recommendation Engine
-----------------------------

Generates explainable, non-authoritative backend recommendations
based on analyzed efficiency, performance, and stability metrics.

Design Principles:
- Never auto-control execution
- Provide explainable reasoning
- Hardware-agnostic logic
- Deterministic output
"""

from typing import Dict, Any


# ============================================================
# Threshold Configuration
# ============================================================

EFFICIENCY_WEIGHT = 0.5
PERFORMANCE_WEIGHT = 0.3
STABILITY_WEIGHT = 0.2

MIN_STABILITY_ACCEPTABLE = 0.6


# ============================================================
# Internal Scoring
# ============================================================

def _score_backend(metrics: Dict[str, Any]) -> float:
    """
    Compute weighted backend score.

    Higher score = better overall backend choice.
    """

    efficiency = metrics.get("efficiency_score", 0.0)
    throughput = metrics.get("throughput_tokens_per_sec", 0.0)
    stability = metrics.get("stability_score", 0.0)

    score = (
        efficiency * EFFICIENCY_WEIGHT
        + throughput * PERFORMANCE_WEIGHT
        + stability * STABILITY_WEIGHT
    )

    return score


# ============================================================
# Reason Generator
# ============================================================

def _build_reason(metrics: Dict[str, Any], mode: str) -> str:
    """
    Generate human-readable justification.
    """

    efficiency = metrics["efficiency_score"]
    energy = metrics["energy_per_1k_tokens_proxy"]
    stability = metrics["stability_score"]

    if mode == "sustainability":
        return (
            f"Selected for superior efficiency "
            f"(score={efficiency:.4f}) and lower "
            f"energy usage ({energy:.2f}/1K tokens)."
        )

    if mode == "performance":
        return (
            "Selected for higher throughput despite "
            "increased energy utilization."
        )

    if stability < MIN_STABILITY_ACCEPTABLE:
        return (
            "Backend shows unstable execution; "
            "recommend cautious deployment."
        )

    return "Balanced efficiency and performance characteristics."


# ============================================================
# Single Backend Recommendation
# ============================================================

def recommend_backend(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend operational mode for a single backend run.
    """

    efficiency = analysis["efficiency_score"]
    stability = analysis["stability_score"]

    # Sustainability-first decision
    if efficiency > 0 and stability >= MIN_STABILITY_ACCEPTABLE:
        mode = "sustainability"
        backend = "CPU"

    else:
        mode = "performance"
        backend = "GPU"

    rationale = _build_reason(analysis, mode)

    return {
        "recommended_backend": backend,
        "mode": mode,
        "confidence": round(stability, 3),
        "rationale": rationale,
    }


# ============================================================
# Multi-Backend Recommendation
# ============================================================

def recommend_from_comparison(
    backend_results: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Select best backend among multiple candidates.
    """

    scored = {}

    for backend, result in backend_results.items():
        metrics = result["analysis"]
        scored[backend] = _score_backend(metrics)

    best_backend = max(scored, key=scored.get)

    best_metrics = backend_results[best_backend]["analysis"]

    recommendation = {
        "recommended_backend": best_backend,
        "mode": _derive_mode(best_metrics),
        "confidence": round(best_metrics["stability_score"], 3),
        "scores": scored,
        "rationale": _build_reason(
            best_metrics,
            _derive_mode(best_metrics),
        ),
    }

    return recommendation


# ============================================================
# Mode Selection Logic
# ============================================================

def _derive_mode(metrics: Dict[str, Any]) -> str:
    """
    Determine operational preference.
    """

    energy = metrics["energy_per_1k_tokens_proxy"]
    stability = metrics["stability_score"]

    if stability < MIN_STABILITY_ACCEPTABLE:
        return "experimental"

    if energy < 100:
        return "sustainability"

    return "performance"