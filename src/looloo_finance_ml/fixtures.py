"""Deterministic synthetic fixtures used by offline tests and smoke runs."""

from __future__ import annotations

from datetime import date
import hashlib

import numpy as np
import pandas as pd

from .calendar import XNYSCalendar

FROZEN_SYMBOLS = (
    "AAPL",
    "AMD",
    "ABBV",
    "AMZN",
    "BAC",
    "CAT",
    "CSCO",
    "CVX",
    "DIS",
    "GOOGL",
    "HD",
    "IBM",
    "JNJ",
    "JPM",
    "KO",
    "MA",
    "META",
    "MRK",
    "MSFT",
    "NFLX",
    "NKE",
    "NVDA",
    "ORCL",
    "PEP",
    "PG",
    "TMO",
    "UNH",
    "V",
    "WMT",
    "XOM",
)
FEATURE_ADJUSTMENT = "split"
LABEL_FILL_ADJUSTMENT = "all"


def _seed(symbol: str, seed: int) -> int:
    digest = hashlib.sha256(f"{symbol}:{seed}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % (2**32)


def synthetic_bars(
    start: date | str = "2021-01-04",
    end: date | str = "2021-06-30",
    symbols: tuple[str, ...] = FROZEN_SYMBOLS,
    *,
    adjustment: str = FEATURE_ADJUSTMENT,
    seed: int = 20250713,
) -> pd.DataFrame:
    """Return valid deterministic daily bars with UTC session-close timestamps."""
    sessions = XNYSCalendar().sessions(start, end)
    rows: list[dict[str, object]] = []
    for symbol in symbols:
        rng = np.random.default_rng(_seed(symbol, seed))
        price = 25.0 + float(rng.uniform(10, 180))
        for session in sessions:
            ret = float(rng.normal(0.0002, 0.012))
            open_price = price * (1.0 + float(rng.normal(0.0, 0.002)))
            close = max(0.01, open_price * (1.0 + ret))
            high = max(open_price, close) * (1.0 + abs(float(rng.normal(0.0, 0.004))))
            low = min(open_price, close) * (1.0 - abs(float(rng.normal(0.0, 0.004))))
            volume = max(1.0, float(rng.lognormal(15.0, 0.25)))
            rows.append(
                {
                    "symbol": symbol,
                    "bar_end_at": session.close_at,
                    "open": round(open_price, 6),
                    "high": round(high, 6),
                    "low": round(low, 6),
                    "close": round(close, 6),
                    "volume": round(volume, 3),
                    "source": "synthetic",
                    "adjustment": adjustment,
                    "raw_timestamp": session.close_at.isoformat(),
                }
            )
            price = close
    return pd.DataFrame(rows).sort_values(["bar_end_at", "symbol"], ignore_index=True)


def synthetic_sec_facts(
    start: date | str = "2018-01-01",
    end: date | str = "2025-12-31",
    symbols: tuple[str, ...] = FROZEN_SYMBOLS,
) -> pd.DataFrame:
    """Return filed-time facts with enough quarters for exact TTM tests."""
    period_ends = pd.date_range(start, end, freq="QE", tz="UTC")
    rows: list[dict[str, object]] = []
    for symbol_index, symbol in enumerate(symbols):
        for index, period_end in enumerate(period_ends):
            period_start = period_end - pd.Timedelta(days=88)
            filed = period_end + pd.Timedelta(days=35)
            base = 100.0 + symbol_index * 3.0 + index * 2.0
            common = {
                "symbol": symbol,
                "taxonomy": "us-gaap",
                "unit": "USD",
                "period_start": period_start,
                "period_end": period_end,
                "filed_at": filed,
                "accepted_at": filed,
                "form": "10-Q",
                "frame": f"CY{period_end.year}Q{period_end.quarter}",
            }
            rows.extend(
                [
                    {**common, "tag": "Revenues", "value": base * 10},
                    {**common, "tag": "OperatingIncomeLoss", "value": base * 2},
                    {**common, "tag": "Assets", "value": base * 50, "period_start": pd.NaT},
                    {
                        **common,
                        "tag": "CashAndCashEquivalentsAtCarryingValue",
                        "value": base * 8,
                        "period_start": pd.NaT,
                    },
                    {
                        **common,
                        "tag": "LongTermDebtAndFinanceLeaseObligationsCurrent",
                        "value": base * 5,
                        "period_start": pd.NaT,
                    },
                    {
                        **common,
                        "tag": "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
                        "value": base * 10,
                        "period_start": pd.NaT,
                    },
                    {
                        **common,
                        "tag": "WeightedAverageNumberOfDilutedSharesOutstanding",
                        "value": base * 1_000,
                        "unit": "shares",
                    },
                ]
            )
    return pd.DataFrame(rows)


def synthetic_ytd_revenue_facts(symbol: str = "AAPL") -> pd.DataFrame:
    """Eight quarters of revenue with Q2-Q4 same-FY cumulative rows for subtraction tests."""
    rows: list[dict[str, object]] = []
    quarters = pd.date_range("2019-03-31", periods=8, freq="QE", tz="UTC")
    for index, period_end in enumerate(quarters):
        fiscal_year = int(period_end.year)
        filed = period_end + pd.Timedelta(days=30)
        quarter = float(100 + index * 5)
        if period_end.month == 3:
            rows.append(
                {
                    "symbol": symbol,
                    "taxonomy": "us-gaap",
                    "tag": "Revenues",
                    "value": quarter,
                    "unit": "USD",
                    "period_start": period_end - pd.Timedelta(days=88),
                    "period_end": period_end,
                    "filed_at": filed,
                    "accepted_at": filed,
                    "form": "10-Q",
                    "fiscal_year": fiscal_year,
                    "frame": f"CY{fiscal_year}Q1",
                }
            )
        else:
            first_index = index - (period_end.quarter - 1)
            cumulative = sum(100 + j * 5 for j in range(first_index, index + 1))
            rows.append(
                {
                    "symbol": symbol,
                    "taxonomy": "us-gaap",
                    "tag": "Revenues",
                    "value": cumulative,
                    "unit": "USD",
                    "period_start": pd.Timestamp(f"{fiscal_year}-01-01", tz="UTC"),
                    "period_end": period_end,
                    "filed_at": filed,
                    "accepted_at": filed,
                    "form": "10-Q",
                    "fiscal_year": fiscal_year,
                    "frame": f"CY{fiscal_year}Q{period_end.quarter}",
                }
            )
    return pd.DataFrame(rows)


def mutate_future_split(
    bars: pd.DataFrame, split_date: str | pd.Timestamp, factor: float = 2.0
) -> pd.DataFrame:
    """Apply a later split back-adjustment to prior rows for invariance tests."""
    if factor <= 0:
        raise ValueError("split factor must be positive")
    result = bars.copy(deep=True)
    timestamps = pd.to_datetime(result["bar_end_at"], utc=True)
    cutoff = pd.Timestamp(split_date)
    cutoff = cutoff.tz_localize("UTC") if cutoff.tzinfo is None else cutoff.tz_convert("UTC")
    prior = timestamps < cutoff
    result.loc[prior, ["open", "high", "low", "close"]] /= factor
    result.loc[prior, "volume"] *= factor
    return result
