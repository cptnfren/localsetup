# Migrated from .cursor/rules/local-keepass-secrets.mdc
# Original: /mnt/data/devzone/localsetup-2/.cursor/rules/local-keepass-secrets.mdc

# Local KeePass secrets rule

## When to invoke localsetup-keepass-secrets

Agents should consider using the `localsetup-keepass-secrets` skill when:

- The user asks for logins, API keys, or service accounts that are described in docs by logical ID (for example `mail.box03.cruxexperts.admin`) or by known aliases (for example an email address).
- A workflow needs DB or mailbox credentials for a host that has a `secrets/<host>-secrets-map.yaml` file.
- Bulk creation or rotation of many accounts is required and passwords must not be written into repo files.

## Hard rules

- Do not write secret values into tracked files (YAML, markdown, code) or long-lived logs.
- Treat `secrets/keepass-config.yaml` and `secrets/*-secrets-map.yaml` as read-only configuration; only humans edit them.
- KeePass `.kdbx` files, keyfiles, and master passwords must not live under this repository path.

