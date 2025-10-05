"""Message endpoints for the mail client service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from fastapi import APIRouter, HTTPException

import email_api
from email_api import Client

if TYPE_CHECKING:
    # Used only for type hints (stringified via __future__.annotations)
    from collections.abc import Callable

router = APIRouter(prefix="/messages", tags=["messages"])


def _client() -> Client:
    """Return the injected email client (configured via dependency injection)."""
    return email_api.get_client()


def _require_method(client: Client, name: str) -> Callable[..., object]:
    """Return a callable method from the client or raise 501 if missing."""
    fn = getattr(cast("Any", client), name, None)
    if callable(fn):
        return cast("Callable[..., object]", fn)
    raise HTTPException(
        status_code=501,
        detail=f"{name} is not implemented by email_api.Client",
    )


@router.get("")
def list_messages() -> list[dict[str, Any]]:
    """Return a list of message summaries.

    Prefer `list_messages()` if available; otherwise fall back to `get_messages()`.
    """
    client = _client()
    if hasattr(client, "list_messages"):
        result = _require_method(client, "list_messages")()
    else:
        result = _require_method(client, "get_messages")(limit=50)
    return cast("list[dict[str, Any]]", result)


@router.get("/{message_id}")
def get_message(message_id: str) -> dict[str, Any]:
    """Return full detail for a single message."""
    client = _client()
    result = _require_method(client, "get_message")(message_id)
    return cast("dict[str, Any]", result)


@router.post("/{message_id}/mark-as-read")
def mark_as_read(message_id: str) -> dict[str, Any]:
    """Mark a message as read."""
    client = _client()
    result = _require_method(client, "mark_as_read")(message_id)
    return cast("dict[str, Any]", result)


@router.delete("/{message_id}")
def delete_message(message_id: str) -> dict[str, Any]:
    """Delete a message."""
    client = _client()
    result = _require_method(client, "delete_message")(message_id)
    return cast("dict[str, Any]", result)
