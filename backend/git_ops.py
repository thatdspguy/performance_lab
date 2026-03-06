"""Git operations for managing mock application repositories."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from backend.apps import APP_DEFINITIONS
from backend.config import settings

logger = logging.getLogger(__name__)


class GitError(Exception):
    """Raised when a git operation fails."""


def _run_git(*args: str, cwd: str | None = None) -> str:
    """Run a git command and return stdout. Raises GitError on failure."""
    cmd = ["git", *args]
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitError(f"git command timed out: {' '.join(cmd)}") from exc
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc

    if result.returncode != 0:
        raise GitError(
            f"git {args[0]} failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def _has_staged_changes(cwd: str) -> bool:
    """Return True if the index has staged changes versus HEAD."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=cwd,
        capture_output=True,
        timeout=30,
    )
    return result.returncode != 0


def _get_current_branch(cwd: str) -> str:
    """Return the name of the current branch."""
    return _run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)


def get_performance_lab_root() -> Path:
    """Find the performance_lab repository root."""
    output = _run_git("rev-parse", "--show-toplevel")
    return Path(output)


def get_repos_dir() -> Path:
    """Return the absolute path to the repos/ directory."""
    return get_performance_lab_root() / settings.mock_repos_dir


def clone_repo(repo_url: str, target_dir: Path) -> None:
    """Clone a repository if it doesn't exist, or pull latest if it does."""
    if target_dir.exists() and (target_dir / ".git").exists():
        logger.info("Pulling latest for %s", target_dir.name)
        _run_git("pull", cwd=str(target_dir))
    else:
        logger.info("Cloning %s into %s", repo_url, target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        _run_git("clone", repo_url, str(target_dir))


def ensure_repos_cloned() -> dict[str, Path]:
    """Clone or pull all mock app repos. Returns {slug: repo_path}."""
    repos_dir = get_repos_dir()
    repo_paths: dict[str, Path] = {}
    for slug, app_def in APP_DEFINITIONS.items():
        repo_name = app_def.repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        target = repos_dir / repo_name
        clone_repo(app_def.repo_url, target)
        repo_paths[slug] = target
    return repo_paths


def get_repo_path(app_slug: str) -> Path:
    """Return the local path for a mock app's repository."""
    app_def = APP_DEFINITIONS[app_slug]
    repo_name = app_def.repo_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return get_repos_dir() / repo_name


def commit_and_push(
    file_paths: str | list[str],
    message: str,
    cwd: str | None = None,
) -> str:
    """Stage file(s), commit, and push to origin.

    Args:
        file_paths: Path or list of paths to stage (relative to repo root).
        message: Commit message.
        cwd: Working directory (repo root). If None, uses performance_lab root.

    Returns:
        The short commit hash of the new commit.
    """
    if cwd is None:
        cwd = str(get_performance_lab_root())

    if isinstance(file_paths, str):
        file_paths = [file_paths]

    for fp in file_paths:
        _run_git("add", fp, cwd=cwd)

    if not _has_staged_changes(cwd):
        raise GitError(
            "No changes to commit — the benchmark config is identical "
            "to the version already committed."
        )

    _run_git("commit", "-m", message, cwd=cwd)
    commit_hash = _run_git("rev-parse", "--short", "HEAD", cwd=cwd)

    branch = _get_current_branch(cwd)
    if branch != "main":
        raise GitError(
            f"Pipeline requires the 'main' branch but you are on '{branch}'. "
            "Switch to main before triggering the pipeline."
        )

    _run_git("push", cwd=cwd)
    return commit_hash
