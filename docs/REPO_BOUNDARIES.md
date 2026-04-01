# Repo boundaries and development flow (private maintainer repo)

Purpose: keep maintainer operations in private scope while preserving a clean public framework repository.

Created date: 2026-02-19
Last updated date: 2026-02-19

## Repositories

- Private maintainer repo: `localsetup-maintainer`
- Public framework repo: `localsetup-2`

These are separate git repositories with separate remotes and histories.

## What belongs where

Private repo (`localsetup-maintainer`):
- Maintainer-only scripts and release automation
- Maintainer hooks and internal checklists
- Private publishing workflows
- Internal operational docs

Public repo (`localsetup-2`):
- Framework code and templates
- Public docs and skills
- Public install and usage behavior
- User-facing workflow definitions

## Default development workflow

1. Choose target scope first: `[public]`, `[private]`, or `[split]`.
2. Do all edits and git operations in that repo only.
3. If the task needs both repos, split it into two explicit phases.
4. Validate repo root and remote before commit and push.

## Prompt templates

Single-repo private task:

`[private] Update maintainer release automation only. No public repo changes.`

Single-repo public task:

`[public] Add feature X in framework. Update docs and tests in public repo only.`

Two-repo task:

`[split] Public phase: add framework feature X. Private phase: update maintainer release flow for X.`
