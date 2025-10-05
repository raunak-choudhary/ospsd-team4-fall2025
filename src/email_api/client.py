"""Email client API."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable

# ==========================
# Data Models
# ==========================

@dataclass(frozen=True)
class EmailAddress:
    """Represents an email address with optional display name."""

    address: str
    name: Optional[str] = None

    def __str__(self) -> str:
        """Return formatted email address."""
        return f"{self.name} <{self.address}>" if self.name else self.address


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


# ==========================
# Abstract Client Interface
# ==========================

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


# ==========================
# Dependency Injection API
# ==========================

_factory: Optional[Callable[[], Client]] = None


def register_client_factory(factory: Callable[[], Client]) -> None:
    """Registers a factory function to create Client instances dynamically.

    Example:
        >>> from gmail_impl import GmailClient
        >>> register_client_factory(lambda: GmailClient())
    """
    global _factory
    _factory = factory


def get_client() -> Client:
    """Return an instance of a Mail Client.

    Returns:
        Client: Instance from the registered factory.

    Raises:
        RuntimeError: If no factory has been registered.
    """
    if _factory is None:
        raise RuntimeError(
            "No email client factory registered. "
            "Call register_client_factory() from an implementation (e.g. gmail_impl)."
        )
    return _factory()
