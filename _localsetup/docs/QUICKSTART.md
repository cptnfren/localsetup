---
status: ACTIVE
version: 2.5
---

# 🚀 Quickstart

Get Localsetup v2 running in your repo in under a minute. This page covers interactive installation, platform selection, verification, and non-interactive one-liners for CI and automation.

## 📦 Prerequisites

- **Required:** `git >= 2.20.0`
- **Recommended for full framework tooling:** `python >= 3.10` and Python module `yaml` (`PyYAML>=6.0`)
- **Linux/macOS:** Bash and curl installed.
- **Windows:** PowerShell 5.1+ or PowerShell Core.
- **Any platform:** Network access to GitHub (or a local clone of this repo).

The installer runs a dependency preflight and prints missing dependencies with install command hints before clone/deploy.

## 🎯 Interactive install (recommended)

The interactive installer prompts you for directory and platform. No flags required.

### Linux and macOS (Bash)

```bash
curl -sSL https://raw.githubusercontent.com/cptnfren/localsetup/main/install | bash
```

### Windows (PowerShell)

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/cptnfren/localsetup/main/install.ps1)))
```

The installer asks:

1. **Directory:** Where to create `_localsetup/` (default: current directory).
2. **Platform(s):** Which agent host(s) to deploy context and skills for.

After install completes, it prints a verification command. Run it to confirm context loaded.

## 🔧 Platform IDs

When prompted (or when using `--tools` / `-Tools`), use one or more of these IDs:

| ID | Agent host | Context path | Skills path |
|----|------------|--------------|-------------|
| `cursor` | Cursor IDE | `.cursor/rules/` | `.cursor/skills/localsetup-*/` |
| `claude-code` | Claude Code | `.claude/CLAUDE.md` | `.claude/skills/localsetup-*/` |
| `codex` | OpenAI Codex CLI | `AGENTS.md` (repo root) | `.agents/skills/localsetup-*/` |
| `openclaw` | OpenClaw | `_localsetup/docs/OPENCLAW_CONTEXT.md` | `skills/localsetup-*/` |

You can deploy to multiple platforms at once by comma-separating: `cursor,claude-code`.

## ✅ Verify installation

After install, run the verification scripts to confirm everything deployed correctly.

### Linux and macOS

```bash
./_localsetup/tools/verify_context
./_localsetup/tools/verify_rules
```

### Windows

```powershell
.\_localsetup\tools\verify_context.ps1
.\_localsetup\tools\verify_rules.ps1
```

Expected output: confirmation that context file exists and skills directory is present.

## ⚡ Non-interactive one-liners

For CI pipelines, automation, or when you already know your platform, use flags to skip prompts.

### Linux and macOS

```bash
curl -sSL https://raw.githubusercontent.com/cptnfren/localsetup/main/install | bash -s -- --directory . --tools cursor --yes
```

```bash
curl -sSL https://raw.githubusercontent.com/cptnfren/localsetup/main/install | bash -s -- --directory . --tools cursor,claude-code --yes
```

### Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/cptnfren/localsetup/main/install.ps1))) -Directory . -Tools cursor -Yes
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/cptnfren/localsetup/main/install.ps1))) -Directory . -Tools "cursor,claude-code" -Yes
```

### From a local clone

If you already have the repo on disk:

```bash
./install --directory /path/to/your/project --tools cursor --yes
```

```powershell
.\install.ps1 -Directory "C:\path\to\your\project" -Tools cursor -Yes
```

## 🔄 Updating

Re-run the same install command. Installer fetches latest framework source, performs an upgrade-aware sync in `_localsetup/`, and redeploys context and skills. Existing repo content outside `_localsetup/` is preserved.

Optional policy:

- `--upgrade-policy preserve` (default)
- `--upgrade-policy force`
- `--upgrade-policy fail-on-conflict`

Examples:

```bash
./install --directory . --tools cursor --yes --upgrade-policy preserve
./install --directory . --tools cursor --yes --upgrade-policy fail-on-conflict
```

## 🧰 If Python tooling is missing

If preflight reports missing `python` or `yaml`, install with whichever package manager you prefer. Common examples:

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y python3 python3-yaml

# Fedora/RHEL
sudo dnf install -y python3 python3-pyyaml

# Arch
sudo pacman -S --needed python python-yaml

# Generic Python env
python3 -m pip install "PyYAML>=6.0"
```

```powershell
# Windows
winget install Python.Python.3.12
py -m pip install "PyYAML>=6.0"
```

## 📖 Next steps

- [Features](FEATURES.md) - full capability list
- [Shipped skills catalog](SKILLS.md) - all 34 built-in skills
- [Platform registry](PLATFORM_REGISTRY.md) - canonical platform definitions
- [Multi-platform install](MULTI_PLATFORM_INSTALL.md) - detailed cross-platform docs

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
