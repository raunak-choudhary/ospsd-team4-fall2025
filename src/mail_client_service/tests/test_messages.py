"""Unit tests for the /messages endpoints (service layer)."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

import email_api
from mail_client_service.app import app


class DummyClient:
    """In-memory dummy client used to isolate the FastAPI layer."""

    def list_messages(self) -> list[dict[str, Any]]:
        """Return an empty list of messages."""
        return []

    def get_message(self, message_id: str) -> dict[str, Any]:
        """Return a single message by id."""
        return {"id": message_id}

    def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """Mark a message as read."""
        return {"id": message_id, "status": "read"}

    def delete_message(self, message_id: str) -> dict[str, Any]:
        """Delete a message."""
        return {"id": message_id, "deleted": True}


def setup_function() -> None:
    """Monkeypatch the DI factory to return our dummy instead of Gmail."""
    email_api.get_client = lambda: DummyClient()  # type: ignore[assignment]


def test_list_messages() -> None:
    """It should return an empty list."""
    client = TestClient(app)
    resp = client.get("/messages")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_message() -> None:
    """It should return the requested message."""
    client = TestClient(app)
    resp = client.get("/messages/ABC123")
    assert resp.status_code == 200
    assert resp.json() == {"id": "ABC123"}


def test_mark_as_read() -> None:
    """It should mark the message as read."""
    client = TestClient(app)
    resp = client.post("/messages/ABC123/mark-as-read")
    assert resp.status_code == 200
    assert resp.json() == {"id": "ABC123", "status": "read"}


def test_delete_message() -> None:
    """It should delete the message."""
    client = TestClient(app)
    resp = client.delete("/messages/ABC123")
    assert resp.status_code == 200
    assert resp.json() == {"id": "ABC123", "deleted": True}
