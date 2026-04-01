# Repo boundary guardrail

Purpose: define canonical source rules and guardrails for safe development in this unified framework repository.

## Canonical source rule

- **Source:** `_localsetup/` is immutable source for the framework. All framework edits go here.
- **Deploy target:** `.cursor/` is populated by `deploy --tools cursor --root .`. Do not edit `.cursor/` for framework content.
- **One-way flow:** `deploy` copies from `_localsetup` to `.cursor/`. Never edit `.cursor/` for framework content.
- **Exception:** Use `scripts/sync-cursor-to-source.py` to promote `.cursor/` changes back to `_localsetup/` (git 3-way: newer wins when source unchanged).

## Hard rules

1. Edit only under `_localsetup/` for framework content.
2. After editing, run `deploy --tools cursor --root .` to update `.cursor/`.
3. Before committing, run `scripts/compare-packaged-vs-cursor` to check for drift.
4. Use `scripts/publish` to version, document, and push changes.

## Git safety checks

Before commit or push:

1. Confirm current repo root path.
2. Confirm `origin` URL is `github.com/cptnfren/localsetup.git`.
3. Confirm staged files are intentional.

If any check fails, stop and ask the user how to proceed.
