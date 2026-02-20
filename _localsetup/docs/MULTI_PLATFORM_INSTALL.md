---
status: ACTIVE
version: 2.0
---

# Multi-platform install (Localsetup v2)

**Purpose:** How to install Localsetup v2 for each supported AI agent platform. Supported platforms (canonical list): [PLATFORM_REGISTRY.md](PLATFORM_REGISTRY.md). Same framework; platform-specific context loaders and skill paths. **Cross-platform:** Bash on Linux/macOS; PowerShell on Windows. The framework detects the host and uses the appropriate scripts.

## Platform detection and script selection

- **Linux / macOS:** Use the Bash scripts (`install`, `framework/tools/deploy`, `verify_context`, `verify_rules`, `tests/automated_test.sh`). Same options and behavior.
- **Windows:** Use the PowerShell scripts (`install.ps1`, `framework/tools/deploy.ps1`, `verify_context.ps1`, `verify_rules.ps1`, `tests/automated_test.ps1`). Equivalent options: `-Directory`, `-Tools`, `-Yes`, `-Help` for install; `-Root`, `-Tools` for deploy.
- **Git Bash (or MSYS/Cygwin) on Windows:** If you run the Bash `install` or framework Bash tools, they **detect Windows** and automatically delegate to the corresponding PowerShell script (pwsh or powershell). No need to call `.ps1` manually.

## Install command

### Linux / macOS (Bash)

From your client repo root:

```bash
curl -sSL https://raw.githubusercontent.com/cptnfren/localsetup/main/install | bash
```

Non-interactive (agents/CI):

```bash
curl -sSL .../install | bash -s -- --directory . --tools cursor --yes
```

Multi-platform in one run:

```bash
curl -sSL .../install | bash -s -- --tools cursor,claude-code --yes
```

### Windows (PowerShell)

From your client repo root (after cloning or downloading the repo):

```powershell
# Interactive
.\install.ps1

# Non-interactive
.\install.ps1 -Directory . -Tools cursor -Yes

# Multiple tools
.\install.ps1 -Tools "cursor,claude-code" -Yes
```

If execution policy blocks scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# or one-time bypass:
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Directory . -Tools cursor -Yes
```

## Options

- `--directory PATH` / `-Directory PATH`  - Client repo root (default: .)
- `--tools LIST` / `-Tools LIST`  - Comma-separated: cursor, claude-code, codex, openclaw
- `--yes` / `-Yes`  - Non-interactive (required when using --tools)
- `--help` / `-Help`  - Print usage and exit

## What gets deployed

- **All platforms:** Framework at `_localsetup/` (tools, lib, docs, skills, templates).
- **Per-platform** context loader and skills paths: see [PLATFORM_REGISTRY.md](PLATFORM_REGISTRY.md) (single source of truth; add new platforms there first).

## Framework tools (Bash vs PowerShell)

| Tool | Linux/macOS | Windows |
|------|-------------|---------|
| Install | `./install` or `bash install` | `.\install.ps1` (or run `./install` from Git Bash to auto-detect) |
| Deploy | `./_localsetup/framework/tools/deploy` | `.\_localsetup\framework\tools\deploy.ps1` |
| Verify context | `./_localsetup/framework/tools/verify_context` | `.\_localsetup\framework\tools\verify_context.ps1` |
| Verify rules | `./_localsetup/framework/tools/verify_rules` | `.\_localsetup\framework\tools\verify_rules.ps1` |
| Tests | `./_localsetup/framework/tests/automated_test.sh` | `.\_localsetup\framework\tests\automated_test.ps1` |

Path resolution and OS detection exist in both: `lib/data_paths.sh` and `lib/data_paths.ps1`; `discovery/core/os_detector.sh` and `discovery/core/os_detector.ps1`.

## Repo-local

All context and framework state live in the repo. Move or clone the repo and the framework goes with it. No home-directory dependency.
