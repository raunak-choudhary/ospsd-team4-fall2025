from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_message_messages_message_id_delete_response_delete_message_messages_message_id_delete import (
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    message_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/messages/{message_id}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete
    | HTTPValidationError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete
    | HTTPValidationError
]:
    """Delete Message

     Delete a message.

    Args:
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete, HTTPValidationError]]
    """
    kwargs = _get_kwargs(
        message_id=message_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete
    | HTTPValidationError
    | None
):
    """Delete Message

     Delete a message.

    Args:
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete, HTTPValidationError]
    """
    return sync_detailed(
        message_id=message_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete
    | HTTPValidationError
]:
    """Delete Message

     Delete a message.

    Args:
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete, HTTPValidationError]]
    """
    kwargs = _get_kwargs(
        message_id=message_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete
    | HTTPValidationError
    | None
):
    """Delete Message

     Delete a message.

    Args:
        message_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeleteMessageMessagesMessageIdDeleteResponseDeleteMessageMessagesMessageIdDelete, HTTPValidationError]
    """
    return (
        await asyncio_detailed(
            message_id=message_id,
            client=client,
        )
    ).parsed
