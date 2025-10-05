# Forward inner email_api classes so top-level "import email_api" works

from .src.email_api import (
    Client,
    Email,
    EmailAddress,
    get_client,
)

__all__ = ["Client", "Email", "EmailAddress", "get_client"]
