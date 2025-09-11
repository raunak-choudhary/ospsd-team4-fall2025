"""
Unit tests for email API interfaces.

These tests verify the protocol contracts by testing against mock implementations.
They ensure that the interfaces work correctly with dependency injection patterns.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from email_api import Email, EmailAddress, EmailClient


class TestEmailClientProtocol:
    """Test EmailClient protocol using mock implementations."""

    @pytest.fixture
    def mock_email_client(self) -> AsyncMock:
        """Create a mock email client that implements the EmailClient protocol."""
        return AsyncMock(spec=EmailClient)

    @pytest.fixture
    def sample_email(self) -> Email:
        """Create a sample email for testing."""
        return Email(
            id="test123",
            subject="Test Email",
            sender=EmailAddress("sender@example.com", "Test Sender"),
            recipients=[EmailAddress("recipient@example.com", "Test Recipient")],
            date_sent=datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
            date_received=datetime(2024, 1, 15, 10, 31, tzinfo=UTC),
            body_text="Hello World",
            body_html="<p>Hello World</p>",
        )

    @pytest.fixture
    def html_only_email(self) -> Email:
        """Create an email with only HTML content."""
        return Email(
            id="html123",
            subject="HTML Email",
            sender=EmailAddress("sender@example.com"),
            recipients=[EmailAddress("recipient@example.com")],
            date_sent=datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
            date_received=datetime(2024, 1, 15, 10, 31, tzinfo=UTC),
            body_text=None,
            body_html="<h1>HTML Only</h1><p>Rich content here</p>",
        )

    @pytest.fixture
    def empty_email(self) -> Email:
        """Create an email with no content."""
        return Email(
            id="empty123",
            subject="Empty Email",
            sender=EmailAddress("sender@example.com"),
            recipients=[EmailAddress("recipient@example.com")],
            date_sent=datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
            date_received=datetime(2024, 1, 15, 10, 31, tzinfo=UTC),
            body_text=None,
            body_html=None,
        )

    @pytest.mark.asyncio
    async def test_list_inbox_messages_protocol(
        self,
        mock_email_client: AsyncMock,
        sample_email: Email,
    ) -> None:
        """Test that list_inbox_messages follows the protocol contract."""
        # Setup mock response
        mock_email_client.list_inbox_messages.return_value = [sample_email]

        # Call the method
        result = await mock_email_client.list_inbox_messages(limit=10)

        # Verify the protocol contract
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Email)
        assert result[0].id == "test123"

        # Verify the method was called with correct parameters
        mock_email_client.list_inbox_messages.assert_called_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_list_inbox_messages_default_parameters(
        self,
        mock_email_client: AsyncMock,
        sample_email: Email,
    ) -> None:
        """Test list_inbox_messages with default parameters."""
        mock_email_client.list_inbox_messages.return_value = [sample_email]

        # Call without parameters to test defaults
        result = await mock_email_client.list_inbox_messages()

        assert len(result) == 1
        # Should be called with default limit=10 according to protocol
        mock_email_client.list_inbox_messages.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_get_email_content_protocol(
        self,
        mock_email_client: AsyncMock,
        sample_email: Email,
    ) -> None:
        """Test that get_email_content follows the protocol contract."""
        # Setup mock response
        mock_email_client.get_email_content.return_value = sample_email

        # Call the method
        result = await mock_email_client.get_email_content("test123")

        # Verify the protocol contract
        assert isinstance(result, Email)
        assert result.id == "test123"
        assert result.subject == "Test Email"

        # Verify the method was called with correct parameters
        mock_email_client.get_email_content.assert_called_once_with("test123")

    @pytest.mark.asyncio
    async def test_close_protocol(self, mock_email_client: AsyncMock) -> None:
        """Test that close follows the protocol contract."""
        # Setup mock (close should return None)
        mock_email_client.close.return_value = None

        # Call the method
        result = await mock_email_client.close()

        # Verify the protocol contract
        assert result is None
        mock_email_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_protocol(
        self,
        mock_email_client: AsyncMock,
    ) -> None:
        """Test that the async context manager protocol works correctly."""
        # Setup mock context manager
        mock_email_client.__aenter__.return_value = mock_email_client
        mock_email_client.__aexit__.return_value = None

        # Use as context manager
        async with mock_email_client as client:
            assert client is mock_email_client

        # Verify context manager methods were called
        mock_email_client.__aenter__.assert_called_once()
        mock_email_client.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_inbox_list(self, mock_email_client: AsyncMock) -> None:
        """Test handling of empty inbox."""
        # Setup mock to return empty list
        mock_email_client.list_inbox_messages.return_value = []

        # Call the method
        result = await mock_email_client.list_inbox_messages(limit=5)

        # Verify empty list is handled correctly
        assert isinstance(result, list)
        assert len(result) == 0
        mock_email_client.list_inbox_messages.assert_called_once_with(limit=5)

    @pytest.mark.asyncio
    async def test_multiple_emails_list(
        self,
        mock_email_client: AsyncMock,
        sample_email: Email,
    ) -> None:
        """Test handling of multiple emails in inbox."""
        # Create multiple sample emails
        email2 = Email(
            id="test456",
            subject="Second Email",
            sender=EmailAddress("sender2@example.com"),
            recipients=[EmailAddress("recipient@example.com")],
            date_sent=datetime(2024, 1, 15, 11, 30, tzinfo=UTC),
            date_received=datetime(2024, 1, 15, 11, 31, tzinfo=UTC),
            body_text="Second message",
            body_html=None,
        )

        # Setup mock to return multiple emails
        mock_email_client.list_inbox_messages.return_value = [sample_email, email2]

        # Call the method
        result = await mock_email_client.list_inbox_messages(limit=2)

        # Verify multiple emails are handled correctly
        expected_count = 2
        assert isinstance(result, list)
        assert len(result) == expected_count
        assert all(isinstance(email, Email) for email in result)
        assert result[0].id == "test123"
        assert result[1].id == "test456"

    def test_protocol_type_checking(self) -> None:
        """Test that protocol allows for proper type checking."""
        # This test verifies that the protocol can be used for type hints
        def process_emails(client: EmailClient) -> str:
            """Example function that accepts EmailClient protocol."""
            return f"Processing emails with {type(client).__name__}"

        # Create a mock that conforms to the protocol
        mock_client = AsyncMock(spec=EmailClient)

        # This should work without type errors
        result = process_emails(mock_client)
        assert "AsyncMock" in result

    @pytest.mark.asyncio
    async def test_email_content_handling_in_protocol(
        self,
        mock_email_client: AsyncMock,
    ) -> None:
        """Test that the protocol properly handles different email content types."""
        # Test with different email content types
        text_email = Email(
            id="text123",
            subject="Text Email",
            sender=EmailAddress("sender@example.com"),
            recipients=[EmailAddress("recipient@example.com")],
            date_sent=datetime.now(UTC),
            date_received=datetime.now(UTC),
            body_text="Plain text content",
            body_html=None,
        )

        html_email = Email(
            id="html123",
            subject="HTML Email",
            sender=EmailAddress("sender@example.com"),
            recipients=[EmailAddress("recipient@example.com")],
            date_sent=datetime.now(UTC),
            date_received=datetime.now(UTC),
            body_text=None,
            body_html="<p>HTML content</p>",
        )

        # Setup mocks for different content types
        mock_email_client.get_email_content.side_effect = [text_email, html_email]

        # Test text email
        result1 = await mock_email_client.get_email_content("text123")
        assert result1.has_text_content
        assert not result1.has_html_content
        assert result1.has_content
        assert result1.get_content() == "Plain text content"

        # Test HTML email
        result2 = await mock_email_client.get_email_content("html123")
        assert not result2.has_text_content
        assert result2.has_html_content
        assert result2.has_content
        assert result2.get_content() == "<p>HTML content</p>"

        # Verify both calls were made
        expected_calls = 2
        assert mock_email_client.get_email_content.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_dependency_injection_pattern(
        self,
        mock_email_client: AsyncMock,
        sample_email: Email,
    ) -> None:
        """Test the dependency injection pattern that the protocol enables."""

        class EmailProcessor:
            """Example class that uses dependency injection with EmailClient."""

            def __init__(self, client: EmailClient) -> None:
                self.client = client

            async def get_first_email_content(self) -> str:
                """Get the content of the first email."""
                emails = await self.client.list_inbox_messages(limit=1)
                if not emails:
                    return "No emails found"

                full_email = await self.client.get_email_content(emails[0].id)
                return full_email.get_content()  # Uses smart content selection

        # Setup mock - return sample_email for both list and get_content
        mock_email_client.list_inbox_messages.return_value = [sample_email]
        mock_email_client.get_email_content.return_value = sample_email

        # Create processor with injected dependency
        processor = EmailProcessor(mock_email_client)

        # Test the functionality
        content = await processor.get_first_email_content()

        assert content == "Hello World"  # Should get text content (preferred over HTML)
        mock_email_client.list_inbox_messages.assert_called_once_with(limit=1)
        mock_email_client.get_email_content.assert_called_once_with("test123")
