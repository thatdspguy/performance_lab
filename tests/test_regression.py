from unittest.mock import patch

from backend.models import RegressionInfo
from backend.regression import detect_regressions


def _make_recent_data(metric: str, values: list[float]) -> list[dict]:
    """Build a list of metric rows suitable for mocking query_recent_metrics."""
    return [
        {
            "time": f"2025-01-01T00:0{i}:00+00:00",
            "application": "test_app",
            "commit_id": f"abc{i:04d}",
            "commit_number": i,
            "cpu_usage": v if metric == "cpu_usage" else 50.0,
            "memory_usage": v if metric == "memory_usage" else 800.0,
            "execution_time": v if metric == "execution_time" else 2.5,
        }
        for i, v in enumerate(values)
    ]


@patch("backend.regression.write_regression_event")
@patch("backend.regression.query_recent_metrics")
def test_no_regression_normal_value(mock_query, mock_write):
    """A value within 2 std devs should produce no regression."""
    data = _make_recent_data("cpu_usage", [50.0] * 10)
    mock_query.return_value = data

    results = detect_regressions(
        application="test_app",
        commit_id="deadbeef",
        new_values={"cpu_usage": 50.5, "memory_usage": 800.0, "execution_time": 2.5},
    )
    assert results == []
    mock_write.assert_not_called()


@patch("backend.regression.write_regression_event")
@patch("backend.regression.query_recent_metrics")
def test_strong_regression_detected(mock_query, mock_write):
    """A value far from the mean should trigger a strong regression."""
    # baseline: mean=50, std~0.5 -> value 55 gives z=10 -> strong
    data = _make_recent_data(
        "cpu_usage",
        [49.5, 50.5, 50.0, 49.8, 50.2, 50.1, 49.9, 50.3, 49.7, 50.0],
    )
    mock_query.return_value = data

    results = detect_regressions(
        application="test_app",
        commit_id="deadbeef",
        new_values={"cpu_usage": 55.0, "memory_usage": 800.0, "execution_time": 2.5},
    )

    cpu_regressions = [r for r in results if r.metric == "cpu_usage"]
    assert len(cpu_regressions) == 1
    assert cpu_regressions[0].severity == "strong"
    assert cpu_regressions[0].z_score > 3


@patch("backend.regression.write_regression_event")
@patch("backend.regression.query_recent_metrics")
def test_possible_regression_detected(mock_query, mock_write):
    """A value between 2 and 3 std devs should be 'possible'."""
    # baseline: mean=50, population std=2.0 -> value 54.5 gives z=2.25 -> possible
    data = _make_recent_data(
        "cpu_usage",
        [48.0, 52.0, 48.0, 52.0, 48.0, 52.0, 48.0, 52.0, 48.0, 52.0],
    )
    mock_query.return_value = data

    results = detect_regressions(
        application="test_app",
        commit_id="deadbeef",
        new_values={"cpu_usage": 54.5, "memory_usage": 800.0, "execution_time": 2.5},
    )

    cpu_regressions = [r for r in results if r.metric == "cpu_usage"]
    assert len(cpu_regressions) == 1
    assert cpu_regressions[0].severity == "possible"
    assert 2 < cpu_regressions[0].z_score < 3


@patch("backend.regression.write_regression_event")
@patch("backend.regression.query_recent_metrics")
def test_insufficient_data_skips(mock_query, mock_write):
    """With fewer than MIN_DATA_POINTS, no regressions are reported."""
    data = _make_recent_data("cpu_usage", [50.0, 50.0, 50.0])
    mock_query.return_value = data

    results = detect_regressions(
        application="test_app",
        commit_id="deadbeef",
        new_values={"cpu_usage": 100.0, "memory_usage": 800.0, "execution_time": 2.5},
    )
    assert results == []


@patch("backend.regression.write_regression_event")
@patch("backend.regression.query_recent_metrics")
def test_zero_std_skips(mock_query, mock_write):
    """If all values are identical (std=0), skip regression detection."""
    data = _make_recent_data("cpu_usage", [50.0] * 10)
    mock_query.return_value = data

    # cpu values all 50.0 -> std=0 -> skip
    # But memory and exec_time also 800.0 and 2.5 with std=0
    results = detect_regressions(
        application="test_app",
        commit_id="deadbeef",
        new_values={"cpu_usage": 100.0, "memory_usage": 800.0, "execution_time": 2.5},
    )
    assert results == []
