# Migrated from .cursor/rules/dependency-preflight.mdc
# Original: /mnt/data/devzone/localsetup-2/.cursor/rules/dependency-preflight.mdc

# Dependency preflight consistency

Purpose: ensure the install scripts' dependency preflight and documentation stay complete and in sync with the project's actual runtime and Python dependencies.

## When this rule applies

- You add, remove, or change a **runtime dependency** (e.g. a CLI tool like `git`, `rg`, `python`, `pip`).
- You add, remove, or change an entry in **`_localsetup/requirements.txt`** (or any Python package the framework expects).

## Required updates (all in the same change)

1. **Bash install** – `install` (root): Update `preflight_checks()` so the new or changed dependency is checked and reported. Add required vs recommended and install hints for the platforms that need them (Linux, Darwin, Windows hints in Bash are for when the script runs on WSL/Git Bash).
2. **PowerShell install** – `install.ps1` (root): Update `Run-PreflightChecks` with the same dependency: required vs recommended and install hints for Windows where applicable.
3. **Canonical list** – `_localsetup/docs/MULTI_PLATFORM_INSTALL.md`: Update the "Dependency preflight" section and the "Canonical dependency list" table so they list every dependency the install scripts check, with Required/Recommended and "Used by".
4. **Short references** – If the dependency is user-facing, update any short prerequisite list in `_localsetup/docs/QUICKSTART.md` and root `README.md` (e.g. "Minimum requirements") so they stay consistent with the canonical list.

## Canonical source of truth

The **canonical dependency list** is the table in `_localsetup/docs/MULTI_PLATFORM_INSTALL.md` under "Dependency preflight". The install scripts (`install` and `install.ps1`) must check exactly those dependencies; no tool used by the install path or by framework tools (e.g. deploy, verify_context, Grep/ripgrep) should be missing from preflight.

## Checklist before committing dependency changes

- [ ] `install`: preflight checks and messages updated.
- [ ] `install.ps1`: preflight checks and messages updated.
- [ ] `_localsetup/docs/MULTI_PLATFORM_INSTALL.md`: canonical table and prose updated.
- [ ] `_localsetup/docs/QUICKSTART.md` and `README.md`: short prerequisite text updated if needed.