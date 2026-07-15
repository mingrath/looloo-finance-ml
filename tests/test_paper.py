from __future__ import annotations

import pandas as pd
import pytest

from looloo_finance_ml.calendar import XNYSCalendar

from looloo_finance_ml.fixtures import FROZEN_SYMBOLS, synthetic_bars
from looloo_finance_ml.paper import PaperConfig, PaperError, simulate_paper


def _scores(decision: str, symbols: tuple[str, ...] = FROZEN_SYMBOLS) -> pd.DataFrame:
    decision_at = XNYSCalendar().session(decision).close_at
    return pd.DataFrame(
        [
            {"decision_at": decision_at, "symbol": symbol, "score": index}
            for index, symbol in enumerate(symbols)
        ]
    )


def test_paper_replay_sizes_cost_inclusive_targets_and_orders_fill_before_mark() -> None:
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=FROZEN_SYMBOLS, adjustment="all")
    result = simulate_paper(_scores("2021-01-08"), bars, symbols=FROZEN_SYMBOLS)
    assert not result.failed
    types = [event["event_type"] for event in result.events]
    assert (
        types.index("decision")
        < types.index("fill")
        < types.index("exit")
        < types.index("mark", types.index("exit"))
    )
    assert result.summary["final_nav"] > 0
    assert all(event.get("cash", 0) >= -1e-8 for event in result.events if "cash" in event)
    assert (
        result.events[-1]["event_at"]
        == XNYSCalendar().sessions_after("2021-01-08", 5)[-1].close_at.isoformat()
    )


def test_missing_entry_bar_emits_skip_without_partial_fills() -> None:
    symbols = FROZEN_SYMBOLS
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=symbols, adjustment="all")
    entry_date = pd.Timestamp("2021-01-11", tz="UTC").date()
    bars = bars[~(bars["symbol"].eq(symbols[0]) & bars["bar_end_at"].dt.date.eq(entry_date))]
    result = simulate_paper(
        _scores("2021-01-08", symbols), bars, symbols=symbols, config=PaperConfig(top_n=10)
    )
    assert not result.failed
    assert not any(event["event_type"] == "fill" for event in result.events)
    assert any(
        event["event_type"] == "skip" and event.get("reason") == "entry_missing_bar"
        for event in result.events
    )


def test_replay_is_byte_deterministic() -> None:
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=FROZEN_SYMBOLS, adjustment="all")
    first = simulate_paper(_scores("2021-01-08"), bars, symbols=FROZEN_SYMBOLS)
    second = simulate_paper(_scores("2021-01-08"), bars, symbols=FROZEN_SYMBOLS)
    assert first.jsonl() == second.jsonl()


def test_replay_rejects_decisions_outside_the_scheduled_close() -> None:
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=FROZEN_SYMBOLS, adjustment="all")
    scores = _scores("2021-01-08")
    scores["decision_at"] = pd.Timestamp("2021-01-08T00:00:00Z")
    with pytest.raises(PaperError, match="scheduled weekly XNYS close"):
        simulate_paper(scores, bars, symbols=FROZEN_SYMBOLS)


def test_replay_rejects_a_nonfinal_session_close() -> None:
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=FROZEN_SYMBOLS, adjustment="all")
    with pytest.raises(PaperError, match="scheduled weekly XNYS close"):
        simulate_paper(_scores("2021-01-04"), bars, symbols=FROZEN_SYMBOLS)


def test_replay_accepts_the_weekly_early_close() -> None:
    bars = synthetic_bars("2021-11-22", "2021-12-31", symbols=FROZEN_SYMBOLS, adjustment="all")
    result = simulate_paper(_scores("2021-11-26"), bars, symbols=FROZEN_SYMBOLS)
    decision = next(event for event in result.events if event["event_type"] == "decision")
    assert decision["decision_at"] == XNYSCalendar().session("2021-11-26").close_at.isoformat()


def test_replay_rejects_feature_stream_prices() -> None:
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=FROZEN_SYMBOLS, adjustment="split")
    with pytest.raises(PaperError, match="adjustment=all"):
        simulate_paper(_scores("2021-01-08"), bars, symbols=FROZEN_SYMBOLS)


def test_nonfinite_entry_price_skips_without_partial_fills() -> None:
    bars = synthetic_bars("2021-01-04", "2021-03-31", symbols=FROZEN_SYMBOLS, adjustment="all")
    entry_date = pd.Timestamp("2021-01-11", tz="UTC").date()
    bars.loc[
        bars["symbol"].eq(FROZEN_SYMBOLS[0]) & bars["bar_end_at"].dt.date.eq(entry_date), "open"
    ] = float("inf")
    result = simulate_paper(_scores("2021-01-08"), bars, symbols=FROZEN_SYMBOLS)
    assert not any(event["event_type"] == "fill" for event in result.events)
    assert any(
        event["event_type"] == "skip" and event.get("reason") == "entry_missing_bar"
        for event in result.events
    )
