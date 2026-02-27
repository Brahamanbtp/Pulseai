"""
PulseAI CLI
-----------
Control plane entrypoint for AI workload profiling.

Responsibilities:
- Parse user commands
- Execute experiments
- Run backend comparisons
- Trigger analysis & recommendations
- Generate verified reports
"""

import argparse
import sys
from typing import List

from pulseai.orchestrator import Orchestrator
from pulseai.analyzer import analyze
from pulseai.recommender import recommend_backend
from pulseai.report import write_report
from pulseai.environment import capture_environment
from pulseai.backends.registry import get_backend
from pulseai.comparison import compare_backends
from pulseai.workloads.text_inference import TextInferenceWorkload


# ============================================================
# Helpers
# ============================================================

def run_single_backend(backend_name: str, runs: int, warmup: int):
    """
    Execute profiling experiment on a single backend.
    """

    print(f"\n[PulseAI] Running workload on backend: {backend_name}")

    backend = get_backend(backend_name)
    workload = TextInferenceWorkload()

    orchestrator = Orchestrator(
        workload=workload,
        backend=backend,
        runs=runs,
        warmup=warmup,
    )

    raw_runs = orchestrator.execute()

    print("[PulseAI] Analyzing results...")
    analysis = analyze(raw_runs)

    recommendation = recommend_backend(analysis)

    environment = capture_environment()

    report_path = write_report(
        result={
            **analysis,
            **recommendation,
            "backend": backend_name,
        },
        environment=environment,
    )

    print("\n========== PulseAI Verdict ==========")
    print(f"Backend Tested      : {backend_name}")
    print(f"Recommended Mode    : {recommendation['mode']}")
    print(f"Suggested Backend   : {recommendation['recommended_backend']}")
    print(f"Reason              : {recommendation['rationale']}")
    print("--------------------------------------")
    print(f"Efficiency Score    : {analysis['efficiency_score']:.6f}")
    print(
        f"Energy / 1K Tokens  : "
        f"{analysis['energy_per_1k_tokens_proxy']:.4f}"
    )
    print("--------------------------------------")
    print(f"Report Saved        : {report_path}")
    print("======================================\n")


def run_comparison(backends: List[str], runs: int, warmup: int):
    """
    Execute comparison across multiple compute backends.
    """

    print("\n[PulseAI] Running cross-backend comparison")

    workload = TextInferenceWorkload()

    results = compare_backends(
        workload=workload,
        backend_names=backends,
        runs=runs,
        warmup=warmup,
    )

    environment = capture_environment()

    report_path = write_report(
        result=results,
        environment=environment,
    )

    print("\n========== Comparison Summary ==========")

    for backend, data in results["backend_results"].items():
        print(f"\nBackend: {backend}")
        print(
            f"Efficiency Score: "
            f"{data['analysis']['efficiency_score']:.6f}"
        )
        print(
            f"Energy/1K Tokens: "
            f"{data['analysis']['energy_per_1k_tokens_proxy']:.4f}"
        )

    print("\nRecommended Backend:",
          results["final_recommendation"]["recommended_backend"])

    print(f"\nReport Saved: {report_path}")
    print("========================================\n")


# ============================================================
# CLI Definition
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        prog="pulseai",
        description="PulseAI — AI Energy & Hardware Profiler",
    )

    subparsers = parser.add_subparsers(dest="command")

    # ----------------------------
    # RUN COMMAND
    # ----------------------------
    run_cmd = subparsers.add_parser(
        "run",
        help="Run profiling on a single backend",
    )

    run_cmd.add_argument(
        "--backend",
        type=str,
        default="cpu",
        help="Backend to use (cpu/gpu)",
    )

    run_cmd.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of measured runs",
    )

    run_cmd.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Warmup runs excluded from stats",
    )

    # ----------------------------
    # COMPARE COMMAND
    # ----------------------------
    cmp_cmd = subparsers.add_parser(
        "compare",
        help="Compare multiple backends",
    )

    cmp_cmd.add_argument(
        "--backends",
        nargs="+",
        default=["cpu"],
        help="Backends to compare",
    )

    cmp_cmd.add_argument(
        "--runs",
        type=int,
        default=5,
    )

    cmp_cmd.add_argument(
        "--warmup",
        type=int,
        default=1,
    )

    return parser


# ============================================================
# ENTRYPOINT
# ============================================================

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        run_single_backend(
            backend_name=args.backend,
            runs=args.runs,
            warmup=args.warmup,
        )

    elif args.command == "compare":
        run_comparison(
            backends=args.backends,
            runs=args.runs,
            warmup=args.warmup,
        )

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()