#!/usr/bin/env python3
# Purpose: Deploy platform-specific context loaders and skills. Called by install.
# Supports both local (repo-local) and global (user-wide) deployment.
# Created: 2026-02-20
# Last updated: 2026-04-01

import argparse
import errno
import json
import os
import shutil
import sys
from pathlib import Path

_ENGINE = Path(__file__).resolve().parents[1]
if str(_ENGINE) not in sys.path:
    sys.path.insert(0, str(_ENGINE))
from lib.path_resolution import get_engine_dir, get_project_root


def _safe_copy2(src: Path, dst: Path) -> None:
    """Copy file and metadata; on EPERM (e.g. overwriting root-owned dest), copy content only then optionally metadata."""
    try:
        shutil.copy2(src, dst)
    except (PermissionError, OSError) as e:
        if isinstance(e, OSError) and e.errno != errno.EPERM:
            raise
        # copy2/copy both fail on root-owned dest (utimes/chmod). Use content-only then best-effort metadata.
        shutil.copyfile(src, dst)
        try:
            shutil.copystat(src, dst)
        except (PermissionError, OSError) as meta_err:
            if isinstance(meta_err, OSError) and meta_err.errno != errno.EPERM:
                raise
            print(
                f"Warning: copied {dst.name} but could not set file metadata (permission denied).",
                file=sys.stderr,
            )


def deploy_cursor(engine_dir: Path, root: Path) -> None:
    rules_dir = root / ".cursor" / "rules"
    skills_dir = root / ".cursor" / "skills"
    rules_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "cursor"
    if (templates / "localsetup-context.mdc").exists():
        _safe_copy2(
            templates / "localsetup-context.mdc", rules_dir / "localsetup-context.mdc"
        )
        _safe_copy2(
            templates / "localsetup-context-index.md",
            rules_dir / "localsetup-context-index.md",
        )
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_kilo(engine_dir: Path, root: Path) -> None:
    rules_dir = root / ".kilocode" / "rules"
    skills_dir = root / ".kilocode" / "skills"
    rules_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "kilocode"
    if (templates / "localsetup-context.md").exists():
        _safe_copy2(
            templates / "localsetup-context.md", rules_dir / "localsetup-context.md"
        )
        _safe_copy2(
            templates / "localsetup-context-index.md",
            rules_dir / "localsetup-context-index.md",
        )
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_claude_code(engine_dir: Path, root: Path) -> None:
    claude_dir = root / ".claude"
    skills_dir = claude_dir / "skills"
    claude_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "claude-code"
    if (templates / "CLAUDE.md").exists():
        _safe_copy2(templates / "CLAUDE.md", claude_dir / "CLAUDE.md")
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_codex(engine_dir: Path, root: Path) -> None:
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "codex"
    if (templates / "AGENTS.md").exists():
        _safe_copy2(templates / "AGENTS.md", root / "AGENTS.md")
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_openclaw(engine_dir: Path, root: Path) -> None:
    skills_dir = root / "skills"
    localsetup_base = root / "_localsetup"
    docs_dir = localsetup_base / "docs"
    skills_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "openclaw"
    if (templates / "OPENCLAW_CONTEXT.md").exists():
        _safe_copy2(templates / "OPENCLAW_CONTEXT.md", docs_dir / "OPENCLAW_CONTEXT.md")
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_opencode(engine_dir: Path, root: Path) -> None:
    opencode_dir = root / ".opencode"
    skills_dir = opencode_dir / "skills"
    opencode_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "opencode"
    if (templates / "AGENTS.md").exists():
        _safe_copy2(templates / "AGENTS.md", root / "AGENTS.md")
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def _parse_jsonc(path: Path) -> dict:
    """Parse a JSONC file, stripping // and /* */ comments."""
    if not path.exists():
        return {}
    content = path.read_text()
    lines = content.split("\n")
    result_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("//"):
            result_lines.append("")
        else:
            result_lines.append(line)
    content = "\n".join(result_lines)
    return json.loads(content) if content.strip() else {}


def _write_jsonc(path: Path, data: dict) -> None:
    """Write data to a JSONC file preserving some formatting."""
    content = json.dumps(data, indent=2)
    path.write_text(content + "\n")


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Deep merge overlay into base, modifying base in place and returning it."""
    for key, val in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        elif key in base and isinstance(base[key], list) and isinstance(val, list):
            for item in val:
                if item not in base[key]:
                    base[key].append(item)
        else:
            base[key] = val
    return base


def _expand_path(path_str: str) -> Path:
    """Expand ~ and environment variables in a path string."""
    return Path(os.path.expanduser(os.path.expandvars(path_str)))


def _get_kilo_config_path() -> Path:
    """Return the global kilo config path (kilo.jsonc)."""
    return _expand_path("~/.config/kilo/kilo.jsonc")


def _deploy_skills_to_dir(engine_dir: Path, dest_dir: Path) -> None:
    """Copy all localsetup-* skills to dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = dest_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_kilo_global(engine_dir: Path) -> None:
    """Deploy skills and rules to global kilo locations.

    Skills go to ~/.kilo/skills/ which Kilo auto-discovers.
    Rules go to ~/.kilo/rules/ - users should add ~/.kilo/rules/*.md to their
    instructions[] in kilo.jsonc if they want rules auto-loaded.
    """
    kilo_home = _expand_path("~/.kilo")
    skills_dir = kilo_home / "skills"
    rules_dir = kilo_home / "rules"

    rules_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    templates_cursor = engine_dir / "templates" / "cursor"
    for rule_file in ["localsetup-context.mdc", "localsetup-context-index.md"]:
        src = templates_cursor / rule_file
        if src.exists():
            _safe_copy2(src, rules_dir / rule_file)

    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    _safe_copy2(f, dest / rel)


def deploy_openclaw_global(engine_dir: Path) -> None:
    """Deploy skills to global openclaw location (~/.openclaw/skills/)."""
    openclaw_dir = _expand_path("~/.openclaw")
    skills_dir = openclaw_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    templates = engine_dir / "templates" / "openclaw"
    context_src = templates / "OPENCLAW_CONTEXT.md"
    if context_src.exists():
        _safe_copy2(context_src, openclaw_dir / "OPENCLAW_CONTEXT.md")

    _deploy_skills_to_dir(engine_dir, skills_dir)


def deploy_claude_code_global(engine_dir: Path) -> None:
    """Deploy skills and context to global claude-code location (~/.claude/)."""
    claude_dir = _expand_path("~/.claude")
    skills_dir = claude_dir / "skills"
    claude_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    templates = engine_dir / "templates" / "claude-code"
    if (templates / "CLAUDE.md").exists():
        _safe_copy2(templates / "CLAUDE.md", claude_dir / "CLAUDE.md")

    _deploy_skills_to_dir(engine_dir, skills_dir)


def deploy_opencode_global(engine_dir: Path) -> None:
    """Deploy skills to global opencode location (~/.config/opencode/skills/)."""
    opencode_dir = _expand_path("~/.config/opencode")
    skills_dir = opencode_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    _deploy_skills_to_dir(engine_dir, skills_dir)


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy platform context and skills.")
    ap.add_argument(
        "--root", default=None, help="Client repo root (default: derived from engine)"
    )
    ap.add_argument(
        "--tools",
        required=True,
        help="Comma-separated: cursor,claude-code,codex,openclaw,opencode,kilo",
    )
    ap.add_argument(
        "--scope",
        default="local",
        choices=["local", "global"],
        help="Deployment scope: local (repo-local) or global (user-wide). Default: local",
    )
    args = ap.parse_args()

    engine_dir = get_engine_dir()
    if args.root is not None:
        root = Path(args.root).resolve()
    else:
        root = get_project_root()

    tools_csv = [t.strip().lower() for t in args.tools.split(",") if t.strip()]
    deployers = {
        "cursor": deploy_cursor,
        "claude-code": deploy_claude_code,
        "codex": deploy_codex,
        "openclaw": deploy_openclaw,
        "opencode": deploy_opencode,
        "kilo": deploy_kilo,
    }
    global_deployers = {
        "kilo": deploy_kilo_global,
        "openclaw": deploy_openclaw_global,
        "claude-code": deploy_claude_code_global,
        "opencode": deploy_opencode_global,
    }

    if args.scope == "global":
        for t in tools_csv:
            if t in global_deployers:
                try:
                    global_deployers[t](engine_dir)
                except (OSError, PermissionError) as e:
                    print(f"Global deploy failed ({t}): {e}", file=sys.stderr)
                    print(
                        "Check permissions on the target directory and that no files are owned by another user or immutable.",
                        file=sys.stderr,
                    )
                    return 1
            elif t:
                print(f"Unknown tool for global deploy: {t}", file=sys.stderr)
        return 0

    for t in tools_csv:
        if t in deployers:
            try:
                deployers[t](engine_dir, root)
            except (OSError, PermissionError) as e:
                print(f"Deploy failed ({t}): {e}", file=sys.stderr)
                print(
                    "Check permissions on the target directory and that no files are owned by another user or immutable.",
                    file=sys.stderr,
                )
                return 1
        elif t:
            print(f"Unknown tool: {t}", file=sys.stderr)

    # Sync docs to _localsetup/docs (skip when engine is inside repo and dest is same as src)
    docs_src = engine_dir / "docs"
    if docs_src.is_dir():
        docs_dest = root / "_localsetup" / "docs"
        if docs_src.resolve() != docs_dest.resolve():
            docs_dest.mkdir(parents=True, exist_ok=True)
            try:
                for f in docs_src.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(docs_src)
                        (docs_dest / rel).parent.mkdir(parents=True, exist_ok=True)
                        _safe_copy2(f, docs_dest / rel)
            except (OSError, PermissionError) as e:
                print(f"Deploy failed (docs sync): {e}", file=sys.stderr)
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
