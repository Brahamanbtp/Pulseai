"""
PulseAI GPU Metrics Collector
-----------------------------

Provides accelerator telemetry for GPU-backed workloads.

Supports:
- NVIDIA CUDA GPUs
- AMD ROCm GPUs (via PyTorch CUDA interface)

Design Goals:
- Safe fallback when GPU unavailable
- Low overhead sampling
- Benchmark correctness
- Cross-platform compatibility
"""

from typing import Dict, Any, List
import time
import torch


# ============================================================
# Availability Check
# ============================================================

def gpu_available() -> bool:
    """
    Check if GPU accelerator is available.
    """
    try:
        return torch.cuda.is_available()
    except Exception:
        return False


# ============================================================
# Device Properties
# ============================================================

def gpu_device_info() -> Dict[str, Any]:
    """
    Static GPU hardware metadata.
    """

    if not gpu_available():
        return {
            "available": False,
            "devices": []
        }

    devices: List[Dict[str, Any]] = []

    for idx in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(idx)

        devices.append({
            "device_id": idx,
            "name": props.name,
            "total_memory_gb":
                round(props.total_memory / (1024 ** 3), 2),
            "multi_processor_count":
                props.multi_processor_count,
            "compute_capability":
                f"{props.major}.{props.minor}",
        })

    return {
        "available": True,
        "device_count": len(devices),
        "devices": devices,
    }


# ============================================================
# Memory Metrics
# ============================================================

def gpu_memory_snapshot(device: int = 0) -> Dict[str, Any]:
    """
    Capture GPU memory usage snapshot.
    """

    if not gpu_available():
        return {
            "gpu_memory_used_mb": None,
            "gpu_memory_reserved_mb": None,
        }

    torch.cuda.synchronize(device)

    allocated = torch.cuda.memory_allocated(device)
    reserved = torch.cuda.memory_reserved(device)

    return {
        "gpu_memory_used_mb":
            round(allocated / (1024 ** 2), 2),
        "gpu_memory_reserved_mb":
            round(reserved / (1024 ** 2), 2),
    }


# ============================================================
# Utilization Proxy
# ============================================================

def gpu_utilization_proxy(device: int = 0) -> float:
    """
    Lightweight utilization proxy.

    True utilization APIs require vendor SDKs
    (NVML / ROCm SMI), so we estimate activity
    using memory allocation pressure.
    """

    if not gpu_available():
        return 0.0

    torch.cuda.synchronize(device)

    allocated = torch.cuda.memory_allocated(device)
    total = torch.cuda.get_device_properties(
        device
    ).total_memory

    if total == 0:
        return 0.0

    return (allocated / total) * 100.0


# ============================================================
# Full Snapshot
# ============================================================

def snapshot_gpu(device: int = 0) -> Dict[str, Any]:
    """
    Full GPU telemetry snapshot.

    Safe for orchestrator + sampler usage.
    """

    if not gpu_available():
        return {
            "timestamp": time.time(),
            "gpu_available": False
        }

    torch.cuda.synchronize(device)

    memory_stats = gpu_memory_snapshot(device)

    snapshot = {
        "timestamp": time.time(),
        "gpu_available": True,
        "device": device,
        "utilization_proxy_percent":
            gpu_utilization_proxy(device),
        **memory_stats,
    }

    return snapshot


# ============================================================
# Fast Sampling Mode
# ============================================================

def gpu_utilization_only(device: int = 0) -> float:
    """
    Minimal overhead utilization read.
    Used by real-time sampler.
    """

    if not gpu_available():
        return 0.0

    return gpu_utilization_proxy(device)