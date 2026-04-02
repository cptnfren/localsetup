# Repo boundaries (unified framework repo)

Purpose: define what belongs in this framework repository and guardrails for safe development.

## This is a unified framework repository

All framework code, skills, docs, automation, and publishing live in this single repository:
- **Source:** `_localsetup/` is the canonical source for the framework
- **Deploy target:** `.cursor/` is populated by `deploy` from `_localsetup/`
- **Scripts:** `scripts/` contains all automation (publish, maintain, bump-version, etc.)

## What belongs where

| Path | Role |
|------|------|
| `_localsetup/` | Canonical source (skills, templates, tools, framework docs) |
| `.cursor/` | Deploy target (auto-generated from _localsetup via `deploy`) |
| `scripts/` | Automation scripts (publish, maintain, compare-packaged-vs-cursor, etc.) |
| `docs/` | Public documentation and user-facing docs |
| `.kilocode/` | Agent rules and skills for Kilo/Cursor tooling |

## Canonical source rule

- `_localsetup/` is **immutable source**. All framework edits go here.
- `.cursor/` is the **deploy target**, populated by `deploy --tools cursor --root .`
- **One-way flow:** `deploy` copies from `_localsetup` to `.cursor`. Never edit `.cursor/` for framework content.
- **Exception:** If you edit in `.cursor/` for testing and want to promote changes back to source, use `scripts/sync-cursor-to-source.py` (git 3-way merge: newer wins when source is unchanged since last commit).

## Development guardrails

1. Edit only under `_localsetup/` for framework content.
2. After editing, run `deploy --tools cursor --root .` to update `.cursor/`.
3. Before committing, run `scripts/compare-packaged-vs-cursor` to check for drift.
4. Use `scripts/publish` to version, document, and push changes.

## Git safety checks

Before commit or push:

1. Confirm current repo root path.
2. Confirm `origin` URL is `github.com/cptnfren/localsetup.git`.
3. Confirm staged files are intentional.
