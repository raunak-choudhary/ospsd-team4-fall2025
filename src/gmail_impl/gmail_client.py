import base64, contextlib, os, re
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
    """Gmail implementation of the Client protocol."""

    SCOPES: ClassVar[list[str]] = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(
        self,
        credentials_file: str | None = None,
        token_file: str | None = None,
    ) -> None:
        self._credentials_file = (
            credentials_file
            or os.getenv("GMAIL_CREDENTIALS_PATH")
            or "credentials.json"
        )
        self._token_file = token_file or os.getenv("GMAIL_TOKEN_PATH") or "token.json"
        self._service: Any = None

    # === Auth ===
    def _authenticate(self) -> Credentials:
        token_path = Path(self._token_file)
        creds: Credentials | None = None

        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(token_path), self.SCOPES
                )
            except (OSError, ValueError, KeyError):
                with contextlib.suppress(OSError):
                    token_path.unlink()

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_path = Path(self._credentials_file)
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with contextlib.suppress(OSError):
                token_path.write_text(creds.to_json())

        return creds

    def _build_service(self, creds: Credentials) -> Any:
        return build("gmail", "v1", credentials=creds)

    def _ensure_connected(self) -> None:
        if self._service is None:
            creds = self._authenticate()
            self._service = self._build_service(creds)
            self._service.users().getProfile(userId="me").execute()

    # === Core ===
    def get_messages(self, limit: int | None = None) -> Iterator[Email]:
        self._ensure_connected()
        messages_yielded, page_token = 0, None

        while True:
            request_params: dict[str, Any] = {"userId": "me", "labelIds": ["INBOX"]}
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
                self._service.users().messages().list(**request_params).execute()
            )
            messages = results.get("messages", [])
            if not messages:
                break

            for msg in messages:
                if limit is not None and messages_yielded >= limit:
                    return
                message_data = (
                    self._service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )
                yield self._parse_message(message_data)
                messages_yielded += 1

            page_token = results.get("nextPageToken")
            if not page_token:
                break

    # === Parsing ===
    def _parse_message(self, message: dict[str, Any]) -> Email:
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        subject, sender_email, sender_name, date_str = "", "unknown@unknown.com", None, ""
        recipient_addresses: list[EmailAddress] = []

        for header in headers:
            name, value = header.get("name", "").lower(), header.get("value", "")
            if name == "subject":
                subject = value
            elif name == "from":
                parsed = self._parse_email_addresses(value)
                if parsed:
                    sender_email = parsed[0].address
                    sender_name = parsed[0].name
            elif name == "to":
                recipient_addresses.extend(self._parse_email_addresses(value))
            elif name == "date":
                date_str = value

        timestamp = self._parse_date(date_str)
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

    def _parse_email_addresses(self, s: str) -> list[EmailAddress]:
        if not s.strip():
            return []
        result: list[EmailAddress] = []
        for part in s.split(","):
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
                result.append(EmailAddress(address=email, name=name))
        return result

    def _parse_date(self, date_str: str) -> datetime:
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.fromtimestamp(0, tz=UTC)

    def _extract_body(self, payload: dict[str, Any]) -> str:
        text, html = None, None

        def extract(part: dict[str, Any]) -> None:
            nonlocal text, html
            mtype = part.get("mimeType", "")
            if mtype == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    text = self._decode_body(data)
            elif mtype == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    html = self._decode_body(data)
            elif mtype.startswith("multipart/"):
                for sub in part.get("parts", []):
                    extract(sub)

        extract(payload)
        if text:
            return text
        if html:
            return self._html_to_text(html)
        return ""

    def _decode_body(self, data: str) -> str:
        try:
            decoded = base64.urlsafe_b64decode(data + "==")
            return decoded.decode("utf-8")
        except Exception:
            return ""

    def _html_to_text(self, html: str) -> str:
        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&quot;", '"', text)
        text = re.sub(r"&#39;", "'", text)
        return re.sub(r"\s+", " ", text).strip()

    def _handle_http_error(self, e: HttpError, op: str) -> None:
        code = e.resp.status
        if code in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN):
            raise RuntimeError(f"Gmail auth failed while {op}") from e
        raise ConnectionError(f"Gmail API error while {op}: {e}") from e
