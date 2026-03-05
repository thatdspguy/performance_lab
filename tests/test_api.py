from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_get_apps():
    response = client.get("/api/apps")
    assert response.status_code == 200
    apps = response.json()
    assert len(apps) == 3
    slugs = {a["slug"] for a in apps}
    assert slugs == {"final_cut", "logic_pro", "xcode"}
    # Verify structure
    for app_info in apps:
        assert "name" in app_info
        assert "cpu_mean" in app_info
        assert "cpu_std" in app_info
        assert "memory_mean" in app_info


@patch("backend.main.detect_regressions", return_value=[])
@patch("backend.main.write_metrics")
@patch("backend.main.get_commit_count", return_value=5)
def test_simulate_success(mock_count, mock_write, mock_detect):
    response = client.post(
        "/api/simulate",
        json={
            "application": "final_cut",
            "cpu_mean": 45,
            "cpu_std": 4,
            "memory_mean": 800,
            "memory_std": 50,
            "execution_time_mean": 2.5,
            "execution_time_std": 0.3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "final_cut"
    assert data["commit_number"] == 6
    assert len(data["commit_id"]) == 8
    assert "cpu_usage" in data["metrics"]
    assert "memory_usage" in data["metrics"]
    assert "execution_time" in data["metrics"]
    assert isinstance(data["regressions"], list)
    mock_write.assert_called_once()


def test_simulate_unknown_app():
    response = client.post(
        "/api/simulate",
        json={
            "application": "unknown_app",
            "cpu_mean": 45,
            "cpu_std": 4,
            "memory_mean": 800,
            "memory_std": 50,
            "execution_time_mean": 2.5,
            "execution_time_std": 0.3,
        },
    )
    assert response.status_code == 400


@patch("backend.main.query_recent_metrics", return_value=[])
def test_get_metrics_empty(mock_query):
    response = client.get("/api/metrics?application=final_cut")
    assert response.status_code == 200
    assert response.json() == []


def test_get_metrics_unknown_app():
    response = client.get("/api/metrics?application=nope")
    assert response.status_code == 400


@patch("backend.main.query_recent_regressions", return_value=[])
def test_get_regressions_empty(mock_query):
    response = client.get("/api/regressions")
    assert response.status_code == 200
    assert response.json() == []


@patch(
    "backend.main.run_full_pipeline",
    return_value=(True, "Committed as abc1234", "abc1234"),
)
def test_pipeline_success(mock_pipeline):
    response = client.post(
        "/api/pipeline",
        json={
            "apps": {
                "final_cut": {
                    "cpu_mean": 45,
                    "cpu_std": 4,
                    "memory_mean": 800,
                    "memory_std": 50,
                    "execution_time_mean": 2.5,
                    "execution_time_std": 0.3,
                }
            },
            "commit_message": "test commit",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["commit_id"] == "abc1234"


def test_pipeline_unknown_app():
    response = client.post(
        "/api/pipeline",
        json={
            "apps": {
                "unknown_app": {
                    "cpu_mean": 1,
                    "cpu_std": 1,
                    "memory_mean": 1,
                    "memory_std": 1,
                    "execution_time_mean": 1,
                    "execution_time_std": 1,
                }
            },
        },
    )
    assert response.status_code == 400


@patch(
    "backend.main.run_full_pipeline",
    return_value=(False, "git push failed", None),
)
def test_pipeline_git_failure(mock_pipeline):
    response = client.post(
        "/api/pipeline",
        json={
            "apps": {
                "final_cut": {
                    "cpu_mean": 45,
                    "cpu_std": 4,
                    "memory_mean": 800,
                    "memory_std": 50,
                    "execution_time_mean": 2.5,
                    "execution_time_std": 0.3,
                }
            },
        },
    )
    assert response.status_code == 500
