---
status: ACTIVE
version: 2.0
---

# Skills and rules (Localsetup v2)

**Purpose:** How the master rule (or platform context loader) and skills interact; when to load which skill; cross-platform paths.

## Model

- **One always-loaded context** per platform: Cursor uses `.cursor/rules/localsetup-context.mdc`; Claude Code uses `.claude/CLAUDE.md`; Codex uses `AGENTS.md`; OpenClaw uses a context skill + optional doc template in _localsetup/docs/.
- **Skills:** Same SKILL.md content across platforms; installer copies to platform path (`.cursor/skills/`, `.claude/skills/`, `.agents/skills/`, or `skills/` for OpenClaw).
- **When to load a skill:** Load when the task matches the skill's description (e.g. user says "decision tree" -> localsetup-decision-tree-workflow). The master rule/context includes an index of skills and when to use them.

## Platform paths

**Canonical list:** Supported platforms and their context/skills paths are defined in _localsetup/docs/PLATFORM_REGISTRY.md. Reference that file when listing platforms or adding a new one. Summary:

| Platform | Context loader | Skills |
|----------|----------------|--------|
| Cursor | .cursor/rules/localsetup-context.mdc | .cursor/skills/localsetup-*/ |
| Claude Code | .claude/CLAUDE.md | .claude/skills/localsetup-*/ |
| Codex | AGENTS.md (repo root) | .agents/skills/localsetup-*/ |
| OpenClaw | Skill localsetup-context + _localsetup/docs/OPENCLAW_CONTEXT.md | skills/localsetup-*/ |

## Format

- Skills follow the [Agent Skills](https://agentskills.io/specification) specification: SKILL.md with required `name` and `description` frontmatter; optional `metadata.version` for skill document versioning; body = instructions. Same files work on all platforms.
- **Skill document versioning:** Each skill includes `metadata.version` (e.g. `"1.0"`). When a commit touches `framework/skills/*/SKILL.md`, the commit-msg hook runs `scripts/bump-skill-versions` so the version is incremented automatically. See _localsetup/docs/AGENT_SKILLS_COMPLIANCE.md.
- When adding a platform or registering a new skill, use _localsetup/docs/PLATFORM_REGISTRY.md as the source of truth.
- **Interoperability:** Skills are [Agent Skills](https://agentskills.io/specification)–compliant and interchangeable: our skills work in any spec-compliant host; external skills (e.g. [Anthropic’s](https://github.com/anthropics/skills)) can be used here with placement + registration. See _localsetup/docs/SKILL_INTEROPERABILITY.md.
