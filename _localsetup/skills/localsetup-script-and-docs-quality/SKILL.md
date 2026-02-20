---
name: localsetup-script-and-docs-quality
description: "Markdown/encoding standards, script generation quality, file creation discipline, documentation discipline. Use when generating scripts, creating/editing markdown or docs."
metadata:
  version: "1.1"
---

# Script and docs quality

## 15. Markdown compatibility (CRITICAL)

- **ASCII-first:** No Unicode emoji, box-drawing, or arrow symbols in markdown. Use [OK], [FAIL], [WARNING], [YES], [NO]; use -> not arrow; use * or - for bullets.
- **No EM dash:** Do not use the EM dash character (—, U+2014) in any user-facing text. Use a space and hyphen ( - ) or a plain hyphen instead.
- **Encoding:** UTF-8; prefer pure ASCII. Verify in markdown preview before committing.

## 16. Script generation quality (all languages)

- **Comments:** Header with purpose, usage, parameters; document each function; descriptive names.
- **Error handling:** Try-catch (or equivalent); validate inputs; check prerequisites; no silent failures.
- **STDOUT:** All scripts output to console; pipeable; STDOUT for normal, STDERR for errors.
- **Structure:** Break into functions; clear error messages with source/trace; actionable guidance.
- **Bash:** set -euo pipefail, trap for cleanup. **Python:** type hints, docstrings, context managers. **PowerShell:** try/catch/finally, Write-* cmdlets.

## 7. File creation discipline

- Before creating any file: verify it belongs; minimal approach; "Is this essential?" Consolidate rather than duplicate.

## 2. Documentation discipline

- **_localsetup/docs/ is ONLY for framework documentation.** Not for IDE setup or external tool guides. All docs must have status (ACTIVE/PROPOSAL/DRAFT/DEPRECATED/ARCHIVED). Check status before assuming a feature is implemented. See _localsetup/docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md.
