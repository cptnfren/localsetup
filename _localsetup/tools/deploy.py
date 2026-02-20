#!/usr/bin/env python3
# Purpose: Deploy platform-specific context loaders and skills. Called by install.
# Created: 2026-02-20
# Last updated: 2026-02-20

import argparse
import shutil
import sys
from pathlib import Path

_ENGINE = Path(__file__).resolve().parents[1]
if str(_ENGINE) not in sys.path:
    sys.path.insert(0, str(_ENGINE))
from lib.path_resolution import get_engine_dir, get_project_root


def deploy_cursor(engine_dir: Path, root: Path) -> None:
    rules_dir = root / ".cursor" / "rules"
    skills_dir = root / ".cursor" / "skills"
    rules_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "cursor"
    if (templates / "localsetup-context.mdc").exists():
        shutil.copy2(templates / "localsetup-context.mdc", rules_dir)
        shutil.copy2(templates / "localsetup-context-index.md", rules_dir)
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest / rel)


def deploy_claude_code(engine_dir: Path, root: Path) -> None:
    claude_dir = root / ".claude"
    skills_dir = claude_dir / "skills"
    claude_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "claude-code"
    if (templates / "CLAUDE.md").exists():
        shutil.copy2(templates / "CLAUDE.md", claude_dir)
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest / rel)


def deploy_codex(engine_dir: Path, root: Path) -> None:
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "codex"
    if (templates / "AGENTS.md").exists():
        shutil.copy2(templates / "AGENTS.md", root / "AGENTS.md")
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest / rel)


def deploy_openclaw(engine_dir: Path, root: Path) -> None:
    skills_dir = root / "skills"
    localsetup_base = root / "_localsetup"
    docs_dir = localsetup_base / "docs"
    skills_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    templates = engine_dir / "templates" / "openclaw"
    if (templates / "OPENCLAW_CONTEXT.md").exists():
        shutil.copy2(templates / "OPENCLAW_CONTEXT.md", docs_dir)
    skills_src = engine_dir / "skills"
    for skill_dir in sorted(skills_src.glob("localsetup-*")):
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(skill_dir)
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest / rel)


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy platform context and skills.")
    ap.add_argument("--root", default=None, help="Client repo root (default: derived from engine)")
    ap.add_argument("--tools", required=True, help="Comma-separated: cursor,claude-code,codex,openclaw")
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
    }
    for t in tools_csv:
        if t in deployers:
            deployers[t](engine_dir, root)
        elif t:
            print(f"Unknown tool: {t}", file=sys.stderr)

    # Sync docs to _localsetup/docs (skip when engine is inside repo and dest is same as src)
    docs_src = engine_dir / "docs"
    if docs_src.is_dir():
        docs_dest = root / "_localsetup" / "docs"
        if docs_src.resolve() != docs_dest.resolve():
            docs_dest.mkdir(parents=True, exist_ok=True)
            for f in docs_src.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(docs_src)
                    (docs_dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, docs_dest / rel)

    return 0


if __name__ == "__main__":
    sys.exit(main())
