"""Gmail configuration and authentication management."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from email_api.exceptions import EmailAuthenticationError, EmailConnectionError

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


@dataclass(frozen=True)
class GmailConfig:
    """Configuration for Gmail API client authentication and service creation.

    This class handles OAuth2 authentication flow and Gmail API service
    instantiation using dependency injection principles.

    Attributes:
        credentials_file: Path to OAuth2 credentials JSON file
        token_file: Path to store/retrieve access token
        scopes: Gmail API permission scopes

    Example:
        config = GmailConfig(
            credentials_file="credentials.json",
            token_file="token.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )
        service = await config.get_gmail_service()
    """

    credentials_file: str | Path = "credentials.json"
    token_file: str | Path = "token.json"  # noqa: S105
    scopes: list[str] | None = None

    def __post_init__(self) -> None:
        """Post-initialization to set defaults and convert types."""
        # Convert string paths to Path objects (immutable assignment)
        if isinstance(self.credentials_file, str):
            object.__setattr__(self, "credentials_file", Path(self.credentials_file))
        if isinstance(self.token_file, str):
            object.__setattr__(self, "token_file", Path(self.token_file))

        # Set default scopes if none provided
        if self.scopes is None:
            object.__setattr__(self, "scopes", ["https://www.googleapis.com/auth/gmail.readonly"])

    async def get_gmail_service(self) -> Resource:  # type: ignore[no-any-unimported]
        """Get authenticated Gmail API service.

        Handles the complete OAuth2 authentication flow including:
        - Loading existing credentials from token file
        - Refreshing expired credentials
        - Running OAuth2 flow for new credentials
        - Testing connection to Gmail API

        Returns:
            Authenticated Gmail API service object

        Raises:
            EmailAuthenticationError: If authentication fails
            EmailConnectionError: If unable to connect to Gmail API
        """
        try:
            creds = await self._get_credentials()
            service: Resource = build("gmail", "v1", credentials=creds)  # type: ignore[no-any-unimported]
            await self._test_connection(service)
        except EmailAuthenticationError:
            # Re-raise authentication errors as-is
            raise
        except EmailConnectionError:
            # Re-raise connection errors as-is
            raise
        except Exception as e:
            connection_error_msg = f"Failed to create Gmail service: {e}"
            raise EmailConnectionError(
                connection_error_msg,
                error_code="GMAIL_SERVICE_CREATION_FAILED",
            ) from e
        else:
            return service

    async def _get_credentials(self) -> Credentials:
        """Get or create OAuth2 credentials.

        Returns:
            Valid OAuth2 credentials

        Raises:
            EmailAuthenticationError: If authentication fails
        """
        creds = None

        # Load existing token
        token_file_path = cast("Path", self.token_file)
        if token_file_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
                    str(token_file_path), self.scopes
                )
            except (OSError, ValueError, KeyError):
                # If token loading fails, we'll create new credentials
                with contextlib.suppress(OSError):
                    token_file_path.unlink()

        # Refresh or create credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # type: ignore[no-untyped-call]
                except Exception as e:
                    auth_error_msg = f"Failed to refresh Gmail credentials: {e}"
                    raise EmailAuthenticationError(
                        auth_error_msg,
                        error_code="GMAIL_TOKEN_REFRESH_FAILED",
                    ) from e
            else:
                # Run OAuth2 flow
                creds = await self._run_oauth_flow()

            # Save credentials for next run
            try:
                token_file_path.write_text(creds.to_json())
            except OSError:
                # Non-critical error - credentials work but won't be saved
                with contextlib.suppress(OSError):
                    pass

        return creds

    async def _run_oauth_flow(self) -> Credentials:
        """Run OAuth2 authorization flow.

        Returns:
            Fresh OAuth2 credentials

        Raises:
            EmailAuthenticationError: If OAuth2 flow fails
        """
        credentials_file_path = cast("Path", self.credentials_file)
        if not credentials_file_path.exists():
            creds_error_msg = (
                f"Credentials file not found: {credentials_file_path}. "
                "Please download it from Google Cloud Console."
            )
            raise EmailAuthenticationError(
                creds_error_msg,
                error_code="GMAIL_CREDENTIALS_NOT_FOUND",
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file_path), self.scopes
            )
            return flow.run_local_server(port=0)  # type: ignore[no-any-return]
        except Exception as e:
            oauth_error_msg = f"OAuth2 flow failed: {e}"
            raise EmailAuthenticationError(
                oauth_error_msg,
                error_code="GMAIL_OAUTH_FLOW_FAILED",
            ) from e

    async def _test_connection(self, service: Resource) -> None:  # type: ignore[no-any-unimported]
        """Test the Gmail API connection.

        Args:
            service: Gmail API service object

        Raises:
            EmailConnectionError: If connection test fails
        """
        try:
            # Simple API call to test connection
            service.users().getProfile(userId="me").execute()
        except Exception as e:
            test_error_msg = f"Gmail API connection test failed: {e}"
            raise EmailConnectionError(
                test_error_msg,
                error_code="GMAIL_CONNECTION_TEST_FAILED",
            ) from e
