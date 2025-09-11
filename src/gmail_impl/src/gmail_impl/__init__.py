"""Gmail implementation of the EmailClient protocol.

This component provides a concrete implementation of the EmailClient protocol
using the Gmail API with OAuth2 authentication and dependency injection.

Example usage:
    import asyncio
    from gmail_impl import GmailClient, GmailConfig

    async def main():
        config = GmailConfig(
            credentials_file="credentials.json",
            token_file="token.json"
        )

        async with GmailClient(config) as client:
            emails = await client.list_inbox_messages(limit=5)
            if emails:
                content = await client.get_email_content(emails[0].id)
                print(f"Subject: {content.subject}")

    asyncio.run(main())
"""

from .client import GmailClient
from .config import GmailConfig

__all__ = ["GmailClient", "GmailConfig"]
