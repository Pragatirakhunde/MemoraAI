import hashlib
import hmac

from app.connectors.git.github_webhook import (
    canonical_github_repository,
    payload_matches_repository,
    verify_github_signature,
)


def test_valid_github_signature_is_accepted():
    body = b'{"ref":"refs/heads/main"}'
    secret = "demo-webhook-secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_github_signature(body, f"sha256={digest}", secret)


def test_invalid_signature_is_rejected():
    assert not verify_github_signature(b"payload", "sha256=invalid", "secret")
    assert not verify_github_signature(b"payload", "", "secret")
    assert not verify_github_signature(b"payload", "sha256=anything", "")


def test_github_url_normalization_handles_https_and_ssh():
    https = canonical_github_repository("https://github.com/TechNova/PayFlow.git")
    ssh = canonical_github_repository("git@github.com:technova/payflow.git")
    assert https == ssh == ("github.com", "technova/payflow")


def test_webhook_repository_must_match_configured_remote():
    payload_repository = {
        "clone_url": "https://github.com/TechNova/PayFlow.git",
        "html_url": "https://github.com/TechNova/PayFlow",
    }
    assert payload_matches_repository("git@github.com:technova/payflow.git", payload_repository)
    assert not payload_matches_repository("https://github.com/TechNova/HRConnect.git", payload_repository)
