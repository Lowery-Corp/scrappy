from collections.abc import AsyncIterator
from typing import Any

from httpx import HTTPStatusError

from core.config import settings
from httpxC.http_client import http_client


class OpenAIRepositoryError(Exception):
    pass


def _headers() -> dict[str, str]:
    if settings.openai_api_key is None:
        raise OpenAIRepositoryError("OPENAI_API_KEY is not configured")

    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    base_url = settings.openai_api_url.rstrip("/")
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{normalized_path}"


async def _request_json(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        response = await http_client.request(
            method,
            _url(path),
            headers=_headers(),
            json=json,
            params=params,
        )
        response.raise_for_status()
        data = response.json()
    except HTTPStatusError as exc:
        raise OpenAIRepositoryError(exc.response.text) from exc

    if not isinstance(data, dict):
        raise OpenAIRepositoryError("OpenAI API returned an unexpected response")

    return data


async def create_openai_conversation(
    *,
    metadata: dict[str, Any] | None = None,
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if metadata is not None:
        body["metadata"] = metadata
    if items is not None:
        body["items"] = items

    return await _request_json("POST", "/v1/conversations", json=body)


async def retrieve_openai_conversation(openai_conversation_id: str) -> dict[str, Any]:
    return await _request_json("GET", f"/v1/conversations/{openai_conversation_id}")


async def update_openai_conversation(
    openai_conversation_id: str,
    *,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return await _request_json(
        "POST",
        f"/v1/conversations/{openai_conversation_id}",
        json={"metadata": metadata},
    )


async def delete_openai_conversation(openai_conversation_id: str) -> dict[str, Any]:
    return await _request_json("DELETE", f"/v1/conversations/{openai_conversation_id}")


async def create_openai_conversation_item(
    openai_conversation_id: str,
    item: dict[str, Any],
) -> dict[str, Any]:
    return await _request_json(
        "POST",
        f"/v1/conversations/{openai_conversation_id}/items",
        json=item,
    )


async def retrieve_openai_conversation_item(
    openai_conversation_id: str,
    item_id: str,
) -> dict[str, Any]:
    return await _request_json(
        "GET",
        f"/v1/conversations/{openai_conversation_id}/items/{item_id}",
    )


async def list_openai_conversation_items(
    openai_conversation_id: str,
    *,
    limit: int | None = None,
    order: str | None = None,
    after: str | None = None,
) -> dict[str, Any]:
    params = {
        key: value
        for key, value in {
            "limit": limit,
            "order": order,
            "after": after,
        }.items()
        if value is not None
    }
    return await _request_json(
        "GET",
        f"/v1/conversations/{openai_conversation_id}/items",
        params=params,
    )


async def delete_openai_conversation_item(
    openai_conversation_id: str,
    item_id: str,
) -> dict[str, Any]:
    return await _request_json(
        "DELETE",
        f"/v1/conversations/{openai_conversation_id}/items/{item_id}",
    )


async def create_openai_response(
    *,
    input: str | list[dict[str, Any]],
    model: str | None = None,
    conversation: str | dict[str, Any] | None = None,
    instructions: str | None = None,
    metadata: dict[str, Any] | None = None,
    stream: bool = False,
    **extra_body: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model or settings.openai_default_model,
        "input": input,
        **extra_body,
    }
    if conversation is not None:
        body["conversation"] = conversation
    if instructions is not None:
        body["instructions"] = instructions
    if metadata is not None:
        body["metadata"] = metadata
    if stream is True:
        body["stream"] = True

    return await _request_json("POST", "/v1/responses", json=body)


async def retrieve_openai_response(response_id: str) -> dict[str, Any]:
    return await _request_json("GET", f"/v1/responses/{response_id}")


async def cancel_openai_response(response_id: str) -> dict[str, Any]:
    return await _request_json("POST", f"/v1/responses/{response_id}/cancel")


async def delete_openai_response(response_id: str) -> dict[str, Any]:
    return await _request_json("DELETE", f"/v1/responses/{response_id}")


async def stream_openai_response(
    *,
    input: str | list[dict[str, Any]],
    model: str | None = None,
    conversation: str | dict[str, Any] | None = None,
    instructions: str | None = None,
    metadata: dict[str, Any] | None = None,
    **extra_body: Any,
) -> AsyncIterator[str]:
    body: dict[str, Any] = {
        "model": model or settings.openai_default_model,
        "input": input,
        "stream": True,
        **extra_body,
    }
    if conversation is not None:
        body["conversation"] = conversation
    if instructions is not None:
        body["instructions"] = instructions
    if metadata is not None:
        body["metadata"] = metadata

    async with http_client.stream(
        "POST",
        _url("/v1/responses"),
        headers=_headers(),
        json=body,
    ) as response:
        try:
            response.raise_for_status()
        except HTTPStatusError as exc:
            error_body = await response.aread()
            raise OpenAIRepositoryError(error_body.decode()) from exc

        async for line in response.aiter_lines():
            if line:
                yield line


def get_response_output_text(response: dict[str, Any]) -> str:
    output_text = response.get("output_text")
    if isinstance(output_text, str):
        return output_text

    text_parts: list[str] = []
    for output_item in response.get("output", []):
        if not isinstance(output_item, dict):
            continue

        for content_item in output_item.get("content", []):
            if not isinstance(content_item, dict):
                continue

            text = content_item.get("text")
            if isinstance(text, str):
                text_parts.append(text)

    return "".join(text_parts)
