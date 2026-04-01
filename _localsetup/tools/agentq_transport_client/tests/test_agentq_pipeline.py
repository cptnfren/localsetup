# Purpose: Ephemeral keyring ingest tests for Agent Q transport client.
# Created: 2026-03-09
# Last updated: 2026-03-09

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[1]
_ENGINE = _PKG.parent.parent
sys.path.insert(0, str(_ENGINE))
sys.path.insert(0, str(_PKG))


@pytest.fixture
def keypair(tmp_path):
    from agentq_transport_client.keygen import generate_keypair_gnupg

    if os.system("which gpg >/dev/null 2>&1") != 0:
        pytest.skip("gpg not available")
    pub, priv, _fp = generate_keypair_gnupg(tmp_path)
    return pub.read_text(), priv.read_text()


def test_seal_unseal_roundtrip(keypair):
    from agentq_transport_client.crypto_pipeline import seal_inner_json, unseal_to_manifest

    pub, priv = keypair
    manifest = {
        "manifest_version": "1",
        "from_agent_id": "agent-test",
        "prd_body": "# Test PRD\n",
    }
    armored = seal_inner_json(manifest, pub)
    assert "BEGIN PGP" in armored
    out = unseal_to_manifest(armored, priv)
    assert out["from_agent_id"] == "agent-test"
    assert "# Test PRD" in out.get("prd_body", "")


def test_ingest_promotes_to_in(keypair, tmp_path):
    from agentq_transport_client.crypto_pipeline import seal_inner_json
    from agentq_transport_client.ingest import ingest_file_drop_blob

    pub, priv = keypair
    queue = tmp_path / "queue"
    (queue / "inbox").mkdir(parents=True)
    manifest = {
        "manifest_version": "1",
        "from_agent_id": "agent-test",
        "prd_body": "status: ready\n---\n# x\n",
    }
    armored = seal_inner_json(manifest, pub)
    blob = tmp_path / "drop" / "a.agentq.asc"
    blob.parent.mkdir(parents=True)
    blob.write_text(armored, encoding="utf-8")

    r = ingest_file_drop_blob(
        blob,
        queue_root=queue,
        recipient_private_armored=priv,
        passphrase="",
        sealed_extension=".agentq.asc",
    )
    assert r["status"] == "ok"
    promoted = Path(r["promoted_to"])
    assert promoted.is_dir()
    assert not blob.exists()  # moved to processed


def test_assert_sender_allowed_denies_unknown():
    from agentq_transport_client.registry import RegistryError, assert_sender_allowed

    validated = {"raw": {"agents": {"agent-b": {}}}}
    assert_sender_allowed(validated, "agent-b")  # ok
    with pytest.raises(RegistryError):
        assert_sender_allowed(validated, "attacker")


def test_manifest_validate_attachments_bounds():
    from agentq_transport_client.crypto_pipeline import CryptoPipelineError
    from agentq_transport_client.manifest_validate import validate_manifest

    with pytest.raises(CryptoPipelineError):
        validate_manifest({"manifest_version": "1", "from_agent_id": "a", "attachments": [{}]})
    validate_manifest(
        {
            "manifest_version": "1",
            "from_agent_id": "a",
            "attachments": [
                {"path": "f", "sha256": "a" * 64},
            ],
        }
    )


def test_extract_attachments_checksum_fail(tmp_path):
    import base64
    import hashlib

    from agentq_transport_client.attachments_extract import extract_attachments_to_staging
    from agentq_transport_client.crypto_pipeline import CryptoPipelineError

    staging = tmp_path / "st"
    staging.mkdir()
    wrong_sha = "a" * 64
    manifest = {
        "manifest_version": "1",
        "from_agent_id": "a",
        "attachments": [
            {
                "path": "f.txt",
                "sha256": wrong_sha,
                "content_b64": base64.b64encode(b"hello").decode(),
            }
        ],
    }
    with pytest.raises(CryptoPipelineError) as ex:
        extract_attachments_to_staging(staging, manifest)
    assert ex.value.code == "ingest_checksum_fail"


def _gpg_batch_gen(home: Path, name: str, email: str) -> None:
    import os
    import subprocess

    home.mkdir(parents=True, exist_ok=True)
    os.chmod(home, 0o700)
    batch = f"""%no-protection
Key-Type: RSA
Key-Length: 2048
Name-Real: {name}
Name-Email: {email}
Expire-Date: 0
%commit
"""
    subprocess.run(
        ["gpg", "--homedir", str(home), "--batch", "--gen-key"],
        input=batch.encode(),
        capture_output=True,
        timeout=60,
        check=True,
    )


@pytest.mark.skipif(os.system("which gpg >/dev/null 2>&1") != 0, reason="gpg missing")
def test_gpg_strict_ship_ingest(tmp_path):
    """Sign-then-encrypt with gpg; ingest --strict-gpg verifies signer in registry."""
    import subprocess
    import yaml

    from agentq_transport_client.ingest import ingest_file_drop_blob
    from agentq_transport_client.ship import ship_file_drop

    gpg_a = tmp_path / "gpg_a"
    gpg_b = tmp_path / "gpg_b"
    _gpg_batch_gen(gpg_a, "Alice", "alice@agentq.test")
    _gpg_batch_gen(gpg_b, "Bob", "bob@agentq.test")
    bob_pub = tmp_path / "bob.pub.asc"
    subprocess.run(
        ["gpg", "--homedir", str(gpg_b), "-a", "--export", "bob@agentq.test"],
        stdout=bob_pub.open("wb"),
        check=True,
        timeout=30,
    )
    alice_pub = tmp_path / "alice.pub.asc"
    subprocess.run(
        ["gpg", "--homedir", str(gpg_a), "-a", "--export", "alice@agentq.test"],
        stdout=alice_pub.open("wb"),
        check=True,
        timeout=30,
    )
    # registry: from_agent_id alice must have alice_pub on disk
    reg_path = tmp_path / "registry.yaml"
    reg_path.write_text(
        yaml.dump(
            {
                "version": 1,
                "local_agent_id": "bob",
                "agents": {
                    "alice": {
                        "display_name": "Alice",
                        "public_key_path": str(alice_pub),
                        "allowed_transports": ["file_drop"],
                    },
                    "bob": {"display_name": "Bob", "public_key_path": str(bob_pub), "allowed_transports": []},
                },
            }
        ),
        encoding="utf-8",
    )
    bob_sec = tmp_path / "bob.sec.asc"
    subprocess.run(
        ["gpg", "--homedir", str(gpg_b), "-a", "--export-secret-keys", "bob@agentq.test"],
        stdout=bob_sec.open("wb"),
        check=True,
        timeout=30,
    )

    out_dir = tmp_path / "out"
    queue = tmp_path / "queue"
    (queue / "inbox").mkdir(parents=True)
    manifest = {
        "manifest_version": "1",
        "from_agent_id": "alice",
        "prd_body": "# strict\n",
    }
    r_ship = ship_file_drop(
        manifest,
        bob_pub,
        out_dir,
        stem="s1",
        signer_gnupghome=gpg_a,
        signer_uid="alice@agentq.test",
    )
    assert r_ship.get("status") == "ok"
    blob = out_dir / "s1.agentq.asc"
    assert blob.is_file()

    ingest_file_drop_blob._strict_gpg = True  # type: ignore[attr-defined]
    priv = bob_sec.read_text()
    r = ingest_file_drop_blob(
        blob,
        queue_root=queue,
        recipient_private_armored=priv,
        passphrase="",
        sealed_extension=".agentq.asc",
        registry_path=reg_path,
        recipient_gnupghome=gpg_b,
    )
    assert r.get("status") == "ok", r


def test_ready_marker_sha256_mismatch_rejects(keypair, tmp_path):
    from agentq_transport_client.crypto_pipeline import seal_inner_json
    from agentq_transport_client.ingest import ingest_file_drop_blob
    from agentq_transport_client.file_drop import ready_marker_path

    pub, priv = keypair
    queue = tmp_path / "queue"
    (queue / "inbox").mkdir(parents=True)
    manifest = {"manifest_version": "1", "from_agent_id": "agent-test", "prd_body": "x"}
    armored = seal_inner_json(manifest, pub)
    blob = tmp_path / "drop" / "a.agentq.asc"
    blob.parent.mkdir(parents=True)
    blob.write_text(armored, encoding="utf-8")
    ready = ready_marker_path(blob, ".agentq.asc")
    ready.write_text("sha256 " + "0" * 64 + "\n", encoding="utf-8")
    r = ingest_file_drop_blob(
        blob,
        queue_root=queue,
        recipient_private_armored=priv,
        passphrase="",
        sealed_extension=".agentq.asc",
    )
    assert r.get("status") == "reject"
    assert r.get("code") == "READY_SHA256_MISMATCH"


def test_registry_validate_example():
    from agentq_transport_client.registry import RegistryError, load_registry_yaml, validate_registry

    example = _ENGINE / "config" / "agent_trust_registry.example.yaml"
    if not example.is_file():
        pytest.skip("example registry missing")
    raw = load_registry_yaml(example)
    with pytest.raises(RegistryError):
        validate_registry(raw, require_keys_exist=True)
    v = validate_registry(raw, require_keys_exist=False)
    assert "agent-b" in v["raw"]["agents"]
