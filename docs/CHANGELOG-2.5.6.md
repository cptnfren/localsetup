# Changelog: v2.5.3 → v2.5.6

**Baseline:** v2.5.3 (`60c83dd`). **Current:** v2.5.6 (`8c13071`).

---

## Fixes and installer behavior

- **Deploy: EPERM on overwrite of root-owned files**  
  When deploy overwrites files that are owned by root (e.g. after a sudo install), it no longer fails with EPERM. `_safe_copy2` in deploy now falls back to copyfile-only on PermissionError, then optionally copystat with suppressed errors and a single metadata warning. Content is still updated.

- **Install and docs**  
  Install script and README/QUICKSTART/MULTI_PLATFORM_INSTALL clarify that `sudo curl | bash` only elevates curl; for a full install as root (and to avoid root-owned deployed files), a two-step flow is recommended. MULTI_PLATFORM_INSTALL and FEATURES document deploy’s behavior when overwriting root-owned files (content updated, optional metadata warning).

---

## New tools

- **`_localsetup/tools/tmux_ops`** and **`tmux_ops.py`**  
  Tmux ops workflow: pick session (idle = prompt on current line), probe sudo (ready vs password_required), send command with a 1 s delay. Input hardening per framework standard; JSON output for agents. When **REMOTE_TMUX_HOST** is set, the shell wrapper runs the Python tool over SSH on the remote host so the same workflow works for VMs and remote servers.

- **`_localsetup/tools/skill_index_scrub.py`**  
  Standalone maintenance tool for `PUBLIC_SKILL_INDEX.yaml`. Audits every index entry for dead/unreachable URLs (HEAD then GET fallback), stub or placeholder descriptions (too short, "Anthropic skill: X" pattern, markdown artifacts), and schema gaps. Fetches real descriptions from upstream `SKILL.md` / `README.md` files using a parallel worker pool. Modes: dry-run audit (default, exit 1 if issues found) and `--fix` (writes fetched descriptions back in-place, updates `updated` timestamp). Emits GFM report to stdout; optionally saves to `--report FILE`. Key flags: `--workers N`, `--timeout S`, `--skip-url-check` (description-only, faster), `--skip-desc-fetch` (URL-check-only), `--name SUBSTR` (single-skill filter), `--index FILE` (alternate index path for testing). Fully hardened per INPUT_HARDENING_STANDARD.

- **`_localsetup/tools/tmux_terminal_mode`** and **`tmux_terminal_mode.py`**  
  Toggleable framework feature for tmux-default terminal mode. Three sub-commands: `enable` applies the chosen Layer 1 variant (IDE terminal profile via `--mode ide`, or shell RC auto-attach via `--mode shell`) plus the mandatory agent ops rule (Layer 2); `disable` removes both layers and restores backups; `status` reports all four layers regardless of mode. Flags: `--mode {ide,shell}`, `--session NAME`, `--settings-file`, `--shell-rc`, `--rules-file`, `--dry-run`. IDE mode auto-detects Cursor Remote SSH, VS Code Remote SSH, Cursor Desktop, and VS Code Desktop settings paths in priority order. Shell mode auto-selects `~/.bash_profile` on macOS, `~/.bashrc` on Linux. All file writes atomic (write `.tmp`, rename). Backups created before any modification; `disable` restores from backup or strips sentinel block. Idempotent: running enable twice is safe. All AC verified by automated smoke tests.

---

## New and updated skills

- **localsetup-cloudflare-dns** (new, v1.0)  
  Manage Cloudflare DNS records (list, create, modify, delete) and run zone surveys via the `flarectl` CLI and a Python wrapper (`cf_dns.py`). Supports scheduling automated DNS snapshots. Implemented Python-first per framework tooling policy; all PRD behaviors replicated from the original Bash spec.

- **localsetup-npm-management** (new, v1.0)  
  Manage Nginx Proxy Manager proxy hosts (create, modify, enable/disable, delete, diagnose, backup/restore) via a native Python client (`npm_api.py`) that talks directly to the NPM REST API using only Python standard library (`urllib`, `json`, `configparser`). Replaces the upstream `npm-api.sh` Bash/curl/jq dependency entirely. Includes token management with caching, input hardening, and GFM output. Full `unittest` suite in `test_npm_api.py`.

- **localsetup-skill-discovery** (v1.3 → v1.4)  
  Added mandatory post-refresh scrub sequence. After every index refresh, the scrub step now runs as part of the workflow rather than being an optional note: refresh → dry-run scrub → apply fixes. Step 1 of the agent workflow updated so "yes, refresh" triggers the full three-step sequence. New "Post-refresh scrub (mandatory)" section documents the command sequence, when to use full URL checking vs `--skip-url-check`, and the "refresh and scrub" shorthand trigger.

- **localsetup-tmux-shared-session-workflow** (v1.3 → v3.3)  
  Reworked around the **tmux_ops** tool: agents use `tmux_ops pick`, `tmux_ops probe -t <session>`, and `tmux_ops send -t <session> '...'` for every step instead of raw `tmux send-keys`. Documents the 1 s send delay, optional `--delay` / `TMUX_OPS_SEND_DELAY`, and remote usage with REMOTE_TMUX_HOST.

- **localsetup-system-info** (new)  
  Quick system diagnostics: CPU, memory, disk, uptime. Use when capturing a server baseline or recording host layout and specs for later operations.

- **localsetup-cron-orchestrator** (new)  
  Manage cron from a repo-local manifest: time triggers, on-boot-with-delay, sequenced tasks; create, remove, reorder, and install.

---

## New documentation

- **`_localsetup/docs/ops/tmux-ops-remote.md`**  
  How to use the tmux_ops workflow when the tmux server runs on another host: REMOTE_TMUX_HOST, REMOTE_TMUX_CWD, usage, and when not to set them. References the skill and the tool.

- **`_localsetup/docs/TMUX_TERMINAL_MODE.md`**  
  User-facing reference for tmux-default terminal mode: modes (ide vs shell), quick start, flags, what each layer does, macOS note on `~/.bash_profile`, session name change workflow, manual rollback steps, and Layer 3 (tmux_ops) reference.

---

## Documentation updates

- **SKILLS.md** and **facts.json** regenerated (39 shipped skills; localsetup-cloudflare-dns and localsetup-npm-management added; localsetup-skill-discovery version bumped to 1.4).
- **FEATURES.md:** tmux_ops and REMOTE_TMUX_HOST in human-in-the-loop and shipped skills; new skill table entries for system-info and cron-orchestrator; deploy/root-owned overwrite behavior. New "Tmux-default terminal mode" feature row added.
- **WORKFLOW_REGISTRY.md:** Tmux shared-session row and Tmux/sudo bullet updated for tmux_ops (pick, probe, send), 1 s delay, and link to ops doc. New "Public skill index maintenance" workflow row and usage bullet added. New "Tmux-default terminal mode" workflow row and usage bullet added.
- **AGENTIC_DESIGN_INDEX.md:** New entry for `ops/tmux-ops-remote.md`; tmux quick reference updated for tmux_ops and remote. New "Audit and scrub the public skill index" quick reference added. New entry for `TMUX_TERMINAL_MODE.md`; "Tmux-default terminal mode" quick reference added.
- **SKILL_DISCOVERY.md:** Refresh section expanded to include mandatory three-step command sequence (refresh → scrub dry-run → scrub fix) with inline flags and when to use full URL checking.
- **docs/README.md:** Tmux ops (remote) added to Core workflow docs.
- **_localsetup/README.md:** Tmux skill row and tools table updated (tmux_ops, REMOTE_TMUX_HOST). `skill_index_scrub.py` and `tmux_terminal_mode` / `tmux_terminal_mode.py` added to tools tree and tools table.
- **FEATURES.md:** Skill discovery row updated to mention mandatory post-refresh scrub. New "Public skill index maintenance" workflow row added.
- **Root README.md:** Shipped skills and human-in-the-loop bullets updated; tmux skill bullet updated for tmux_ops and REMOTE_TMUX_HOST.
- **Platform registration:** localsetup-system-info, localsetup-cron-orchestrator, localsetup-cloudflare-dns, and localsetup-npm-management added to localsetup-context/SKILL.md and to all platform templates (Cursor, Claude Code, Codex, OpenClaw).
- **PUBLIC_SKILL_INDEX.yaml:** All 93 stub/placeholder descriptions enriched with real descriptions fetched from upstream SKILL.md/README.md files. `updated` timestamp refreshed.

---

## Contributions

- **contributions/**  
  Added contribution sidecar (LOCALSETUP-CONTRIBUTION.md and localsetup-framework-contribution.tar.xz) describing the production contribution that was merged and how to reproduce or merge similar packages.

---

## Dependency refactor and upgrade gap handling

- **`requirements.txt`**  
  Added `requests>=2.28` and `python-frontmatter>=1.1` with rationale comments alongside the existing `PyYAML>=6.0`. These are now the three approved framework Python libraries.

- **`_localsetup/lib/deps.py`** (new)  
  Shared dependency helper for all framework Python tools. Provides `require_deps(names)` (live `importlib` check, exits with code 2 and actionable stderr on failure) and `check_deps(names)` (returns missing list, no exit). Always performs a live check; never reads the `.deps-missing` sentinel file so a stale sentinel from an older install cannot block tools.

- **`install` and `install.ps1`**  
  Extended preflight to check `requests` and `frontmatter` modules alongside `yaml`. Added `--install-deps` (Bash) / `-InstallDeps` (PowerShell) flag: when set, runs `pip install` on any missing packages after deploy and clears the sentinel. Without the flag, install completes, writes `.deps-missing` as a notice-only file listing missing package names, and prints actionable instructions. When all packages are present, any stale `.deps-missing` is cleared automatically.

- **Upgrade path from v2.5.2**  
  `lib/deps.py` is new so it is always added cleanly. All refactored tools are framework-managed files clients have not modified, so they are overwritten by `apply_upgrade()` under the default `preserve` policy. A timestamped backup of the prior state is written before any change. Tools use live import checks, so a leftover `.deps-missing` sentinel from an older install has no effect.

- **`TOOLING_POLICY.md`**  
  New "Approved libraries (mandatory use)" section: table of all three approved libraries with import names and use cases; prohibition on reimplementing what they cover; `require_deps()` usage pattern; explicit instruction for AI agents to use approved libraries instead of generating custom implementations.

- **Documentation updates**  
  `MULTI_PLATFORM_INSTALL.md`: dependency table extended with requests and frontmatter rows; `--install-deps` flag documented with copy-paste examples. `QUICKSTART.md`: prerequisites updated; troubleshooting section updated to mention `--install-deps` re-run. `_localsetup/README.md` and root `README.md`: requirements lines updated to list all three packages and the `--install-deps` flag.

---

## Summary

| Area        | Change |
|------------|--------|
| Fixes      | Deploy no longer fails with EPERM when overwriting root-owned files; install/docs clarify sudo and root-owned deploy behavior. |
| Tools      | New tmux_ops + tmux_ops.py (pick/probe/send, REMOTE_TMUX_HOST). New skill_index_scrub.py (URL liveness, stub detection, upstream description fetch, --fix mode). New tmux_terminal_mode + tmux_terminal_mode.py (enable/disable/status, ide/shell mode, agent rule injection, atomic writes, backup/restore). New lib/deps.py (live dependency check helper, require_deps/check_deps). |
| Install    | --install-deps / -InstallDeps flag for automatic pip install; preflight extended to check requests and python-frontmatter; .deps-missing sentinel is notice-only, never read by tools. |
| Skills     | Tmux workflow v3.3; new system-info and cron-orchestrator; new cloudflare-dns and npm-management; skill-discovery v1.4 (mandatory post-refresh scrub). |
| Deps       | requirements.txt now includes requests>=2.28 and python-frontmatter>=1.1. TOOLING_POLICY.md mandates use of approved libraries. Upgrade path from v2.5.2 is gap-free. |
| Docs       | New ops/tmux-ops-remote.md and TMUX_TERMINAL_MODE.md; post-refresh scrub sequence added to skill-discovery skill and docs; WORKFLOW_REGISTRY.md and AGENTIC_DESIGN_INDEX.md updated for index maintenance and tmux-default terminal mode workflows; PUBLIC_SKILL_INDEX.yaml enriched. TOOLING_POLICY.md: approved libraries section. MULTI_PLATFORM_INSTALL.md, QUICKSTART.md, READMEs updated for new deps and --install-deps flag. |
| Shipped    | 39 skills (was 35 at 2.5.3). |
