"""Shared pytest configuration for integration and E2E tests."""

import os
from pathlib import Path

import pytest

from gmail_impl import GmailConfig


def credentials_available() -> bool:
    """Check if Gmail credentials are available (file or environment variable)."""
    return (
        Path("credentials.json").exists()
        or os.getenv("GMAIL_CREDENTIALS_JSON") is not None
    )


@pytest.fixture(scope="session")
def gmail_credentials_file() -> Path:
    """Ensure Gmail credentials file exists, creating from env var if needed."""
    creds_file = Path("credentials.json")

    # If file doesn't exist but env var does, create the file
    if not creds_file.exists():
        creds_json = os.getenv("GMAIL_CREDENTIALS_JSON")
        if creds_json:
            creds_file.write_text(creds_json)
        else:
            pytest.skip("Gmail credentials not available")

    return creds_file


@pytest.fixture
def integration_config(gmail_credentials_file: Path) -> GmailConfig:
    """Create Gmail configuration for integration testing."""
    # Use CI token if available, otherwise fall back to test_token.json
    token_file = (
        "ci_token.json" if os.getenv("GMAIL_CI_TOKEN_JSON") else "test_token.json"
    )

    return GmailConfig(
        credentials_file=str(gmail_credentials_file),
        token_file=token_file,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )


@pytest.fixture
def e2e_config(gmail_credentials_file: Path) -> GmailConfig:
    """Create Gmail configuration for E2E testing."""
    # Use E2E token if available, otherwise fall back to e2e_token.json
    token_file = "e2e_token.json"

    return GmailConfig(
        credentials_file=str(gmail_credentials_file),
        token_file=token_file,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
