"""Small deterministic evaluation and experiment-record helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .hashing import sha256_json
from .metrics import rank_ic


@dataclass(frozen=True)
class ExperimentRecord:
    run_id: str
    project: str
    contract_version: str
    data_manifest_hash: str
    raw_response_hashes: tuple[str, ...]
    symbols: tuple[str, ...]
    feature_group: str
    feature_schema_hash: str
    model_name: str
    model_family: str
    model_params: dict[str, Any]
    fold_ids: tuple[str, ...]
    fold_ranges: tuple[dict[str, Any], ...]
    seed: int
    runtime: dict[str, str]
    code_commit: str
    execution_settings: dict[str, Any]
    metrics: dict[str, Any]
    warnings: tuple[str, ...] = ()
    output_artifact_hashes: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["raw_response_hashes"] = list(self.raw_response_hashes)
        data["symbols"] = list(self.symbols)
        data["fold_ids"] = list(self.fold_ids)
        data["fold_ranges"] = list(self.fold_ranges)
        data["warnings"] = list(self.warnings)
        data["output_artifact_hashes"] = list(self.output_artifact_hashes)
        data["created_at"] = self.created_at.astimezone(timezone.utc).isoformat()
        data["record_hash"] = sha256_json(data)
        return data


def write_experiment_record(path: str | Path, record: ExperimentRecord) -> None:
    from .hashing import canonical_json

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("ab") as handle:
        handle.write(canonical_json(record.as_dict()) + b"\n")


def prediction_metrics(
    rows: pd.DataFrame, *, prediction: str = "prediction", target: str = "target"
) -> dict[str, float]:
    required = {"decision_at", prediction, target}
    missing = required.difference(rows.columns)
    if missing:
        raise ValueError(f"prediction rows missing: {sorted(missing)}")
    data = rows[[prediction, target]].apply(pd.to_numeric, errors="coerce").dropna()
    if data.empty:
        return {
            "rank_ic": float("nan"),
            "mae": float("nan"),
            "rmse": float("nan"),
            "top_tercile_excess": float("nan"),
        }
    mean_ic, _ = rank_ic(rows, prediction=prediction, target=target)
    errors = data[prediction] - data[target]
    top_excess: list[float] = []
    for _, group in rows.groupby("decision_at", sort=True):
        group = group.copy()
        group[prediction] = pd.to_numeric(group[prediction], errors="coerce")
        group[target] = pd.to_numeric(group[target], errors="coerce")
        group = group.dropna(subset=[prediction, target])
        if len(group) < 3:
            continue
        threshold = group[prediction].quantile(2 / 3)
        top = group[group[prediction] >= threshold]
        if not top.empty:
            top_excess.append(float(top[target].mean() - group[target].mean()))
    return {
        "rank_ic": mean_ic,
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "top_tercile_excess": float(np.mean(top_excess)) if top_excess else float("nan"),
    }


def block_bootstrap(
    values: Iterable[float], *, block_size: int = 4, samples: int = 2_000, seed: int = 20250713
) -> pd.DataFrame:
    data = np.asarray(list(values), dtype=float)
    if data.size == 0 or block_size <= 0 or samples <= 0:
        raise ValueError("bootstrap requires values, positive block_size, and samples")
    rng = np.random.default_rng(seed)
    blocks = [data[index : index + block_size] for index in range(0, len(data) - block_size + 1)]
    if not blocks:
        blocks = [data]
    results = np.empty(samples, dtype=float)
    for sample in range(samples):
        selected = [
            blocks[int(index)]
            for index in rng.integers(
                0, len(blocks), size=max(1, math.ceil(len(data) / block_size))
            )
        ]
        results[sample] = float(np.concatenate(selected)[: len(data)].mean())
    return pd.DataFrame({"sample": np.arange(samples), "mean": results})
