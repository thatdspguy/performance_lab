from __future__ import annotations

import hashlib
import uuid

import numpy as np


def generate_commit_id() -> str:
    """Generate a short simulated commit hash."""
    return hashlib.sha1(uuid.uuid4().bytes).hexdigest()[:8]


def simulate_metrics(
    cpu_mean: float,
    cpu_std: float,
    memory_mean: float,
    memory_std: float,
    execution_time_mean: float,
    execution_time_std: float,
) -> dict[str, float]:
    """Generate one sample of benchmark metrics from normal distributions.

    Values are clamped to sensible minimums (cpu >= 0, memory >= 0, exec_time >= 0).
    """
    rng = np.random.default_rng()

    cpu = float(rng.normal(cpu_mean, cpu_std))
    memory = float(rng.normal(memory_mean, memory_std))
    execution_time = float(rng.normal(execution_time_mean, execution_time_std))

    return {
        "cpu_usage": max(0.0, round(cpu, 2)),
        "memory_usage": max(0.0, round(memory, 2)),
        "execution_time": max(0.0, round(execution_time, 4)),
    }
