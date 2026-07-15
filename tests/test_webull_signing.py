from __future__ import annotations

import base64
import hashlib
import hmac
from urllib.parse import quote

from looloo_finance_ml.webull import webull_signature


def test_webull_sha256_signature_uses_only_documented_signed_headers() -> None:
    secret = "secret"
    path = "/openapi/market-data/stock/bars"
    query = {"symbol": "AAPL", "category": "US_STOCK"}
    headers = {
        "host": "api.example.test",
        "x-app-key": "app",
        "x-signature-algorithm": "HMAC-SHA256",
        "x-signature-nonce": "nonce",
        "x-signature-version": "1.0",
        "x-timestamp": "2026-07-13T00:00:00Z",
        "x-access-token": "must-not-be-signed",
        "Accept": "application/json",
    }
    body = b'{"x":1}'
    pairs = sorted(
        [
            ("category", "US_STOCK"),
            ("symbol", "AAPL"),
            ("host", "api.example.test"),
            ("x-app-key", "app"),
            ("x-signature-algorithm", "HMAC-SHA256"),
            ("x-signature-nonce", "nonce"),
            ("x-signature-version", "1.0"),
            ("x-timestamp", "2026-07-13T00:00:00Z"),
        ]
    )
    canonical = (
        path
        + "&"
        + "&".join(f"{name}={value}" for name, value in pairs)
        + "&"
        + hashlib.sha256(body).hexdigest().upper()
    )
    expected = base64.b64encode(
        hmac.new(
            (secret + "&").encode(), quote(canonical, safe="").encode(), hashlib.sha256
        ).digest()
    ).decode()
    assert webull_signature(secret, path=path, query=query, headers=headers, body=body) == expected
