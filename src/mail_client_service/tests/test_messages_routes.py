# src/mail_client_service/tests/test_messages_routes.py
import pytest


@pytest.mark.unit
class TestMessagesRoutes:
    def test_list_messages_ok(self, test_client, mock_mail_client):
        res = test_client.get("/messages?limit=1")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert data[0]["id"] == "m_123"
        # Your route calls list_messages(), not get_messages()
        mock_mail_client.list_messages.assert_called_once()

    def test_get_message_ok(self, test_client, mock_mail_client):
        res = test_client.get("/messages/m_123")
        assert res.status_code == 200
        assert res.json()["id"] == "m_123"
        mock_mail_client.get_message.assert_called_once_with("m_123")

    def test_mark_as_read_ok(self, test_client, mock_mail_client):
        res = test_client.post("/messages/m_123/mark-as-read")
        assert res.status_code == 200
        assert res.json()["is_read"] is True
        mock_mail_client.mark_as_read.assert_called_once_with("m_123")

    def test_delete_message_ok(self, test_client, mock_mail_client):
        res = test_client.delete("/messages/m_123")
        assert res.status_code == 200
        assert res.json()["ok"] is True
        mock_mail_client.delete_message.assert_called_once_with("m_123")
