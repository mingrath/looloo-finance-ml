from __future__ import annotations

import pandas as pd
import pytest

from looloo_finance_ml.calendar import XNYSCalendar
from looloo_finance_ml.features import _visible_facts, build_labels, build_sec_features
from looloo_finance_ml.fixtures import FROZEN_SYMBOLS, synthetic_bars, synthetic_sec_facts


def test_unknown_acceptance_timestamp_is_excluded_from_pit_features() -> None:
    facts = synthetic_sec_facts(symbols=("AAPL",))
    cutoff_period = pd.Timestamp("2019-12-31", tz="UTC")
    facts.loc[facts["period_end"].ge(cutoff_period), "accepted_at"] = pd.NaT
    result = build_sec_features(
        facts, [pd.Timestamp("2021-06-30", tz="UTC")], symbols=("AAPL",)
    ).iloc[0]
    assert pd.isna(result["revenue_growth_ttm"])


def test_amendment_is_visible_only_after_its_acceptance() -> None:
    facts = synthetic_sec_facts(symbols=("AAPL",))
    latest = pd.Timestamp("2021-06-30", tz="UTC")
    original = facts[(facts["tag"] == "Revenues") & facts["period_end"].eq(latest)].iloc[0].copy()
    amendment = original.copy()
    amendment["value"] = float(original["value"]) * 2
    amendment["accepted_at"] = pd.Timestamp("2021-09-01", tz="UTC")
    facts = pd.concat([facts, pd.DataFrame([amendment])], ignore_index=True)
    before = _visible_facts(facts, "AAPL", pd.Timestamp("2021-08-15", tz="UTC"))
    after = _visible_facts(facts, "AAPL", pd.Timestamp("2021-10-01", tz="UTC"))
    assert float(
        before[(before["tag"] == "Revenues") & before["period_end"].eq(latest)].iloc[-1]["value"]
    ) == float(original["value"])
    assert float(
        after[(after["tag"] == "Revenues") & after["period_end"].eq(latest)].iloc[-1]["value"]
    ) == float(amendment["value"])


def test_labels_use_next_session_open_and_fail_closed_on_missing_symbol_bar() -> None:
    calendar = XNYSCalendar()
    decision = calendar.sessions("2021-01-04", "2021-01-08")[-1]
    symbols = FROZEN_SYMBOLS[:3]
    bars = synthetic_bars("2021-01-04", "2021-02-01", symbols=symbols, adjustment="all")
    following = calendar.sessions_after(decision.session_date, 5)
    missing_date = following[4].session_date
    bars = bars[~(bars["symbol"].eq(symbols[0]) & bars["bar_end_at"].dt.date.eq(missing_date))]
    labels, skipped = build_labels(bars, [decision], symbols=symbols, calendar=calendar)
    assert labels.empty
    assert skipped.iloc[0]["reason"] == "missing_label_bar"

    complete = synthetic_bars("2021-01-04", "2021-02-01", symbols=symbols, adjustment="all")
    labels, skipped = build_labels(complete, [decision], symbols=symbols, calendar=calendar)
    assert skipped.empty
    assert labels["execution_at"].iloc[0] == following[0].open_at
    assert labels["label_end"].iloc[0] == following[4].close_at


def test_labels_reject_feature_stream_adjustment() -> None:
    calendar = XNYSCalendar()
    decision = calendar.sessions("2021-01-04", "2021-01-08")[-1]
    bars = synthetic_bars(
        "2021-01-04", "2021-02-01", symbols=FROZEN_SYMBOLS[:3], adjustment="split"
    )
    with pytest.raises(ValueError, match="adjustment=all"):
        build_labels(bars, [decision], symbols=FROZEN_SYMBOLS[:3], calendar=calendar)
