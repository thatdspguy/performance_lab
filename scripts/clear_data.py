#!/usr/bin/env python3
"""Clear all performance data from InfluxDB to start fresh.

Drops and recreates the InfluxDB bucket so all performance_metrics
and regression_events are wiped. (InfluxDB Cloud serverless v3 does
not support range deletes, so bucket recreation is the only option.)

Usage:
    uv run python scripts/clear_data.py
    uv run python scripts/clear_data.py --yes          # skip confirmation
    uv run python scripts/clear_data.py --repos        # also reset cloned repos
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path

# Add project root to path so we can import backend modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings
from backend.git_ops import get_repos_dir


def delete_influxdb_data() -> None:
    """Drop and recreate the bucket to clear all data.

    InfluxDB Cloud serverless v3 does not support the delete API,
    so we delete the entire bucket and create a fresh one with the
    same name.
    """
    from influxdb_client import InfluxDBClient

    client = InfluxDBClient(
        url=settings.influxdb_url,
        token=settings.influxdb_token,
        org=settings.influxdb_org,
    )
    try:
        buckets_api = client.buckets_api()

        # Find the existing bucket
        bucket = buckets_api.find_bucket_by_name(settings.influxdb_bucket)
        if bucket is None:
            print(f"  Bucket '{settings.influxdb_bucket}' not found, nothing to delete.")
            return

        org_id = bucket.org_id

        # Delete the bucket
        print(f"  Deleting bucket '{settings.influxdb_bucket}'...", end=" ", flush=True)
        buckets_api.delete_bucket(bucket)
        print("done")

        # Recreate with the same name
        print(f"  Recreating bucket '{settings.influxdb_bucket}'...", end=" ", flush=True)
        buckets_api.create_bucket(bucket_name=settings.influxdb_bucket, org_id=org_id)
        print("done")
    finally:
        client.close()


def _rm_readonly(func, path, _exc_info):
    """Error handler for shutil.rmtree to clear read-only files (Windows git objects)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def reset_repos() -> None:
    """Delete and re-clone all mock repos to reset git history."""
    repos_dir = get_repos_dir()
    if not repos_dir.exists():
        print("  No repos directory found, nothing to reset.")
        return

    for child in sorted(repos_dir.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            print(f"  Removing {child.name}...", end=" ", flush=True)
            shutil.rmtree(child, onexc=_rm_readonly)
            print("done")

    print("  Repos cleared. They will be re-cloned on next pipeline run.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clear all performance lab data for a fresh start"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--repos",
        action="store_true",
        help="Also delete and reset cloned mock repos",
    )
    args = parser.parse_args()

    print("This will delete ALL data from InfluxDB:")
    print(f"  Bucket: {settings.influxdb_bucket} (will be dropped and recreated)")
    print(f"  URL:    {settings.influxdb_url}")
    if args.repos:
        print("  + Delete cloned repos (will re-clone on next run)")

    if not args.yes:
        try:
            response = input("\nProceed? [y/N] ").strip().lower()
        except EOFError:
            print("\nNo input available. Aborting.")
            sys.exit(1)
        if response not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    print()
    print("Clearing InfluxDB data...")
    delete_influxdb_data()

    if args.repos:
        print("\nResetting repos...")
        reset_repos()

    print("\nAll clear! Dashboards will show empty until new data is pushed.")


if __name__ == "__main__":
    main()
