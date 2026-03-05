from __future__ import annotations

from pydantic import BaseModel


class SimulateRequest(BaseModel):
    application: str
    cpu_mean: float
    cpu_std: float
    memory_mean: float
    memory_std: float
    execution_time_mean: float
    execution_time_std: float


class MetricsResult(BaseModel):
    cpu_usage: float
    memory_usage: float
    execution_time: float


class RegressionInfo(BaseModel):
    metric: str
    value: float
    z_score: float
    baseline_mean: float
    baseline_std: float
    severity: str  # "possible" or "strong"


class SimulateResponse(BaseModel):
    commit_id: str
    commit_number: int
    application: str
    metrics: MetricsResult
    regressions: list[RegressionInfo]


class AppInfo(BaseModel):
    name: str
    slug: str
    cpu_mean: float
    cpu_std: float
    memory_mean: float
    memory_std: float
    execution_time_mean: float
    execution_time_std: float


class MetricRecord(BaseModel):
    time: str
    application: str
    commit_id: str
    commit_number: int
    cpu_usage: float
    memory_usage: float
    execution_time: float


class RegressionRecord(BaseModel):
    time: str
    application: str
    commit_id: str
    metric: str
    severity: str
    value: float
    z_score: float
    baseline_mean: float
    baseline_std: float


class AppBenchmarkConfig(BaseModel):
    """Per-app benchmark parameters (mean/std for each metric)."""

    cpu_mean: float
    cpu_std: float
    memory_mean: float
    memory_std: float
    execution_time_mean: float
    execution_time_std: float


class BenchmarkConfig(BaseModel):
    """Full benchmark config with per-app parameters."""

    apps: dict[str, AppBenchmarkConfig]


class PipelineRequest(BaseModel):
    """Request body for the full pipeline endpoint."""

    apps: dict[str, AppBenchmarkConfig]
    commit_message: str = "Update benchmark config"


class PipelineResponse(BaseModel):
    """Response from the full pipeline endpoint."""

    success: bool
    commit_id: str | None = None
    message: str
