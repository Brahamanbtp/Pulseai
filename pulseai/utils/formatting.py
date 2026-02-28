"""
PulseAI Formatting Utilities
----------------------------

Provides standardized formatting helpers for:

- CLI summaries
- Benchmark results
- Comparison outputs
- Human-readable reports

Design Goals
------------
- Consistent output style
- Readable engineering summaries
- Safe numeric formatting
"""

from typing import Dict, Any, List


# ==========================================================
# Numeric Formatting
# ==========================================================

def fmt_float(value: float | None, precision: int = 4) -> str:
    """
    Safely format floating values.
    """

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.{precision}f}"
    except Exception:
        return "N/A"


def fmt_percent(value: float | None) -> str:
    """
    Format percentage values.
    """

    if value is None:
        return "N/A"

    return f"{fmt_float(value, 2)}%"


# ==========================================================
# Section Headers
# ==========================================================

def header(title: str, width: int = 50) -> str:
    """
    Create formatted section header.
    """

    line = "=" * width
    centered = title.center(width)

    return f"\n{line}\n{centered}\n{line}"


def subheader(title: str, width: int = 50) -> str:
    line = "-" * width
    centered = title.center(width)

    return f"\n{centered}\n{line}"


# ==========================================================
# Key-Value Table
# ==========================================================

def key_value_block(data: Dict[str, Any]) -> str:
    """
    Format dictionary into aligned key-value block.
    """

    if not data:
        return ""

    longest = max(len(str(k)) for k in data.keys())

    lines = []

    for key, value in data.items():
        lines.append(
            f"{key:<{longest}} : {value}"
        )

    return "\n".join(lines)


# ==========================================================
# Analysis Summary
# ==========================================================

def format_analysis(analysis: Dict[str, Any]) -> str:
    """
    Pretty-print analyzer output.
    """

    summary = {
        "Latency Mean (s)":
            fmt_float(
                analysis.get("latency_sec", {}).get("mean")
            ),
        "Throughput (tokens/s)":
            fmt_float(
                analysis.get(
                    "throughput_tokens_per_sec"
                )
            ),
        "Efficiency Score":
            fmt_float(
                analysis.get("efficiency_score")
            ),
        "Energy / 1K Tokens":
            fmt_float(
                analysis.get(
                    "energy_per_1k_tokens_proxy"
                )
            ),
        "Stability":
            fmt_float(
                analysis.get("stability_score")
            ),
        "Samples":
            analysis.get("sample_size"),
    }

    return header("Analysis Summary") + "\n" + \
        key_value_block(summary)


# ==========================================================
# Recommendation Output
# ==========================================================

def format_recommendation(
    recommendation: Dict[str, Any]
) -> str:
    """
    Display backend recommendation cleanly.
    """

    block = {
        "Recommended Backend":
            recommendation.get("recommended_backend"),
        "Mode":
            recommendation.get("mode"),
        "Confidence":
            fmt_float(
                recommendation.get("confidence")
            ),
        "Reason":
            recommendation.get("rationale"),
    }

    return header("PulseAI Recommendation") + "\n" + \
        key_value_block(block)


# ==========================================================
# Backend Comparison Table
# ==========================================================

def format_comparison(
    ranking: Dict[str, Dict[str, Any]]
) -> str:
    """
    Format backend comparison results.
    """

    output = [header("Backend Comparison")]

    for backend, metrics in ranking.items():

        output.append(
            subheader(f"Backend: {backend}")
        )

        formatted = {
            "Efficiency":
                fmt_float(metrics.get("efficiency")),
            "Throughput":
                fmt_float(metrics.get("throughput")),
            "Energy":
                fmt_float(metrics.get("energy")),
            "Stability":
                fmt_float(metrics.get("stability")),
        }

        output.append(key_value_block(formatted))

    return "\n".join(output)


# ==========================================================
# Divider
# ==========================================================

def divider(width: int = 50) -> str:
    return "-" * width


# ==========================================================
# Success / Status Messages
# ==========================================================

def success(msg: str) -> str:
    return f"[✓] {msg}"


def warning(msg: str) -> str:
    return f"[!] {msg}"


def info(msg: str) -> str:
    return f"[i] {msg}"