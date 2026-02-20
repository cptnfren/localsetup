---
status: ACTIVE
version: 2.1
---

# Framework maintenance workflow (Localsetup v2)

**Purpose:** Standard workflow after any modification to the framework: bump version, commit, and push to **main**. This keeps the framework on main current; it is not a formal release process. Use this for every change so the public repo stays in sync.

## When to run

- After **any** change to the framework: docs, scripts, skills, config, or code.
- Keeps **main** the single source of truth: version bumped (patch), all changes committed, and pushed to `origin main`.

## One command (recommended)

From repo root, after you have committed your changes and updated any relevant docs:

```bash
./scripts/publish --push
```

This will: (1) bump **VERSION** from the last commit message (Conventional Commits: feat: → minor, fix:/docs: → patch) or use `--major`/`--minor`/`--patch` to force; (2) regenerate doc artifacts (SKILLS.md, facts, managed blocks); (3) commit with message `chore: bump to X.Y.Z and sync docs`; (4) push to `origin main`.

Commit only (no push): `./scripts/publish`. Then `git push origin main` when ready.

Alternative (always patch bump, stage everything): `./scripts/maintain` (see script for behavior).

## Manual steps (if you prefer)

1. `./scripts/publish` (bumps from last commit message, regenerates docs, commits), then `git push origin main`.
2. Or: `./scripts/bump-version --patch`, `./scripts/generate-doc-artifacts`, then stage and commit.
4. `git push origin main`

## Windows

From repo root in PowerShell (or Git Bash): run the publish workflow so version and docs are bumped and committed, then push:

```powershell
# From Git Bash or WSL
./scripts/publish --push
```

Or run `./scripts/publish` (commit only), then `git push origin main`.

## Policy

**Every modification to this framework should end with this maintenance workflow** so that:

- **main** stays current with all changes (no separate release branch).
- Version and docs stay in sync.
- The public repo (GitHub) and live server get updates after each change.
- **Attribution:** Only humans are contributors. See [ATTRIBUTION.md](ATTRIBUTION.md).

See [VERSIONING.md](VERSIONING.md) for how version numbers and bump types work.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
