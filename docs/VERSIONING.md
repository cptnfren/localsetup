---
status: ACTIVE
version: 2.1
---

# Versioning and Git hooks (Localsetup v2)

**Purpose:** How version is bumped automatically on commit and how to enable/override it.

## Source of truth

- **VERSION** at repo root: single line, semantic version `MAJOR.MINOR.PATCH` (e.g. `2.0.0`).
- **README.md** and **framework/README.md** display `**Version:** X.Y.Z`; the bump script and commit-msg hook keep them in sync when you bump.
- **Framework docs** (`framework/docs/*.md` and `docs/*.md`) use YAML front matter `version: X.Y` (major.minor); the bump script updates these as well so the displayed version is correct before publishing to GitHub.
- **Skill documents** (framework/skills/*/SKILL.md): Each skill has its own `metadata.version` (e.g. `"1.0"`) per the [Agent Skills](https://agentskills.io/specification) spec. When you commit changes to a skill file, the commit-msg hook runs `scripts/bump-skill-versions` and increments that skill’s version in the same commit. See framework/docs/AGENT_SKILLS_COMPLIANCE.md.

## Automatic bump on commit

When Git hooks are installed (see below), every **commit** triggers:

1. **commit-msg** hook runs with the commit message file.
2. **scripts/bump-version** reads the message and applies [Conventional Commits](https://www.conventionalcommits.org/) rules:
   - **MAJOR** (e.g. 2.0.0 → 3.0.0): `BREAKING CHANGE:` in the body, or type followed by `!` (e.g. `feat!: new API`).
   - **MINOR** (e.g. 2.0.0 → 2.1.0): `feat:` (new feature).
   - **PATCH** (e.g. 2.0.0 → 2.0.1): `fix:`, `docs:`, `chore:`, `style:`, `refactor:`, `perf:`, `test:`, `ci:`, `build:`.
   - Any other message: **PATCH** by default.
3. Merge commits (message starting with `Merge `) are **skipped** (no bump).
4. The hook updates **VERSION** and the README **Version:** lines, stages them, and **amends** the commit so the version change is part of the same commit.

So each commit gets exactly one version bump (or none for merge commits).

## Enable hooks (one-time per clone)

From repo root:

```bash
./scripts/install-githooks
```

This runs `git config core.hooksPath .githooks`, so Git uses the version-controlled hooks in **.githooks/** instead of **.git/hooks/**.

## Manual bump

To bump without committing, or to force a bump type:

```bash
# From commit message (e.g. for CI)
./scripts/bump-version .git/COMMIT_EDITMSG

# Explicit bump type
./scripts/bump-version --major
./scripts/bump-version --minor
./scripts/bump-version --patch

# No bump (just print current version)
./scripts/bump-version --no-bump
```

PowerShell (Windows):

```powershell
.\scripts\bump-version.ps1 -Minor
.\scripts\bump-version.ps1 -MessageFile .git\COMMIT_EDITMSG
```

## Maintenance workflow (after modifications)

**Standard workflow:** After any modification to the framework, bump the version, commit, and push to **main** so the framework stays current. Use one command from repo root:

```bash
./scripts/maintain
```

Optional: pass a custom commit message: `./scripts/maintain "fix: install tty fallback"`

See [MAINTENANCE_WORKFLOW.md](MAINTENANCE_WORKFLOW.md) for full steps and policy. **Every modification should end with this maintenance workflow (keeps main current; not a formal release).**

## Skipping the hook

- **Merge and rebase:** The hook does not amend during a merge or an active rebase.
- **Bypass for one commit:** `git commit --no-verify -m "message"` (skips all commit-msg hooks).
- **Disable hooks:** `git config --unset core.hooksPath` (use default .git/hooks again).

## Commit message examples

```text
feat: add PowerShell install script
→ minor bump (2.0.0 → 2.1.0)

fix: correct path in deploy.ps1
→ patch bump (2.1.0 → 2.1.1)

docs: update MULTI_PLATFORM_INSTALL
→ patch bump

feat!: change install default directory
→ major bump (2.1.1 → 3.0.0)

BREAKING CHANGE: remove support for tool X
→ major bump
```

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
