---
status: ACTIVE
version: 3.0
---

# Versioning

This repository uses semantic versioning in `VERSION`.

## Source of truth

- `VERSION` at repo root is the canonical version value.
- Bump operations are performed by `scripts/bump-version`.

## Recommended workflow

1. Make and commit your functional changes.
2. Run `./scripts/publish` (or `./scripts/publish --push`).
3. The publish flow bumps version, regenerates docs artifacts, and commits sync updates.

## Bump behavior

- `feat:` in the latest commit message -> minor bump
- `fix:`, `docs:`, `chore:` and similar -> patch bump
- Use explicit flags to force bump type:
  - `./scripts/publish --major`
  - `./scripts/publish --minor`
  - `./scripts/publish --patch`
