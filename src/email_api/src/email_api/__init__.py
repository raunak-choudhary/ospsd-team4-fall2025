"""Expose core email_api implementation."""

from .client import (
    Client,
    Email,
    EmailAddress,
    register_client_factory,
    get_client,
)

__all__ = ["Client", "Email", "EmailAddress", "register_client_factory", "get_client"]
