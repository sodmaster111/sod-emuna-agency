#!/usr/bin/env python3
"""Backup runner for Postgres logical dumps with optional S3 syncing.

Scheduling options (choose one outside the script):
- Option A: Run this script on an interval via cron inside a dedicated backup container.
- Option B: Use host-level cron to invoke `docker run --rm -v /host/backups:/backups backup-image`.
- Option C: Trigger this script from an application task scheduler (e.g., Celery beat calling a wrapper command or HTTP endpoint).
"""
import datetime as _dt
import gzip
import importlib.util
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Iterable, List

import yaml

if importlib.util.find_spec("boto3"):
    import boto3  # type: ignore
else:
    boto3 = None


def _load_config() -> dict:
    config_path = os.environ.get("BACKUP_CONFIG", "/ops/backup.yml")
    path = Path(config_path)
    if not path.exists():
        print(f"[ERROR] Config file not found at {path}", file=sys.stderr)
        sys.exit(1)

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data


def _ensure_backup_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def _run_pg_dump(config: dict, destination: Path) -> Path:
    pg = config.get("postgres", {})
    required_keys = ["host", "port", "db", "user", "password"]
    missing = [k for k in required_keys if k not in pg]
    if missing:
        print(f"[ERROR] Missing postgres config keys: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    timestamp = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{pg['db']}-{timestamp}.sql.gz"
    backup_path = destination / filename

    print(f"[INFO] Starting pg_dump for database '{pg['db']}' to {backup_path}")
    env = os.environ.copy()
    env["PGPASSWORD"] = str(pg["password"])

    dump_cmd = [
        "pg_dump",
        "-h",
        str(pg["host"]),
        "-p",
        str(pg["port"]),
        "-U",
        str(pg["user"]),
        str(pg["db"]),
    ]

    with subprocess.Popen(dump_cmd, stdout=subprocess.PIPE, env=env) as proc:
        with gzip.open(backup_path, "wb") as gz_file:
            if proc.stdout is not None:
                for chunk in iter(lambda: proc.stdout.read(1024 * 1024), b""):
                    gz_file.write(chunk)
        return_code = proc.wait()

    if return_code != 0:
        print(f"[ERROR] pg_dump failed with exit code {return_code}", file=sys.stderr)
        if backup_path.exists():
            backup_path.unlink()
        sys.exit(return_code)

    print(f"[INFO] Backup created: {backup_path}")
    return backup_path


def _cleanup_old_backups(destination: Path, retention_days: int) -> None:
    cutoff = _dt.datetime.utcnow() - _dt.timedelta(days=retention_days)
    for entry in destination.iterdir():
        if not entry.is_file():
            continue
        try:
            mtime = _dt.datetime.utcfromtimestamp(entry.stat().st_mtime)
        except OSError:
            continue
        if mtime < cutoff:
            print(f"[INFO] Removing expired backup {entry}")
            try:
                entry.unlink()
            except OSError as exc:
                print(f"[WARNING] Failed to remove {entry}: {exc}", file=sys.stderr)


def _archive_directories(paths: Iterable[str], destination: Path) -> List[Path]:
    archives: List[Path] = []
    timestamp = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    existing_paths: List[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.exists():
            existing_paths.append(path)
        else:
            print(f"[WARNING] Skipping missing path {path}", file=sys.stderr)
    if not existing_paths:
        return archives

    archive_path = destination / f"data-{timestamp}.tar.gz"
    print(f"[INFO] Archiving data directories to {archive_path}")
    with tarfile.open(archive_path, "w:gz") as tar:
        for path in existing_paths:
            tar.add(path, arcname=path.name)
            print(f"[INFO] Added {path} to archive")

    archives.append(archive_path)
    return archives


def _upload_to_s3(config: dict, backup_path: Path) -> None:
    s3_cfg = config.get("s3", {})
    if not s3_cfg.get("enabled"):
        return

    if boto3 is None:
        print("[ERROR] boto3 is required for S3 uploads but is not installed.", file=sys.stderr)
        sys.exit(1)

    required_keys = ["endpoint", "bucket", "access_key", "secret_key"]
    missing = [k for k in required_keys if k not in s3_cfg]
    if missing:
        print(f"[ERROR] Missing S3 config keys: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    print(
        f"[INFO] Uploading {backup_path.name} to bucket {s3_cfg['bucket']} at {s3_cfg['endpoint']}"
    )
    session = boto3.session.Session()
    client = session.client(
        "s3",
        endpoint_url=s3_cfg["endpoint"],
        aws_access_key_id=s3_cfg["access_key"],
        aws_secret_access_key=s3_cfg["secret_key"],
    )

    try:
        client.upload_file(str(backup_path), s3_cfg["bucket"], backup_path.name)
    except Exception as exc:  # noqa: BLE001 - want to catch all upload issues to report and exit
        print(f"[ERROR] Failed to upload backup to S3: {exc}", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Upload to S3 completed")


def main() -> None:
    config = _load_config()

    local_dir = Path(config.get("local_backup_dir", "/backups"))
    _ensure_backup_dir(local_dir)

    retention_days = int(config.get("retention_days", 7))

    backup_path = _run_pg_dump(config, local_dir)
    data_archives = _archive_directories(config.get("data_directories", []), local_dir)
    _cleanup_old_backups(local_dir, retention_days)

    _upload_to_s3(config, backup_path)
    for archive in data_archives:
        _upload_to_s3(config, archive)

    print("[INFO] Backup run completed successfully")


if __name__ == "__main__":
    main()
