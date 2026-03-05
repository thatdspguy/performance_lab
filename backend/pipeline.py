"""Full pipeline: write benchmark config, commit, and push."""

from __future__ import annotations

import json
from pathlib import Path

from backend.git_ops import GitError, commit_and_push, get_repo_root
from backend.models import PipelineRequest

CONFIG_FILENAME = "benchmark_config.json"


def write_benchmark_config(request: PipelineRequest) -> Path:
    """Write benchmark config JSON to the repository root.

    Returns the absolute path to the written file.
    """
    repo_root = get_repo_root()
    config_path = repo_root / CONFIG_FILENAME

    config_data = {
        "apps": {
            slug: {
                "cpu_mean": app_config.cpu_mean,
                "cpu_std": app_config.cpu_std,
                "memory_mean": app_config.memory_mean,
                "memory_std": app_config.memory_std,
                "execution_time_mean": app_config.execution_time_mean,
                "execution_time_std": app_config.execution_time_std,
            }
            for slug, app_config in request.apps.items()
        }
    }

    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
        f.write("\n")

    return config_path


def run_full_pipeline(
    request: PipelineRequest,
) -> tuple[bool, str, str | None]:
    """Execute the full pipeline: write config -> git add -> commit -> push.

    Returns:
        (success, message, commit_hash_or_none)
    """
    try:
        write_benchmark_config(request)
        commit_hash = commit_and_push(
            file_path=CONFIG_FILENAME,
            message=request.commit_message,
        )
        return True, f"Committed and pushed as {commit_hash}", commit_hash
    except GitError as exc:
        return False, str(exc), None
