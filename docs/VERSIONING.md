---
status: ACTIVE
version: 2.2
---

# Versioning (Localsetup v2)

**Purpose:** How version is defined and displayed. The framework uses semantic versioning; the displayed version is maintained by the repository maintainers.

## Source of truth

- **VERSION** at repo root: single line, semantic version `MAJOR.MINOR.PATCH` (e.g. `2.0.0`).
- **README.md** and **framework/README.md** display `**Version:** X.Y.Z`.
- **Framework docs** use YAML front matter `version: X.Y` (major.minor) where applicable.
- **Skill documents** (framework/skills/*/SKILL.md): Each skill has its own `metadata.version` per the [Agent Skills](https://agentskills.io/specification) spec.

## Conventional Commits (reference)

Version bumps follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:` implies minor, `fix:`/`docs:` imply patch, `feat!:` or `BREAKING CHANGE` imply major. The repository maintainers run the version and doc sync workflow; contributors do not need to run any scripts.

## For contributors

Framework version and displayed version are kept in sync by the repo maintainers. If you need to understand how version is bumped or displayed, see the repository maintainer or the full versioning documentation in the maintainer workflow.
