"""
PulseAI Configuration Module
----------------------------

Centralized configuration management for PulseAI.

Responsibilities:
- Load environment variables
- Provide validated runtime configuration
- Define global defaults
- Prevent scattered configuration logic
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()


# ==========================================================
# Project Metadata
# ==========================================================

PROJECT_NAME = "PulseAI"
PROJECT_VERSION = "1.0.0"


# ==========================================================
# Directory Configuration
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = Path(
    os.getenv("PULSEAI_REPORT_DIR", BASE_DIR / "reports")
)

LOG_DIR = Path(
    os.getenv("PULSEAI_LOG_DIR", BASE_DIR / "logs")
)

CACHE_DIR = Path(
    os.getenv("PULSEAI_CACHE_DIR", BASE_DIR / ".cache")
)


def ensure_directories():
    """
    Ensure required runtime directories exist.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Experiment Defaults
# ==========================================================

DEFAULT_RUNS = int(
    os.getenv("PULSEAI_DEFAULT_RUNS", 5)
)

DEFAULT_WARMUP_RUNS = int(
    os.getenv("PULSEAI_DEFAULT_WARMUP", 1)
)

MAX_ALLOWED_RUNS = int(
    os.getenv("PULSEAI_MAX_RUNS", 50)
)


# ==========================================================
# Backend Configuration
# ==========================================================

DEFAULT_BACKEND = os.getenv(
    "PULSEAI_DEFAULT_BACKEND",
    "cpu"
)

AVAILABLE_BACKENDS = ["cpu", "gpu"]


def validate_backend(name: str):
    if name not in AVAILABLE_BACKENDS:
        raise ValueError(
            f"Unsupported backend '{name}'. "
            f"Available: {AVAILABLE_BACKENDS}"
        )


# ==========================================================
# Metrics Sampling Configuration
# ==========================================================

METRIC_SAMPLE_INTERVAL_SEC = float(
    os.getenv("PULSEAI_SAMPLE_INTERVAL", 0.1)
)

ENABLE_TIME_SERIES_SAMPLING = (
    os.getenv("PULSEAI_ENABLE_SAMPLING", "true").lower()
    == "true"
)


# ==========================================================
# Analysis Configuration
# ==========================================================

OUTLIER_STD_THRESHOLD = float(
    os.getenv("PULSEAI_OUTLIER_STD", 2.5)
)

ENABLE_OUTLIER_FILTERING = (
    os.getenv("PULSEAI_FILTER_OUTLIERS", "true").lower()
    == "true"
)


# ==========================================================
# Sustainability Metrics
# ==========================================================

ENERGY_NORMALIZATION_FACTOR = float(
    os.getenv("PULSEAI_ENERGY_NORMALIZATION", 1000)
)
"""
Used for:
energy_per_1k_tokens_proxy
"""


# ==========================================================
# Integrity Configuration
# ==========================================================

HASH_ALGORITHM = os.getenv(
    "PULSEAI_HASH_ALGO",
    "sha256"
)

INCLUDE_ENVIRONMENT_IN_HASH = (
    os.getenv("PULSEAI_HASH_ENV", "true").lower()
    == "true"
)


# ==========================================================
# Debug / Development Flags
# ==========================================================

DEBUG_MODE = (
    os.getenv("PULSEAI_DEBUG", "false").lower()
    == "true"
)

VERBOSE_LOGGING = (
    os.getenv("PULSEAI_VERBOSE", "false").lower()
    == "true"
)


# ==========================================================
# Runtime Validation
# ==========================================================

def validate_runtime():
    """
    Validate configuration sanity at startup.
    """

    if DEFAULT_RUNS <= 0:
        raise ValueError("DEFAULT_RUNS must be > 0")

    if DEFAULT_WARMUP_RUNS < 0:
        raise ValueError("Warmup runs cannot be negative")

    if DEFAULT_RUNS > MAX_ALLOWED_RUNS:
        raise ValueError(
            f"Runs exceed limit ({MAX_ALLOWED_RUNS})"
        )


# ==========================================================
# Initialization Hook
# ==========================================================

def initialize():
    """
    Initialize PulseAI runtime configuration.
    Must be called once at application startup.
    """

    ensure_directories()
    validate_runtime()


# Auto-init when imported
initialize()