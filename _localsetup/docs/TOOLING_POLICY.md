---
status: ACTIVE
version: 2.3
---

# Tooling policy

Purpose: define project-wide tooling language and dependency rules.

## Core rule

- Python is the primary and only language for framework tooling after installation.
- Shell and PowerShell are limited to bootstrap and platform entrypoints:
  - install bootstrap (`install`, `install.ps1`)
  - minimal wrappers/delegation for host compatibility
  - environment orchestration outside framework runtime

## Python runtime target

- Minimum supported version: Python 3.10.
- Baseline rationale: Ubuntu 22.04 LTS default runtime and forward compatibility on newer LTS versions.

## Dependency policy

- Keep third-party libraries minimal.
- Add dependency only when it materially reduces complexity, risk, or maintenance cost.
- Prefer mature libraries with:
  - active maintenance
  - broad adoption
  - clear license
  - recent release activity
- Pin lower bounds in `requirements.txt` and document why each dependency exists.

## External input rule

- All Python tooling that consumes external input must follow:
  - hostile-by-default handling
  - input sanitization
  - schema and bounds validation
  - actionable STDERR error output
  - no silent failure
- See `INPUT_HARDENING_STANDARD.md` for mandatory controls.

## Migration direction

- New tooling and significant refactors should be implemented in Python.
- Existing shell/PowerShell tooling may remain temporarily where needed for bootstrap and compatibility, but should not expand in scope.
