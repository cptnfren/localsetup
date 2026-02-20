# Contributing to Localsetup v2

Thank you for your interest in contributing. Here’s how to get started.

## How to contribute

- **Bug reports and feature requests**  - Open an [Issue](https://github.com/cptnfren/localsetup/issues).
- **Questions and ideas**  - Use [Discussions](https://github.com/cptnfren/localsetup/discussions).
- **Code or docs changes**  - Open a Pull Request against `main`. Please keep the scope focused and reference any related Issues.

## What to expect

- We’ll review your Issue or PR and respond when we can.
- For framework changes (new skills, tools, or workflow behavior), we may ask for a short rationale or use case so we can keep the project consistent.
- By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as the project.

## Repository layout

- **Root**  - Install scripts (`install`, `install.ps1`), README, LICENSE, versioning scripts, and docs.
- **`framework/`**  - The engine: `tools/`, `lib/`, `skills/`, `templates/`, `docs/`. Changes here affect what gets deployed into a client’s `_localsetup/`.
- **Version and doc sync:** Run `./scripts/publish` (or `./scripts/publish --push`) after you commit; it bumps VERSION from the last commit message, regenerates doc artifacts, and commits the sync. See [docs/VERSIONING.md](docs/VERSIONING.md).

For detailed structure and conventions, see [framework/README.md](framework/README.md) and the docs under `framework/docs/`.

## Maintenance workflow (maintainers and agents)

After **any** modification to the framework (docs, scripts, skills, config), run the maintenance workflow so the version is bumped and changes are committed and pushed to **main**:

```bash
./scripts/maintain
```

Optional: `./scripts/maintain "fix: short description"`. See [docs/MAINTENANCE_WORKFLOW.md](docs/MAINTENANCE_WORKFLOW.md). This keeps the framework on main current; it is not a formal release. **Every modification should end with this step.**

## Attribution and contributors

**Only humans are listed as contributors.** Do not add AI assistants, IDEs, or tools (e.g. Cursor, Copilot, Claude, ChatGPT) as co-authors in commit messages or in any contributor/credit list in the repo. We do not credit every tool in the chain; authorship and contributor attribution are human-only.

## Code and docs standards

- **Scripts:** Bash and PowerShell; keep cross-platform in mind where relevant.
- **Skills:** Follow the [Agent Skills](https://agentskills.io/specification) spec (SKILL.md with `name` and `description` frontmatter).
- **Docs:** Markdown; use clear headings and relative links. Framework docs live under `framework/docs/` and are copied to `_localsetup/docs/` on deploy.

If you have questions, open a Discussion and we’ll be happy to clarify.


---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
