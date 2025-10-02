"""Gmail client implementation of the Client protocol."""

import base64
from collections.abc import Iterator
import contextlib
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import os
from pathlib import Path
import re
from typing import Any, ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_api import Client, Email, EmailAddress

# HTTP status code constants
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404


class GmailClient(Client):
    """Gmail implementation of the Client protocol.

    This client provides Gmail API access through OAuth2 authentication.

    Example:
        client = GmailClient()
        for email in client.get_messages(limit=10):
            print(email.subject)
    """

    SCOPES: ClassVar[list[str]] = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(
        self,
        credentials_file: str | None = None,
        token_file: str | None = None,
    ) -> None:
        """Initialize Gmail client with configuration.

        Args:
            credentials_file: Path to OAuth2 credentials JSON file.
                Defaults to GMAIL_CREDENTIALS_PATH env var or "credentials.json"
            token_file: Path to store/retrieve access token.
                Defaults to GMAIL_TOKEN_PATH env var or "token.json"
        """
        self._credentials_file = (
            credentials_file
            or os.getenv("GMAIL_CREDENTIALS_PATH")
            or "credentials.json"
        )
        self._token_file = (
            token_file
            or os.getenv("GMAIL_TOKEN_PATH")
            or "token.json"
        )
        self._service: Any = None

    def _authenticate(self) -> Credentials:
        """Get or create OAuth2 credentials.

        Returns:
            Valid OAuth2 credentials

        Raises:
            RuntimeError: If authentication fails
            FileNotFoundError: If credentials file is missing
        """
        creds = None
        token_path = Path(self._token_file)

        # Load existing token
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
                    str(token_path), self.SCOPES,
                )
            except (OSError, ValueError, KeyError):
                # If token loading fails, delete and create new credentials
                with contextlib.suppress(OSError):
                    token_path.unlink()

        # Refresh or create credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # type: ignore[no-untyped-call]
                except Exception as e:
                    msg = f"Failed to refresh Gmail credentials: {e}"
                    raise RuntimeError(msg) from e
            else:
                # Run OAuth2 flow
                credentials_path = Path(self._credentials_file)
                if not credentials_path.exists():
                    msg = (
                        f"Credentials file not found: {credentials_path}. "
                        "Please download it from Google Cloud Console."
                    )
                    raise FileNotFoundError(msg)

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), self.SCOPES,
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    msg = f"OAuth2 flow failed: {e}"
                    raise RuntimeError(msg) from e

            # Save credentials for next run
            with contextlib.suppress(OSError):
                # Non-critical error - credentials work but won't be saved
                token_path.write_text(creds.to_json())

        return creds  # type: ignore[no-any-return]

    def _build_service(self, creds: Credentials) -> Any:  # noqa: ANN401
        """Build Gmail API service.

        Args:
            creds: OAuth2 credentials

        Returns:
            Gmail API service object
        """
        return build("gmail", "v1", credentials=creds)

    def _ensure_connected(self) -> None:
        """Ensure client is connected to Gmail API.

        Raises:
            ConnectionError: If unable to connect to Gmail API
            RuntimeError: If authentication fails
        """
        if self._service is None:
            try:
                creds = self._authenticate()
                self._service = self._build_service(creds)
                # Test connection
                self._service.users().getProfile(userId="me").execute()
            except (RuntimeError, FileNotFoundError):
                # Re-raise authentication errors
                raise
            except Exception as e:
                msg = f"Failed to connect to Gmail API: {e}"
                raise ConnectionError(msg) from e

    def get_messages(  # noqa: C901
        self,
        limit: int | None = None,
    ) -> Iterator[Email]:
        """Return an iterator of messages from inbox.

        Args:
            limit: Maximum number of messages to retrieve (optional)

        Yields:
            Email objects from the inbox

        Raises:
            ConnectionError: If unable to connect to mail service
            RuntimeError: If authentication fails
        """
        self._ensure_connected()

        try:
            messages_yielded = 0
            page_token = None

            while True:
                # Get message list from inbox
                request_params: dict[str, Any] = {
                    "userId": "me",
                    "labelIds": ["INBOX"],
                }

                # Determine batch size
                if limit is not None:
                    remaining = limit - messages_yielded
                    if remaining <= 0:
                        break
                    request_params["maxResults"] = min(100, remaining)
                else:
                    request_params["maxResults"] = 100

                if page_token:
                    request_params["pageToken"] = page_token

                results = (
                    self._service.users()
                    .messages()
                    .list(**request_params)
                    .execute()
                )

                messages = results.get("messages", [])
                if not messages:
                    break

                # Get and yield each message
                for msg in messages:
                    if limit is not None and messages_yielded >= limit:
                        return

                    try:
                        # Fetch full message format to get complete content
                        message_data = (
                            self._service.users()
                            .messages()
                            .get(userId="me", id=msg["id"], format="full")
                            .execute()
                        )

                        email = self._parse_message(message_data)
                        yield email
                        messages_yielded += 1
                    except (KeyError, ValueError, TypeError):
                        # Skip messages that can't be parsed
                        continue

                # Check for next page
                page_token = results.get("nextPageToken")
                if not page_token:
                    break

        except HttpError as e:
            self._handle_http_error(e, "listing inbox messages")
        except Exception as e:
            msg = f"Failed to list inbox messages: {e}"
            raise ConnectionError(msg) from e

    def _parse_message(self, message: dict[str, Any]) -> Email:
        """Parse Gmail API message into Email object.

        Args:
            message: Gmail API message data

        Returns:
            Email object with parsed data
        """
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        # Parse headers
        subject = ""
        sender_email = "unknown@unknown.com"
        sender_name = None
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
                    sender_name = sender.name
            elif name == "to":
                recipient_addresses.extend(self._parse_email_addresses(value))
            elif name == "date":
                date_str = value

        # Parse date
        timestamp = self._parse_date(date_str)

        # Parse body content
        body = self._extract_body(payload)

        return Email(
            id=message["id"],
            subject=subject,
            sender=EmailAddress(address=sender_email, name=sender_name),
            recipients=recipient_addresses,
            body=body,
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
                addresses.append(EmailAddress(address=email, name=name or None))

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

    def _extract_body(self, payload: dict[str, Any]) -> str:
        """Extract body content from Gmail message payload.

        Prefers plain text content. If only HTML is available, converts it to text.

        Args:
            payload: Gmail message payload

        Returns:
            Body content as plain text string
        """
        text_content = None
        html_content = None

        def extract_parts(part: dict[str, Any]) -> None:
            nonlocal text_content, html_content

            mime_type = part.get("mimeType", "")

            if mime_type == "text/plain":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    text_content = self._decode_body(body_data)
            elif mime_type == "text/html":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    html_content = self._decode_body(body_data)
            elif mime_type.startswith("multipart/"):
                # Recursively process multipart messages
                for subpart in part.get("parts", []):
                    extract_parts(subpart)

        extract_parts(payload)

        # Prefer plain text, convert HTML if needed
        if text_content:
            return text_content
        if html_content:
            return self._html_to_text(html_content)
        return ""

    def _decode_body(self, data: str) -> str | None:
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

    def _html_to_text(self, html: str) -> str:
        """Convert HTML content to plain text.

        Simple HTML to text conversion by stripping tags and decoding entities.

        Args:
            html: HTML content string

        Returns:
            Plain text content
        """
        if not html:
            return ""

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html)

        # Decode common HTML entities
        text = text.replace("&nbsp;", " ")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _handle_http_error(self, error: HttpError, operation: str) -> None:
        """Handle HTTP errors from Gmail API.

        Args:
            error: HTTP error from Gmail API
            operation: Description of the operation that failed

        Raises:
            RuntimeError: For auth-related errors (401, 403)
            ConnectionError: For other HTTP errors
        """
        status_code = error.resp.status

        if status_code == HTTP_UNAUTHORIZED:
            msg = f"Gmail authentication failed while {operation}"
            raise RuntimeError(msg) from error
        if status_code == HTTP_FORBIDDEN:
            msg = (
                f"Gmail API access forbidden while {operation}. "
                "Check scopes and permissions."
            )
            raise RuntimeError(msg) from error

        msg = f"Gmail API error while {operation}: {error}"
        raise ConnectionError(msg) from error
