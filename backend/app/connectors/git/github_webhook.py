"""Small, side-effect-free helpers for validating GitHub webhook deliveries."""
from __future__ import annotations

import hashlib
import hmac
from urllib.parse import urlparse


def verify_github_signature(body: bytes, signature: str, secret: str) -> bool:
    """Validate GitHub's X-Hub-Signature-256 value using constant-time comparison."""
    if not secret or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


def canonical_github_repository(value: str | None) -> tuple[str, str] | None:
    """Return (host, owner/repository), normalizing HTTPS and SSH GitHub URLs."""
    if not value or not value.strip():
        return None
    value = value.strip()
    if value.startswith("git@") and ":" in value:
        host, path = value[4:].split(":", 1)
        host = host.lower()
    else:
        parsed = urlparse(value)
        host = (parsed.hostname or "").lower()
        path = parsed.path
    if not host or not path:
        return None
    path = path.strip("/")
    if path.lower().endswith(".git"):
        path = path[:-4]
    parts = [part for part in path.split("/") if part]
    if len(parts) != 2:
        return None
    return host, f"{parts[0].lower()}/{parts[1].lower()}"


def payload_matches_repository(remote_url: str | None, payload_repository: dict) -> bool:
    """Ensure a signed delivery is about the repository configured for this record."""
    configured = canonical_github_repository(remote_url)
    if configured is None:
        return False
    candidates = (
        payload_repository.get("clone_url"),
        payload_repository.get("ssh_url"),
        payload_repository.get("html_url"),
        payload_repository.get("url"),
    )
    return any(canonical_github_repository(candidate) == configured for candidate in candidates)
