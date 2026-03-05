from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from backend.config import settings


def _get_client() -> InfluxDBClient:
    return InfluxDBClient(
        url=settings.influxdb_url,
        token=settings.influxdb_token,
        org=settings.influxdb_org,
    )


def write_metrics(
    application: str,
    workflow: str,
    commit_id: str,
    commit_number: int,
    cpu_usage: float,
    memory_usage: float,
    execution_time: float,
) -> None:
    """Write a performance_metrics data point to InfluxDB."""
    client = _get_client()
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("performance_metrics")
            .tag("application", application)
            .tag("workflow", workflow)
            .tag("commit_id", commit_id)
            .tag("commit_number", str(commit_number))
            .field("cpu_usage", cpu_usage)
            .field("memory_usage", memory_usage)
            .field("execution_time", execution_time)
            .time(datetime.now(timezone.utc), WritePrecision.MS)
        )
        write_api.write(bucket=settings.influxdb_bucket, record=point)
    finally:
        client.close()


def write_regression_event(
    application: str,
    workflow: str,
    commit_id: str,
    metric: str,
    severity: str,
    value: float,
    z_score: float,
    baseline_mean: float,
    baseline_std: float,
) -> None:
    """Write a regression_events data point to InfluxDB."""
    client = _get_client()
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("regression_events")
            .tag("application", application)
            .tag("workflow", workflow)
            .tag("commit_id", commit_id)
            .tag("metric", metric)
            .tag("severity", severity)
            .field("value", value)
            .field("z_score", z_score)
            .field("baseline_mean", baseline_mean)
            .field("baseline_std", baseline_std)
            .time(datetime.now(timezone.utc), WritePrecision.MS)
        )
        write_api.write(bucket=settings.influxdb_bucket, record=point)
    finally:
        client.close()


def query_recent_metrics(
    application: str,
    workflow: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Query the most recent performance_metrics for an application/workflow."""
    client = _get_client()
    try:
        query_api = client.query_api()
        wf_filter = ""
        if workflow:
            wf_filter = (
                f'  |> filter(fn: (r) => r.workflow == "{workflow}")\n'
            )
        flux = f"""
from(bucket: "{settings.influxdb_bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "performance_metrics")
  |> filter(fn: (r) => r.application == "{application}")
{wf_filter}  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit})
"""
        tables = query_api.query(flux, org=settings.influxdb_org)
        results: list[dict[str, Any]] = []
        for table in tables:
            for record in table.records:
                results.append(
                    {
                        "time": record.get_time().isoformat(),
                        "application": record.values.get("application", ""),
                        "workflow": record.values.get("workflow", ""),
                        "commit_id": record.values.get("commit_id", ""),
                        "commit_number": int(
                            record.values.get("commit_number", 0)
                        ),
                        "cpu_usage": record.values.get("cpu_usage", 0.0),
                        "memory_usage": record.values.get("memory_usage", 0.0),
                        "execution_time": record.values.get(
                            "execution_time", 0.0
                        ),
                    }
                )
        return results
    finally:
        client.close()


def query_recent_regressions(
    application: str | None = None,
    workflow: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Query recent regression_events, optionally filtered by application/workflow."""
    client = _get_client()
    try:
        query_api = client.query_api()
        extra_filters = ""
        if application:
            extra_filters += (
                f'  |> filter(fn: (r) => r.application == "{application}")\n'
            )
        if workflow:
            extra_filters += (
                f'  |> filter(fn: (r) => r.workflow == "{workflow}")\n'
            )
        flux = f"""
from(bucket: "{settings.influxdb_bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "regression_events")
{extra_filters}  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit})
"""
        tables = query_api.query(flux, org=settings.influxdb_org)
        results: list[dict[str, Any]] = []
        for table in tables:
            for record in table.records:
                results.append(
                    {
                        "time": record.get_time().isoformat(),
                        "application": record.values.get("application", ""),
                        "workflow": record.values.get("workflow", ""),
                        "commit_id": record.values.get("commit_id", ""),
                        "metric": record.values.get("metric", ""),
                        "severity": record.values.get("severity", ""),
                        "value": record.values.get("value", 0.0),
                        "z_score": record.values.get("z_score", 0.0),
                        "baseline_mean": record.values.get(
                            "baseline_mean", 0.0
                        ),
                        "baseline_std": record.values.get(
                            "baseline_std", 0.0
                        ),
                    }
                )
        return results
    finally:
        client.close()


def get_commit_count(application: str, workflow: str | None = None) -> int:
    """Get the current commit count for an application/workflow from InfluxDB."""
    client = _get_client()
    try:
        query_api = client.query_api()
        wf_filter = ""
        if workflow:
            wf_filter = (
                f'  |> filter(fn: (r) => r.workflow == "{workflow}")\n'
            )
        flux = f"""
from(bucket: "{settings.influxdb_bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "performance_metrics")
  |> filter(fn: (r) => r.application == "{application}")
{wf_filter}  |> filter(fn: (r) => r._field == "cpu_usage")
  |> count()
"""
        tables = query_api.query(flux, org=settings.influxdb_org)
        for table in tables:
            for record in table.records:
                return int(record.get_value())
        return 0
    finally:
        client.close()
