---
status: ACTIVE
version: 2.2
---

# Versioning (Localsetup v2)

**Purpose:** How version is defined and displayed. The framework uses semantic versioning; public version and docs are maintained through the maintainer workflow.

## Source of truth

- **VERSION** at repo root: single line, semantic version `MAJOR.MINOR.PATCH` (e.g. `2.0.0`).
- **README.md** and **framework/README.md** display `**Version:** X.Y.Z`.
- **Framework docs** use YAML front matter `version: X.Y` (major.minor) where applicable.
- **Skill documents** (framework/skills/*/SKILL.md): Each skill has its own `metadata.version` per the [Agent Skills](https://agentskills.io/specification) spec.

## Conventional Commits (reference)

Version bumps follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:` implies minor, `fix:`/`docs:` imply patch, `feat!:` or `BREAKING CHANGE` imply major.

## Public release workflow

Public version bumps and generated docs sync are executed by maintainers from the private maintainer repository workflow, then pushed to this public repository.

For contributors: update public-facing docs for your feature in this repo, then hand off to the maintainer publish workflow for final version/doc sync.
