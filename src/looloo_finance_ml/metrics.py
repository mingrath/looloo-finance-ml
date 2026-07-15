"""Frozen predictive and portfolio metric formulas."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd


def rank_ic(
    rows: pd.DataFrame, *, prediction: str = "prediction", target: str = "target"
) -> tuple[float, pd.DataFrame]:
    """Return mean weekly cross-sectional rank IC and the per-date series."""
    required = {"decision_at", prediction, target}
    missing = required.difference(rows.columns)
    if missing:
        raise ValueError(f"rank_ic rows missing: {sorted(missing)}")
    values: list[dict[str, object]] = []
    for decision_at, group in rows.groupby("decision_at", sort=True):
        if len(group) < 3:
            values.append(
                {
                    "decision_at": decision_at,
                    "ic": np.nan,
                    "n": len(group),
                    "reason": "fewer_than_three",
                }
            )
            continue
        predicted = pd.to_numeric(group[prediction], errors="coerce")
        observed = pd.to_numeric(group[target], errors="coerce")
        valid = predicted.notna() & observed.notna()
        if valid.sum() < 3 or predicted[valid].nunique() < 2 or observed[valid].nunique() < 2:
            values.append(
                {
                    "decision_at": decision_at,
                    "ic": np.nan,
                    "n": int(valid.sum()),
                    "reason": "constant_or_missing",
                }
            )
            continue
        ic = float(
            predicted[valid].rank(method="average").corr(observed[valid].rank(method="average"))
        )
        values.append({"decision_at": decision_at, "ic": ic, "n": int(valid.sum()), "reason": None})
    per_date = pd.DataFrame(values)
    mean_ic = (
        float(per_date["ic"].dropna().mean())
        if not per_date.empty and per_date["ic"].notna().any()
        else float("nan")
    )
    return mean_ic, per_date


def weekly_returns(
    nav_marks: pd.DataFrame, *, initial_nav: float, nav: str = "net_nav"
) -> pd.DataFrame:
    """Compute arithmetic returns from the last scheduled close of each week."""
    required = {"event_at", nav}
    missing = required.difference(nav_marks.columns)
    if missing:
        raise ValueError(f"NAV marks missing: {sorted(missing)}")
    if initial_nav <= 0:
        raise ValueError("initial_nav must be positive")
    marks = nav_marks.copy()
    marks["event_at"] = pd.to_datetime(marks["event_at"], utc=True)
    marks = marks.sort_values("event_at")
    local = marks["event_at"].dt.tz_convert("America/New_York").dt.isocalendar()
    marks["week"] = local["year"].astype(str) + "-W" + local["week"].astype(str).str.zfill(2)
    week = marks.groupby("week", sort=True).tail(1).copy()
    values = pd.to_numeric(week[nav], errors="coerce")
    if values.isna().any() or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("NAV marks must be finite and positive")
    denominators = values.shift(1)
    if len(denominators):
        denominators.iloc[0] = initial_nav
    week["weekly_return"] = values.to_numpy() / denominators.to_numpy() - 1.0
    return week.reset_index(drop=True)


def annualized_volatility(returns: Iterable[float]) -> float:
    values = np.asarray(list(returns), dtype=float)
    return float(np.std(values, ddof=1) * math.sqrt(52.0)) if len(values) >= 2 else float("nan")


def sharpe(returns: Iterable[float]) -> float:
    values = np.asarray(list(returns), dtype=float)
    if len(values) < 2:
        return float("nan")
    denominator = float(np.std(values, ddof=1))
    return float(np.mean(values) / denominator * math.sqrt(52.0)) if denominator else float("nan")


def sortino(returns: Iterable[float]) -> float:
    values = np.asarray(list(returns), dtype=float)
    if len(values) == 0:
        return float("nan")
    downside = float(np.sqrt(np.mean(np.minimum(values, 0.0) ** 2)))
    return float(np.mean(values) / downside * math.sqrt(52.0)) if downside else float("nan")


def maximum_drawdown(nav: Iterable[float], initial_nav: float | None = None) -> float:
    values = np.asarray(list(nav), dtype=float)
    if initial_nav is not None:
        values = np.concatenate(([float(initial_nav)], values))
    if len(values) == 0 or np.any(values <= 0):
        return float("nan")
    peaks = np.maximum.accumulate(values)
    return float(np.min(values / peaks - 1.0))


def weekly_hit_rate(returns: Iterable[float]) -> float:
    values = np.asarray(list(returns), dtype=float)
    return float(np.mean(values > 0.0)) if len(values) else float("nan")


def average_exposure(marks: pd.DataFrame) -> float:
    if "gross_exposure" not in marks:
        raise ValueError("marks require gross_exposure")
    values = pd.to_numeric(marks["gross_exposure"], errors="coerce")
    return float(values.mean()) if values.notna().any() else float("nan")


def one_way_turnover(fill_events: pd.DataFrame) -> float:
    required = {"trade_notional", "nav_before_event"}
    missing = required.difference(fill_events.columns)
    if missing:
        raise ValueError(f"fill events missing: {sorted(missing)}")
    notional = pd.to_numeric(fill_events["trade_notional"], errors="coerce").abs()
    nav = pd.to_numeric(fill_events["nav_before_event"], errors="coerce")
    if (nav <= 0).any() or nav.isna().any():
        raise ValueError("nav_before_event must be positive")
    return float((notional / nav).sum())


def cost_drag(gross_nav: float, net_nav: float, initial_nav: float) -> float:
    if initial_nav <= 0:
        raise ValueError("initial_nav must be positive")
    return float((gross_nav - net_nav) / initial_nav)


def portfolio_summary(
    net_weekly: pd.DataFrame,
    net_marks: pd.DataFrame,
    *,
    gross_weekly: pd.DataFrame | None = None,
    initial_nav: float = 100_000.0,
) -> dict[str, float]:
    net_returns = pd.to_numeric(net_weekly["weekly_return"], errors="coerce").dropna().to_numpy()
    net_nav = pd.to_numeric(net_weekly["net_nav"], errors="coerce").dropna().to_numpy()
    summary = {
        "cumulative_return": float(net_nav[-1] / initial_nav - 1.0)
        if len(net_nav)
        else float("nan"),
        "annualized_volatility": annualized_volatility(net_returns),
        "sharpe": sharpe(net_returns),
        "sortino": sortino(net_returns),
        "maximum_drawdown": maximum_drawdown(net_nav, initial_nav),
        "weekly_hit_rate": weekly_hit_rate(net_returns),
        "average_exposure": average_exposure(net_marks),
    }
    if gross_weekly is not None and not gross_weekly.empty:
        gross_returns = (
            pd.to_numeric(gross_weekly["weekly_return"], errors="coerce").dropna().to_numpy()
        )
        gross_nav = pd.to_numeric(gross_weekly["gross_nav"], errors="coerce").dropna().to_numpy()
        summary.update(
            {
                "gross_cumulative_return": float(gross_nav[-1] / initial_nav - 1.0),
                "gross_annualized_volatility": annualized_volatility(gross_returns),
                "gross_sharpe": sharpe(gross_returns),
                "gross_sortino": sortino(gross_returns),
                "gross_maximum_drawdown": maximum_drawdown(gross_nav, initial_nav),
                "gross_weekly_hit_rate": weekly_hit_rate(gross_returns),
            }
        )
    return summary
