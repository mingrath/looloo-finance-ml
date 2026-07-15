from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from looloo_finance_ml.models import (
    FittedModel,
    FoldPreprocessor,
    ModelError,
    choose_development_winner,
    registered_specs,
)
from looloo_finance_ml.validation import ExpandingWalkForward, ValidationError


def _panel(symbol_count: int = 20) -> pd.DataFrame:
    weeks = pd.date_range("2021-01-01", periods=100, freq="W-FRI", tz="UTC")
    return pd.DataFrame(
        [
            {
                "decision_at": week,
                "label_end": week + pd.Timedelta(days=7),
                "symbol": f"S{index:02d}",
            }
            for week in weeks
            for index in range(symbol_count)
        ]
    )


def test_walk_forward_starts_after_training_and_embargo_decisions() -> None:
    folds = ExpandingWalkForward().split(_panel())
    first = folds[0]
    weeks = pd.Series(sorted(_panel()["decision_at"].unique()))
    assert first.embargo_start == weeks.iloc[52]
    assert first.validation_start == weeks.iloc[53]
    assert len(set(_panel().loc[list(first.train_index), "decision_at"])) == 52


def test_walk_forward_rejects_underpopulated_panel() -> None:
    with pytest.raises(ValidationError, match="insufficient_training_history"):
        ExpandingWalkForward().split(_panel(symbol_count=1))


def test_registry_has_every_pre_registered_configuration() -> None:
    specs = registered_specs()
    assert len(specs) == 41
    assert len({spec.name for spec in specs}) == 41
    assert sum(spec.rung == "B2" for spec in specs) == 27
    assert sum(spec.rung == "M1" for spec in specs) == 12
    assert {spec.params["max_depth"] for spec in specs if spec.rung == "M1"} == {2, 3}
    assert {spec.params["learning_rate"] for spec in specs if spec.rung == "M1"} == {0.05, 0.1}
    assert all(spec.params["max_iter"] == 10000 for spec in specs if spec.rung == "B2")
    assert all(spec.params["tol"] == 1e-4 for spec in specs if spec.rung == "B2")


def test_fold_preprocessor_drops_high_missing_features_and_pairs_indicators() -> None:
    frame = pd.DataFrame(
        {"keep": [1.0, np.nan, 3.0, 4.0], "drop": [np.nan] * 4, "full": [2.0, 3.0, 4.0, 5.0]}
    )
    fitted = FoldPreprocessor(("keep", "drop", "full")).fit(frame)
    assert fitted.dropped_feature_columns_ == ("drop",)
    assert fitted.get_feature_names_out().tolist() == [
        "keep",
        "full",
        "keep__missing",
        "full__missing",
    ]
    assert fitted.transform(frame).shape == (4, 4)


def test_promotion_uses_b1_threshold_and_lowest_complexity() -> None:
    specs = registered_specs()
    simple = next(
        spec for spec in specs if spec.rung == "B2" and spec.feature_group == "price_volume"
    )
    complex_candidate = next(
        spec for spec in specs if spec.rung == "M1" and spec.feature_group == "price_volume"
    )
    results = pd.DataFrame(
        [
            {"name": "B1", "mean_development_ic": 0.10, "nonnegative_fold_fraction": 1.0},
            {"name": simple.name, "mean_development_ic": 0.111, "nonnegative_fold_fraction": 0.60},
            {
                "name": complex_candidate.name,
                "mean_development_ic": 0.50,
                "nonnegative_fold_fraction": 1.0,
            },
        ]
    )
    assert choose_development_winner(results).name == simple.name


def test_promotion_breaks_same_complexity_ic_ties_by_registration_order() -> None:
    candidates = [
        spec
        for spec in registered_specs()
        if spec.rung == "B2" and spec.feature_group == "price_volume"
    ][:3]
    results = pd.DataFrame(
        [
            {"name": "B1", "mean_development_ic": 0.10, "nonnegative_fold_fraction": 1.0},
            {
                "name": candidates[0].name,
                "mean_development_ic": 0.111,
                "nonnegative_fold_fraction": 1.0,
            },
            {
                "name": candidates[1].name,
                "mean_development_ic": 0.112,
                "nonnegative_fold_fraction": 1.0,
            },
            {
                "name": candidates[2].name,
                "mean_development_ic": 0.1120005,
                "nonnegative_fold_fraction": 1.0,
            },
        ]
    )
    assert choose_development_winner(results).name == candidates[1].name


def test_holdout_end_date_is_inclusive_through_close() -> None:
    rows = pd.DataFrame(
        {
            "decision_at": [
                pd.Timestamp("2025-12-31T21:00:00Z"),
                pd.Timestamp("2026-01-01T00:00:00Z"),
            ]
        }
    )
    result = ExpandingWalkForward().holdout_rows(rows)
    assert len(result) == 1


def test_walk_forward_rejects_holdout_only_rows() -> None:
    rows = pd.DataFrame(
        [
            {
                "decision_at": pd.Timestamp("2025-01-03T21:00:00Z"),
                "label_end": pd.Timestamp("2025-01-10T21:00:00Z"),
                "symbol": "AAPL",
            }
        ]
    )
    with pytest.raises(ValidationError, match="insufficient_training_history"):
        ExpandingWalkForward().split(rows)


def test_model_hash_is_verified_before_joblib_deserialization(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact = tmp_path / "model.joblib"
    artifact.write_bytes(b"untrusted")
    monkeypatch.setattr(
        "looloo_finance_ml.models.joblib.load", lambda _: pytest.fail("joblib.load must not run")
    )
    with pytest.raises(ModelError, match="hash mismatch"):
        FittedModel.load(artifact, expected_hash="0" * 64)
