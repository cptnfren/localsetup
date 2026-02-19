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

From repo root:

```bash
./scripts/maintain
```

This will:

1. Run **bump-version --patch** (updates `VERSION`, READMEs, and doc front matter).
2. **Stage** all changes (`git add -A`).
3. **Commit** with message `chore: maintain (bump to X.Y.Z)` (or your message if you pass one).
4. **Push** to `origin main`.

With a custom commit message:

```bash
./scripts/maintain "fix: install tty fallback and README one-liners"
```

## Manual steps (if you prefer)

1. `./scripts/bump-version --patch`
2. `git add -A && git status`
3. `git commit -m "your message (bump to $(cat VERSION))"`
4. `git push origin main`

## Windows

From repo root in PowerShell:

```powershell
.\scripts\bump-version.ps1 -Patch
git add -A
git commit -m "chore: maintain (bump to $(Get-Content VERSION))"
git push origin main
```

Or run the Bash script from Git Bash: `./scripts/maintain`

## Policy

**Every modification to this framework should end with this maintenance workflow** so that:

- **main** stays current with all changes (no separate release branch).
- Version and docs stay in sync.
- The public repo (GitHub) and live server get updates after each change.
- **Attribution:** Only humans are contributors; the commit-msg hook strips AI/bot `Co-authored-by` trailers. See [ATTRIBUTION.md](ATTRIBUTION.md).

See [VERSIONING.md](VERSIONING.md) for how version numbers and bump types work.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
