"""Read-only Webull comparison adapter; never a canonical data fallback."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
import os
from typing import Any, Iterable, Mapping
from urllib.parse import quote, urlencode
from uuid import uuid4

import pandas as pd

from .config import ConfigError, RuntimeConfig
from .hashing import sha256_bytes
from .http import JsonResponse, request_json


class WebullComparisonError(RuntimeError):
    """Raised when Webull comparison data cannot be normalized safely."""


@dataclass(frozen=True)
class WebullComparison:
    frame: pd.DataFrame
    raw_response_hash: str
    diagnostics: tuple[str, ...]
    source_url: str | None = None


def compact_json(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def webull_signature(
    app_secret: str,
    *,
    path: str,
    query: Mapping[str, str | int | float | list[str]] = (),
    headers: Mapping[str, str] = (),
    body: bytes = b"",
) -> str:
    """Create the documented HMAC-SHA256 signature without transmitting app_secret."""
    allowed = {
        "host",
        "x-app-key",
        "x-signature-algorithm",
        "x-signature-nonce",
        "x-signature-version",
        "x-timestamp",
    }
    signed = {
        str(name).lower(): value
        for name, value in dict(headers).items()
        if str(name).lower() in allowed
    }
    pairs: list[tuple[str, str]] = []
    for name, value in query.items():
        values = value if isinstance(value, list) else [value]
        pairs.extend((str(name), str(item)) for item in values)
    pairs.extend((name, str(value)) for name, value in signed.items())
    pairs.sort()
    canonical = path + "&" + "&".join(f"{name}={value}" for name, value in pairs)
    if body:
        canonical += "&" + hashlib.sha256(body).hexdigest().upper()
    encoded = quote(canonical, safe="")
    key = (app_secret + "&").encode("utf-8")
    return base64.b64encode(hmac.new(key, encoded.encode("utf-8"), hashlib.sha256).digest()).decode(
        "ascii"
    )


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise WebullComparisonError(f"schema_mismatch: {field} is not numeric") from exc
    if not pd.notna(number) or number <= 0:
        raise WebullComparisonError(f"schema_mismatch: {field} must be positive")
    return number


def _timestamp(value: Any) -> pd.Timestamp:
    if isinstance(value, (int, float)):
        value = float(value)
        value = value / 1000.0 if abs(value) > 10**11 else value
        parsed = pd.to_datetime(value, unit="s", utc=True)
    else:
        parsed = pd.Timestamp(value)
        if parsed.tzinfo is None:
            raise WebullComparisonError("schema_mismatch: bar timestamp lacks timezone")
        parsed = parsed.tz_convert("UTC")
    return pd.Timestamp(parsed)


def _bar_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        candidate = payload.get(
            "bars", payload.get("data", payload.get("items", payload.get("list")))
        )
        if isinstance(candidate, dict):
            candidate = candidate.get("bars", candidate.get("items", candidate.get("list")))
        items = candidate
    else:
        items = None
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise WebullComparisonError("schema_mismatch: expected a bar list")
    return items


def normalize_webull_bars(
    payload: Any,
    *,
    symbol: str,
    raw_body: bytes = b"",
    source_url: str | None = None,
    requested_count: int | None = None,
) -> WebullComparison:
    """Normalize common Webull daily-bar fields into a separately named frame."""
    items = _bar_items(payload)
    rows: list[dict[str, Any]] = []
    diagnostics: list[str] = []
    seen: set[pd.Timestamp] = set()
    for item in items:
        raw_timestamp = item.get("timestamp", item.get("time", item.get("ts", item.get("t"))))
        timestamp = _timestamp(raw_timestamp)
        if timestamp in seen:
            raise WebullComparisonError("schema_mismatch: duplicate bar timestamp")
        seen.add(timestamp)
        open_ = _number(item.get("open", item.get("o")), "open")
        high = _number(item.get("high", item.get("h")), "high")
        low = _number(item.get("low", item.get("l")), "low")
        close = _number(item.get("close", item.get("c")), "close")
        volume = _number(item.get("volume", item.get("v")), "volume")
        if high < max(open_, close) or low > min(open_, close):
            raise WebullComparisonError("schema_mismatch: malformed OHLC")
        adjustment = str(item.get("adjustment", item.get("adjusted", "forward_adjusted"))).lower()
        if adjustment not in {"forward_adjusted", "forward-adjusted", "adjusted", "qfq", "hfq"}:
            diagnostics.append("forward_adjusted_only")
            raise WebullComparisonError(
                "forward_adjusted_only: daily Webull bars must be forward-adjusted"
            )
        rows.append(
            {
                "symbol": symbol.upper(),
                "bar_end_at": timestamp,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "source": "webull",
                "adjustment": "forward_adjusted",
                "raw_timestamp": str(raw_timestamp),
            }
        )
    columns = [
        "symbol",
        "bar_end_at",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "adjustment",
        "raw_timestamp",
    ]
    frame = (
        pd.DataFrame(rows).sort_values("bar_end_at", ignore_index=True)
        if rows
        else pd.DataFrame(columns=columns)
    )
    diagnostics.append("coverage_unproven")
    raw = raw_body or json.dumps(payload, sort_keys=True).encode("utf-8")
    return WebullComparison(
        frame=frame,
        raw_response_hash=sha256_bytes(raw),
        diagnostics=tuple(dict.fromkeys(diagnostics)),
        source_url=source_url,
    )


@dataclass
class WebullClient:
    app_key: str
    app_secret: str
    config: RuntimeConfig
    timeout: float = 30.0
    token_path: str = "/openapi/auth/token/create"
    snapshot_path: str = "/openapi/market-data/stock/snapshot"
    bars_path: str = "/openapi/market-data/stock/bars"
    active_token: str | None = None

    @classmethod
    def from_config(cls, config: RuntimeConfig | None = None) -> "WebullClient":
        config = config or RuntimeConfig.from_env()
        if config.webull_env not in {"uat", "production"}:
            raise ConfigError("invalid Webull environment")
        app_key, app_secret = config.require_webull_credentials()
        return cls(app_key, app_secret, config, active_token=os.getenv("WEBULL_ACCESS_TOKEN"))

    def _url(self, path: str) -> str:
        return f"{self.config.webull_base_url.rstrip('/')}/{path.lstrip('/')}"

    def _signed_request(
        self,
        path: str,
        *,
        method: str = "GET",
        query: Mapping[str, str | int | float | list[str]] | None = None,
        body: Any = None,
        access_token: str | None = None,
    ) -> JsonResponse:
        params = dict(query or {})
        body_bytes = compact_json(body) if body is not None else b""
        host = self.config.webull_base_url.split("//", 1)[-1].split("/", 1)[0]
        headers: dict[str, str] = {
            "x-app-key": self.app_key,
            "x-signature-algorithm": "HMAC-SHA256",
            "x-signature-version": "1.0",
            "x-signature-nonce": uuid4().hex,
            "x-timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "x-version": "v2",
            "host": host,
            "Accept": "application/json",
        }
        if body_bytes:
            headers["Content-Type"] = "application/json"
        if access_token:
            headers["x-access-token"] = access_token
        headers["x-signature"] = webull_signature(
            self.app_secret, path=path, query=params, headers=headers, body=body_bytes
        )
        url = self._url(path)
        if params:
            url += "?" + urlencode(params, doseq=True)
        return request_json(
            url, method=method, body=body_bytes or None, headers=headers, timeout=self.timeout
        )

    def access_token(self) -> tuple[str, JsonResponse]:
        response = self._signed_request(self.token_path, method="POST")
        payload = response.payload
        data = (
            payload.get("data")
            if isinstance(payload, dict) and isinstance(payload.get("data"), dict)
            else payload
        )
        token = data.get("token", data.get("access_token")) if isinstance(data, dict) else None
        status = str(data.get("status", "")).upper() if isinstance(data, dict) else ""
        if not token:
            raise WebullComparisonError("schema_mismatch: token response has no token")
        if status and status != "NORMAL":
            raise WebullComparisonError(
                "token_pending_verification: verify the token in the Webull app before comparison"
            )
        self.active_token = str(token)
        return str(token), response

    def discover_symbol(self, symbol: str, token: str) -> tuple[str, JsonResponse]:
        """Use the documented snapshot endpoint to prove the symbol is recognized."""
        response = self._signed_request(
            self.snapshot_path,
            query={"symbols": symbol.upper(), "category": "US_STOCK"},
            access_token=token,
        )
        payload = response.payload
        candidate = payload.get("data", payload) if isinstance(payload, dict) else payload
        if isinstance(candidate, dict):
            candidate = candidate.get("items", candidate.get("list", [candidate]))
        items = candidate if isinstance(candidate, list) else []
        for item in items:
            if isinstance(item, dict):
                returned = str(item.get("symbol", item.get("ticker", symbol))).upper()
                if returned == symbol.upper():
                    return returned, response
        raise WebullComparisonError("coverage_unproven: snapshot did not recognize symbol")

    def historical_bars(
        self, symbol: str, *, end: str | None = None, count: int = 120, timespan: str = "D"
    ) -> WebullComparison:
        if not 1 <= count <= 1200 or timespan != "D":
            raise WebullComparisonError(
                "schema_mismatch: daily bars require count 1..1200 and timespan D"
            )
        if self.active_token:
            token = self.active_token
            token_body = b""
        else:
            token, token_response = self.access_token()
            token_body = token_response.body
        discovered, discovery_response = self.discover_symbol(symbol, token)
        params: dict[str, str | int] = {
            "symbol": discovered,
            "category": "US_STOCK",
            "timespan": timespan,
            "count": count,
            "real_time_required": "false",
        }
        if end:
            params["end"] = end
        response = self._signed_request(self.bars_path, query=params, access_token=token)
        comparison = normalize_webull_bars(
            response.payload,
            symbol=discovered,
            raw_body=response.body,
            source_url=response.url,
            requested_count=count,
        )
        digest = sha256_bytes(token_body + discovery_response.body + response.body)
        return WebullComparison(comparison.frame, digest, comparison.diagnostics, response.url)


def compare_webull_payloads(
    payloads: Iterable[tuple[str, Any, bytes]], *, requested_count: int | None = None
) -> pd.DataFrame:
    """Normalize multiple symbols for comparison output; never feeds canonical builders."""
    comparisons = [
        normalize_webull_bars(
            payload, symbol=symbol, raw_body=body, requested_count=requested_count
        )
        for symbol, payload, body in payloads
    ]
    if not comparisons:
        return pd.DataFrame()
    return pd.concat([comparison.frame for comparison in comparisons], ignore_index=True)
