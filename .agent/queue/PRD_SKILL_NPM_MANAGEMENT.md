# PRD: NPM (Nginx Proxy Manager) Management Skill

**Status:** done
**Purpose:** Specification for an AI agent skill that manages Nginx Proxy Manager (NPM) proxy hosts via its REST API, using the npm-api.sh Bash script. Any agent on any machine can read this PRD and implement the full workflow set from scratch.
**Created:** 2026-02-26
**Last updated:** 2026-02-26

---

## 1. Overview

This skill gives an AI agent the ability to manage reverse proxy configuration in Nginx Proxy Manager through a terminal script rather than the NPM web UI. The agent can create, list, search, update, enable, disable, and delete proxy hosts; trigger NPM backups; and coordinate with Docker operations to deploy or remove services.

The skill is built on [npm-api.sh](https://github.com/Erreur32/nginx-proxy-manager-Bash-API) (Erreur32/nginx-proxy-manager-Bash-API), a Bash script that wraps NPM's REST API. It works entirely headlessly and is suitable for automation, cron jobs, and agent-driven deployment workflows.

---

## 2. Architecture context

NPM is an Nginx-based reverse proxy that runs in Docker. It sits in front of all containers that need public HTTP/HTTPS access. The architecture rule is simple:

- Any container that must be reachable from the internet is placed on a shared Docker network (e.g. `npm_default`). NPM is also on that network and resolves backends by container name via Docker DNS.
- No container publishes host ports 80 or 443. NPM listens on 80/443 and forwards by hostname.
- A container that does not need public access is NOT on that shared network (or has no NPM proxy host).

This means: creating a new service = deploy container on `<NPM_NETWORK>` + create NPM proxy host. Removing a service = delete NPM proxy host + stop/remove containers.

The skill covers the NPM proxy host side. Docker operations (compose, inspect, stop, rm) are shell commands the agent runs alongside the NPM API script.

---

## 3. Scope

This PRD covers:

- Tooling setup (npm-api.sh install, config file)
- Proxy host default template and parameter conventions
- Six workflows: Create, Modify, Diagnose, Remove, Cleanup, Backup/Restore
- Safety rules (destructive operations, multi-item selection)
- Agent behavior rules

Out of scope: NPM access lists, streams (TCP/UDP forwarding), redirection hosts, or dead certificate management. These can be added as extensions.

---

## 4. Prerequisites

The target machine must have:

- **Docker** and **Docker Compose** (or equivalent) running.
- **Nginx Proxy Manager** deployed in a container, admin API reachable (default: HTTP on port 81). Standard image: `jc21/nginx-proxy-manager:latest`.
- A **shared Docker network** (e.g. `npm_default`) that both NPM and all public-facing containers are attached to.
- **Bash**, **curl**, **jq** (required by npm-api.sh).
- NPM admin credentials (email and password).

---

## 5. Directory layout

```
<TOOLS_DIR>/npm-api/
    npm-api.sh      # the Erreur32 script; make executable
    npm-api.conf    # local config (gitignored)
    data/           # default backup directory used by the script
    README.md       # upstream script readme
    CHANGELOG.md    # upstream changelog
```

Optional convenience symlink: `<TOOLS_DIR>/bin/npm-api` pointing to `npm-api.sh`.

---

## 6. npm-api.sh installation

Clone or download from the upstream repo:

```bash
git clone https://github.com/Erreur32/nginx-proxy-manager-Bash-API.git <TOOLS_DIR>/npm-api
chmod +x <TOOLS_DIR>/npm-api/npm-api.sh
```

Or download just the script:

```bash
mkdir -p <TOOLS_DIR>/npm-api
curl -L https://raw.githubusercontent.com/Erreur32/nginx-proxy-manager-Bash-API/main/npm-api.sh \
  -o <TOOLS_DIR>/npm-api/npm-api.sh
chmod +x <TOOLS_DIR>/npm-api/npm-api.sh
```

Verify the script runs:

```bash
<TOOLS_DIR>/npm-api/npm-api.sh --help
```

---

## 7. Config file (`npm-api.conf`)

Create `<TOOLS_DIR>/npm-api/npm-api.conf` and gitignore it. This file is sourced by the script.

Required fields:

```bash
NGINX_IP=127.0.0.1      # IP where NPM admin API is reachable from this machine
NGINX_PORT=81           # NPM admin port (default 81)
API_USER=admin@example.com   # NPM admin email
API_PASS=yourpassword        # NPM admin password
```

Optional:

```bash
DATA_DIR=<TOOLS_DIR>/npm-api/data   # directory for NPM backups; defaults to data/ inside script dir
```

The script auto-generates and caches an API token; you do not manage the bearer token manually.

---

## 8. Proxy host: conventions and default template

Every proxy host maps one or more public hostnames to one container (or backend). The key parameters are:

| Parameter | Description | Default |
|-----------|-------------|---------|
| domain_names | Public hostname(s) for the service | (required) |
| forward_host | Backend hostname or container name | (required) |
| forward_port | Port the backend listens on internally | (required) |
| forward_scheme | Protocol NPM uses to reach backend | `http` |
| ssl_forced | Redirect HTTP to HTTPS | `true` |
| http2_support | Enable HTTP/2 | `true` |
| hsts_enabled | Send HSTS header | `false` |
| caching_enabled | NPM-level caching | `false` |
| block_exploits | Block common exploit patterns | `true` |
| allow_websocket_upgrade | Pass WebSocket upgrade headers | `false` |
| access_list_id | NPM access list to apply | `0` (none) |
| advanced_config | Raw nginx config block | (empty) |
| locations | Custom location blocks | `[]` |
| enabled | Host is active | `true` |

**Forward host:** For containers on the shared NPM network, always use the **Docker container name** as `forward_host`. NPM resolves it via Docker DNS. Never use the host machine's IP for containers on that network. Exception: `localhost` when targeting the NPM container itself.

**Forward scheme:** Use `http` unless the container serves TLS internally (e.g. some admin panels that only serve HTTPS on their internal port). Use `https` only when the container's internal port actually speaks TLS.

**SSL:** NPM terminates TLS. Attach a Let's Encrypt certificate (or an existing cert) for the domain. Certificate management is done via NPM UI or via additional npm-api.sh SSL commands.

**WebSockets:** Set `allow_websocket_upgrade=true` only for apps that actually use WebSockets (e.g. chat apps, live dashboards, media servers, development proxies).

**Advanced config:** Use only when the app requires nginx-level tuning (e.g. `client_max_body_size 1000M;` for large file uploads). Leave empty for standard web apps.

---

## 9. Key npm-api.sh commands

All commands are called as:

```bash
<NPM_API> <flag> [args] -y
```

`-y` suppresses interactive prompts (use in all agent/automation contexts).

| Action | Command |
|--------|---------|
| Check connectivity / token | `<NPM_API> --info -y` |
| List all proxy hosts | `<NPM_API> --host-list -y` |
| Search by domain | `<NPM_API> --host-search <domain> -y` |
| Show one host (by ID) | `<NPM_API> --host-show <id> -y` |
| Create proxy host | `<NPM_API> --host-create <domain> -i <container_name> -p <port> [options] -y` |
| Update a field on a host | `<NPM_API> --host-update <id> <field>=<value> -y` |
| Enable a proxy host | `<NPM_API> --host-enable <id> -y` |
| Disable a proxy host | `<NPM_API> --host-disable <id> -y` |
| Delete a proxy host | `<NPM_API> --host-delete <id> -y` |
| Backup NPM config | `<NPM_API> --backup -y` |
| List users | `<NPM_API> --user-list -y` |

Run `<NPM_API> --help` for the full flag list and exact syntax for the installed version. Flags and option names vary slightly between script versions.

The proxy host **ID** is an integer assigned by NPM. Get it from `--host-list` or `--host-search` output. IDs are stable across restarts but not across a full NPM data wipe.

---

## 10. Workflow: Create (deploy service and expose via NPM)

**Purpose:** Deploy a new container or stack and, for each container that needs public access, create an NPM proxy host using the default template.

**Steps:**

1. **Define the stack.** In the compose file (or `docker run` command): attach any service that must be publicly reachable to `<NPM_NETWORK>`. Do not publish host ports 80 or 443 for that service.

2. **Deploy.**

```bash
docker compose up -d
```

or equivalent.

3. **For each public container, gather the proxy host parameters:**
   - domain_names: the public hostname(s)
   - forward_host: the Docker container name on `<NPM_NETWORK>`
   - forward_port: the container's internal port
   - forward_scheme: `http` unless the container serves TLS internally
   - Determine if WebSocket support is needed

4. **Create the proxy host.**

```bash
<NPM_API> --host-create <domain> -i <container_name> -p <port> [options] -y
```

Attach an SSL certificate (Let's Encrypt or existing) for the domain via NPM UI or npm-api.sh SSL commands.

5. **Optional: create the DNS record.** If the public hostname must resolve and you have DNS automation set up, run the DNS skill (see `PRD_SKILL_CLOUDFLARE_DNS.md`) to create the corresponding A or CNAME record. The DNS step is separate from this skill but is the natural next step after proxy host creation.

6. **Verify.** Confirm the proxy host is listed and enabled:

```bash
<NPM_API> --host-search <domain> -y
```

Test the public URL in a browser or with curl.

---

## 11. Workflow: Modify (change deployment or proxy config)

**Purpose:** Change an existing deployment (image version, env vars, ports, network membership) and/or update the corresponding NPM proxy host.

**Safety: this is a destructive workflow.** Double confirmation required before applying changes:

1. The user states intent (e.g. "change the forward port for app.example.com").
2. The agent shows exactly what will be modified: proxy host ID(s), domain(s), container name(s), and a concise summary of the change. Waits.
3. The user must confirm again with a phrase that **includes the word "modify"** (e.g. "confirm modify"). Vague or single-word replies are not accepted.

**Steps:**

1. **Identify current state.** List or search proxy hosts; inspect the container.

```bash
<NPM_API> --host-list -y
<NPM_API> --host-search <domain> -y
docker inspect <container_name>
```

Show the user the current state (proxy ID, domain, container name, port, scheme). Present what will change. **Wait for second confirmation.**

2. **Apply Docker-side changes.** Update compose file, recreate containers (`docker compose up -d --force-recreate`), or run `docker stop` / `docker rm` / `docker run`. If network membership changes, ensure `<NPM_NETWORK>` is still attached for public-facing containers.

3. **Update the NPM proxy host if needed** (if domain, container name, port, or scheme changed).

```bash
<NPM_API> --host-update <id> forward_host=<new_name> -y
<NPM_API> --host-update <id> forward_port=<new_port> -y
<NPM_API> --host-update <id> forward_scheme=<http|https> -y
```

Update the SSL certificate if the domain changed.

---

## 12. Workflow: Diagnose (inspect and troubleshoot)

**Purpose:** Inspect running state, logs, connectivity, and NPM proxy config to troubleshoot issues.

**Steps:**

1. **Get an overview.**

```bash
docker ps -a
docker network inspect <NPM_NETWORK>
<NPM_API> --host-list -y
<NPM_API> --info -y
```

2. **Per service.** Check the container's logs, stats, and health. Verify it is a member of `<NPM_NETWORK>`. Verify an NPM proxy host exists for it with the correct container name and internal port.

```bash
docker logs <container_name>
docker inspect <container_name> --format '{{json .NetworkSettings.Networks}}'
<NPM_API> --host-search <domain> -y
```

3. **Common failure modes to check:**

| Symptom | Check |
|---------|-------|
| 502 Bad Gateway | Container is not on `<NPM_NETWORK>`; wrong port; container not running |
| SSL errors | Certificate missing or expired; domain mismatch |
| Redirect loop | ssl_forced=true on a backend that also redirects to HTTPS |
| WebSocket failure | allow_websocket_upgrade not enabled |
| "Not found" / wrong app | forward_host or forward_port points to wrong container |
| DNS not resolving | DNS record missing or not yet propagated |

4. **Connectivity test from NPM container.**

```bash
docker exec <npm_container_name> curl -s http://<backend_container_name>:<port>/
```

This verifies Docker DNS resolution and backend reachability from NPM's network namespace.

---

## 13. Workflow: Remove (decommission service and proxy host)

**Purpose:** Stop and remove containers and delete the corresponding NPM proxy host(s).

**Safety: this is a destructive workflow.** Double confirmation required:

1. The user states intent (e.g. "remove the X service").
2. The agent shows exactly what will be removed (proxy host ID, domain, container name). For multiple items: list with numeric indices, get user selection by number, echo back interpreted selection. Waits.
3. The user must confirm again with a phrase that **includes the word "remove"** (e.g. "confirm remove"). Vague or single-word replies are not accepted.

**Multi-item selection protocol:**

When multiple proxy hosts or containers are candidates:

1. List all candidates with metadata (domain, container, stack, enabled/disabled) and numeric indices (1, 2, 3...).
2. User selects by number ("1, 3, 4" or "all").
3. Agent relists only the selected items (numbers + key metadata) and says: "I will remove: 1. [X], 3. [Y]. Confirm this list (e.g. 'confirm remove')."
4. Execute only after that second confirmation.

**Steps:**

1. **Identify targets.**

```bash
<NPM_API> --host-list -y
<NPM_API> --host-search <domain> -y
```

Present the list. If multiple items, apply the multi-item selection protocol. **Wait for second confirmation.**

2. **Delete NPM proxy host(s).**

```bash
<NPM_API> --host-delete <id> -y
```

3. **Stop and remove containers.**

```bash
docker compose down       # from the stack directory
# or
docker stop <name> && docker rm <name>
```

Optionally remove named volumes if decommissioning completely:

```bash
docker compose down -v
```

Warn the user before removing volumes; this is irreversible.

---

## 14. Workflow: Cleanup (prune orphans and unused resources)

**Purpose:** Remove NPM proxy hosts that have no running backend and prune unused Docker resources (stopped containers, dangling images, unused networks).

**Safety: this is a destructive workflow.** Double confirmation with multi-item selection protocol (same as Section 13). Second confirmation phrase must include "cleanup" (e.g. "confirm cleanup").

**Steps:**

1. **Build a candidate list.** Do not rely on `docker system prune --dry-run` (availability varies). Instead:
   - List all NPM proxy hosts; for each, check whether a matching container exists and is running. Mark as "orphan" if the backend is missing or stopped.
   - List stopped containers, dangling images, unused networks.
   - Assign metadata (created date, status, stack) and numeric indices.
   - Present to the user.

```bash
<NPM_API> --host-list -y
docker ps -a
docker images -f dangling=true
docker network ls
```

2. **User selects by number.** Agent echo-backs selection. User confirms with "confirm cleanup".

3. **Remove selected orphan NPM proxy hosts.**

```bash
<NPM_API> --host-delete <id> -y
```

4. **Docker prune** as selected by the user (targeted, not catch-all unless user explicitly asked for full prune).

```bash
docker container prune -f       # stopped containers
docker image prune -f           # dangling images
docker image prune -af          # all unused images (more aggressive)
docker network prune -f         # unused networks
docker volume prune -f          # unused volumes (CAREFUL: data loss)
```

Warn separately before `volume prune`: volumes may contain database or user data.

---

## 15. Workflow: Backup and Restore

**Purpose:** Backup NPM configuration and compose/stack definitions; restore from backup.

**Backup steps are non-destructive.** No double confirmation required.

**Restore is destructive.** Before executing any restore, show exactly what will be overwritten and require double confirmation. Second confirmation phrase must include "restore" (e.g. "confirm restore").

**Backup steps:**

1. **Backup NPM config** (proxy hosts, certs, users, settings).

```bash
<NPM_API> --backup -y
```

The script writes the backup to `DATA_DIR` (set in `npm-api.conf`; default: `data/` inside the script directory). Note the path from the output.

2. **Backup compose/stack files.** Copy compose files, env files, and any custom configs to a local backup directory.

```bash
mkdir -p <BACKUP_DIR>/<stack-name>
cp -r /path/to/stack/. <BACKUP_DIR>/<stack-name>/
```

Recommended backup directory: `~/.localsetup/backups/compose/` or a path documented in local context so all agents use the same location.

**Restore steps:**

NPM restore via the script is not fully implemented in all versions. Current approach:

- **NPM config restore:** Check current npm-api.sh version for `--restore` support. If not available: restore manually via NPM UI (re-create proxy hosts from backup file) or re-run the Create workflow for each host.
- **Compose restore:** Re-deploy from saved compose files (`docker compose up -d`).

Before any restore action: show the user what backup file will be used, what it will overwrite, and what the expected result is. Wait for "confirm restore".

---

## 16. Agent behavior rules

**Zone / environment awareness:**

- The agent must know the value of `<NPM_NETWORK>` for the target machine before running any workflow. Default is `npm_default` but it may differ per environment.
- Confirm the NPM API is reachable before attempting operations: `<NPM_API> --info -y`.

**Destructive operations (Modify, Remove, Cleanup, Restore):**

- Always require double confirmation as specified per workflow.
- Never accept "yes", "ok", "go ahead", or similar vague replies as the second confirmation. The second confirmation must include the operation name.
- For multi-item operations: always present numbered lists, echo back the interpreted selection, then ask for the named confirmation.

**Proxy host IDs:**

- IDs are integers assigned by NPM. Always fetch a fresh list before modify, delete, or enable/disable to get current IDs. Do not reuse IDs from memory.

**Container name as forward_host:**

- For containers on `<NPM_NETWORK>`, always use the Docker container name, not an IP address. Container names are stable across restarts; IPs are not.

**SSL:**

- When creating a new proxy host, always raise the question of SSL certificate attachment. NPM handles TLS termination; if the domain must serve HTTPS (which is the default for any public service), the agent should prompt the user to attach or request a Let's Encrypt certificate.

**Error handling:**

- If npm-api.sh exits non-zero, show the error output to the user.
- If the API token is stale or rejected, the script auto-refreshes. If that fails, check `NGINX_IP`, `NGINX_PORT`, `API_USER`, `API_PASS` in the config.
- If a container is not found on `<NPM_NETWORK>` when creating a proxy host, warn the user before proceeding.

---

## 17. Skill file structure (implementation guide)

When implementing this as a Cursor skill or agent skill on a new machine, create the following:

```
<TOOLS_DIR>/npm-api/
    npm-api.sh              # Erreur32 script (Section 6)
    npm-api.conf            # Config (Section 7; gitignored)
    data/                   # Backup directory (auto-created by script)
    README.md
<DOCS_DIR>/
    DOCKER_DEVOPS_INDEX.md  # Workflow table of contents
    DOCKER_WORKFLOW_CREATE.md
    DOCKER_WORKFLOW_MODIFY.md
    DOCKER_WORKFLOW_DIAGNOSE.md
    DOCKER_WORKFLOW_REMOVE.md
    DOCKER_WORKFLOW_CLEANUP.md
    DOCKER_WORKFLOW_BACKUP_RESTORE.md
    NPM_PROXY_HOST_BASELINE.md   # Architecture rule summary
    NPM_PROXY_PATTERNS_AND_TEMPLATE.md  # Default template reference
    NPM_AND_API_AUTOMATION.md    # Generic automation overview
```

The skill's `SKILL.md` (or equivalent entrypoint) should:

1. State the architecture rule: public containers go on `<NPM_NETWORK>`; NPM handles 80/443.
2. Point the agent to `DOCKER_DEVOPS_INDEX.md` to select the right workflow.
3. State destructive-operation confirmation requirements upfront.
4. Reference `npm-api.sh` as the primary tool and note that `-y` is required for headless use.

---

## 18. Placeholders reference

Use these consistently across all workflow docs so they can be adapted to any environment:

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `<TOOLS_DIR>` | Root of the tools directory | `~/.localsetup/tools` |
| `<NPM_API>` | Full path to npm-api.sh | `~/.localsetup/tools/npm-api/npm-api.sh` |
| `<NPM_NETWORK>` | Shared Docker network name | `npm_default` |
| `<BACKUP_DIR>` | Backup directory for compose files | `~/.localsetup/backups/compose` |

---

## 19. Security checklist

- `npm-api.conf` is gitignored. It contains the NPM admin password.
- NPM admin port (81) is not exposed to the internet. It must be reachable only from localhost or a trusted management network.
- Use a strong NPM admin password. The npm-api.sh script does not hash or encrypt credentials; the config file must have permissions `600`.
- The `data/` backup directory may contain SSL private keys. Restrict permissions accordingly.

---

*Local doc. Not part of the framework repo.*

---

## Implementation outcome

**Status:** done  
**Completed:** 2026-02-26  
**Implemented by:** Cursor agent (claude-4.6-sonnet-medium)  
**Commit:** 09c1aa3 (v2.6.0)

### What was built

- `_localsetup/skills/localsetup-npm-management/SKILL.md` — skill entrypoint with full operation catalogue
- `_localsetup/skills/localsetup-npm-management/scripts/npm_api.py` — native Python REST client (replaces npm-api.sh entirely)
- `_localsetup/skills/localsetup-npm-management/scripts/test_npm_api.py` — unittest suite covering input hardening, config, token logic, CLI, and HTTP error handling
- `_localsetup/skills/localsetup-npm-management/references/npm-api-conf-example.md` — config template with security notes
- `_localsetup/skills/localsetup-npm-management/references/proxy-host-template.md` — full proxy host parameter reference

### Deviations from PRD

- **Tooling:** PRD specified `npm-api.sh` (Erreur32/nginx-proxy-manager-Bash-API). After evaluation, the upstream script was identified as a `curl`/`jq` wrapper around a REST API. Replaced entirely with a native Python client (`npm_api.py`) using only Python standard library (`urllib`, `json`, `configparser`). Eliminates Bash, curl, and jq dependencies. All PRD behaviors replicated verbatim.
- No other deviations. All 19 spec sections implemented.

### Registration

Registered in localsetup-context/SKILL.md and all platform templates (Cursor, Claude Code, Codex, OpenClaw). Skill count bumped from 37 to 39 (shared count with cloudflare-dns).
