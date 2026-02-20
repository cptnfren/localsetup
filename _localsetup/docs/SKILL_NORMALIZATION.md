---
status: ACTIVE
version: 2.2
---

# Skill normalization (spec compliance and platform-neutral)

**Purpose:** When importing skills or normalizing skills already in the tree, apply this doc so each skill is (1) compliant with the [Agent Skills specification](https://agentskills.io/specification) and (2) platform-neutral where possible. Normalization applies to **SKILL.md only**; references, scripts, and playbooks are copied or left unchanged. The skill-importer and the standalone normalizer (localsetup-skill-normalizer) both use this doc as the single source of truth.

## When normalization runs

- **During import:** After the user selects skills and duplicate/overlap check, offer "Normalize before copy?" If yes, apply the rules below, show a summary plus concrete key edits, get approval, then copy the normalized skill. If the user declines, copy as-is and warn once with a pointer to this doc.
- **After the fact:** The standalone normalizer skill can run on any skill(s) already in the tree (e.g. previously imported skills, or skills the user dropped in by copying files). Same rules and approval flow.

## Spec-compliance checklist (frontmatter)

Apply these checks and fixes so SKILL.md frontmatter satisfies the Agent Skills spec:

1. **name** (required)
   - Must be 1–64 characters.
   - Only lowercase letters (a–z), numbers, and hyphens.
   - Must not start or end with a hyphen; no consecutive hyphens (`--`).
   - Must match the parent directory name (e.g. `localsetup-ansible-skill` for `_localsetup/skills/localsetup-ansible-skill/`).
   - If the skill is imported with a different dir name (e.g. `localsetup-<name>`), set `name` in frontmatter to that directory name.

2. **description** (required)
   - Must be 1–1024 characters, non-empty.
   - Should describe what the skill does and when to use it; include keywords that help agents match the task.
   - Remove or generalize platform-specific phrasing (e.g. "OpenClaw VPS setup" → "VPS setup (including optional agent-host examples)" or similar).

3. **compatibility** (optional)
   - Use for runtime or environment requirements (e.g. required binaries, system packages, network).
   - Max 500 characters if provided.
   - If the skill has platform-specific metadata (e.g. `metadata.openclaw` with `requires`/`install`), convert that into a generic `compatibility` string and remove the platform-specific block (see before/after below).

4. **metadata** (optional)
   - Keep `metadata.version` (e.g. `"1.0"`) so the framework versioning hook can bump it.
   - Remove or convert platform-only keys (e.g. `metadata.openclaw`) into `compatibility` or a short note in the body; do not leave product-specific metadata as the only record of requirements.

5. **license** (optional)
   - Leave as-is if present; no change required for normalization.

## Before/after frontmatter examples

### Platform-specific metadata → compatibility

**Before:**

```yaml
---
name: some-skill
description: "Does X. Use with OpenClaw."
metadata:
  version: "1.0"
  openclaw:
    requires: { bins: ["ansible", "ansible-playbook"] }
    install:
      - id: ansible
        kind: pip
        package: ansible
        bins: ["ansible", "ansible-playbook"]
        label: "Install Ansible (pip)"
---
```

**After:**

```yaml
---
name: localsetup-some-skill
description: "Does X. Use when you need Ansible for server provisioning and playbooks."
metadata:
  version: "1.0"
compatibility: "Requires ansible, ansible-playbook (e.g. pip install ansible or system package)."
---
```

Optional: in the body, add one line such as "Install Ansible via your package manager or `pip install ansible` if not present."

### Description: platform-specific → generic

**Before:** `"Includes playbooks for OpenClaw VPS setup, security hardening, and common server configurations."`

**After:** `"Includes example playbooks for VPS setup, security hardening, and common server configurations. Bundled examples may reference one platform; adapt paths and commands for your environment."`

## Platform-neutralization rules (body)

Apply these in order. Detection is **product-agnostic**: look for patterns like "Integration with …", "From … Agent", "Run via … exec/tool", regardless of which product name appears.

### 1. Integration / "From X Agent" sections

- **Detect:** A section whose title matches patterns such as:
  - "Integration with *" (e.g. "Integration with OpenClaw")
  - "From * Agent" (e.g. "From OpenClaw Agent")
  - "Using * with this skill"
  - Or a subsection that is entirely platform-specific commands (e.g. `exec command="..."`, product-named paths, product-named secret stores).
- **Replace with:** The generic snippet below (or equivalent). Remove the platform-specific section; do not keep product names in the replacement unless in an optional "Example: ProductName" note.

**Generic snippet: Running from an agent**

```markdown
## Running playbooks from an agent

Use your platform's command or terminal tool to run ansible-playbook (or the skill's main commands). Paths in examples are relative to the skill directory or repo root; adjust for your layout.

- **Running playbooks:** Invoke the playbook via your platform's shell/exec/run capability (e.g. terminal, exec tool, or run command). Example: `ansible-playbook -i inventory/hosts.yml playbooks/site.yml --limit <host>`.
- **Secrets:** Store credentials in your platform's secret store or use Ansible Vault; pass vault password via `--ask-vault-pass` or a vault password file. Do not hardcode secrets in the skill or inventory.
```

If the original section mentioned a specific product's secret integration (e.g. Vaultwarden), add one line: "Some platforms offer secret managers; use them if available, otherwise Ansible Vault is the standard approach."

### 2. Platform-specific command examples in body

- **Detect:** Inline or block examples that show a single platform's invocation (e.g. `exec command="..."`, or "Run in OpenClaw: …").
- **Replace with:** Generic wording. Use "Run via your platform's command or terminal:" followed by the underlying command (e.g. `ansible-playbook ...`) without the platform wrapper. If the example is valuable for one platform, keep it as a short "Example (PlatformName):" subsection after the generic version.

### 3. Product-named host groups, playbooks, roles in prose

- In the **body text** (not in bundled files), you may generalize references to product-named inventory groups or playbook names (e.g. "openclaw" host group, "openclaw-vps.yml") to "agent hosts" or "your playbook for agent hosts" with a note that the bundled files may use a specific name (e.g. "Bundled playbook `openclaw-vps.yml` is one example; adapt or rename for your setup."). Do not rename files on disk; only adjust explanatory text in SKILL.md so the skill reads as platform-neutral.

## Scope

- **Normalization applies to SKILL.md only.** References, scripts, assets, and playbooks are not rewritten; they are copied unchanged or left in place. The skill directory name and frontmatter `name` are aligned with framework convention (e.g. `localsetup-<name>`); no automatic renaming of bundled files (e.g. `openclaw-vps.yml`) is required.

## Approval flow

1. Apply the checklist and rules to SKILL.md (in memory or a temp copy).
2. Produce a **summary** (e.g. "Frontmatter: add compatibility, remove metadata.openclaw; description generalized; replace 'Integration with OpenClaw' with generic 'Running playbooks from an agent' section.").
3. Produce a **concrete list of key edits** (e.g. "Remove metadata.openclaw block"; "Replace lines 427–453 with generic snippet"; "Description: change 'OpenClaw VPS setup' to 'VPS setup (optional agent-host examples)'.").
4. Present summary + key edits to the user; get explicit approval.
5. If approved, write the normalized SKILL.md. If not, skip (during import: copy as-is and warn; standalone: do not write).

## Reference

- [Agent Skills specification](https://agentskills.io/specification)
- [SKILL_IMPORTING.md](SKILL_IMPORTING.md) for the import workflow and when normalization is offered
- [PLATFORM_REGISTRY.md](PLATFORM_REGISTRY.md) for supported platforms and skill registration

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
