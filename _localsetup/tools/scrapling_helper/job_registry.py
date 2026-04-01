"""
Purpose: On-disk job registry for long-running Scrapling operations.
Created: 2026-03-16
Last Updated: 2026-03-16
"""

from __future__ import annotations

import json
import signal
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import ScraplingConfig


@dataclass
class JobRecord:
    job_id: str
    kind: str
    status: str
    created_at: str
    updated_at: str
    command: List[str]
    workdir: str
    pid: Optional[int] = None
    output_path: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def _jobs_dir(cfg: ScraplingConfig) -> Path:
    # Prefer cache_dir so jobs are contained under the framework tree.
    jobs_root = cfg.cache_dir / "jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)
    scrapling_jobs = jobs_root / "scrapling"
    scrapling_jobs.mkdir(parents=True, exist_ok=True)
    return scrapling_jobs


def _job_path(cfg: ScraplingConfig, job_id: str) -> Path:
    return _jobs_dir(cfg) / f"{job_id}.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(cfg: ScraplingConfig, job: JobRecord) -> JobRecord:
    path = _job_path(cfg, job.job_id)
    if path.exists():
        # Overwrite for now; callers should use unique job_ids.
        pass
    path.write_text(json.dumps(asdict(job), indent=2), encoding="utf-8")
    return job


def load_job(cfg: ScraplingConfig, job_id: str) -> Optional[JobRecord]:
    path = _job_path(cfg, job_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return JobRecord(
        job_id=data["job_id"],
        kind=data["kind"],
        status=data["status"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        command=data.get("command", []),
        workdir=data.get("workdir", ""),
        pid=data.get("pid"),
        output_path=data.get("output_path"),
        error=data.get("error"),
        metadata=data.get("metadata", {}),
    )


def list_jobs(cfg: ScraplingConfig, kind: Optional[str] = None) -> List[JobRecord]:
    jobs: List[JobRecord] = []
    jobs_dir = _jobs_dir(cfg)
    for path in jobs_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        record = JobRecord(
            job_id=data["job_id"],
            kind=data["kind"],
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            command=data.get("command", []),
            workdir=data.get("workdir", ""),
            pid=data.get("pid"),
            output_path=data.get("output_path"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )
        if kind is None or record.kind == kind:
            jobs.append(record)
    return jobs


def update_job(cfg: ScraplingConfig, job: JobRecord, **changes: Any) -> JobRecord:
    for key, value in changes.items():
        setattr(job, key, value)
    job.updated_at = _utc_now_iso()
    path = _job_path(cfg, job.job_id)
    path.write_text(json.dumps(asdict(job), indent=2), encoding="utf-8")
    return job


def cancel_job(cfg: ScraplingConfig, job_id: str) -> Dict[str, Any]:
    job = load_job(cfg, job_id)
    if job is None:
        return {"job_id": job_id, "cancelled": False, "reason": "job_not_found"}

    if job.pid is None:
        job.error = "no_pid_recorded"
        update_job(cfg, job, status="cancelled")
        return {"job_id": job_id, "cancelled": False, "reason": "no_pid"}

    try:
        # First send SIGTERM; callers can decide if SIGKILL retries are needed.
        signal.kill(job.pid, signal.SIGTERM)
        update_job(cfg, job, status="cancelling")
        result = {"job_id": job_id, "cancelled": True, "status": "cancelling"}
    except ProcessLookupError:
        job.error = "process_not_found"
        update_job(cfg, job, status="cancelled")
        result = {"job_id": job_id, "cancelled": False, "reason": "process_not_found"}

    return result

