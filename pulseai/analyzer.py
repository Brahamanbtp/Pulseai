"""
PulseAI Analyzer
----------------

Transforms raw experiment runs into normalized,
statistically valid efficiency insights.

Responsibilities:
- Aggregate multi-run metrics
- Remove noisy outliers
- Normalize performance
- Compute sustainability proxies
- Produce backend-comparable results
"""

from typing import List, Dict, Any
import statistics

from pulseai.config import (
    ENABLE_OUTLIER_FILTERING,
    OUTLIER_STD_THRESHOLD,
    ENERGY_NORMALIZATION_FACTOR,
)

from pulseai.stats import aggregate


# ============================================================
# Outlier Filtering
# ============================================================

def _filter_outliers(values: List[float]) -> List[float]:
    """
    Remove statistical outliers using std deviation threshold.
    """

    if len(values) < 3:
        return values

    mean = statistics.mean(values)
    std = statistics.stdev(values)

    if std == 0:
        return values

    filtered = [
        v for v in values
        if abs(v - mean) <= OUTLIER_STD_THRESHOLD * std
    ]

    return filtered if filtered else values


# ============================================================
# Derived Metrics
# ============================================================

def _compute_throughput(tokens_mean: float,
                        latency_mean: float) -> float:
    """
    Tokens processed per second.
    """
    if latency_mean == 0:
        return 0.0
    return tokens_mean / latency_mean


def _compute_efficiency(tokens_mean: float,
                        latency_mean: float,
                        utilization_mean: float) -> float:
    """
    Performance-per-utilization proxy.
    """

    if latency_mean == 0 or utilization_mean == 0:
        return 0.0

    return tokens_mean / (latency_mean * utilization_mean)


def _compute_energy_proxy(tokens_mean: float,
                          latency_mean: float,
                          utilization_mean: float) -> float:
    """
    Energy proxy normalized per 1K tokens.
    """

    if tokens_mean == 0:
        return 0.0

    energy = latency_mean * utilization_mean
    return (energy / tokens_mean) * ENERGY_NORMALIZATION_FACTOR


# ============================================================
# Stability Analysis
# ============================================================

def _stability_score(values: List[float]) -> float:
    """
    Measures runtime stability using coefficient of variation.
    Lower variance → higher stability.
    """

    if len(values) < 2:
        return 1.0

    mean = statistics.mean(values)
    std = statistics.stdev(values)

    if mean == 0:
        return 0.0

    cov = std / mean
    return max(0.0, 1.0 - cov)


# ============================================================
# Main Analyzer
# ============================================================

def analyze(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze experiment runs and compute normalized metrics.
    """

    if not runs:
        raise ValueError("No runs provided for analysis")

    durations = [r["duration"] for r in runs]
    tokens = [r["tokens"] for r in runs]
    cpu_util = [r["cpu_after"]["cpu_percent"] for r in runs]

    # ---------------------------------------------
    # Optional Outlier Filtering
    # ---------------------------------------------
    if ENABLE_OUTLIER_FILTERING:
        durations = _filter_outliers(durations)
        tokens = _filter_outliers(tokens)
        cpu_util = _filter_outliers(cpu_util)

    # ---------------------------------------------
    # Statistical Aggregation
    # ---------------------------------------------
    latency_stats = aggregate(durations)
    token_stats = aggregate(tokens)
    cpu_stats = aggregate(cpu_util)

    latency_mean = latency_stats["mean"]
    token_mean = token_stats["mean"]
    cpu_mean = cpu_stats["mean"]

    # ---------------------------------------------
    # Derived Metrics
    # ---------------------------------------------
    throughput = _compute_throughput(
        token_mean,
        latency_mean,
    )

    efficiency_score = _compute_efficiency(
        token_mean,
        latency_mean,
        cpu_mean,
    )

    energy_per_1k_tokens = _compute_energy_proxy(
        token_mean,
        latency_mean,
        cpu_mean,
    )

    stability = _stability_score(durations)

    # ---------------------------------------------
    # Final Structured Output
    # ---------------------------------------------
    return {
        "latency_sec": latency_stats,
        "tokens": token_stats,
        "cpu_percent": cpu_stats,

        "throughput_tokens_per_sec": throughput,

        "efficiency_score": efficiency_score,

        "energy_per_1k_tokens_proxy":
            energy_per_1k_tokens,

        "stability_score": stability,

        "sample_size": len(runs),
    }