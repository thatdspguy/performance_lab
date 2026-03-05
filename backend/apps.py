from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppDefinition:
    name: str
    slug: str
    cpu_mean: float
    cpu_std: float
    memory_mean: float
    memory_std: float
    execution_time_mean: float
    execution_time_std: float


APP_DEFINITIONS: dict[str, AppDefinition] = {
    "final_cut": AppDefinition(
        name="Final Cut Pro",
        slug="final_cut",
        cpu_mean=45,
        cpu_std=4,
        memory_mean=800,
        memory_std=50,
        execution_time_mean=2.5,
        execution_time_std=0.3,
    ),
    "logic_pro": AppDefinition(
        name="Logic Pro",
        slug="logic_pro",
        cpu_mean=30,
        cpu_std=3,
        memory_mean=400,
        memory_std=25,
        execution_time_mean=1.5,
        execution_time_std=0.2,
    ),
    "xcode": AppDefinition(
        name="Xcode",
        slug="xcode",
        cpu_mean=55,
        cpu_std=5,
        memory_mean=1200,
        memory_std=80,
        execution_time_mean=4.0,
        execution_time_std=0.5,
    ),
}


def get_app(slug: str) -> AppDefinition:
    """Return an app definition by slug, raising KeyError if not found."""
    return APP_DEFINITIONS[slug]


def list_apps() -> list[AppDefinition]:
    """Return all application definitions."""
    return list(APP_DEFINITIONS.values())
