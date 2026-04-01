---
status: ACTIVE
version: 2.10
last_updated: "2026-04-01"
---

# Workflow index

**Purpose:** Single reference to find the right workflow by trigger words or intent.

**Mandatory:** When a workflow is added or removed, this index must be updated in the same change.

## Quick lookup table

| Slug | Trigger words | Purpose | Script / location |
|------|---------------|---------|-------------------|
| **publish** | `publish`, `run publish`, `bump and push`, `sync version and docs`, `finalize changes` | Full publish: validate context and rules, run tests, refresh skill index, regenerate docs, bump version from commits, commit and optionally push. | `scripts/publish` |
| **maintain** | `maintain`, `run maintain`, `patch bump everything`, `stage all and push` | Quick patch bump: always bumps patch, regenerates docs, stages all, commits and pushes. | `scripts/maintain` |
| **bump** | `bump version`, `version bump only` | Update VERSION and doc front matter only. No commit. | `scripts/bump-version` |
| **sync-docs** | `sync docs`, `generate docs`, `regenerate doc artifacts` | Regenerate SKILLS.md, facts.json from canonical sources. | `scripts/generate-doc-artifacts` |
| **compare-cursor** | `compare packaged vs cursor`, `check cursor sync`, `compare cursor` | Compare _localsetup with .cursor; report which files differ and which is newer. | `scripts/compare-packaged-vs-cursor` |
| **sync-runtime** | `sync cursor to source`, `harvest runtime`, `sync .cursor to _localsetup` | Sync .cursor back to _localsetup (git 3-way: newer wins when source unchanged). | `scripts/sync-cursor-to-source.py` |
| **install-hooks** | `install hooks`, `setup git hooks` | Set `core.hooksPath` to `.githooks` for commit hooks. | `scripts/install-githooks` |
| **docs-sync-ci** | `docs sync ci`, `ci docs` | GitHub Action: on PR or push, verify generated docs are committed. | `.github/workflows/docs-sync.yml` |

## How to use this index

- **By trigger:** User or agent says a trigger word (e.g. "publish"). Match to the row and run the script.
- **By intent:** User describes what they want. Match intent to Purpose and use the Script.

## Publishing workflow

1. Make and commit your functional changes.
2. Run `./scripts/publish` (or `./scripts/publish --push`).
3. The publish flow:
   - Validates context and rules
   - Runs automated tests
   - Refreshes public skill index
   - Validates skill registration coverage
   - Regenerates doc artifacts
   - Bumps version from commit messages (conventional commits: feat=minor, fix/chore/docs=patch)
   - Commits version and doc sync

## Versioning

- `VERSION` at repo root is the canonical version.
- `./scripts/bump-version` updates VERSION and doc front matter.
- Conventional commits: `feat:` = minor bump, `fix:`/`docs:`/`chore:` = patch bump.

## Related docs

- `docs/REPO_BOUNDARIES.md` - Canonical source rules and repo structure.
- `docs/VERSIONING.md` - How bump type is determined.
- `docs/CURSOR_PACKAGING_AND_SYNC.md` - Canonical source vs deploy target; compare script.
