---
status: ACTIVE
version: 2.2
---

# Skill discovery (public registries)

**Purpose:** How the framework discovers and recommends publicly available skills from external collections (e.g. awesome lists, ClawHub). Used together with skill-creator and skill-importer so users can find similar existing skills before creating or importing.

## Where the registry and index live

- **This project's GitHub repository** maintains its own copy of the public skill registry and (when refreshed) the public skill index. The canonical files live under `framework/docs/`: `PUBLIC_SKILL_REGISTRY.urls` and `PUBLIC_SKILL_INDEX.yaml`. When you install or update the framework, you get these files under `_localsetup/docs/`.
- **Two ways to use them:**
  - **Use the project's maintained copies:** If you do not want to maintain your own list or index, you can download the latest registry and (optionally) index from the project's GitHub repo (e.g. raw files from the default branch, or pull/update the framework so `_localsetup/` gets the latest). That way you always have the project's curated registry URLs and, if the project publishes a pre-built index, an up-to-date index without building it yourself.
  - **Maintain your own:** Edit `_localsetup/docs/PUBLIC_SKILL_REGISTRY.urls` and refresh `PUBLIC_SKILL_INDEX.yaml` locally. Your changes stay in your repo and are not overwritten unless you reinstall or overwrite those files. The agent uses whatever is in `_localsetup/docs/` for discovery.

## Public repo registry

- **File:** `_localsetup/docs/PUBLIC_SKILL_REGISTRY.urls`
- **Format:** One URL per line. Lines starting with `#` are ignored. No trailing spaces. URLs point to skill collections (e.g. [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)), GitHub repos, or index pages the agent can fetch and parse.
- **Maintenance:** The project repo keeps a maintained copy; add or remove URLs as new public registries become available. The agent and any refresh tool read this file to know where to look for skills.

## Public skill index

- **File:** `_localsetup/docs/PUBLIC_SKILL_INDEX.yaml`
- **Schema:** `sources` (optional list of URLs), `updated` (ISO8601 date or datetime of last refresh), `skills` (list of entries with `name`, `description`, `url`, `source_registry`, optional `category`). Used for similarity matching and recommendations.
- **Refresh:** The agent or a script updates the index from the registry URLs: fetch each URL, parse the list (e.g. awesome list markdown, ClawHub API), write normalized entries to the YAML, and set `updated` to the current date/time (ISO8601). To run the refresh script locally: `python3 _localsetup/tools/refresh_public_skill_index.py` (requires Python deps in `_localsetup/requirements.txt`; run `pip install -r _localsetup/requirements.txt` first).

## Index refresh and user prompts

- **When to prompt for refresh:** Base behavior on the index file and the `updated` field. Obtain the current date from the environment (e.g. `date` on Linux/macOS, `Get-Date` in PowerShell) so calculations are correct.
- **Index missing or never refreshed:** If the index file does not exist, or `updated` is null/missing/empty, **always prompt the user** to build or rebuild the index before using discovery: e.g. "The public skill index has not been built yet. I can refresh it now from the registry URLs (this may take a minute). Should I proceed?"
- **Default minimum before prompting:** **7 days.** Do not prompt to refresh if the last refresh (`updated`) was less than 7 days ago. If `updated` is 7 or more days ago, prompt the user to refresh: e.g. "The public skill index was last refreshed on YYYY-MM-DD (X days ago). Would you like to refresh it now for up-to-date recommendations?"
- **On every skill operation:** Whenever the user does a skill operation that uses discovery (creating a skill, importing a skill, or asking to discover/recommend public skills), **remind them** of the last refresh and how long ago it was. For example: "Last index refresh: 2026-02-10 (8 days ago)." Use the actual `updated` date and compute the elapsed time in **days** (e.g. "3 days ago"), **weeks** (e.g. "2 weeks ago"), or **years** (e.g. "1 year ago") as appropriate. Then, if the index is older than 7 days, add the prompt: "The index is over 7 days old. Would you like to refresh it now?"
- **After a refresh:** When the agent or user completes a refresh, set `updated` in the YAML to the current date/time so the next run can compute "last refreshed X days ago" correctly.

## When discovery runs

- **With skill-creator:** When the user starts creating a new skill (after gathering input and proposing name/triggers), load localsetup-skill-discovery: compare the proposed purpose/description to the public index; return top 5 similar skills; present options (see skill doc).
- **With skill-importer:** When the user is about to import from a URL or path, optionally check the public index for similar skills and suggest: "Similar public skills exist; would you like to consider one of these instead or in addition?"

## Recommendation flow

1. **Index and refresh:** Read `PUBLIC_SKILL_INDEX.yaml` (or detect if missing). Get current date from the environment. If index missing or `updated` null: prompt user to build the index; do not proceed until built or user declines. Otherwise show "Last index refresh: YYYY-MM-DD (X days/weeks/years ago)." If age >= 7 days, prompt to refresh. If user agrees to refresh, fetch registry URLs, parse, write YAML, set `updated` to now.
2. Compare user intent (new skill description or candidate skill description) to index entries (e.g. by keyword overlap, description similarity); rank and take top 5.
3. **Present recommendations** using the **default recommendation output format** (see below). After the formatted list, offer the four options: (1) In-depth summary of each, (2) Use one (pull and run through our import process so it's compliant), (3) Continue working on your own, (4) Adapt from one (use as base and customize).
4. If user chooses (2) or (4): resolve the skill URL (e.g. from awesome list link to actual repo), then run the skill-importer workflow (fetch, scan, validate, screen, user selects, duplicate check, import). The imported skill becomes framework-compliant; no need to recreate from scratch.

### Default recommendation output format

Discovery **always** presents the top 5 (or fewer) matches in this structure. Do not use a shorter list or bare names only.

- **Intro line:** One sentence naming the topic or query (e.g. "Top 5: DevOps on a Linux server" or "Top 5 similar to your description: …").
- **For each skill:** Bold skill name; **URL:** (full link from index); **Description:** (index description verbatim); **Why it's a good fit:** one to three sentences tying the skill to the user's intent (specific, not generic).
- **After the list:** Optional short line on using these in the framework (e.g. "To add any of these, use the skill-importer with the skill URL."), then the four options.

The skill **localsetup-skill-discovery** (SKILL.md) contains the full format and an example; agents must follow it when returning recommendations.

## Reference

- Load skill **localsetup-skill-discovery** when the user is creating a new skill, importing a skill, or asking to discover/recommend public skills. Use in conjunction with localsetup-skill-creator and localsetup-skill-importer.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
