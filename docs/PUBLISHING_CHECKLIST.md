# Publishing checklist (Localsetup v2)

Use this checklist before publishing the repo as a **public** repository on GitHub.

## Documentation and structure

- [ ] **README**  - Clear value proposition, install instructions, layout, versioning, license, and author. Contents table or TOC for navigation.
- [ ] **SECURITY.md**  - How to report vulnerabilities (private report or contact); link from repo Security tab.
- [ ] **CONTRIBUTING.md**  - How to open Issues, Discussions, and PRs; license and repo layout.
- [ ] **LICENSE**  - MIT (or chosen license) with correct copyright holder (e.g. Crux Experts LLC).
- [ ] **Framework README**  - `framework/README.md` describes engine, tools, skills, and docs; links to root where needed.

## Scrub: no PII or context-specific artifacts

- [ ] **No personal data**  - No real email addresses, physical addresses, or phone numbers (except intended public contact).
- [ ] **No secrets**  - No API keys, tokens, passwords, or credentials. No `.env` or secret files committed.
- [ ] **No machine-specific paths**  - No hardcoded `/home/username`, `/Users/name`, `C:\Users\...`, or internal hostnames (e.g. devzone, SKTOP01) in docs or code. Use placeholders or env vars where paths are needed.
- [ ] **Clone URL**  - Default `REPO_URL` / `LOCALSETUP_2_REPO` in `install` and `install.ps1` points to the public repo (e.g. `https://github.com/cptnfren/localsetup.git`). Overridable via env for forks.
- [ ] **Issue/Discussion links**  - README and framework README use the correct repo owner in GitHub URLs.
- [ ] **Deploy artifacts**  - `framework/_localsetup/` is in `.gitignore` and not tracked (deploy creates it at client repo root; it should not be in the source repo).

## Version and release

- [ ] **VERSION**  - Set to the intended release version (e.g. 2.0.0).
- [ ] **Version display**  - README and framework README show the same version; framework docs’ front matter `version: X.Y` matches if used.
- [ ] **Versioning docs**  - `docs/VERSIONING.md` explains bump behavior and optional hooks.

## Repository settings (on GitHub)

- [ ] **Visibility**  - Set to Public when ready.
- [ ] **Description and topics**  - Short description and topics (e.g. `workflow`, `cursor`, `devops`, `agent`) for discoverability.
- [ ] **Default branch**  - Usually `main`; install script and README curl URLs use the correct branch name.
- [ ] **Issues and Discussions**  - Enabled if you want contact via GitHub.
- [ ] **Security**  - “Private vulnerability reporting” optional but recommended; SECURITY.md explains how to report.

## Optional

- [ ] **GitHub Actions**  - CI (e.g. shellcheck, tests) if desired.
- [ ] **Code of conduct**  - Add `CODE_OF_CONDUCT.md` if you want a formal CoC.
- [ ] **Changelog**  - `CHANGELOG.md` for release notes (optional).

---

**Quick scrub commands (from repo root):**

```bash
# Search for possible secrets or PII (review any matches)
grep -rniE 'password|secret|api[_-]?key|token|/home/|/Users/|@[a-z0-9.-]+\.[a-z]{2,}' --include='*.md' --include='*.sh' --include='*.ps1' --include='*.yaml' . 2>/dev/null || true

# Ensure no backup or local files tracked
git status --short
```

After all items are checked, the repo is ready for public publish.

---

<p align="center">
<strong>Author:</strong> <a href="https://github.com/cptnfren">Slavic Kozyuk</a><br>
<strong>Copyright</strong> © 2026 <a href="https://www.cruxexperts.com/">Crux Experts LLC</a> – Innovate, Automate, Dominate.
</p>
