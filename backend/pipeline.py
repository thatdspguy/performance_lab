"""Pipeline: write workflow config to a mock repo, commit, and push."""

from __future__ import annotations

import json
from pathlib import Path

from backend.git_ops import GitError, commit_and_push, get_repo_path, clone_repo
from backend.apps import APP_DEFINITIONS
from backend.models import PipelineRequest

CONFIG_FILENAME = "benchmark_config.json"


def write_workflow_config(request: PipelineRequest) -> Path:
    """Write workflow benchmark config JSON to the mock app repository.

    Returns the absolute path to the written file.
    """
    app_def = APP_DEFINITIONS[request.application]
    repo_path = get_repo_path(request.application)

    # Ensure the repo is cloned
    if not (repo_path / ".git").exists():
        clone_repo(app_def.repo_url, repo_path)

    config_data = {
        "app": request.application,
        "workflows": {
            wf_slug: {
                "cpu_mean": wf_config.cpu_mean,
                "memory_mean": wf_config.memory_mean,
                "execution_time_mean": wf_config.execution_time_mean,
            }
            for wf_slug, wf_config in request.workflows.items()
        },
    }

    config_path = repo_path / CONFIG_FILENAME
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
        f.write("\n")

    return config_path


def run_app_pipeline(
    request: PipelineRequest,
) -> tuple[bool, str, str | None]:
    """Execute the pipeline for a single mock app repo.

    Writes config, commits, and pushes to the mock app's repository.

    Returns:
        (success, message, commit_hash_or_none)
    """
    try:
        write_workflow_config(request)
        repo_path = get_repo_path(request.application)
        commit_hash = commit_and_push(
            file_path=CONFIG_FILENAME,
            message=request.commit_message,
            cwd=str(repo_path),
        )
        return True, f"Committed and pushed as {commit_hash}", commit_hash
    except GitError as exc:
        return False, str(exc), None
