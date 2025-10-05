from typing import Any
import email_api

def to_email_model(payload: Any) -> email_api.Email:
    """Convert service JSON payload to email_api.Email object."""
    return email_api.Email(
        id=str(payload["id"]),
        subject=str(payload.get("subject", "")),
        sender=email_api.EmailAddress(address=str(payload.get("from", ""))),
        recipients=[email_api.EmailAddress(address="placeholder@recipient.com")],
        date_sent=payload.get("date_sent", "1970-01-01T00:00:00Z"),
        date_received=payload.get("date_received", "1970-01-01T00:00:00Z"),
        body=str(payload.get("body", "")),
    )

def to_message_id(message_id: str) -> str:
    """Convert generic ID to service-compatible message ID string."""
    return str(message_id)
