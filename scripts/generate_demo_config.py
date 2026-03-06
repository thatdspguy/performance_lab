#!/usr/bin/env python3
"""Generate demo_config.json from docs/demo-scenario.md.

Parses the markdown scenario tables and produces the JSON config file
that run_demo.py consumes.

Usage:
    uv run python scripts/generate_demo_config.py
    uv run python scripts/generate_demo_config.py --scenario docs/demo-scenario.md --output scripts/demo_config.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Mapping from markdown section header keywords to app config.
# The key is a substring matched against ## headings in the markdown.
APP_TABLE_DEFS: dict[str, dict] = {
    "Final Cut Pro": {
        "slug": "final_cut",
        "name": "Final Cut Pro",
        "column_to_slug": {
            "Importing Video": "importing_video",
            "Editing Video": "editing_video",
            "Exporting Video": "exporting_video",
        },
    },
    "Logic Pro": {
        "slug": "logic_pro",
        "name": "Logic Pro",
        "column_to_slug": {
            "Loading Project": "loading_project",
            "Real-Time Playback": "realtime_playback",
            "Bouncing Final Mix": "bouncing_final_mix",
        },
    },
    "Xcode": {
        "slug": "xcode",
        "name": "Xcode",
        "column_to_slug": {
            "Clean Build": "clean_build",
            "Incremental Build": "incremental_build",
            "Run Unit Tests": "run_unit_tests",
        },
    },
}


def parse_metric_cell(cell: str) -> tuple[float, float, float]:
    """Parse a cell like '40 / 900 / 3.0' into (cpu, memory, time)."""
    parts = [p.strip() for p in cell.split("/")]
    if len(parts) != 3:
        raise ValueError(f"Expected 3 metric values in '{cell}', got {len(parts)}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def find_app_section(lines: list[str], app_display_name: str) -> int:
    """Find the line index of the ## header containing the app name."""
    for i, line in enumerate(lines):
        if line.startswith("## ") and app_display_name in line:
            return i
    raise ValueError(f"Could not find section header for '{app_display_name}'")


def parse_table_for_app(
    lines: list[str], start_idx: int, app_def: dict
) -> list[dict]:
    """Parse the markdown table starting near start_idx.

    Returns a list of commit dicts matching the JSON schema.
    """
    column_to_slug = app_def["column_to_slug"]

    # Find the header row (starts with | # |)
    header_idx = None
    for i in range(start_idx, min(start_idx + 15, len(lines))):
        if lines[i].strip().startswith("| # |") or lines[i].strip().startswith("|---|"):
            # Look one line back for header if this is the separator
            if lines[i].strip().startswith("|---|"):
                header_idx = i - 1
            else:
                header_idx = i
            break

    if header_idx is None:
        raise ValueError(
            f"Could not find table header near line {start_idx} "
            f"for app '{app_def['name']}'"
        )

    # Parse column headers to determine workflow column positions
    header_cells = [c.strip() for c in lines[header_idx].split("|")]
    # Remove empty strings from leading/trailing pipes
    header_cells = [c for c in header_cells if c]

    # Build mapping: column index -> workflow slug
    # header_cells[0] = "#", [1] = "Commit Message", [2..4] = workflow columns, [5] = "Notes"
    col_to_slug: dict[int, str] = {}
    for col_idx, header in enumerate(header_cells):
        for display_name, slug in column_to_slug.items():
            if display_name in header:
                col_to_slug[col_idx] = slug
                break

    if len(col_to_slug) != len(column_to_slug):
        raise ValueError(
            f"Expected {len(column_to_slug)} workflow columns, "
            f"found {len(col_to_slug)} in header: {header_cells}"
        )

    # Skip the separator row (|---|---|...)
    data_start = header_idx + 2

    commits = []
    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        # Stop at blank line, horizontal rule, or next section
        if not line or line.startswith("---") or line.startswith("##") or line.startswith("**"):
            break
        if not line.startswith("|"):
            break

        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]  # drop empties from leading/trailing |

        if len(cells) < 4:
            continue

        commit_number = int(cells[0])
        commit_message = cells[1].strip()

        workflows = {}
        for col_idx, slug in col_to_slug.items():
            cpu, mem, time_val = parse_metric_cell(cells[col_idx])
            workflows[slug] = {
                "cpu_mean": cpu,
                "memory_mean": mem,
                "execution_time_mean": time_val,
            }

        commits.append({
            "commit_number": commit_number,
            "commit_message": commit_message,
            "workflows": workflows,
        })

    return commits


def generate_config(scenario_path: Path) -> dict:
    """Parse the full scenario file and return the config dict."""
    text = scenario_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    apps = {}
    for display_name, app_def in APP_TABLE_DEFS.items():
        section_idx = find_app_section(lines, display_name)
        commits = parse_table_for_app(lines, section_idx, app_def)
        slug = app_def["slug"]
        apps[slug] = {
            "name": app_def["name"],
            "workflow_slugs": list(app_def["column_to_slug"].values()),
            "commits": commits,
        }

    return {
        "settings": {
            "batch_size": 3,
            "delay_between_batches_seconds": 90,
            "apps": list(apps.keys()),
            "commit_order": "interleaved",
        },
        "apps": apps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate demo config JSON from scenario markdown"
    )
    parser.add_argument(
        "--scenario",
        default="docs/demo-scenario.md",
        help="Path to the demo scenario markdown file (default: docs/demo-scenario.md)",
    )
    parser.add_argument(
        "--output",
        default="scripts/demo_config.json",
        help="Output path for the generated JSON config (default: scripts/demo_config.json)",
    )
    args = parser.parse_args()

    scenario_path = Path(args.scenario)
    if not scenario_path.exists():
        print(f"Error: scenario file not found: {scenario_path}", file=sys.stderr)
        sys.exit(1)

    config = generate_config(scenario_path)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    total_commits = sum(len(a["commits"]) for a in config["apps"].values())
    print(
        f"Generated {output_path} with {len(config['apps'])} apps, "
        f"{total_commits} total commits"
    )


if __name__ == "__main__":
    main()
