"""
PulseAI Time Utilities
----------------------

Provides high-precision, benchmark-safe timing utilities.

Design Goals
------------
- Monotonic timing (no clock drift)
- High resolution measurements
- Context-managed timing
- Deterministic duration tracking
"""

from typing import Callable, Any, Tuple
import time


# ==========================================================
# High Precision Clock
# ==========================================================

def now() -> float:
    """
    Return high-resolution monotonic timestamp.

    Uses perf_counter which is:
    - monotonic
    - system-clock independent
    - ideal for benchmarking
    """

    return time.perf_counter()


# ==========================================================
# Duration Measurement
# ==========================================================

def duration(start: float, end: float) -> float:
    """
    Compute elapsed duration safely.
    """

    elapsed = end - start

    if elapsed < 0:
        raise RuntimeError(
            "Negative duration detected. "
            "Clock inconsistency occurred."
        )

    return elapsed


# ==========================================================
# Function Timing
# ==========================================================

def time_function(
    fn: Callable[..., Any],
    *args,
    **kwargs
) -> Tuple[Any, float]:
    """
    Execute function and measure execution time.

    Returns
    -------
    result, elapsed_time
    """

    start = now()
    result = fn(*args, **kwargs)
    end = now()

    return result, duration(start, end)


# ==========================================================
# Timer Context Manager
# ==========================================================

class Timer:
    """
    Context manager for scoped timing.

    Example
    -------
        with Timer() as t:
            workload()

        print(t.elapsed)
    """

    def __init__(self):
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.elapsed: float = 0.0

    def __enter__(self):
        self.start_time = now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = now()
        self.elapsed = duration(
            self.start_time,
            self.end_time
        )


# ==========================================================
# Sleep Helper (Stable Sampling)
# ==========================================================

def precise_sleep(seconds: float):
    """
    Sleep helper designed for sampling loops.

    Prevents negative or zero sleep calls.
    """

    if seconds <= 0:
        return

    time.sleep(seconds)


# ==========================================================
# Timestamp Utilities
# ==========================================================

def unix_timestamp() -> float:
    """
    Wall-clock timestamp for logging/reporting.
    """

    return time.time()


def iso_timestamp() -> str:
    """
    ISO8601 formatted timestamp.
    """

    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime()
    )