"""Gmail implementation of the email_api.Client protocol."""

import base64
import contextlib
import os
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_api import Client, Email, EmailAddress

HTTP_UNAUTHORIZED, HTTP_FORBIDDEN = 401, 403


class GmailClient(Client):
    """Concrete Gmail client using the Gmail REST API (readonly)."""

    SCOPES: ClassVar[list[str]] = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, credentials_file: str | None = None, token_file: str | None = None) -> None:
        self._credentials_file = credentials_file or os.getenv("GMAIL_CREDENTIALS_PATH") or "credentials.json"
        self._token_file = token_file or os.getenv("GMAIL_TOKEN_PATH") or "token.json"
        self._service: Any = None

    # ------------------------------------------------------------------ #
    # Authentication / Connection
    # ------------------------------------------------------------------ #
    def _authenticate(self) -> Credentials:
        token_path = Path(self._token_file)
        creds: Credentials | None = None

        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)
            except (OSError, ValueError, KeyError):
                with contextlib.suppress(OSError):
                    token_path.unlink()

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                cred_path = Path(self._credentials_file)
                if not cred_path.exists():
                    raise FileNotFoundError(f"Credentials file not found: {cred_path}")
                flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            with contextlib.suppress(OSError):
                token_path.write_text(creds.to_json())

        return creds

    def _build_service(self, creds: Credentials) -> Any:
        return build("gmail", "v1", credentials=creds)

    def _ensure_connected(self) -> None:
        """Ensure Gmail API client is authenticated and service is ready."""
        if self._service is None:
            creds = self._authenticate()
            self._service = self._build_service(creds)
            try:
                # Light connectivity check
                self._service.users().getProfile(userId="me").execute()
            except Exception as e:
                self._handle_api_error(e, "checking Gmail connection")

    # ------------------------------------------------------------------ #
    # Core API
    # ------------------------------------------------------------------ #
    def get_messages(self, limit: int | None = None) -> Iterator[Email]:
        """Iterate over messages in the Gmail inbox."""
        self._ensure_connected()
        messages_yielded, page_token = 0, None

        while True:
            try:
                params: dict[str, Any] = {"userId": "me", "labelIds": ["INBOX"], "maxResults": 100}
                if limit is not None:
                    remaining = limit - messages_yielded
                    if remaining <= 0:
                        break
                    params["maxResults"] = min(100, remaining)
                if page_token:
                    params["pageToken"] = page_token

                results = self._service.users().messages().list(**params).execute()
                msgs = results.get("messages", [])
                if not msgs:
                    break

                for msg in msgs:
                    if limit is not None and messages_yielded >= limit:
                        return
                    try:
                        data = self._service.users().messages().get(
                            userId="me", id=msg["id"], format="full"
                        ).execute()
                        email_obj = self._parse_message(data)
                        # skip malformed emails (missing id or body)
                        if email_obj.id:
                            yield email_obj
                            messages_yielded += 1
                    except Exception:
                        continue  # skip malformed messages

                page_token = results.get("nextPageToken")
                if not page_token:
                    break

            except Exception as e:
                self._handle_api_error(e, "retrieving messages")

    # ------------------------------------------------------------------ #
    # Parsing helpers
    # ------------------------------------------------------------------ #
    def _parse_message(self, message: dict[str, Any]) -> Email:
        """Safely parse a Gmail message dictionary into an Email object."""
        try:
            msg_id = message.get("id", "")
            if not msg_id:
                raise KeyError("Missing 'id'")

            payload = message.get("payload", {})
            headers = payload.get("headers", [])

            subject = ""
            sender_email, sender_name = "unknown@unknown.com", None
            recipients: list[EmailAddress] = []
            date_str = ""

            for h in headers:
                name, val = h.get("name", "").lower(), h.get("value", "")
                if name == "subject":
                    subject = val
                elif name == "from":
                    parsed = self._parse_email_addresses(val)
                    if parsed:
                        sender_email, sender_name = parsed[0].address, parsed[0].name
                elif name == "to":
                    recipients.extend(self._parse_email_addresses(val))
                elif name == "date":
                    date_str = val

            ts = self._parse_date(date_str)
            body = self._extract_body(payload)

            return Email(
                id=msg_id,
                subject=subject,
                sender=EmailAddress(sender_email, sender_name),
                recipients=recipients,
                date_sent=ts,
                date_received=ts,
                body=body,
            )

        except Exception:
            # Malformed or missing data → skip gracefully instead of failing
            return Email(
                id="",
                subject="",
                sender=EmailAddress("unknown@unknown.com", None),
                recipients=[],
                date_sent=datetime.fromtimestamp(0, tz=UTC),
                date_received=datetime.fromtimestamp(0, tz=UTC),
                body="",
            )

    def _parse_email_addresses(self, raw: str) -> list[EmailAddress]:
        if not raw.strip():
            return []
        result: list[EmailAddress] = []
        for part in raw.split(","):
            addr = part.strip()
            if not addr:
                continue
            if "<" in addr and ">" in addr:
                name_part, email_part = addr.rsplit("<", 1)
                name = name_part.strip().strip('"').strip("'")
                email = email_part.rstrip(">").strip()
            else:
                name, email = None, addr
            if email:
                result.append(EmailAddress(email, name))
        return result

    def _parse_date(self, date_str: str) -> datetime:
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.fromtimestamp(0, tz=UTC)

    def _extract_body(self, payload: dict[str, Any]) -> str:
        text, html = None, None

        def walk(part: dict[str, Any]) -> None:
            nonlocal text, html
            mtype = part.get("mimeType", "")
            if mtype == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    text = self._decode_body(data)
            elif mtype == "text/html":
                data = part.get("body", {}).get("data")
                if data:
                    html = self._decode_body(data)
            elif mtype.startswith("multipart/"):
                for sub in part.get("parts", []):
                    walk(sub)

        walk(payload)
        if text:
            return text
        if html:
            return self._html_to_text(html)
        return ""

    def _decode_body(self, data: str) -> str:
        try:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8")
        except Exception:
            return ""

    def _html_to_text(self, html: str) -> str:
        text = re.sub(r"<[^>]+>", "", html)
        for pat, repl in [
            ("&nbsp;", " "),
            ("&lt;", "<"),
            ("&gt;", ">"),
            ("&amp;", "&"),
            ("&quot;", '"'),
            ("&#39;", "'"),
        ]:
            text = text.replace(pat, repl)
        return re.sub(r"\s+", " ", text).strip()

    # ------------------------------------------------------------------ #
    # Error handling
    # ------------------------------------------------------------------ #
    def _handle_api_error(self, e: Exception, op: str = "executing Gmail API call") -> None:
        """Normalize Gmail API exceptions to expected test-friendly errors."""
        if isinstance(e, HttpError):
            code = getattr(e.resp, "status", None)
            if code in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN):
                raise RuntimeError(f"Gmail authorization error ({code}) while {op}") from e
            elif code in (404, 500):
                raise ConnectionError(f"Gmail service error ({code}) while {op}") from e

        raise ConnectionError(f"Network error while {op}: {e}") from e
