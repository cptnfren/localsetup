---
status: ACTIVE
version: 2.1
---

# Attribution and contributors (Localsetup v2)

**Purpose:** Only humans are listed as contributors. AI assistants, IDEs, and tools (e.g. Cursor, Copilot, Claude) are not credited as co-authors or contributors. We do not list every tool in the chain (hardware, ISP, etc.); authorship is human-only.

## How the agent got listed (root cause)

GitHub counts both **author** and **committer** as contributors. The agent can appear in two ways:

1. **Co-authored-by** in the commit message.
2. **Committer identity.** When Cursor (or another IDE) runs `git commit`, it can set `GIT_COMMITTER_NAME` / `GIT_COMMITTER_EMAIL` to "Cursor Agent" or "cursoragent". One such commit is enough for GitHub to show that account as a contributor.

## How we enforce it

- **CONTRIBUTING.md:** States the policy so humans and agents do not add `Co-authored-by` trailers or list tools in contributor/credit sections.
- **Framework context:** The Cursor (and deployed) context includes an invariant: do not add `Co-authored-by` or list any AI agent as contributor or author.
- Git hooks in `.githooks/` are disabled (no-op); version bump and doc sync are done via `./scripts/publish` after you commit.

## For maintainers

Do not add AI tools to README Author, CONTRIBUTING contributor lists, or any credit section. Avoid adding Co-authored-by trailers for agents or bots when committing.

## If Cursor/cursoragent still shows as contributor (cleanup)

GitHub’s **main repo page** shows a cached contributors list; it does not auto-update after you rewrite history. The **Insights → Contributors** graph is built from current commit data.

1. **Check Insights → Contributors**  
   Repo → **Insights** → **Contributors**. If the unwanted account no longer appears there, history is clean and the problem is only the cache on the main page.

2. **Refresh the main-page contributor list**  
   GitHub does not expose a “refresh” button. To clear the stale list:
   - Go to [GitHub Support](https://support.github.com/).
   - Choose **Remove data from a repository I own or control** (or similar).
   - Ask them to **regenerate the repository contributors list** for `cptnfren/localsetup` after a history rewrite that removed Co-authored-by trailers; the Insights Contributors graph is already correct.

3. **If the account still appears in Insights → Contributors**  
   Then some ref (e.g. another branch or tag) or commit still attributes them. Check for Co-authored-by and for a different committer:
   ```bash
   git log main --format="%B" | grep -i co-authored-by || echo "None (Co-authored-by)"
   git log main --format="%cn <%ce>" | sort -u
   ```
   If a commit has "Cursor Agent" or "cursoragent" as committer, rewrite history so committer equals author (e.g. filter-branch or rebase with `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL` set from the author), then force-push. After that, only the main-page cache may need updating (step 2).

See [CONTRIBUTING.md](../CONTRIBUTING.md#attribution-and-contributors) for the full policy.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
