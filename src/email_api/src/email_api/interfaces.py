"""Email client interface definitions using Protocol for dependency injection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self

if TYPE_CHECKING:
    from types import TracebackType

    from .models import Email


class EmailClient(Protocol):
    """Protocol defining the interface for basic email client operations.

    This protocol defines the contract that all email client implementations must follow
    for basic inbox crawling and email content retrieval operations.

    Using Protocol instead of ABC provides better typing support and more flexibility
    for dependency injection.

    Example usage with dependency injection:
        async def process_emails(client: EmailClient) -> None:
            emails = await client.list_inbox_messages()
            if emails:
                email_content = await client.get_email_content(emails[0].id)
                print(f"Subject: {email_content.subject}")
    """

    async def list_inbox_messages(self, limit: int = 10) -> list[Email]:
        """List messages from the inbox.

        This method searches the inbox and returns a list of emails with basic
        information. Behind this simple interface lies complex functionality:
        - Authentication with email servers
        - Protocol-specific communication (IMAP, Gmail API, etc.)
        - Message parsing and normalization
        - Error handling and retries
        - Pagination and filtering

        Args:
            limit: Maximum number of messages to retrieve (default: 10)

        Returns:
            List of Email objects with basic information, ordered by date (newest first)

        Raises:
            EmailConnectionError: If connection to email service fails
            EmailAuthenticationError: If authentication fails
        """
        ...

    async def get_email_content(self, email_id: str) -> Email:
        """Get the full content of a specific email.

        This simple interface hides substantial complexity:
        - Fetching complete email data from servers
        - Parsing MIME structures and multipart messages
        - Decoding different character encodings
        - Handling various email formats (plain text, HTML, rich text)

        Args:
            email_id: Unique identifier for the email

        Returns:
            Email object with complete content details

        Raises:
            EmailNotFoundError: If email with given ID doesn't exist
            EmailConnectionError: If connection to email service fails
            EmailAuthenticationError: If authentication fails
        """
        ...

    async def close(self) -> None:
        """Close the email client connection and clean up resources.

        This method should be called when done with the client to ensure
        proper resource cleanup and connection closure.
        """
        ...

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager and cleanup resources."""
        ...
