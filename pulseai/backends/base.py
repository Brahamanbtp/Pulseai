"""
PulseAI Compute Backend Interface
---------------------------------

Defines the Hardware Abstraction Layer (HAL) used by PulseAI.

All compute backends (CPU, GPU, Accelerator/NPU) must implement
this interface to participate in profiling experiments.

Design Goals:
- Hardware agnostic execution
- Deterministic lifecycle control
- Safe resource management
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

    # --------------------------------------------------------
    # Required Metadata
    # --------------------------------------------------------

    name: str = "undefined"

    # --------------------------------------------------------
    # Lifecycle Management
    # --------------------------------------------------------

    @abstractmethod
    def setup(self) -> None:
        """
        Prepare backend before execution.

        Examples:
        - initialize device
        - allocate runtime resources
        - set execution flags
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, workload: Any) -> int:
        """
        Execute workload.

        Parameters
        ----------
        workload:
            Callable workload object.

        Returns
        -------
        int
            Units of work completed
            (e.g., tokens processed).
        """
        raise NotImplementedError

    @abstractmethod
    def teardown(self) -> None:
        """
        Cleanup backend resources.

        Must always succeed safely even after failure.
        """
        raise NotImplementedError

    # --------------------------------------------------------
    # Optional Capabilities
    # --------------------------------------------------------

    def device_info(self) -> Dict[str, Any]:
        """
        Return backend device metadata.

        Optional override.
        """

        return {
            "backend": self.name,
            "info": "generic compute backend"
        }

    def supports_sampling(self) -> bool:
        """
        Indicates whether backend supports
        fine-grained telemetry sampling.
        """
        return False

    def synchronize(self) -> None:
        """
        Optional device synchronization.

        Needed for GPU/NPU correctness.
        CPU backend may ignore.
        """
        pass

    # --------------------------------------------------------
    # Context Manager Support
    # --------------------------------------------------------

    def __enter__(self):
        """
        Enables:

            with backend:
                run workload
        """
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Guarantees teardown execution.
        """
        self.teardown()