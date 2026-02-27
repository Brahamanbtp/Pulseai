"""
PulseAI Integrity Module
------------------------

Provides cryptographic integrity guarantees for PulseAI
experiment reports.

Responsibilities:
- Canonical serialization
- SHA-based fingerprinting
- Experiment verification
- Tamper detection
- Reproducibility validation

Design Principles:
- Deterministic hashing
- Vendor neutral
- Audit friendly
- Zero external dependencies
"""

from typing import Dict, Any
import hashlib
import json

from pulseai.config import HASH_ALGORITHM


# ============================================================
# Canonical Serialization
# ============================================================

def _canonical_json(payload: Dict[str, Any]) -> bytes:
    """
    Convert dictionary into deterministic JSON bytes.

    Ensures identical hashing across machines.
    """

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


# ============================================================
# Hash Engine
# ============================================================

def _get_hasher():
    """
    Create configured hashing algorithm.
    """

    try:
        return hashlib.new(HASH_ALGORITHM)
    except ValueError as exc:
        raise RuntimeError(
            f"Unsupported hash algorithm: {HASH_ALGORITHM}"
        ) from exc


# ============================================================
# Run Fingerprint
# ============================================================

def compute_run_hash(payload: Dict[str, Any]) -> str:
    """
    Compute cryptographic fingerprint for experiment.

    Covers:
    - experiment config
    - environment metadata
    - analysis results
    """

    hasher = _get_hasher()
    canonical = _canonical_json(payload)

    hasher.update(canonical)

    return hasher.hexdigest()


# ============================================================
# Integrity Envelope
# ============================================================

def attach_integrity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attach integrity metadata to payload.
    """

    fingerprint = compute_run_hash(payload)

    payload["integrity"] = {
        "hash_algorithm": HASH_ALGORITHM,
        "fingerprint": fingerprint,
    }

    return payload


# ============================================================
# Verification
# ============================================================

def verify_integrity(payload: Dict[str, Any]) -> bool:
    """
    Verify payload integrity.

    Returns:
        True  -> valid
        False -> tampered
    """

    if "integrity" not in payload:
        raise ValueError("No integrity metadata found")

    integrity_block = payload["integrity"]

    expected_hash = integrity_block["fingerprint"]

    # Remove integrity temporarily
    payload_copy = dict(payload)
    payload_copy.pop("integrity")

    actual_hash = compute_run_hash(payload_copy)

    return actual_hash == expected_hash


# ============================================================
# Integrity Report
# ============================================================

def integrity_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce detailed verification report.
    """

    valid = verify_integrity(payload)

    return {
        "verified": valid,
        "algorithm": payload["integrity"]["hash_algorithm"],
        "fingerprint": payload["integrity"]["fingerprint"],
        "status": "VALID" if valid else "TAMPERED",
    }