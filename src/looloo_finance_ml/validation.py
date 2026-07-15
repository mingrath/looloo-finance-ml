"""Date-aware expanding walk-forward folds with overlap purge and embargo."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


class ValidationError(ValueError):
    """Raised when the temporal contract cannot be satisfied."""


@dataclass(frozen=True)
class TemporalFold:
    fold_id: str
    train_index: tuple[int, ...]
    validation_index: tuple[int, ...]
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    validation_start: pd.Timestamp
    validation_end: pd.Timestamp
    embargo_start: pd.Timestamp
    purged_count: int


@dataclass(frozen=True)
class TemporalSpec:
    development_start: str = "2021-01-01"
    development_end: str = "2024-12-31"
    holdout_start: str = "2025-01-01"
    holdout_end: str = "2025-12-31"
    minimum_training_weeks: int = 52
    minimum_symbols_per_week: int = 20
    validation_weeks: int = 13
    embargo_weeks: int = 1
    advance_weeks: int = 13


class ExpandingWalkForward:
    """Build folds from weekly decision rows without random shuffling."""

    def __init__(self, spec: TemporalSpec | None = None) -> None:
        self.spec = spec or TemporalSpec()

    @staticmethod
    def _utc_series(values: pd.Series) -> pd.Series:
        return pd.to_datetime(values, utc=True)

    def split(self, rows: pd.DataFrame) -> tuple[TemporalFold, ...]:
        required = {"decision_at", "label_end", "symbol"}
        missing = required.difference(rows.columns)
        if missing:
            raise ValidationError(f"rows missing temporal columns: {sorted(missing)}")
        data = rows.copy()
        data["decision_at"] = self._utc_series(data["decision_at"])
        data["label_end"] = self._utc_series(data["label_end"])
        start = pd.Timestamp(self.spec.development_start, tz="UTC")
        end_exclusive = pd.Timestamp(self.spec.development_end, tz="UTC") + pd.Timedelta(days=1)
        dev = data[(data["decision_at"] >= start) & (data["decision_at"] < end_exclusive)]
        if dev.empty:
            raise ValidationError("insufficient_training_history: development window has no rows")
        weeks = pd.Series(sorted(dev["decision_at"].drop_duplicates()), dtype="datetime64[ns, UTC]")
        folds: list[TemporalFold] = []
        first = self.spec.minimum_training_weeks + self.spec.embargo_weeks
        for position in range(first, len(weeks), self.spec.advance_weeks):
            validation_weeks = weeks.iloc[position : position + self.spec.validation_weeks]
            if len(validation_weeks) < self.spec.validation_weeks:
                break
            validation_start = validation_weeks.iloc[0]
            validation_end = validation_weeks.iloc[-1]
            embargo_index = position - self.spec.embargo_weeks
            if embargo_index < 0:
                continue
            embargo_start = weeks.iloc[embargo_index]
            train_candidates = dev[dev["decision_at"] < embargo_start]
            train_candidates = train_candidates[train_candidates["label_end"] < validation_start]
            validation_rows = dev[dev["decision_at"].isin(validation_weeks.tolist())]
            train_week_counts = train_candidates.groupby("decision_at")["symbol"].nunique()
            validation_week_counts = validation_rows.groupby("decision_at")["symbol"].nunique()
            if len(train_week_counts) < self.spec.minimum_training_weeks:
                raise ValidationError(
                    "insufficient_training_history: purge/embargo left fewer than the minimum training weeks"
                )
            bad_train = train_week_counts[train_week_counts < self.spec.minimum_symbols_per_week]
            bad_validation = validation_week_counts[
                validation_week_counts < self.spec.minimum_symbols_per_week
            ]
            if not bad_train.empty or not bad_validation.empty:
                raise ValidationError(
                    f"insufficient_training_history: fewer than {self.spec.minimum_symbols_per_week} eligible symbols in train={bad_train.to_dict()} validation={bad_validation.to_dict()}"
                )
            if validation_rows.empty:
                raise ValidationError(
                    "insufficient_training_history: validation window has no rows"
                )
            folds.append(
                TemporalFold(
                    fold_id=f"fold-{len(folds):02d}",
                    train_index=tuple(int(i) for i in train_candidates.index),
                    validation_index=tuple(int(i) for i in validation_rows.index),
                    train_start=train_candidates["decision_at"].min(),
                    train_end=train_candidates["decision_at"].max(),
                    validation_start=validation_start,
                    validation_end=validation_end,
                    embargo_start=embargo_start,
                    purged_count=int(
                        len(dev[dev["decision_at"] < embargo_start]) - len(train_candidates)
                    ),
                )
            )
        if not folds:
            raise ValidationError(
                "insufficient_training_history: no valid expanding folds satisfy panel, validation, and embargo requirements"
            )
        return tuple(folds)

    def holdout_rows(self, rows: pd.DataFrame) -> pd.DataFrame:
        decision = self._utc_series(rows["decision_at"])
        start = pd.Timestamp(self.spec.holdout_start, tz="UTC")
        end_exclusive = pd.Timestamp(self.spec.holdout_end, tz="UTC") + pd.Timedelta(days=1)
        return rows.loc[(decision >= start) & (decision < end_exclusive)].copy()


def validate_holdout_seam(
    final_fit_rows: pd.DataFrame,
    *,
    holdout_start: str = "2025-01-01",
    embargo_start: str = "2024-12-27",
) -> None:
    """Reject a final-fit row whose label crosses the holdout or embargo seam."""
    decision = pd.to_datetime(final_fit_rows["decision_at"], utc=True)
    label_end = pd.to_datetime(final_fit_rows["label_end"], utc=True)
    holdout = pd.Timestamp(holdout_start, tz="UTC")
    embargo = pd.Timestamp(embargo_start, tz="UTC")
    invalid = (label_end >= holdout) | ((decision >= embargo) & (decision < holdout))
    if invalid.any():
        bad = final_fit_rows.index[invalid].tolist()
        raise ValidationError(f"final-fit rows cross the holdout seam: {bad}")
