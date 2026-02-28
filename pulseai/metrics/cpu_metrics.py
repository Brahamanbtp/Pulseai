"""
PulseAI CPU Metrics Collector
-----------------------------

Provides lightweight, non-privileged CPU telemetry
for AI workload profiling.

Design Goals:
- Cross-platform compatibility
- Low measurement overhead
- Deterministic snapshots
- Sampling-safe metrics
"""

from typing import Dict, Any
import psutil
import time


# ============================================================
# Internal Stabilization
# ============================================================

_INITIALIZED = False


def _initialize_cpu_monitor():
    """
    Stabilize psutil CPU measurement.

    First cpu_percent() call is unreliable,
    so we warm it once globally.
    """
    global _INITIALIZED

    if not _INITIALIZED:
        psutil.cpu_percent(interval=None)
        time.sleep(0.05)
        _INITIALIZED = True


# ============================================================
# Core Snapshot
# ============================================================

def snapshot_cpu() -> Dict[str, Any]:
    """
    Capture instantaneous CPU telemetry snapshot.

    Returns
    -------
    dict containing:
        cpu_percent
        per_core_percent
        memory_usage_mb
        memory_percent
        load_average
        timestamp
    """

    _initialize_cpu_monitor()

    virtual_mem = psutil.virtual_memory()

    try:
        load_avg = psutil.getloadavg()
    except Exception:
        load_avg = (None, None, None)

    snapshot = {
        "timestamp": time.time(),

        # Overall utilization
        "cpu_percent":
            psutil.cpu_percent(interval=None),

        # Per-core visibility
        "per_core_percent":
            psutil.cpu_percent(
                interval=None,
                percpu=True
            ),

        # Memory
        "memory_usage_mb":
            round(
                virtual_mem.used / (1024 * 1024),
                2
            ),

        "memory_percent":
            virtual_mem.percent,

        # System load
        "load_avg_1m": load_avg[0],
        "load_avg_5m": load_avg[1],
        "load_avg_15m": load_avg[2],
    }

    return snapshot


# ============================================================
# Lightweight Sampling Metric
# ============================================================

def cpu_utilization_only() -> float:
    """
    Fast CPU utilization read.

    Used in high-frequency samplers where
    minimal overhead is required.
    """

    _initialize_cpu_monitor()
    return psutil.cpu_percent(interval=None)


# ============================================================
# CPU Frequency Metrics
# ============================================================

def cpu_frequency() -> Dict[str, Any]:
    """
    Retrieve CPU frequency information.
    """

    freq = psutil.cpu_freq()

    if freq is None:
        return {
            "current_mhz": None,
            "min_mhz": None,
            "max_mhz": None,
        }

    return {
        "current_mhz": freq.current,
        "min_mhz": freq.min,
        "max_mhz": freq.max,
    }


# ============================================================
# Core Count Information
# ============================================================

def cpu_core_info() -> Dict[str, int]:
    """
    CPU topology information.
    """

    return {
        "physical_cores":
            psutil.cpu_count(logical=False),
        "logical_cores":
            psutil.cpu_count(logical=True),
    }