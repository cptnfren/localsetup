# PRD: Cloudflare DNS Management Skill

**Status:** done
**Purpose:** Specification for an AI agent skill that manages Cloudflare DNS records using the flarectl CLI and a Bash wrapper. Any agent on any machine can read this PRD and implement the full workflow set from scratch.
**Created:** 2026-02-26
**Last updated:** 2026-02-26

---

## 1. Overview

This skill gives an AI agent the ability to manage DNS records in a Cloudflare account via the terminal. The agent can list, create, modify, and delete DNS records across multiple zones (domains), run a zone survey, and schedule automated refreshes. All operations run headlessly from a shell; no browser or Cloudflare UI is required.

The skill is implemented as a wrapper script (`cf-dns.sh`) around [flarectl](https://github.com/cloudflare/cloudflare-go/tree/master/cmd/flarectl), the official Cloudflare CLI written in Go. Config (API token) is kept in a local, gitignored file.

---

## 2. Scope

This PRD covers:

- Tooling setup (flarectl install, wrapper script, config file)
- All four DNS operations: List, Create, Modify, Delete
- Zone survey (snapshot of all zones and records)
- Automated survey scheduling
- Safety rules (destructive operations)
- Agent behavior rules (multi-zone, confirmation gates)

Out of scope: Cloudflare Pages, Workers, or other Cloudflare services beyond DNS.

---

## 3. Prerequisites

The target machine must have:

- **Bash** (v4+)
- **curl** and **jq** (used by the zone survey script)
- **Go** (recommended, for building flarectl) OR a pre-built flarectl binary
- A **Cloudflare account** with at least one zone (domain)
- A **Cloudflare API token** with "Edit zone DNS" permission (see Section 6)
- **Python 3** with PyYAML installed (optional; for YAML survey output)
  - `pip3 install --user pyyaml`

---

## 4. Directory layout

All tool files live under a tools directory on the host. The recommended path is `~/.localsetup/tools/cf-dns/`, but the agent may adapt the base path to the environment. The layout must be:

```
<TOOLS_DIR>/cf-dns/
    cf-dns.sh           # wrapper script (see Section 7)
    cf-dns.conf         # token config (gitignored; created by operator)
    cf-dns.conf.example # example/template config (safe to commit)
    flarectl            # binary (local copy, OR resolved from PATH)
    survey-dns-zones.sh # zone survey script (see Section 8)
    setup-survey-schedule.sh  # scheduling wrapper (see Section 9)
    README.md           # tool-level documentation
```

Optional convenience symlink: `<TOOLS_DIR>/bin/cf-dns` pointing to `cf-dns.sh`, so that `cf-dns` works when `<TOOLS_DIR>/bin` is in PATH.

---

## 5. flarectl installation

Install the flarectl binary using one of the following methods (pick one):

**Option 1: Go install (recommended)**

```bash
go install github.com/cloudflare/cloudflare-go/cmd/flarectl@latest
cp "$(go env GOPATH)/bin/flarectl" <TOOLS_DIR>/cf-dns/flarectl
```

**Option 2: Homebrew (Linux/macOS)**

```bash
brew install flarectl
```

The wrapper script (`cf-dns.sh`) checks for the binary both alongside itself and on PATH, so a Homebrew install works without copying the binary.

**Option 3: Manual build**

```bash
git clone https://github.com/cloudflare/cloudflare-go
cd cloudflare-go
go build ./cmd/flarectl
cp flarectl <TOOLS_DIR>/cf-dns/flarectl
```

After any install, verify:

```bash
flarectl --version
```

---

## 6. API token setup

1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Go to: My Profile > API Tokens > Create Token.
3. Use the "Edit zone DNS" template, or create a custom token with:
   - **Permissions:** Zone > DNS > Edit
   - **Zone resources:** Include > All zones (or specific zones if preferred)
   - **IP restrictions (recommended):** Add the public IP(s) of the machine(s) that will call the API. This prevents token misuse if it leaks.
4. Copy the token. Store it in `<TOOLS_DIR>/cf-dns/cf-dns.conf`:

```bash
CF_API_TOKEN=your_token_here
```

The config file must be gitignored. The wrapper script sources this file if `CF_API_TOKEN` is not already set in the environment.

**Multi-machine note:** If you deploy this skill to multiple machines, each machine needs its public IP whitelisted on the token (or use separate tokens per machine). Do not use a token with no IP restriction across multiple machines.

---

## 7. Wrapper script (`cf-dns.sh`)

The wrapper is a Bash script that:

1. Resolves its own directory.
2. Sources `cf-dns.conf` if `CF_API_TOKEN` is not already in the environment.
3. Finds the flarectl binary: first looks alongside itself, then in PATH.
4. Errors clearly if the binary or token is missing.
5. Passes all arguments through to flarectl via `exec`.

Full script content:

```bash
#!/usr/bin/env bash
# Wrapper for flarectl: loads CF_API_TOKEN from cf-dns.conf and runs flarectl.
# Usage: cf-dns.sh [flarectl args...] e.g. cf-dns.sh dns list --zone=example.com
# Created: 2026-02-13.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/cf-dns.conf"

if [[ -z "${CF_API_TOKEN:-}" && -f "$CONFIG" ]]; then
  source "$CONFIG"
fi

FLARECTL_BIN=""
if [[ -x "$SCRIPT_DIR/flarectl" ]]; then
  FLARECTL_BIN="$SCRIPT_DIR/flarectl"
elif command -v flarectl &>/dev/null; then
  FLARECTL_BIN="flarectl"
fi

if [[ -z "$FLARECTL_BIN" ]]; then
  echo "flarectl not found. Install: go install github.com/cloudflare/cloudflare-go/cmd/flarectl@latest" >&2
  exit 1
fi

if [[ -z "${CF_API_TOKEN:-}" ]]; then
  echo "CF_API_TOKEN not set. Set it in $CONFIG." >&2
  exit 1
fi

exec "$FLARECTL_BIN" "$@"
```

Make it executable: `chmod +x <TOOLS_DIR>/cf-dns/cf-dns.sh`

---

## 8. Zone survey script (`survey-dns-zones.sh`)

A Bash script that calls the Cloudflare REST API (not flarectl) to snapshot all zones and their DNS records. For each record it sets a boolean field `points_to_this_host`: true if the record is an A record pointing to this machine's public IP, or a CNAME whose target is such an A name.

**Output files:**

- `<OUTPUT_DIR>/cloudflare_dns_survey.json` (always written)
- `<OUTPUT_DIR>/cloudflare_dns_survey.yaml` (written if Python 3 + PyYAML are available)

Default output directory: `~/.localsetup/context/dns/` (or adapt to the environment).

**Output schema:**

```
survey_generated_at: <ISO8601 timestamp>
this_host_ip: <public IP of the machine that ran the survey>
zones:
  - zone: <domain name>
    zone_id: <Cloudflare zone ID>
    records:
      - id: <record ID>
        type: A | CNAME | MX | TXT | ...
        name: <FQDN>
        content: <value>
        proxied: true | false
        ttl: <integer>
        points_to_this_host: true | false
```

**Usage:**

```bash
~/.localsetup/tools/cf-dns/survey-dns-zones.sh [output_dir]
```

The script sources `cf-dns.conf` for the token (same mechanism as the wrapper). It calls the Cloudflare API's `/zones` and `/zones/<id>/dns_records` endpoints directly with `curl` and `jq`.

---

## 9. Survey scheduling (`setup-survey-schedule.sh`)

A setup wrapper that schedules `survey-dns-zones.sh` to run daily (recommended: 03:15 local time). Implementation preference:

1. If cron is available: add a crontab entry for the current user.
2. Otherwise: create a systemd user timer.

The script must be idempotent (safe to run multiple times without duplicating schedules).

Usage:

```bash
~/.localsetup/tools/cf-dns/setup-survey-schedule.sh
```

---

## 10. Workflow: List DNS records

**Purpose:** Show all DNS records for a zone. Use to inspect current state, find record IDs for modify/delete, or troubleshoot.

**Agent behavior:**

- Do not assume a default zone. Always ask the user which domain to list, or infer from context.
- Present the output as a table (name, type, content, proxied, ID).

**Command:**

```bash
cf-dns.sh dns list --zone=<domain>
```

Example:

```bash
cf-dns.sh dns list --zone=example.com
```

**Record IDs** are required for modify and delete operations. Capture them from this output.

---

## 11. Workflow: Create DNS record

**Purpose:** Add a new DNS record to a zone.

**Parameters to gather:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| zone | Domain (zone) | `example.com` |
| name | Subdomain or `@` for apex | `app` or `@` |
| type | Record type | `A`, `AAAA`, `CNAME`, `MX`, `TXT` |
| content | Record value | IP for A/AAAA; hostname for CNAME |
| proxied | Cloudflare proxy (orange cloud) | Add `--proxy` flag if yes |

**Command:**

```bash
cf-dns.sh dns create --zone=<domain> --name=<name> --type=<type> --content=<content> [--proxy]
```

Examples:

```bash
# CNAME proxied through Cloudflare
cf-dns.sh dns create --zone=example.com --name=app --type=CNAME --content=target.example.com --proxy

# A record for apex, proxied
cf-dns.sh dns create --zone=example.com --name=@ --type=A --content=203.0.113.10 --proxy

# A record, DNS-only (grey cloud)
cf-dns.sh dns create --zone=example.com --name=internal --type=A --content=10.0.0.5
```

**After creation:** Confirm to the user by showing the flarectl output or re-listing the zone.

---

## 12. Workflow: Modify DNS record

**Purpose:** Change an existing record's content, TTL, or proxied status.

**Safety: this is a destructive workflow.** The agent must not apply any change until double confirmation is obtained:

1. The user states intent (e.g. "change the A record for app.example.com").
2. The agent lists the record(s) that will be changed (zone, name, type, current content, proposed new content, record ID) and waits.
3. The user must confirm again with a phrase that **includes the word "modify"** (e.g. "confirm modify"). Single-word or vague affirmatives are not accepted.

**Steps:**

1. List the zone to find the record ID:

```bash
cf-dns.sh dns list --zone=<domain>
```

2. Show the user exactly which record will change. Wait for second confirmation.

3. Apply the update:

```bash
cf-dns.sh dns update --zone=<domain> --id=<record_id> --content=<new_content> [--proxy | --no-proxy]
```

Note: exact flags for `dns update` may vary by flarectl version. Always run `flarectl dns --help` to verify available flags for the installed version.

4. Confirm: list the zone again or show the updated record.

---

## 13. Workflow: Delete DNS record

**Purpose:** Remove a DNS record from a zone.

**Safety: this is a destructive workflow.** The agent must not delete anything until double confirmation is obtained:

1. The user states intent (e.g. "delete the DNS record for app.example.com").
2. The agent shows exactly what will be deleted (zone, name, type, content, record ID) and waits.
3. The user must confirm again with a phrase that **includes the word "delete"** (e.g. "confirm delete"). Single-word or vague affirmatives are not accepted.

**Steps:**

1. List the zone to find the record ID:

```bash
cf-dns.sh dns list --zone=<domain>
```

2. Show the exact record (with ID) that will be deleted. Wait for second confirmation.

3. Delete:

```bash
cf-dns.sh dns delete --zone=<domain> <record_id>
```

4. Confirm: tell the user the record was removed. Optionally re-list the zone to prove it is gone.

---

## 14. Agent behavior rules

These rules apply to every DNS operation the agent performs:

**Multi-zone (mandatory):**
- Never assume a single domain. Always ask for or infer the zone (domain) before running any command.
- Always pass `--zone=<domain>` explicitly in every flarectl call.
- When the account has multiple zones, do not default to any one of them.

**Destructive operations (Modify, Delete):**
- Always require double confirmation as specified in Sections 12 and 13.
- Show the full details of what will be affected before asking for the second confirmation.
- Never accept a vague confirmation ("yes", "ok", "sure"). The second confirmation must include the operation name.

**Record IDs:**
- Always fetch the current record list before modify or delete to get the live record ID.
- Do not guess or reuse a record ID from a previous session without re-listing.

**Error handling:**
- If flarectl exits non-zero, surface the error output to the user.
- If the token is missing or the API call fails with an auth error, direct the user to check `cf-dns.conf` and the token's IP restrictions.

**Survey usage:**
- The agent may read `cloudflare_dns_survey.yaml` (or `.json`) for read-only context (e.g. "what records point to this host"), but must always use a live `dns list` command for any modify or delete operation to get current record IDs.

---

## 15. Skill file structure (implementation guide)

When implementing this as a Cursor skill or agent skill on a new machine, create the following files:

```
<TOOLS_DIR>/cf-dns/
    cf-dns.sh              # Section 7 (wrapper)
    cf-dns.conf.example    # Template: CF_API_TOKEN=<token>
    survey-dns-zones.sh    # Section 8
    setup-survey-schedule.sh  # Section 9
    README.md              # Brief usage guide
<DOCS_DIR>/
    DNS_WORKFLOW_INDEX.md  # Table of operations with links
    DNS_WORKFLOW_LIST.md
    DNS_WORKFLOW_CREATE.md
    DNS_WORKFLOW_MODIFY.md
    DNS_WORKFLOW_DELETE.md
```

The skill's `SKILL.md` (or equivalent entrypoint) should:

1. Point the agent to `DNS_WORKFLOW_INDEX.md` to determine which operation to run.
2. State the multi-zone rule upfront.
3. State the destructive-operation confirmation requirement upfront.
4. Reference `cf-dns.sh` as the primary tool and describe how to find flarectl.

---

## 16. Security checklist

- `cf-dns.conf` is gitignored.
- The API token has only "Edit zone DNS" permission (not account-level permissions).
- The token has an IP restriction set to the machine's public IP (rotate or update if the IP changes).
- The survey output files (`cloudflare_dns_survey.*`) contain record IDs and content: treat as sensitive; store in a gitignored location.

---

*Local doc. Not part of the framework repo.*
