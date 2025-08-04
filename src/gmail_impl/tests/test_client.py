"""Tests for GmailClient implementation."""

import base64
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from googleapiclient.errors import HttpError

from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailNotFoundError,
)
from email_api.models import Email, EmailAddress
from gmail_impl.client import GmailClient
from gmail_impl.config import GmailConfig


class TestGmailClient:
    """Test cases for GmailClient class."""

    @pytest.fixture
    def mock_config(self) -> MagicMock:
        """Create a mock Gmail config."""
        return MagicMock(spec=GmailConfig)

    @pytest.fixture
    def mock_service(self) -> MagicMock:
        """Create a mock Gmail API service."""
        return MagicMock()

    @pytest.fixture
    def client(self, mock_config: MagicMock) -> GmailClient:
        """Create a GmailClient instance with mock config."""
        return GmailClient(mock_config)

    def test_init(self, mock_config: MagicMock) -> None:
        """Test GmailClient initialization."""
        client = GmailClient(mock_config)

        assert client._config == mock_config
        assert client._service is None

    @pytest.mark.asyncio
    async def test_context_manager_enter(
        self, client: GmailClient, mock_config: MagicMock,
    ) -> None:
        """Test async context manager entry."""
        mock_service = MagicMock()
        mock_config.get_gmail_service.return_value = mock_service

        result = await client.__aenter__()

        assert result == client
        assert client._service == mock_service
        mock_config.get_gmail_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exit(self, client: GmailClient) -> None:
        """Test async context manager exit."""
        client._service = MagicMock()

        await client.__aexit__(None, None, None)

        assert client._service is None

    @pytest.mark.asyncio
    async def test_close(self, client: GmailClient) -> None:
        """Test client close method."""
        client._service = MagicMock()

        await client.close()

        assert client._service is None

    @pytest.mark.asyncio
    async def test_list_inbox_messages_not_connected(
        self, client: GmailClient,
    ) -> None:
        """Test listing messages when not connected."""
        with pytest.raises(EmailConnectionError) as exc_info:
            await client.list_inbox_messages()

        assert exc_info.value.error_code == "CLIENT_NOT_CONNECTED"

    @pytest.mark.asyncio
    async def test_list_inbox_messages_success(
        self, client: GmailClient, mock_service: MagicMock,
    ) -> None:
        """Test successful inbox message listing."""
        # Mock the chain of calls properly
        mock_users = MagicMock()
        mock_messages = MagicMock()
        mock_list = MagicMock()

        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {
            "messages": [
                {"id": "msg1"},
                {"id": "msg2"},
            ],
        }

        # Set the service
        client._service = mock_service

        # Create a mock Email for the parse method to return
        mock_email = Email(
            id="msg1",
            subject="Test Subject",
            sender=EmailAddress(address="test@example.com"),
            recipients=[EmailAddress(address="recipient@example.com")],
            date_sent=datetime.now(tz=UTC),
            date_received=datetime.now(tz=UTC),
            body_text=None,
            body_html=None,
        )

        # Use patch to mock the _parse_gmail_message method
        mock_parse_patch = patch.object(
            client, "_parse_gmail_message", return_value=mock_email,
        )
        with mock_parse_patch:
            emails = await client.list_inbox_messages(limit=2)

            assert len(emails) == 2
            assert emails[0].subject == "Test Subject"

        # Verify the chained calls - users() is called once for list + twice for get
        assert mock_service.users.call_count == 3  # 1 for list, 2 for gets
        assert mock_users.messages.call_count == 3  # 1 for list, 2 for gets
        mock_messages.list.assert_called_once_with(
            userId="me", labelIds=["INBOX"], maxResults=2,
        )

    @pytest.mark.asyncio
    async def test_list_inbox_messages_empty_inbox(
        self, client: GmailClient, mock_service: MagicMock,
    ) -> None:
        """Test listing messages from empty inbox."""
        mock_service.users().messages().list().execute.return_value = {
            "messages": [],
        }
        client._service = mock_service

        emails = await client.list_inbox_messages()

        assert len(emails) == 0

    @pytest.mark.asyncio
    async def test_list_inbox_messages_http_error(
        self, client: GmailClient, mock_service: MagicMock,
    ) -> None:
        """Test handling HTTP error during message listing."""
        error = HttpError(MagicMock(status=403), b"Forbidden")
        mock_service.users().messages().list().execute.side_effect = error
        client._service = mock_service

        with pytest.raises(EmailAuthenticationError):
            await client.list_inbox_messages()

    @pytest.mark.asyncio
    async def test_get_email_content_not_connected(
        self, client: GmailClient,
    ) -> None:
        """Test getting email content when not connected."""
        with pytest.raises(EmailConnectionError) as exc_info:
            await client.get_email_content("test_id")

        assert exc_info.value.error_code == "CLIENT_NOT_CONNECTED"

    @pytest.mark.asyncio
    async def test_get_email_content_success(
        self, client: GmailClient, mock_service: MagicMock,
    ) -> None:
        """Test successful email content retrieval."""
        mock_message = {
            "id": "test_id",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Wed, 15 Mar 2023 10:30:00 +0000"},
                ],
            },
            "internalDate": "1678877400000",
        }

        mock_service.users().messages().get().execute.return_value = mock_message
        client._service = mock_service

        email = await client.get_email_content("test_id")

        assert email.id == "test_id"
        assert email.subject == "Test Subject"

    @pytest.mark.asyncio
    async def test_get_email_content_not_found(
        self, client: GmailClient, mock_service: MagicMock,
    ) -> None:
        """Test getting non-existent email content."""
        error = HttpError(MagicMock(status=404), b"Not Found")
        mock_service.users().messages().get().execute.side_effect = error
        client._service = mock_service

        with pytest.raises(EmailNotFoundError) as exc_info:
            await client.get_email_content("nonexistent_id")

        assert exc_info.value.error_code == "EMAIL_NOT_FOUND"

    def _parse_email_address(self, address_str: str) -> EmailAddress | None:
        """Helper method for single address parsing (for tests)."""
        # This method is not used anymore - keeping for reference
        return None

    def test_parse_email_address_with_name(self, client: GmailClient) -> None:
        """Test parsing email address with name."""
        # Test the actual method on the client
        addresses = client._parse_email_addresses("John Doe <john@example.com>")
        address = addresses[0] if addresses else None

        assert address is not None
        assert address.address == "john@example.com"
        assert address.name == "John Doe"

    def test_parse_email_address_without_name(self, client: GmailClient) -> None:
        """Test parsing email address without name."""
        addresses = client._parse_email_addresses("john@example.com")
        address = addresses[0] if addresses else None

        assert address is not None
        assert address.address == "john@example.com"
        assert address.name is None

    def test_parse_email_address_empty(self, client: GmailClient) -> None:
        """Test parsing empty email address."""
        addresses = client._parse_email_addresses("")

        assert len(addresses) == 0

    def test_parse_email_addresses_multiple(self, client: GmailClient) -> None:
        """Test parsing multiple email addresses."""
        addresses = client._parse_email_addresses(
            "John Doe <john@example.com>, jane@example.com, "
            "Bob Smith <bob@example.com>",
        )

        assert len(addresses) == 3
        assert addresses[0].address == "john@example.com"
        assert addresses[0].name == "John Doe"
        assert addresses[1].address == "jane@example.com"
        assert addresses[1].name is None
        assert addresses[2].address == "bob@example.com"
        assert addresses[2].name == "Bob Smith"

    def test_parse_email_addresses_empty(self, client: GmailClient) -> None:
        """Test parsing empty email addresses string."""
        addresses = client._parse_email_addresses("")

        assert addresses == []

    def test_parse_date_valid(self, client: GmailClient) -> None:
        """Test parsing valid date string."""
        date_str = "Wed, 15 Mar 2023 10:30:00 +0000"
        date = client._parse_date(date_str)

        assert date.year == 2023
        assert date.month == 3
        assert date.day == 15

    def test_parse_date_invalid(self, client: GmailClient) -> None:
        """Test parsing invalid date string."""
        date = client._parse_date("invalid date")

        assert date == datetime.fromtimestamp(0, tz=UTC)

    def test_parse_date_empty(self, client: GmailClient) -> None:
        """Test parsing empty date string."""
        date = client._parse_date("")

        assert date == datetime.fromtimestamp(0, tz=UTC)

    def test_decode_body_data_valid(self, client: GmailClient) -> None:
        """Test decoding valid base64url data."""
        text = "Hello, World!"
        # Properly encode as base64url
        encoded = base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")
        result = client._decode_body_data(encoded)

        assert result == text

    def test_decode_body_data_no_data(self, client: GmailClient) -> None:
        """Test decoding empty body data."""
        result = client._decode_body_data("")

        # Empty string returns empty string, not None
        assert result == ""

    def test_decode_body_data_invalid(self, client: GmailClient) -> None:
        """Test decoding invalid base64url data."""
        result = client._decode_body_data("invalid_base64")

        assert result is None

    def test_extract_message_content_text_only(self, client: GmailClient) -> None:
        """Test extracting text-only content."""
        payload = {
            "mimeType": "text/plain",
            "body": {"data": base64.urlsafe_b64encode(b"Hello World").decode()},
        }

        text, html = client._extract_message_content(payload)
        assert text == "Hello World"
        assert html is None

    def test_extract_message_content_multipart(self, client: GmailClient) -> None:
        """Test extracting multipart content."""
        text_data = base64.urlsafe_b64encode(b"Text content").decode()
        html_data = base64.urlsafe_b64encode(b"<p>HTML content</p>").decode()

        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": text_data},
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": html_data},
                },
            ],
        }

        text, html = client._extract_message_content(payload)
        assert text == "Text content"
        assert html == "<p>HTML content</p>"

    def test_handle_http_error_401(self, client: GmailClient) -> None:
        """Test handling 401 HTTP error."""
        error = HttpError(MagicMock(status=401), b"Unauthorized")

        with pytest.raises(EmailAuthenticationError) as exc_info:
            client._handle_http_error(error, "test operation")

        assert exc_info.value.error_code == "GMAIL_AUTH_EXPIRED"

    def test_handle_http_error_403(self, client: GmailClient) -> None:
        """Test handling 403 HTTP error."""
        error = HttpError(MagicMock(status=403), b"Forbidden")

        with pytest.raises(EmailAuthenticationError) as exc_info:
            client._handle_http_error(error, "test operation")

        assert exc_info.value.error_code == "GMAIL_FORBIDDEN"

    def test_handle_http_error_other(self, client: GmailClient) -> None:
        """Test handling other HTTP errors."""
        error = HttpError(MagicMock(status=500), b"Internal Server Error")

        with pytest.raises(EmailConnectionError) as exc_info:
            client._handle_http_error(error, "test operation")

        assert exc_info.value.error_code == "GMAIL_HTTP_500"

    @pytest.mark.asyncio
    async def test_parse_gmail_message_basic(self, client: GmailClient) -> None:
        """Test parsing basic Gmail message data."""
        message_data = {
            "id": "test_id",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "Mon, 1 Jan 2024 10:00:00 +0000"},
                ],
            },
        }

        email = client._parse_gmail_message(message_data, include_body=False)

        assert email.id == "test_id"
        assert email.subject == "Test Subject"
        assert email.sender.address == "sender@example.com"
        assert len(email.recipients) == 1
        assert email.recipients[0].address == "recipient@example.com"

    @pytest.mark.asyncio
    async def test_parse_gmail_message_with_body(self, client: GmailClient) -> None:
        """Test parsing Gmail message with body content."""
        message_data = {
            "id": "test_id",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Test content").decode()},
            },
        }

        email = client._parse_gmail_message(message_data, include_body=True)

        assert email.body_text == "Test content"
        assert email.body_html is None
