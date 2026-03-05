from backend.simulator import generate_commit_id, simulate_metrics


def test_generate_commit_id_length():
    cid = generate_commit_id()
    assert len(cid) == 8
    assert all(c in "0123456789abcdef" for c in cid)


def test_generate_commit_id_unique():
    ids = {generate_commit_id() for _ in range(100)}
    assert len(ids) == 100


def test_simulate_metrics_keys():
    result = simulate_metrics(
        cpu_mean=50, cpu_std=5,
        memory_mean=800, memory_std=50,
        execution_time_mean=2.5, execution_time_std=0.3,
    )
    assert set(result.keys()) == {"cpu_usage", "memory_usage", "execution_time"}


def test_simulate_metrics_non_negative():
    for _ in range(200):
        result = simulate_metrics(
            cpu_mean=1, cpu_std=10,
            memory_mean=1, memory_std=10,
            execution_time_mean=0.1, execution_time_std=1.0,
        )
        assert result["cpu_usage"] >= 0
        assert result["memory_usage"] >= 0
        assert result["execution_time"] >= 0


def test_simulate_metrics_reasonable_range():
    """With tight std dev, values should be close to the mean."""
    results = [
        simulate_metrics(
            cpu_mean=50, cpu_std=0.01,
            memory_mean=800, memory_std=0.01,
            execution_time_mean=2.5, execution_time_std=0.001,
        )
        for _ in range(50)
    ]
    cpus = [r["cpu_usage"] for r in results]
    assert all(49 < c < 51 for c in cpus)
