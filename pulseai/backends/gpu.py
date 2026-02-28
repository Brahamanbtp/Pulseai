"""
PulseAI GPU Backend
-------------------

GPU execution backend supporting accelerator-based inference.

Design Goals:
- Correct async GPU timing
- Safe execution fallback
- Deterministic benchmarking
- Hardware metadata visibility
- Vendor-neutral structure (CUDA / ROCm ready)
"""

from typing import Any, Dict
import torch
import time

from pulseai.backends.base import ComputeBackend


class GPUBackend(ComputeBackend):
    """
    GPU compute backend.

    Supports CUDA GPUs and remains compatible with
    ROCm-enabled PyTorch environments (AMD GPUs).
    """

    name = "gpu"

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def setup(self) -> None:
        """
        Initialize GPU execution environment.
        """

        if not torch.cuda.is_available():
            raise RuntimeError(
                "GPU backend requested but CUDA/ROCm "
                "device not available."
            )

        self.device = torch.device("cuda")

        # Warm GPU context
        torch.cuda.init()

        # Empty cache for stable benchmarking
        torch.cuda.empty_cache()

    # ==========================================================
    # Execution
    # ==========================================================

    def run(self, workload: Any) -> int:
        """
        Execute workload on GPU.

        Workload must internally move tensors
        to correct device when required.
        """

        if not callable(workload):
            raise TypeError("Workload must be callable")

        # Ensure previous kernels finished
        self.synchronize()

        start = time.perf_counter()

        result = workload()

        # CRITICAL:
        # GPU execution is asynchronous
        self.synchronize()

        end = time.perf_counter()

        duration = end - start

        if duration <= 0:
            raise RuntimeError(
                "Invalid GPU execution duration"
            )

        if not isinstance(result, int):
            raise ValueError(
                "Workload must return token/work-unit count"
            )

        return result

    # ==========================================================
    # Synchronization
    # ==========================================================

    def synchronize(self) -> None:
        """
        Block until all GPU kernels complete.
        REQUIRED for correct timing.
        """

        if torch.cuda.is_available():
            torch.cuda.synchronize()

    # ==========================================================
    # Cleanup
    # ==========================================================

    def teardown(self) -> None:
        """
        Release GPU memory safely.
        """

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ==========================================================
    # Sampling Capability
    # ==========================================================

    def supports_sampling(self) -> bool:
        return True

    # ==========================================================
    # Device Metadata
    # ==========================================================

    def device_info(self) -> Dict[str, Any]:
        """
        Return GPU hardware metadata.
        """

        if not torch.cuda.is_available():
            return {
                "backend": self.name,
                "available": False
            }

        idx = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(idx)

        return {
            "backend": self.name,
            "available": True,
            "device_id": idx,
            "name": props.name,
            "total_memory_gb":
                round(props.total_memory / (1024 ** 3), 2),
            "multi_processor_count":
                props.multi_processor_count,
            "compute_capability":
                f"{props.major}.{props.minor}",
        }