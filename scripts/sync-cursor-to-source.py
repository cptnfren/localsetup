#!/usr/bin/env python3
# Purpose: Sync .cursor/skills and .cursor/rules into _localsetup using git-based 3-way merge.
#          Uses HEAD (last commit) as base; only copies when .cursor has changes and packaged doesn't.
#          Ignores mtime so touch/trivial edits don't overwrite real changes.
# Created: 2026-02-24
# Last updated: 2026-02-24

"""
Sync Cursor runtime (.cursor) back to package source (_localsetup) with git-based strategy.
- Base = file content as in HEAD (last commit) in the public repo.
- Copy cursor -> packaged only when: cursor != base and (packaged == base or packaged missing).
- Skip when: packaged != base (packaged has edits), or both differ from base (conflict), or identical.
- New files (not in git): copy when packaged missing; when both exist, fall back to mtime.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _read_file(p: Path) -> bytes | None:
    """Return file contents or None if missing/unreadable."""
    try:
        return p.read_bytes()
    except OSError:
        return None


def _git_show(repo: Path, git_path: str) -> bytes | None:
    """Return file content from HEAD, or None if not in git / error."""
    try:
        r = subprocess.run(
            ["git", "show", f"HEAD:{git_path}"],
            cwd=repo,
            capture_output=True,
            timeout=5,
        )
        if r.returncode != 0:
            return None
        return r.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _git_last_commit_time(repo: Path, git_path: str) -> float | None:
    """Return Unix timestamp of last commit that touched path, or None."""
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", git_path],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return None
        return float(r.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ValueError):
        return None


def _copy_cursor_to_dst(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _sync_file(
    repo: Path,
    cursor_path: Path,
    packaged_path: Path,
    git_path: str,
    dry_run: bool,
) -> str:
    """
    Returns: 'copied' | 'skipped_packaged_has_changes' | 'skipped_cursor_stale' | 'skipped_same' | 'skipped_conflict' | 'skipped_missing_src'
    """
    cursor_content = _read_file(cursor_path)
    if cursor_content is None:
        return "skipped_missing_src"

    packaged_content = _read_file(packaged_path)
    base_content = _git_show(repo, git_path)

    # Identical: nothing to do
    if packaged_content is not None and cursor_content == packaged_content:
        return "skipped_same"

    # Not in git (new file): copy only if packaged missing; else use mtime as tie-breaker
    if base_content is None:
        if packaged_content is None:
            _copy_cursor_to_dst(cursor_path, packaged_path, dry_run)
            return "copied"
        # Both exist, no base: use mtime to avoid overwriting recently edited packaged
        try:
            if cursor_path.stat().st_mtime > packaged_path.stat().st_mtime:
                _copy_cursor_to_dst(cursor_path, packaged_path, dry_run)
                return "copied"
        except OSError:
            pass
        return "skipped_packaged_has_changes"

    # In git: 3-way decision
    packaged_eq_base = packaged_content == base_content
    cursor_eq_base = cursor_content == base_content

    if packaged_eq_base and not cursor_eq_base:
        # Cursor differs from base, packaged matches base. Only harvest if cursor was modified after last commit
        # (avoids overwriting with stale .cursor when packaged was committed more recently).
        commit_time = _git_last_commit_time(repo, git_path)
        try:
            cursor_mtime = cursor_path.stat().st_mtime
        except OSError:
            cursor_mtime = 0.0
        if commit_time is not None and cursor_mtime <= commit_time:
            return "skipped_cursor_stale"  # cursor not modified after last commit; don't overwrite with stale content
        _copy_cursor_to_dst(cursor_path, packaged_path, dry_run)
        return "copied"
    if not packaged_eq_base and cursor_eq_base:
        # Packaged has changes, cursor is unchanged -> don't overwrite
        return "skipped_packaged_has_changes"
    if not packaged_eq_base and not cursor_eq_base:
        # Both changed from base
        if cursor_content == packaged_content:
            return "skipped_same"
        return "skipped_conflict"
    # both eq base and cursor != packaged already handled (cursor_eq_base and packaged_eq_base => same)
    return "skipped_same"


def sync_context(repo: Path, dry_run: bool) -> tuple[int, int, int, int]:
    """Sync .cursor/rules context files. Returns (copied, skipped_packaged, skipped_stale, conflicts)."""
    cursor_rules = repo / ".cursor" / "rules"
    templates = repo / "_localsetup" / "templates" / "cursor"
    names = ("localsetup-context.mdc", "localsetup-context-index.md")
    copied, skipped, stale, conflicts = 0, 0, 0, 0
    for name in names:
        src = cursor_rules / name
        dst = templates / name
        git_path = f"_localsetup/templates/cursor/{name}"
        result = _sync_file(repo, src, dst, git_path, dry_run)
        if result == "copied":
            copied += 1
            print(f"  synced context: {name}")
        elif result == "skipped_packaged_has_changes":
            skipped += 1
            print(f"  skipped (packaged has changes): {name}")
        elif result == "skipped_cursor_stale":
            stale += 1
            print(f"  skipped (cursor not newer than last commit): {name}")
        elif result == "skipped_conflict":
            conflicts += 1
            print(f"  conflict (both changed): {name}")
    return copied, skipped, stale, conflicts


def sync_skills(repo: Path, dry_run: bool) -> tuple[int, int, int, int]:
    """Sync .cursor/skills/localsetup-* into _localsetup/skills file-by-file. Returns (copied, skipped, stale, conflicts)."""
    cursor_skills = repo / ".cursor" / "skills"
    packaged_skills = repo / "_localsetup" / "skills"
    if not cursor_skills.is_dir():
        return 0, 0, 0, 0

    copied_total, skipped_total, stale_total, conflicts_total = 0, 0, 0, 0
    for runtime_skill in sorted(cursor_skills.iterdir()):
        if not runtime_skill.is_dir() or not runtime_skill.name.startswith("localsetup-"):
            continue
        name = runtime_skill.name
        target_dir = packaged_skills / name
        target_dir.mkdir(parents=True, exist_ok=True)
        copied_s, skipped_s, stale_s, conflicts_s = 0, 0, 0, 0
        for src_file in runtime_skill.rglob("*"):
            if src_file.is_dir():
                continue
            rel = src_file.relative_to(runtime_skill)
            dst_file = target_dir / rel
            git_path = f"_localsetup/skills/{name}/{rel.as_posix()}"
            result = _sync_file(repo, src_file, dst_file, git_path, dry_run)
            if result == "copied":
                copied_s += 1
            elif result == "skipped_packaged_has_changes":
                skipped_s += 1
            elif result == "skipped_cursor_stale":
                stale_s += 1
            elif result == "skipped_conflict":
                conflicts_s += 1
        if copied_s:
            copied_total += copied_s
            print(f"  synced skill: {name} ({copied_s} file(s))")
        if skipped_s:
            skipped_total += skipped_s
            print(f"  skipped (packaged has changes) in {name}: {skipped_s} file(s)")
        if stale_s:
            stale_total += stale_s
            print(f"  skipped (cursor not newer than last commit) in {name}: {stale_s} file(s)")
        if conflicts_s:
            conflicts_total += conflicts_s
            print(f"  conflict (both changed) in {name}: {conflicts_s} file(s)")
    return copied_total, skipped_total, stale_total, conflicts_total


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Sync .cursor into _localsetup using git 3-way: only overwrite when .cursor has changes and packaged matches last commit."
    )
    ap.add_argument("--public-repo", required=True, metavar="PATH", help="Path to public repo (localsetup-2) root")
    ap.add_argument("--dry-run", action="store_true", help="Report what would be done without copying")
    args = ap.parse_args()

    repo = Path(args.public_repo).resolve()
    if not repo.is_dir():
        print(f"Error: not a directory: {repo}", file=sys.stderr)
        return 1

    # Check we're in a git repo
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo,
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: public repo is not a git repository or git unavailable.", file=sys.stderr)
        return 1

    packaged_skills = repo / "_localsetup" / "skills"
    packaged_templates = repo / "_localsetup" / "templates" / "cursor"
    if not packaged_skills.is_dir():
        print(f"Error: missing {packaged_skills}", file=sys.stderr)
        return 1
    if not packaged_templates.is_dir():
        print(f"Error: missing {packaged_templates}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("Dry run (no copies will be made):")

    print("== Harvest runtime -> source (git 3-way: base=HEAD) ==")
    c1, s1, t1, x1 = sync_context(repo, args.dry_run)
    c2, s2, t2, x2 = sync_skills(repo, args.dry_run)
    total_copied = c1 + c2
    total_skipped = s1 + s2
    total_stale = t1 + t2
    total_conflicts = x1 + x2
    parts = [f"{total_copied} synced"]
    if total_skipped:
        parts.append(f"{total_skipped} skipped (packaged has changes)")
    if total_stale:
        parts.append(f"{total_stale} skipped (cursor not newer than last commit)")
    if total_conflicts:
        parts.append(f"{total_conflicts} conflict(s) (both changed)")
    print(f"Summary: {', '.join(parts)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
