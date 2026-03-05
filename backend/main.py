from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.apps import APP_DEFINITIONS, list_apps
from backend.config import settings
from backend.git_ops import ensure_repos_cloned
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
    WorkflowInfo,
)
from backend.pipeline import run_app_pipeline
from backend.regression import detect_regressions
from backend.simulator import generate_commit_id, simulate_metrics

logger = logging.getLogger(__name__)

app = FastAPI(title="Performance Lab", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GRAFANA_URLS = {
    "final_cut": settings.grafana_final_cut_url,
    "logic_pro": settings.grafana_logic_pro_url,
    "xcode": settings.grafana_xcode_url,
}


@app.get("/api/config")
def get_config():
    """Return frontend configuration values."""
    return {"grafana_urls": GRAFANA_URLS}


@app.get("/api/apps", response_model=list[AppInfo])
def get_apps() -> list[AppInfo]:
    """List all application definitions with their workflow configs."""
    return [
        AppInfo(
            name=a.name,
            slug=a.slug,
            repo_url=a.repo_url,
            workflows=[
                WorkflowInfo(
                    name=wf.name,
                    slug=wf.slug,
                    cpu_mean=wf.cpu_mean,
                    memory_mean=wf.memory_mean,
                    execution_time_mean=wf.execution_time_mean,
                )
                for wf in a.workflows
            ],
        )
        for a in list_apps()
    ]


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(req: SimulateRequest) -> SimulateResponse:
    """Simulate a benchmark run for a single workflow."""
    if req.application not in APP_DEFINITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown application: {req.application}",
        )

    app_def = APP_DEFINITIONS[req.application]
    valid_workflows = {wf.slug for wf in app_def.workflows}
    if req.workflow not in valid_workflows:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown workflow '{req.workflow}' for {req.application}",
        )

    commit_id = generate_commit_id()
    commit_number = get_commit_count(req.application, workflow=req.workflow) + 1

    metrics = simulate_metrics(
        cpu_mean=req.cpu_mean,
        memory_mean=req.memory_mean,
        execution_time_mean=req.execution_time_mean,
    )

    write_metrics(
        application=req.application,
        workflow=req.workflow,
        commit_id=commit_id,
        commit_number=commit_number,
        **metrics,
    )

    regressions = detect_regressions(
        application=req.application,
        workflow=req.workflow,
        commit_id=commit_id,
        new_values=metrics,
    )

    return SimulateResponse(
        commit_id=commit_id,
        commit_number=commit_number,
        application=req.application,
        workflow=req.workflow,
        metrics=MetricsResult(**metrics),
        regressions=regressions,
    )


@app.get("/api/metrics", response_model=list[MetricRecord])
def get_metrics(
    application: str = Query(..., description="App slug"),
    workflow: str | None = Query(None, description="Workflow slug filter"),
    limit: int = Query(50, ge=1, le=500),
) -> list[MetricRecord]:
    """Retrieve recent metrics for an application, optionally by workflow."""
    if application not in APP_DEFINITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown application: {application}",
        )
    rows = query_recent_metrics(application, workflow=workflow, limit=limit)
    return [MetricRecord(**r) for r in rows]


@app.get("/api/regressions", response_model=list[RegressionRecord])
def get_regressions(
    application: str | None = Query(None, description="App slug filter"),
    workflow: str | None = Query(None, description="Workflow slug filter"),
    limit: int = Query(50, ge=1, le=500),
) -> list[RegressionRecord]:
    """Retrieve recent regression events."""
    rows = query_recent_regressions(
        application=application, workflow=workflow, limit=limit
    )
    return [RegressionRecord(**r) for r in rows]


@app.post("/api/pipeline", response_model=PipelineResponse)
def trigger_pipeline(req: PipelineRequest) -> PipelineResponse:
    """Write workflow config, commit, and push to a mock app's repo."""
    if req.application not in APP_DEFINITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown application: {req.application}",
        )

    app_def = APP_DEFINITIONS[req.application]
    valid_workflows = {wf.slug for wf in app_def.workflows}
    for wf_slug in req.workflows:
        if wf_slug not in valid_workflows:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow '{wf_slug}' for {req.application}",
            )

    success, message, commit_id = run_app_pipeline(req)

    if not success:
        raise HTTPException(status_code=500, detail=message)

    return PipelineResponse(
        success=True,
        commit_id=commit_id,
        message=message,
    )


@app.post("/api/repos/sync")
def sync_repos():
    """Clone or pull all mock app repositories."""
    try:
        repo_paths = ensure_repos_cloned()
        return {
            "success": True,
            "repos": {slug: str(path) for slug, path in repo_paths.items()},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
