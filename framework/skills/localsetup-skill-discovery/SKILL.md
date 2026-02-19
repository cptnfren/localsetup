---
name: localsetup-skill-discovery
description: "Discover and recommend public skills from external registries (e.g. awesome lists, skill hubs). Use when the user is creating a new skill, importing a skill, or asking to find similar public skills. Maintains PUBLIC_SKILL_REGISTRY.urls and PUBLIC_SKILL_INDEX.yaml; returns top 5 similar matches and offers in-depth summary, use public skill (pull + import), continue on own, or adapt."
metadata:
  version: "1.3"
---

# Skill discovery (public registries)

**Purpose:** Let users discover publicly available skills from external collections (e.g. [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)) so they can reuse or adapt existing skills instead of building from scratch. Runs in conjunction with skill-creator and skill-importer: when the user is creating or importing a skill, recommend up to five similar public skills and offer clear next steps.

## When to use this skill

- User is **creating a new skill** (skill-creator flow): after they describe the skill or propose name/triggers, run discovery and recommend similar public skills before they draft.
- User is **importing skills** (skill-importer flow): optionally check public index for similar skills and suggest "consider these instead or in addition."
- User asks to **discover**, **find similar**, or **recommend public skills** for a topic or description.

## Registry and index

- **Public repo registry:** `_localsetup/docs/PUBLIC_SKILL_REGISTRY.urls`  - One URL per line (skill collections, awesome lists, GitHub repos). Lines starting with `#` are ignored. This defines where to look for public skills.
- **Public skill index:** `_localsetup/docs/PUBLIC_SKILL_INDEX.yaml`  - YAML with `sources`, `updated` (ISO8601 date/datetime of last refresh), and `skills`. Used for similarity matching. Refresh from registry URLs; set `updated` when done. See "Index refresh and prompts" below.
- **Project-maintained copies:** The framework's GitHub repository keeps its own copy of the registry and index. Users who do not want to maintain their own can download these files from the project repo (e.g. raw URLs from the default branch) or update the framework so `_localsetup/docs/` gets the latest; alternatively they can edit and refresh locally.

## Index refresh and prompts

- **Current date:** Obtain the current date from the environment (e.g. `date` on Linux/macOS, `Get-Date` in PowerShell) for all age calculations.
- **Index missing or never refreshed:** If the index file does not exist or `updated` is null/missing/empty, **always prompt the user** to build the index: e.g. "The public skill index has not been built yet. I can refresh it now from the registry URLs. Should I proceed?" Do not run discovery until the user agrees and the index is built, or the user declines.
- **Default minimum: 7 days.** Do not prompt to refresh if last refresh was less than 7 days ago. If `updated` is 7 or more days ago, **prompt to refresh**: e.g. "The index was last refreshed on YYYY-MM-DD (X days ago). Would you like to refresh it now?"
- **On every skill operation:** Whenever you use this skill (create, import, or discover), **remind the user**: "Last index refresh: YYYY-MM-DD (X days ago)." or "(X weeks ago)" or "(X years ago)" using the `updated` value and the current date. Then if the index is older than 7 days, add: "The index is over 7 days old. Would you like to refresh it now?" If the user says yes, perform the refresh (fetch registry URLs, parse, write YAML, set `updated` to now).
- **After refresh:** Write `updated` to the YAML with the current date/time (ISO8601) so the next run shows the correct "last refreshed" age.

## Workflow (agent steps)

1. **Check index and last refresh**  - Read PUBLIC_SKILL_INDEX.yaml (or confirm it is missing). Get current date from the environment. If file missing or `updated` is null/empty: prompt user to build the index; do not continue until built or user declines. Otherwise compute age (days/weeks/years since `updated`) and show: "Last index refresh: <date> (<X days/weeks/years ago>)." If age >= 7 days, prompt: "The index is over 7 days old. Would you like to refresh it now?" If user says yes, refresh (fetch registry URLs, parse, write YAML, set `updated` to now).
2. **Match and rank**  - Read the user's intent (proposed skill description, or candidate skill name/description). Compare to each index entry (e.g. keyword overlap, description similarity). Return the **top 5** best matches. If fewer than 5 exist, return what is available.
3. **Present recommendations**  - Always use the **default recommendation format** (see below). After the formatted list, offer: "Would you like: **(1) In-depth summary** of each, **(2) Use a public skill** (I'll pull it from the source and run it through our import process so it's compliant), **(3) Continue on your own** (ignore these and keep creating/importing as planned), or **(4) Adapt from one** (use one as a base and customize)?" Ask the user to choose.
4. **Handle choice**  - (1) For each of the top 5, fetch or summarize the skill (e.g. from README or SKILL.md) and present a short in-depth summary. (2) Resolve the skill URL (e.g. from awesome list to actual repo), then run the **skill-importer** workflow: fetch, run skill_importer_scan, validate, security screen, user selects, duplicate/overlap check, import. The result is a framework-compliant skill; no need to recreate. (3) Do nothing; continue with skill-creator or skill-importer as before. (4) Same as (2) but after import, help the user adapt the skill (edit name, description, add/remove sections) so it fits their case.

## Integration with skill-creator and skill-importer

- **Skill-creator:** After "Decide name and triggers" (and before or after "Duplicate, overlap, and namespace check"), run this discovery: get top 5 similar public skills, present the four options. If user picks (2) or (4), switch to import flow for the chosen public skill; then for (4) guide adaptation.
- **Skill-importer:** Before or after "User selects" which skills to import, optionally run discovery against the selected candidates and suggest: "Similar skills are available from public registries; would you like summaries or to pull one instead?"

## Default recommendation output format

**Always** present the top 5 (or fewer) matches in this structure. Do not substitute a shorter list or bare names only.

1. **Intro line**  - One sentence that names the topic or query (e.g. "Top 5: DevOps on a Linux server" or "Top 5 similar to your description: …").
2. **For each recommended skill**, output in order:
   - **Skill name** (bold, as in the index).
   - **URL:** the skill's `url` from the index (full link).
   - **Description:** the index `description` verbatim (one line).
   - **Why it's a good fit:** one to three sentences explaining why this skill matches the user's intent (e.g. relevance to their topic, use case, or query). Be specific; avoid generic praise.
3. **After the list**  - One short line on how to use these in the framework (e.g. "To add any of these, use the skill-importer with the skill URL.") if relevant, then the four options (in-depth summary, use public skill, continue on own, adapt from one).

Example for one entry:

**senior-devops**  
**URL:** https://github.com/openclaw/skills/tree/main/skills/alirezarezvani/senior-devops/SKILL.md  
**Description:** Comprehensive DevOps skill for CI/CD, infrastructure.  
**Why it's a good fit:** Directly targets "DevOps": CI/CD and infrastructure. Best single match when you want broad DevOps guidance (pipelines, infra as code, practices) that applies to Linux servers and beyond.

## Options summary

| Option | Action |
|--------|--------|
| In-depth summary | For each of the top 5, fetch/summarize the skill and show what it does in detail. |
| Use public skill | Pull the skill from the source (e.g. GitHub), run through import (scan, validate, screen, duplicate check, import). User gets a compliant skill without recreating. |
| Continue on own | No change; user keeps creating or importing as they were. |
| Adapt from one | Same as "Use public skill" then help user customize (rename, edit description, add/remove content). |

## Reference

- _localsetup/docs/SKILL_DISCOVERY.md  - Registry and index format; when discovery runs; recommendation flow.
- _localsetup/docs/PUBLIC_SKILL_REGISTRY.urls  - One URL per line; where to look for public skills.
- _localsetup/docs/PUBLIC_SKILL_INDEX.yaml  - Index of skills for similarity; refresh from registry.
- Use with **localsetup-skill-creator** and **localsetup-skill-importer** when creating or importing.
