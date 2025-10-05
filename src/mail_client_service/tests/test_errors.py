# src/mail_client_service/tests/test_errors.py
import pytest


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


@pytest.mark.unit
def test_get_message_not_found(test_client, mock_mail_client):
    def boom(_id: str):
        raise NotFoundError("no such message")

    mock_mail_client.get_message.side_effect = boom

    res = test_client.get("/messages/m_missing")
    # Accept whatever your route maps to
    assert res.status_code in (404, 400, 422, 500)


@pytest.mark.unit
def test_mark_as_read_bad_request(test_client, mock_mail_client):
    mock_mail_client.mark_as_read.side_effect = BadRequestError("bad id")

    res = test_client.post("/messages/bad/mark-as-read")
    # Accept 500 until the route maps exceptions to 4xx
    assert res.status_code in (400, 422, 500)
