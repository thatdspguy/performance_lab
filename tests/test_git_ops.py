import subprocess
from unittest.mock import MagicMock, patch

import pytest

from backend.git_ops import GitError, _run_git, commit_and_push, clone_repo


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


@patch("backend.git_ops._get_current_branch", return_value="main")
@patch("backend.git_ops._has_staged_changes", return_value=True)
@patch("backend.git_ops._run_git")
def test_commit_and_push_with_cwd(mock_git, mock_staged, mock_branch):
    """Test commit_and_push with an explicit cwd (for mock repos)."""
    mock_git.side_effect = [
        "",  # git add
        "",  # git commit
        "abc1234",  # git rev-parse --short HEAD
        "",  # git push
    ]
    result = commit_and_push("benchmark_config.json", "test commit", cwd="/repo")
    assert result == "abc1234"
    assert mock_git.call_count == 4


@patch("backend.git_ops._get_current_branch", return_value="main")
@patch("backend.git_ops._has_staged_changes", return_value=True)
@patch("backend.git_ops._run_git")
@patch("backend.git_ops.get_performance_lab_root")
def test_commit_and_push_default_cwd(mock_root, mock_git, mock_staged, mock_branch):
    """Test commit_and_push without cwd falls back to performance lab root."""
    from pathlib import Path

    mock_root.return_value = Path("/performance_lab")
    mock_git.side_effect = [
        "",  # git add
        "",  # git commit
        "abc1234",  # git rev-parse --short HEAD
        "",  # git push
    ]
    result = commit_and_push("benchmark_config.json", "test commit")
    assert result == "abc1234"


@patch("backend.git_ops._has_staged_changes", return_value=False)
@patch("backend.git_ops._run_git")
def test_commit_and_push_no_changes(mock_git, mock_staged):
    mock_git.side_effect = [
        "",  # git add
    ]
    with pytest.raises(GitError, match="No changes to commit"):
        commit_and_push("benchmark_config.json", "test commit", cwd="/repo")


@patch("backend.git_ops._get_current_branch", return_value="feature-x")
@patch("backend.git_ops._has_staged_changes", return_value=True)
@patch("backend.git_ops._run_git")
def test_commit_and_push_wrong_branch(mock_git, mock_staged, mock_branch):
    mock_git.side_effect = [
        "",  # git add
        "",  # git commit
        "abc1234",  # git rev-parse --short HEAD
    ]
    with pytest.raises(GitError, match="requires the 'main' branch"):
        commit_and_push("benchmark_config.json", "test commit", cwd="/repo")


@patch("backend.git_ops._run_git")
def test_clone_repo_new(mock_git, tmp_path):
    """Clone into a new directory."""
    target = tmp_path / "mock_final_cut"
    clone_repo("https://github.com/test/repo.git", target)
    mock_git.assert_called_once_with("clone", "https://github.com/test/repo.git", str(target))


@patch("backend.git_ops._run_git")
def test_clone_repo_existing(mock_git, tmp_path):
    """Pull if repo already exists."""
    target = tmp_path / "mock_final_cut"
    target.mkdir()
    (target / ".git").mkdir()
    clone_repo("https://github.com/test/repo.git", target)
    mock_git.assert_called_once_with("pull", cwd=str(target))
