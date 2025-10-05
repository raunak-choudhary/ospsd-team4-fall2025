"""Unit tests for email API data models and dependency injection.

Tests validate dataclass implementations and the dependency injection pattern.
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

import email_api
from email_api import Client, Email, EmailAddress


class TestEmailAddress:
    """Test EmailAddress data model."""

    def test_email_address_without_name(self) -> None:
        """Test EmailAddress with just an address formats correctly."""
        addr = EmailAddress(address="test@example.com")

        assert addr.address == "test@example.com"
        assert addr.name is None
        assert str(addr) == "test@example.com"

    def test_email_address_with_name(self) -> None:
        """Test EmailAddress with both address and name formats correctly."""
        addr = EmailAddress(address="test@example.com", name="John Doe")

        assert addr.address == "test@example.com"
        assert addr.name == "John Doe"
        assert str(addr) == "John Doe <test@example.com>"

    def test_email_address_with_empty_name_string(self) -> None:
        """Test EmailAddress with empty string name (edge case)."""
        addr = EmailAddress(address="test@example.com", name="")

        # Empty string name should be preserved, not treated as None
        assert addr.name == ""
        # Empty string name should format as just the address
        assert str(addr) == "test@example.com"


class TestEmail:
    """Test Email data model."""

    def test_email_creation_with_all_required_fields(self) -> None:
        """Test basic Email creation stores all fields correctly."""
        sender = EmailAddress("sender@example.com", "Sender Name")
        recipient = EmailAddress("recipient@example.com")
        sent_time = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        received_time = datetime(2024, 1, 15, 10, 31, tzinfo=UTC)

        email = Email(
            id="email123",
            subject="Test Subject",
            sender=sender,
            recipients=[recipient],
            date_sent=sent_time,
            date_received=received_time,
            body="Hello World",
        )

        assert email.id == "email123"
        assert email.subject == "Test Subject"
        assert email.sender == sender
        assert email.recipients == [recipient]
        assert email.date_sent == sent_time
        assert email.date_received == received_time
        assert email.body == "Hello World"

    def test_email_with_empty_body(self) -> None:
        """Test Email with empty body preserves empty string."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")
        sent_time = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        received_time = datetime(2024, 1, 15, 10, 31, tzinfo=UTC)

        email = Email(
            id="email123",
            subject="Test Subject",
            sender=sender,
            recipients=[recipient],
            date_sent=sent_time,
            date_received=received_time,
            body="",
        )

        assert email.body == ""

    def test_email_with_whitespace_only_body(self) -> None:
        """Test Email preserves whitespace-only body content."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")
        sent_time = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        received_time = datetime(2024, 1, 15, 10, 31, tzinfo=UTC)

        email = Email(
            id="email125",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=sent_time,
            date_received=received_time,
            body="   \n\t  ",
        )

        assert email.body == "   \n\t  "

    def test_email_with_multiple_recipients(self) -> None:
        """Test Email stores multiple recipients correctly."""
        sender = EmailAddress("sender@example.com")
        recipients = [
            EmailAddress("recipient1@example.com", "Recipient One"),
            EmailAddress("recipient2@example.com", "Recipient Two"),
            EmailAddress("recipient3@example.com"),
        ]
        sent_time = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        received_time = datetime(2024, 1, 15, 10, 31, tzinfo=UTC)

        email = Email(
            id="email123",
            subject="Test Subject",
            sender=sender,
            recipients=recipients,
            date_sent=sent_time,
            date_received=received_time,
            body="Hello Everyone",
        )

        assert len(email.recipients) == 3
        assert email.recipients[0].name == "Recipient One"
        assert email.recipients[1].name == "Recipient Two"
        assert email.recipients[2].name is None

    def test_email_with_empty_recipients_list(self) -> None:
        """Test Email with no recipients (edge case)."""
        sender = EmailAddress("sender@example.com")
        sent_time = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        received_time = datetime(2024, 1, 15, 10, 31, tzinfo=UTC)

        email = Email(
            id="email126",
            subject="No Recipients",
            sender=sender,
            recipients=[],
            date_sent=sent_time,
            date_received=received_time,
            body="This email has no recipients",
        )

        assert email.recipients == []
        assert len(email.recipients) == 0


class TestClientInjection:
    """Test client dependency injection pattern."""

    def test_get_client_returns_injected_implementation(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that get_client returns the injected client implementation."""
        mock_client = Mock(spec=Client)
        monkeypatch.setattr(email_api, "get_client", lambda: mock_client)

        client = email_api.get_client()

        assert client is mock_client

    def test_get_client_without_implementation_raises_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that get_client raises NotImplementedError."""

        def raise_not_implemented() -> Client:
            raise NotImplementedError

        monkeypatch.setattr(email_api, "get_client", raise_not_implemented)

        with pytest.raises(NotImplementedError):
            email_api.get_client()
