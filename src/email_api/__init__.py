# Forward inner email_api classes so top-level "import email_api" works
from email_api.src.email_api import (
    Client as Client,
    Email as Email,
    EmailAddress as EmailAddress,
    get_client as get_client,
)

__all__ = ["Client", "Email", "EmailAddress", "get_client"]
