from __future__ import annotations

from datetime import datetime, timezone

import pytest
from looloo_finance_ml.http import JsonResponse
from looloo_finance_ml.sources import AlpacaBarsClient, DataError, SecClient

from looloo_finance_ml.config import ConfigError, RuntimeConfig
from looloo_finance_ml.schema import Bar, Event
from looloo_finance_ml.webull import WebullComparisonError, normalize_webull_bars


def test_alpaca_live_fetch_paginates_and_preserves_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [
        JsonResponse(
            "first",
            200,
            b"first",
            {
                "bars": {
                    "AAPL": [
                        {"t": "2021-01-04T21:00:00Z", "o": 1, "h": 2, "l": 1, "c": 1.5, "v": 10}
                    ]
                },
                "next_page_token": "next",
            },
        ),
        JsonResponse(
            "second",
            200,
            b"second",
            {
                "bars": {
                    "AAPL": [
                        {"t": "2021-01-05T21:00:00Z", "o": 2, "h": 3, "l": 2, "c": 2.5, "v": 20}
                    ]
                },
                "next_page_token": None,
            },
        ),
    ]
    urls: list[str] = []

    def request(url: str, **_: object) -> JsonResponse:
        urls.append(url)
        return pages[len(urls) - 1]

    monkeypatch.setattr("looloo_finance_ml.sources.request_json", request)
    frame, manifest = AlpacaBarsClient("key", "secret").fetch_bars(
        ("AAPL",), "2021-01-04", "2021-01-06", adjustment="split", stream="feature_stream"
    )
    assert frame["bar_end_at"].nunique() == 2
    assert "page_token=next" in urls[1]
    assert manifest.stream == "feature_stream"


def test_alpaca_rejects_mismatched_stream_and_adjustment() -> None:
    with pytest.raises(DataError, match="stream/adjustment"):
        AlpacaBarsClient("key", "secret").fetch_bars(
            ("AAPL",), "2021-01-04", "2021-01-06", adjustment="all", stream="feature_stream"
        )


def test_sec_provenance_hash_covers_ticker_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    ticker_body = [b"ticker-map-v1"]

    def get(_: SecClient, url: str) -> JsonResponse:
        if url.endswith("company_tickers.json"):
            return JsonResponse(
                url, 200, ticker_body[0], {"0": {"ticker": "AAPL", "cik_str": 320193}}
            )
        if "/submissions/" in url:
            return JsonResponse(url, 200, b"submissions", {"filings": {"recent": {}, "files": []}})
        return JsonResponse(url, 200, b"facts", {"facts": {}})

    monkeypatch.setattr(SecClient, "_get", get)
    client = SecClient("Researcher researcher@example.com")
    _, first_hash = client.facts_for_symbols(("AAPL",))
    ticker_body[0] = b"ticker-map-v2"
    _, second_hash = client.facts_for_symbols(("AAPL",))

    assert first_hash != second_hash


def test_webull_comparison_normalizes_common_fields_without_canonical_fallback() -> None:
    payload = {
        "bars": [
            {
                "timestamp": "2021-01-04T21:00:00+00:00",
                "open": "1",
                "high": "2",
                "low": "1",
                "close": "1.5",
                "volume": "10",
                "adjustment": "forward_adjusted",
            }
        ]
    }
    result = normalize_webull_bars(payload, symbol="aapl", raw_body=b"fixture", requested_count=2)
    assert result.frame.iloc[0]["symbol"] == "AAPL"
    assert result.frame.iloc[0]["adjustment"] == "forward_adjusted"
    assert "coverage_unproven" in result.diagnostics
    assert result.raw_response_hash


def test_webull_rejects_non_forward_adjusted_payload() -> None:
    payload = {
        "bars": [
            {
                "timestamp": "2021-01-04T21:00:00+00:00",
                "open": 1,
                "high": 2,
                "low": 1,
                "close": 1.5,
                "volume": 10,
                "adjustment": "unadjusted",
            }
        ]
    }
    with pytest.raises(WebullComparisonError, match="forward_adjusted_only"):
        normalize_webull_bars(payload, symbol="AAPL")


def test_schema_rejects_naive_or_nonfinite_values_and_reserved_event_fields() -> None:
    with pytest.raises(ValueError):
        Bar("AAPL", datetime(2021, 1, 1), 1, 1, 1, 1, 1, "fixture", "split")
    with pytest.raises(ValueError):
        Bar(
            "AAPL",
            datetime(2021, 1, 1, tzinfo=timezone.utc),
            float("inf"),
            1,
            1,
            1,
            1,
            "fixture",
            "split",
        )
    with pytest.raises(ValueError, match="collides"):
        Event(
            "run",
            "event",
            "v1",
            "code",
            datetime(2021, 1, 1, tzinfo=timezone.utc),
            0,
            "mark",
            fields={"event_seq": 1},
        )


def test_webull_environment_and_credentials_are_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEBULL_ENV", "bad")
    with pytest.raises(ConfigError, match="WEBULL_ENV"):
        RuntimeConfig.from_env()
