"""Registered baselines, fold-local preprocessing, and development promotion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .hashing import sha256_file

RANDOM_STATE = 20250713
FEATURE_GROUPS = ("price_volume", "fundamentals", "combined")
FEATURE_GROUP_ORDER = {name: index for index, name in enumerate(FEATURE_GROUPS)}


class ModelError(ValueError):
    """Raised when a registered model cannot be fitted or selected."""


@dataclass(frozen=True)
class CandidateSpec:
    """One immutable model/configuration/feature-group identity."""

    name: str
    family: str
    feature_group: str
    complexity: int
    params: dict[str, Any]
    rung: str = ""
    registration_order: int = 0

    @property
    def config_id(self) -> str:
        return self.name

    @property
    def family_rank(self) -> int:
        return {"elastic_net": 0, "hist_gradient_boosting": 1}.get(self.family, -1)


def _registered_candidates() -> tuple[CandidateSpec, ...]:
    specs: list[CandidateSpec] = [
        CandidateSpec("B0", "constant_zero", "price_volume", 0, {}, "B0", 0),
        CandidateSpec("B1", "momentum", "price_volume", 1, {"window": 20}, "B1", 1),
    ]
    order = 2
    for feature_group in FEATURE_GROUPS:
        for alpha in (0.001, 0.01, 0.1):
            for l1_ratio in (0.1, 0.5, 0.9):
                config = f"a{alpha:g}-l{l1_ratio:g}"
                specs.append(
                    CandidateSpec(
                        f"B2-{feature_group}-{config}",
                        "elastic_net",
                        feature_group,
                        2 + FEATURE_GROUP_ORDER[feature_group],
                        {
                            "alpha": alpha,
                            "l1_ratio": l1_ratio,
                            "max_iter": 10000,
                            "tol": 1e-4,
                            "random_state": RANDOM_STATE,
                        },
                        "B2",
                        order,
                    )
                )
                order += 1
    for feature_group in FEATURE_GROUPS:
        for max_depth in (2, 3):
            for learning_rate in (0.05, 0.10):
                config = f"d{max_depth}-r{learning_rate:g}"
                specs.append(
                    CandidateSpec(
                        f"M1-{feature_group}-{config}",
                        "hist_gradient_boosting",
                        feature_group,
                        5 + FEATURE_GROUP_ORDER[feature_group],
                        {
                            "max_depth": max_depth,
                            "learning_rate": learning_rate,
                            "max_iter": 200,
                            "min_samples_leaf": 20,
                            "l2_regularization": 1.0,
                            "random_state": RANDOM_STATE,
                        },
                        "M1",
                        order,
                    )
                )
                order += 1
    return tuple(specs)


CANDIDATES = _registered_candidates()


class FoldPreprocessor(BaseEstimator, TransformerMixin):
    """Training-fold median imputation plus one indicator for every retained column."""

    def __init__(self, feature_columns: tuple[str, ...], missing_threshold: float = 0.30) -> None:
        self.feature_columns = tuple(feature_columns)
        self.missing_threshold = float(missing_threshold)

    def fit(self, X: pd.DataFrame, y: Any = None) -> "FoldPreprocessor":
        if not isinstance(X, pd.DataFrame):
            raise ModelError("fold preprocessing requires a pandas DataFrame")
        missing = [column for column in self.feature_columns if column not in X.columns]
        if missing:
            raise ModelError(f"features missing from fold: {missing}")
        frame = X.loc[:, self.feature_columns].apply(pd.to_numeric, errors="coerce")
        fractions = frame.isna().mean()
        self.dropped_feature_columns_ = tuple(
            column
            for column in self.feature_columns
            if float(fractions[column]) > self.missing_threshold
        )
        self.retained_feature_columns_ = tuple(
            column for column in self.feature_columns if column not in self.dropped_feature_columns_
        )
        if not self.retained_feature_columns_:
            raise ModelError("all features exceed the fold missingness threshold")
        self.medians_ = frame.loc[:, self.retained_feature_columns_].median()
        self.output_feature_names_ = self.retained_feature_columns_ + tuple(
            f"{column}__missing" for column in self.retained_feature_columns_
        )
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not hasattr(self, "retained_feature_columns_"):
            raise ModelError("fold preprocessor is not fitted")
        if not isinstance(X, pd.DataFrame):
            raise ModelError("fold preprocessing requires a pandas DataFrame")
        missing = [column for column in self.feature_columns if column not in X.columns]
        if missing:
            raise ModelError(f"features missing from fold: {missing}")
        frame = X.loc[:, self.retained_feature_columns_].apply(pd.to_numeric, errors="coerce")
        indicators = frame.isna().to_numpy(dtype=float)
        values = frame.fillna(self.medians_).to_numpy(dtype=float)
        return np.concatenate((values, indicators), axis=1)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        if not hasattr(self, "output_feature_names_"):
            raise ModelError("fold preprocessor is not fitted")
        return np.asarray(self.output_feature_names_, dtype=object)


@dataclass
class FittedModel:
    spec: CandidateSpec
    feature_columns: tuple[str, ...]
    estimator: Any | None = None

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        if self.spec.family == "constant_zero":
            return np.zeros(len(frame), dtype=float)
        if self.spec.family == "momentum":
            if "ret_20" not in frame:
                raise ModelError("B1 requires ret_20")
            return pd.to_numeric(frame["ret_20"], errors="coerce").fillna(0.0).to_numpy(dtype=float)
        if self.estimator is None:
            raise ModelError(f"{self.spec.name} has no fitted estimator")
        return np.asarray(self.estimator.predict(frame.loc[:, self.feature_columns]), dtype=float)

    @property
    def dropped_feature_columns(self) -> tuple[str, ...]:
        if self.estimator is None or "preprocess" not in self.estimator.named_steps:
            return ()
        return tuple(self.estimator.named_steps["preprocess"].dropped_feature_columns_)

    def save(self, path: str | Path) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, target)
        return sha256_file(target)

    @staticmethod
    def load(
        path: str | Path,
        *,
        expected_hash: str,
        expected_model_name: str | None = None,
        expected_feature_columns: tuple[str, ...] | None = None,
    ) -> "FittedModel":
        if sha256_file(path) != expected_hash:
            raise ModelError("model artifact hash mismatch; refusing to deserialize")
        model = joblib.load(path)
        if not isinstance(model, FittedModel) or model.spec not in CANDIDATES:
            raise ModelError("artifact is not a registered FittedModel")
        if expected_model_name is not None and model.spec.name != expected_model_name:
            raise ModelError("model artifact identity does not match its manifest")
        if (
            expected_feature_columns is not None
            and model.feature_columns != expected_feature_columns
        ):
            raise ModelError("model artifact feature schema does not match its manifest")
        return model


def _estimator_for(spec: CandidateSpec, feature_columns: tuple[str, ...]) -> Pipeline:
    preprocessor = FoldPreprocessor(feature_columns)
    if spec.family == "elastic_net":
        model = ElasticNet(
            alpha=spec.params["alpha"],
            l1_ratio=spec.params["l1_ratio"],
            max_iter=spec.params["max_iter"],
            tol=spec.params["tol"],
            random_state=spec.params["random_state"],
        )
        return Pipeline(
            [("preprocess", preprocessor), ("scale", StandardScaler()), ("model", model)]
        )
    if spec.family == "hist_gradient_boosting":
        model = HistGradientBoostingRegressor(
            max_iter=spec.params["max_iter"],
            max_depth=spec.params["max_depth"],
            min_samples_leaf=spec.params["min_samples_leaf"],
            learning_rate=spec.params["learning_rate"],
            l2_regularization=spec.params["l2_regularization"],
            random_state=spec.params["random_state"],
        )
        return Pipeline([("preprocess", preprocessor), ("model", model)])
    raise ModelError(f"unregistered model family: {spec.family}")


def fit_model(
    spec: CandidateSpec, frame: pd.DataFrame, target: pd.Series, feature_columns: tuple[str, ...]
) -> FittedModel:
    if spec.family in {"constant_zero", "momentum"}:
        return FittedModel(spec=spec, feature_columns=feature_columns)
    X = frame.loc[:, feature_columns]
    y = pd.to_numeric(target.reindex(frame.index), errors="coerce")
    valid = y.notna()
    if valid.sum() < 2:
        raise ModelError(f"{spec.name} has fewer than two target rows")
    estimator = _estimator_for(spec, feature_columns)
    estimator.fit(X.loc[valid], y.loc[valid])
    return FittedModel(spec=spec, feature_columns=feature_columns, estimator=estimator)


def registered_specs() -> tuple[CandidateSpec, ...]:
    return CANDIDATES


def _metric_column(results: pd.DataFrame, *names: str) -> str:
    for name in names:
        if name in results.columns:
            return name
    raise ModelError(f"promotion results missing one of: {list(names)}")


def choose_development_winner(results: pd.DataFrame) -> CandidateSpec:
    """Apply the frozen B1-only development promotion rule."""
    identity = _metric_column(results, "name", "config_id")
    ic_column = _metric_column(results, "mean_development_ic", "development_ic")
    fraction_column = _metric_column(
        results, "nonnegative_fold_fraction", "fold_ic_nonnegative_fraction"
    )
    names = results[identity].astype(str)
    baseline_rows = results[names.eq("B1")]
    if baseline_rows.empty:
        raise ModelError("promotion requires a B1 development result")
    baseline = baseline_rows.iloc[0]
    threshold = float(baseline[ic_column]) + 0.010
    passing = results.loc[
        ~names.isin({"B0", "B1"})
        & (pd.to_numeric(results[ic_column], errors="coerce") >= threshold)
        & (pd.to_numeric(results[fraction_column], errors="coerce") >= 0.60)
    ].copy()
    spec_by_name = {spec.name: spec for spec in CANDIDATES}
    passing = passing[passing[identity].astype(str).isin(spec_by_name)]
    if passing.empty:
        return next(spec for spec in CANDIDATES if spec.name == "B1")
    passing["complexity"] = passing[identity].map(lambda name: spec_by_name[str(name)].complexity)
    simplest = passing[passing["complexity"].eq(passing["complexity"].min())].copy()
    mean_ic = pd.to_numeric(simplest[ic_column], errors="coerce")
    tied = simplest[(mean_ic.max() - mean_ic) <= 1e-6].copy()
    tied["registration_order"] = tied[identity].map(
        lambda name: spec_by_name[str(name)].registration_order
    )
    tied = tied.sort_values("registration_order")
    return spec_by_name[str(tied.iloc[0][identity])]
