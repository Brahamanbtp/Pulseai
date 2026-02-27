"""
PulseAI CPU Backend
-------------------

Reference compute backend executing workloads on CPU.

Responsibilities:
- Deterministic workload execution
- Accurate timing boundary support
- Safe lifecycle handling
- Hardware metadata exposure
"""

from typing import Any, Dict
import platform
import psutil
import time

from pulseai.backends.base import ComputeBackend


class CPUBackend(ComputeBackend):
    """
    CPU execution backend.

    Acts as baseline reference backend for all
    heterogeneous comparisons.
    """

    name = "cpu"

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def setup(self) -> None:
        """
        Prepare CPU execution environment.

        CPU requires minimal setup but we explicitly
        stabilize execution conditions.
        """

        # Warm CPU usage sampling once to stabilize psutil
        psutil.cpu_percent(interval=None)

    # ==========================================================
    # Execution
    # ==========================================================

    def run(self, workload: Any) -> int:
        """
        Execute workload on CPU.

        Parameters
        ----------
        workload : callable
            Must return number of processed tokens.

        Returns
        -------
        int
            Work units completed.
        """

        if not callable(workload):
            raise TypeError(
                "Workload must be callable"
            )

        start = time.perf_counter()

        result = workload()

        end = time.perf_counter()

        # CPU execution is synchronous,
        # but explicit boundary kept for parity with GPU
        self.synchronize()

        duration = end - start

        if duration <= 0:
            raise RuntimeError(
                "Invalid execution duration detected"
            )

        if not isinstance(result, int):
            raise ValueError(
                "Workload must return token/work-unit count"
            )

        return result

    # ==========================================================
    # Cleanup
    # ==========================================================

    def teardown(self) -> None:
        """
        CPU cleanup.

        No explicit resource release required,
        but method exists for interface symmetry.
        """
        pass

    # ==========================================================
    # Synchronization
    # ==========================================================

    def synchronize(self) -> None:
        """
        CPU execution is blocking,
        included for backend parity.
        """
        return

    # ==========================================================
    # Sampling Capability
    # ==========================================================

    def supports_sampling(self) -> bool:
        """
        CPU backend supports telemetry sampling.
        """
        return True

    # ==========================================================
    # Device Metadata
    # ==========================================================

    def device_info(self) -> Dict[str, Any]:
        """
        Return CPU hardware metadata.
        """

        freq = psutil.cpu_freq()

        return {
            "backend": self.name,
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "physical_cores": psutil.cpu_count(
                logical=False
            ),
            "logical_cores": psutil.cpu_count(
                logical=True
            ),
            "current_frequency_mhz":
                freq.current if freq else None,
        }