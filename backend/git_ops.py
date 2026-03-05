"""Git operations for the full pipeline commit mode."""

from __future__ import annotations

import subprocess
from pathlib import Path


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
    # exit 0 = no diff (no staged changes), exit 1 = there are diffs
    return result.returncode != 0


def get_repo_root() -> Path:
    """Find the git repository root. Raises GitError if not in a repo."""
    output = _run_git("rev-parse", "--show-toplevel")
    return Path(output)


def commit_and_push(file_path: str, message: str) -> str:
    """Stage a file, commit, and push to origin.

    Args:
        file_path: Path to the file to stage (relative to repo root).
        message: Commit message.

    Returns:
        The short commit hash of the new commit.

    Raises:
        GitError: If any git operation fails.
    """
    repo_root = str(get_repo_root())
    _run_git("add", file_path, cwd=repo_root)

    if not _has_staged_changes(repo_root):
        raise GitError(
            "No changes to commit — the benchmark config is identical "
            "to the version already committed."
        )

    _run_git("commit", "-m", message, cwd=repo_root)
    commit_hash = _run_git("rev-parse", "--short", "HEAD", cwd=repo_root)
    _run_git("push", cwd=repo_root)
    return commit_hash
