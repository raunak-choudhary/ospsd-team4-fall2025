"""
Unit tests for email API exceptions.

These tests verify the exception hierarchy and behavior.
"""

import pytest

from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailError,
)


class TestEmailError:
    """Test base EmailError exception."""

    def test_basic_email_error(self) -> None:
        """Test EmailError with just a message."""
        error = EmailError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.error_code is None

    def test_email_error_with_code(self) -> None:
        """Test EmailError with message and error code."""
        error = EmailError("Something went wrong", error_code="ERR001")

        assert str(error) == "[ERR001] Something went wrong"
        assert error.message == "Something went wrong"
        assert error.error_code == "ERR001"

    def test_email_error_inheritance(self) -> None:
        """Test that EmailError inherits from Exception."""
        error = EmailError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, EmailError)

    def test_email_error_can_be_raised(self) -> None:
        """Test that EmailError can be raised and caught."""
        error_message = "Test error"
        error_code = "TEST"

        with pytest.raises(EmailError) as exc_info:
            raise EmailError(error_message, error_code=error_code)

        assert exc_info.value.message == error_message
        assert exc_info.value.error_code == error_code


class TestEmailConnectionError:
    """Test EmailConnectionError exception."""

    def test_connection_error_inheritance(self) -> None:
        """Test that EmailConnectionError inherits from EmailError."""
        error = EmailConnectionError("Connection failed")

        assert isinstance(error, EmailError)
        assert isinstance(error, EmailConnectionError)
        assert str(error) == "Connection failed"

    def test_connection_error_with_code(self) -> None:
        """Test EmailConnectionError with error code."""
        error = EmailConnectionError("Timeout", error_code="TIMEOUT")

        assert str(error) == "[TIMEOUT] Timeout"
        assert error.error_code == "TIMEOUT"

    def test_connection_error_can_be_caught_as_base(self) -> None:
        """Test that EmailConnectionError can be caught as EmailError."""
        error_message = "Connection failed"

        with pytest.raises(EmailError):
            raise EmailConnectionError(error_message)


class TestEmailAuthenticationError:
    """Test EmailAuthenticationError exception."""

    def test_auth_error_inheritance(self) -> None:
        """Test that EmailAuthenticationError inherits from EmailError."""
        error = EmailAuthenticationError("Invalid credentials")

        assert isinstance(error, EmailError)
        assert isinstance(error, EmailAuthenticationError)
