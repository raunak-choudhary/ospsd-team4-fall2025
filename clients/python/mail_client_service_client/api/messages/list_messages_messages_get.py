from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_messages_messages_get_response_200_item import (
    ListMessagesMessagesGetResponse200Item,
)
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/messages",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list["ListMessagesMessagesGetResponse200Item"] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListMessagesMessagesGetResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list["ListMessagesMessagesGetResponse200Item"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[list["ListMessagesMessagesGetResponse200Item"]]:
    """List Messages

     Return a list of message summaries.

    Prefer `list_messages()` if available; otherwise fall back to `get_messages()`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ListMessagesMessagesGetResponse200Item']]
    """
    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> list["ListMessagesMessagesGetResponse200Item"] | None:
    """List Messages

     Return a list of message summaries.

    Prefer `list_messages()` if available; otherwise fall back to `get_messages()`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ListMessagesMessagesGetResponse200Item']
    """
    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[list["ListMessagesMessagesGetResponse200Item"]]:
    """List Messages

     Return a list of message summaries.

    Prefer `list_messages()` if available; otherwise fall back to `get_messages()`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['ListMessagesMessagesGetResponse200Item']]
    """
    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> list["ListMessagesMessagesGetResponse200Item"] | None:
    """List Messages

     Return a list of message summaries.

    Prefer `list_messages()` if available; otherwise fall back to `get_messages()`.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['ListMessagesMessagesGetResponse200Item']
    """
    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
