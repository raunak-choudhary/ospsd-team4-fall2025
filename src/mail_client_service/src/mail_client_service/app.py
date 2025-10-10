"""FastAPI application wiring for the mail client service."""

from __future__ import annotations

from fastapi import FastAPI

# Import order: all imports first (avoid E402), then app creation.
import email_api  # noqa: F401
import gmail_impl  # noqa: F401  # importing performs DI to register Gmail client

from .routes import messages

app = FastAPI(title="Mail Client Service", version="0.1.0")
app.include_router(messages.router)
