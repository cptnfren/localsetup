#!/usr/bin/env python3
# Purpose: Compare _localsetup/skills and _localsetup/templates/cursor with .cursor/skills and .cursor/rules
#          in the public repo. Reports which files differ and which version is newer (mtime).
#          Run before commit/publish to avoid overwriting newer .cursor with older packaged or vice versa.
# Created: 2026-02-20
# Last updated: 2026-02-20

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compare packaged source (_localsetup) with .cursor in the public repo; report diffs and which is newer."
    )
    ap.add_argument(
        "--public-repo",
        required=True,
        metavar="PATH",
        help="Path to the public repo root (localsetup-2) where _localsetup and .cursor exist",
    )
    args = ap.parse_args()

    repo = Path(args.public_repo).resolve()
    if not repo.is_dir():
        print(f"Error: not a directory: {repo}", file=sys.stderr)
        return 1

    packaged_skills = repo / "_localsetup" / "skills"
    packaged_templates = repo / "_localsetup" / "templates" / "cursor"
    cursor_skills = repo / ".cursor" / "skills"
    cursor_rules = repo / ".cursor" / "rules"

    if not packaged_skills.is_dir():
        print(f"Error: missing {packaged_skills}", file=sys.stderr)
        return 1

    issues = []
    diff_files = []
    newer_cursor = []
    newer_packaged = []

    # 1) Context files: templates/cursor/* -> .cursor/rules/
    for name in ("localsetup-context.mdc", "localsetup-context-index.md"):
        p_src = packaged_templates / name
        p_dst = cursor_rules / name
        if not p_src.exists():
            continue
        if not p_dst.exists():
            issues.append(f"CONTEXT_ONLY_IN_PACKAGED: {name} (not in .cursor/rules)")
            continue
        try:
            t_src = p_src.stat().st_mtime
            t_dst = p_dst.stat().st_mtime
        except OSError:
            continue
        if p_src.read_bytes() != p_dst.read_bytes():
            diff_files.append(("context", name, p_src, p_dst))
            if t_src > t_dst:
                newer_packaged.append(("context", name))
            else:
                newer_cursor.append(("context", name))

    # 2) Skills: _localsetup/skills/localsetup-* -> .cursor/skills/localsetup-*
    for skill_dir in sorted(packaged_skills.glob("localsetup-*")):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        cursor_skill = cursor_skills / name
        for f in skill_dir.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(skill_dir)
            c_file = cursor_skill / rel
            if not c_file.exists():
                issues.append(f"FILE_ONLY_IN_PACKAGED: {name}/{rel}")
                continue
            try:
                t_src = f.stat().st_mtime
                t_dst = c_file.stat().st_mtime
            except OSError:
                continue
            if f.read_bytes() != c_file.read_bytes():
                diff_files.append((name, str(rel), f, c_file))
                if t_src > t_dst:
                    newer_packaged.append((name, str(rel)))
                else:
                    newer_cursor.append((name, str(rel)))

    # Skills in .cursor but not in packaged
    if cursor_skills.exists():
        for c_skill in cursor_skills.iterdir():
            if c_skill.is_dir() and c_skill.name.startswith("localsetup-"):
                if not (packaged_skills / c_skill.name).exists():
                    issues.append(
                        f"SKILL_ONLY_IN_CURSOR: {c_skill.name} (missing in _localsetup/skills)"
                    )

    # Report
    if issues:
        print("--- Only in one place ---")
        for line in issues:
            print(line)
    if diff_files:
        print("\n--- Different content (path -> packaged vs .cursor) ---")
        for item in diff_files:
            scope, rel = item[0], item[1]
            print(f"  {scope}/{rel}")
    if newer_cursor:
        print(
            "\n--- NEWER in .cursor (risk: overwrite by deploy; run publish-from-dogfood to harvest, or copy back to _localsetup then deploy) ---"
        )
        for scope, rel in newer_cursor:
            print(f"  {scope}/{rel}")
    if newer_packaged:
        print("\n--- NEWER in packaged (run deploy in public repo to update .cursor) ---")
        for scope, rel in newer_packaged:
            print(f"  {scope}/{rel}")

    if not issues and not diff_files and not newer_cursor and not newer_packaged:
        print("No differences. Packaged and .cursor are in sync.")
        return 0
    if newer_cursor:
        print(
            "\nAction: Run scripts/publish-from-dogfood --public-repo <path> to harvest .cursor into source, or copy changed files to _localsetup and deploy."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
