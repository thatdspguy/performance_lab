"""CLI entry point for running benchmarks from config file.

Usage:
    uv run python -m backend.cli [--config benchmark_config.json]

Reads benchmark config (per-workflow format), simulates metrics, writes to
InfluxDB, and runs regression detection for each workflow.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from backend.apps import APP_DEFINITIONS
from backend.metrics import get_commit_count, write_metrics
from backend.regression import detect_regressions
from backend.simulator import get_commit_id, simulate_metrics


def load_config(config_path: str) -> dict:
    """Load benchmark config JSON."""
    path = Path(config_path)
    if not path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def run_benchmark(config: dict) -> bool:
    """Run benchmark simulation for all workflows in config.

    Supports the per-workflow config format:
        { "app": "<slug>", "workflows": { "<wf_slug>": { "cpu_mean": ..., ... } } }

    Returns True if any regressions were detected.
    """
    any_regressions = False
    app_slug = config.get("app", "")
    workflows = config.get("workflows", {})

    if app_slug not in APP_DEFINITIONS:
        print(f"Error: unknown app '{app_slug}'", file=sys.stderr)
        sys.exit(1)

    commit_id = get_commit_id()
    print(f"Benchmarking: {app_slug} (commit {commit_id})")
    print("=" * 60)

    for wf_slug, params in workflows.items():
        print(f"\n  Workflow: {wf_slug}")
        commit_number = get_commit_count(app_slug, workflow=wf_slug) + 1

        metrics = simulate_metrics(
            cpu_mean=params["cpu_mean"],
            memory_mean=params["memory_mean"],
            execution_time_mean=params["execution_time_mean"],
        )

        print(f"    CPU:       {metrics['cpu_usage']:.2f}%")
        print(f"    Memory:    {metrics['memory_usage']:.2f} MB")
        print(f"    Exec Time: {metrics['execution_time']:.4f}s")

        write_metrics(
            application=app_slug,
            workflow=wf_slug,
            commit_id=commit_id,
            commit_number=commit_number,
            **metrics,
        )

        regressions = detect_regressions(
            application=app_slug,
            workflow=wf_slug,
            commit_id=commit_id,
            new_values=metrics,
        )

        if regressions:
            any_regressions = True
            for r in regressions:
                print(
                    f"    REGRESSION: {r.metric} z={r.z_score:.2f} ({r.severity})"
                )
        else:
            print("    No regressions detected.")

    return any_regressions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run performance benchmarks from config"
    )
    parser.add_argument(
        "--config",
        default="benchmark_config.json",
        help="Path to benchmark config JSON file (default: benchmark_config.json)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    had_regressions = run_benchmark(config)

    print("\n" + "=" * 60)
    if had_regressions:
        print("Regressions detected! Check InfluxDB/Grafana for details.")
    else:
        print("All benchmarks passed without regressions.")


if __name__ == "__main__":
    main()
