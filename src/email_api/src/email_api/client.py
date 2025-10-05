"""Email client API."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ============================
# Data Models
# ============================

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


# ============================
# Abstract Client
# ============================

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


# ============================
# Dummy Client (Fallback)
# ============================

class DummyClient(Client):
    """Fallback client used when no real implementation is injected."""

    def get_messages(self, limit: int | None = None) -> Iterator[Email]:
        """Return an empty iterator."""
        return iter([])


# ============================
# Client Factory / Registration
# ============================

_client_factory: Optional[type[Client]] = None


def register_client_factory(factory: type[Client]) -> None:
    """Allow implementations (like gmail_impl) to register their client."""
    global _client_factory
    _client_factory = factory


def get_client() -> Client:
    """Return an instance of the registered mail client.

    If no implementation package has registered a client, return DummyClient.
    """
    if _client_factory is not None:
        return _client_factory()  # type: ignore[call-arg]
    return DummyClient()
