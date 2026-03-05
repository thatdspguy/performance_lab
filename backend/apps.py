from __future__ import annotations

from dataclasses import dataclass, field


STD_FRACTION = 0.10  # Standard deviation = 10% of the mean


@dataclass(frozen=True)
class WorkflowDefinition:
    name: str
    slug: str
    cpu_mean: float
    memory_mean: float
    execution_time_mean: float


@dataclass(frozen=True)
class AppDefinition:
    name: str
    slug: str
    repo_url: str
    workflows: tuple[WorkflowDefinition, ...] = field(default_factory=tuple)


APP_DEFINITIONS: dict[str, AppDefinition] = {
    "final_cut": AppDefinition(
        name="Final Cut Pro",
        slug="final_cut",
        repo_url="https://github.com/thatdspguy/mock_final_cut.git",
        workflows=(
            WorkflowDefinition(
                name="Importing Video",
                slug="importing_video",
                cpu_mean=40,
                memory_mean=900,
                execution_time_mean=3.0,
            ),
            WorkflowDefinition(
                name="Editing Video",
                slug="editing_video",
                cpu_mean=55,
                memory_mean=1200,
                execution_time_mean=2.0,
            ),
            WorkflowDefinition(
                name="Exporting Video",
                slug="exporting_video",
                cpu_mean=75,
                memory_mean=1500,
                execution_time_mean=8.0,
            ),
        ),
    ),
    "logic_pro": AppDefinition(
        name="Logic Pro",
        slug="logic_pro",
        repo_url="https://github.com/thatdspguy/mock_logic_pro.git",
        workflows=(
            WorkflowDefinition(
                name="Loading Project",
                slug="loading_project",
                cpu_mean=35,
                memory_mean=600,
                execution_time_mean=2.5,
            ),
            WorkflowDefinition(
                name="Real-Time Playback",
                slug="realtime_playback",
                cpu_mean=50,
                memory_mean=800,
                execution_time_mean=1.0,
            ),
            WorkflowDefinition(
                name="Bouncing Final Mix",
                slug="bouncing_final_mix",
                cpu_mean=65,
                memory_mean=700,
                execution_time_mean=5.0,
            ),
        ),
    ),
    "xcode": AppDefinition(
        name="Xcode",
        slug="xcode",
        repo_url="https://github.com/thatdspguy/mock_xcode.git",
        workflows=(
            WorkflowDefinition(
                name="Clean Build",
                slug="clean_build",
                cpu_mean=80,
                memory_mean=2000,
                execution_time_mean=6.0,
            ),
            WorkflowDefinition(
                name="Incremental Build",
                slug="incremental_build",
                cpu_mean=45,
                memory_mean=1200,
                execution_time_mean=1.5,
            ),
            WorkflowDefinition(
                name="Run Unit Tests",
                slug="run_unit_tests",
                cpu_mean=60,
                memory_mean=1500,
                execution_time_mean=4.0,
            ),
        ),
    ),
}


def get_app(slug: str) -> AppDefinition:
    """Return an app definition by slug, raising KeyError if not found."""
    return APP_DEFINITIONS[slug]


def get_workflow(app_slug: str, workflow_slug: str) -> WorkflowDefinition:
    """Return a workflow definition by app and workflow slug."""
    app = get_app(app_slug)
    for wf in app.workflows:
        if wf.slug == workflow_slug:
            return wf
    raise KeyError(f"Unknown workflow '{workflow_slug}' for app '{app_slug}'")


def list_apps() -> list[AppDefinition]:
    """Return all application definitions."""
    return list(APP_DEFINITIONS.values())
