import subprocess
from unittest.mock import MagicMock, patch

import pytest

from backend.git_ops import GitError, _run_git, commit_and_push


@patch("backend.git_ops.subprocess.run")
def test_run_git_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="output\n", stderr="")
    result = _run_git("status")
    assert result == "output"
    mock_run.assert_called_once()


@patch("backend.git_ops.subprocess.run")
def test_run_git_failure(mock_run):
    mock_run.return_value = MagicMock(
        returncode=1, stdout="", stderr="fatal: error"
    )
    with pytest.raises(GitError, match="git status failed"):
        _run_git("status")


@patch("backend.git_ops.subprocess.run")
def test_run_git_timeout(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=30)
    with pytest.raises(GitError, match="timed out"):
        _run_git("push")


@patch("backend.git_ops.subprocess.run")
def test_run_git_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError()
    with pytest.raises(GitError, match="not installed"):
        _run_git("status")


@patch("backend.git_ops._run_git")
def test_commit_and_push(mock_git):
    mock_git.side_effect = [
        "/repo",  # get_repo_root -> rev-parse --show-toplevel
        "",  # git add
        "",  # git commit
        "abc1234",  # git rev-parse --short HEAD
        "",  # git push
    ]
    result = commit_and_push("benchmark_config.json", "test commit")
    assert result == "abc1234"
    assert mock_git.call_count == 5
