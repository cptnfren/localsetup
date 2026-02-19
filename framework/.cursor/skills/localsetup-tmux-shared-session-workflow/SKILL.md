---
name: localsetup-tmux-shared-session-workflow
description: Run server operations inside a shared tmux session so a human can attach, observe, and provide sudo. Agent captures output via log files or tmux capture. Use when running server/system commands, deployments, or when user mentions tmux, shared session, or human-in-the-loop ops.
metadata:
  version: "1.3"
---

# tmux Shared Session Workflow (Generic, Human Visible Ops)

**Purpose:** Always run server operations inside a shared tmux session so a human can attach at any time, observe progress, and safely provide sudo when needed. The agent must read command output itself (no user copy/paste) via log files and/or tmux capture.

## Definitions

- **Base session name:** `ops`
- **Derived sessions:** `ops1`, `ops2`, `ops3`, ...
- **Idle session:** session/window/pane where the foreground command is a shell prompt (safe to type into).
- **Busy session:** pane is running a foreground process or prompt state is unknown.

## Hard Rules

1. All operational commands must run inside tmux.
2. Prefer reusing `ops` if it is idle.
3. If `ops` exists but is busy, create/use the next available `opsN`.
4. Never send keystrokes to a busy/unknown pane.
5. If a task requires sudo, stop and request a human sudo trigger (see Sudo Gate).
6. Create distinct windows for clarity: `sys`, `deploy`, `logs`.
7. The agent must capture and read outputs itself. Do not rely on the user to relay tmux output.
8. Always print "what I'm about to do" before running commands.

## Standard Session Acquisition Algorithm

1) **If not already inside tmux:**
   - Attempt attach/create `ops`: `tmux new-session -A -s ops`
2) **If `ops` exists but is busy or prompt state is unknown:**
   - Use next available name: try `ops1`, then `ops2`, etc.
   - Attach/create the first non-existent: `tmux new-session -A -s ops1`
3) **Once attached, ensure windows exist:** `sys`, `deploy`, `logs` (create if missing).

## Human Join Commands

- Attach/create base: `tmux new-session -A -s ops`
- List sessions: `tmux ls`
- Attach specific: `tmux attach -t ops1`

## Session/Window Conventions

- Window 1: `sys`  - packages, firewall, users/groups, filesystem
- Window 2: `deploy`  - git, builds, releases, switching versions
- Window 3: `logs`  - journalctl, docker logs, tail -f

Create windows if missing:

```bash
tmux new-window -t <session> -n sys
tmux new-window -t <session> -n deploy
tmux new-window -t <session> -n logs
```

## Output Awareness (Required)

The agent must be aware of command output without user transcription. Use one of these for every meaningful command batch.

### Method A (preferred): redirect to a log file the agent can read

Log filename must include the **tmux session name** so concurrent sessions stay separated.

- **Log path format:** `/tmp/agent-<session>-YYYYmmdd-HHMMSS.log`
- **Examples:** `/tmp/agent-ops-20260218-213045.log`, `/tmp/agent-ops1-20260218-213045.log`

Run with output capture:

```bash
command |& tee -a /tmp/agent-<session>-YYYYmmdd-HHMMSS.log
```

After completion, read the log to decide next steps:

```bash
tail -n 200 /tmp/agent-<session>-YYYYmmdd-HHMMSS.log
```

Rules: Use `|&` (stdout+stderr) when available. Keep logs in `/tmp` unless retention elsewhere is required. Rotate by timestamp. For multi-batch tasks, reuse the same log file for that session/task where practical.

### Method B: capture tmux pane content

When needed:

```bash
tmux capture-pane -p -S -200 -t <session>:<window>.<pane>
```

Rules: Only use on panes the agent created or can safely inspect. Use to verify final status when commands were not tee'd.

### Method C: long-running services  - system logs

- **systemd:** `journalctl -u <service> -n 200 --no-pager`; follow: `journalctl -u <service> -f`
- **Docker:** `docker logs --tail 200 <container>`; follow: `docker logs -f <container>`

## Idle vs Busy Detection (Practical Heuristic)

Policy: do not inject into an existing pane unless you can confirm it is idle.

**Safe cases:** You just created the session in this run (you own the active pane), or you can clearly see a shell prompt waiting (no running foreground process).

If uncertain, create a new session `opsN` instead.

## Sudo discovery (once at start of ops)

Before requesting sudo or running sudo-dependent commands, the agent must discover the environment:

1. **Is sudo already valid?** Run `sudo -n true 2>/dev/null`. If it succeeds, no password is needed for this run (e.g. NOPASSWD or recent auth). Proceed without prompting.
2. **What is the timeout?** Run `sudo -V 2>/dev/null` and look for "Authentication timestamp timeout" (minutes). Default on Ubuntu 24 is 15 minutes; each sudo use extends the timer, idle terminal lets it expire. Some systems use different timeouts or require sudo on every command; adjust strategy accordingly.
3. **Is sudo actually required?** Only prompt when an upcoming command genuinely needs sudo. If none do, continue without the sudo gate.

Use this to decide: skip gate (already valid or not needed), or request one human trigger and then run all sudo commands within the validity window without bothering the user again.

## Sudo Gate (Human-in-the-loop)

When a command genuinely requires sudo and `sudo -n true` failed (or was not run yet), the agent must pause and get one human-approved sudo in the shared session. After that, do not prompt again until sudo expires (re-check with `sudo -n true` before later sudo batches; if it fails, repeat the gate).

### Step 1: Tell the user where to join

Output the **exact session** the user must attach to so they run the trigger in the same pane the agent will use. Example:

"Join the tmux session where I will run commands. In your terminal, run:

```bash
tmux attach -t ops
```

(or `tmux new-session -A -s ops` if the session does not exist yet). Use the window/pane I am using for this task (e.g. `sys` or `deploy`)."

### Step 2: Output the trigger in a code block

In the same message, give the exact command for the user to run **in that attached session**:

```bash
sudo -v && echo SUDO_READY
```

The user runs it, enters their password when prompted, and sees `SUDO_READY` when successful.

### Step 3: Wait for confirmation (and optionally monitor)

- **Preferred:** Monitor the session log or tmux capture for the line `SUDO_READY` so the agent can proceed as soon as it appears.
- **Otherwise:** Wait for the user to report that they see `SUDO_READY` (e.g. "sudo ready" or "SUDO_READY").

Do not send further keys or commands until SUDO_READY is confirmed (via log or user).

### Step 4: Proceed without re-prompting

Once SUDO_READY is confirmed, the agent sends or runs all subsequent commands that need sudo in that session. Do not ask the user for sudo again for each command. The system keeps the sudo timestamp valid for the discovered timeout (e.g. 15 minutes); each command run extends it. Only if sudo later fails (e.g. timeout expired) should the agent repeat the gate: output join instructions again, the same code block, wait for SUDO_READY, then continue.

Summary: one join instruction, one code block, wait (monitor log or user), then run all sudo commands in the validity window. Re-prompt only when `sudo -n true` fails again.

## Acceptance Criteria

- Every server change is visible in tmux scrollback.
- The agent can read and reason over outputs via logs or tmux capture.
- A human can attach and see exactly what is happening.
- No commands are injected into unknown/busy panes.
- Sudo is never executed silently; always human-authorized via the sudo trigger.
