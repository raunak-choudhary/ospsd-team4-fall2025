import email_api
from mail_client_adapter.src.mail_client_adapter.adapter import ServiceBackedClient


def test_list_messages_unit(monkeypatch):
    """Unit test for list_messages with a fake response."""

    # Fake API response simulating one message
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

    # Patch the adapter’s imported API function (correct path)
    import mail_client_adapter.src.mail_client_adapter.adapter as adapter_module
    monkeypatch.setattr(
        adapter_module.api_list_messages,
        "sync",
        fake_sync,
    )

    # Create the adapter client (base_url is irrelevant for mock)
    client = ServiceBackedClient(base_url="http://irrelevant")

    # Call list_messages (should trigger our fake_sync)
    emails = client.list_messages()

    # Verify expected results
    assert len(emails) == 1
    assert isinstance(emails[0], email_api.Email)
    assert emails[0].subject == "Hello"

