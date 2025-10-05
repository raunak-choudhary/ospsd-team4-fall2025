# src/mail_client_service/tests/conftest.py
from typing import Generator

import pathlib
import sys
import types
import importlib.util
import pytest
from fastapi.testclient import TestClient

# ---------- Paths ----------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SERVICE_SRC_ROOT = (
    REPO_ROOT / "src" / "mail_client_service" / "src"
)  # .../src/mail_client_service/src
SERVICE_PKG_DIR = (
    SERVICE_SRC_ROOT / "mail_client_service"
)  # .../src/mail_client_service/src/mail_client_service
APP_FILE = SERVICE_PKG_DIR / "app.py"

EMAIL_API_SRC_ROOT = REPO_ROOT / "src" / "email_api" / "src"  # .../src/email_api/src

# Add inner src roots so imports inside app.py resolve (e.g., email_api)
for p in (SERVICE_SRC_ROOT, EMAIL_API_SRC_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

# ---------- Stub gmail_impl (avoid wiring real Gmail during unit tests) ----------
if "gmail_impl" not in sys.modules:
    sys.modules["gmail_impl"] = types.ModuleType("gmail_impl")

# ---------- Create runtime package and load app.py as mail_client_service.app ----------
if not APP_FILE.exists():
    raise ImportError(f"app.py not found at expected path: {APP_FILE}")

# Ensure top-level package exists with the CORRECT __path__ (== package dir)
PKG_NAME = "mail_client_service"
if PKG_NAME not in sys.modules:
    pkg = types.ModuleType(PKG_NAME)
    pkg.__path__ = [str(SERVICE_PKG_DIR)]  # point to the package folder
    sys.modules[PKG_NAME] = pkg

# Load app.py as submodule "mail_client_service.app" so relative imports ('.routes') work
SUBMOD_NAME = "mail_client_service.app"
spec = importlib.util.spec_from_file_location(
    SUBMOD_NAME, APP_FILE, submodule_search_locations=[str(SERVICE_PKG_DIR)]
)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not create spec for {SUBMOD_NAME} at {APP_FILE}")

mod = importlib.util.module_from_spec(spec)
sys.modules[SUBMOD_NAME] = mod
spec.loader.exec_module(mod)  # type: ignore[attr-defined]

if not hasattr(mod, "app"):
    raise ImportError(
        f"{APP_FILE} loaded as {SUBMOD_NAME}, but no global `app` was found."
    )
app = getattr(mod, "app")


# ---------- Fixtures ----------
@pytest.fixture()
def test_client() -> Generator[TestClient, None, None]:
    # prevent server exceptions from bubbling; we want HTTP responses for error-path tests
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture()
def mock_mail_client(monkeypatch):
    """Patch email_api.get_client to return a mock client with expected methods."""
    from unittest.mock import Mock
    import email_api  # resolves from src/email_api/src

    mock = Mock()

    # Your service calls list_messages(...) for GET /messages
    mock.list_messages.return_value = [
        {
            "id": "m_123",
            "sender": {"address": "alice@example.com"},
            "subject": "Hello",
            "snippet": "Preview…",
            "is_read": False,
        }
    ]

    # Keep these for other routes
    mock.get_messages.return_value = mock.list_messages.return_value
    mock.get_message.return_value = {
        "id": "m_123",
        "sender": {"address": "alice@example.com"},
        "subject": "Hello",
        "body": "Long body",
        "is_read": False,
    }
    mock.mark_as_read.return_value = {"id": "m_123", "is_read": True}
    mock.delete_message.return_value = {"ok": True}

    # Service uses our mock instead of a live client
    monkeypatch.setattr(email_api, "get_client", lambda: mock)
    return mock
