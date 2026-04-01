# Localsetup framework contribution (sidecar)

**Purpose:** This document describes the compressed tarball `localsetup-framework-contribution.tar.xz` and how the upstream/master Localsetup repo maintainer can merge it. Delivery is tarball + this sidecar; no push or PR from this repo. Merge is manual copy.

---

## What this is

A snapshot of the **Localsetup v2 framework** tree (`_localsetup/`) as used in this devops repo. It is for import into the **upstream** Localsetup repository so that new tools, skills, and docs can be merged there.

**Upstream = the GitHub copy of the framework (master).** No earlier contribution package from this devops repo was ever shipped to upstream. Development and bug fixes have been done in place here; this package is the one to deploy into upstream so the GitHub repo has the same framework state.

**Repo-specific context is not included** (e.g. `.cursor/rules/operator-memory.mdc`, project-only rules). Only the framework tree under `_localsetup/` is in the tarball.

---

## Contents of the tarball

- **Path inside the archive:** One top-level directory `_localsetup/`.
- **Compression:** xz, max compression (`XZ_OPT=-9e`).
- **Extract:** `tar -xJf localsetup-framework-contribution.tar.xz` (creates or overwrites `_localsetup/` in the current directory).

Included: `docs/`, `lib/`, `skills/`, `tools/`, `templates/`, `tests/`, `discovery/`, and other framework dirs. Excluded when building: `.localsetup-meta/backups`, `__pycache__`, `*.pyc`, so the archive stays smaller and free of backups/cache.

---

## What was added or changed (merge guidance)

### Tooling

- **`tools/tmux_ops.py`** – Python tool for the tmux ops workflow:
  - **pick:** First available session in `ops`, `ops1`, `ops2`, … Available = session does not exist, or current line (cursor line) matches a shell prompt (line ends with `$` or `#`), or cursor is on the sudo password prompt line (`waiting_sudo`). Returns JSON: `{"session": "ops", "reason": "idle"}` or `"created"` or `"waiting_sudo"`.
  - **probe:** Sends `sudo -v && echo SUDO_READY` to the session, waits, then reads only the cursor line; returns `{"sudo": "ready"}` or `{"sudo": "password_required"}`. If pick returned `waiting_sudo`, the workflow cancels any abandoned command (C-c) before probing.
  - **send:** Sends one command string to the session (send-keys + Enter), then **sleeps 1 s** (default). Use this instead of raw `tmux send-keys` so the delay is deterministic and avoids a “pylon effect” on high-latency links. Optional `--delay SECS` or env `TMUX_OPS_SEND_DELAY`. Returns JSON: `{"session": "...", "sent": true, "delay_s": 1.0}`.
  - **Hardening (INPUT_HARDENING_STANDARD):** Session and command input sanitized (control chars stripped; session pattern `ops`/`opsN`; command max length 32 KiB). Tmux failures return structured errors with `error`, `detail`, `source`. Top-level exception handler emits JSON with `exception_type`, `exception_message`. No silent suppression; stderr gets actionable messages for agents.
- **`tools/tmux_ops`** – Shell wrapper: runs the Python tool locally, or over SSH when **REMOTE_TMUX_HOST** is set (VMs, remote, Docker). **REMOTE_TMUX_CWD** optional (default `/opt/devzone/devops`). Checks that the tool script exists before running; on SSH failure, prints a clear error to stderr.

### Skill updates

- **`skills/localsetup-tmux-shared-session-workflow/SKILL.md`** (v3.3):
  - Workflow uses **tmux_ops** for pick, probe, and **send**. Agents must use `tmux_ops send -t <session> '...'` for each step (not raw `tmux send-keys`).
  - **Idle:** Current line matches shell prompt regex; **waiting_sudo:** cursor on sudo password prompt line (session still usable; probe returns password_required, user enters password).
  - **Send:** Documented 1 s delay, optional `--delay` / `TMUX_OPS_SEND_DELAY`.
  - **Remote:** When `REMOTE_TMUX_HOST` is set, agents run `tmux_ops send` as usual; the wrapper runs the tool over SSH, so the 1 s delay is applied on the remote side.
  - Checklist and reference updated to require tmux_ops send and to avoid piling commands or using raw send-keys.

### Docs (inside _localsetup)

- **`docs/ops/tmux-ops-remote.md`** – REMOTE_TMUX_HOST, REMOTE_TMUX_CWD, usage, when not to set. If the master repo uses a different docs layout, merge this into the appropriate ops doc. Note: the skill now recommends `tmux_ops send` for remote as well; the doc’s “run tmux commands via SSH” example can be updated to “run `./_localsetup/tools/tmux_ops send -t <session> 'cmd'` as usual; the wrapper runs on the remote.”

### Templates (cursor)

- **`templates/cursor/localsetup-context.mdc`** and **`templates/cursor/localsetup-context-index.md`** – Include the full skills table (including e.g. localsetup-cron-orchestrator). Synced with `.cursor/rules/` in this repo so both sides are identical.

### Synced state

Before packaging, `.cursor/skills/` and `_localsetup/skills/` were synced so that the tmux skill (v3.3) and any other common skills are identical. Context files in `.cursor/rules/` and `_localsetup/templates/cursor/` were also made identical. The tarball’s `_localsetup/` is the single source for the framework; no `.cursor/` content is inside the archive.

---

## How to create the tarball (from devops repo root)

```bash
cd /opt/devzone/devops
tar --exclude='_localsetup/.localsetup-meta/backups' \
    --exclude='__pycache__' --exclude='*.pyc' \
    -cJf contributions/localsetup-framework-contribution.tar.xz _localsetup
```

Use a clean tree (no uncommitted changes you don’t want in the snapshot) when creating the archive.

---

## How to merge (for the master repo maintainer)

The files in this package are **modified** relative to whatever is currently in upstream. Before merging, **check the difference** between each contribution file and the corresponding file in the master repo so that only **new or changed** content is imported. Do not overwrite blindly.

---

## Checksum (optional)

After extract, verify the tree (e.g. diff against a known good tree or run the framework test suite).

---

## Contact

If anything in the tarball or this sidecar is unclear, the contributor can clarify. This package reflects the devops repo state at tarball creation time; no ongoing sync is implied.
