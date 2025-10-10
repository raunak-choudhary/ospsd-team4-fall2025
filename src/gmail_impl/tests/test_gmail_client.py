"""Tests for GmailClient implementation.

These tests verify the public Client interface behavior when using the Gmail
implementation. Tests use mocking to avoid actual Gmail API calls.
"""

import base64
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock, Mock, patch

from googleapiclient.errors import HttpError
import pytest

import email_api
from email_api import Email

# Test Data Constants - No logic, just hardcoded data

SAMPLE_GMAIL_MESSAGE = {
    "id": "msg123",
    "payload": {
        "headers": [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "From", "value": "Sender Name <sender@example.com>"},
            {"name": "To", "value": "recipient@example.com"},
            {"name": "Date", "value": "Mon, 15 Jan 2024 10:30:00 +0000"},
        ],
        "mimeType": "text/plain",
        "body": {"data": base64.urlsafe_b64encode(b"Test email body").decode()},
    },
}

FIRST_MESSAGE_DATA = {
    "id": "msg0",
    "payload": {
        "headers": [
            {"name": "Subject", "value": "First Email"},
            {"name": "From", "value": "sender1@example.com"},
            {"name": "To", "value": "recipient@example.com"},
            {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
        ],
        "mimeType": "text/plain",
        "body": {"data": base64.urlsafe_b64encode(b"First body").decode()},
    },
}

SECOND_MESSAGE_DATA = {
    "id": "msg1",
    "payload": {
        "headers": [
            {"name": "Subject", "value": "Second Email"},
            {"name": "From", "value": "sender2@example.com"},
            {"name": "To", "value": "recipient@example.com"},
            {"name": "Date", "value": "Mon, 15 Jan 2024 11:00:00 +0000"},
        ],
        "mimeType": "text/plain",
        "body": {"data": base64.urlsafe_b64encode(b"Second body").decode()},
    },
}

THIRD_MESSAGE_DATA = {
    "id": "msg2",
    "payload": {
        "headers": [
            {"name": "Subject", "value": "Third Email"},
            {"name": "From", "value": "sender3@example.com"},
            {"name": "To", "value": "recipient@example.com"},
            {"name": "Date", "value": "Mon, 15 Jan 2024 12:00:00 +0000"},
        ],
        "mimeType": "text/plain",
        "body": {"data": base64.urlsafe_b64encode(b"Third body").decode()},
    },
}


@pytest.fixture
def mock_gmail_service() -> MagicMock:
    """Fixture providing a mock Gmail API service with common configuration."""
    service = MagicMock()
    # Default configuration for basic successful operations
    service.users().getProfile().execute.return_value = {
        "emailAddress": "test@example.com",
    }
    service.users().messages().list().execute.return_value = {"messages": []}
    return service


@pytest.fixture
def mock_authentication() -> Generator[None, None, None]:
    """Mock authentication for tests that don't need real file operations."""
    mock_creds = MagicMock()
    with patch(
        "gmail_impl.gmail_client.GmailClient._authenticate",
        return_value=mock_creds,
    ):
        yield


class TestGmailClientMessageRetrieval:
    """Test cases for retrieving messages via the public Client interface."""

    def test_get_messages_returns_empty_list_for_empty_inbox(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test retrieving messages from an empty inbox returns no messages."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [],
        }

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 0

    def test_get_messages_returns_single_email_with_correct_data(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test retrieving single email with all fields."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg123"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = (
            SAMPLE_GMAIL_MESSAGE
        )

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 1

            email = messages[0]
            assert isinstance(email, Email)
            assert email.id == "msg123"
            assert email.subject == "Test Subject"
            assert email.sender.address == "sender@example.com"
            assert email.sender.name == "Sender Name"
            assert len(email.recipients) == 1
            assert email.recipients[0].address == "recipient@example.com"
            assert email.body == "Test email body"
            assert email.date_sent == datetime(2024, 1, 15, 10, 30, tzinfo=UTC)

    def test_get_messages_returns_multiple_emails_in_order(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test retrieving multiple emails returns all messages in correct order."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg0"}, {"id": "msg1"}],
        }
        mock_gmail_service.users().messages().get().execute.side_effect = [
            FIRST_MESSAGE_DATA,
            SECOND_MESSAGE_DATA,
        ]

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 2
            assert messages[0].id == "msg0"
            assert messages[0].subject == "First Email"
            assert messages[1].id == "msg1"
            assert messages[1].subject == "Second Email"

    def test_get_messages_with_limit_returns_specified_number(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test get_messages with limit parameter returns exact count requested."""
        # Setup: 3 messages available, limit to 2
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg0"}, {"id": "msg1"}, {"id": "msg2"}],
        }
        mock_gmail_service.users().messages().get().execute.side_effect = [
            FIRST_MESSAGE_DATA,
            SECOND_MESSAGE_DATA,
            THIRD_MESSAGE_DATA,
        ]

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages(limit=2))

            assert len(messages) == 2
            assert messages[0].id == "msg0"
            assert messages[1].id == "msg1"

    def test_get_messages_with_zero_limit_returns_empty(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test get_messages with limit=0 returns no messages."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg0"}],
        }

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages(limit=0))

            assert len(messages) == 0

    def test_get_messages_returns_iterator_not_list(
        self,
        mock_gmail_service,
    ) -> None:
        """Test that get_messages returns an iterator for lazy evaluation."""
        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            result = client.get_messages()

            # Verify it's an iterator by checking for iterator protocol methods
            assert hasattr(result, "__iter__")
            assert hasattr(result, "__next__")


class TestGmailClientEmailParsing:
    """Test cases for parsing various email formats."""

    def test_get_messages_parses_email_with_multiple_recipients(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test parsing email with multiple recipients in various formats."""
        message_data = {
            "id": "msg123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Multi-recipient Test"},
                    {"name": "From", "value": "sender@example.com"},
                    {
                        "name": "To",
                        "value": "Alice <alice@example.com>, bob@example.com, "
                        "Charlie <charlie@example.com>",
                    },
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Body").decode()},
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg123"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())
            email = messages[0]

            assert len(email.recipients) == 3
            # First recipient with name
            assert email.recipients[0].address == "alice@example.com"
            assert email.recipients[0].name == "Alice"
            # Second recipient without name
            assert email.recipients[1].address == "bob@example.com"
            assert email.recipients[1].name is None
            # Third recipient with name
            assert email.recipients[2].address == "charlie@example.com"
            assert email.recipients[2].name == "Charlie"

    def test_get_messages_parses_html_email_converts_to_text(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test HTML email body is converted to plain text."""
        html_content = "<h1>Title</h1><p>This is a <b>test</b> message.</p>"
        message_data = {
            "id": "msg124",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "HTML Email"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "text/html",
                "body": {
                    "data": base64.urlsafe_b64encode(html_content.encode()).decode(),
                },
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg124"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())
            email = messages[0]

            # Verify HTML tags are removed
            assert "<h1>" not in email.body
            assert "<p>" not in email.body
            assert "<b>" not in email.body
            # Verify text content is preserved
            assert "Title" in email.body
            assert "test" in email.body

    def test_get_messages_parses_multipart_email_prefers_plain_text(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test multipart email extraction prefers plain text over HTML."""
        text_content = "Plain text version"
        html_content = "<p>HTML version</p>"

        message_data = {
            "id": "msg125",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Multipart Email"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "multipart/alternative",
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": base64.urlsafe_b64encode(
                                text_content.encode(),
                            ).decode(),
                        },
                    },
                    {
                        "mimeType": "text/html",
                        "body": {
                            "data": base64.urlsafe_b64encode(
                                html_content.encode(),
                            ).decode(),
                        },
                    },
                ],
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg125"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())
            email = messages[0]

            assert email.body == "Plain text version"

    def test_get_messages_handles_empty_body(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test email with no body content returns empty string."""
        message_data = {
            "id": "msg126",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "No Body"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": ""},
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg126"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())
            email = messages[0]

            assert email.body == ""

    def test_get_messages_handles_missing_subject_header(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test email without Subject header defaults to empty string."""
        message_data = {
            "id": "msg127",
            "payload": {
                "headers": [
                    # No Subject header
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Body").decode()},
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg127"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())
            email = messages[0]

            assert email.subject == ""


class TestGmailClientErrorHandling:
    """Test cases for error handling during email retrieval."""

    def test_get_messages_raises_runtime_error_on_401_unauthorized(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test HTTP 401 Unauthorized error raises RuntimeError."""
        mock_gmail_service.users().messages().list().execute.side_effect = HttpError(
            Mock(status=401),
            b"Unauthorized",
        )

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            with pytest.raises(RuntimeError):
                list(client.get_messages())

    def test_get_messages_raises_runtime_error_on_403_forbidden(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test HTTP 403 Forbidden error raises RuntimeError."""
        mock_gmail_service.users().messages().list().execute.side_effect = HttpError(
            Mock(status=403),
            b"Forbidden",
        )

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            with pytest.raises(RuntimeError):
                list(client.get_messages())

    def test_get_messages_raises_connection_error_on_500_server_error(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test HTTP 500 Internal Server Error raises ConnectionError."""
        mock_gmail_service.users().messages().list().execute.side_effect = HttpError(
            Mock(status=500),
            b"Internal Server Error",
        )

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            with pytest.raises(ConnectionError):
                list(client.get_messages())

    def test_get_messages_raises_connection_error_on_404_not_found(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test HTTP 404 Not Found error raises ConnectionError."""
        mock_gmail_service.users().messages().list().execute.side_effect = HttpError(
            Mock(status=404),
            b"Not Found",
        )

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            with pytest.raises(ConnectionError):
                list(client.get_messages())

    def test_get_messages_handles_pagination(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test get_messages correctly handles pagination."""
        # First page with nextPageToken
        mock_gmail_service.users().messages().list().execute.side_effect = [
            {
                "messages": [{"id": "msg0"}],
                "nextPageToken": "token123",
            },
            {
                "messages": [{"id": "msg1"}],
            },
        ]
        mock_gmail_service.users().messages().get().execute.side_effect = [
            FIRST_MESSAGE_DATA,
            SECOND_MESSAGE_DATA,
        ]

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 2

    def test_get_messages_skips_malformed_messages(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test get_messages skips messages that fail to parse."""
        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg0"}, {"id": "msg1"}],
        }
        # First message has malformed data (missing id key), second is valid
        mock_gmail_service.users().messages().get().execute.side_effect = [
            {"payload": {}},  # Missing "id" key - will raise KeyError in _parse_message
            FIRST_MESSAGE_DATA,
        ]

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            # Should only get the valid message
            assert len(messages) == 1
            assert messages[0].id == "msg0"

    def test_get_messages_raises_connection_error_on_generic_exception(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test non-HttpError exceptions raise ConnectionError."""
        mock_gmail_service.users().messages().list().execute.side_effect = Exception(
            "Network error",
        )

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            with pytest.raises(ConnectionError):
                list(client.get_messages())

    def test_parse_message_handles_empty_date(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test parsing message with empty date defaults to epoch."""
        message_data = {
            "id": "msg128",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": ""},  # Empty date
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Body").decode()},
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg128"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 1
            # Should default to epoch time
            assert messages[0].date_sent == datetime.fromtimestamp(0, tz=UTC)

    def test_parse_message_handles_invalid_date(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test parsing message with invalid date format defaults to epoch."""
        message_data = {
            "id": "msg129",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "not a valid date"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Body").decode()},
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg129"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 1
            # Should default to epoch time
            assert messages[0].date_sent == datetime.fromtimestamp(0, tz=UTC)

    def test_parse_message_handles_empty_html(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test parsing message with empty HTML body."""
        message_data = {
            "id": "msg130",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "text/html",
                "body": {"data": ""},  # Empty HTML
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg130"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 1
            assert messages[0].body == ""

    def test_parse_email_addresses_handles_empty_string(
        self,
        mock_gmail_service,
        mock_authentication,
    ) -> None:
        """Test parsing empty email address string."""
        message_data = {
            "id": "msg131",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "   "},  # Empty/whitespace only
                    {"name": "Date", "value": "Mon, 15 Jan 2024 10:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Body").decode()},
            },
        }

        mock_gmail_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg131"}],
        }
        mock_gmail_service.users().messages().get().execute.return_value = message_data

        with (
            patch(
                "gmail_impl.gmail_client.build",
                return_value=mock_gmail_service,
            ),
            patch("gmail_impl.gmail_client.Credentials"),
        ):
            client = email_api.get_client()
            messages = list(client.get_messages())

            assert len(messages) == 1
            assert len(messages[0].recipients) == 0
