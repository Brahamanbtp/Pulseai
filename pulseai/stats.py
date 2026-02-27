"""
PulseAI Statistical Utilities
-----------------------------

Provides deterministic statistical aggregation utilities
used across PulseAI analysis pipelines.

Design Goals:
- Stable results across runs
- Safe handling of small datasets
- Benchmark-grade aggregation
- Backend-comparable metrics
"""

from typing import List, Dict
import statistics
import math


# ============================================================
# Safe Helpers
# ============================================================

def _safe_mean(values: List[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _safe_median(values: List[float]) -> float:
    return statistics.median(values) if values else 0.0


def _safe_std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _safe_min(values: List[float]) -> float:
    return min(values) if values else 0.0


def _safe_max(values: List[float]) -> float:
    return max(values) if values else 0.0


# ============================================================
# Core Aggregation
# ============================================================

def aggregate(values: List[float]) -> Dict[str, float]:
    """
    Aggregate numeric values into benchmark-ready statistics.

    Returns:
        {
            mean,
            median,
            stddev,
            min,
            max,
            coefficient_of_variation,
            confidence_95
        }
    """

    if not values:
        raise ValueError("Cannot aggregate empty value list")

    mean_val = _safe_mean(values)
    std_val = _safe_std(values)

    # Coefficient of Variation
    cov = std_val / mean_val if mean_val != 0 else 0.0

    # 95% confidence interval approximation
    confidence = _confidence_interval_95(
        mean_val,
        std_val,
        len(values)
    )

    return {
        "mean": mean_val,
        "median": _safe_median(values),
        "stddev": std_val,
        "min": _safe_min(values),
        "max": _safe_max(values),
        "coefficient_of_variation": cov,
        "confidence_95": confidence,
        "samples": len(values),
    }


# ============================================================
# Confidence Interval
# ============================================================

def _confidence_interval_95(
    mean: float,
    stddev: float,
    n: int
) -> float:
    """
    Compute 95% confidence interval width.

    Uses normal approximation:
        1.96 * (σ / sqrt(n))
    """

    if n < 2:
        return 0.0

    return 1.96 * (stddev / math.sqrt(n))


# ============================================================
# Dataset Comparison Utilities
# ============================================================

def relative_improvement(
    baseline: float,
    candidate: float
) -> float:
    """
    Percentage improvement between two metrics.

    Positive → improvement
    Negative → regression
    """

    if baseline == 0:
        return 0.0

    return ((candidate - baseline) / baseline) * 100.0


def normalize(values: List[float]) -> List[float]:
    """
    Normalize values to [0,1] range.
    Useful for backend comparison scoring.
    """

    if not values:
        return values

    min_v = min(values)
    max_v = max(values)

    if max_v == min_v:
        return [1.0 for _ in values]

    return [(v - min_v) / (max_v - min_v) for v in values]


# ============================================================
# Stability Metric
# ============================================================

def stability_from_std(mean: float, stddev: float) -> float:
    """
    Convert variance into stability score.

    Stability ∈ [0,1]
    Higher is better.
    """

    if mean == 0:
        return 0.0

    cov = stddev / mean
    stability = 1.0 - cov

    return max(0.0, min(1.0, stability))