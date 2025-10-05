from collections.abc import Iterator
from typing import Any

import email_api
from mail_client_service_client import Client as GeneratedClient
from mail_client_service_client.api.messages import (
    delete_message_messages_message_id_delete as api_delete_message,
    get_message_messages_message_id_get as api_get_message,
    list_messages_messages_get as api_list_messages,
    mark_as_read_messages_message_id_mark_as_read_post as api_mark_as_read,
)
from .mapping import to_email_model, to_message_id


class ServiceBackedClient(email_api.Client):
    """Implements email_api.Client using the generated HTTP client.
    Consumers don’t know if they’re using a local or remote service.
    """

    def __init__(self, base_url: str) -> None:
        self._client = GeneratedClient(base_url=base_url)

    def list_messages(self) -> list[email_api.Email]:
        """Fetch list of all messages from remote service."""
        resp = api_list_messages.sync(client=self._client)
        return [to_email_model(msg) for msg in (resp or [])]

    def get_message(self, message_id: str) -> email_api.Email:
        """Fetch a specific message by ID."""
        resp = api_get_message.sync(
            client=self._client,
            message_id=to_message_id(message_id),
        )
        return to_email_model(resp)

    def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """Mark message as read on the server."""
        return api_mark_as_read.sync(
            client=self._client,
            message_id=to_message_id(message_id),
        )

    def delete_message(self, message_id: str) -> dict[str, Any]:
        """Delete message by ID from the server."""
        return api_delete_message.sync(
            client=self._client,
            message_id=to_message_id(message_id),
        )

    def get_messages(self, limit: int | None = None) -> Iterator[email_api.Email]:
        """Wrapper for compatibility with abstract Client interface."""
        for msg in self.list_messages():
            yield msg
