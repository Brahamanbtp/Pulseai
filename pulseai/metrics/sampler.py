"""
PulseAI Metric Sampler
----------------------

Real-time telemetry sampling engine used during workload
execution.

Responsibilities:
- Background metric collection
- CPU + GPU unified telemetry
- Low overhead sampling
- Thread-safe lifecycle
- Time-series generation
"""

from typing import List, Dict, Any
import threading
import time

from pulseai.config import METRIC_SAMPLE_INTERVAL_SEC
from pulseai.metrics.cpu_metrics import cpu_utilization_only
from pulseai.metrics.gpu_metrics import (
    gpu_available,
    gpu_utilization_only,
)


class MetricSampler:
    """
    Background telemetry sampler.

    Collects system utilization metrics while workload runs.
    """

    def __init__(
        self,
        interval: float = METRIC_SAMPLE_INTERVAL_SEC
    ):
        self.interval = interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        self.data: List[Dict[str, Any]] = []

    # ==========================================================
    # Sampling Loop
    # ==========================================================

    def _sample_loop(self):
        """
        Continuous sampling loop.
        """

        while self._running:

            timestamp = time.time()

            cpu_util = cpu_utilization_only()

            gpu_util = (
                gpu_utilization_only()
                if gpu_available()
                else 0.0
            )

            sample = {
                "timestamp": timestamp,
                "cpu_util_percent": cpu_util,
                "gpu_util_percent": gpu_util,
            }

            with self._lock:
                self.data.append(sample)

            time.sleep(self.interval)

    # ==========================================================
    # Lifecycle Control
    # ==========================================================

    def start(self):
        """
        Start telemetry sampling.
        """

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._sample_loop,
            daemon=True,
        )

        self._thread.start()

    def stop(self):
        """
        Stop sampling safely.
        """

        if not self._running:
            return

        self._running = False

        if self._thread:
            self._thread.join()

    # ==========================================================
    # Data Access
    # ==========================================================

    def get_samples(self) -> List[Dict[str, Any]]:
        """
        Thread-safe sample retrieval.
        """

        with self._lock:
            return list(self.data)

    def clear(self):
        """
        Reset stored samples.
        """

        with self._lock:
            self.data.clear()

    # ==========================================================
    # Context Manager Support
    # ==========================================================

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()