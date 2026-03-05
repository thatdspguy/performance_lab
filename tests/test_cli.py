import sys
from unittest.mock import patch

import pytest

from backend.cli import run_benchmark


SAMPLE_CONFIG = {
    "app": "final_cut",
    "workflows": {
        "importing_video": {
            "cpu_mean": 40,
            "memory_mean": 900,
            "execution_time_mean": 3.0,
        },
    },
}


@patch("backend.cli.detect_regressions", return_value=[])
@patch("backend.cli.write_metrics")
@patch("backend.cli.get_commit_count", return_value=5)
def test_run_benchmark_no_regressions(mock_count, mock_write, mock_detect):
    result = run_benchmark(SAMPLE_CONFIG)
    assert result is False
    mock_write.assert_called_once()
    mock_detect.assert_called_once()


def test_run_benchmark_unknown_app():
    config = {
        "app": "nonexistent_app",
        "workflows": {
            "test_wf": {
                "cpu_mean": 1,
                "memory_mean": 1,
                "execution_time_mean": 1,
            },
        },
    }
    with pytest.raises(SystemExit):
        run_benchmark(config)


@patch("backend.cli.detect_regressions", return_value=[])
@patch("backend.cli.write_metrics")
@patch("backend.cli.get_commit_count", return_value=0)
def test_run_benchmark_multiple_workflows(mock_count, mock_write, mock_detect):
    config = {
        "app": "final_cut",
        "workflows": {
            "importing_video": {
                "cpu_mean": 40,
                "memory_mean": 900,
                "execution_time_mean": 3.0,
            },
            "editing_video": {
                "cpu_mean": 55,
                "memory_mean": 1200,
                "execution_time_mean": 2.0,
            },
        },
    }
    run_benchmark(config)
    assert mock_write.call_count == 2
    assert mock_detect.call_count == 2
