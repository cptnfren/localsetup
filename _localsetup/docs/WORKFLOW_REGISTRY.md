---
status: ACTIVE
version: 2.5
---

# Workflow and module registry (Localsetup v2)

**Purpose:** Registry of named workflows and when to use them; impact review when required.

## Core

| Name | Description | When to use | Impact review |
|------|-------------|-------------|---------------|
| Master rule / context | Always-loaded framework context | Always | No |
| Skills index | List of skills and when to use | When discovering which skill to load | No |

## Workflows

| Name | Description | When to use | Impact review |
|------|-------------|-------------|---------------|
| Decision tree | One Q per turn, 4 options A-D, preferred + rationale | User says "decision tree" or "reverse prompt" | No |
| Agent Q (queue) | Process specs in .agent/queue/; implement, status, outcome | User says "process PRDs" or "run batch from PRD folder" | Yes if destructive |
| Umbrella workflow | Multi-phase single kickoff; named workflows | User invokes by name (e.g. "execute umbrella workflow X") | Yes for big/destructive |
| Manual execution (lazy admin) | Human-in-the-loop; three-block format; info-gather before destructive | Sudo, confirmation, manual steps | No (protocol is guardrail) |
| Tmux shared session | All server ops in tmux via tmux_ops (pick, probe, send); 1 s delay between sends; human can attach; sudo gate via probe; REMOTE_TMUX_HOST for remote/VMs | Server commands, deployments, tmux, human-in-the-loop | No (skill defines gate) |
| Framework audit | Run doc/link/skill matrix/version checks; output user-specified path; optional `--deep` (Deep Analysis: derive invocations from SKILL.md and script `--help`, run in sandbox, summary JSON + sidecar tarball; requires output path) | User says "run audit", "run framework audit", or before release | No |

Release and publish (including version bump) are maintained in a separate maintainer repository; not documented here.

## Usage

- **Agents:** For workflows marked impact review, present impact summary and get user confirmation before proceeding.
- **Skills:** Load the matching skill (localsetup-decision-tree-workflow, localsetup-agentic-prd-batch, localsetup-agentic-umbrella-queue, localsetup-tmux-shared-session-workflow, etc.) when the task matches.
- **Tmux/sudo:** See skill localsetup-tmux-shared-session-workflow and tool `_localsetup/tools/tmux_ops`: pick session (idle = prompt on current line), probe (ready vs password_required), send with 1 s delay. Use tmux_ops send for every step; do not use raw tmux send-keys. When REMOTE_TMUX_HOST is set, wrapper runs tool over SSH. Doc: [ops/tmux-ops-remote.md](ops/tmux-ops-remote.md). Re-prompt only when probe returns password_required.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
