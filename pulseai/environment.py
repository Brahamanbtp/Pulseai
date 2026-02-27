"""
PulseAI Environment Capture
---------------------------

Captures runtime environment metadata required for
reproducible AI workload profiling.

Responsibilities:
- System identification
- Hardware visibility
- Runtime dependency versions
- Accelerator availability
- Experiment reproducibility context
"""

from typing import Dict, Any
import platform
import os
import psutil
import torch


# ============================================================
# CPU INFORMATION
# ============================================================

def _cpu_info() -> Dict[str, Any]:
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "cpu_freq_mhz":
            psutil.cpu_freq().current
            if psutil.cpu_freq()
            else None,
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }


# ============================================================
# MEMORY INFORMATION
# ============================================================

def _memory_info() -> Dict[str, Any]:
    mem = psutil.virtual_memory()

    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
    }


# ============================================================
# GPU INFORMATION
# ============================================================

def _gpu_info() -> Dict[str, Any]:
    gpu_data = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": 0,
        "devices": [],
    }

    if torch.cuda.is_available():
        count = torch.cuda.device_count()
        gpu_data["device_count"] = count

        for idx in range(count):
            props = torch.cuda.get_device_properties(idx)

            gpu_data["devices"].append({
                "id": idx,
                "name": props.name,
                "total_memory_gb":
                    round(props.total_memory / (1024 ** 3), 2),
                "multi_processor_count":
                    props.multi_processor_count,
            })

    return gpu_data


# ============================================================
# SOFTWARE STACK
# ============================================================

def _software_stack() -> Dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "platform": platform.platform(),
        "os": os.name,
    }


# ============================================================
# ENVIRONMENT VARIABLES (SAFE SUBSET)
# ============================================================

SAFE_ENV_KEYS = [
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "CUDA_VISIBLE_DEVICES",
]


def _environment_variables() -> Dict[str, Any]:
    env = {}

    for key in SAFE_ENV_KEYS:
        if key in os.environ:
            env[key] = os.environ[key]

    return env


# ============================================================
# MAIN CAPTURE FUNCTION
# ============================================================

def capture_environment() -> Dict[str, Any]:
    """
    Capture full execution environment snapshot.

    Used for:
    - report generation
    - integrity hashing
    - reproducibility validation
    """

    return {
        "system": {
            "hostname": platform.node(),
            "platform": platform.system(),
            "platform_release": platform.release(),
        },
        "cpu": _cpu_info(),
        "memory": _memory_info(),
        "gpu": _gpu_info(),
        "software": _software_stack(),
        "environment_variables": _environment_variables(),
    }