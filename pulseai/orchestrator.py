"""
PulseAI Orchestrator
--------------------

Responsible for executing deterministic profiling experiments.

Core Responsibilities:
- Backend lifecycle management
- Warmup stabilization
- Multi-run execution
- Metrics capture
- Experiment isolation
- Reproducible run outputs
"""

from typing import List, Dict, Any
import time

from pulseai.metrics.cpu_metrics import snapshot_cpu
from pulseai.config import (
    DEFAULT_RUNS,
    DEFAULT_WARMUP_RUNS,
    ENABLE_TIME_SERIES_SAMPLING,
)
from pulseai.metrics.sampler import MetricSampler


class Orchestrator:
    """
    Executes profiling experiments for a workload on a given backend.
    """

    def __init__(
        self,
        workload,
        backend,
        runs: int = DEFAULT_RUNS,
        warmup: int = DEFAULT_WARMUP_RUNS,
    ):
        self.workload = workload
        self.backend = backend
        self.runs = runs
        self.warmup = warmup

    # ==========================================================
    # Internal Helpers
    # ==========================================================

    def _execute_single_run(self) -> Dict[str, Any]:
        """
        Execute one workload run with metrics collection.
        """

        sampler = None

        # Optional time-series sampling
        if ENABLE_TIME_SERIES_SAMPLING:
            sampler = MetricSampler()
            sampler.start()

        before_metrics = snapshot_cpu()

        start_time = time.perf_counter()

        # workload returns token count
        tokens_processed = self.backend.run(self.workload)

        end_time = time.perf_counter()

        after_metrics = snapshot_cpu()

        if sampler:
            sampler.stop()

        duration = end_time - start_time

        return {
            "duration": duration,
            "tokens": tokens_processed,
            "cpu_before": before_metrics,
            "cpu_after": after_metrics,
            "time_series": sampler.data if sampler else [],
        }

    # ==========================================================
    # Public Execution API
    # ==========================================================

    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute full experiment lifecycle.

        Flow:
        1. Backend setup
        2. Warmup runs (discarded)
        3. Measured runs
        4. Backend teardown
        """

        print(
            f"[PulseAI] Starting experiment "
            f"(runs={self.runs}, warmup={self.warmup})"
        )

        results: List[Dict[str, Any]] = []

        total_iterations = self.runs + self.warmup

        self.backend.setup()

        try:
            for iteration in range(total_iterations):

                run_result = self._execute_single_run()

                # Discard warmups
                if iteration < self.warmup:
                    print(f"[Warmup {iteration+1}] completed")
                    continue

                print(
                    f"[Run {iteration - self.warmup + 1}] "
                    f"duration={run_result['duration']:.4f}s"
                )

                results.append(run_result)

        finally:
            self.backend.teardown()

        print("[PulseAI] Experiment complete")

        return results