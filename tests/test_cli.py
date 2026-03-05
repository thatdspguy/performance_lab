from unittest.mock import patch

from backend.cli import run_benchmark


SAMPLE_CONFIG = {
    "apps": {
        "final_cut": {
            "cpu_mean": 45,
            "cpu_std": 4,
            "memory_mean": 800,
            "memory_std": 50,
            "execution_time_mean": 2.5,
            "execution_time_std": 0.3,
        }
    }
}


@patch("backend.cli.detect_regressions", return_value=[])
@patch("backend.cli.write_metrics")
@patch("backend.cli.get_commit_count", return_value=5)
def test_run_benchmark_no_regressions(mock_count, mock_write, mock_detect):
    result = run_benchmark(SAMPLE_CONFIG)
    assert result is False
    mock_write.assert_called_once()
    mock_detect.assert_called_once()


@patch("backend.cli.detect_regressions", return_value=[])
@patch("backend.cli.write_metrics")
@patch("backend.cli.get_commit_count", return_value=0)
def test_run_benchmark_skips_unknown_app(mock_count, mock_write, mock_detect):
    config = {
        "apps": {
            "nonexistent_app": {
                "cpu_mean": 1,
                "cpu_std": 1,
                "memory_mean": 1,
                "memory_std": 1,
                "execution_time_mean": 1,
                "execution_time_std": 1,
            }
        }
    }
    result = run_benchmark(config)
    assert result is False
    mock_write.assert_not_called()


@patch("backend.cli.detect_regressions", return_value=[])
@patch("backend.cli.write_metrics")
@patch("backend.cli.get_commit_count", return_value=0)
def test_run_benchmark_multiple_apps(mock_count, mock_write, mock_detect):
    config = {
        "apps": {
            "final_cut": {
                "cpu_mean": 45,
                "cpu_std": 4,
                "memory_mean": 800,
                "memory_std": 50,
                "execution_time_mean": 2.5,
                "execution_time_std": 0.3,
            },
            "xcode": {
                "cpu_mean": 55,
                "cpu_std": 5,
                "memory_mean": 1200,
                "memory_std": 80,
                "execution_time_mean": 4.0,
                "execution_time_std": 0.5,
            },
        }
    }
    run_benchmark(config)
    assert mock_write.call_count == 2
    assert mock_detect.call_count == 2
