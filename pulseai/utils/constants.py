"""
PulseAI Global Constants
------------------------

Central location for system-wide constants used across
PulseAI modules.

Design Goals
------------
- Remove magic numbers
- Ensure consistency
- Simplify tuning
- Improve maintainability
"""

# ==========================================================
# Project Identity
# ==========================================================

PROJECT_NAME = "PulseAI"
PROJECT_TAGLINE = "AI Energy & Hardware Profiler"

DEFAULT_REPORT_PREFIX = "pulseai"


# ==========================================================
# Experiment Defaults
# ==========================================================

DEFAULT_WARMUP_RUNS = 1
DEFAULT_MEASURED_RUNS = 5

MAX_ALLOWED_RUNS = 50


# ==========================================================
# Timing & Sampling
# ==========================================================

# Default telemetry sampling interval (seconds)
DEFAULT_SAMPLE_INTERVAL_SEC = 0.1

# Minimum allowed sampling interval
MIN_SAMPLE_INTERVAL_SEC = 0.01

# Timer precision safeguard
MIN_VALID_DURATION_SEC = 1e-6


# ==========================================================
# Analyzer Constants
# ==========================================================

# Energy normalization target
TOKENS_NORMALIZATION_FACTOR = 1000

# Stability computation safeguard
MIN_SAMPLE_SIZE_FOR_STABILITY = 2

# Outlier filtering threshold
DEFAULT_OUTLIER_STD_THRESHOLD = 2.5


# ==========================================================
# Recommendation Engine
# ==========================================================

EFFICIENCY_WEIGHT = 0.5
PERFORMANCE_WEIGHT = 0.3
STABILITY_WEIGHT = 0.2

MIN_STABILITY_ACCEPTABLE = 0.6


# ==========================================================
# Backend Identifiers
# ==========================================================

BACKEND_CPU = "cpu"
BACKEND_GPU = "gpu"

SUPPORTED_BACKENDS = [
    BACKEND_CPU,
    BACKEND_GPU,
]


# ==========================================================
# Reporting
# ==========================================================

DEFAULT_REPORT_DIR = "reports"

JSON_INDENT = 2
CSV_ENCODING = "utf-8"


# ==========================================================
# Integrity / Security
# ==========================================================

DEFAULT_HASH_ALGORITHM = "sha256"

INTEGRITY_FIELD_NAME = "integrity"


# ==========================================================
# Workload Defaults
# ==========================================================

DEFAULT_TEXT_MODEL = "distilgpt2"

DEFAULT_MAX_NEW_TOKENS = 50

DEFAULT_PROMPTS = [
    "Artificial intelligence will",
    "Future processors enable",
    "Efficient computing requires",
]


# ==========================================================
# CLI Formatting
# ==========================================================

DEFAULT_HEADER_WIDTH = 50

SUCCESS_SYMBOL = "[✓]"
WARNING_SYMBOL = "[!]"
INFO_SYMBOL = "[i]"


# ==========================================================
# Environment Capture
# ==========================================================

SAFE_ENV_VARIABLES = [
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "CUDA_VISIBLE_DEVICES",
]


# ==========================================================
# Internal Limits
# ==========================================================

MAX_TIME_SERIES_SAMPLES = 100000

MAX_PROMPT_LENGTH = 2048


# ==========================================================
# Versioning
# ==========================================================

PULSEAI_VERSION = "1.0.0"
API_VERSION = "v1"