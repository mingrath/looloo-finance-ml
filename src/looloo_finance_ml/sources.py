"""Credential-gated Alpaca/SEC sources and read-only Webull comparison source."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import time
from typing import Any, Iterable
from urllib.parse import urlencode

import pandas as pd

from .config import RuntimeConfig
from .http import JsonResponse, request_json
from .calendar import CalendarError, XNYSCalendar
from .manifests import manifest_for_frame
from .schema import Bar, Manifest

ALPACA_SYMBOLS = "symbols"
ALLOWED_SEC_FORMS = frozenset({"10-Q", "10-Q/A", "10-K", "10-K/A"})


class DataError(RuntimeError):
    """Raised when a source cannot satisfy the frozen data contract."""


def _hash_pages(pages: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    for page in pages:
        digest.update(len(page).to_bytes(8, "big"))
        digest.update(page)
    return digest.hexdigest()


def _timestamp(value: Any) -> datetime:
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is None:
        parsed = parsed.tz_localize("UTC")
    return parsed.to_pydatetime().astimezone(timezone.utc)


def _bars_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    columns = (
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
    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=list(columns))
    frame["bar_end_at"] = pd.to_datetime(frame["bar_end_at"], utc=True)
    frame = frame.sort_values(["bar_end_at", "symbol"], ignore_index=True)
    for column in columns:
        if column not in frame:
            frame[column] = None
    return frame.loc[:, list(columns)]


@dataclass
class AlpacaBarsClient:
    api_key: str
    api_secret: str
    base_url: str = "https://data.alpaca.markets/v2"
    timeout: float = 30.0

    @classmethod
    def from_config(cls, config: RuntimeConfig | None = None) -> "AlpacaBarsClient":
        config = config or RuntimeConfig.from_env()
        key, secret = config.require_alpaca_credentials()
        return cls(key, secret, config.alpaca_data_url)

    def fetch_bars(
        self,
        symbols: tuple[str, ...],
        start: str,
        end: str,
        *,
        adjustment: str,
        stream: str,
        asof: str = "2025-12-31",
        retrieved_at: datetime | None = None,
    ) -> tuple[pd.DataFrame, Manifest]:
        expected_adjustment = {"feature_stream": "split", "label_fill_stream": "all"}.get(stream)
        if expected_adjustment is None or adjustment != expected_adjustment:
            raise DataError(f"invalid Alpaca stream/adjustment pair: {stream}/{adjustment}")
        symbols = tuple(symbol.upper() for symbol in symbols)
        params: dict[str, Any] = {
            "symbols": ",".join(symbols),
            "start": start,
            "end": end,
            "timeframe": "1Day",
            "feed": "sip",
            "adjustment": adjustment,
            "asof": asof,
            "currency": "USD",
            "sort": "asc",
            "limit": 10_000,
        }
        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Accept": "application/json",
        }
        calendar = XNYSCalendar()
        pages: list[bytes] = []
        rows: list[dict[str, Any]] = []
        seen_bars: set[tuple[str, datetime]] = set()
        seen_tokens: set[str] = set()
        page_token: str | None = None
        while True:
            query = dict(params)
            if page_token:
                query["page_token"] = page_token
            response = request_json(
                f"{self.base_url.rstrip('/')}/stocks/bars?{urlencode(query)}",
                headers=headers,
                timeout=self.timeout,
            )
            pages.append(response.body)
            payload = response.payload
            if not isinstance(payload, dict):
                raise DataError("Alpaca bars response must be a JSON object")
            bars_by_symbol = payload.get("bars")
            if not isinstance(bars_by_symbol, dict):
                raise DataError("Alpaca bars response has invalid or missing bars mapping")
            for symbol, bars in bars_by_symbol.items():
                if not isinstance(bars, list):
                    raise DataError(f"Alpaca bars for {symbol} are not a list")
                for bar in bars:
                    if not isinstance(bar, dict):
                        raise DataError("Alpaca bar is not an object")
                    raw_timestamp = _timestamp(bar["t"])
                    try:
                        session = calendar.session(raw_timestamp.date())
                    except CalendarError as exc:
                        raise DataError(
                            f"Alpaca bar timestamp is not an XNYS session: {bar['t']}"
                        ) from exc
                    key = (str(symbol).upper(), session.close_at)
                    if key in seen_bars:
                        raise DataError(f"duplicate Alpaca bar timestamp for {key[0]} at {key[1]}")
                    seen_bars.add(key)
                    item = {
                        "symbol": str(symbol).upper(),
                        "bar_end_at": session.close_at,
                        "open": float(bar["o"]),
                        "high": float(bar["h"]),
                        "low": float(bar["l"]),
                        "close": float(bar["c"]),
                        "volume": float(bar["v"]),
                        "source": "alpaca",
                        "adjustment": adjustment,
                        "raw_timestamp": raw_timestamp.isoformat(),
                    }
                    Bar(**item).validate()
                    rows.append(item)
            next_token = payload.get("next_page_token")
            if not next_token:
                break
            if next_token in seen_tokens:
                raise DataError("Alpaca pagination token repeated")
            seen_tokens.add(str(next_token))
            page_token = str(next_token)
        frame = _bars_frame(rows)
        missing_symbols = sorted(set(symbols).difference(frame["symbol"]))
        if missing_symbols:
            raise DataError(f"Alpaca returned no bars for requested symbols: {missing_symbols}")
        notes = ("raw_response_hash covers every page in order",)
        manifest = manifest_for_frame(
            frame,
            source="alpaca",
            stream=stream,
            params=params,
            symbols=symbols,
            start=start,
            end=end,
            raw_response_digest=_hash_pages(pages),
            retrieved_at=retrieved_at,
            notes=notes,
        )
        return frame, manifest


@dataclass
class SecClient:
    user_agent: str
    base_url: str = "https://data.sec.gov"
    sec_url: str = "https://www.sec.gov"
    timeout: float = 30.0

    @classmethod
    def from_config(cls, config: RuntimeConfig | None = None) -> "SecClient":
        config = config or RuntimeConfig.from_env()
        return cls(config.require_sec_user_agent())

    def _get(self, url: str) -> JsonResponse:
        time.sleep(0.11)
        return request_json(
            url,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
            timeout=self.timeout,
        )

    def ticker_map(self) -> tuple[dict[str, str], bytes]:
        response = self._get(f"{self.sec_url}/files/company_tickers.json")
        if not isinstance(response.payload, dict):
            raise DataError("SEC ticker map must be an object")
        result = {}
        for item in response.payload.values():
            if isinstance(item, dict) and item.get("ticker") and item.get("cik_str"):
                result[str(item["ticker"]).upper()] = str(int(item["cik_str"])).zfill(10)
        return result, response.body

    def _submissions(self, cik: str) -> tuple[dict[str, str], list[bytes]]:
        response = self._get(f"{self.base_url}/submissions/CIK{cik}.json")
        if not isinstance(response.payload, dict) or not isinstance(
            response.payload.get("filings"), dict
        ):
            raise DataError(f"SEC submissions for CIK {cik} are malformed")
        pages = [response.body]
        payloads = [response.payload]
        filings = response.payload["filings"]
        for item in filings.get("files", []) if isinstance(filings, dict) else []:
            name = item.get("name") if isinstance(item, dict) else None
            if not name:
                continue
            older = self._get(f"{self.base_url}/submissions/{name}")
            pages.append(older.body)
            if isinstance(older.payload, dict):
                payloads.append(older.payload)
        mapping: dict[str, str] = {}
        for payload in payloads:
            accession = payload.get("accessionNumber", [])
            accepted = payload.get("acceptanceDateTime", [])
            mapping.update({str(a): str(t) for a, t in zip(accession, accepted) if a and t})
            recent = (
                payload.get("filings", {}).get("recent", {})
                if isinstance(payload.get("filings"), dict)
                else {}
            )
            mapping.update(
                {
                    str(a): str(t)
                    for a, t in zip(
                        recent.get("accessionNumber", []), recent.get("acceptanceDateTime", [])
                    )
                    if a and t
                }
            )
        return mapping, pages

    def facts_for_cik(self, cik: str, symbol: str) -> tuple[pd.DataFrame, list[bytes]]:
        acceptance, submission_pages = self._submissions(cik)
        response = self._get(f"{self.base_url}/api/xbrl/companyfacts/CIK{cik}.json")
        payload = response.payload
        if not isinstance(payload, dict):
            raise DataError(f"SEC companyfacts for {symbol} must be an object")
        facts = payload.get("facts")
        if not isinstance(facts, dict):
            raise DataError(f"SEC facts for {symbol} are malformed")
        rows: list[dict[str, Any]] = []
        for taxonomy, tag_map in facts.items():
            if taxonomy not in {"us-gaap", "dei"} or not isinstance(tag_map, dict):
                continue
            for tag, definition in tag_map.items():
                if taxonomy == "dei" and tag != "EntityCommonStockSharesOutstanding":
                    continue
                units = definition.get("units", {}) if isinstance(definition, dict) else {}
                if not isinstance(units, dict):
                    continue
                for unit, observations in units.items():
                    if not isinstance(observations, list):
                        continue
                    for observation in observations:
                        if not isinstance(observation, dict):
                            continue
                        form = observation.get("form")
                        if form not in ALLOWED_SEC_FORMS:
                            continue
                        filed = observation.get("filed")
                        end = observation.get("end")
                        if not filed or not end or "val" not in observation:
                            continue
                        accession_number = str(observation.get("accn", ""))
                        accepted_at = acceptance.get(accession_number)
                        rows.append(
                            {
                                "symbol": symbol.upper(),
                                "taxonomy": taxonomy,
                                "tag": tag,
                                "value": observation["val"],
                                "unit": unit,
                                "period_start": pd.Timestamp(_timestamp(observation["start"]))
                                if observation.get("start")
                                else pd.NaT,
                                "period_end": pd.Timestamp(_timestamp(end)),
                                "filed_at": pd.Timestamp(_timestamp(filed)),
                                "accepted_at": pd.Timestamp(_timestamp(accepted_at))
                                if accepted_at
                                else pd.NaT,
                                "form": form,
                                "frame": observation.get("frame"),
                                "fiscal_year": observation.get("fy"),
                                "fiscal_period": observation.get("fp"),
                                "accession": accession_number,
                                "source_url": response.url,
                            }
                        )
        return pd.DataFrame(rows), [*submission_pages, response.body]

    def facts_for_symbols(self, symbols: tuple[str, ...]) -> tuple[pd.DataFrame, str]:
        ticker_map, ticker_page = self.ticker_map()
        pages: list[bytes] = [ticker_page]
        frames: list[pd.DataFrame] = []
        for symbol in symbols:
            cik = ticker_map.get(symbol.upper())
            if not cik:
                raise DataError(f"SEC ticker map has no CIK for {symbol}")
            frame, bodies = self.facts_for_cik(cik, symbol)
            pages.extend(bodies)
            frames.append(frame)
        result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return result, _hash_pages(pages)
