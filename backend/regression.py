from __future__ import annotations

from backend.metrics import query_recent_metrics, write_regression_event
from backend.models import RegressionInfo

METRIC_NAMES = ["cpu_usage", "memory_usage", "execution_time"]
BASELINE_WINDOW = 20
MIN_DATA_POINTS = 5


def detect_regressions(
    application: str,
    commit_id: str,
    new_values: dict[str, float],
) -> list[RegressionInfo]:
    """Run z-score regression detection for all metrics.

    Queries the last BASELINE_WINDOW data points (excluding the just-written one)
    and computes z-scores. Detected regressions are written to InfluxDB and returned.
    """
    recent = query_recent_metrics(application, limit=BASELINE_WINDOW)

    if len(recent) < MIN_DATA_POINTS:
        return []

    regressions: list[RegressionInfo] = []

    for metric in METRIC_NAMES:
        values = [r[metric] for r in recent if metric in r]
        if len(values) < MIN_DATA_POINTS:
            continue

        baseline_mean = sum(values) / len(values)
        variance = sum((v - baseline_mean) ** 2 for v in values) / len(values)
        baseline_std = variance**0.5

        if baseline_std == 0:
            continue

        new_value = new_values[metric]
        z_score = (new_value - baseline_mean) / baseline_std

        if abs(z_score) > 3:
            severity = "strong"
        elif abs(z_score) > 2:
            severity = "possible"
        else:
            continue

        regression = RegressionInfo(
            metric=metric,
            value=round(new_value, 4),
            z_score=round(z_score, 4),
            baseline_mean=round(baseline_mean, 4),
            baseline_std=round(baseline_std, 4),
            severity=severity,
        )
        regressions.append(regression)

        write_regression_event(
            application=application,
            commit_id=commit_id,
            metric=metric,
            severity=severity,
            value=new_value,
            z_score=round(z_score, 4),
            baseline_mean=round(baseline_mean, 4),
            baseline_std=round(baseline_std, 4),
        )

    return regressions
