"""Unit test for ServiceBackedClient adapter."""

import sys
import pathlib
import email_api

# -----------------------------------------------------------------------------
# 🔧 PATH FIX — ensure Python finds all nested packages correctly
# -----------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parents[3]
ADAPTER_SRC = ROOT / "src" / "mail_client_adapter" / "src"
CLIENTS_SRC = ROOT / "clients" / "python"

# Add both adapter and generated-client directories to sys.path
for path in (ADAPTER_SRC, CLIENTS_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# -----------------------------------------------------------------------------
# ✅ IMPORTS (work after sys.path fix)
# -----------------------------------------------------------------------------
from mail_client_adapter.adapter import ServiceBackedClient
import mail_client_adapter.adapter as adapter_module


# -----------------------------------------------------------------------------
# 🧪 TESTS
# -----------------------------------------------------------------------------
def test_list_messages_unit(monkeypatch):
    """Unit test for list_messages with a fake response."""

    # Step 1: Fake API response simulating one message
    def fake_sync(**kwargs):
        return [
            {
                "id": "1",
                "subject": "Hello",
                "from": "a@b.com",
                "body": "test",
                "is_read": False,
            }
        ]

    # Step 2: Monkeypatch the adapter’s API call
    monkeypatch.setattr(adapter_module.api_list_messages, "sync", fake_sync)

    # Step 3: Instantiate the adapter client (base_url irrelevant for mock)
    client = ServiceBackedClient(base_url="http://irrelevant")

    # Step 4: Execute the method under test
    emails = list(client.get_messages())

    # Step 5: Assertions — verify correctness
    assert len(emails) == 1
    assert isinstance(emails[0], email_api.Email)
    assert emails[0].subject == "Hello"
    assert emails[0].sender.address == "a@b.com"
    assert not emails[0].is_read if hasattr(emails[0], "is_read") else True
