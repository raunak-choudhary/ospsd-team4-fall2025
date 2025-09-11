"""Gmail client implementation of the EmailClient protocol."""

from __future__ import annotations

import base64
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from types import TracebackType

from googleapiclient.errors import HttpError

from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailNotFoundError,
)
from email_api.interfaces import EmailClient
from email_api.models import Email, EmailAddress

if TYPE_CHECKING:
    from .config import GmailConfig

# HTTP status code constants
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_BAD_REQUEST = 400


class GmailClient(EmailClient):
    """Gmail implementation of the EmailClient protocol.

    This client provides Gmail API access through OAuth2 authentication,
    implementing the EmailClient protocol for inbox operations and email
    content retrieval.

    The client uses dependency injection - the Gmail API service is provided
    by the GmailConfig during context manager entry, not created internally.

    Example:
        config = GmailConfig("credentials.json", "token.json")
        async with GmailClient(config) as client:
            emails = await client.list_inbox_messages(limit=10)
            content = await client.get_email_content(emails[0].id)
    """

    def __init__(self, config: GmailConfig) -> None:
        """Initialize Gmail client with configuration.

        Args:
            config: Gmail configuration object that handles authentication
                   and provides the Gmail API service
        """
        self._config = config
        self._service: Any = None

    async def __aenter__(self) -> Self:
        """Enter async context manager and establish Gmail API connection."""
        self._service = await self._config.get_gmail_service()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager and cleanup resources."""
        await self.close()

    async def close(self) -> None:
        """Close Gmail client and cleanup resources."""
        self._service = None

    async def list_inbox_messages(self, limit: int = 10) -> list[Email]:
        """List messages from the Gmail inbox.

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            List of Email objects with basic information

        Raises:
            EmailConnectionError: If client not connected or API call fails
            EmailAuthenticationError: If authentication fails
        """
        if not self._service:
            connection_error_msg = (
                "Gmail client not connected. Use async context manager "
                "or call connect()."
            )
            raise EmailConnectionError(
                connection_error_msg,
                error_code="CLIENT_NOT_CONNECTED",
            )

        try:
            # Get message list from inbox
            results = (
                self._service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"], maxResults=limit)
                .execute()
            )

            messages = results.get("messages", [])
            emails = []

            # Get metadata for each message
            for msg in messages:
                try:
                    # Fetch metadata format to get headers without full body
                    message_data = (
                        self._service.users()
                        .messages()
                        .get(userId="me", id=msg["id"], format="metadata")
                        .execute()
                    )

                    email = self._parse_gmail_message(
                        message_data, include_body=False
                    )
                    emails.append(email)
                except (KeyError, ValueError, TypeError):
                    # Skip messages that can't be parsed
                    continue

        except HttpError as e:
            self._handle_http_error(e, "listing inbox messages")
            # This return will never be reached but satisfies mypy
            return []
        except Exception as e:
            list_error_msg = f"Failed to list inbox messages: {e}"
            raise EmailConnectionError(
                list_error_msg,
                error_code="GMAIL_LIST_FAILED",
            ) from e
        else:
            return emails

    async def get_email_content(self, email_id: str) -> Email:
        """Get full email content by ID.

        Args:
            email_id: Gmail message ID

        Returns:
            Email object with full content

        Raises:
            EmailConnectionError: If client not connected or API call fails
            EmailNotFoundError: If email with given ID doesn't exist
            EmailAuthenticationError: If authentication fails
        """
        if not self._service:
            connection_error_msg = (
                "Gmail client not connected. Use async context manager "
                "or call connect()."
            )
            raise EmailConnectionError(
                connection_error_msg,
                error_code="CLIENT_NOT_CONNECTED",
            )

        try:
            # Get full message
            message = (
                self._service.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )

            return self._parse_gmail_message(message, include_body=True)

        except HttpError as e:
            # Handle 404 specifically for not found emails
            if e.resp.status == 404:  # noqa: PLR2004
                not_found_msg = f"Email with ID '{email_id}' not found"
                raise EmailNotFoundError(
                    not_found_msg,
                    error_code="EMAIL_NOT_FOUND",
                ) from e

            self._handle_http_error(e, "getting email content")
            # This return will never be reached but satisfies mypy
            unreachable_msg = "Unreachable"
            raise EmailConnectionError(
                unreachable_msg, error_code="UNREACHABLE",
            ) from e
        except Exception as e:
            get_error_msg = f"Failed to get email content: {e}"
            raise EmailConnectionError(
                get_error_msg,
                error_code="GMAIL_GET_FAILED",
            ) from e

    def _parse_gmail_message(
        self, message: dict[str, Any], *, include_body: bool = True
    ) -> Email:
        """Parse Gmail API message into Email object.

        Args:
            message: Gmail API message data
            include_body: Whether to parse message body content

        Returns:
            Email object with parsed data
        """
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        # Parse headers
        subject = ""
        sender_email = "unknown@unknown.com"
        sender_name = ""
        recipient_addresses: list[EmailAddress] = []
        date_str = ""

        for header in headers:
            name = header.get("name", "").lower()
            value = header.get("value", "")

            if name == "subject":
                subject = value
            elif name == "from":
                parsed_addresses = self._parse_email_addresses(value)
                if parsed_addresses:
                    sender = parsed_addresses[0]
                    sender_email = sender.address
                    sender_name = sender.name or ""
            elif name == "to":
                recipient_addresses.extend(self._parse_email_addresses(value))
            elif name == "date":
                date_str = value

        # Parse date
        timestamp = self._parse_date(date_str)

        # Parse body content if requested
        body_text = None
        body_html = None

        if include_body:
            body_text, body_html = self._extract_message_content(payload)

        return Email(
            id=message["id"],
            subject=subject,
            sender=EmailAddress(address=sender_email, name=sender_name),
            recipients=recipient_addresses,
            body_text=body_text,
            body_html=body_html,
            date_sent=timestamp,
            date_received=timestamp,
        )

    def _parse_email_addresses(self, address_string: str) -> list[EmailAddress]:
        """Parse email addresses from header string.

        Args:
            address_string: Email address string from header

        Returns:
            List of EmailAddress objects
        """
        if not address_string.strip():
            return []

        addresses = []
        # Split on comma but be careful about commas in names
        parts = address_string.split(",")

        for addr_part in parts:
            addr_str = addr_part.strip()
            if not addr_str:
                continue

            # Handle formats like "Name <email@domain.com>" or just "email@domain.com"
            if "<" in addr_str and ">" in addr_str:
                name_part, email_part = addr_str.rsplit("<", 1)
                name = name_part.strip().strip('"').strip("'")
                email = email_part.rstrip(">").strip()
            else:
                name = None
                email = addr_str

            if email:  # Only add if we have an email address
                addresses.append(EmailAddress(address=email, name=name))

        return addresses

    def _parse_date(self, date_str: str) -> datetime:
        """Parse Gmail date string to datetime object.

        Args:
            date_str: Date string from Gmail API

        Returns:
            Parsed datetime object, defaults to epoch if parsing fails
        """
        if not date_str:
            return datetime.fromtimestamp(0, tz=UTC)

        try:
            # Gmail typically uses RFC 2822 format
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            # Fallback to epoch time if parsing fails
            return datetime.fromtimestamp(0, tz=UTC)

    def _extract_message_content(
        self, payload: dict[str, Any]
    ) -> tuple[str | None, str | None]:
        """Extract text and HTML content from Gmail message payload.

        Args:
            payload: Gmail message payload

        Returns:
            Tuple of (text_content, html_content)
        """
        text_content = None
        html_content = None

        def extract_parts(part: dict[str, Any]) -> None:
            nonlocal text_content, html_content

            mime_type = part.get("mimeType", "")

            if mime_type == "text/plain":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    text_content = self._decode_body_data(body_data)
            elif mime_type == "text/html":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    html_content = self._decode_body_data(body_data)
            elif mime_type.startswith("multipart/"):
                # Recursively process multipart messages
                for subpart in part.get("parts", []):
                    extract_parts(subpart)

        extract_parts(payload)
        return text_content, html_content

    def _decode_body_data(self, data: str) -> str | None:
        """Decode base64url encoded body data.

        Args:
            data: Base64url encoded body data

        Returns:
            Decoded text content or None if decoding fails
        """
        if not data:
            return ""

        try:
            # Gmail uses base64url encoding (URL-safe base64)
            decoded_bytes = base64.urlsafe_b64decode(data + "==")
            return decoded_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return None

    def _handle_http_error(self, error: HttpError, operation: str) -> None:  # type: ignore[no-any-unimported]
        """Handle HTTP errors from Gmail API.

        Args:
            error: HTTP error from Gmail API
            operation: Description of the operation that failed

        Raises:
            EmailAuthenticationError: For auth-related errors (401, 403)
            EmailNotFoundError: For non-existent email errors (400 with
                "Invalid id value")
            EmailConnectionError: For other HTTP errors
        """
        status_code = error.resp.status
        error_content = str(error)

        if status_code == HTTP_UNAUTHORIZED:
            auth_error_msg = f"Gmail authentication failed while {operation}"
            raise EmailAuthenticationError(
                auth_error_msg,
                error_code="GMAIL_AUTH_EXPIRED",
            ) from error
        if status_code == HTTP_FORBIDDEN:
            forbidden_msg = (
                f"Gmail API access forbidden while {operation}. "
                "Check scopes and permissions."
            )
            raise EmailAuthenticationError(
                forbidden_msg,
                error_code="GMAIL_FORBIDDEN",
            ) from error
        if status_code == HTTP_BAD_REQUEST and "Invalid id value" in error_content:
            not_found_msg = f"Email not found while {operation}"
            raise EmailNotFoundError(
                not_found_msg,
                error_code="EMAIL_NOT_FOUND",
            ) from error

        general_error_msg = f"Gmail API error while {operation}: {error}"
        raise EmailConnectionError(
            general_error_msg,
            error_code=f"GMAIL_HTTP_{status_code}",
        ) from error
