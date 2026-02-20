---
status: ACTIVE
version: 2.0
---

# Agent Skills compliance (Localsetup v2)

**Purpose:** Confirm framework skills conform to the [Agent Skills](https://agentskills.io/specification) specification and document versioning and validation.

## Specification reference

- **Specification:** [agentskills.io/specification](https://agentskills.io/specification)
- **Repo:** [github.com/agentskills/agentskills](https://github.com/agentskills/agentskills)
- **Validation (optional):** Use [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) to validate: `skills-ref validate path/to/skill`

## Compliance summary

| Requirement | Framework behavior |
|-------------|--------------------|
| **Directory structure** | Each skill is a directory with `SKILL.md`; optional `scripts/`, `references/`, `assets/` per spec. |
| **name** (required) | Present in every skill; lowercase, hyphens, 1–64 chars; matches parent directory (e.g. `localsetup-context`). |
| **description** (required) | Present; what the skill does and when to use it; under 1024 chars. |
| **metadata.version** (optional) | Used for skill document versioning; bumped automatically when the skill file is updated (see below). |
| **Body** | Markdown instructions after frontmatter; progressive disclosure; keep under ~500 lines per spec. |
| **File references** | Relative paths from skill root; one level deep where possible. |

## Skill document versioning

- Each framework skill includes **metadata.version** (e.g. `"1.0"`) in SKILL.md frontmatter per the spec’s optional `metadata` field.
- **Automatic bump:** When a commit includes changes to `framework/skills/*/SKILL.md`, the commit-msg hook runs `scripts/bump-skill-versions` for those files and amends the commit so the version increment is in the same commit. Patch is incremented (e.g. 1.0 → 1.1, 1.0.0 → 1.0.1).
- **Manual bump:** Run `./scripts/bump-skill-versions path/to/framework/skills/name/SKILL.md` to increment that skill’s version without committing.
- After bumping a skill under `framework/skills/`, the same version is synced to `framework/.cursor/skills/<name>/SKILL.md` if present so Cursor-deployed copies stay in sync.

## Validation

- Optionally run `skills-ref validate ./framework/skills/localsetup-<name>` (after installing [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)) to check frontmatter and naming.
- Framework skill names use the `localsetup-*` prefix and match the directory name; descriptions include trigger terms for discovery.

## Interoperability

- **Framework skills are valid Agent Skills.** They use only spec-defined fields and layout; they can be copied into any Agent Skills–compatible host (e.g. [Anthropic’s skills](https://github.com/anthropics/skills), Claude Code) and used as-is.
- **External spec-compliant skills can be used in this framework.** Copy the skill directory into `framework/skills/`, add `metadata.version` if missing, register per [PLATFORM_REGISTRY.md](PLATFORM_REGISTRY.md), and deploy. No body or structure changes required for spec compliance.
- Full import/export steps: [SKILL_INTEROPERABILITY.md](SKILL_INTEROPERABILITY.md).

## Reference

- [SKILL_INTEROPERABILITY.md](SKILL_INTEROPERABILITY.md)  - Import external skills; use our skills in other hosts; spec alignment for interchange.
- [SKILLS_AND_RULES.md](SKILLS_AND_RULES.md)  - How skills are loaded and platform paths.
- [PLATFORM_REGISTRY.md](PLATFORM_REGISTRY.md)  - Supported platforms and registration file list.
- Repo VERSION and conventional commits: docs/VERSIONING.md (repo root). Skill versioning is per-skill (metadata.version), not the repo VERSION.
