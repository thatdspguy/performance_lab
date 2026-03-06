from __future__ import annotations

import subprocess

import numpy as np

from backend.apps import STD_FRACTION


def get_commit_id(repo_path: str | None = None) -> str:
    """Get the real git commit short SHA for a repo.

    Args:
        repo_path: Path to the git repo. If None, uses the current directory.

    Returns:
        The short commit hash, or "unknown" if git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=repo_path,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def simulate_metrics(
    cpu_mean: float,
    memory_mean: float,
    execution_time_mean: float,
) -> dict[str, float]:
    """Generate one sample of benchmark metrics from normal distributions.

    Standard deviations are automatically computed as STD_FRACTION (10%) of
    the corresponding mean.  Values are clamped to >= 0.
    """
    rng = np.random.default_rng()

    cpu = float(rng.normal(cpu_mean, cpu_mean * STD_FRACTION))
    memory = float(rng.normal(memory_mean, memory_mean * STD_FRACTION))
    execution_time = float(
        rng.normal(execution_time_mean, execution_time_mean * STD_FRACTION)
    )

    return {
        "cpu_usage": max(0.0, round(cpu, 2)),
        "memory_usage": max(0.0, round(memory, 2)),
        "execution_time": max(0.0, round(execution_time, 4)),
    }
