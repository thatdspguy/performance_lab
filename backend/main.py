from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.apps import APP_DEFINITIONS, list_apps
from backend.metrics import (
    get_commit_count,
    query_recent_metrics,
    query_recent_regressions,
    write_metrics,
)
from backend.models import (
    AppInfo,
    MetricRecord,
    MetricsResult,
    PipelineRequest,
    PipelineResponse,
    RegressionRecord,
    SimulateRequest,
    SimulateResponse,
)
from backend.pipeline import run_full_pipeline
from backend.regression import detect_regressions
from backend.simulator import generate_commit_id, simulate_metrics

app = FastAPI(title="Performance Lab", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/apps", response_model=list[AppInfo])
def get_apps() -> list[AppInfo]:
    """List all application definitions with their default configs."""
    return [
        AppInfo(
            name=a.name,
            slug=a.slug,
            cpu_mean=a.cpu_mean,
            cpu_std=a.cpu_std,
            memory_mean=a.memory_mean,
            memory_std=a.memory_std,
            execution_time_mean=a.execution_time_mean,
            execution_time_std=a.execution_time_std,
        )
        for a in list_apps()
    ]


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(req: SimulateRequest) -> SimulateResponse:
    """Trigger a simulated commit with benchmark run."""
    if req.application not in APP_DEFINITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown application: {req.application}",
        )

    commit_id = generate_commit_id()
    commit_number = get_commit_count(req.application) + 1

    metrics = simulate_metrics(
        cpu_mean=req.cpu_mean,
        cpu_std=req.cpu_std,
        memory_mean=req.memory_mean,
        memory_std=req.memory_std,
        execution_time_mean=req.execution_time_mean,
        execution_time_std=req.execution_time_std,
    )

    write_metrics(
        application=req.application,
        commit_id=commit_id,
        commit_number=commit_number,
        **metrics,
    )

    regressions = detect_regressions(
        application=req.application,
        commit_id=commit_id,
        new_values=metrics,
    )

    return SimulateResponse(
        commit_id=commit_id,
        commit_number=commit_number,
        application=req.application,
        metrics=MetricsResult(**metrics),
        regressions=regressions,
    )


@app.get("/api/metrics", response_model=list[MetricRecord])
def get_metrics(
    application: str = Query(..., description="App slug"),
    limit: int = Query(50, ge=1, le=500),
) -> list[MetricRecord]:
    """Retrieve recent metrics for an application."""
    if application not in APP_DEFINITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown application: {application}",
        )
    rows = query_recent_metrics(application, limit=limit)
    return [MetricRecord(**r) for r in rows]


@app.get("/api/regressions", response_model=list[RegressionRecord])
def get_regressions(
    application: str | None = Query(None, description="App slug filter"),
    limit: int = Query(50, ge=1, le=500),
) -> list[RegressionRecord]:
    """Retrieve recent regression events."""
    rows = query_recent_regressions(application=application, limit=limit)
    return [RegressionRecord(**r) for r in rows]


@app.post("/api/pipeline", response_model=PipelineResponse)
def trigger_pipeline(req: PipelineRequest) -> PipelineResponse:
    """Write benchmark config, commit, and push to trigger CI pipeline."""
    for slug in req.apps:
        if slug not in APP_DEFINITIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown application: {slug}",
            )

    success, message, commit_id = run_full_pipeline(req)

    if not success:
        raise HTTPException(status_code=500, detail=message)

    return PipelineResponse(
        success=True,
        commit_id=commit_id,
        message=message,
    )
