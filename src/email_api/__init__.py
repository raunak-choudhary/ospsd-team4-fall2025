"""Expose the inner email_api package cleanly."""

import sys
from pathlib import Path
from importlib import import_module

# Compute absolute path to the inner src/email_api directory
_inner_path = Path(__file__).resolve().parent / "src" / "email_api"
if _inner_path.exists() and str(_inner_path) not in sys.path:
    sys.path.insert(0, str(_inner_path))

# Import from the *inner* package
_inner = import_module("client", package="email_api")

Client = _inner.Client
Email = _inner.Email
EmailAddress = _inner.EmailAddress
register_client_factory = _inner.register_client_factory
get_client = _inner.get_client

__all__ = ["Client", "Email", "EmailAddress", "register_client_factory", "get_client"]
