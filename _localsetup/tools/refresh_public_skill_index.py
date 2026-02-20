#!/usr/bin/env python3
# Purpose: Refresh PUBLIC_SKILL_INDEX.yaml from PUBLIC_SKILL_REGISTRY.urls.
# Created: 2026-02-18
# Last updated: 2026-02-18

"""
Fetches each registry URL, parses skill entries (awesome-list markdown or
GitHub API), normalizes to index schema, and writes PUBLIC_SKILL_INDEX.yaml
with updated set to current ISO8601 time.
"""

import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Awesome list: - [name](url) - description
AWESOME_LINE = re.compile(r"^\s*-\s*\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.+)$")
# Optional category from ## Section Name (we capture current section while scanning)
SECTION_HEADER = re.compile(r"^##\s+(.+)$")

REGISTRY_AWESOME = "https://github.com/VoltAgent/awesome-openclaw-skills"
REGISTRY_ANTHROPICS = "https://github.com/anthropics/skills/tree/main/skills"
RAW_AWESOME = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"
API_ANTHROPICS = "https://api.github.com/repos/anthropics/skills/contents/skills"

DESC_MAX = 300  # cap description length for index


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Localsetup-Skill-Index/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url: str):
    import json
    text = fetch_text(url)
    return json.loads(text)


def parse_awesome_list(text: str, source_registry: str) -> list[dict]:
    skills = []
    current_category = ""
    for line in text.splitlines():
        m = SECTION_HEADER.match(line)
        if m:
            current_category = m.group(1).strip()
            continue
        m = AWESOME_LINE.match(line)
        if not m:
            continue
        name, url, desc = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        if len(desc) > DESC_MAX:
            desc = desc[: DESC_MAX - 3] + "..."
        entry = {
            "name": name,
            "description": desc or name,
            "url": url,
            "source_registry": source_registry,
        }
        if current_category:
            entry["category"] = current_category
        skills.append(entry)
    return skills


def fetch_anthropics_skills(source_registry: str) -> list[dict]:
    data = fetch_json(API_ANTHROPICS)
    skills = []
    for item in data:
        if item.get("type") != "dir":
            continue
        name = item.get("name", "")
        url = item.get("html_url", "")
        if not name or not url:
            continue
        desc = name.replace("-", " ").title()
        skills.append({
            "name": name,
            "description": f"Anthropic skill: {desc}",
            "url": url,
            "source_registry": source_registry,
        })
    return skills


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    docs = repo_root / "_localsetup" / "docs"
    if not docs.is_dir():
        docs = repo_root / "docs"
    index_path = docs / "PUBLIC_SKILL_INDEX.yaml"
    registry_path = docs / "PUBLIC_SKILL_REGISTRY.urls"

    sources = [
        "https://github.com/VoltAgent/awesome-openclaw-skills",
        "https://github.com/anthropics/skills/tree/main/skills",
    ]
    if registry_path.exists():
        for line in registry_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                if line not in sources:
                    sources.append(line)

    all_skills = []
    seen_urls = set()

    # Awesome OpenClaw list
    try:
        text = fetch_text(RAW_AWESOME)
        for s in parse_awesome_list(text, REGISTRY_AWESOME):
            if s["url"] not in seen_urls:
                seen_urls.add(s["url"])
                all_skills.append(s)
    except Exception as e:
        print(f"Warning: awesome list fetch failed: {e}", file=sys.stderr)

    # Anthropics skills
    try:
        for s in fetch_anthropics_skills(REGISTRY_ANTHROPICS):
            if s["url"] not in seen_urls:
                seen_urls.add(s["url"])
                all_skills.append(s)
    except Exception as e:
        print(f"Warning: anthropics fetch failed: {e}", file=sys.stderr)

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {
        "sources": sources,
        "updated": updated,
        "skills": all_skills,
    }

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Public skill index - refresh periodically from PUBLIC_SKILL_REGISTRY.urls.\n")
        f.write("# Used by localsetup-skill-discovery to recommend similar public skills when\n")
        f.write("# the user is creating or importing a skill. Schema: sources, updated (ISO8601), skills.\n")
        yaml.dump(out, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

    print(f"Wrote {len(all_skills)} skills to {index_path} (updated={updated})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
