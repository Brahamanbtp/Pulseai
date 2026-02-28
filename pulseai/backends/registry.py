"""
PulseAI Backend Registry
------------------------

Central registry responsible for discovering,
validating, and providing compute backends.

Responsibilities:
- Backend registration
- Availability detection
- Safe backend retrieval
- Runtime backend validation
"""

from typing import Dict, Type, List

from pulseai.backends.base import ComputeBackend
from pulseai.backends.cpu import CPUBackend
from pulseai.backends.gpu import GPUBackend


# ============================================================
# Backend Registry Storage
# ============================================================

_BACKEND_REGISTRY: Dict[str, Type[ComputeBackend]] = {}


# ============================================================
# Registration
# ============================================================

def register_backend(
    name: str,
    backend_cls: Type[ComputeBackend],
) -> None:
    """
    Register backend implementation.
    """

    if not issubclass(backend_cls, ComputeBackend):
        raise TypeError(
            "Backend must inherit ComputeBackend"
        )

    _BACKEND_REGISTRY[name] = backend_cls


# ============================================================
# Default Backend Registration
# ============================================================

def _register_defaults():
    """
    Register built-in PulseAI backends.
    """

    register_backend("cpu", CPUBackend)
    register_backend("gpu", GPUBackend)


_register_defaults()


# ============================================================
# Backend Availability
# ============================================================

def backend_available(name: str) -> bool:
    """
    Check if backend exists and initializes safely.
    """

    if name not in _BACKEND_REGISTRY:
        return False

    try:
        backend = _BACKEND_REGISTRY[name]()
        backend.setup()
        backend.teardown()
        return True

    except Exception:
        return False


def available_backends() -> List[str]:
    """
    Return list of usable backends.
    """

    available = []

    for name in _BACKEND_REGISTRY:
        if backend_available(name):
            available.append(name)

    return available


# ============================================================
# Backend Retrieval
# ============================================================

def get_backend(name: str) -> ComputeBackend:
    """
    Instantiate backend safely.
    """

    if name not in _BACKEND_REGISTRY:
        raise ValueError(
            f"Unknown backend '{name}'. "
            f"Available: {list(_BACKEND_REGISTRY.keys())}"
        )

    backend_cls = _BACKEND_REGISTRY[name]

    backend = backend_cls()

    return backend


# ============================================================
# Metadata
# ============================================================

def backend_info(name: str):
    """
    Retrieve backend device metadata.
    """

    backend = get_backend(name)

    try:
        backend.setup()
        info = backend.device_info()
    finally:
        backend.teardown()

    return info