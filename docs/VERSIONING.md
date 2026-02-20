---
status: ACTIVE
version: 2.1
---

# Versioning (Localsetup v2)

**Purpose:** How version is bumped and how to publish (bump + doc sync + commit).

## Source of truth

- **VERSION** at repo root: single line, semantic version `MAJOR.MINOR.PATCH` (e.g. `2.0.0`).
- **README.md** and **framework/README.md** display `**Version:** X.Y.Z`; the bump script updates them when you run the publish workflow.
- **Framework docs** (`framework/docs/*.md` and `docs/*.md`) use YAML front matter `version: X.Y` (major.minor); the bump script updates these as well.
- **Skill documents** (framework/skills/*/SKILL.md): Each skill has its own `metadata.version` (e.g. `"1.0"`) per the [Agent Skills](https://agentskills.io/specification) spec. Bump skill versions manually with `scripts/bump-skill-versions` when you change a skill. See framework/docs/AGENT_SKILLS_COMPLIANCE.md.

## Publish workflow (recommended)

Version bump and doc sync are not done on every commit. After you have committed your changes and updated any docs that need manual edits, run from repo root:

```bash
./scripts/publish
```

This: (1) bumps VERSION using the last commit message and [Conventional Commits](https://www.conventionalcommits.org/) (feat: → minor, fix:/docs: → patch, feat!: or BREAKING CHANGE → major), or pass `--major`, `--minor`, or `--patch` to force a bump type; (2) regenerates doc artifacts (SKILLS.md, facts.json, managed blocks); (3) commits the version and doc changes with message `chore: bump to X.Y.Z and sync docs`. To push in the same step: `./scripts/publish --push`.

## Manual bump only (no commit)

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

After any modification to the framework, run the publish workflow so version and docs stay in sync, then push to **main**:

```bash
./scripts/publish --push
```

Alternatively: `./scripts/publish` (commit only), then `git push origin main` when ready.

See [MAINTENANCE_WORKFLOW.md](MAINTENANCE_WORKFLOW.md) for full steps and policy.

## Commit message examples (used when you run publish)

Publish infers bump type from the **last** commit message. Examples:

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
