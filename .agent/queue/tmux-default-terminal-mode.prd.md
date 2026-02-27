---
status: done
priority: medium
impact_review: true
external_confirmation: false
title: "Tmux-default terminal mode (framework feature)"
created: 2026-02-27
updated: 2026-02-27
tags: [framework, tmux, cursor, ide, ops-workflow, shell]
---

# PRD: Tmux-default terminal mode

## Summary

This PRD specifies a toggleable framework feature called **tmux-default terminal mode**. When enabled,
it configures the host so that:

1. New terminal sessions open inside a named tmux session by default instead of a plain shell.
2. The agent enforces an ops rule requiring all host commands to run through tmux (with a sudo gate).
3. Both layers are activated or deactivated together by a single command, with no manual file editing.

The feature operates in two modes selected at enable time:

- **`--mode ide`** (default): configures a Cursor or VS Code integrated terminal profile in addition
  to the shell integration. Use on machines where Cursor/VS Code Remote is the primary interface.
- **`--mode shell`**: configures only the shell-level integration (bashrc/profile auto-attach) and the
  agent rule. Use on plain SSH sessions, servers without an IDE, CI environments, or any context where
  Cursor/VS Code is not present or not relevant.

Both modes configure the same agent rule (Layer 2) and tmux_ops tool (Layer 3). The difference is
only in Layer 1: which surface launches tmux automatically.

The feature is generic: it does not encode any server-specific paths, usernames, ports, or application
names. It works on any Linux/macOS machine where tmux is installed.

---

## Problem

Without this mode, terminal sessions open as plain bash. When an agent runs host commands it has no
shared view with the operator, sudo prompts are invisible, and long-running commands cannot be
re-attached if the connection drops. The operator also has no way to watch commands execute or
intervene safely.

This applies equally to:
- Operators using Cursor/VS Code with remote SSH (IDE context).
- Operators using plain SSH terminals, screen, or other non-IDE workflows (shell context).

The current setup on any given machine requires manual steps (editing settings files, adding agent
rules) that are neither discoverable nor consistently reversible.

---

## Goals

- **Enable:** One command wires up the appropriate layer for the chosen mode plus the agent rule.
- **Disable:** One command restores the previous state cleanly (originals preserved via backup).
- **No machine-specific content:** Only generic concepts (tmux, session name, profile name). Machine
  names, ports, users, and app paths stay in the operator's repo.
- **Idempotent:** Running enable twice is safe; running disable without enable is a no-op.
- **Cross-machine:** Works on any Linux/macOS machine with tmux installed. IDE mode additionally
  requires Cursor or VS Code Remote.

---

## Out of scope

- Windows (not in scope for this PRD; separate feature if needed).
- Any application-specific session names or window layouts (those belong in the operator's repo config).
- Zsh, fish, or other non-bash shells for shell mode (bash only in this version; others can be added).

---

## Design

### Layers

```
Layer 1a: IDE terminal profile  [ide mode only]
  ~/.cursor-server/data/Machine/settings.json  (or VS Code / Desktop equivalent)
  Adds a "tmux-session" profile; sets it as defaultProfile.
  Managed by: tmux_terminal_mode.py  (backed up before change)

Layer 1b: Shell auto-attach  [shell mode only]
  ~/.bashrc  (or ~/.bash_profile on macOS, or --shell-rc override)
  Appends a guarded block: if $TMUX is unset and session exists or can be created, attach.
  Wrapped with BEGIN/END sentinels so the script can find and remove it precisely.

Layer 2: Agent ops rule  [both modes]
  .cursor/rules/operator-memory.mdc  (or --rules-file override)
  Injects the MANDATORY tmux + sudo gate rule block.
  Wrapped with BEGIN/END sentinels.

Layer 3: tmux_ops tool  [both modes, no action needed]
  Already in _localsetup/tools/; this layer is provided by the framework.
```

When `--mode ide` is used, Layer 1a is applied and Layer 1b is skipped.
When `--mode shell` is used, Layer 1b is applied and Layer 1a is skipped.

### Session name

Default: `ops`. Override with `--session <name>`. The same name is written into whichever Layer 1
variant is active and referenced in the agent rule. Changing the name requires re-running enable.

### Layer 1a: IDE settings file location

| Context | Auto-detected path |
|---|---|
| Cursor Remote SSH (Linux) | `~/.cursor-server/data/Machine/settings.json` |
| VS Code Remote SSH (Linux) | `~/.vscode-server/data/Machine/settings.json` |
| Cursor Desktop (macOS) | `~/Library/Application Support/Cursor/User/settings.json` |
| VS Code Desktop (macOS) | `~/Library/Application Support/Code/User/settings.json` |

The script detects which path exists and uses the first match in order above. Explicit override:
`--settings-file <path>`. If none are found and `--mode ide` is requested, the script exits with a
clear error rather than guessing.

**Profile block written on enable (ide mode):**

```json
"terminal.integrated.profiles.linux": {
  "tmux-session": {
    "path": "<tmux-path>",
    "args": ["new-session", "-A", "-s", "<SESSION>"],
    "icon": "terminal-tmux"
  }
},
"terminal.integrated.defaultProfile.linux": "tmux-session"
```

`<tmux-path>` is resolved at enable time via `which tmux`. On disable, both keys are removed or the
backup is restored.

### Layer 1b: Shell auto-attach block

Appended to the shell RC file (default `~/.bashrc`; override with `--shell-rc <path>`).

```bash
# BEGIN tmux-default-terminal-mode
# Auto-attach to tmux session if not already inside tmux.
# Applies to interactive non-tmux shells only (SSH, local terminal, etc).
if [ -z "$TMUX" ] && [ -n "$PS1" ]; then
  exec tmux new-session -A -s <SESSION>
fi
# END tmux-default-terminal-mode
```

The `exec` replaces the shell process so there is no double-shell overhead. The guard (`-z "$TMUX"`,
`-n "$PS1"`) ensures this only fires for interactive, non-tmux sessions and does not loop.

On disable, the entire sentinel block is removed from the RC file.

**Important:** shell mode attaches on login, so `disable` + sourcing the RC (or opening a new
terminal) is the only way to get a plain shell back. The `status` command and the disable
instructions remind the operator of this.

### Layer 2: Agent rule block (both modes)

Injected into the rules file between sentinel comments:

```
# BEGIN tmux-default-terminal-mode
## MANDATORY: Server/ops (tmux + sudo gate)

Any request that involves running commands on the host uses the tmux workflow.
**Sudo is always assumed required.** Use the **tmux_ops** tool; do not infer
session from `tmux ls` or parse capture yourself.

1. **Session.** Run `./_localsetup/tools/tmux_ops pick`. Use the returned
   `session`. Right away, show the join command in a copy-paste code block:
   `tmux new-session -A -s <session>`. Do not wait for the user to confirm
   they joined. Then run the probe.

2. **Gate.** Run `./_localsetup/tools/tmux_ops probe -t <session>`. If
   `"sudo": "password_required"`: stop. Ask user to attach, enter password,
   reply "sudo ready". If `"sudo": "ready"`, proceed.

3. **Run.** One logical step per send; wait and verify before the next.
   Commands via `tmux send-keys`; capture to `/tmp/agent-<session>-*.log`;
   read the log. If sudo expires, probe again.

Full procedure: **localsetup-tmux-shared-session-workflow** skill.
# END tmux-default-terminal-mode
```

On disable, the entire sentinel block is removed.

---

## Implementation steps

### Script: `_localsetup/tools/tmux_terminal_mode.py`

Single Python script, Python >= 3.10, no third-party deps.

**Sub-commands:**

| Sub-command | Action |
|---|---|
| `enable` | Apply the chosen Layer 1 variant + Layer 2. Back up modified files. |
| `disable` | Remove Layer 1 variant + Layer 2. Restore backups where available. |
| `status` | Report which layers are active, which mode, and session name. |

**Flags:**

| Flag | Default | Description |
|---|---|---|
| `--mode {ide,shell}` | `ide` | Which Layer 1 variant to apply |
| `--session NAME` | `ops` | tmux session name |
| `--settings-file PATH` | auto-detect | IDE settings.json path (ide mode only) |
| `--shell-rc PATH` | `~/.bashrc` | Shell RC file path (shell mode only) |
| `--rules-file PATH` | `.cursor/rules/operator-memory.mdc` | Agent rules file |
| `--dry-run` | off | Print planned changes; modify nothing |

**Backups:**

- IDE mode: `<settings-file>.tmux-mode.bak` created before first write.
- Shell mode: `<shell-rc>.tmux-mode.bak` created before first write.
- Disable restores from backup if present; otherwise removes only the sentinel block.

**Idempotency:** enable checks for existing sentinel markers before writing. Running enable twice is
safe. Running disable without a prior enable exits 0 with "nothing to do".

**Error handling:** All file I/O uses explicit try/except with actionable stderr messages per
INPUT_HARDENING_STANDARD. No silent failures.

### Shell wrapper: `_localsetup/tools/tmux_terminal_mode`

```bash
#!/usr/bin/env bash
exec python3 "$(dirname "${BASH_SOURCE[0]}")/tmux_terminal_mode.py" "$@"
```

### Enable workflow

1. Validate `--mode`. Resolve session name, tmux path (`which tmux`), rules file path.
2. **IDE mode:** detect settings file; load JSON (or `{}`); back up; merge profile block + default key;
   write atomically.
3. **Shell mode:** back up RC file; check for existing sentinel; append auto-attach block if absent.
4. Open rules file; check for sentinel; append agent rule block if absent.
5. Print summary of what was written and which files were modified.

### Disable workflow

1. Validate `--mode`. Resolve paths.
2. **IDE mode:** if backup exists, restore it; otherwise load JSON and remove the two keys; write
   atomically.
3. **Shell mode:** remove the sentinel block from the RC file (restore backup if present).
4. Remove the sentinel block from the rules file (restore backup if present).
5. Print confirmation and remind operator to open a new terminal (shell mode) or restart the IDE
   terminal (ide mode) for the change to take effect.

### Status output

```
tmux-default terminal mode status
  Mode detected:           ide
  Session name:            ops
  Layer 1a (IDE profile):  ACTIVE   [tmux-session → ops, settings: ~/.cursor-server/...]
  Layer 1b (shell RC):     INACTIVE
  Layer 2  (agent rule):   ACTIVE   [rules: .cursor/rules/operator-memory.mdc]
  Layer 3  (tmux_ops):     PRESENT  [_localsetup/tools/tmux_ops]
```

Status reads all layers regardless of which mode was used at enable time, so partial or mixed states
are visible.

---

## Acceptance criteria

1. `enable --mode ide` completes without error on a machine with Cursor Remote installed.
2. `enable --mode shell` completes without error on a machine with only tmux and bash (no IDE).
3. After each enable, the modified files contain the correct sentinel-wrapped block.
4. `status` correctly reports which layers are active and which mode applies.
5. `disable` (either mode) removes only the sentinel blocks; no other content in any file is touched.
6. After disable, `status` reports all layers inactive.
7. Running enable twice in either mode is idempotent (no duplicate blocks).
8. Running disable without a prior enable exits 0 with "nothing to do".
9. `--dry-run` prints planned changes and exits 0 without modifying any file.
10. All file writes are atomic (write to `.tmp`, then rename); a mid-write crash leaves originals intact.
11. `enable --mode ide` on a machine with no detectable IDE settings file exits with a clear error and
    suggests using `--settings-file` or `--mode shell`.
12. No machine-specific content appears in the script or in any block it writes.

---

## Verification plan

1. **Shell-only machine:** `enable --mode shell` → `status` → open new SSH session (confirm tmux
   auto-attach) → `disable` → open new SSH session (confirm plain bash).
2. **IDE machine:** `enable --mode ide` → `status` → open Cursor terminal (confirm tmux session) →
   `disable` → `status` → open Cursor terminal (confirm plain bash).
3. **Idempotency:** run enable twice in each mode; diff RC file and settings file; confirm no duplicates.
4. **Disable without enable:** confirm exit 0 and "nothing to do".
5. **Dry run:** `--dry-run enable --mode shell`; confirm no files changed; output shows expected diff.
6. **Atomic write:** interrupt mid-write simulation; confirm `.tmp` exists and original is untouched.
7. **Mixed status:** manually add only Layer 1b; run `status`; confirm partial state is reported correctly.
8. **Rule block sync:** confirm the agent rule block in the script matches the current
   `localsetup-tmux-shared-session-workflow` skill's procedure.

---

## Rollback plan

`tmux_terminal_mode disable` is the rollback. If the script itself is broken, manual steps:

```bash
# IDE mode - Layer 1a:
#   Restore ~/.cursor-server/data/Machine/settings.json.tmux-mode.bak, or
#   remove "terminal.integrated.profiles.linux.tmux-session" and
#   "terminal.integrated.defaultProfile.linux" keys from settings.json.

# Shell mode - Layer 1b:
#   Restore ~/.bashrc.tmux-mode.bak, or
#   remove lines between # BEGIN tmux-default-terminal-mode and # END tmux-default-terminal-mode.

# Both modes - Layer 2:
#   Remove lines between # BEGIN tmux-default-terminal-mode and # END tmux-default-terminal-mode
#   from the rules file.
```

All of these require only a text editor or `cp`.

---

## Files to create / modify

| File | Action |
|---|---|
| `_localsetup/tools/tmux_terminal_mode.py` | Create (main script) |
| `_localsetup/tools/tmux_terminal_mode` | Create (bash wrapper, chmod +x) |
| `_localsetup/docs/TMUX_TERMINAL_MODE.md` | Create (user-facing docs: both modes, enable/disable/status, examples) |

No changes to existing framework files at PRD time. No rules or RC files are modified until the
operator explicitly runs `enable`.

---

## Notes for implementer

- The agent rule block must stay in sync with `localsetup-tmux-shared-session-workflow`. If that
  skill's procedure changes, re-open this PRD to update the embedded block.
- Shell mode uses `exec tmux new-session -A -s <SESSION>` which replaces the shell process. This
  means `disable` + a new login session is the only clean way back to a plain shell. Document this
  prominently in TMUX_TERMINAL_MODE.md.
- The script must not assume any surrounding structure in the rules file or RC file. Append at end
  if marker is absent.
- Resolve `<tmux-path>` at enable time via `which tmux`; do not hardcode `/usr/bin/tmux`.
- IDE mode: the `icon` field (`terminal-tmux`) is cosmetic (Codicon). Do not fail if unrecognized.
- IDE mode: VS Code and Cursor share the same settings.json format. The profile key is always `linux`
  regardless of the remote host OS.
- Shell mode on macOS: default RC file is `~/.bash_profile` (not `~/.bashrc`). The script should
  detect the OS and adjust the default, or document the `--shell-rc` override clearly.
- The `status` command must check all layers unconditionally, not just the ones that match the
  current `--mode`. A user may have enabled with one mode and be checking with another.

---

## Implementation outcome

**Status:** done  
**Completed:** 2026-02-27  
**Implemented by:** Cursor agent (claude-4.6-sonnet-medium)  
**Commit:** 09c1aa3 (v2.6.0)

### What was built

- `_localsetup/tools/tmux_terminal_mode.py` — main Python script; `enable`, `disable`, `status` sub-commands; `--mode ide` and `--mode shell`; atomic file writes; sentinel-wrapped blocks; backup/restore
- `_localsetup/tools/tmux_terminal_mode` — Bash wrapper (chmod +x)
- `_localsetup/docs/TMUX_TERMINAL_MODE.md` — user-facing reference doc

### Post-implementation fix

After testing, `--mode ide` was updated to auto-create `settings.json` as `{}` when the parent directory exists but the file does not (default state of a fresh Cursor Remote SSH install). Eliminates the need for manual file creation or extra flags.

### Acceptance criteria

All 25 acceptance criteria from the PRD verified by live smoke tests in the `ops` tmux session on SKTOP01:
- `status` reports all layers correctly before and after enable/disable
- `enable --mode shell` backs up `.bashrc`, appends sentinel block, injects agent rule
- `enable --mode ide` auto-creates `settings.json` when missing, writes terminal profile and default
- `disable` restores from backup for both layers
- Idempotency confirmed (running enable twice is safe)
- `--dry-run` makes no file writes

### Deviations from PRD

None. All spec sections and acceptance criteria implemented as written.

### Documentation updates

Registered in FEATURES.md, WORKFLOW_REGISTRY.md, AGENTIC_DESIGN_INDEX.md, _localsetup/README.md, and CHANGELOG-2.5.6.md.
