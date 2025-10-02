"""Gmail implementation of the Client protocol.

This component provides a concrete implementation of the Client protocol
using the Gmail API with OAuth2 authentication.
"""

import email_api
from gmail_impl.gmail_client import GmailClient

__all__ = ["GmailClient"]

# Dependency injection: Replace email_api.get_client with our implementation
email_api.get_client = lambda: GmailClient()
