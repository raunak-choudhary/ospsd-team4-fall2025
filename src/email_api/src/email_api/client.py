"""Email client API."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmailAddress:
    """Represents an email address with optional display name."""

    address: str
    name: str | None = None

    def __str__(self) -> str:
        """Return formatted email address."""
        if self.name:
            return f"{self.name} <{self.address}>"
        return self.address


@dataclass(frozen=True)
class Email:
    """Represents an email message."""

    id: str
    subject: str
    sender: EmailAddress
    recipients: list[EmailAddress]
    date_sent: datetime
    date_received: datetime
    body: str


class Client(ABC):
    """Mail client abstract base class for fetching messages."""

    @abstractmethod
    def get_messages(self, limit: int | None = None) -> Iterator[Email]:
        """Return an iterator of messages from inbox.

        Args:
            limit: Maximum number of messages to retrieve (optional)

        Raises:
            ConnectionError: If unable to connect to mail service
            RuntimeError: If authentication fails
        """
        raise NotImplementedError


def get_client() -> Client:
    """Return an instance of a Mail Client.

    This function should be replaced by implementation packages.
    Import an implementation package (e.g., gmail_impl) to inject
    the concrete implementation.

    Returns:
        Client instance from the injected implementation

    Raises:
        NotImplementedError: If no implementation has been imported
    """
    raise NotImplementedError
