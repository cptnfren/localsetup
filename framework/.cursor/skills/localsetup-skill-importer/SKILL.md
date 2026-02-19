---
name: localsetup-skill-importer
description: Import external skills from a URL (GitHub or other) or local path; discover, validate, security-screen, and summarize each skill so the user can choose which to import. Use when the user wants to add skills from a repo/URL or local folder, or when screening and selecting skills to add to the framework.
metadata:
  version: "1.3"
---

# Skill importer (framework)

**Purpose:** Let the user point at a **URL** (e.g. GitHub repo) or **local path** containing skills; discover and validate them; run a heuristic security screen (no execution); produce a **per-skill brief** (what it does, what it has, what kind of code); then let the user **choose which to import** and complete registration.

## When to use this skill

- User wants to "import skills from this URL" or "add skills from GitHub/anthropics/skills."
- User has a local folder or markdown and wants to screen/import skills.
- User asks to "parse a repo and add the skills" or "validate and import skills."

## Workflow (agent steps)

1. **Get source**  - URL or local path. If URL: clone or download to a temp dir (e.g. `git clone --depth 1 <url> /tmp/skills-src`); then use that path as scan root. If local path: use as scan root.
2. **Scan**  - Run `_localsetup/tools/skill_importer_scan <path>` (or `.ps1` on Windows). It discovers skill dirs (containing SKILL.md with valid frontmatter), validates format, lists contents and code types, and runs heuristic security checks. Output: per-skill summary.
3. **Summarize for user**  - For each skill present a brief:
   - **What it does**  - From description (and body if needed).
   - **What it has**  - Scripts, references, assets; file types and languages.
   - **Code**  - Kinds of code (Python, Bash, etc.); any deps or compatibility notes.
   - **Security**  - Screening result: no concerns, or "Review: …" with file/line. Do not auto-block; let the user decide.
4. **User selects**  - Ask which skills to import (by name or "all"). Use AskQuestion or a clear list with instructions (e.g. "Reply with names or 'all'").
4b. **Public skill discovery (optional)**  - For each selected candidate, optionally load **localsetup-skill-discovery**: check PUBLIC_SKILL_INDEX.yaml for similar public skills; if relevant matches exist, suggest "Similar public skills are available; would you like in-depth summaries or to pull one instead?" and offer the same four options (in-depth summary, use public skill, continue, adapt).
5. **Duplicate, overlap, and namespace check**  - Before importing each selected skill, compare to existing framework skills. List existing skills from `framework/skills/` (each dir name and SKILL.md `name` + `description`). For each candidate: (a) **Namespace collision**  - same `name` or directory as an existing skill: warn and offer **Ignore new**, **Replace existing**, **Merge** (combine best of both), or **Create as new** (different name). (b) **High overlap**  - no name match but description/purpose/triggers very similar to an existing skill: warn and offer the same four options. Do not auto-replace or auto-merge; get explicit user choice. For **Merge**, combine content from both into one skill and replace the existing; do not add the candidate as a second copy.
6. **Import**  - For each selected, after user choice (and any merge/rename): copy dir to `framework/skills/<name>/`; optionally rename to `localsetup-<name>` and set `name` in frontmatter; add `metadata.version: "1.0"` if missing; register in every file in _localsetup/docs/PLATFORM_REGISTRY.md § Skill registration (new skills); optionally run deploy.
7. **Confirm**  - Tell the user what was imported and that they can run deploy.

## Security screening (heuristic only)

- Tool does **not** execute any skill code. It only scans file contents.
- Flags patterns that may indicate risk: e.g. `eval(`, `curl | sh`, `base64 -d` to shell, `Invoke-Expression`, hardcoded tokens. Output is "Review: …" for the user; do not block import automatically.

## Sources

- **URL**  - GitHub repo, archive link, or any fetchable URL. Agent fetches; then runs scan on the resulting path.
- **Local path**  - Directory on disk with skill subdirs.
- **Single markdown**  - Use the skill-creator workflow to create a new skill from a doc; that skill is then framework-compatible and can be used with this importer flow for batch consistency.

## Compatibility

- Only directories that contain a valid SKILL.md (Agent Skills spec: `name`, `description`) are considered skills. Imported skills remain spec-compliant and interchangeable (see _localsetup/docs/SKILL_INTEROPERABILITY.md).

## Duplicate and overlap (user options)

- Check each candidate against existing `framework/skills/` (names and descriptions). On **namespace collision** (same name/dir) or **high overlap** (very similar purpose), warn and offer: **Ignore new**, **Replace existing**, **Merge** (best of both into one), **Create as new** (e.g. different name). User choice is final.

## Reference

- _localsetup/docs/SKILL_IMPORTING.md  - Full workflow, duplicate/overlap checks, tool usage, security notes.
- _localsetup/docs/SKILL_DISCOVERY.md  - Public registries; use localsetup-skill-discovery to recommend similar public skills when importing.
- _localsetup/docs/PLATFORM_REGISTRY.md  - Registration file list after import.
- _localsetup/docs/SKILL_INTEROPERABILITY.md  - Import/export and spec.
