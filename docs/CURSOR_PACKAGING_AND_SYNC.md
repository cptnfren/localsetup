# Cursor packaging and sync

**Purpose:** Understand the canonical source vs deploy target relationship. Avoid packaging mistakes.

## Canonical source vs deploy target

| Location | Role |
|----------|------|
| `_localsetup/skills/localsetup-*/` | **Canonical.** Edit skill content here. This is what gets committed and published. |
| `_localsetup/templates/cursor/` | **Canonical** for Cursor context files. |
| `.cursor/skills/localsetup-*/` | **Deploy target.** Filled by `deploy --tools cursor`. Do not edit for framework content. |
| `.cursor/rules/*.mdc` | **Deploy target.** Filled by deploy. Do not edit for framework context. |

## One-way rule

`deploy` copies from `_localsetup` to `.cursor`. It never copies from `.cursor` back into `_localsetup`.

**If you edit in `.cursor/` for testing:** Use `scripts/sync-cursor-to-source.py` to promote changes back to source.

## Deploy command

After editing `_localsetup/`, run deploy so Cursor sees the change:

```bash
./_localsetup/tools/deploy --tools cursor --root .
```

## Before commit: check for drift

Run the compare script to ensure you don't overwrite newer `.cursor` with older packaged:

```bash
./scripts/compare-packaged-vs-cursor
```

The script reports:
- **FILE_ONLY_IN_PACKAGED:** File exists only in `_localsetup/` (not in `.cursor/`).
- **FILE_ONLY_IN_CURSOR:** File exists only in `.cursor/` (not deployed yet or was removed from source).
- **Different content:** Same path exists in both but content differs.
- **NEWER in .cursor:** The copy under `.cursor/` was modified more recently. Run `sync-cursor-to-source.py` to harvest, or re-run deploy to overwrite.
- **NEWER in packaged:** Packaged version is newer. Run deploy to update `.cursor/`.

## Sync .cursor back to source (git 3-way merge)

When you've made changes in `.cursor/` and want to promote them back to `_localsetup/`:

```bash
./scripts/sync-cursor-to-source.py --repo-root .
```

This uses git-based 3-way merge (base=HEAD):
- Copies from `.cursor` to `_localsetup` only when:
  1. `.cursor` differs from HEAD
  2. `_localsetup` equals HEAD (or is missing)
  3. `.cursor` was modified after the last commit that touched that path
- Reports conflicts when both diverged from base.

Use `--dry-run` to see what would be copied or skipped.

## Related

- `docs/WORKFLOW_INDEX.md` - `compare-cursor` and `sync-runtime` workflow entries.
- `scripts/sync-cursor-to-source.py` - Git 3-way sync implementation.
- `scripts/compare-packaged-vs-cursor` - Compare packaged vs cursor status.
