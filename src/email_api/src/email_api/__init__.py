"""Email API Component.

This component provides abstract interfaces for basic email client functionality,
following clean architecture principles with dependency injection support.

The interfaces define the contract for email operations without implementation details,
allowing for multiple email provider implementations (Gmail, Outlook, etc.).

This component focuses on the core requirement: building an Email Client that can
crawl your inbox, pick an email, and get its content.

Example usage:
    from email_api import EmailClient, Email

    # Your implementation will inject the actual client
    async def process_emails(client: EmailClient) -> None:
        emails = await client.list_inbox_messages(limit=5)
        if emails:
            email_content = await client.get_email_content(emails[0].id)
            print(f"Subject: {email_content.subject}")
            print(f"From: {email_content.sender}")
"""

from .exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailError,
    EmailNotFoundError,
)
from .interfaces import EmailClient
from .models import Email, EmailAddress

__all__ = [
    "Email",
    "EmailAddress",
    "EmailAuthenticationError",
    "EmailClient",
    "EmailConnectionError",
    "EmailError",
    "EmailNotFoundError",
]

__version__ = "0.1.0"
__author__ = "Adithya Balachandra"
__description__ = "Email client interface component"
