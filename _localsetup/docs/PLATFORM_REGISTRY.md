---
status: ACTIVE
version: 2.10
---

# Platform registry (Localsetup v2)

**Purpose:** Single source of truth for which AI agent platforms the framework supports. When you need to list supported platforms, reference this file instead of scattering names across docs. When adding a new platform, add it here first; when registering a new skill, use the "Skill registration (new skills)" list below so no platform is missed.

**Deploy flag:** The install/deploy scripts use platform **IDs** (e.g. `cursor`, `claude-code`, `codex`, `openclaw`, `kilo`, `opencode`) in the `--tools` / `-Tools` option. Values must match the **ID** column.

## Supported platforms

| ID | Display name | Context loader (path in client repo) | Skills path (path in client repo) |
|----|--------------|--------------------------------------|------------------------------------|
| cursor | Cursor | .cursor/rules/localsetup-context.mdc (and .cursor/rules/localsetup-context-index.md) | .cursor/skills/localsetup-*/ |
| claude-code | Claude Code | .claude/CLAUDE.md | .claude/skills/localsetup-*/ |
| codex | OpenAI Codex CLI | AGENTS.md (repo root) | .agents/skills/localsetup-*/ |
| openclaw | OpenClaw | [OPENCLAW_CONTEXT.md](../templates/openclaw/OPENCLAW_CONTEXT.md) (merge into workspace MEMORY.md if desired) | skills/localsetup-*/ (repo root) |
| kilo | Kilo CLI | `.kilocode/rules/localsetup-context.md` | `.kilocode/skills/localsetup-*/` |
| opencode | OpenCode CLI | AGENTS.md (repo root) | .opencode/skills/localsetup-*/ |

*More platforms may be added later. Update this table and the "Skill registration (new skills)" section when adding one.*

## Global deployment (user-wide, cross-project)

When deployed with `--scope global` (via `./install --global` or `install.ps1 -Global`), the framework installs skills and rules to user-wide locations. This makes the framework available across all projects without per-repo installation.

| Platform | Global skills path | Global config | Notes |
|----------|-------------------|---------------|-------|
| kilo | `~/.kilo/skills/` | Not required | Skills auto-discovered by Kilo |
| kilo | `~/.kilo/rules/` | Add to `instructions[]` in kilo.jsonc | Rules deployed as `.md` files |
| openclaw | `~/.openclaw/skills/` | `~/.openclaw/openclaw.json` | Skills auto-discovered from `~/.openclaw/skills/` |
| claude-code | `~/.claude/skills/` | N/A | Uses `~/.claude/CLAUDE.md` for global context |
| opencode | `~/.config/opencode/skills/` | N/A | Skills auto-discovered from `~/.config/opencode/skills/` |

**Precedence:** Repo-local deployment wins over global. Project-local skills/rules override global ones, allowing projects to customize without affecting the global install.

**Kilo-specific:** Global skills go to `~/.kilo/skills/` which Kilo auto-discovers. Rules go to `~/.kilo/rules/`. To enable rules globally, add `"~/.kilo/rules/*.md"` to the `instructions[]` array in your `kilo.jsonc` (project-level or global). This is a one-time setup; subsequent global deploys only update the rule files.

## Skill registration (new skills)

When adding a new framework skill, register it in **every** file below so the skill appears in each platform’s context and in the framework README. Paths are relative to the **framework source root** (the directory that contains `templates/`, `skills/`, `docs/`).

Add one row or bullet per new skill with a short "When to use" description. Use the same phrasing everywhere.

| Platform / scope | File to update |
|-----------------|----------------|
| Cursor (templates) | _localsetup/templates/cursor/localsetup-context-index.md |
| Cursor (templates) | _localsetup/templates/cursor/localsetup-context.mdc |
| Claude Code | _localsetup/templates/claude-code/CLAUDE.md |
| Codex | _localsetup/templates/codex/AGENTS.md |
| OpenClaw | _localsetup/templates/openclaw/OPENCLAW_CONTEXT.md |
| OpenCode | _localsetup/templates/opencode/AGENTS.md |
| Kilo (templates) | _localsetup/templates/kilocode/localsetup-context.md |
| Kilo (templates) | _localsetup/templates/kilocode/localsetup-context-index.md |
| Framework README | _localsetup/README.md (Skills table) |
| Context skill (source) | _localsetup/skills/localsetup-context/SKILL.md |

**If you add a new platform:** extend the Supported platforms table above, add the platform’s context/skills paths, and add the corresponding registration file(s) to this table so the skill-creator and maintainers keep all platforms in sync.

## Reference

- Deploy script: `_localsetup/tools/deploy` (Bash) / `deploy.ps1` (PowerShell); accepts `--tools "cursor,claude-code,codex,openclaw,kilo,opencode"` and `--scope local|global`.
- Global install: root `install` (Bash) / `install.ps1` (PowerShell) with `--global` / `-Global` flag. Auto-detects installed agents (kilo, openclaw, claude). Skills go to `~/.kilo/skills/` (auto-discovered), rules go to `~/.kilo/rules/`.
- Skills and rules (paths and model): [SKILLS_AND_RULES.md](SKILLS_AND_RULES.md).
- Release and publish (including packaging and sync checks) are maintained in a separate maintainer repository.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
