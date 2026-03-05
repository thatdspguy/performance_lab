from unittest.mock import patch

from backend.git_ops import GitError
from backend.models import AppBenchmarkConfig, PipelineRequest
from backend.pipeline import run_full_pipeline


def _make_request() -> PipelineRequest:
    return PipelineRequest(
        apps={
            "final_cut": AppBenchmarkConfig(
                cpu_mean=45,
                cpu_std=4,
                memory_mean=800,
                memory_std=50,
                execution_time_mean=2.5,
                execution_time_std=0.3,
            ),
        },
        commit_message="test commit",
    )


@patch("backend.pipeline.commit_and_push", return_value="abc1234")
@patch("backend.pipeline.write_benchmark_config")
def test_run_full_pipeline_success(mock_write_config, mock_commit):
    req = _make_request()
    success, message, commit_hash = run_full_pipeline(req)
    assert success is True
    assert commit_hash == "abc1234"
    mock_write_config.assert_called_once()
    mock_commit.assert_called_once()


@patch("backend.pipeline.commit_and_push")
@patch("backend.pipeline.write_benchmark_config")
def test_run_full_pipeline_git_error(mock_write_config, mock_commit):
    mock_commit.side_effect = GitError("push failed: authentication error")
    req = _make_request()
    success, message, commit_hash = run_full_pipeline(req)
    assert success is False
    assert "push failed" in message
    assert commit_hash is None
