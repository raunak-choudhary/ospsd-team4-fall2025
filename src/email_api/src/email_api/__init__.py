"""Email API Component.

This component provides abstract interfaces for basic email client functionality,
following clean architecture principles with dependency injection support.

The interfaces define the contract for email operations without implementation details,
allowing for multiple email provider implementations (Gmail, Outlook, etc.).

This component focuses on the core requirement: building an Email Client that can
crawl your inbox, pick an email, and get its content.

Example usage:
    from email_api import Client, Email

    # Your implementation will inject the actual client
    def process_emails(client: Client) -> None:
        for email in client.get_messages():
            print(f"Subject: {email.subject}")
            print(f"From: {email.sender}")
"""

from email_api.client import Client, Email, EmailAddress, get_client

__all__ = [
    "Client",
    "Email",
    "EmailAddress",
    "get_client",
]

__version__ = "0.1.0"
__author__ = "Adithya Balachandra"
__description__ = "Email client interface component"
