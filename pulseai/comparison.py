"""
PulseAI Backend Comparison Engine
---------------------------------

Executes identical experiments across multiple compute
backends and produces normalized comparison results.

Responsibilities:
- Execute experiments per backend
- Ensure fair comparison
- Normalize outputs
- Rank hardware efficiency
- Generate final recommendation input
"""

from typing import Dict, List, Any

from pulseai.orchestrator import Orchestrator
from pulseai.analyzer import analyze
from pulseai.backends.registry import get_backend
from pulseai.recommender import recommend_from_comparison


# ============================================================
# Validation
# ============================================================

def _validate_backends(backends: List[str]):
    if not backends:
        raise ValueError("No backends provided for comparison")

    if len(backends) < 2:
        raise ValueError(
            "Comparison requires at least two backends"
        )


# ============================================================
# Backend Execution
# ============================================================

def _run_backend(
    workload,
    backend_name: str,
    runs: int,
    warmup: int,
) -> Dict[str, Any]:
    """
    Execute profiling experiment on a single backend.
    """

    print(f"[PulseAI] Executing backend: {backend_name}")

    backend = get_backend(backend_name)

    orchestrator = Orchestrator(
        workload=workload,
        backend=backend,
        runs=runs,
        warmup=warmup,
    )

    raw_runs = orchestrator.execute()
    analysis = analyze(raw_runs)

    return {
        "backend": backend_name,
        "raw_runs": raw_runs,
        "analysis": analysis,
    }


# ============================================================
# Ranking Logic
# ============================================================

def _rank_backends(
    backend_results: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Rank backends across multiple dimensions.
    """

    ranking = {}

    for backend, result in backend_results.items():
        metrics = result["analysis"]

        ranking[backend] = {
            "efficiency": metrics["efficiency_score"],
            "throughput": metrics["throughput_tokens_per_sec"],
            "stability": metrics["stability_score"],
            "energy": metrics["energy_per_1k_tokens_proxy"],
        }

    return ranking


# ============================================================
# Public Comparison API
# ============================================================

def compare_backends(
    workload,
    backend_names: List[str],
    runs: int,
    warmup: int,
) -> Dict[str, Any]:
    """
    Run full backend comparison experiment.

    Flow:
        backend → orchestrator → analyzer
                 ↓
        normalized comparison
                 ↓
        recommendation
    """

    _validate_backends(backend_names)

    backend_results: Dict[str, Dict[str, Any]] = {}

    # --------------------------------------------------------
    # Execute experiments
    # --------------------------------------------------------
    for backend_name in backend_names:
        result = _run_backend(
            workload,
            backend_name,
            runs,
            warmup,
        )

        backend_results[backend_name] = result

    # --------------------------------------------------------
    # Ranking Summary
    # --------------------------------------------------------
    ranking = _rank_backends(backend_results)

    # --------------------------------------------------------
    # Final Recommendation
    # --------------------------------------------------------
    final_recommendation = recommend_from_comparison(
        backend_results
    )

    # --------------------------------------------------------
    # Structured Output
    # --------------------------------------------------------
    return {
        "comparison_type": "heterogeneous_backend",
        "tested_backends": backend_names,
        "backend_results": backend_results,
        "ranking": ranking,
        "final_recommendation": final_recommendation,
    }