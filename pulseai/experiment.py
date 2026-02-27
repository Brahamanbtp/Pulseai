"""
PulseAI Experiment Definition
-----------------------------

Defines a deterministic experiment configuration and metadata
snapshot used for reproducible AI workload profiling.

Responsibilities:
- Experiment identity
- Configuration snapshotting
- Reproducibility guarantees
- Backend + workload binding
- Metadata normalization
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any
import uuid
import platform
import torch

from pulseai.config import (
    DEFAULT_RUNS,
    DEFAULT_WARMUP_RUNS,
    PROJECT_VERSION,
)


# ============================================================
# Experiment Configuration
# ============================================================

@dataclass
class ExperimentConfig:
    """
    Immutable configuration describing an experiment.
    """

    backend: str
    workload: str
    runs: int = DEFAULT_RUNS
    warmup_runs: int = DEFAULT_WARMUP_RUNS
    notes: str | None = None


# ============================================================
# Experiment Metadata
# ============================================================

@dataclass
class ExperimentMetadata:
    """
    Environment + runtime metadata.
    """

    experiment_id: str
    created_at: str
    hostname: str
    os: str
    python_version: str
    torch_version: str
    cuda_available: bool


# ============================================================
# Experiment Object
# ============================================================

class Experiment:
    """
    Represents a single PulseAI experiment.

    Acts as the reproducibility boundary.
    """

    def __init__(self, config: ExperimentConfig):

        self.config = config
        self.metadata = self._capture_metadata()

    # --------------------------------------------------------
    # Metadata Capture
    # --------------------------------------------------------

    def _capture_metadata(self) -> ExperimentMetadata:
        """
        Capture execution environment.
        """

        return ExperimentMetadata(
            experiment_id=f"exp-{uuid.uuid4()}",
            created_at=datetime.utcnow().isoformat(),
            hostname=platform.node(),
            os=platform.platform(),
            python_version=platform.python_version(),
            torch_version=torch.__version__,
            cuda_available=torch.cuda.is_available(),
        )

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert experiment into canonical representation.
        Used for hashing & reporting.
        """

        return {
            "pulseai_version": PROJECT_VERSION,
            "config": asdict(self.config),
            "metadata": asdict(self.metadata),
        }

    # --------------------------------------------------------
    # Human Summary
    # --------------------------------------------------------

    def summary(self) -> str:
        """
        Human-readable experiment summary.
        """

        cfg = self.config

        return (
            "\n========== Experiment ==========\n"
            f"Experiment ID : {self.metadata.experiment_id}\n"
            f"Backend       : {cfg.backend}\n"
            f"Workload      : {cfg.workload}\n"
            f"Runs          : {cfg.runs}\n"
            f"Warmup Runs   : {cfg.warmup_runs}\n"
            f"Created At    : {self.metadata.created_at}\n"
            "================================\n"
        )