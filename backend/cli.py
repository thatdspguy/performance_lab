"""CLI entry point for running benchmarks from config file.

Usage:
    uv run python -m backend.cli [--config benchmark_config.json]

Reads benchmark config, simulates metrics, writes to InfluxDB, and runs
regression detection for each configured application.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from backend.apps import APP_DEFINITIONS
from backend.metrics import get_commit_count, write_metrics
from backend.regression import detect_regressions
from backend.simulator import generate_commit_id, simulate_metrics


def load_config(config_path: str) -> dict:
    """Load benchmark config JSON."""
    path = Path(config_path)
    if not path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def run_benchmark(config: dict) -> bool:
    """Run benchmark simulation for all apps in config.

    Returns True if any regressions were detected.
    """
    any_regressions = False
    apps = config.get("apps", {})

    for app_slug, params in apps.items():
        if app_slug not in APP_DEFINITIONS:
            print(
                f"Warning: unknown app '{app_slug}', skipping", file=sys.stderr
            )
            continue

        print(f"\n--- Benchmarking: {app_slug} ---")

        commit_id = generate_commit_id()
        commit_number = get_commit_count(app_slug) + 1

        metrics = simulate_metrics(
            cpu_mean=params["cpu_mean"],
            cpu_std=params["cpu_std"],
            memory_mean=params["memory_mean"],
            memory_std=params["memory_std"],
            execution_time_mean=params["execution_time_mean"],
            execution_time_std=params["execution_time_std"],
        )

        print(f"  Commit: {commit_id} (#{commit_number})")
        print(f"  CPU: {metrics['cpu_usage']}%")
        print(f"  Memory: {metrics['memory_usage']} MB")
        print(f"  Exec Time: {metrics['execution_time']}s")

        write_metrics(
            application=app_slug,
            commit_id=commit_id,
            commit_number=commit_number,
            **metrics,
        )

        regressions = detect_regressions(
            application=app_slug,
            commit_id=commit_id,
            new_values=metrics,
        )

        if regressions:
            any_regressions = True
            for r in regressions:
                print(
                    f"  REGRESSION: {r.metric} z={r.z_score} ({r.severity})"
                )
        else:
            print("  No regressions detected.")

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

    if had_regressions:
        print(
            "\n*** Regressions detected! Check InfluxDB/Grafana for details. ***"
        )
    else:
        print("\nAll benchmarks passed without regressions.")


if __name__ == "__main__":
    main()
