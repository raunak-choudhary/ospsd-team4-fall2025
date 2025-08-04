"""Tests for Gmail configuration and authentication."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
)
from gmail_impl.config import GmailConfig


class TestGmailConfig:
    """Test cases for GmailConfig class."""

    def test_init_default_values(self) -> None:
        """Test GmailConfig initialization with default values."""
        config = GmailConfig()

        assert config.credentials_file == Path("credentials.json")
        assert config.token_file == Path("token.json")
        assert config.scopes == ["https://www.googleapis.com/auth/gmail.readonly"]

    def test_init_custom_values(self) -> None:
        """Test GmailConfig initialization with custom values."""
        config = GmailConfig(
            credentials_file="custom_creds.json",
            token_file="custom_token.json",
            scopes=["https://www.googleapis.com/auth/gmail.modify"],
        )

        assert config.credentials_file == Path("custom_creds.json")
        assert config.token_file == Path("custom_token.json")
        assert config.scopes == ["https://www.googleapis.com/auth/gmail.modify"]

    @pytest.mark.asyncio
    async def test_get_gmail_service_success(self) -> None:
        """Test successful Gmail service creation."""
        config = GmailConfig()

        mock_creds = MagicMock()
        mock_service = MagicMock()

        with (
            patch.object(
                GmailConfig, "_get_credentials", return_value=mock_creds
            ) as mock_get_creds,
            patch("gmail_impl.config.build", return_value=mock_service) as mock_build,
            patch.object(GmailConfig, "_test_connection") as mock_test,
        ):
            service = await config.get_gmail_service()

            # For instance methods patched at class level, only check call count
            assert mock_get_creds.call_count == 1
            mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
            assert mock_test.call_count == 1
            assert service == mock_service

    @pytest.mark.asyncio
    async def test_get_gmail_service_auth_error(self) -> None:
        """Test Gmail service creation with authentication error."""
        config = GmailConfig()

        auth_error = EmailAuthenticationError("Auth failed", "AUTH_ERROR")

        with (
            patch.object(GmailConfig, "_get_credentials", side_effect=auth_error),
            pytest.raises(EmailAuthenticationError),
        ):
            await config.get_gmail_service()

    @pytest.mark.asyncio
    async def test_get_gmail_service_connection_error(self) -> None:
        """Test Gmail service creation with connection error."""
        config = GmailConfig()

        connection_error = EmailConnectionError(
            "Connection failed", "CONNECTION_ERROR"
        )

        with (
            patch.object(GmailConfig, "_get_credentials", side_effect=connection_error),
            pytest.raises(EmailConnectionError),
        ):
            await config.get_gmail_service()

    @pytest.mark.asyncio
    async def test_get_credentials_refresh_expired_token(self) -> None:
        """Test refreshing expired credentials."""
        config = GmailConfig(token_file="test_token.json")

        # Mock expired credentials
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_creds.to_json.return_value = '{"token": "mock_token"}'

        with (
            patch("gmail_impl.config.Path.exists", return_value=True),
            patch(
                "gmail_impl.config.Credentials.from_authorized_user_file",
                return_value=mock_creds,
            ),
            patch("gmail_impl.config.Request") as mock_request_class,
            patch("gmail_impl.config.Path.write_text") as mock_write,
        ):
            mock_request = mock_request_class.return_value

            result = await config._get_credentials()

            mock_creds.refresh.assert_called_once_with(mock_request)
            mock_write.assert_called_once_with('{"token": "mock_token"}')
            assert result == mock_creds

    @pytest.mark.asyncio
    async def test_get_credentials_oauth_flow(self) -> None:
        """Test OAuth flow when no valid credentials exist."""
        config = GmailConfig(
            credentials_file="creds.json",
            token_file="new_token.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )

        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "new_mock_token"}'

        with (
            patch("gmail_impl.config.Path.exists", return_value=False),
            patch.object(
                GmailConfig, "_run_oauth_flow", return_value=mock_creds
            ) as mock_oauth,
            patch("gmail_impl.config.Path.write_text") as mock_write,
        ):
            result = await config._get_credentials()

            assert mock_oauth.call_count == 1
            mock_write.assert_called_once_with('{"token": "new_mock_token"}')
            assert result == mock_creds

    @pytest.mark.asyncio
    async def test_get_credentials_oauth_flow_failed(self) -> None:
        """Test OAuth flow failure."""
        config = GmailConfig(
            credentials_file="missing_creds.json",
            token_file="token.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )

        with patch("gmail_impl.config.Path.exists", return_value=False):
            with pytest.raises(EmailAuthenticationError) as exc_info:
                await config._run_oauth_flow()

            assert exc_info.value.error_code == "GMAIL_CREDENTIALS_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_credentials_missing_credentials_file(self) -> None:
        """Test error when credentials file is missing."""
        config = GmailConfig(credentials_file="missing.json")

        with pytest.raises(EmailAuthenticationError) as exc_info:
            await config._run_oauth_flow()

        assert exc_info.value.error_code == "GMAIL_CREDENTIALS_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_test_connection_success(self) -> None:
        """Test successful connection test."""
        config = GmailConfig()

        mock_service = MagicMock()
        mock_profile = {"emailAddress": "test@example.com"}

        # Configure the mock chain properly
        mock_service.users.return_value.getProfile.return_value.execute.return_value = (
            mock_profile
        )

        # Should not raise an exception
        await config._test_connection(mock_service)

        # Verify the method chain was called correctly
        mock_service.users.assert_called_once()
        mock_service.users.return_value.getProfile.assert_called_once_with(userId="me")
        mock_service.users.return_value.getProfile.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self) -> None:
        """Test connection test failure."""
        config = GmailConfig()

        mock_service = MagicMock()
        mock_service.users().getProfile().execute.side_effect = Exception("API Error")

        with pytest.raises(EmailConnectionError) as exc_info:
            await config._test_connection(mock_service)

        assert exc_info.value.error_code == "GMAIL_CONNECTION_TEST_FAILED"
