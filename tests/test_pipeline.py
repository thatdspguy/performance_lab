from unittest.mock import patch

from backend.git_ops import GitError
from backend.models import PipelineRequest, WorkflowConfig
from backend.pipeline import run_app_pipeline


def _make_request() -> PipelineRequest:
    return PipelineRequest(
        application="final_cut",
        workflows={
            "importing_video": WorkflowConfig(
                cpu_mean=40,
                memory_mean=900,
                execution_time_mean=3.0,
            ),
        },
        commit_message="test commit",
    )


@patch("backend.pipeline.commit_and_push", return_value="abc1234")
@patch("backend.pipeline.write_workflow_config")
@patch("backend.pipeline.get_repo_path")
def test_run_app_pipeline_success(mock_path, mock_write_config, mock_commit, tmp_path):
    mock_path.return_value = tmp_path
    req = _make_request()
    success, message, commit_hash = run_app_pipeline(req)
    assert success is True
    assert commit_hash == "abc1234"
    mock_write_config.assert_called_once()
    mock_commit.assert_called_once()


@patch("backend.pipeline.commit_and_push")
@patch("backend.pipeline.write_workflow_config")
@patch("backend.pipeline.get_repo_path")
def test_run_app_pipeline_git_error(mock_path, mock_write_config, mock_commit, tmp_path):
    mock_path.return_value = tmp_path
    mock_commit.side_effect = GitError("push failed: authentication error")
    req = _make_request()
    success, message, commit_hash = run_app_pipeline(req)
    assert success is False
    assert "push failed" in message
    assert commit_hash is None
