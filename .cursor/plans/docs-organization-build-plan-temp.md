## Docs organization skill: end to end build plan

### 1. Goals and constraints

- Create a new Localsetup skill that:
  - Classifies documentation requests.
  - Chooses or creates folder slugs based on that classification.
  - Encourages updating existing docs instead of creating bloat.
  - Maintains a human index and a machine index.
- Keep it repo adaptable:
  - No hardcoded global taxonomy.
  - Folder names are generic, reusable slugs chosen per repo.
- Make it effectively always on:
  - Agents route any doc work through this behavior by default.
  - Strict advisory, not hard blocking.
- Reuse existing standards:
  - Script and docs quality rules.
  - Humanizer skill for writing style.

---

### 2. Skill file: structure and contract

Target file:

- `_localsetup/skills/localsetup-docs-organization/SKILL.md`

2.1 Frontmatter

- name: `localsetup-docs-organization`
- description: short summary of purpose.
- metadata:
  - version: start at `"0.1.0"`.

2.2 Purpose section

Describe in plain language:

- This skill is the repo level docs router.
- It decides:
  - Where docs live.
  - How they are named.
  - How the index stays current.
- It is used for:
  - New doc creation.
  - Moving docs.
  - Significant doc updates.

2.3 Inputs section

Define input fields clearly:

- intent (required)
  - Short description of what the doc is for.
- title (required)
  - Proposed human title.
- summary (optional)
  - One to three sentence description.
- doc_type_hint (optional)
  - Values like `runbook`, `adr`, `spec`, `how_to`, `notes`, `reference`.
- tags (optional)
  - List of strings such as component names, domains, features.
- allow_nonstandard_docs (optional, default false)
  - Explicit override flag for non standard locations.

2.4 Outputs section

Define output fields:

- category_label
  - Human label for doc category, such as `architecture`, `runbook`, `decision_log`, `spec`, `how_to`, `notes`, `reference`.
- category_slug
  - Folder safe slug derived from label, lowercase ASCII, hyphen separated.
- component_slug (optional)
  - Slug for primary system or feature.
- proposed_path
  - Repo relative folder path, for example `docs/incident-runbooks/payments`.
- filename
  - Slugified filename, for example `payments-architecture-overview.md`.
- index_entry
  - Structured record suitable for `docs/index.yaml`.
- warnings
  - List of warning strings, including `nonstandard_location` when overrides happen.

2.5 Behavior overview section

Summarize behavior in one place:

- Classify request.
- Suggest folder and filename.
- Decide update versus new file.
- Maintain both indexes.
- Enforce strict advisory rules.

You will go into detail in later sections.

---

### 3. Classification and folder slug behavior

3.1 Classification inputs

- Use fields:
  - intent
  - title
  - summary
  - doc_type_hint
  - tags
- Prefer doc_type_hint if present when choosing category_label.
- If doc_type_hint is missing:
  - Infer a type from intent, title, and tags.

3.2 Category labels

- Keep a small set of example labels in the doc, but explicitly say they are examples:
  - architecture
  - runbook
  - decision_log
  - spec
  - how_to
  - notes
  - reference
- State the rule:
  - Always prefer reusing category labels already used in this repo.
  - Only create a new label when the intent clearly does not fit any existing one.

3.3 Manifest of categories

- Define a manifest file location:
  - `docs/.docs-classifications.yaml`
- Define its structure, for example:

  - Each entry holds:
    - label
    - slug
    - description

- Behavior:
  - On classification:
    - Load this manifest if present.
    - If a label is available that fits, reuse it and its slug.
    - If none fit, create a new label plus slug and append to the manifest.
  - Clarify that manifest is repo local and not part of the framework.

3.4 Slug generation

Describe slug rules:

- Lowercase everything.
- Replace spaces and separators with `-`.
- Drop characters that are not safe across common filesystems.
- Examples:
  - `Incident runbooks` to `incident-runbooks`
  - `API reference` to `api-reference`

3.5 Proposed path

- Docs root:
  - Default to `docs/` but make this configurable later.
- Path rules:
  - Base pattern:
    - `docs/<category_slug>/`
  - If a clear component_slug exists:
    - `docs/<category_slug>/<component_slug>/`
- Say explicitly:
  - Only add additional depth when there is a clear structural reason.
  - Avoid deeply nested trees by default.

---

### 4. Document placement and reuse logic

4.1 Reuse before create

Define the standard flow for a new request:

- Step 1:
  - Run classification to produce category_label, category_slug, component_slug, and proposed_path.
- Step 2:
  - Search for existing docs that might be the right place to update.
  - Primary search surface is `docs/index.yaml` if it exists.
  - Use:
    - Title similarity.
    - Shared tags.
    - Same category_label and component_slug.
- Step 3:
  - Decide if there is a strong candidate for update.
  - Examples of strong match:
    - Same component_slug and very similar title.
    - Same category_label and overlapping tags, where topic sounds the same.
- Step 4:
  - If a strong match exists:
    - Suggest updating that existing doc.
    - Return both:
      - The proposed new location.
      - The recommended existing path.
- Step 5:
  - If caller picks update:
    - Keep path and filename from the existing doc.
    - Only change content and metadata.
  - If caller still wants a new doc:
    - Proceed to new file creation.

4.2 New file creation

Describe filename behavior:

- Base:
  - Slugify the title to a file name and append `.md`.
- Conflict handling:
  - If file already exists in proposed_path:
    - If topic is clearly the same, suggest merging.
    - If it is truly distinct, append a small semantic suffix:
      - Example:
        - `payments-architecture-overview-v2.md`
        - `payments-architecture-deep-dive.md`
- Folder behavior:
  - If proposed_path does not exist:
    - It should be created under the docs root.

4.3 Doc metadata header

Specify minimal metadata for managed docs:

- status
  - Use values from `DOCUMENT_LIFECYCLE_MANAGEMENT.md`.
- last_updated
  - ISO date.
- doc_type
  - Same language as doc_type_hint when appropriate.
- tags
  - List of strings.

Define update rules:

- On each significant update:
  - Refresh last_updated.
  - Optionally adjust status if changes stabilize the doc.

---

### 5. Index design and ownership

5.1 Machine index

Path:

- `docs/index.yaml`

Schema for each entry:

- id
  - Stable identifier.
  - Either:
    - A deterministic slug derived from the path.
    - Or a generated UUID stored in both doc header and index.
- path
  - Repo relative path to the doc.
- title
- category_label
- category_slug
- component_slug (optional)
- status
- last_updated
- doc_type
- tags
- nonstandard_location (optional boolean)

State clearly:

- id plus path is the identity.
- Path can change, id stays.

5.2 Human index

Path:

- `docs/INDEX.md`

Content:

- Sections grouped by category_label.
- Within each category:
  - List entries with:
    - Title.
    - Link to path.
    - Optional short description or tags.
- Order:
  - Choose either:
    - Alphabetical by title.
    - Or descending by last_updated.
  - State the rule and keep it consistent.

5.3 Index update rules

Whenever the skill creates, moves, or significantly edits a doc:

- Update or insert associated entry in `docs/index.yaml`.
- Regenerate or patch `docs/INDEX.md` from `docs/index.yaml`, not the other way around.
- Ensure:
  - No stale entries.
  - No missing entries for managed docs.

5.4 Query patterns for other tools

Document how other agents or tools should use the index:

- To find docs for a category:
  - Filter index entries by category_label.
- To find docs for a component:
  - Filter by component_slug.
- To find the primary doc for a topic:
  - Use tags and doc_type to find the top candidate.
  - Example:
    - The main architecture overview for a given service.

---

### 6. Enforcement rules (strict advisory)

6.1 Normal behavior

Describe default expectation:

- Docs creation or movement should go through this skill.
- The skill returns:
  - Recommended path and filename.
  - Warnings as needed.

6.2 Handling non standard operations

When a caller wants to use a different path:

- If allow_nonstandard_docs is false:
  - The skill must:
    - Emit a clear warning that this is non standard.
    - Return both:
      - The recommended location.
      - The requested non standard path.
- If allow_nonstandard_docs is true:
  - Treat this as deliberate override.

For both cases:

- The index should still be updated.
- Entry should set nonstandard_location true when the chosen path does not match the recommended placement.

6.3 Framework docs guardrail

State explicitly:

- `_localsetup/docs/` remains the home of framework docs.
- This skill must not redefine where framework docs live.
- It can still:
  - Use the same metadata pattern.
  - Help with subfolder organization.
  - But must not conflict with `DOCUMENT_LIFECYCLE_MANAGEMENT.md` and related framework docs.

---

### 7. Integration with other Localsetup skills

7.1 Script and docs quality

Reference:

- `localsetup-script-and-docs-quality`

Rules:

- All markdown and file handling behaviors follow that skill.
- This includes:
  - Encoding and formatting rules.
  - File creation discipline.
  - Handling external input.

7.2 Humanizer

Reference:

- `localsetup-humanizer`

Rules:

- For substantial new docs or big rewrites:
  - Recommend or require a pass through the humanizer before finalization.
- Provide a hook in the behavior description:
  - Callers can:
    - Generate content.
    - Run it through humanizer.
    - Then save it via the docs organization index update path.

---

### 8. Rules and context wiring

8.1 Cursor rules

Define a new rule file under `.cursor/rules`, for example `docs-organization.mdc`:

- Describe that:
  - When user instructions involve:
    - Creating documentation.
    - Adding runbooks.
    - Updating docs for a feature or component.
  - Agents should:
    - Invoke `localsetup-docs-organization` first to get:
      - Path.
      - Filename.
      - Index updates.
- Note strict advisory semantics:
  - Nonstandard placements are allowed only with explicit override.
  - These must be marked in the index.

8.2 Other platform contexts

For each supported agent host:

- Add a short rule or pointer:
  - This skill is the default docs router.
  - Mirror the same triggers you defined for Cursor.

8.3 Framework docs index

If there is a framework level docs index:

- Add a short entry describing this skill:
  - What it does.
  - Where it lives.
  - Where its rules are documented.

---

### 9. Configuration and extensibility

9.1 Optional config file

Define file:

- `docs.config.yaml` at repo root.

Describe fields:

- root
  - Docs root path, default `docs/`.
- categories
  - Map from category_label to:
    - slug.
    - short description.
- aliases
  - Map from alternate labels to canonical labels.
- required_front_matter_fields
  - Repo specific extra metadata.

Behavior:

- Skill must work without this config.
- When config exists:
  - It takes precedence over heuristics.
  - New labels can still be added and recorded.

9.2 Future extensions

Examples you can mention but do not need to implement now:

- Rules for when to split large docs.
- Automatic cross linking between related docs using tags and component_slug.
- Audits to:
  - Find nonstandard_location entries.
  - Suggest reorganizations.

---

### 10. Testing and validation plan

10.1 New repo scenario

- Start with:
  - No `docs/` directory.
- Actions:
  - Create:
    - One architecture doc.
    - One runbook.
    - One how to.
- Verify:
  - `docs/` appears with reasonable subfolders.
  - `docs/index.yaml` and `docs/INDEX.md` exist.
  - Entries match expectations for category, component, and tags.

10.2 Messy existing repo scenario

- In a repo with ad hoc docs:
  - Add a new doc for a topic that already has partial coverage.
- Verify:
  - Skill proposes updating an existing doc where it makes sense.
  - New folders are not created that mirror existing ones.

10.3 Move and rename scenario

- Move a doc from one folder to another through this behavior.
- Verify:
  - File path changes.
  - id stays the same.
  - Index entries are updated.

10.4 Override scenario

- Intentionally create a doc in a non recommended location with allow_nonstandard_docs true.
- Verify:
  - Warning is present.
  - Index marks nonstandard_location true.

---

### 11. Implementation order of operations

1. Write `_localsetup/skills/localsetup-docs-organization/SKILL.md`
   - Include sections:
     - Purpose.
     - Inputs.
     - Outputs.
     - Behavior details for classification, placement, and index handling.
     - Integration with script and docs quality and humanizer.
2. Add `.cursor/rules/docs-organization.mdc`
   - Document:
     - When to call the skill.
     - Strict advisory behavior.
     - Expectations around index updates.
3. Create placeholder index and manifest files, if you want visible anchors:
   - `docs/INDEX.md`
   - `docs/index.yaml`
   - `docs/.docs-classifications.yaml`
4. Optionally add `docs.config.yaml`
   - Start minimal, with:
     - root: `docs/`
     - empty or small categories map.
5. Run through test scenarios by hand in one repo
   - Use the skill description as a checklist for agent and human behavior.
   - Adjust SKILL.md text until the flow feels natural and does not fight real work.

