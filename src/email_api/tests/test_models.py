"""
Unit tests for email data models.

These tests verify the data model implementations including validation,
serialization, and the business logic in model methods.
"""

from datetime import UTC, datetime

import pytest

from email_api import Email, EmailAddress


class TestEmailAddress:
    """Test EmailAddress data model."""

    def test_email_address_without_name(self) -> None:
        """Test EmailAddress with just an address."""
        addr = EmailAddress(address="test@example.com")

        assert addr.address == "test@example.com"
        assert addr.name is None
        assert str(addr) == "test@example.com"

    def test_email_address_with_name(self) -> None:
        """Test EmailAddress with both address and name."""
        addr = EmailAddress(address="test@example.com", name="John Doe")

        assert addr.address == "test@example.com"
        assert addr.name == "John Doe"
        assert str(addr) == "John Doe <test@example.com>"

    def test_email_address_immutable(self) -> None:
        """Test that EmailAddress is immutable (frozen dataclass)."""
        addr = EmailAddress(address="test@example.com")

        with pytest.raises(AttributeError):
            addr.address = "new@example.com"  # type: ignore[misc]


class TestEmail:
    """Test Email data model."""

    def test_email_creation(self) -> None:
        """Test basic Email creation with required fields."""
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
            body_text="Hello World",
            body_html="<p>Hello World</p>",
        )

        assert email.id == "email123"
        assert email.subject == "Test Subject"
        assert email.sender == sender
        assert email.recipients == [recipient]
        assert email.date_sent == sent_time
        assert email.date_received == received_time
        assert email.body_text == "Hello World"
        assert email.body_html == "<p>Hello World</p>"

    def test_email_with_none_content(self) -> None:
        """Test Email with None content fields."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")

        email = Email(
            id="email123",
            subject="Test Subject",
            sender=sender,
            recipients=[recipient],
            date_sent=datetime.now(UTC),
            date_received=datetime.now(UTC),
            body_text=None,
            body_html=None,
        )

        assert email.body_text is None
        assert email.body_html is None
        assert not email.has_text_content
        assert not email.has_html_content

    def test_has_text_content_property(self) -> None:
        """Test has_text_content property logic."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")
        base_time = datetime.now(UTC)

        # Email with text content
        email_with_text = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text="Hello World",
            body_html=None,
        )
        assert email_with_text.has_text_content

        # Email with empty text
        email_empty_text = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text="",
            body_html=None,
        )
        assert not email_empty_text.has_text_content

        # Email with whitespace only
        email_whitespace = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text="   \n\t  ",
            body_html=None,
        )
        assert not email_whitespace.has_text_content

        # Email with None text
        email_none_text = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html=None,
        )
        assert not email_none_text.has_text_content

    def test_has_html_content_property(self) -> None:
        """Test has_html_content property logic."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")
        base_time = datetime.now(UTC)

        # Email with HTML content
        email_with_html = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html="<p>Hello</p>",
        )
        assert email_with_html.has_html_content

        # Email with empty HTML
        email_empty_html = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html="",
        )
        assert not email_empty_html.has_html_content

        # Email with whitespace only HTML
        email_whitespace_html = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html="   \n\t  ",
        )
        assert not email_whitespace_html.has_html_content

        # Email with None HTML
        email_none_html = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html=None,
        )
        assert not email_none_html.has_html_content

    def test_email_content_methods(self) -> None:
        """Test the content helper methods."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")
        base_time = datetime.now(UTC)

        # Email with both text and HTML content
        email_both = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text="Hello World",
            body_html="<p>Hello HTML</p>",
        )
        assert email_both.has_content
        assert email_both.get_content() == "Hello World"  # Prefers text

        # Email with only HTML content
        email_html = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html="<p>Hello HTML</p>",
        )
        assert email_html.has_content
        assert email_html.get_content() == "<p>Hello HTML</p>"

        # Email with no content
        email_empty = Email(
            id="email123",
            subject="Test",
            sender=sender,
            recipients=[recipient],
            date_sent=base_time,
            date_received=base_time,
            body_text=None,
            body_html=None,
        )
        assert not email_empty.has_content
        assert email_empty.get_content() == ""
        """Test Email with multiple recipients."""
        sender = EmailAddress("sender@example.com")
        recipients = [
            EmailAddress("recipient1@example.com", "Recipient One"),
            EmailAddress("recipient2@example.com", "Recipient Two"),
            EmailAddress("recipient3@example.com"),
        ]

        email = Email(
            id="email123",
            subject="Test Subject",
            sender=sender,
            recipients=recipients,
            date_sent=datetime.now(UTC),
            date_received=datetime.now(UTC),
            body_text="Hello Everyone",
            body_html=None,
        )

        expected_recipients = 3
        assert len(email.recipients) == expected_recipients
        assert email.recipients[0].name == "Recipient One"
        assert email.recipients[1].name == "Recipient Two"
        assert email.recipients[2].name is None

    def test_email_immutable(self) -> None:
        """Test that Email is immutable (frozen dataclass)."""
        sender = EmailAddress("sender@example.com")
        recipient = EmailAddress("recipient@example.com")

        email = Email(
            id="email123",
            subject="Test Subject",
            sender=sender,
            recipients=[recipient],
            date_sent=datetime.now(UTC),
            date_received=datetime.now(UTC),
            body_text="Hello World",
            body_html=None,
        )

        with pytest.raises(AttributeError):
            email.subject = "New Subject"  # type: ignore[misc]
