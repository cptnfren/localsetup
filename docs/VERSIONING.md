---
status: ACTIVE
version: 2.2
---

# Versioning (Localsetup v2)

**Purpose:** How version is defined and displayed. The framework uses semantic versioning; public version and docs are updated through the public publish scripts.

## Source of truth

- **VERSION** at repo root: single line, semantic version `MAJOR.MINOR.PATCH` (e.g. `2.0.0`).
- **README.md** and **framework/README.md** display `**Version:** X.Y.Z`.
- **Framework docs** use YAML front matter `version: X.Y` (major.minor) where applicable.
- **Skill documents** (framework/skills/*/SKILL.md): Each skill has its own `metadata.version` per the [Agent Skills](https://agentskills.io/specification) spec.

## Conventional Commits (reference)

Version bumps follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:` implies minor, `fix:`/`docs:` imply patch, `feat!:` or `BREAKING CHANGE` imply major.

## Public workflow

From public repo root:

```bash
./scripts/publish --push
```

This workflow:

1. bumps `VERSION` based on last commit message (or explicit `--major|--minor|--patch`);
2. regenerates docs artifacts;
3. commits version/doc sync updates;
4. pushes to `origin main` when `--push` is provided.

Patch-only shortcut:

```bash
./scripts/maintain
```
