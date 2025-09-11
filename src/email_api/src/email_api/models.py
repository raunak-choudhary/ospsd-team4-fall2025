"""Email data models and types.

This module defines the core data structures used in the email interface,
providing a clean contract for basic email operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime  # noqa: TC003  # Required at runtime for dataclass fields


@dataclass(frozen=True)
class EmailAddress:
    """Represents an email address with optional display name.

    Attributes:
        address: The email address (e.g., "user@example.com")
        name: Optional display name (e.g., "John Doe")
    """
    address: str
    name: str | None = None

    def __str__(self) -> str:
        """Return formatted email address."""
        if self.name:
            return f"{self.name} <{self.address}>"
        return self.address


@dataclass(frozen=True)
class Email:
    """Represents an email message with essential information.

    This provides a clean, simple interface to email data while hiding
    the complexity of different email formats and protocols underneath.
    """
    id: str
    subject: str
    sender: EmailAddress
    recipients: list[EmailAddress]
    date_sent: datetime
    date_received: datetime
    body_text: str | None
    body_html: str | None

    @property
    def has_content(self) -> bool:
        """Check if email has any readable content."""
        return self.has_text_content or self.has_html_content

    @property
    def has_text_content(self) -> bool:
        """Check if email has text content."""
        return self.body_text is not None and len(self.body_text.strip()) > 0

    @property
    def has_html_content(self) -> bool:
        """Check if email has HTML content."""
        return self.body_html is not None and len(self.body_html.strip()) > 0

    def get_content(self) -> str:
        """Get the best available content representation.

        Returns text content if available, otherwise HTML content,
        or empty string if no content exists.
        """
        if self.has_text_content:
            return self.body_text or ""
        if self.has_html_content:
            return self.body_html or ""
        return ""
