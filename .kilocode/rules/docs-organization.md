# Migrated from .cursor/rules/docs-organization.mdc
# Original: /mnt/data/devzone/localsetup-2/.cursor/rules/docs-organization.mdc

## Docs organization rules

### Scope

These rules describe how agents should use the `localsetup-docs-organization` skill when creating, moving, or significantly updating documentation in this repo.

### When to invoke the docs organization skill

- When a user asks to create documentation, for example:
  - "create documentation for X"
  - "write a runbook"
  - "document this feature"
  - "add a guide for Y"
- When a user asks to update documentation, for example:
  - "update the docs for Y"
  - "extend the architecture overview for Z"
  - "improve the runbook for on call"
- When a tool or workflow needs to add or reorganize markdown docs under the project docs root.

In these cases, agents should:

1. Call the `localsetup-docs-organization` skill with at least:
   - intent
   - title
2. Include summary, doc_type_hint, tags, and allow_nonstandard_docs when available.
3. Use the returned proposed_path, filename, and index_entry as the default placement and metadata.

### Default behavior

- Docs should normally be created or moved into the path recommended by the docs organization skill.
- Agents should update `docs/index.yaml` and `docs/INDEX.md` in line with the index_entry returned by the skill.
- Agents should prefer updating existing docs suggested by the skill over creating near duplicates that fragment information.

### Strict advisory enforcement

- If a user explicitly wants a different location than the recommended one:
  - Agents should explain that it is a non standard placement and show the recommended path and filename.
  - Agents should only proceed with the non standard location if the user accepts this and sets allow_nonstandard_docs or the equivalent override in their request.
- When a non standard location is used:
  - The index entry must mark nonstandard_location as true.
  - Agents should still update `docs/index.yaml` and `docs/INDEX.md` so navigation stays accurate.

Creating or moving docs without consulting `localsetup-docs-organization` should be treated as non compliant with these rules, except when the user explicitly instructs otherwise and understands the impact.

### Framework docs guardrail

- Framework documentation under `_localsetup/docs/` is governed by framework level rules and lifecycle docs.
- These docs may adopt the same metadata pattern and index design, but agents must not move them out of `_localsetup/docs/` or override lifecycle guidance defined in `_localsetup/docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md`.

