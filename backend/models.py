from __future__ import annotations

from pydantic import BaseModel


class WorkflowConfig(BaseModel):
    """Per-workflow benchmark parameters (means only, std auto-computed)."""

    cpu_mean: float
    memory_mean: float
    execution_time_mean: float


class WorkflowInfo(BaseModel):
    """Workflow definition returned by the API."""

    name: str
    slug: str
    cpu_mean: float
    memory_mean: float
    execution_time_mean: float


class AppInfo(BaseModel):
    """Application definition returned by the API."""

    name: str
    slug: str
    repo_url: str
    workflows: list[WorkflowInfo]


class SimulateRequest(BaseModel):
    """Request body for simulating a single workflow run."""

    application: str
    workflow: str
    cpu_mean: float
    memory_mean: float
    execution_time_mean: float


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
    workflow: str
    metrics: MetricsResult
    regressions: list[RegressionInfo]


class MetricRecord(BaseModel):
    time: str
    application: str
    workflow: str
    commit_id: str
    commit_number: int
    cpu_usage: float
    memory_usage: float
    execution_time: float


class RegressionRecord(BaseModel):
    time: str
    application: str
    workflow: str
    commit_id: str
    metric: str
    severity: str
    value: float
    z_score: float
    baseline_mean: float
    baseline_std: float


class PipelineRequest(BaseModel):
    """Request body for committing to a mock app repo."""

    application: str
    workflows: dict[str, WorkflowConfig]
    commit_message: str = "Update benchmark config"


class PipelineResponse(BaseModel):
    """Response from the pipeline endpoint."""

    success: bool
    commit_id: str | None = None
    message: str
