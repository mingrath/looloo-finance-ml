"""Small standard-library HTTP helper with exact-body capture."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class HttpError(RuntimeError):
    """Raised for transport, HTTP, or JSON failures."""


@dataclass(frozen=True)
class JsonResponse:
    url: str
    status: int
    body: bytes
    payload: object


def request_json(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    method: str = "GET",
    body: bytes | None = None,
    timeout: float = 30.0,
) -> JsonResponse:
    request = Request(url, data=body, headers=dict(headers or {}), method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = int(response.status)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise HttpError(f"request failed for {url}: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HttpError(f"response was not JSON for {url}") from exc
    return JsonResponse(url=url, status=status, body=raw, payload=payload)
