"""Contract-frozen price, SEC, and five-session label builders."""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import numpy as np
import pandas as pd

from .calendar import Session, XNYSCalendar
from .fixtures import FROZEN_SYMBOLS

PRICE_FEATURE_COLUMNS = (
    "ret_1",
    "ret_5",
    "ret_20",
    "ret_60",
    "rv20",
    "volume_z20",
    "dollar_volume20",
    "drawdown60",
    "range20",
)
SEC_FEATURE_COLUMNS = (
    "revenue_growth_ttm",
    "operating_margin_ttm",
    "debt_to_assets",
    "cash_to_assets",
    "diluted_share_change",
)
ALL_FEATURE_COLUMNS = PRICE_FEATURE_COLUMNS + SEC_FEATURE_COLUMNS


def _ensure_bars(frame: pd.DataFrame, *, expected_adjustment: str) -> pd.DataFrame:
    required = {"symbol", "bar_end_at", "open", "high", "low", "close", "volume", "adjustment"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"bars missing columns: {sorted(missing)}")
    adjustments = set(frame["adjustment"].dropna().astype(str))
    if not frame.empty and (
        adjustments != {expected_adjustment} or frame["adjustment"].isna().any()
    ):
        raise ValueError(
            f"bars must contain only adjustment={expected_adjustment}; observed={sorted(adjustments)}"
        )
    result = frame.copy()
    result["bar_end_at"] = pd.to_datetime(result["bar_end_at"], utc=True)
    for column in ("open", "high", "low", "close", "volume"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    if (
        result[["symbol", "bar_end_at", "open", "high", "low", "close", "volume"]]
        .isna()
        .any()
        .any()
    ):
        raise ValueError("bars contain missing key or OHLCV values")
    result["symbol"] = result["symbol"].astype(str).str.upper()
    result = result.sort_values(["symbol", "bar_end_at"], ignore_index=True)
    if result.duplicated(["symbol", "bar_end_at"]).any():
        raise ValueError("bars contain duplicate symbol timestamps")
    values = result[["open", "high", "low", "close", "volume"]]
    if not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("bars contain non-finite OHLCV values")
    if (values <= 0).any().any():
        raise ValueError("bars contain non-positive OHLCV values")
    malformed = result["high"].lt(result[["open", "close"]].max(axis=1)) | result["low"].gt(
        result[["open", "close"]].min(axis=1)
    )
    if malformed.any():
        raise ValueError("bars contain malformed OHLC values")
    return result


def build_price_features(bars: pd.DataFrame) -> pd.DataFrame:
    """Build only split-invariant price/volume features from `feature_stream`."""
    source = _ensure_bars(bars, expected_adjustment="split")
    groups: list[pd.DataFrame] = []
    for symbol, group in source.groupby("symbol", sort=True):
        group = group.copy()
        close = group["close"]
        log_close = np.log(close)
        returns = log_close.diff()
        group["ret_1"] = returns
        for window in (5, 20, 60):
            group[f"ret_{window}"] = log_close - log_close.shift(window)
        group["rv20"] = returns.rolling(20, min_periods=20).std(ddof=1) * np.sqrt(252.0)
        log_volume = np.log(group["volume"])
        volume_mean = log_volume.rolling(20, min_periods=20).mean()
        volume_std = log_volume.rolling(20, min_periods=20).std(ddof=1)
        group["volume_z20"] = (log_volume - volume_mean) / volume_std.replace(0.0, np.nan)
        dollar_volume = group["close"] * group["volume"]
        group["dollar_volume20"] = np.log1p(dollar_volume.rolling(20, min_periods=20).median())
        group["drawdown60"] = close / close.rolling(60, min_periods=60).max() - 1.0
        group["range20"] = (
            group["high"].rolling(20, min_periods=20).max()
            - group["low"].rolling(20, min_periods=20).min()
        ) / close
        groups.append(group)
    if not groups:
        return pd.DataFrame(columns=["symbol", "decision_at", *PRICE_FEATURE_COLUMNS])
    result = pd.concat(groups, ignore_index=True).rename(columns={"bar_end_at": "decision_at"})
    return result[["symbol", "decision_at", *PRICE_FEATURE_COLUMNS]]


def _visible_facts(facts: pd.DataFrame, symbol: str, cutoff: pd.Timestamp) -> pd.DataFrame:
    if facts.empty:
        return facts.copy()
    result = facts[facts["symbol"].eq(symbol)].copy()
    result["filed_at"] = pd.to_datetime(result["filed_at"], utc=True)
    accepted = (
        pd.to_datetime(result.get("accepted_at"), utc=True, errors="coerce")
        if "accepted_at" in result
        else pd.Series(pd.NaT, index=result.index, dtype="datetime64[ns, UTC]")
    )
    result["visibility_at"] = accepted
    result = result[result["visibility_at"].notna() & (result["visibility_at"] <= cutoff)].copy()
    result["period_end"] = pd.to_datetime(result["period_end"], utc=True)
    if "period_start" in result:
        result["period_start"] = pd.to_datetime(result["period_start"], utc=True, errors="coerce")
    else:
        result["period_start"] = pd.NaT
    result["value"] = pd.to_numeric(result["value"], errors="coerce")
    return result.dropna(subset=["value", "period_end"]).sort_values(
        ["period_end", "visibility_at"]
    )


def _latest_by_tag(facts: pd.DataFrame, tag: str, unit: str | None = None) -> pd.DataFrame:
    result = facts[facts["tag"].eq(tag)].copy()
    if unit is not None:
        result = result[result["unit"].eq(unit)]
    result = result.sort_values(["period_end", "visibility_at"])
    return result.drop_duplicates(["period_end", "unit"], keep="last")


def _quarter_index(value: pd.Timestamp) -> pd.Period:
    return value.tz_convert("UTC").tz_localize(None).to_period("Q")


def _standalone_flow(facts: pd.DataFrame, tag: str, unit: str = "USD") -> pd.DataFrame:
    """Return one compatible-unit value per quarter, deriving same-FY YTD rows."""
    source = facts[facts["tag"].eq(tag) & facts["unit"].eq(unit)].copy()
    if source.empty:
        return source
    source["period_start"] = pd.to_datetime(source["period_start"], utc=True, errors="coerce")
    source["period_end"] = pd.to_datetime(source["period_end"], utc=True)
    source = source.sort_values(["period_end", "visibility_at"])
    candidates: list[dict[str, object]] = []
    for period_end, contexts in source.groupby("period_end", sort=True):
        direct = contexts[
            contexts["period_start"].notna()
            & ((contexts["period_end"] - contexts["period_start"]).dt.days.between(45, 130))
        ]
        if direct.empty:
            frame = contexts["frame"].fillna("").astype(str)
            direct = contexts[
                contexts["period_start"].isna()
                & frame.str.contains("Q")
                & ~frame.str.contains("FY")
            ]
        if not direct.empty:
            candidates.append({**direct.iloc[-1].to_dict(), "_kind": 0})
            continue
        cumulative = contexts[
            contexts["period_start"].notna()
            & ((contexts["period_end"] - contexts["period_start"]).dt.days > 130)
            & contexts["fiscal_year"].notna()
        ].sort_values("visibility_at", ascending=False)
        for _, current in cumulative.iterrows():
            prior = source[
                source["period_end"].lt(current["period_end"])
                & source["fiscal_year"].eq(current["fiscal_year"])
                & source["period_start"].eq(current["period_start"])
            ]
            if prior.empty and _quarter_index(current["period_end"]).quarter == 2:
                current_quarter = _quarter_index(current["period_end"])
                prior = source[
                    source["period_end"].lt(current["period_end"])
                    & source["fiscal_year"].eq(current["fiscal_year"])
                    & source["period_end"].map(_quarter_index).eq(current_quarter - 1)
                ]
            if prior.empty:
                continue
            previous = prior.iloc[-1]
            candidates.append(
                {
                    **current.to_dict(),
                    "value": float(current["value"]) - float(previous["value"]),
                    "period_start": previous["period_end"],
                    "_kind": 1,
                }
            )
            break
    result = pd.DataFrame(candidates)
    if result.empty:
        return result
    return (
        result.sort_values(["period_end", "_kind", "visibility_at"])
        .drop_duplicates(["period_end"], keep="first")
        .drop(columns="_kind")
    )


def _latest_instant(
    facts: pd.DataFrame,
    tags: tuple[str, ...],
    period: pd.Timestamp | None = None,
    unit: str = "USD",
) -> float | None:
    for tag in tags:
        candidates = _latest_by_tag(facts, tag, unit)
        if period is not None:
            candidates = candidates[candidates["period_end"].eq(period)]
        if not candidates.empty:
            return float(candidates.iloc[-1]["value"])
    return None


def _latest_common_period(
    facts: pd.DataFrame,
    tags: tuple[str, ...],
    period: pd.Timestamp | None = None,
    unit: str = "USD",
) -> tuple[pd.Timestamp, dict[str, float]] | None:
    tables = {tag: _latest_by_tag(facts, tag, unit) for tag in tags}
    if period is not None:
        tables = {tag: table[table["period_end"].eq(period)] for tag, table in tables.items()}
    if any(table.empty for table in tables.values()):
        return None
    periods = set.intersection(*(set(table["period_end"]) for table in tables.values()))
    if not periods:
        return None
    selected = max(periods)
    return selected, {
        tag: float(tables[tag].loc[tables[tag]["period_end"].eq(selected)].iloc[-1]["value"])
        for tag in tags
    }


def _consecutive_tail(series: pd.DataFrame, count: int, unit: str = "USD") -> pd.DataFrame:
    if series.empty or "unit" not in series:
        return pd.DataFrame()
    if set(series["unit"].dropna()) != {unit}:
        return pd.DataFrame()
    ordered = (
        series.sort_values("period_end").drop_duplicates(["period_end"], keep="last").tail(count)
    )
    if len(ordered) != count:
        return pd.DataFrame()
    quarters = [_quarter_index(value) for value in ordered["period_end"]]
    if any(
        current.ordinal - previous.ordinal != 1 for previous, current in zip(quarters, quarters[1:])
    ):
        return pd.DataFrame()
    return ordered


def _ttm_pair(series: pd.DataFrame) -> tuple[float | None, float | None]:
    ordered = _consecutive_tail(series, 8, "USD")
    if ordered.empty:
        return None, None
    values = pd.to_numeric(ordered["value"], errors="coerce")
    if values.isna().any():
        return None, None
    return float(values.iloc[-4:].sum()), float(values.iloc[:4].sum())


def _aligned_ttm_pair(
    numerator: pd.DataFrame, denominator: pd.DataFrame
) -> tuple[float | None, float | None, float | None]:
    if numerator.empty or denominator.empty:
        return None, None, None
    if set(numerator.get("unit", pd.Series(dtype=str)).dropna()) != {"USD"} or set(
        denominator.get("unit", pd.Series(dtype=str)).dropna()
    ) != {"USD"}:
        return None, None, None
    common = numerator.merge(denominator, on=["period_end", "unit"], suffixes=("_num", "_den"))
    common = common.sort_values("period_end").drop_duplicates(["period_end"], keep="last")
    common = _consecutive_tail(common.assign(unit="USD"), 4)
    if common.empty:
        return None, None, None
    values_num = pd.to_numeric(common["value_num"], errors="coerce")
    values_den = pd.to_numeric(common["value_den"], errors="coerce")
    if values_num.isna().any() or values_den.isna().any():
        return None, None, None
    return float(values_num.sum()), float(values_den.sum()), float(values_den.iloc[-1])


def build_sec_features(
    facts: pd.DataFrame,
    decision_dates: Iterable[pd.Timestamp | datetime | date],
    symbols: tuple[str, ...] = FROZEN_SYMBOLS,
) -> pd.DataFrame:
    """Build filed-time SEC features with standalone-quarter normalization."""
    dates: list[pd.Timestamp] = []
    for value in decision_dates:
        timestamp = pd.Timestamp(value)
        dates.append(
            timestamp.tz_localize("UTC")
            if timestamp.tzinfo is None
            else timestamp.tz_convert("UTC")
        )
    rows: list[dict[str, object]] = []
    for decision_at in dates:
        for symbol in symbols:
            visible = _visible_facts(facts, symbol, decision_at)
            row: dict[str, object] = {"symbol": symbol, "decision_at": decision_at}
            revenue_candidates = [
                _standalone_flow(visible, revenue_tag, "USD")
                for revenue_tag in (
                    "RevenueFromContractWithCustomerExcludingAssessedTax",
                    "Revenues",
                    "SalesRevenueNet",
                )
            ]
            revenue_for_growth = next(
                (
                    candidate
                    for candidate in revenue_candidates
                    if _ttm_pair(candidate) != (None, None)
                ),
                pd.DataFrame(),
            )
            latest_revenue, prior_revenue = _ttm_pair(revenue_for_growth)
            row["revenue_growth_ttm"] = (
                latest_revenue / prior_revenue - 1.0
                if latest_revenue is not None and prior_revenue not in (None, 0)
                else np.nan
            )
            operating = _standalone_flow(visible, "OperatingIncomeLoss", "USD")
            margin_pair = next(
                (
                    pair
                    for pair in (
                        _aligned_ttm_pair(operating, candidate) for candidate in revenue_candidates
                    )
                    if pair[0] is not None
                ),
                (None, None, None),
            )
            operating_sum, aligned_revenue_sum, _ = margin_pair
            row["operating_margin_ttm"] = (
                operating_sum / aligned_revenue_sum
                if operating_sum is not None and aligned_revenue_sum not in (None, 0)
                else np.nan
            )
            debt = _latest_common_period(
                visible,
                (
                    "Assets",
                    "LongTermDebtAndFinanceLeaseObligationsCurrent",
                    "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
                ),
                unit="USD",
            )
            if debt is None:
                debt = _latest_common_period(
                    visible, ("Assets", "LongTermDebtCurrent", "LongTermDebtNoncurrent"), unit="USD"
                )
            row["debt_to_assets"] = (
                (
                    sum(value for tag, value in debt[1].items() if tag != "Assets")
                    / debt[1]["Assets"]
                )
                if debt is not None and debt[1]["Assets"]
                else np.nan
            )
            cash = _latest_common_period(
                visible, ("Assets", "CashAndCashEquivalentsAtCarryingValue"), unit="USD"
            )
            if cash is None:
                cash = _latest_common_period(
                    visible,
                    ("Assets", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"),
                    unit="USD",
                )
            row["cash_to_assets"] = (
                (cash[1][next(tag for tag in cash[1] if tag != "Assets")] / cash[1]["Assets"])
                if cash is not None and cash[1]["Assets"]
                else np.nan
            )
            shares = visible[
                visible["tag"].eq("WeightedAverageNumberOfDilutedSharesOutstanding")
                & visible["unit"].eq("shares")
                & visible["period_start"].notna()
                & ((visible["period_end"] - visible["period_start"]).dt.days.between(45, 130))
            ].copy()
            comparable_shares = _consecutive_tail(shares, 5, "shares")
            if not comparable_shares.empty:
                current, prior = (
                    float(comparable_shares.iloc[-1]["value"]),
                    float(comparable_shares.iloc[0]["value"]),
                )
                row["diluted_share_change"] = current / prior - 1.0 if prior else np.nan
            else:
                dei = _latest_by_tag(
                    visible[visible["taxonomy"].eq("dei")]
                    if "taxonomy" in visible
                    else visible.iloc[0:0],
                    "EntityCommonStockSharesOutstanding",
                    "shares",
                )
                comparable_dei = _consecutive_tail(dei, 5, "shares")
                if not comparable_dei.empty:
                    current, prior = (
                        float(comparable_dei.iloc[-1]["value"]),
                        float(comparable_dei.iloc[0]["value"]),
                    )
                    row["diluted_share_change"] = current / prior - 1.0 if prior else np.nan
                else:
                    row["diluted_share_change"] = np.nan
            rows.append(row)
    return pd.DataFrame(rows, columns=["symbol", "decision_at", *SEC_FEATURE_COLUMNS])


def build_labels(
    label_fill_bars: pd.DataFrame,
    decision_sessions: Iterable[Session],
    symbols: tuple[str, ...] = FROZEN_SYMBOLS,
    calendar: XNYSCalendar | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build weekly five-session excess-return labels and explicit skipped dates."""
    bars = _ensure_bars(label_fill_bars, expected_adjustment="all")
    index = bars.set_index(["symbol", "bar_end_at"])
    cal = calendar or XNYSCalendar()
    rows: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for decision in decision_sessions:
        following = cal.sessions_after(decision.session_date, 5)
        if len(following) < 5:
            skipped.append(
                {"decision_at": decision.close_at, "reason": "insufficient_calendar_sessions"}
            )
            continue
        entry, exit_session = following[0], following[4]
        values: dict[str, tuple[float, float]] = {}
        missing: list[str] = []
        for symbol in symbols:
            try:
                entry_row = index.loc[(symbol, pd.Timestamp(entry.close_at))]
                exit_row = index.loc[(symbol, pd.Timestamp(exit_session.close_at))]
            except KeyError:
                missing.append(symbol)
                continue
            values[symbol] = (float(entry_row["open"]), float(exit_row["close"]))
        if missing:
            skipped.append(
                {
                    "decision_at": decision.close_at,
                    "reason": "missing_label_bar",
                    "symbols": missing,
                }
            )
            continue
        returns = {
            symbol: float(np.log(close / open_)) for symbol, (open_, close) in values.items()
        }
        basket = float(np.mean(list(returns.values())))
        for symbol, value in returns.items():
            rows.append(
                {
                    "symbol": symbol,
                    "decision_at": decision.close_at,
                    "execution_at": entry.open_at,
                    "label_end": exit_session.close_at,
                    "raw_return": value,
                    "basket_return": basket,
                    "target": value - basket,
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(skipped)


def join_features(price: pd.DataFrame, sec: pd.DataFrame) -> pd.DataFrame:
    """Join two feature groups without joining labels into the feature table."""
    if price.empty:
        return price.copy()
    return price.merge(sec, on=["symbol", "decision_at"], how="left", validate="one_to_one")
