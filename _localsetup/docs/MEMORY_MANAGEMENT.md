---
status: ACTIVE
version: 2.12
---

# Agent Memory Management (Localsetup v2)

**Purpose:** How to use the persistent memory file for AI agent learnings, with strict curation to prevent file bloat.

## Overview

Localsetup v2 includes a persistent **Agent Memory Bank** for each supported platform. This memory file stores AI agent learnings, patterns, and troubleshooting solutions across sessions. Unlike `AGENTS.md` (which is write-protected), the memory file is freely writable by the AI agent.

## Core Principle: Curation Over Accumulation

Memory files **must remain curated and concise**. Without active curation, these files grow unbounded and become useless. The following rules are enforced:

### Curation Rules (Mandatory)

| Rule | Description |
|------|-------------|
| **Maximum 20 entries per section** | When exceeded, remove oldest/least relevant entries first |
| **Revise, don't append** | Update existing entries rather than adding new ones |
| **Stale = removed** | Entries older than 30 days without reaffirmation are deleted |
| **Quality over quantity** | Only record patterns confirmed in 2+ sessions |
| **Escalate significant learnings** | Put important patterns in framework docs, not just memory |

## Memory File Locations

Each platform has its own memory file location:

| Platform | Memory File Location | Context File |
|----------|---------------------|--------------|
| **Kilo CLI** | `.kilo/AGENT_MEMORY.md` | `.kilo/instructions.md` |
| **OpenCode CLI** | `.opencode/AGENT_MEMORY.md` | `AGENTS.md` (repo root) |
| **Claude Code** | `.claude/AGENT_MEMORY.md` | `.claude/CLAUDE.md` |
| **Codex CLI** | `.agents/AGENT_MEMORY.md` | `AGENTS.md` (repo root) |
| **Cursor** | `.cursor/rules/agent-memory.md` | `.cursor/rules/localsetup-context.mdc` |
| **OpenClaw** | `AGENT_MEMORY.md` (repo root) | `OPENCLAW_CONTEXT.md` |

## Memory File Structure

Each memory file contains:

```markdown
# Agent Memory Bank [Platform]

This file stores AI agent learnings. It is NOT protected - you can write freely.
However, this file must remain CURATED and CONCISE. Bloat will be corrected.

## Curation Rules (MUST Follow)

1. **Maximum 20 entries per section** - When exceeded, remove oldest/least relevant
2. **Revise, don't append** - Update existing entries rather than adding new ones
3. **Stale = removed** - Entries older than 30 days without reaffirmation are deleted
4. **Quality over quantity** - Only record patterns confirmed in 2+ sessions
5. **Escalate significant learnings** - Put important patterns in framework docs, not here

## Framework Learnings
- [Date] [Pattern] - [Why it's effective]

## Project Patterns
- [Date] [Convention] - [Context where it applies]

## Troubleshooting Log
- [Date] [Problem] - [Solution]

## Improvement Suggestions
- [Date] [Suggestion] - [Rationale]
```

## Memory Management Flow

When you discover something valuable:

1. **Check before writing** - Does this pattern already exist?
2. **Be specific** - Good: `- 2026-04-02: Use ruff format before ruff check`
3. **Quality gate** - Only record patterns confirmed in 2+ sessions
4. **Curate actively** - Before adding, remove stale entries
5. **Escalate** - Move important patterns to framework docs
6. **No bloat** - If section exceeds 20 entries, remove old ones first

## What to Record

### Good candidates for memory:
- **Confirmed patterns** observed across 2+ sessions
- **Effective conventions** specific to this project
- **Troubleshooting solutions** that worked
- **Tool preferences** discovered through experience

### Poor candidates (put in framework docs instead):
- Universal best practices (not project-specific)
- Security policies
- Patterns that should be documented as invariants
- Anything that belongs in `AGENTS.md` or skill files

## Deployment: Global vs Repo-Local

### Repo-Local Deployment (Default)

When deploying with `--tools <platform>` (without `--global`):

- Memory file deploys to the **project directory**
- Each project has its own isolated memory
- Memory is versioned with the project (travels with git)

### Global Deployment (Cross-Project)

When deploying with `--global`:

- Memory file deploys to **user home directory**
- Memory is shared across all projects
- Useful for universal patterns and conventions

| Platform | Global Memory Path |
|----------|------------------|
| Kilo CLI | `~/.config/kilo/AGENT_MEMORY.md` |
| OpenCode CLI | `~/.config/opencode/AGENT_MEMORY.md` |
| Claude Code | `~/.claude/AGENT_MEMORY.md` |
| OpenClaw | `~/.openclaw/AGENT_MEMORY.md` |

### Precedence Rules

**Repo-local takes precedence over global.** This means:
- Project-specific memory is not overwritten by global memory
- Each project can have its own curated memory
- Global memory supplements (doesn't replace) project memory

## Platform-Specific Notes

### Kilo CLI

Kilo CLI uses `.kilo/instructions.md` at repo root for framework context (local deploy) or `~/.config/kilo/instructions/localsetup.md` (global deploy). The memory file is at `.kilo/AGENT_MEMORY.md` (local) or `~/.config/kilo/AGENT_MEMORY.md` (global).

**Setup for memory loading:** No additional configuration is required. The deploy script idempotently adds the context file to your `instructions[]` in `kilo.json`/`kilo.jsonc`.

### Cursor

Cursor uses `.cursor/rules/agent-memory.md` (lowercase filename per Cursor conventions). The context file references this automatically.

### Claude Code

Claude Code uses `.claude/AGENT_MEMORY.md`. The `CLAUDE.md` context file references this automatically.

## Integration with Context Files

Each platform's context file (AGENTS.md, CLAUDE.md, etc.) includes a reference to its memory file and the curation rules. The AI agent is prompted to:

1. Check the memory file at session start
2. Update it with new learnings
3. Curate before adding (remove stale entries)
4. Escalate significant patterns to framework docs

## See Also

- [PLATFORM_REGISTRY.md](PLATFORM_REGISTRY.md) - Platform paths and memory file locations
- [MULTI_PLATFORM_INSTALL.md](MULTI_PLATFORM_INSTALL.md) - Deployment options including global
- [SKILLS_AND_RULES.md](SKILLS_AND_RULES.md) - How context and skills interact

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> - Innovate, Automate, Dominate.
</p>
