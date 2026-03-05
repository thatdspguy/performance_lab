#!/usr/bin/env python3
"""Standalone benchmark runner for mock application repositories.

Reads benchmark_config.json, simulates metrics for each workflow,
writes results to InfluxDB, and runs z-score regression detection.

Required environment variables:
    INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import numpy as np
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

STD_FRACTION = 0.10
BASELINE_WINDOW = 20
MIN_DATA_POINTS = 5
METRIC_NAMES = ["cpu_usage", "memory_usage", "execution_time"]


def get_influx_settings() -> dict[str, str]:
    required = ["INFLUXDB_URL", "INFLUXDB_TOKEN", "INFLUXDB_ORG", "INFLUXDB_BUCKET"]
    settings = {}
    for key in required:
        val = os.environ.get(key)
        if not val:
            print(f"Error: {key} environment variable is required", file=sys.stderr)
            sys.exit(1)
        settings[key] = val
    return settings


def get_client(settings: dict[str, str]) -> InfluxDBClient:
    return InfluxDBClient(
        url=settings["INFLUXDB_URL"],
        token=settings["INFLUXDB_TOKEN"],
        org=settings["INFLUXDB_ORG"],
    )


def generate_commit_id() -> str:
    return hashlib.sha1(uuid.uuid4().bytes).hexdigest()[:8]


def simulate_metrics(cpu_mean: float, memory_mean: float, execution_time_mean: float) -> dict[str, float]:
    rng = np.random.default_rng()
    cpu = float(rng.normal(cpu_mean, cpu_mean * STD_FRACTION))
    memory = float(rng.normal(memory_mean, memory_mean * STD_FRACTION))
    exec_time = float(rng.normal(execution_time_mean, execution_time_mean * STD_FRACTION))
    return {
        "cpu_usage": max(0.0, round(cpu, 2)),
        "memory_usage": max(0.0, round(memory, 2)),
        "execution_time": max(0.0, round(exec_time, 4)),
    }


def write_metrics(
    client: InfluxDBClient,
    bucket: str,
    application: str,
    workflow: str,
    commit_id: str,
    commit_number: int,
    metrics: dict[str, float],
) -> None:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = (
        Point("performance_metrics")
        .tag("application", application)
        .tag("workflow", workflow)
        .tag("commit_id", commit_id)
        .tag("commit_number", str(commit_number))
        .field("cpu_usage", metrics["cpu_usage"])
        .field("memory_usage", metrics["memory_usage"])
        .field("execution_time", metrics["execution_time"])
        .time(datetime.now(timezone.utc), WritePrecision.MS)
    )
    write_api.write(bucket=bucket, record=point)


def query_recent_metrics(
    client: InfluxDBClient,
    org: str,
    bucket: str,
    application: str,
    workflow: str,
    limit: int = BASELINE_WINDOW,
) -> list[dict[str, float]]:
    query_api = client.query_api()
    flux = f"""
from(bucket: "{bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "performance_metrics")
  |> filter(fn: (r) => r.application == "{application}")
  |> filter(fn: (r) => r.workflow == "{workflow}")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit})
"""
    tables = query_api.query(flux, org=org)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "cpu_usage": record.values.get("cpu_usage", 0.0),
                "memory_usage": record.values.get("memory_usage", 0.0),
                "execution_time": record.values.get("execution_time", 0.0),
            })
    return results


def get_commit_count(
    client: InfluxDBClient,
    org: str,
    bucket: str,
    application: str,
    workflow: str,
) -> int:
    query_api = client.query_api()
    flux = f"""
from(bucket: "{bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "performance_metrics")
  |> filter(fn: (r) => r.application == "{application}")
  |> filter(fn: (r) => r.workflow == "{workflow}")
  |> filter(fn: (r) => r._field == "cpu_usage")
  |> count()
"""
    tables = query_api.query(flux, org=org)
    for table in tables:
        for record in table.records:
            return int(record.get_value())
    return 0


def write_regression_event(
    client: InfluxDBClient,
    bucket: str,
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
    write_api.write(bucket=bucket, record=point)


def detect_regressions(
    client: InfluxDBClient,
    org: str,
    bucket: str,
    application: str,
    workflow: str,
    commit_id: str,
    new_values: dict[str, float],
) -> list[dict]:
    recent = query_recent_metrics(client, org, bucket, application, workflow)
    if len(recent) < MIN_DATA_POINTS:
        return []

    regressions = []
    for metric in METRIC_NAMES:
        values = [r[metric] for r in recent if metric in r]
        if len(values) < MIN_DATA_POINTS:
            continue

        baseline_mean = sum(values) / len(values)
        variance = sum((v - baseline_mean) ** 2 for v in values) / len(values)
        baseline_std = variance ** 0.5

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

        regressions.append({
            "metric": metric,
            "severity": severity,
            "value": round(new_value, 4),
            "z_score": round(z_score, 4),
            "baseline_mean": round(baseline_mean, 4),
            "baseline_std": round(baseline_std, 4),
        })

        write_regression_event(
            client=client,
            bucket=bucket,
            application=application,
            workflow=workflow,
            commit_id=commit_id,
            metric=metric,
            severity=severity,
            value=new_value,
            z_score=round(z_score, 4),
            baseline_mean=round(baseline_mean, 4),
            baseline_std=round(baseline_std, 4),
        )

    return regressions


def main() -> None:
    influx_settings = get_influx_settings()
    client = get_client(influx_settings)
    org = influx_settings["INFLUXDB_ORG"]
    bucket = influx_settings["INFLUXDB_BUCKET"]

    try:
        with open("benchmark_config.json") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: benchmark_config.json not found", file=sys.stderr)
        sys.exit(1)

    application = config["app"]
    workflows = config["workflows"]
    commit_id = generate_commit_id()
    has_regressions = False

    print(f"Running benchmarks for {application} (commit {commit_id})")
    print("=" * 60)

    try:
        for wf_slug, wf_config in workflows.items():
            print(f"\n  Workflow: {wf_slug}")
            commit_number = get_commit_count(client, org, bucket, application, wf_slug) + 1

            metrics = simulate_metrics(
                cpu_mean=wf_config["cpu_mean"],
                memory_mean=wf_config["memory_mean"],
                execution_time_mean=wf_config["execution_time_mean"],
            )

            print(f"    CPU Usage:      {metrics['cpu_usage']:.2f}%")
            print(f"    Memory Usage:   {metrics['memory_usage']:.2f} MB")
            print(f"    Execution Time: {metrics['execution_time']:.4f} s")

            write_metrics(client, bucket, application, wf_slug, commit_id, commit_number, metrics)

            regressions = detect_regressions(
                client, org, bucket, application, wf_slug, commit_id, metrics
            )

            if regressions:
                has_regressions = True
                for r in regressions:
                    print(f"    ⚠ REGRESSION ({r['severity']}): {r['metric']} "
                          f"z={r['z_score']:.2f}")

    finally:
        client.close()

    print("\n" + "=" * 60)
    if has_regressions:
        print("⚠ Regressions detected!")
        sys.exit(1)
    else:
        print("All benchmarks passed.")


if __name__ == "__main__":
    main()
