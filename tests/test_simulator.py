from backend.simulator import get_commit_id, simulate_metrics


def test_get_commit_id_returns_string():
    cid = get_commit_id()
    assert isinstance(cid, str)
    assert len(cid) > 0


def test_simulate_metrics_keys():
    result = simulate_metrics(
        cpu_mean=50,
        memory_mean=800,
        execution_time_mean=2.5,
    )
    assert set(result.keys()) == {"cpu_usage", "memory_usage", "execution_time"}


def test_simulate_metrics_non_negative():
    for _ in range(200):
        result = simulate_metrics(
            cpu_mean=1,
            memory_mean=1,
            execution_time_mean=0.1,
        )
        assert result["cpu_usage"] >= 0
        assert result["memory_usage"] >= 0
        assert result["execution_time"] >= 0


def test_simulate_metrics_uses_10pct_std():
    """With a large mean and 10% std, values should cluster around the mean."""
    results = [
        simulate_metrics(cpu_mean=100, memory_mean=1000, execution_time_mean=10.0)
        for _ in range(50)
    ]
    cpus = [r["cpu_usage"] for r in results]
    # 10% std = 10, so almost all values should be within 70-130
    assert all(60 < c < 140 for c in cpus)
