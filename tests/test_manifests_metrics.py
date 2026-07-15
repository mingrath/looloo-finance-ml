from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from looloo_finance_ml.manifests import dataframe_schema_hash, manifest_for_frame
from looloo_finance_ml.metrics import (
    maximum_drawdown,
    one_way_turnover,
    portfolio_summary,
    rank_ic,
    sharpe,
    sortino,
    weekly_returns,
)


def test_manifest_hash_covers_schema_and_raw_response() -> None:
    frame = pd.DataFrame({"symbol": ["AAPL"], "close": [1.0]})
    first = manifest_for_frame(
        frame,
        source="fixture",
        stream="feature_stream",
        params={},
        symbols=("AAPL",),
        start="2021-01-01",
        end="2021-01-02",
        raw_payload={"a": 1},
        retrieved_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
    )
    second = manifest_for_frame(
        frame,
        source="fixture",
        stream="feature_stream",
        params={},
        symbols=("AAPL",),
        start="2021-01-01",
        end="2021-02-02",
        raw_payload={"a": 1},
        retrieved_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
    )
    assert first.schema_hash == dataframe_schema_hash(frame)
    assert first.manifest_hash != second.manifest_hash


def test_rank_ic_and_risk_metrics_use_fixed_conventions() -> None:
    rows = pd.DataFrame(
        {
            "decision_at": ["2021-01-01"] * 4,
            "prediction": [4, 3, 2, 1],
            "target": [0.4, 0.3, 0.2, 0.1],
        }
    )
    mean_ic, per_date = rank_ic(rows)
    assert mean_ic == pytest.approx(1.0)
    assert per_date.iloc[0]["n"] == 4
    assert sharpe([0.01, -0.01]) == pytest.approx(0.0)
    assert sortino([0.02, -0.01]) > 0
    assert maximum_drawdown([100, 110, 90], 100) == pytest.approx(-20 / 110)
    assert one_way_turnover(
        pd.DataFrame({"trade_notional": [100, 50], "nav_before_event": [1000, 1000]})
    ) == pytest.approx(0.15)


def test_rank_ic_keeps_valid_rows_with_null_diagnostic_reason() -> None:
    rows = pd.DataFrame(
        {
            "decision_at": ["2021-01-01"] * 4,
            "prediction": [4, 3, 2, 1],
            "target": [0.4, 0.3, 0.2, 0.1],
        }
    )
    _, per_date = rank_ic(rows)
    assert per_date["reason"].isna().all()
    assert per_date["ic"].dropna().tolist() == pytest.approx([1.0])


def test_weekly_metrics_use_explicit_initial_nav_and_week_end_drawdown() -> None:
    marks = pd.DataFrame(
        {
            "event_at": [
                "2021-01-04T21:00:00Z",
                "2021-01-08T21:00:00Z",
                "2021-01-11T21:00:00Z",
                "2021-01-15T21:00:00Z",
            ],
            "net_nav": [80_000.0, 110_000.0, 90_000.0, 105_000.0],
            "gross_exposure": [1.0, 1.0, 1.0, 1.0],
        }
    )
    weekly = weekly_returns(marks, initial_nav=100_000.0)
    assert weekly["weekly_return"].tolist() == pytest.approx([0.10, 105_000 / 110_000 - 1])
    summary = portfolio_summary(weekly, marks)
    assert summary["maximum_drawdown"] == pytest.approx(105_000 / 110_000 - 1)
