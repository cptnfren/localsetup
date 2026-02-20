#!/usr/bin/env python3
# Purpose: Run framework audit (doc, link, skill matrix, version/facts); optional --deep analysis.
# Created: 2026-02-20
# Last updated: 2026-02-20

"""
Single entrypoint for pre-release audit. Phases: doc checks, link checks, skill matrix
(sandbox), version/facts, maintainer refs. Optional --deep: derive invocations from SKILL.md
and --help, run in sandbox, write summary JSON + sidecar tarball. Output path from --output
or LOCALSETUP_AUDIT_OUTPUT; no in-repo default. Deep Analysis requires an output path.
Exit 0 only when zero errors. Follows INPUT_HARDENING_STANDARD.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Limits and patterns (INPUT_HARDENING)
OUTPUT_PATH_MAX = 4096
PATH_COMPONENT_MAX = 256
# Plain "see docs/..." or "See _localsetup/..." that should be markdown links
PLAIN_SEE_DOCS = re.compile(r"\b[Ss]ee\s+docs/[^\s\]\)\"']+")
PLAIN_SEE_LOCALSETUP = re.compile(r"\b[Ss]ee\s+_localsetup/[^\s\]\)\"']+")
MAINTAINER_PATTERN = re.compile(r"scripts/maintain|localsetup-maintainer")
VERSION_LINE = re.compile(r"^\*\*Version:\*\*\s*([\d.]+)", re.MULTILINE)


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _framework_root() -> Path:
    # scripts/ -> skill dir -> skills/ -> _localsetup/
    return _script_dir().parent.parent.parent


def _repo_root() -> Path:
    return _framework_root().parent


def _sanitize_output_path(s: str | None) -> Path | None:
    if s is None or (isinstance(s, str) and not s.strip()):
        return None
    s = s.strip().strip("\x00")[:OUTPUT_PATH_MAX]
    if not s:
        return None
    p = Path(s).resolve()
    for part in p.parts:
        if len(part) > PATH_COMPONENT_MAX:
            raise ValueError(f"path component too long: {part[:32]}...")
    return p


def _resolve_evidence_paths(report_path: Path) -> tuple[Path | None, Path | None]:
    """Resolve summary JSON and tarball paths for Deep Analysis. Returns (summary_path, tarball_path) or (None, None) on error."""
    report_stem = report_path.stem
    env_val = os.environ.get("LOCALSETUP_AUDIT_DEEP_EVIDENCE")
    if not env_val or not (env_val := env_val.strip().strip("\x00")[:OUTPUT_PATH_MAX]):
        summary = report_path.parent / f"{report_stem}_deep_summary.json"
        tarball = report_path.parent / f"{report_stem}_evidence.tar.gz"
        return (summary, tarball)
    try:
        p = Path(env_val).resolve()
    except (OSError, RuntimeError) as e:
        print(f"run_framework_audit: invalid LOCALSETUP_AUDIT_DEEP_EVIDENCE: {e}", file=sys.stderr)
        return (None, None)
    for part in p.parts:
        if len(part) > PATH_COMPONENT_MAX:
            print(f"run_framework_audit: evidence path component too long", file=sys.stderr)
            return (None, None)
    if p.is_dir():
        summary = p / f"{report_stem}_deep_summary.json"
        tarball = p / f"{report_stem}_evidence.tar.gz"
        return (summary, tarball)
    parent = p.parent
    stem = p.stem
    if not stem:
        print("run_framework_audit: LOCALSETUP_AUDIT_DEEP_EVIDENCE has no stem", file=sys.stderr)
        return (None, None)
    summary = parent / f"{stem}_deep_summary.json"
    tarball = parent / f"{stem}_evidence.tar.gz"
    return (summary, tarball)


def _read_version_file(root: Path) -> str | None:
    vf = root / "VERSION"
    if not vf.is_file():
        return None
    try:
        line = vf.read_text(encoding="utf-8", errors="replace").strip().split("\n")[0].strip()
        return line[:64] if line else None
    except OSError:
        return None


def _read_readme_version(root: Path) -> str | None:
    readme = root / "README.md"
    if not readme.is_file():
        return None
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
        m = VERSION_LINE.search(text)
        return m.group(1).strip() if m else None
    except OSError:
        return None


def _read_facts_version(root: Path) -> str | None:
    facts = root / "_localsetup" / "docs" / "_generated" / "facts.json"
    if not facts.is_file():
        return None
    try:
        text = facts.read_text(encoding="utf-8", errors="replace")
        if '"version"' in text:
            m = re.search(r'"version"\s*:\s*"([^"]+)"', text)
            return m.group(1).strip() if m else None
    except OSError:
        pass
    return None


def phase_doc_checks(root: Path, fw: Path) -> list[str]:
    errors: list[str] = []
    required = [
        root / "VERSION",
        root / "README.md",
        root / "docs" / "VERSIONING.md",
        fw / "README.md",
        fw / "docs" / "README.md",
        fw / "tests" / "skill_smoke_commands.yaml",
    ]
    for p in required:
        if not p.exists():
            errors.append(f"Missing required doc/path: {p.relative_to(root)}")
    return errors


def phase_link_checks(root: Path) -> list[tuple[str, int, str]]:
    """Return list of (file, line_no, snippet) for plain 'see docs/...' or 'See _localsetup/...'."""
    findings: list[tuple[str, int, str]] = []
    for md in root.rglob("*.md"):
        try:
            rel = md.relative_to(root)
            if "_generated" in rel.parts or "node_modules" in rel.parts:
                continue
            text = md.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
        for i, line in enumerate(text.split("\n"), 1):
            if "](docs/" in line or "](_localsetup/" in line:
                continue
            if PLAIN_SEE_DOCS.search(line) or PLAIN_SEE_LOCALSETUP.search(line):
                findings.append((str(rel), i, line.strip()[:80]))
    return findings


# Per-script run: (skill_id, script_relpath, exit_code, stdout, stderr)
ScriptRun = tuple[str, str, int, str, str]

OUTPUT_SNIPPET_MAX = 2000  # chars of stdout+stderr to store per run


def _code_block(content: str, lang: str = "text") -> list[str]:
    """Format content as a GitHub-style fenced code block. Uses ~~~ so content may contain ```."""
    lines: list[str] = []
    if not content.strip():
        return lines
    lines.append(f"~~~{lang}")
    lines.append(content.rstrip())
    lines.append("~~~")
    return lines


def _discover_scripts(skill_path: Path) -> list[str]:
    """Return relative paths of all .py files under skill_path/scripts/ (e.g. scripts/foo.py)."""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.is_dir():
        return []
    out: list[str] = []
    for p in sorted(scripts_dir.rglob("*.py")):
        try:
            rel = p.relative_to(skill_path)
            out.append(str(rel))
        except ValueError:
            continue
    return out


# Deep Analysis limits (INPUT_HARDENING)
MAX_CMD_LINE_LEN = 1024
MAX_CMD_BLOCK_SIZE = 8192
SNIPPET_MAX_REPORT = 800
DEEP_PASS_SNIPPET_MAX = 500
SKILL_ID_PATTERN = re.compile(r"^localsetup-[a-zA-Z0-9_-]+$")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _extract_commands_from_skill_md(skill_path: Path) -> list[str]:
    """Extract command lines from SKILL.md fenced code blocks that invoke scripts in this skill."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return []
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    commands: list[str] = []
    in_fence = False
    fence_end = re.compile(r"^```\s*$")
    block_size = 0
    for line in text.split("\n"):
        if fence_end.match(line.strip()):
            in_fence = False
            block_size = 0
            continue
        if line.strip().startswith("```"):
            in_fence = True
            block_size = 0
            continue
        if not in_fence:
            continue
        block_size += len(line) + 1
        if block_size > MAX_CMD_BLOCK_SIZE:
            continue
        line_clean = CONTROL_CHARS.sub("", line).strip()
        if len(line_clean) > MAX_CMD_LINE_LEN:
            continue
        if "python" in line_clean and "scripts/" in line_clean and not line_clean.startswith("#"):
            commands.append(line_clean)
    known_scripts = set(_discover_scripts(skill_path))
    valid: list[str] = []
    for cmd in commands:
        if "scripts/" not in cmd:
            continue
        for known in known_scripts:
            if known in cmd and (skill_path / known).exists():
                valid.append(cmd)
                break
    return valid


def _parse_subcommands_from_help(help_stdout: str) -> list[str]:
    """Parse subcommand names from python script --help output (e.g. subparsers)."""
    subcommands: list[str] = []
    lines = help_stdout.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if "subcommands:" in line.lower() or "positional arguments:" in line.lower():
            for j in range(i + 1, min(i + 30, len(lines))):
                sub = lines[j].strip()
                if not sub or sub.startswith("-") or sub.startswith("{"):
                    continue
                if re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*\s", sub) or re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", sub):
                    name = sub.split()[0] if sub.split() else sub
                    if name and name not in subcommands:
                        subcommands.append(name)
            break
        m = re.search(r"\{([^}]+)\}", line)
        if m:
            for part in m.group(1).split(","):
                name = part.strip()
                if name and name not in subcommands:
                    subcommands.append(name)
    return subcommands


def _sanitize_tarball_script_rel(script_rel: str) -> str:
    """Sanitize script path for use inside tarball; no .., safe chars only."""
    s = (script_rel or "").strip().replace("\x00", "")
    s = re.sub(r"[^a-zA-Z0-9_./-]", "_", s)
    if ".." in s:
        s = s.replace("..", "_")
    s = s.replace("/", "_")
    return s[:PATH_COMPONENT_MAX] if len(s) > PATH_COMPONENT_MAX else s


def _sanitize_skill_id_for_tarball(skill_id: str) -> str:
    """Return skill_id if it matches localsetup-* pattern; else escaped safe form."""
    if not skill_id:
        return "unknown"
    s = (skill_id.strip().replace("\x00", ""))[:PATH_COMPONENT_MAX]
    if SKILL_ID_PATTERN.match(s):
        return s
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s)


def _sanitize_snippet_for_report(text: str) -> str:
    """Normalize snippet for embedding in report (control chars, limit, line endings)."""
    if not text:
        return "*Output truncated or empty.*"
    s = CONTROL_CHARS.sub("", text)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.strip()
    if len(s) > SNIPPET_MAX_REPORT:
        s = s[-SNIPPET_MAX_REPORT:]
        if "\n" in s:
            s = s[s.index("\n") + 1 :]
        s = s.strip() or "*Output truncated or empty.*"
    return s if s else "*Output truncated or empty.*"


def phase_skill_matrix(
    root: Path, fw: Path
) -> tuple[list[str], list[str], list[tuple[str, str]], list[ScriptRun]]:
    """Discover and run every Python script in each skill (sandbox). Return (errors, warnings, results, script_runs)."""
    errors: list[str] = []
    warnings: list[str] = []
    results: list[tuple[str, str]] = []  # (skill_id, status)
    script_runs: list[ScriptRun] = []  # (skill_id, script_path, exit_code, stdout, stderr)
    skills_dir = fw / "skills"
    create_sandbox = fw / "skills" / "localsetup-skill-sandbox-tester" / "scripts" / "create_sandbox.py"
    if not create_sandbox.is_file():
        errors.append("Sandbox tooling (create_sandbox.py) not found")
        return (errors, warnings, results, script_runs)
    skill_dirs = [d for d in sorted(skills_dir.iterdir()) if d.is_dir() and d.name.startswith("localsetup-")]
    for skill_path in skill_dirs:
        skill_id = skill_path.name
        scripts = _discover_scripts(skill_path)
        if not scripts:
            results.append((skill_id, "skip"))
            continue
        try:
            print(f"  [skill matrix] {skill_id}: create_sandbox...", file=sys.stderr)
            cp = subprocess.run(
                [sys.executable, str(create_sandbox), "--skill-path", str(skill_path)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if cp.returncode != 0:
                errors.append(f"Skill matrix {skill_id}: create_sandbox failed: {cp.stderr or cp.stdout}")
                results.append((skill_id, "fail"))
                continue
            sandbox_dir = cp.stdout.strip().split("\n")[-1].strip()
            if not sandbox_dir:
                errors.append(f"Skill matrix {skill_id}: empty sandbox path")
                results.append((skill_id, "fail"))
                continue
            skill_failed = False
            for script_rel in scripts:
                print(f"  [skill matrix] {skill_id}: run {script_rel}...", file=sys.stderr)
                cmd = [sys.executable, script_rel, "--help"]
                try:
                    r = subprocess.run(
                        cmd,
                        cwd=sandbox_dir,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    out_snip = (r.stdout or "")[:OUTPUT_SNIPPET_MAX]
                    err_snip = (r.stderr or "")[:OUTPUT_SNIPPET_MAX]
                    script_runs.append((skill_id, script_rel, r.returncode, out_snip, err_snip))
                    if r.returncode != 0:
                        skill_failed = True
                        errors.append(f"Skill matrix {skill_id} {script_rel}: exit {r.returncode}")
                except subprocess.TimeoutExpired:
                    script_runs.append((skill_id, script_rel, -1, "", "timeout"))
                    skill_failed = True
                    errors.append(f"Skill matrix {skill_id} {script_rel}: timeout")
                except Exception as e:
                    script_runs.append((skill_id, script_rel, -1, "", str(e)))
                    skill_failed = True
                    errors.append(f"Skill matrix {skill_id} {script_rel}: {e}")
            results.append((skill_id, "fail" if skill_failed else "pass"))
        except subprocess.TimeoutExpired:
            errors.append(f"Skill matrix {skill_id}: create_sandbox timeout")
            results.append((skill_id, "fail"))
        except Exception as e:
            errors.append(f"Skill matrix {skill_id}: {e}")
            results.append((skill_id, "fail"))
    return (errors, warnings, results, script_runs)


def phase_version_facts(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    v = _read_version_file(root)
    rv = _read_readme_version(root)
    fv = _read_facts_version(root)
    if not v:
        errors.append("VERSION file missing or unreadable")
    if not rv:
        errors.append("README.md version line (**Version:** X.Y.Z) missing or unreadable")
    if v and rv and v != rv:
        errors.append(f"VERSION ({v}) != README version ({rv})")
    if v and fv and v != fv:
        errors.append(f"VERSION ({v}) != facts.json version ({fv})")
    if not (root / "_localsetup" / "docs" / "_generated" / "facts.json").is_file():
        warnings.append("facts.json missing; version/facts comparison partial")
    return (errors, warnings)


def phase_maintainer_refs(root: Path) -> list[str]:
    findings: list[str] = []
    for md in root.rglob("*.md"):
        try:
            rel = md.relative_to(root)
            if "_generated" in rel.parts:
                continue
            text = md.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
        for i, line in enumerate(text.split("\n"), 1):
            if MAINTAINER_PATTERN.search(line):
                findings.append(f"{rel}:{i}: {line.strip()[:72]}")
    return findings


def _derive_invocations_for_script(
    skill_path: Path,
    script_rel: str,
    sandbox_dir: str,
    root: Path,
    fw: Path,
    timeout: int,
) -> list[list[str]]:
    """Return list of argv lists (safe invocations) for this script: --help, safe from SKILL.md, subcmd --help."""
    invocations: list[list[str]] = []
    script_path = skill_path / script_rel
    if not script_path.exists():
        return [[sys.executable, script_rel, "--help"]]
    base_help: list[str] = [sys.executable, script_rel, "--help"]
    invocations.append(base_help)
    try:
        r = subprocess.run(
            base_help,
            cwd=sandbox_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        subcommands = _parse_subcommands_from_help(r.stdout or "")
        for sub in subcommands:
            invocations.append([sys.executable, script_rel, sub, "--help"])
    except (subprocess.TimeoutExpired, OSError):
        pass
    skill_commands = _extract_commands_from_skill_md(skill_path)
    safe_flags = ("--help", "--list", "--dry-run", "--no-op")
    for cmd in skill_commands:
        if script_rel not in cmd:
            continue
        if not any(f in cmd for f in safe_flags):
            continue
        parts = cmd.split()
        if not parts:
            continue
        if parts[0].lower() in ("python", "python3"):
            argv_cand = [sys.executable] + parts[1:]
        else:
            argv_cand = [sys.executable, script_rel] + parts
        if script_rel in argv_cand and argv_cand not in invocations:
            invocations.append(argv_cand)
    seen = set()
    unique: list[list[str]] = []
    for argv in invocations:
        key = tuple(argv)
        if key not in seen:
            seen.add(key)
            unique.append(argv)
    return unique


def phase_deep_analysis(
    root: Path,
    fw: Path,
    report_path: Path,
    evidence_summary_path: Path,
    evidence_tarball_path: Path,
    timeout: int = 60,
) -> tuple[list[dict], dict, Path | None, Path | None]:
    """Run Deep Analysis: staging dir, per-skill/script invocations, trace files, tarball in staging. Returns (evidence_list, summary_dict, staging_dir, staging_tarball_path)."""
    staging_dir: Path | None = None
    try:
        staging_dir = Path(tempfile.mkdtemp(prefix="localsetup_audit_deep_"))
    except OSError as e:
        print(f"run_framework_audit: could not create staging dir: {e}", file=sys.stderr)
        return ([], {"total_invocations": 0, "pass": 0, "fail": 0, "unvalidated": 0, "skipped": 0}, None, None)
    create_sandbox = fw / "skills" / "localsetup-skill-sandbox-tester" / "scripts" / "create_sandbox.py"
    if not create_sandbox.is_file():
        return ([], {"total_invocations": 0, "pass": 0, "fail": 0, "unvalidated": 0, "skipped": 0}, staging_dir, None)
    skills_dir = fw / "skills"
    skill_dirs = [d for d in sorted(skills_dir.iterdir()) if d.is_dir() and d.name.startswith("localsetup-")]
    evidence_list: list[dict] = []
    trace_files_created: list[Path] = []
    for skill_path in skill_dirs:
        skill_id = skill_path.name
        scripts = _discover_scripts(skill_path)
        if not scripts:
            continue
        try:
            cp = subprocess.run(
                [sys.executable, str(create_sandbox), "--skill-path", str(skill_path)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if cp.returncode != 0:
                continue
            sandbox_dir = cp.stdout.strip().split("\n")[-1].strip()
            if not sandbox_dir:
                continue
        except (subprocess.TimeoutExpired, OSError):
            continue
        for script_rel in scripts:
            invocations = _derive_invocations_for_script(skill_path, script_rel, sandbox_dir, root, fw, timeout)
            run_index = 0
            for argv in invocations:
                print(f"  [Deep analysis] {skill_id}: {script_rel} ...", file=sys.stderr)
                try:
                    r = subprocess.run(
                        argv,
                        cwd=sandbox_dir,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=timeout,
                    )
                except subprocess.TimeoutExpired:
                    r = type("R", (), {"returncode": -1, "stdout": "", "stderr": "timeout"})()
                except OSError as e:
                    r = type("R", (), {"returncode": -1, "stdout": "", "stderr": str(e)})()
                traceback_in_stderr = "Traceback" in (r.stderr or "")
                if r.returncode == 0 and not traceback_in_stderr:
                    validation_status = "pass"
                elif r.returncode != 0 or traceback_in_stderr:
                    validation_status = "fail"
                else:
                    validation_status = "unvalidated"
                stdout_text = (r.stdout or "")[:DEEP_PASS_SNIPPET_MAX] if validation_status == "pass" else (r.stdout or "")
                stderr_text = (r.stderr or "")[:DEEP_PASS_SNIPPET_MAX] if validation_status == "pass" else (r.stderr or "")
                ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                script_sanitized = _sanitize_tarball_script_rel(script_rel)
                skill_sanitized = _sanitize_skill_id_for_tarball(skill_id)
                trace_rel = f"{skill_sanitized}/{script_sanitized}/{ts}_{run_index:02d}_run.log"
                trace_file_path = staging_dir / trace_rel
                trace_file_path.parent.mkdir(parents=True, exist_ok=True)
                trace_file_inside_tarball = trace_rel
                if validation_status in ("fail", "unvalidated"):
                    try:
                        header = f"skill_id={skill_id} script_rel={script_rel} argv={argv!r} exit_code={r.returncode} timestamp={ts}\n"
                        trace_file_path.write_text(
                            header + (r.stdout or "") + "\n--- stderr ---\n" + (r.stderr or ""),
                            encoding="utf-8",
                        )
                        trace_files_created.append(trace_file_path)
                    except OSError:
                        trace_file_inside_tarball = ""
                else:
                    trace_file_inside_tarball = ""
                evidence_list.append({
                    "skill_id": skill_id,
                    "script_rel": script_rel,
                    "argv": argv,
                    "exit_code": getattr(r, "returncode", -1),
                    "validation_status": validation_status,
                    "stdout_snippet": (stdout_text[:DEEP_PASS_SNIPPET_MAX] if validation_status == "pass" else (stdout_text[:OUTPUT_SNIPPET_MAX])),
                    "stderr_snippet": (stderr_text[:DEEP_PASS_SNIPPET_MAX] if validation_status == "pass" else (stderr_text[:OUTPUT_SNIPPET_MAX])),
                    "trace_file": trace_file_inside_tarball,
                })
                run_index += 1
    summary_dict = {
        "total_invocations": len(evidence_list),
        "pass": sum(1 for e in evidence_list if e.get("validation_status") == "pass"),
        "fail": sum(1 for e in evidence_list if e.get("validation_status") == "fail"),
        "unvalidated": sum(1 for e in evidence_list if e.get("validation_status") == "unvalidated"),
        "skipped": sum(1 for e in evidence_list if e.get("validation_status") == "skipped"),
    }
    staging_tarball_path = staging_dir / "evidence.tar.gz"
    try:
        with tarfile.open(staging_tarball_path, "w:gz") as tf:
            for p in trace_files_created:
                try:
                    tf.add(p, arcname=p.relative_to(staging_dir))
                except (ValueError, OSError):
                    pass
    except OSError as e:
        print(f"run_framework_audit: could not create staging tarball: {e}", file=sys.stderr)
    return (evidence_list, summary_dict, staging_dir, staging_tarball_path if staging_tarball_path.exists() else None)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run framework audit (doc, link, skill matrix, version/facts). Output to --output or LOCALSETUP_AUDIT_OUTPUT; no file written if unset."
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        help="Write full report to this path (or set LOCALSETUP_AUDIT_OUTPUT)",
    )
    parser.add_argument(
        "--deep",
        "--deep-analysis",
        dest="deep",
        action="store_true",
        help="Run Deep Analysis: derive invocations from SKILL.md and --help, run in sandbox, write summary JSON + sidecar tarball (requires --output)",
    )
    args = parser.parse_args()
    out_path = args.output or os.environ.get("LOCALSETUP_AUDIT_OUTPUT")
    try:
        out_resolved = _sanitize_output_path(out_path) if out_path else None
    except ValueError as e:
        print(f"run_framework_audit: {e}", file=sys.stderr)
        return 2
    if getattr(args, "deep", False) and out_resolved is None:
        print(
            "run_framework_audit: Deep Analysis requires an output path; set --output or LOCALSETUP_AUDIT_OUTPUT",
            file=sys.stderr,
        )
        return 2
    evidence_summary_path: Path | None = None
    evidence_tarball_path: Path | None = None
    if getattr(args, "deep", False) and out_resolved is not None:
        evidence_summary_path, evidence_tarball_path = _resolve_evidence_paths(out_resolved)
        if evidence_summary_path is None or evidence_tarball_path is None:
            return 2
    root = _repo_root()
    fw = _framework_root()
    all_errors: list[str] = []
    all_warnings: list[str] = []
    link_findings: list[tuple[str, int, str]] = []
    maintainer_findings: list[str] = []

    # Phase 1: doc checks
    all_errors.extend(phase_doc_checks(root, fw))
    # Phase 2: link checks
    link_findings = phase_link_checks(root)
    for f, ln, snip in link_findings:
        all_warnings.append(f"Plain link candidate {f}:{ln}: {snip}")
    # Phase 3: skill matrix
    print("Phase 3: skill matrix (discover and run every script in each skill)...", file=sys.stderr)
    em, wm, matrix_results, script_runs = phase_skill_matrix(root, fw)
    all_errors.extend(em)
    all_warnings.extend(wm)
    # Phase 4: version/facts
    ev, wv = phase_version_facts(root)
    all_errors.extend(ev)
    all_warnings.extend(wv)
    # Phase 5: maintainer refs
    maintainer_findings = phase_maintainer_refs(root)
    if maintainer_findings:
        all_warnings.extend([f"Maintainer ref: {x}" for x in maintainer_findings[:20]])

    deep_evidence_list: list[dict] = []
    deep_summary_dict: dict = {}
    staging_dir: Path | None = None
    staging_tarball_path: Path | None = None
    if getattr(args, "deep", False) and out_resolved and evidence_summary_path and evidence_tarball_path:
        print("Phase 6: Deep Analysis...", file=sys.stderr)
        deep_evidence_list, deep_summary_dict, staging_dir, staging_tarball_path = phase_deep_analysis(
            root, fw, out_resolved, evidence_summary_path, evidence_tarball_path, timeout=60
        )

    # Report (GFM-compatible per TOOLING_POLICY.md § Markdown output)
    report_lines: list[str] = []
    report_lines.append("# Framework audit report")
    report_lines.append("")
    report_lines.append(f"**Repo root:** `{root}`")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append("| Metric | Count |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| **Errors** | {len(all_errors)} |")
    report_lines.append(f"| **Warnings** | {len(all_warnings)} |")
    report_lines.append(f"| **Script runs** | {len(script_runs)} |")
    report_lines.append("")
    pass_count = sum(1 for _, s in matrix_results if s == "pass")
    skip_count = sum(1 for _, s in matrix_results if s == "skip")
    fail_count = sum(1 for _, s in matrix_results if s == "fail")
    report_lines.append("| Skill matrix | Count |")
    report_lines.append("|--------------|-------|")
    report_lines.append(f"| **Pass** | {pass_count} |")
    report_lines.append(f"| **Skip** (no scripts) | {skip_count} |")
    report_lines.append(f"| **Fail** | {fail_count} |")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Skill matrix")
    report_lines.append("")
    report_lines.append("### Skill status")
    report_lines.append("")
    report_lines.append("| Skill | Status |")
    report_lines.append("|-------|--------|")
    for skill_id, status in matrix_results:
        report_lines.append(f"| `{skill_id}` | {status} |")
    report_lines.append("")
    report_lines.append("### Per-script runs")
    report_lines.append("")
    report_lines.append("Command: `python <script> --help`, **cwd** = sandbox copy of skill.")
    report_lines.append("")
    for skill_id, script_rel, exit_code, stdout_text, stderr_text in script_runs:
        disp = "**PASS**" if exit_code == 0 else "**FAIL**"
        report_lines.append(f"#### `{skill_id}` / `{script_rel}`")
        report_lines.append("")
        report_lines.append(f"- **Exit code:** `{exit_code}` — {disp}")
        report_lines.append("")
        if stdout_text or stderr_text:
            if stdout_text:
                report_lines.append("**stdout**")
                report_lines.append("")
                report_lines.extend(_code_block(stdout_text.strip()))
                report_lines.append("")
            if stderr_text:
                report_lines.append("**stderr**")
                report_lines.append("")
                report_lines.extend(_code_block(stderr_text.strip()))
                report_lines.append("")
        else:
            report_lines.append("*No output captured.*")
            report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    if all_errors:
        report_lines.append("## Errors")
        report_lines.append("")
        for e in all_errors:
            report_lines.append(f"- {e}")
        report_lines.append("")
    if all_warnings:
        report_lines.append("## Warnings")
        report_lines.append("")
        for w in all_warnings:
            report_lines.append(f"- {w}")
        report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## requires_review / human_decision")
    report_lines.append("")
    report_lines.append("- Review **Errors** and **Warnings** above. Fix errors before release; accept or fix warnings.")
    report_lines.append("- Doc-only skills: agent produces step summary and logic-gap notes per SKILL.md; no script run.")
    report_lines.append("")

    report_stem = out_resolved.stem if out_resolved else "report"
    if deep_evidence_list:
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## Deep Analysis")
        report_lines.append("")
        report_lines.append("### Summary")
        report_lines.append("")
        report_lines.append("| Metric | Count |")
        report_lines.append("|--------|-------|")
        report_lines.append(f"| **Total invocations** | {deep_summary_dict.get('total_invocations', 0)} |")
        report_lines.append(f"| **Pass** | {deep_summary_dict.get('pass', 0)} |")
        report_lines.append(f"| **Fail** | {deep_summary_dict.get('fail', 0)} |")
        report_lines.append(f"| **Unvalidated** | {deep_summary_dict.get('unvalidated', 0)} |")
        report_lines.append(f"| **Skipped** | {deep_summary_dict.get('skipped', 0)} |")
        report_lines.append("")
        report_lines.append("### Evidence summary")
        report_lines.append("")
        report_lines.append("| Skill | Script | Invocation | Status | Trace |")
        report_lines.append("|-------|--------|------------|--------|-------|")
        for e in deep_evidence_list:
            argv_short = " ".join(str(x) for x in (e.get("argv") or [])[:4])
            if len(argv_short) > 50:
                argv_short = argv_short[:47] + "..."
            trace_ref = e.get("trace_file") or ""
            report_lines.append(f"| `{e.get('skill_id', '')}` | `{e.get('script_rel', '')}` | {argv_short} | {e.get('validation_status', '')} | {trace_ref} |")
        report_lines.append("")
        for e in deep_evidence_list:
            if e.get("validation_status") not in ("fail", "unvalidated"):
                continue
            report_lines.append(f"#### `{e.get('skill_id', '')}` / `{e.get('script_rel', '')}`")
            report_lines.append("")
            report_lines.append(f"**Invocation:** `{' '.join(str(x) for x in (e.get('argv') or []))}`")
            report_lines.append("")
            report_lines.append(f"**Exit code:** `{e.get('exit_code', '')}`")
            report_lines.append("")
            report_lines.append(f"**Validation:** {e.get('validation_status', '')}")
            report_lines.append("")
            snippet = _sanitize_snippet_for_report((e.get("stderr_snippet") or "") or (e.get("stdout_snippet") or ""))
            report_lines.append("**Snippet**")
            report_lines.append("")
            report_lines.extend(_code_block(snippet))
            report_lines.append("")
            report_lines.append(f"**Full logs:** `{report_stem}_evidence.tar.gz`")
            report_lines.append("")

    summary = f"Errors: {len(all_errors)}, Warnings: {len(all_warnings)}"
    exit_code = 0 if not all_errors else 1
    try:
        if out_resolved:
            try:
                out_resolved.parent.mkdir(parents=True, exist_ok=True)
                out_resolved.write_text("\n".join(report_lines), encoding="utf-8")
            except OSError as e:
                print(f"run_framework_audit: could not write report: {e}", file=sys.stderr)
                exit_code = 1
        if getattr(args, "deep", False) and evidence_summary_path and deep_evidence_list is not None:
            summary_for_json = {
                "deep_analysis": [
                    {k: v for k, v in ent.items() if k in ("skill_id", "script_rel", "argv", "exit_code", "validation_status", "stdout_snippet", "stderr_snippet", "trace_file")}
                    for ent in deep_evidence_list
                ],
                "summary": deep_summary_dict,
            }
            try:
                evidence_summary_path.parent.mkdir(parents=True, exist_ok=True)
                evidence_summary_path.write_text(json.dumps(summary_for_json, indent=2), encoding="utf-8")
            except OSError as e:
                print(f"run_framework_audit: could not write summary JSON: {e}", file=sys.stderr)
                exit_code = 1
        if getattr(args, "deep", False) and staging_tarball_path is not None and staging_tarball_path.exists() and evidence_tarball_path is not None:
            try:
                evidence_tarball_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staging_tarball_path, evidence_tarball_path)
            except OSError as e:
                print(f"run_framework_audit: could not write tarball: {e}", file=sys.stderr)
                exit_code = 1
    finally:
        if staging_dir is not None and staging_dir.exists():
            try:
                shutil.rmtree(staging_dir, ignore_errors=True)
            except OSError:
                pass
    print(summary)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
