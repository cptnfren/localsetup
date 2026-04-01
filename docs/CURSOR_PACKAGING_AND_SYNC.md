# Cursor packaging and sync (maintainer)

**Purpose:** Avoid packaging mistakes when working with the .cursor folder in the public repo. Canonical source is _localsetup; deploy copies out to .cursor. Run the compare script before commit/publish so you don't overwrite newer .cursor with older packaged, or ship without packaging changes.

## Canonical source vs deploy target (in public repo)

| Location (in public repo) | Role |
|---------------------------|------|
| `_localsetup/skills/localsetup-*/` | **Canonical.** Edit skill content here. This is what gets committed and published. |
| `_localsetup/templates/cursor/` | **Canonical** for Cursor context (localsetup-context.mdc, localsetup-context-index.md). |
| `.cursor/skills/localsetup-*/` | **Deploy target.** Filled by `deploy --tools cursor`. Do not edit for framework content. |
| `.cursor/rules/localsetup-context.mdc`, `localsetup-context-index.md` | **Deploy target.** Filled by deploy. Do not edit for framework context. |

**One-way rule:** Deploy copies from _localsetup to .cursor. It never copies from .cursor back into _localsetup. If you edit a file under .cursor/skills or .cursor/rules (for framework content), that change is orphaned unless you harvest it (e.g. via `publish-from-dogfood`).

## Before commit / before publish (check for drift)

From the **maintainer** repo root, run:

```bash
./scripts/compare-packaged-vs-cursor --public-repo /path/to/localsetup-2
```

Replace `/path/to/localsetup-2` with the actual path to the public repo (the one that contains `_localsetup/` and `.cursor/`).

The script reports:

- **FILE_ONLY_IN_PACKAGED** / **SKILL_ONLY_IN_CURSOR:** File or skill exists in one place only.
- **Different content:** Same path exists in both but content differs.
- **NEWER in .cursor:** The copy under .cursor was modified more recently. Risk: running deploy in the public repo would overwrite that change with the (older) packaged version. **Action:** Run `scripts/publish-from-dogfood --public-repo <path>` to harvest .cursor back into _localsetup, or copy the changed file(s) into _localsetup and then run deploy in the public repo. Then commit in the public repo.
- **NEWER in packaged:** Packaged version is newer. Run deploy in the public repo to update .cursor.

## After editing packaged skills or Cursor templates (in public repo)

1. Edit only under `_localsetup/skills/` or `_localsetup/templates/cursor/` in the public repo.
2. In the public repo, run deploy so Cursor sees the change:  
   `./_localsetup/tools/deploy --tools cursor --root .`
3. Commit the changes under _localsetup in the public repo. Do not rely on .cursor/skills or .cursor/rules as source of truth; they are generated.

## Publishing workflow (maintainer)

1. Ensure all intended changes are in the public repo under _localsetup (skills, templates, docs).
2. Run `./scripts/compare-packaged-vs-cursor --public-repo /path/to/localsetup-2`. Resolve any **NEWER in .cursor** by running `publish-from-dogfood` (harvest) or by copying those files into _localsetup and re-running deploy in the public repo; then commit in the public repo.
3. Run framework audit from the public repo if desired (e.g. `python _localsetup/skills/localsetup-framework-audit/scripts/run_framework_audit.py --output /path/to/report.md`).
4. Run publish/maintain from the maintainer repo as usual (bump, commit, push in the public repo).

## Harvest (publish-from-dogfood): git 3-way merge

When you run `publish-from-dogfood`, the harvest step uses a **git-based 3-way merge**. The "base" is the file content as in the last commit (HEAD) in the public repo. It copies from .cursor into _localsetup only when: (1) the .cursor version **differs from base**, (2) the packaged version **equals base** (or is missing), and (3) the .cursor file was **modified after the last commit** that touched that path (cursor mtime is newer than that commit). So touch or a trivial edit in .cursor does not win: if the packaged version was committed more recently, we skip. When both have diverged from base, we report a conflict and skip. New files (not in git): copy when packaged is missing; when both exist, mtime is used as a fallback. Implementation: `scripts/sync-cursor-to-source.py`. Use `--dry-run` to see what would be copied or skipped.

## Related

- **WORKFLOW_INDEX.md** – `compare-packaged-vs-cursor` and `dogfood` (publish-from-dogfood) entries.
- **publish-from-dogfood** – Harvests .cursor back to _localsetup (newer wins), then syncs docs, bumps, commits, and optionally pushes in the public repo.
- **sync-cursor-to-source.py** – Per-file newer-wins sync; used by publish-from-dogfood. Optional: `--dry-run`.
- Public repo: deploy script is `_localsetup/tools/deploy`; packaging/sync checks are documented here in the maintainer repo.
