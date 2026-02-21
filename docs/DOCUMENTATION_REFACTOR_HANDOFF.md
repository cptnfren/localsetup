# Documentation comprehensive refactor: handoff

**Completed:** 2026-02-20 (per execution date).

## Verification checklist

Use this to confirm the refactor is complete and links behave as expected.

1. **Link resolution**  
   Open the root [README](README.md) and [_localsetup/docs/QUICKSTART.md](_localsetup/docs/QUICKSTART.md) on GitHub (or in a GFM preview). Click a sample of links (e.g. SKILLS.md, FEATURES.md, PLATFORM_REGISTRY.md, QUICKSTART.md, VERSIONING.md, root README from package README). Confirm each resolves to the correct file.

2. **Unlinked bare refs**  
   From repo root run:
   ```bash
   rg 'See [A-Z][a-zA-Z_]+\.md' _localsetup/docs README.md docs --glob '*.md' || true
   rg 'in [A-Z][a-zA-Z_]+\.md' _localsetup/docs README.md docs --glob '*.md' || true
   ```
   Fix or document any remaining matches. (Some may be inside code blocks or examples; only prose refs need links.) Platform default for generated content: [_localsetup/docs/OUTPUT_AND_DOC_GENERATION.md](_localsetup/docs/OUTPUT_AND_DOC_GENERATION.md) (rich output, links, humanized).

3. **QUICKSTART box counts**  
   In [_localsetup/docs/QUICKSTART.md](_localsetup/docs/QUICKSTART.md) confirm:
   - **Non-interactive one-liners:** 8 boxes (4 Linux/macOS: Cursor, Claude Code, Codex CLI, OpenClaw; 4 Windows PowerShell: same four).
   - **From a local clone:** 8 boxes (4 Linux/macOS + 4 Windows PowerShell, same platforms).
   - **Updating:** 2 separate boxes (preserve policy; fail-on-conflict).

4. **README agreement**  
   Confirm root [README](README.md) and [_localsetup/README.md](_localsetup/README.md) agree on:
   - Version (e.g. 2.5.0).
   - Phrasing for shipped skills ("all shipped skills" with link to SKILLS.md).
   - Supported platforms list (cursor, claude-code, codex, openclaw).

5. **Case sensitivity**  
   Spot-check that link targets match actual file names (e.g. `FEATURES.md` not `Features.md`). Grep for `\.md)` or `\.yaml)` in modified files and confirm path casing matches the filesystem.

---

## Diff/summary (files changed)

| File | Summary |
|------|--------|
| README.md | Problem-led opening (pain points → solution → bright future); registry/shipped links; maintainer wording softened; platform registry link. |
| _localsetup/README.md | Intro line added: link to root README for first-time setup; version sync; maintainer ref softened. |
| _localsetup/docs/AGENTIC_DESIGN_INDEX.md | Doc and registry refs turned into links (DECISION_TREE, PRD_SCHEMA, WORKFLOW_REGISTRY, SKILL_*, PUBLIC_SKILL_*). |
| _localsetup/docs/FEATURES.md | PLATFORM_REGISTRY, SKILLS.md, PUBLIC_SKILL_REGISTRY.urls, PUBLIC_SKILL_INDEX.yaml linked in tables. |
| _localsetup/docs/PLATFORM_REGISTRY.md | OPENCLAW_CONTEXT and SKILLS_AND_RULES linked; maintainer sentence softened. |
| _localsetup/docs/QUICKSTART.md | Restructured to 8 curl + 8 local-clone + 2 update boxes; one command per box; Windows PowerShell only; Next steps "all shipped skills" + link. |
| _localsetup/docs/README.md | "All 34 built-in skills" → "All shipped skills" (no number). |
| _localsetup/docs/SKILLS_AND_RULES.md | PUBLIC_SKILL_INDEX, TASK_SKILL_MATCHING, PLATFORM_REGISTRY linked. |
| _localsetup/docs/SKILL_DISCOVERY.md | PUBLIC_SKILL_REGISTRY.urls and PUBLIC_SKILL_INDEX.yaml linked throughout. |
| _localsetup/docs/SKILL_NORMALIZATION.md | INPUT_HARDENING_STANDARD.md linked. |
| _localsetup/docs/TASK_SKILL_MATCHING.md | SKILLS_AND_RULES, PUBLIC_SKILL_INDEX, PLATFORM_REGISTRY, References section linked. |
| _localsetup/docs/TOOLING_POLICY.md | INPUT_HARDENING_STANDARD.md linked. |
| _localsetup/docs/WORKFLOW_REGISTRY.md | Maintainer sentence softened to generic "separate maintainer repository". |
| _localsetup/skills/localsetup-context/SKILL.md | PRD_SCHEMA, AGENTIC_DESIGN_INDEX, WORKFLOW_REGISTRY, DECISION_TREE, INPUT_HARDENING, TOOLING_POLICY, PUBLIC_SKILL_INDEX, TASK_SKILL_MATCHING linked (../../docs/). |
| _localsetup/skills/localsetup-task-skill-matcher/SKILL.md | PLATFORM_REGISTRY, PUBLIC_SKILL_INDEX, TASK_SKILL_MATCHING, SKILLS_AND_RULES linked (../../docs/). |
| docs/VERSIONING.md | Maintainer refs softened (private/maintainer publish → separate maintainer repository workflow). |

**Total:** 16 files changed, ~179 insertions, ~68 deletions.
