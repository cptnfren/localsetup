---
name: localsetup-automatic-versioning
description: Use and maintain automatic versioning from conventional commits; VERSION as source of truth; commit-msg hook; sync to READMEs and docs. Use when working on version bumps, release workflow, or when the user asks about versioning or conventional commits.
metadata:
  version: "1.1"
---

# Automatic versioning (framework)

**Purpose:** The framework supports automatic semantic versioning driven by commit messages. Use this skill when implementing, explaining, or changing versioning behavior so it stays consistent and framework-appropriate.

## Source of truth

- **VERSION** (repo root): single line, semantic version `MAJOR.MINOR.PATCH` (e.g. `2.0.0`). This is the only canonical version value.
- **Displayed version** must stay in sync: README and framework README show `**Version:** X.Y.Z`; framework docs use YAML front matter `version: X.Y` (major.minor). The bump process updates these so published docs show the correct version.

## Conventional Commits → bump type

- **MAJOR:** `BREAKING CHANGE:` in body, or type followed by `!` (e.g. `feat!: new API`).
- **MINOR:** `feat:` (new feature).
- **PATCH:** `fix:`, `docs:`, `chore:`, `style:`, `refactor:`, `perf:`, `test:`, `ci:`, `build:`; any other message defaults to PATCH.
- **No bump:** Merge commits (message starts with `Merge `). Skip during rebase/merge in hook logic.

## Enabling automatic bump on commit

- **One-time per clone:** Run `./scripts/install-githooks` from repo root. This sets `git config core.hooksPath .githooks`.
- **commit-msg hook:** Reads the commit message file, runs the bump script to determine new version, updates VERSION and synced files (READMEs, docs front matter), stages them, and amends the commit so the version change is in the same commit.
- **Skip conditions:** Hook must not amend during merge or active rebase. Document this in the hook.

## Manual bump (no commit)

- **Bash:** `./scripts/bump-version --major|--minor|--patch` or `./scripts/bump-version <path-to-commit-msg-file>` for conventional-commit parsing. `--no-bump` prints current version only.
- **PowerShell:** `.\scripts\bump-version.ps1 -Major|-Minor|-Patch` or `-MessageFile path`. `-NoBump` prints current version.
- Use when: preparing a release tag, CI, or bypassing the hook for a one-off version set.

## Bypassing the hook

- **One commit:** `git commit --no-verify -m "message"` (skips commit-msg hook).
- **Disable hooks:** `git config --unset core.hooksPath` to use default .git/hooks again.

## Framework requirements (when adding or changing versioning)

- **Cross-platform:** Provide both Bash and PowerShell bump scripts so behavior is identical on Linux/macOS and Windows.
- **Sync list:** Bump script must update (1) VERSION, (2) any file displaying full semver (e.g. READMEs), (3) any file with major.minor in front matter (e.g. framework/docs and repo docs). Keep the list in one place (script or config) so new docs are easy to add.
- **Documentation:** Maintain a single versioning doc (e.g. docs/VERSIONING.md) that explains source of truth, conventional commit rules, how to enable hooks, manual bump, and bypass options. Link to it from the main README.

## Reference

- Full procedure and examples: _localsetup/docs/VERSIONING.md (or repo root docs/VERSIONING.md in source repo).
