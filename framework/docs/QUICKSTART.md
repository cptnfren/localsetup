---
status: ACTIVE
version: 2.2
---

# 🚀 Quickstart

Get Localsetup v2 running in your repo in under a minute. This page covers interactive installation, platform selection, verification, and non-interactive one-liners for CI and automation.

## 📦 Prerequisites

- **Linux/macOS:** Bash, curl, and git installed.
- **Windows:** PowerShell 5.1+ or PowerShell Core; git installed.
- **Any platform:** Network access to GitHub (or a local clone of this repo).

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
./_localsetup/framework/tools/verify_context
./_localsetup/framework/tools/verify_rules
```

### Windows

```powershell
.\_localsetup\framework\tools\verify_context.ps1
.\_localsetup\framework\tools\verify_rules.ps1
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

Re-run the same install command. If `_localsetup/` already exists as a git clone, the installer runs `git pull --rebase` inside it before redeploying context and skills. Your local edits outside `_localsetup/` are preserved.

## 📖 Next steps

- [Features](FEATURES.md) - full capability list
- [Shipped skills catalog](SKILLS.md) - all 32 built-in skills
- [Platform registry](PLATFORM_REGISTRY.md) - canonical platform definitions
- [Multi-platform install](MULTI_PLATFORM_INSTALL.md) - detailed cross-platform docs

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
