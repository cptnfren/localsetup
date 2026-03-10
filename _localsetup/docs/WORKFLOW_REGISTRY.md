---
status: ACTIVE
version: 2.9
---

# Workflow and module registry (Localsetup v2)

**Purpose:** Registry of named workflows and when to use them; impact review when required. For the full agentic doc index, see [AGENTIC_DESIGN_INDEX.md](AGENTIC_DESIGN_INDEX.md).

## Core

| Name | Description | When to use | Impact review |
|------|-------------|-------------|---------------|
| Master rule / context | Always-loaded framework context | Always | No |
| Skills index | List of skills and when to use | When discovering which skill to load | No |

**Doc map:** Master rule and skills table live per platform (e.g. `.cursor/rules/localsetup-context.mdc`, templates under `_localsetup/templates/`). Generated catalog: [SKILLS.md](SKILLS.md).

## Workflows

| Name | Description | When to use | Impact review | Canonical doc / skill |
|------|-------------|-------------|---------------|------------------------|
| Decision tree | One Q per turn, 4 options A-D, preferred + rationale | User says "decision tree" or "reverse prompt" | No | [DECISION_TREE_WORKFLOW.md](DECISION_TREE_WORKFLOW.md); skill `localsetup-decision-tree-workflow` |
| Agent Q (queue) | Process specs in `.agent/queue/` (or structured `in/`); implement, status, outcome | User says "process PRDs" or "run batch from PRD folder" | Yes if destructive | [AGENTIC_AGENT_Q_PATTERN.md](AGENTIC_AGENT_Q_PATTERN.md), [PRD_SCHEMA_EXTERNAL_AGENT_GUIDE.md](PRD_SCHEMA_EXTERNAL_AGENT_GUIDE.md); skill `localsetup-agentic-prd-batch` |
| Agent Q bidirectional | Transport adapters (mail/file_drop) pull sealed payloads into inbox/in; outbound ack/artifact after pre-ship gate | Agent-to-agent PRD exchange over shared folder or mail | Yes if destructive ship | [AGENTIC_AGENT_TO_AGENT_PROTOCOL.md](AGENTIC_AGENT_TO_AGENT_PROTOCOL.md), [AGENTIC_AGENT_Q_SCENARIOS.md](AGENTIC_AGENT_Q_SCENARIOS.md), [AGENTIC_AGENT_Q_BIDIRECTIONAL_BUILD_SPEC.md](AGENTIC_AGENT_Q_BIDIRECTIONAL_BUILD_SPEC.md); skills `localsetup-agentq-transport`, `localsetup-mail-protocol-control` (strict mail: `preencrypted_openpgp_armored`); CLI `_localsetup/tools/agentq_transport_client/agentq_cli.py` |
| Umbrella workflow | Multi-phase single kickoff; named workflows; PHC gates | User invokes by name (e.g. "execute umbrella workflow X") | Yes for big/destructive | [AGENTIC_UMBRELLA_WORKFLOWS.md](AGENTIC_UMBRELLA_WORKFLOWS.md); skill `localsetup-agentic-umbrella-queue` |
| Manual execution (lazy admin) | Human-in-the-loop; info-gather before destructive; checkpoints | Sudo, confirmation, manual steps | No (protocol is guardrail) | Skill `localsetup-framework-compliance` (pre-task, destructive gates); tmux ops still require `localsetup-tmux-shared-session-workflow` |
| Tmux shared session | Server ops in tmux via `tmux_ops` (pick, probe, send, wait); pylon-guard delay; `send --wait` / `wait --timeout N`; REMOTE_TMUX_HOST for remote/VMs | Server commands, deployments, tmux, human-in-the-loop | No (skill defines gate) | [ops/tmux-ops-remote.md](ops/tmux-ops-remote.md); skill `localsetup-tmux-shared-session-workflow`; tool `_localsetup/tools/tmux_ops` |
| Framework audit | Doc/link/skill matrix/version checks; **output path required** for report file | User says "run audit", "run framework audit", or before release | No | Skill `localsetup-framework-audit`; entrypoint `python _localsetup/skills/localsetup-framework-audit/scripts/run_framework_audit.py --output /path/to/report.md` (or `LOCALSETUP_AUDIT_OUTPUT`). Smoke list: `_localsetup/tests/skill_smoke_commands.yaml` |
| Public skill index maintenance | Refresh index then scrub (mandatory sequence) | User says "refresh skills", "update public skill index", "refresh and scrub", or "scrub the index" | No | [SKILL_DISCOVERY.md](SKILL_DISCOVERY.md) (refresh + scrub block); skill `localsetup-skill-discovery`. Commands from repo root: (1) `python3 _localsetup/tools/refresh_public_skill_index.py` (2) `python3 _localsetup/tools/skill_index_scrub.py --skip-url-check` (3) `python3 _localsetup/tools/skill_index_scrub.py --skip-url-check --fix`. Optional: `--report path`; full URL check: omit `--skip-url-check`, optional `--workers 20` |
| Tmux-default terminal mode | Enable/disable/status via `_localsetup/tools/tmux_terminal_mode`; ide or shell mode; injects agent ops rule | User says "enable tmux mode", "tmux terminal mode", "disable tmux mode", or setting up ops machine | No | [TMUX_TERMINAL_MODE.md](TMUX_TERMINAL_MODE.md); tool `_localsetup/tools/tmux_terminal_mode` |

Release and publish (including version bump) are maintained in a separate maintainer repository; not documented here.

## Usage

- **Agents:** For workflows marked impact review, present impact summary and get user confirmation before proceeding.
- **Skills:** Load the matching skill when the task matches (see Canonical doc / skill column above).
- **Tmux/sudo:** Pick session (idle = prompt on current line), probe (`ready` vs `password_required`), send with pylon-guard delay, `send --wait` for idle confirmation, standalone `wait --timeout N` for long ops. Use `tmux_ops` for every step; never use raw tmux send-keys. When `REMOTE_TMUX_HOST` is set, wrapper runs over SSH. Re-prompt only when probe returns `password_required`.
- **Public skill index:** Run refresh then scrub then scrub --fix in order; see [SKILL_DISCOVERY.md](SKILL_DISCOVERY.md). Scrub also applies when index refresh is triggered through skill-discovery.
- **Tmux-default terminal mode:** `_localsetup/tools/tmux_terminal_mode enable [--mode ide|shell] [--session NAME]`, `disable`, or `status`. See [TMUX_TERMINAL_MODE.md](TMUX_TERMINAL_MODE.md).
- **Framework audit:** Do not claim a `--deep` flag unless the audit script documents it; current entrypoint is `run_framework_audit.py` with `--output` or env (see skill `localsetup-framework-audit`).

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
