#!/usr/bin/env python3
"""Demo runner: step through the demo scenario by driving the pipeline.

Reads a demo config JSON file and executes commits in order, calling
the existing run_app_pipeline() for each commit with configurable
batching and delays.

Usage:
    uv run python scripts/run_demo.py scripts/demo_config.json
    uv run python scripts/run_demo.py scripts/demo_config.json --batch-size 1 --delay 120
    uv run python scripts/run_demo.py scripts/demo_config.json --apps final_cut,xcode
    uv run python scripts/run_demo.py scripts/demo_config.json --start-at 5
    uv run python scripts/run_demo.py scripts/demo_config.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Add project root to path so we can import backend modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models import PipelineRequest, WorkflowConfig
from backend.pipeline import run_app_pipeline


@dataclass
class DemoStep:
    """One unit of work: a single app commit."""

    app_slug: str
    app_name: str
    commit_number: int
    commit_message: str
    workflows: dict[str, WorkflowConfig]


def load_config(config_path: Path) -> dict:
    """Load and validate the demo config JSON."""
    with open(config_path) as f:
        config = json.load(f)

    if "settings" not in config:
        print("Error: config missing 'settings' key", file=sys.stderr)
        sys.exit(1)
    if "apps" not in config:
        print("Error: config missing 'apps' key", file=sys.stderr)
        sys.exit(1)

    for slug, app_data in config["apps"].items():
        if "commits" not in app_data:
            print(
                f"Error: app '{slug}' missing 'commits' key", file=sys.stderr
            )
            sys.exit(1)

    return config


def build_step_sequence(
    config: dict, target_apps: list[str]
) -> list[DemoStep]:
    """Build the ordered list of DemoSteps from config.

    If commit_order is "interleaved" (default):
        commit 1 for all apps, commit 2 for all apps, ...

    If commit_order is "sequential":
        all commits for app 1, then all for app 2, ...
    """
    settings = config["settings"]
    commit_order = settings.get("commit_order", "interleaved")
    apps_data = config["apps"]

    # Filter and preserve order from target_apps
    ordered_slugs = [s for s in target_apps if s in apps_data]

    def make_step(slug: str, commit: dict) -> DemoStep:
        return DemoStep(
            app_slug=slug,
            app_name=apps_data[slug]["name"],
            commit_number=commit["commit_number"],
            commit_message=commit["commit_message"],
            workflows={
                wf_slug: WorkflowConfig(**wf_data)
                for wf_slug, wf_data in commit["workflows"].items()
            },
        )

    steps: list[DemoStep] = []

    if commit_order == "interleaved":
        max_commits = max(
            len(apps_data[s]["commits"]) for s in ordered_slugs
        )
        for commit_idx in range(max_commits):
            for slug in ordered_slugs:
                commits = apps_data[slug]["commits"]
                if commit_idx < len(commits):
                    steps.append(make_step(slug, commits[commit_idx]))
    else:  # sequential
        for slug in ordered_slugs:
            for commit in apps_data[slug]["commits"]:
                steps.append(make_step(slug, commit))

    return steps


def execute_step(step: DemoStep, dry_run: bool = False) -> bool:
    """Execute a single demo step by calling run_app_pipeline.

    Returns True on success, False on failure.
    """
    request = PipelineRequest(
        application=step.app_slug,
        workflows=step.workflows,
        commit_message=step.commit_message,
    )

    if dry_run:
        wf_summary = ", ".join(
            f"{slug}(cpu={wf.cpu_mean}, mem={wf.memory_mean}, "
            f"time={wf.execution_time_mean})"
            for slug, wf in step.workflows.items()
        )
        print(f"  [DRY RUN] Would commit to {step.app_slug}: {step.commit_message}")
        print(f"            Workflows: {wf_summary}")
        return True

    success, message, commit_hash = run_app_pipeline(request)
    if success:
        print(f"  OK: {message}")
    else:
        print(f"  FAILED: {message}")
    return success


def run_demo(
    steps: list[DemoStep],
    batch_size: int,
    delay_seconds: float,
    dry_run: bool = False,
    on_error: str = "ask",
) -> None:
    """Main execution loop with batching and delay."""
    total = len(steps)
    completed = 0
    failed = 0
    batch_count = 0

    print(f"\nDemo Runner: {total} steps to execute")
    print(f"  Batch size: {batch_size}")
    print(f"  Delay between batches: {delay_seconds}s")
    print(f"  Error handling: {on_error}")
    if dry_run:
        print("  MODE: DRY RUN (no actual commits)")
    print("=" * 60)

    for i, step in enumerate(steps):
        step_num = i + 1

        print(
            f"\n[{step_num}/{total}] {step.app_name} - "
            f"Commit #{step.commit_number}"
        )
        print(f"  Message: {step.commit_message}")

        success = execute_step(step, dry_run=dry_run)

        if success:
            completed += 1
        else:
            failed += 1
            if on_error == "abort":
                print("\nAborting due to error (--on-error=abort)")
                break
            elif on_error == "ask":
                try:
                    response = input("\nContinue? [y/N] ").strip().lower()
                except EOFError:
                    print("\nNo input available. Aborting.")
                    break
                if response not in ("y", "yes"):
                    print("Aborted by user.")
                    break
            # on_error == "continue" falls through

        batch_count += 1
        if batch_count >= batch_size and step_num < total:
            batch_count = 0
            if not dry_run and delay_seconds > 0:
                print(
                    f"\n--- Batch complete. Waiting {delay_seconds}s "
                    f"for CI to finish... ---"
                )
                try:
                    time.sleep(delay_seconds)
                except KeyboardInterrupt:
                    print("\nInterrupted during wait. Stopping.")
                    break

    print("\n" + "=" * 60)
    skipped = total - completed - failed
    print(
        f"Demo complete: {completed} succeeded, {failed} failed, "
        f"{skipped} skipped"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the performance lab demo scenario"
    )
    parser.add_argument(
        "config",
        help="Path to the demo config JSON file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override batch size from config (commits per batch)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Override delay between batches in seconds",
    )
    parser.add_argument(
        "--apps",
        type=str,
        default=None,
        help="Comma-separated list of app slugs to target (overrides config)",
    )
    parser.add_argument(
        "--start-at",
        type=int,
        default=1,
        help="Start at this commit number, skipping earlier ones (default: 1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without actually committing",
    )
    parser.add_argument(
        "--on-error",
        choices=["ask", "continue", "abort"],
        default="ask",
        help="What to do on error: ask (interactive), continue, or abort (default: ask)",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    settings = config["settings"]

    # CLI args override config settings
    batch_size = args.batch_size or settings.get("batch_size", 3)
    delay = (
        args.delay
        if args.delay is not None
        else settings.get("delay_between_batches_seconds", 90)
    )
    target_apps = (
        args.apps.split(",")
        if args.apps
        else settings.get("apps", list(config["apps"].keys()))
    )

    steps = build_step_sequence(config, target_apps)

    if args.start_at > 1:
        steps = [s for s in steps if s.commit_number >= args.start_at]
        print(f"Starting at commit #{args.start_at} ({len(steps)} steps remaining)")

    if not steps:
        print("No steps to execute.")
        sys.exit(0)

    run_demo(
        steps=steps,
        batch_size=batch_size,
        delay_seconds=delay,
        dry_run=args.dry_run,
        on_error=args.on_error,
    )


if __name__ == "__main__":
    main()
