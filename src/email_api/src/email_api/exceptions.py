"""Email interface exception hierarchy.

This module defines the basic exceptions that can be raised by email client
implementations, providing consistent error handling for email operations.
"""



class EmailError(Exception):
    """Base exception for all email-related errors.

    All email client implementations should raise exceptions that inherit
    from this base class.

    Attributes:
        message: Human-readable error message
        error_code: Optional error code for programmatic handling
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
    ) -> None:
        """Initialize EmailError with message and optional error code."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class EmailConnectionError(EmailError):
    """Raised when there are connection issues with the email service.

    This includes network timeouts, DNS resolution failures, and
    other connectivity-related problems.
    """


class EmailAuthenticationError(EmailError):
    """Raised when authentication with the email service fails.

    This includes invalid credentials, expired tokens, and
    OAuth authentication failures.
    """


class EmailNotFoundError(EmailError):
    """Raised when a requested email cannot be found.

    This includes attempts to access non-existent emails by ID.
    """
