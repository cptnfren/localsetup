# Agent Q transport ship gate checklist

Use before declaring the feature complete for a release.

| # | Criterion | Check |
|---|-----------|-------|
| 1 | Protocol doc ACTIVE | AGENTIC_AGENT_TO_AGENT_PROTOCOL.md front matter |
| 2 | Client docs present | USER_GUIDE, ADMIN_GUIDE, API_EXAMPLES, TROUBLESHOOTING |
| 3 | Tests pass | `pytest _localsetup/tools/agentq_transport_client/tests/` |
| 4 | No plaintext adapter ingest | ingest only armored blobs; manual PRD drop to `in/` still OK |
| 5 | Ledger events | ingest_log + ship_log JSONL present when using queue |
| 6 | Registry optional but fail-closed when set | unknown from_agent_id rejected with REGISTRY_SENDER_DENIED |
| 7 | Framework audit | Run framework-audit to user path; fix broken links |
| 8 | SKILLS.md / templates | Mention agentq client + mail-pull where relevant |

## Sign-then-encrypt (Part 1 #5)

- **file_drop strict path:** `ship-file-drop --signer-gnupghome` + `ingest-blob --strict-gpg` gives gpg sign-then-encrypt and signer fingerprint binding to `from_agent_id`. Use this when the spec requires signature as legitimacy gate on the adapter path.
- **file_drop default path:** PGPy encrypt-only outer (`agentq_outer`) remains for backward compatibility and mail parity.
- **Mail path:** Still encrypt-only outer via mail stack; deferred to phase when mail_send can wrap gpg-signed payload (see DEFERRED.md).

Deferred by design (see DEFERRED.md): mail outer gpg sign-then-encrypt, multi-recipient phase 2, Drive API, Telegram adapter, full tar bundle without size cap.
