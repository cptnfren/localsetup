---
name: localsetup-tmux-shared-session-workflow
description: Server/ops in tmux; use tmux_ops tool to pick session (idle = prompt on current line) and probe sudo; run commands only in chosen session. Supports REMOTE_TMUX_HOST for VMs/remote/Docker.
metadata:
  version: "3.3"
---

# tmux shared session workflow (ops)

**Rule:** Any request that involves running commands on the host uses this workflow. Sudo is always assumed required. Use the **tmux_ops** tool to pick session and probe; do not infer busy from `tmux ls` or parse raw capture yourself.

## Tool (use this)

- **Entrypoint:** From repo root run `./_localsetup/tools/tmux_ops` (or set `REMOTE_TMUX_HOST` to run the same tool on a remote host via SSH; see Remote below).
- **Pick session:** `./_localsetup/tools/tmux_ops pick` → JSON e.g. `{"session": "ops", "reason": "idle"}` or `{"reason": "created"}` or `{"reason": "waiting_sudo"}`. Use that `session` for the whole run. `waiting_sudo` = cursor is on the sudo password prompt line; we reuse that session (probe will return password_required, user enters password there).
- **Probe sudo:** `./_localsetup/tools/tmux_ops probe -t <session>` → JSON `{"sudo": "ready"}` or `{"sudo": "password_required"}`. The tool looks only at the **cursor line**: if the cursor is on the line showing the sudo password prompt, that is the stop signal (password_required). If ready, keep rolling; if password_required, stop and ask the user to enter password in that pane and reply "sudo ready".
- **Send command (use this for every step):** `./_localsetup/tools/tmux_ops send -t <session> '...'` sends the command to the pane and then **waits 1 s** inside the tool. Use this instead of raw `tmux send-keys` so the delay is deterministic and avoids a "pylon effect" (commands racing ahead of output on high-latency links, e.g. 300–400 ms to a server). Optional: `--delay SECS` or env `TMUX_OPS_SEND_DELAY`.
- **Idle definition:** The tool treats a session as free when the **current line** (cursor line) in the pane matches a shell prompt (line ends with `$` or `#`). It does not use "(attached)" or list-clients.

## Sequence (follow exactly)

1. **Pick session.** Run `./_localsetup/tools/tmux_ops pick`. Parse JSON; use the returned `session` for the whole run. If the tool errors, report and stop.

2. **Show attach command immediately.** Right after pick (whether the session was created or already existed), display the join command in a **copy-paste code block** so the user can attach at any time. Do not wait for the user to confirm they joined.
   - Put this in a fenced code block (e.g. ` ```bash ` … ` ``` `):
     `tmux new-session -A -s <session>`
   - Optionally one line: "Join this session to watch or enter sudo if prompted."
   - **If pick returned `reason: "waiting_sudo"`:** the session may be abandoned with something like `sudo apt upgrade` waiting for the password. Cancel it so nothing runs after the user types the password: send `tmux send-keys -t <session> C-c` (Ctrl+C), wait ~1 s, then run the probe. That way only our trigger runs after they enter the password.
   - Then run the probe: `./_localsetup/tools/tmux_ops probe -t <session>` (or after the cancel, when reason was waiting_sudo).

3. **Gate on probe only.** If the probe returns `"sudo": "password_required"` (cursor is on the line showing the sudo password prompt): stop. Do not send any further commands. Ask the user to attach to the session, enter the password in that pane, and reply "sudo ready". Only after they reply may you send the first command. If the probe returns `"sudo": "ready"`, continue to step 4. You do not wait for the user to confirm join before probing; the only stop is the password prompt on the cursor line.

4. **Do not pile commands.** Send one logical step at a time (e.g. one block that sets LOG and runs one hardening step). Use **tmux_ops send** for each step so the built-in 1 s delay runs between sends. After sending, wait (e.g. 5 s), then read the log or capture the pane to confirm the step finished. Only then send the next step. Do not send multiple independent commands in one send.

5. **Run.** Commands go via `./_localsetup/tools/tmux_ops send -t <session> '...'` (tool adds Enter and 1 s delay). Use a log: `/tmp/agent-<session>-YYYYmmdd-HHMMSS.log` (e.g. `|& tee -a $LOG`). Read the log yourself. Never run those commands in the agent shell.

6. **Re-gate if sudo expires.** If a later command fails (e.g. sudo timeout), run the probe again; if password_required, stop and ask for "sudo ready"; only then continue.

## Remote (VMs, remote SSH, Docker)

When the tmux server runs on a different host (e.g. Cursor on laptop, tmux on VM or remote server):

- Set **REMOTE_TMUX_HOST** to that host (e.g. `export REMOTE_TMUX_HOST=sh0t`). Optionally **REMOTE_TMUX_CWD** to the repo path on the remote (default `/opt/devzone/devops`).
- Run `./_localsetup/tools/tmux_ops pick` and `probe -t <session>` as usual; the wrapper runs the tool over SSH and returns the same JSON.
- **Sending commands:** When REMOTE_TMUX_HOST is set, run `./_localsetup/tools/tmux_ops send -t <session> 'cmd'` as usual; the wrapper runs the tool over SSH, so the 1 s delay is applied on the remote side. Use the same session and log path on the remote (e.g. `/tmp/agent-ops-*.log`). If the agent runs on the same host as tmux (e.g. Cursor Remote SSH), do not set REMOTE_TMUX_HOST.

## Checklist

| Step | Do | Do not |
|------|-----|--------|
| 1 | Run tmux_ops pick; use returned session for whole run. | Infer session from tmux ls or "(attached)". |
| 2 | Right after pick, show attach in code block. If reason was waiting_sudo, send C-c to session first (cancel abandoned command), then run probe. Do not wait for user to join. | Wait for "I joined"; skip cancel when waiting_sudo. |
| 3 | If probe says password_required (cursor on sudo prompt line), stop and ask user; only then send commands. If ready, continue. | Send commands before user says sudo ready when probe said password_required. |
| 4 | One step per send via tmux_ops send; wait and verify (log/capture) before next. | Pile multiple commands in one send; use raw tmux send-keys. |
| 5 | Run in chosen session via tmux_ops send; tee to log; read log. | Run in agent shell; skip log. |
| 6 | If sudo expired, probe again; if password_required, stop. | Assume sudo still valid. |

## Session and log

- Session: the one returned by `tmux_ops pick` (e.g. `ops` or `ops1`).
- Log: `/tmp/agent-<session>-YYYYmmdd-HHMMSS.log`. Commands: `... |& tee -a $LOG`. After run: read log (e.g. `tail -n 200` that file).

## Hard rules

1. Server/ops commands run only in tmux. Use tmux_ops to pick session (idle = prompt on current line) and probe; never in the agent shell for the actual ops commands.
2. If probe returns ready, continue immediately; do not stop for a chat "sudo ready". Only stop when probe returns password_required.
3. If password_required: ask user to enter password in the ops pane and reply "sudo ready"; then proceed.
4. Right after pick, display the attach command in a copy-paste code block; do not wait for user to confirm join before probing.
5. Capture output to the log path; the agent reads the log. State what you are about to do before running commands.

## Reference

- Tool: `_localsetup/tools/tmux_ops` (pick, probe -t SESSION, send -t SESSION 'cmd'). Send enforces 1 s delay after each command. Remote: REMOTE_TMUX_HOST, REMOTE_TMUX_CWD.
- Attach: `tmux new-session -A -s <name>`. Session names: `ops`, `ops1`, `ops2`, … Windows (optional): `sys`, `deploy`, `logs`.
