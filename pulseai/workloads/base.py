"""
PulseAI Compute Backend Interface
---------------------------------

Defines the Hardware Abstraction Layer (HAL) used by PulseAI.

All compute backends must implement this interface.

Design Goals
------------
- Hardware agnostic execution
- Deterministic experiment lifecycle
- Safe resource management
- Accurate benchmarking boundaries
- Future accelerator extensibility
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ComputeBackend(ABC):
    """
    Abstract compute backend.

    Represents a hardware execution target capable of
    running AI workloads under PulseAI orchestration.
    """

    # ==========================================================
    # Backend Identity
    # ==========================================================

    name: str = "undefined"

    # ==========================================================
    # Lifecycle Management
    # ==========================================================

    @abstractmethod
    def setup(self) -> None:
        """
        Prepare backend before execution.

        Examples:
        - Initialize device/runtime
        - Allocate resources
        - Warm execution context
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, workload: Any) -> int:
        """
        Execute workload.

        Parameters
        ----------
        workload : callable
            Workload object or callable.

        Returns
        -------
        int
            Units of completed work
            (tokens, samples, etc.)
        """
        raise NotImplementedError

    @abstractmethod
    def teardown(self) -> None:
        """
        Cleanup backend resources.

        Must always succeed safely even after failure.
        """
        raise NotImplementedError

    # ==========================================================
    # Synchronization (CRITICAL FOR GPU/NPU)
    # ==========================================================

    def synchronize(self) -> None:
        """
        Ensure device execution completion.

        Required for asynchronous devices like:
        - GPU
        - NPU
        - Accelerator runtimes

        CPU backend may safely ignore.
        """
        pass

    # ==========================================================
    # Capability Introspection
    # ==========================================================

    def supports_sampling(self) -> bool:
        """
        Indicates backend supports telemetry sampling.
        """
        return False

    def device_info(self) -> Dict[str, Any]:
        """
        Return backend device metadata.

        Can be overridden by implementations.
        """

        return {
            "backend": self.name,
            "description": "generic compute backend"
        }

    # ==========================================================
    # Health Check
    # ==========================================================

    def health_check(self) -> bool:
        """
        Validate backend availability.

        Used by backend registry discovery.
        """

        try:
            self.setup()
            self.teardown()
            return True
        except Exception:
            return False

    # ==========================================================
    # Context Manager Support
    # ==========================================================

    def __enter__(self):
        """
        Enables safe usage:

            with backend:
                backend.run(...)
        """
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Guarantees teardown even on failure.
        """

        try:
            self.teardown()
        except Exception:
            # teardown must never propagate failure
            pass

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return f"<ComputeBackend name={self.name}>"