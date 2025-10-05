"""Dependency injection entrypoint for mail_client_adapter.

When imported, this module overrides email_api.get_client()
so that all calls to get_client() return the service-backed adapter.
"""

import email_api

from .adapter import ServiceBackedClient

DEFAULT_BASE_URL = "http://127.0.0.1:8080"

# Override factory
email_api.get_client = lambda: ServiceBackedClient(base_url=DEFAULT_BASE_URL)
