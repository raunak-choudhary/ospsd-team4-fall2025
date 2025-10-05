"""Email API Component.

Provides abstract interfaces and dependency injection for email clients.
"""

# Re-export everything from the inner client
from .client import (
    Client,
    Email,
    EmailAddress,
    get_client,
    register_client_factory,
)

__all__ = [
    "Client",
    "Email",
    "EmailAddress",
    "get_client",
    "register_client_factory",
]

__version__ = "0.1.0"
__author__ = "Adithya Balachandra"
__description__ = "Email client interface component"
