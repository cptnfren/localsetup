#!/usr/bin/env python3
# Purpose: Run pre_ship_checks from manifest or CLI before ship (spec Part 12).
# Created: 2026-03-09
# Last updated: 2026-03-09

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run_pre_ship_checks(
    manifest: dict[str, Any],
    *,
    cwd: Path | None = None,
) -> dict[str, Any]:
    """
    If manifest has pre_ship_checks (list of shell commands), run each; all must exit 0.
    Returns {ok: bool, results: [{cmd, returncode, stdout, stderr}]}.
    """
    checks = manifest.get("pre_ship_checks")
    if not checks:
        return {"ok": True, "results": [], "skipped": True}
    if not isinstance(checks, list):
        return {"ok": False, "error": "pre_ship_checks must be a list"}
    results = []
    cwd = str(cwd) if cwd else None
    for cmd in checks:
        if not cmd or not isinstance(cmd, str):
            continue
        r = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        results.append(
            {
                "cmd": cmd[:500],
                "returncode": r.returncode,
                "stdout": (r.stdout or "")[:2000],
                "stderr": (r.stderr or "")[:2000],
            }
        )
        if r.returncode != 0:
            return {"ok": False, "results": results, "failed_cmd": cmd[:500]}
    return {"ok": True, "results": results}
