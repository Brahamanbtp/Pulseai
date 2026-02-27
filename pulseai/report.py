"""
PulseAI Reporting Module
------------------------

Responsible for generating immutable, verifiable experiment
artifacts.

Responsibilities:
- Assemble final experiment payload
- Attach integrity fingerprint
- Persist reports safely
- Export machine + human readable artifacts
"""

from typing import Dict, Any
from pathlib import Path
import json
import datetime
import uuid
import csv

from pulseai.config import REPORT_DIR
from pulseai.integrity import attach_integrity


# ============================================================
# Helpers
# ============================================================

def _generate_run_id() -> str:
    """
    Generate unique run identifier.
    """
    return f"pulseai-{uuid.uuid4()}"


def _timestamp() -> str:
    return datetime.datetime.utcnow().isoformat()


def _ensure_report_dir():
    Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)


# ============================================================
# Payload Assembly
# ============================================================

def build_report_payload(
    result: Dict[str, Any],
    environment: Dict[str, Any],
    experiment: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Construct canonical PulseAI report payload.
    """

    payload = {
        "run_id": _generate_run_id(),
        "timestamp_utc": _timestamp(),
        "experiment": experiment or {},
        "environment": environment,
        "result": result,
    }

    # Attach cryptographic integrity
    payload = attach_integrity(payload)

    return payload


# ============================================================
# JSON Persistence
# ============================================================

def _write_json(payload: Dict[str, Any]) -> Path:
    """
    Save JSON report artifact.
    """

    _ensure_report_dir()

    file_path = Path(REPORT_DIR) / f"{payload['run_id']}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return file_path


# ============================================================
# CSV Summary Export
# ============================================================

def _write_csv_summary(payload: Dict[str, Any]) -> Path:
    """
    Export flattened CSV summary for quick inspection.
    """

    result = payload["result"]

    csv_path = Path(REPORT_DIR) / f"{payload['run_id']}.csv"

    flattened = {
        "run_id": payload["run_id"],
        "efficiency_score": result.get("efficiency_score"),
        "throughput_tokens_per_sec":
            result.get("throughput_tokens_per_sec"),
        "energy_per_1k_tokens":
            result.get("energy_per_1k_tokens_proxy"),
        "stability_score":
            result.get("stability_score"),
        "recommended_backend":
            result.get("recommended_backend"),
        "mode":
            result.get("mode"),
    }

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=flattened.keys()
        )
        writer.writeheader()
        writer.writerow(flattened)

    return csv_path


# ============================================================
# Public API
# ============================================================

def write_report(
    result: Dict[str, Any],
    environment: Dict[str, Any],
    experiment: Dict[str, Any] | None = None,
) -> str:
    """
    Create complete PulseAI report artifact.

    Returns:
        Path to JSON report.
    """

    payload = build_report_payload(
        result=result,
        environment=environment,
        experiment=experiment,
    )

    json_path = _write_json(payload)
    _write_csv_summary(payload)

    return str(json_path)