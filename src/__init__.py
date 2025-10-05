"""Register GmailClient as the default email_api client implementation."""

from email_api import register_client_factory
from .gmail_client import GmailClient  # ✅ correct local import (no circular dependency)

# Register GmailClient so that email_api.get_client() uses it by default
register_client_factory(GmailClient)

# Expose for direct test imports
gmail_client = GmailClient
GmailClient = GmailClient

__all__ = ["GmailClient", "gmail_client"]
