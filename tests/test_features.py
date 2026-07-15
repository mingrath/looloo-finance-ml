from __future__ import annotations

import pandas as pd
import pytest

from looloo_finance_ml.features import (
    _standalone_flow,
    _visible_facts,
    build_sec_features,
    build_price_features,
)
from looloo_finance_ml.fixtures import (
    mutate_future_split,
    synthetic_bars,
    synthetic_sec_facts,
    synthetic_ytd_revenue_facts,
)


def test_sec_fixture_computes_eight_quarter_and_same_period_ratios() -> None:
    facts = synthetic_sec_facts(symbols=("AAPL",))
    result = build_sec_features(
        facts, [pd.Timestamp("2021-06-30", tz="UTC")], symbols=("AAPL",)
    ).iloc[0]
    assert result["revenue_growth_ttm"] == pytest.approx(
        (sum(1000 + 20 * i for i in range(9, 13)) / sum(1000 + 20 * i for i in range(5, 9))) - 1
    )
    assert result["operating_margin_ttm"] == pytest.approx(0.2)
    assert result["debt_to_assets"] == pytest.approx(0.3)
    assert result["cash_to_assets"] == pytest.approx(0.16)
    assert result["diluted_share_change"] == pytest.approx((124 / 116) - 1)


def test_diluted_share_change_does_not_subtract_ytd_weighted_averages() -> None:
    facts = synthetic_ytd_revenue_facts()
    facts["tag"] = "WeightedAverageNumberOfDilutedSharesOutstanding"
    facts["unit"] = "shares"

    result = build_sec_features(
        facts, [pd.Timestamp("2021-02-01", tz="UTC")], symbols=("AAPL",)
    ).iloc[0]

    assert pd.isna(result["diluted_share_change"])


def test_ytd_facts_are_quarterized_by_same_fy_subtraction() -> None:
    facts = synthetic_ytd_revenue_facts()
    visible = _visible_facts(facts, "AAPL", pd.Timestamp("2021-12-31", tz="UTC"))
    quarterly = _standalone_flow(visible, "Revenues")
    assert quarterly["value"].tolist() == [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0]


def test_missing_debt_is_missing_not_zero() -> None:
    facts = synthetic_sec_facts(symbols=("AAPL",))
    facts = facts[~facts["tag"].str.contains("LongTermDebt")]
    result = build_sec_features(
        facts, [pd.Timestamp("2021-06-30", tz="UTC")], symbols=("AAPL",)
    ).iloc[0]
    assert pd.isna(result["debt_to_assets"])


def test_price_features_are_invariant_to_future_split_mutation() -> None:
    bars = synthetic_bars("2021-01-04", "2021-06-30", symbols=("AAPL",))
    mutated = mutate_future_split(bars, "2021-05-03")
    original = build_price_features(bars)
    changed = build_price_features(mutated)
    cutoff = pd.Timestamp("2021-05-03", tz="UTC")
    left = original[original["decision_at"] < cutoff].reset_index(drop=True)
    right = changed[changed["decision_at"] < cutoff].reset_index(drop=True)
    pd.testing.assert_frame_equal(left, right, check_exact=False, rtol=1e-10, atol=1e-10)


def test_price_features_reject_label_fill_adjustment() -> None:
    bars = synthetic_bars("2021-01-04", "2021-06-30", symbols=("AAPL",), adjustment="all")
    with pytest.raises(ValueError, match="adjustment=split"):
        build_price_features(bars)


def test_price_features_revalidate_persisted_ohlcv() -> None:
    bars = synthetic_bars("2021-01-04", "2021-06-30", symbols=("AAPL",))
    nonpositive = bars.copy()
    nonpositive.loc[0, "close"] = 0
    with pytest.raises(ValueError, match="non-positive"):
        build_price_features(nonpositive)

    malformed = bars.copy()
    malformed.loc[0, "high"] = min(malformed.loc[0, "open"], malformed.loc[0, "close"]) / 2
    with pytest.raises(ValueError, match="malformed"):
        build_price_features(malformed)

    nonfinite = bars.copy()
    nonfinite.loc[0, "volume"] = float("inf")
    with pytest.raises(ValueError, match="non-finite"):
        build_price_features(nonfinite)

    duplicate = pd.concat([bars, bars.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        build_price_features(duplicate)


def test_price_features_normalize_symbols_before_time_sorting() -> None:
    bars = synthetic_bars("2021-01-04", "2021-06-30", symbols=("AAPL",))
    mixed_case = bars.copy()
    mixed_case.loc[mixed_case.index[::2], "symbol"] = "aapl"
    pd.testing.assert_frame_equal(build_price_features(bars), build_price_features(mixed_case))
