---
status: ACTIVE
version: 2.3
last_updated: "2026-02-20"
---

# Maintainer workflow index

**Purpose:** Single reference to find the right maintenance workflow by trigger words or intent. Use this when you need to run a maintainer script, add a new workflow, or explain what a workflow does.

**Mandatory:** When a workflow is added or removed in this repo, this index must be updated in the same change. See `.cursor/rules/` for the requirement.

## Quick lookup table

| Slug | Trigger words | Purpose | Script / location |
|------|---------------|---------|-------------------|
| **publish** | `publish`, `run publish`, `bump and push`, `sync version and docs`, `run maintain/publish`, `finalize changes` | Bump VERSION from last commit (Conventional Commits) or explicit flag; regenerate doc artifacts; commit bump and doc sync; optionally push to main. Use after you have committed framework changes and want to bump version and sync docs on main. | `scripts/publish` |
| **maintain** | `maintain`, `run maintain`, `patch bump everything`, `stage all and push` | Always patch bump; regenerate doc artifacts; stage all changes (`git add -A`); commit; push to main. Use when you want a single "keep main current" step and are okay staging everything. | `scripts/maintain` |
| **dogfood** | `dogfood`, `publish from dogfood`, `harvest and publish`, `sync cursor to source`, `harvest runtime` | Harvest Cursor runtime back to package source (`.cursor/skills/` and `.cursor/rules/` into `_localsetup/`), refresh generated artifacts, re-deploy Cursor from source, validate, then bump/commit/push in the public repo. Requires `--public-repo /path/to/localsetup-2`. Use when you edited skills or context in .cursor and want to pull those into the public package and publish. | `scripts/publish-from-dogfood` |
| **bump** | `bump version`, `version bump only`, `bump major/minor/patch` | Update VERSION file and README/doc front matter only. No commit. Use when you need to change version without running full publish or maintain. | `scripts/bump-version` |
| **sync-docs** | `sync docs`, `generate docs`, `regenerate doc artifacts`, `refresh SKILLS.md` | Regenerate SKILLS.md, facts, and other generated docs from canonical sources. No version bump or commit. Use when you want fresh doc artifacts without publishing. | `scripts/generate-doc-artifacts` |
| **compare-cursor** | `compare packaged vs cursor`, `packaging sync check`, `check cursor sync`, `compare cursor` | Compare _localsetup/skills and templates/cursor with .cursor/skills and .cursor/rules in the public repo; report which files differ and which version is newer. Requires `--public-repo /path/to/localsetup-2`. Run before commit/publish to avoid overwriting newer .cursor or missing packaged changes. | `scripts/compare-packaged-vs-cursor` |
| **validate** | `validate workflow`, `validate maintainer`, `check repo wiring` | Check that required paths, executables, and script syntax exist; origin remote; publish --help. Use to verify the maintainer repo is correctly set up after clone or changes. | `scripts/validate-maintainer-workflow` |
| **install-hooks** | `install hooks`, `install githooks`, `setup git hooks` | Set `core.hooksPath` to `.githooks` so commit-msg and post-commit run. Run once per clone. Use when you need commit hooks for version/skill bump or attribution. | `scripts/install-githooks` |
| **docs-sync-ci** | `docs sync ci`, `ci docs`, `verify generated docs` | GitHub Action: on PR or push to main, run generate-doc-artifacts and verify generated files are committed. No manual trigger; runs in CI. | `.github/workflows/docs-sync.yml` |

## How to use this index

- **By trigger:** User or agent says a trigger word (e.g. "publish", "dogfood", "sync docs"). Match to the row and run the script with the documented options.
- **By intent:** User describes what they want (e.g. "I edited skills in .cursor and want to get them into the repo and push"). Match intent to Purpose; use the Script.
- **When adding/removing a workflow:** Update this table and the "Last updated" in the front matter. The Cursor rules require this update in the same change.

## Related docs

- `docs/MAINTENANCE_WORKFLOW.md` – When to run publish, one-command flow, manual steps.
- `docs/VERSIONING.md` – How bump type is chosen (commit message vs flags).
- `docs/REPO_BOUNDARIES.md` – Scope and cross-repo rules.
- `docs/CURSOR_PACKAGING_AND_SYNC.md` – Canonical source vs .cursor; compare script; before-commit/publish checks.
- `.cursor/skills/localsetup-publish-workflow/SKILL.md` – Skill for the publish workflow (trigger words and steps).
