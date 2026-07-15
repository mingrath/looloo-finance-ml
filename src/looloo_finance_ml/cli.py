"""Reproducible command-line surface for the research package."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
from typing import Any, Sequence
from uuid import uuid4
from collections import Counter

import numpy as np
import pandas as pd

from .config import RuntimeConfig
from .evaluation import (
    ExperimentRecord,
    block_bootstrap,
    prediction_metrics,
    write_experiment_record,
)
from .features import (
    ALL_FEATURE_COLUMNS,
    PRICE_FEATURE_COLUMNS,
    SEC_FEATURE_COLUMNS,
    build_labels,
    build_price_features,
    build_sec_features,
)
from .fixtures import FROZEN_SYMBOLS, synthetic_bars, synthetic_sec_facts
from .hashing import sha256_file, sha256_json
from .calendar import XNYSCalendar
from .manifests import (
    dataframe_schema_hash,
    manifest_for_frame,
    read_json,
    write_json,
    write_manifest,
)
from .metrics import cost_drag, one_way_turnover, portfolio_summary, rank_ic, weekly_returns
from .models import (
    FittedModel,
    RANDOM_STATE,
    choose_development_winner,
    fit_model,
    registered_specs,
)
from .paper import PaperConfig, PaperError, PaperLedger, ReplayResult
from .sources import AlpacaBarsClient, DataError, SecClient
from .http import HttpError
from .validation import ExpandingWalkForward, TemporalSpec, validate_holdout_seam
from .webull import WebullClient, normalize_webull_bars


HOLDOUT_START = pd.Timestamp("2025-01-01", tz="UTC")
HOLDOUT_END_EXCLUSIVE = pd.Timestamp("2026-01-01", tz="UTC")
EMBARGO_START = pd.Timestamp("2024-12-27", tz="UTC")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="looloo-finance-ml")
    parser.add_argument("--artifacts", default="artifacts")
    sub = parser.add_subparsers(dest="command", required=True)
    data = sub.add_parser("data-build")
    data.add_argument("--live", action="store_true")
    data.add_argument("--start", default="2018-01-01")
    data.add_argument("--end", default="2025-12-31")
    all_commands = sub.add_parser("all")
    all_commands.add_argument("--live", action="store_true")
    all_commands.add_argument("--start", default="2018-01-01")
    all_commands.add_argument("--end", default="2025-12-31")
    export = sub.add_parser("evidence-export")
    export.add_argument("--output", default="evidence")
    export.add_argument("--attempt-journal")
    sub.add_parser("evidence-selfcheck")
    sub.add_parser("train")
    sub.add_parser("evaluate")
    sub.add_parser("paper-run")
    sub.add_parser("report")
    webull = sub.add_parser("webull-compare")
    webull.add_argument("symbol", nargs="?", default="AAPL")
    webull.add_argument("--fixture", action="store_true")
    return parser


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def _read_bars(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing data prerequisite: {path}")
    return pd.read_csv(path, parse_dates=["bar_end_at"])


def _read_facts(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing data prerequisite: {path}")
    return pd.read_csv(path, parse_dates=["period_start", "period_end", "filed_at", "accepted_at"])


def _write_hashed_json(path: Path, value: dict[str, Any]) -> dict[str, Any]:
    payload = {**value, "manifest_hash": sha256_json(value)}
    write_json(path, payload)
    return payload


def _read_hashed_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing manifest prerequisite: {path}")
    payload = read_json(path)
    if not isinstance(payload, dict) or "manifest_hash" not in payload:
        raise RuntimeError(f"invalid manifest: {path}")
    content = {key: value for key, value in payload.items() if key != "manifest_hash"}
    if sha256_json(content) != payload["manifest_hash"]:
        raise RuntimeError(f"manifest hash mismatch: {path}")
    return payload


PUBLIC_EVIDENCE_FILES = (
    "evidence_report.md",
    "experiment_results.csv",
    "fold_metrics.csv",
    "predictive_robustness.csv",
    "development_portfolio_comparison.csv",
    "paper_weekly_returns.csv",
    "paper_model_comparison.csv",
    "paper_cost_sensitivity.csv",
    "paper_skip_counts.csv",
)


def _write_public_report(source: Path, destination: Path) -> None:
    report = source.read_text(encoding="utf-8")
    public, marker, _ = report.partition("\n## Artifact index\n")
    if not marker:
        raise RuntimeError("evidence report is missing its private artifact index")
    destination.write_text(public.rstrip() + "\n", encoding="utf-8")


def _public_source_requests(manifests: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    return [
        {
            "source": manifest["source"],
            "stream": manifest["stream"],
            "endpoint_family": "https://data.alpaca.markets/v2/stocks/bars"
            if manifest["source"] == "alpaca"
            else "https://data.sec.gov/api/xbrl",
            "params": {
                key: value
                for key, value in manifest["params"].items()
                if key in {"adjustment", "asof", "currency", "feed", "forms", "sort", "timeframe"}
            },
            "response_hash": manifest["response_hash"],
            "retrieved_at": manifest["retrieved_at"],
        }
        for manifest in manifests.values()
    ]


def _attempt_summary(path: Path, data_manifest_hash: str) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"missing live attempt journal: {path}")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    accepted = [row for row in rows if row.get("outcome") == "accepted"]
    if len(accepted) != 1 or accepted[0].get("data_manifest_hash") != data_manifest_hash:
        raise RuntimeError("attempt journal does not identify this accepted snapshot")
    reasons = Counter(str(row["reason"]) for row in rows if row.get("outcome") == "rejected")
    attempts = [
        {
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
            "outcome": row["outcome"],
            "reason": row["reason"],
        }
        for row in rows
    ]
    return {
        "attempt_count": len(rows),
        "accepted_snapshot_hash": data_manifest_hash,
        "rejected_reason_counts": dict(sorted(reasons.items())),
        "attempts": attempts,
    }


def _build_evidence_package(
    destination_root: Path,
    *,
    run_dir: Path,
    run_id: object,
    data_manifest_hash: str,
    code_commit: str,
    manifests: dict[str, dict[str, Any]],
    journal: Path,
) -> dict[str, object]:
    from .evidence import (
        ALLOWLIST_VERSION,
        EVIDENCE_SCHEMA_VERSION,
        HASHED_PUBLIC_FILES,
        validate_public_evidence,
    )

    if destination_root.exists():
        raise RuntimeError("public evidence root already exists")
    package = destination_root / data_manifest_hash[:12]
    package.mkdir(parents=True)
    for filename in PUBLIC_EVIDENCE_FILES:
        source = run_dir / filename
        if not source.exists():
            raise FileNotFoundError(f"missing public evidence source: {source}")
        destination = package / filename
        if filename == "evidence_report.md":
            _write_public_report(source, destination)
        else:
            shutil.copyfile(source, destination)
    provenance = {
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "allowlist_version": ALLOWLIST_VERSION,
        "source_mode": "live",
        "run_id": run_id,
        "data_manifest_hash": data_manifest_hash,
        "code_commit": code_commit,
        "lockfile_hash": sha256_file(Path("uv.lock")),
        "runtime": {**_runtime_versions(), "os": platform.platform(), "architecture": platform.machine()},
        "source_requests": _public_source_requests(manifests),
        "attempt_summary": _attempt_summary(journal, data_manifest_hash),
    }
    write_json(package / "public_provenance.json", provenance)
    write_json(
        package / "public_artifact_index.json",
        {
            "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
            "files": {name: sha256_file(package / name) for name in HASHED_PUBLIC_FILES},
        },
    )
    write_json(
        package / "review_attestation.json",
        {
            "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
            "allowlist_version": ALLOWLIST_VERSION,
            "status": "pending",
            "reviewer_handle": "",
            "public_contact": "",
            "reviewed_at": "",
            "code_commit": code_commit,
            "ci_result": "pending",
            "ci_run_url": "",
            "source_snapshot_hash": data_manifest_hash,
            "public_artifact_index_hash": sha256_file(package / "public_artifact_index.json"),
            "terms_url": "",
            "terms_version": "",
            "terms_accessed_at": "",
            "terms_publication_decision": "pending",
            "attestation": "",
        },
    )
    write_json(
        destination_root / "CANONICAL.json",
        {
            "directory": package.name,
            "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
            "snapshot_manifest_hash": data_manifest_hash,
        },
    )
    validate_public_evidence(destination_root, pending=True)
    return {"evidence_directory": str(package), "data_manifest_hash": data_manifest_hash}


def _export_evidence(args: argparse.Namespace, root: Path) -> dict[str, object]:
    data_summary = read_json(root / "data_build_summary.json")
    if data_summary["source_mode"] != "live":
        raise RuntimeError("public evidence export requires a live source snapshot")
    active = _read_hashed_json(root / "active_run.json")
    model_manifest = _read_hashed_json(Path(str(active["model_manifest"])))
    data_manifest_hash, _, manifests = _data_provenance(root)
    if model_manifest["code_commit"] != _checked_live_commit():
        raise RuntimeError("export must run from the exact commit recorded by the live run")
    journal = (
        Path(args.attempt_journal)
        if args.attempt_journal
        else root.parent / f".{root.name}.attempts.jsonl"
    )
    return _build_evidence_package(
        Path(args.output),
        run_dir=Path(str(active["run_directory"])),
        run_id=active["run_id"],
        data_manifest_hash=data_manifest_hash,
        code_commit=str(model_manifest["code_commit"]),
        manifests=manifests,
        journal=journal,
    )


def _selfcheck_evidence(args: argparse.Namespace, root: Path) -> dict[str, object]:
    """Exercise the packaging path against any completed run, then discard the output."""
    del args
    active = _read_hashed_json(root / "active_run.json")
    model_manifest = _read_hashed_json(Path(str(active["model_manifest"])))
    data_manifest_hash, _, manifests = _data_provenance(root)
    scratch = Path(tempfile.mkdtemp())
    journal = scratch / "attempts.jsonl"
    journal.write_text(
        json.dumps(
            {
                "attempt_id": "selfcheck",
                "started_at": "1970-01-01T00:00:00+00:00",
                "finished_at": "1970-01-01T00:00:01+00:00",
                "outcome": "accepted",
                "reason": "contract_valid",
                "data_manifest_hash": data_manifest_hash,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        _build_evidence_package(
            scratch / "evidence",
            run_dir=Path(str(active["run_directory"])),
            run_id=active["run_id"],
            data_manifest_hash=data_manifest_hash,
            code_commit=str(model_manifest["code_commit"]),
            manifests=manifests,
            journal=journal,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return {"evidence_selfcheck": "ok", "data_manifest_hash": data_manifest_hash}


def _data_provenance(root: Path) -> tuple[str, tuple[str, ...], dict[str, dict[str, Any]]]:
    manifests = {
        name: _read_hashed_json(root / f"{name}_manifest.json")
        for name in ("feature", "label", "sec")
    }
    bundle = _read_hashed_json(root / "data_artifact_manifest.json")
    expected_manifest_hashes = {
        name: manifest["manifest_hash"] for name, manifest in manifests.items()
    }
    if bundle["source_manifest_hashes"] != expected_manifest_hashes:
        raise RuntimeError("data artifact and source manifests disagree")
    for filename, digest in bundle["artifact_hashes"].items():
        if sha256_file(root / filename) != digest:
            raise RuntimeError(f"data artifact hash mismatch: {filename}")
    raw_hashes = tuple(
        str(manifests[name]["response_hash"]) for name in ("feature", "label", "sec")
    )
    expected_summary = {
        "source_mode": bundle["source_mode"],
        "data_manifest_hash": bundle["manifest_hash"],
        "feature_manifest_hash": manifests["feature"]["manifest_hash"],
        "label_manifest_hash": manifests["label"]["manifest_hash"],
        "sec_manifest_hash": manifests["sec"]["manifest_hash"],
        "raw_response_hashes": list(raw_hashes),
        "feature_rows": manifests["feature"]["row_count"],
        "label_rows": manifests["label"]["row_count"],
        "sec_rows": manifests["sec"]["row_count"],
        "complete_history_symbol_count": len(
            read_json(root / "complete_history_subset.json")["symbols"]
        ),
    }
    if read_json(root / "data_build_summary.json") != expected_summary:
        raise RuntimeError("data build summary does not match immutable data artifacts")
    return str(bundle["manifest_hash"]), raw_hashes, manifests


def _complete_history(feature_bars: pd.DataFrame, start: str, end: str) -> dict[str, Any]:
    expected = [session.session_date for session in XNYSCalendar().sessions(start, end)]
    bars = feature_bars.copy()
    bars["bar_end_at"] = pd.to_datetime(bars["bar_end_at"], utc=True)
    diagnostics: dict[str, dict[str, Any]] = {}
    subset: list[str] = []
    for symbol in FROZEN_SYMBOLS:
        observed = set(
            bars.loc[bars["symbol"].astype(str).str.upper().eq(symbol), "bar_end_at"].dt.date
        )
        run = longest = 0
        for session_date in expected:
            run = 0 if session_date in observed else run + 1
            longest = max(longest, run)
        coverage = len(observed.intersection(expected)) / len(expected) if expected else 0.0
        diagnostics[symbol] = {"coverage": coverage, "longest_missing_session_run": longest}
        if coverage >= 0.95 and longest <= 5:
            subset.append(symbol)
    return {
        "symbols": subset,
        "criteria": {"minimum_coverage": 0.95, "maximum_missing_session_run": 5},
        "diagnostics": diagnostics,
    }


def data_build(args: argparse.Namespace, root: Path) -> dict[str, object]:
    if (root / "data_artifact_manifest.json").exists() or (root / "active_run.json").exists():
        raise RuntimeError("artifact root is immutable; use a fresh artifact directory")
    config = RuntimeConfig.from_env()
    if args.live:
        client = AlpacaBarsClient.from_config(config)
        feature_bars, feature_manifest = client.fetch_bars(
            FROZEN_SYMBOLS, args.start, args.end, adjustment="split", stream="feature_stream"
        )
        label_bars, label_manifest = client.fetch_bars(
            FROZEN_SYMBOLS, args.start, args.end, adjustment="all", stream="label_fill_stream"
        )
        sec, sec_response_hash = SecClient.from_config(config).facts_for_symbols(FROZEN_SYMBOLS)
        sec_manifest = manifest_for_frame(
            sec,
            source="sec",
            stream="sec_facts",
            params={"forms": ["10-Q", "10-Q/A", "10-K", "10-K/A"]},
            symbols=FROZEN_SYMBOLS,
            start=args.start,
            end=args.end,
            raw_response_digest=sec_response_hash,
            notes=("accepted_at is the point-in-time availability boundary",),
        )
    else:
        feature_bars = synthetic_bars(args.start, args.end, adjustment="split")
        label_bars = synthetic_bars(args.start, args.end, adjustment="all")
        sec = synthetic_sec_facts(start="2018-01-01", end=args.end)
        feature_manifest = manifest_for_frame(
            feature_bars,
            source="synthetic",
            stream="feature_stream",
            params={"adjustment": "split"},
            symbols=FROZEN_SYMBOLS,
            start=args.start,
            end=args.end,
            raw_payload=feature_bars.to_dict("records"),
            notes=("offline fixture",),
        )
        label_manifest = manifest_for_frame(
            label_bars,
            source="synthetic",
            stream="label_fill_stream",
            params={"adjustment": "all"},
            symbols=FROZEN_SYMBOLS,
            start=args.start,
            end=args.end,
            raw_payload=label_bars.to_dict("records"),
            notes=("offline fixture",),
        )
        sec_manifest = manifest_for_frame(
            sec,
            source="synthetic",
            stream="sec_facts",
            params={"forms": ["10-Q", "10-Q/A", "10-K", "10-K/A"]},
            symbols=FROZEN_SYMBOLS,
            start=args.start,
            end=args.end,
            raw_payload=sec.to_dict("records"),
            notes=("offline fixture", "accepted_at is the point-in-time availability boundary"),
        )
    _write_csv(root / "feature_bars.csv", feature_bars)
    _write_csv(root / "label_fill_bars.csv", label_bars)
    _write_csv(root / "sec_facts.csv", sec)
    write_manifest(root / "feature_manifest.json", feature_manifest)
    write_manifest(root / "label_manifest.json", label_manifest)
    write_manifest(root / "sec_manifest.json", sec_manifest)
    complete_history = _complete_history(feature_bars, args.start, args.end)
    write_json(root / "complete_history_subset.json", complete_history)
    source_mode = "live" if args.live else "synthetic"
    data_artifact_manifest = _write_hashed_json(
        root / "data_artifact_manifest.json",
        {
            "contract_version": "finance-ml-v1",
            "source_mode": source_mode,
            "source_manifest_hashes": {
                "feature": feature_manifest.manifest_hash,
                "label": label_manifest.manifest_hash,
                "sec": sec_manifest.manifest_hash,
            },
            "artifact_hashes": {
                filename: sha256_file(root / filename)
                for filename in (
                    "feature_bars.csv",
                    "label_fill_bars.csv",
                    "sec_facts.csv",
                    "complete_history_subset.json",
                )
            },
        },
    )
    data_manifest_hash = str(data_artifact_manifest["manifest_hash"])
    result = {
        "source_mode": source_mode,
        "data_manifest_hash": data_manifest_hash,
        "feature_manifest_hash": feature_manifest.manifest_hash,
        "label_manifest_hash": label_manifest.manifest_hash,
        "sec_manifest_hash": sec_manifest.manifest_hash,
        "raw_response_hashes": [
            feature_manifest.response_hash,
            label_manifest.response_hash,
            sec_manifest.response_hash,
        ],
        "feature_rows": len(feature_bars),
        "label_rows": len(label_bars),
        "sec_rows": len(sec),
        "complete_history_symbol_count": len(complete_history["symbols"]),
    }
    write_json(root / "data_build_summary.json", result)
    return result


def _feature_columns(feature_group: str) -> tuple[str, ...]:
    if feature_group == "price_volume":
        return PRICE_FEATURE_COLUMNS
    if feature_group == "fundamentals":
        return SEC_FEATURE_COLUMNS
    if feature_group == "combined":
        return ALL_FEATURE_COLUMNS
    raise ValueError(f"unknown feature group: {feature_group}")


def _drop_incomplete_dates(
    frame: pd.DataFrame, *, name: str, expected_dates: set[pd.Timestamp]
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    expected_symbols = set(FROZEN_SYMBOLS)
    grouped = {
        pd.Timestamp(decision_at): group
        for decision_at, group in frame.groupby("decision_at", sort=True)
    }
    bad_dates: set[pd.Timestamp] = set()
    diagnostics: list[dict[str, object]] = []
    for decision_at in sorted(expected_dates.union(grouped)):
        group = grouped.get(decision_at, frame.iloc[0:0])
        normalized = group["symbol"].astype(str).str.upper()
        observed = set(normalized)
        duplicates = sorted(normalized[normalized.duplicated()].unique())
        if observed != expected_symbols or len(group) != len(expected_symbols):
            bad_dates.add(decision_at)
            diagnostics.append(
                {
                    "decision_at": decision_at,
                    "source": name,
                    "reason": "incomplete_cross_section",
                    "missing_symbols": sorted(expected_symbols.difference(observed)),
                    "extra_symbols": sorted(observed.difference(expected_symbols)),
                    "duplicate_symbols": duplicates,
                }
            )
    return frame[~frame["decision_at"].isin(bad_dates)].copy(), diagnostics


def _assert_complete_dates(frame: pd.DataFrame, *, name: str) -> None:
    expected = set(FROZEN_SYMBOLS)
    for decision_at, group in frame.groupby("decision_at", sort=True):
        normalized = group["symbol"].astype(str).str.upper()
        observed = set(normalized)
        if observed != expected or len(group) != len(expected):
            raise RuntimeError(
                f"{name} retained an incomplete cross-section at {decision_at}: missing={sorted(expected.difference(observed))}, extra={sorted(observed.difference(expected))}"
            )


def _assert_finite_columns(frame: pd.DataFrame, columns: tuple[str, ...], *, name: str) -> None:
    invalid = pd.Series(False, index=frame.index)
    for column in columns:
        invalid |= ~np.isfinite(pd.to_numeric(frame[column], errors="coerce"))
    if invalid.any():
        sample = frame.loc[invalid, ["decision_at", "symbol", *columns]].head(10).to_dict("records")
        raise RuntimeError(f"{name} contains non-finite values: {sample}")


def _build_training_rows(root: Path) -> pd.DataFrame:
    feature_bars = _read_bars(root / "feature_bars.csv")
    label_bars = _read_bars(root / "label_fill_bars.csv")
    facts = _read_facts(root / "sec_facts.csv")
    calendar = XNYSCalendar()
    decision_sessions = calendar.weekly_decisions("2021-01-01", "2025-12-31")
    price = build_price_features(feature_bars)
    decision_dates = {pd.Timestamp(session.close_at) for session in decision_sessions}
    price = price[price["decision_at"].isin(decision_dates)]
    sec = build_sec_features(
        facts, [session.close_at for session in decision_sessions], symbols=FROZEN_SYMBOLS
    )
    labels, skipped = build_labels(
        label_bars, decision_sessions, symbols=FROZEN_SYMBOLS, calendar=calendar
    )
    if labels.empty:
        raise RuntimeError("label build produced no eligible rows")
    price, price_skips = _drop_incomplete_dates(
        price, name="price_features", expected_dates=decision_dates
    )
    sec, sec_skips = _drop_incomplete_dates(sec, name="sec_features", expected_dates=decision_dates)
    labels, label_skips = _drop_incomplete_dates(
        labels, name="labels", expected_dates=decision_dates
    )
    bad_dates = {item["decision_at"] for item in (*price_skips, *sec_skips, *label_skips)}
    price = price[~price["decision_at"].isin(bad_dates)]
    sec = sec[~sec["decision_at"].isin(bad_dates)]
    labels = labels[~labels["decision_at"].isin(bad_dates)]
    _assert_complete_dates(labels, name="labels")
    features = price.merge(sec, on=["symbol", "decision_at"], how="left", validate="one_to_one")
    rows = labels.merge(features, on=["symbol", "decision_at"], how="inner", validate="one_to_one")
    if rows.empty:
        raise RuntimeError("feature/label join produced no rows")
    _assert_complete_dates(rows, name="training")
    _assert_finite_columns(rows, ("target",), name="training labels")
    closes = (
        feature_bars.sort_values(["symbol", "bar_end_at"])
        .groupby("symbol", sort=False)["close"]
        .pct_change(fill_method=None)
    )
    diagnostics = {
        "feature_bar_rows": len(feature_bars),
        "label_fill_bar_rows": len(label_bars),
        "sec_fact_rows": len(facts),
        "eligible_rows": len(rows),
        "development_rows": int(
            ((rows["decision_at"] < EMBARGO_START) & (rows["label_end"] < HOLDOUT_START)).sum()
        ),
        "holdout_rows": int(
            (
                (rows["decision_at"] >= HOLDOUT_START)
                & (rows["decision_at"] < HOLDOUT_END_EXCLUSIVE)
            ).sum()
        ),
        "dropped_decision_count": len(bad_dates),
        "close_return_volatility": float(pd.to_numeric(closes, errors="coerce").std()),
        "feature_missing_fractions": {
            column: float(rows[column].isna().mean()) for column in ALL_FEATURE_COLUMNS
        },
    }
    write_json(root / "input_diagnostics.json", diagnostics)
    _write_csv(
        root / "development_rows.csv",
        rows[(rows["decision_at"] < EMBARGO_START) & (rows["label_end"] < HOLDOUT_START)],
    )
    _write_csv(
        root / "label_skips.csv",
        pd.concat(
            [skipped, pd.DataFrame([*price_skips, *sec_skips, *label_skips])], ignore_index=True
        ),
    )
    return rows


def _runtime_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "exchange_calendars": version("exchange-calendars"),
        "joblib": version("joblib"),
        "numpy": version("numpy"),
        "pandas": version("pandas"),
        "scikit_learn": version("scikit-learn"),
        "looloo_finance_ml": version("looloo-finance-ml"),
    }


def _git_output(*args: str) -> str:
    if shutil.which("git") is None:
        raise RuntimeError("live evidence requires a Git checkout")
    result = subprocess.run(
        ("git", *args), capture_output=True, check=False, text=True
    )
    if result.returncode:
        raise RuntimeError("live evidence requires a Git checkout")
    return result.stdout.strip()


def _checked_live_commit() -> str:
    value = os.environ.get("GIT_COMMIT", os.environ.get("CODE_COMMIT", "")).strip()
    if not value:
        raise RuntimeError("GIT_COMMIT is required for a live evidence run")
    head = _git_output("rev-parse", "HEAD")
    if value != head:
        raise RuntimeError("GIT_COMMIT must match the checked-out HEAD for a live evidence run")
    if _git_output("status", "--porcelain"):
        raise RuntimeError("live evidence requires a clean Git worktree")
    return head


def _code_commit(root: Path) -> str:
    source_mode = _read_hashed_json(root / "data_artifact_manifest.json")["source_mode"]
    value = os.environ.get("GIT_COMMIT", os.environ.get("CODE_COMMIT", "")).strip()
    if source_mode != "live":
        return value or "working-tree"
    return _checked_live_commit()


def _append_live_attempt(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, default=str, sort_keys=True) + "\n")


def _live_data_build(args: argparse.Namespace, root: Path) -> dict[str, object]:
    from .evidence import ATTEMPT_ACCEPTED_REASON
    _checked_live_commit()
    if root.exists():
        raise RuntimeError("live evidence target must not exist; use a fresh artifact directory")
    started_at = datetime.now(timezone.utc)
    attempt_id = uuid4().hex
    staging = root.parent / ".staging" / f"{root.name}-{attempt_id}"
    journal = root.parent / f".{root.name}.attempts.jsonl"
    staging.mkdir(parents=True, exist_ok=False)
    try:
        result = data_build(args, staging)
    except Exception as exc:
        reason = (
            "transport_failure"
            if isinstance(exc, HttpError)
            else "contract_validation_failure"
            if isinstance(exc, DataError)
            else "unexpected_failure"
        )
        _append_live_attempt(
            journal,
            {
                "attempt_id": attempt_id,
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc),
                "outcome": "rejected",
                "reason": reason,
            },
        )
        shutil.rmtree(staging, ignore_errors=True)
        raise
    staging.replace(root)
    _append_live_attempt(
        journal,
        {
            "attempt_id": attempt_id,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc),
            "outcome": "accepted",
            "reason": ATTEMPT_ACCEPTED_REASON,
            "data_manifest_hash": result["data_manifest_hash"],
        },
    )
    return result


def train(args: argparse.Namespace, root: Path) -> dict[str, object]:
    del args
    data_manifest_hash, raw_response_hashes, _ = _data_provenance(root)
    if (root / "holdout_reveal.json").exists():
        raise RuntimeError(
            "this artifact root already contains a final-holdout reveal; use a fresh root rather than reopening 2025"
        )
    rows = _build_training_rows(root)
    temporal = ExpandingWalkForward(TemporalSpec())
    folds = temporal.split(rows)
    specs = registered_specs()
    created_at = datetime.now(timezone.utc)
    run_id = f"{created_at.strftime('%Y%m%dT%H%M%S%fZ')}-{data_manifest_hash[:8]}"
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    code_commit = _code_commit(root)
    runtime = _runtime_versions()
    fold_ranges = tuple(
        {
            "fold_id": fold.fold_id,
            "train_start": fold.train_start,
            "train_end": fold.train_end,
            "validation_start": fold.validation_start,
            "validation_end": fold.validation_end,
            "embargo_start": fold.embargo_start,
            "purged_count": fold.purged_count,
        }
        for fold in folds
    )
    write_json(run_dir / "folds.json", {"folds": list(fold_ranges)})
    b1_ics: list[float] = []
    results: list[dict[str, object]] = []
    all_fold_metrics: list[dict[str, object]] = []
    model_oof_artifacts: dict[str, dict[str, Any]] = {}
    candidate_fold_artifacts: dict[str, dict[str, str]] = {}
    for spec in specs:
        feature_columns = _feature_columns(spec.feature_group)
        feature_schema_hash = sha256_json(
            {
                "columns": list(feature_columns),
                "schema": dataframe_schema_hash(rows.loc[:, list(feature_columns)]),
            }
        )
        fold_ics: list[float] = []
        errors: list[str] = []
        candidate_fold_metrics: list[dict[str, object]] = []
        candidate_predictions: list[pd.DataFrame] = []
        for fold in folds:
            train_rows = rows.loc[list(fold.train_index)]
            validation_rows = rows.loc[list(fold.validation_index)]
            fold_row: dict[str, object] = {
                "model": spec.name,
                "fold_id": fold.fold_id,
                "train_start": fold.train_start,
                "train_end": fold.train_end,
                "validation_start": fold.validation_start,
                "validation_end": fold.validation_end,
                "embargo_start": fold.embargo_start,
                "train_rows": len(train_rows),
                "validation_rows": len(validation_rows),
                "purged_rows": fold.purged_count,
            }
            try:
                fitted = fit_model(spec, train_rows, train_rows["target"], feature_columns)
                validation = validation_rows.copy()
                validation["prediction"] = fitted.predict(validation)
                _assert_finite_columns(
                    validation, ("prediction", "target"), name=f"{spec.name} validation"
                )
                validation["fold_id"] = fold.fold_id
                candidate_predictions.append(
                    validation[
                        ["decision_at", "symbol", "prediction", "target", "label_end", "fold_id"]
                    ]
                )
                metrics = prediction_metrics(validation, prediction="prediction", target="target")
                ic = float(metrics["rank_ic"])
                if not np.isfinite(ic) and spec.name != "B0":
                    raise RuntimeError(
                        "undefined rank IC from constant or missing validation predictions"
                    )
                fold_ics.append(ic)
                fold_row.update(metrics)
                fold_row["dropped_features"] = json.dumps(fitted.dropped_feature_columns)
                fold_row["error"] = ""
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                errors.append(error)
                fold_ics.append(float("nan"))
                fold_row.update(
                    {
                        "rank_ic": None,
                        "mae": None,
                        "rmse": None,
                        "top_tercile_excess": None,
                        "rank_ic_dates": 0,
                        "dropped_features": "[]",
                        "error": error,
                    }
                )
            candidate_fold_metrics.append(fold_row)
            all_fold_metrics.append(fold_row)
        completed = len(fold_ics) == len(folds) and all(np.isfinite(value) for value in fold_ics)
        if spec.name == "B1":
            b1_ics = fold_ics
            if not completed:
                raise RuntimeError(f"B1 failed one or more development folds: {errors}")
        mean_ic = float(np.mean(fold_ics)) if completed else None
        nonnegative = (
            float(np.mean([candidate >= baseline for candidate, baseline in zip(fold_ics, b1_ics)]))
            if completed
            and len(b1_ics) == len(fold_ics)
            and all(np.isfinite(value) for value in b1_ics)
            else None
        )
        result_row: dict[str, object] = {
            "name": spec.name,
            "family": spec.family,
            "feature_group": spec.feature_group,
            "mean_development_ic": mean_ic,
            "nonnegative_fold_fraction": nonnegative,
            "completed_fold_count": sum(np.isfinite(value) for value in fold_ics),
            "fold_ics": json.dumps([value if np.isfinite(value) else None for value in fold_ics]),
            "errors": json.dumps(errors),
        }
        results.append(result_row)
        candidate_path = run_dir / f"{spec.name}_fold_metrics.csv"
        _write_csv(candidate_path, pd.DataFrame(candidate_fold_metrics))
        candidate_fold_artifacts[spec.name] = {
            "path": str(candidate_path),
            "hash": sha256_file(candidate_path),
        }
        candidate_oof_path = run_dir / "model_oof" / f"{spec.name}.csv"
        candidate_oof = (
            pd.concat(candidate_predictions, ignore_index=True)
            if candidate_predictions
            else pd.DataFrame(
                columns=["decision_at", "symbol", "prediction", "target", "label_end", "fold_id"]
            )
        )
        _write_csv(candidate_oof_path, candidate_oof)
        model_oof_artifacts[spec.name] = {
            "path": str(candidate_oof_path),
            "hash": sha256_file(candidate_oof_path),
            "family": spec.family,
            "feature_group": spec.feature_group,
            "feature_schema_hash": feature_schema_hash,
        }
        record_metrics = {"completed_fold_count": float(result_row["completed_fold_count"])}
        if mean_ic is not None:
            record_metrics["mean_development_ic"] = mean_ic
        if nonnegative is not None:
            record_metrics["nonnegative_fold_fraction"] = nonnegative
        record = ExperimentRecord(
            project="cross-sectional-equity-return-ranking",
            contract_version="finance-ml-v1",
            data_manifest_hash=data_manifest_hash,
            raw_response_hashes=raw_response_hashes,
            symbols=FROZEN_SYMBOLS,
            feature_group=spec.feature_group,
            feature_schema_hash=feature_schema_hash,
            model_name=spec.name,
            model_family=spec.family,
            model_params=spec.params,
            fold_ids=tuple(fold.fold_id for fold in folds),
            fold_ranges=fold_ranges,
            seed=RANDOM_STATE,
            runtime=runtime,
            code_commit=code_commit,
            execution_settings={
                "missing_threshold": 0.30,
                "imputation": "training-fold median",
                "holdout_start": HOLDOUT_START,
                "holdout_end_exclusive": HOLDOUT_END_EXCLUSIVE,
                "embargo_start": EMBARGO_START,
            },
            metrics=record_metrics,
            warnings=tuple(errors),
            output_artifact_hashes=(sha256_file(candidate_path), sha256_file(candidate_oof_path)),
            run_id=f"{run_id}-{spec.name}",
        )
        write_experiment_record(run_dir / "experiment_records.jsonl", record)
        write_experiment_record(root / "experiment_records.jsonl", record)
    model_oof_index = _write_hashed_json(
        run_dir / "model_oof_index.json", {"models": model_oof_artifacts}
    )
    result_frame = pd.DataFrame(results)
    _write_csv(run_dir / "experiment_results.csv", result_frame)
    _write_csv(run_dir / "fold_metrics.csv", pd.DataFrame(all_fold_metrics))
    winner = choose_development_winner(
        result_frame[["name", "mean_development_ic", "nonnegative_fold_fraction"]]
    )
    development = rows[
        (rows["decision_at"] < HOLDOUT_START)
        & (rows["label_end"] < HOLDOUT_START)
        & (rows["decision_at"] < EMBARGO_START)
    ].copy()
    validate_holdout_seam(development, holdout_start="2025-01-01", embargo_start="2024-12-27")
    feature_columns = _feature_columns(winner.feature_group)
    oof_parts: list[pd.DataFrame] = []
    for fold in folds:
        fold_train = rows.loc[list(fold.train_index)]
        fold_validation = rows.loc[list(fold.validation_index)].copy()
        fold_model = fit_model(winner, fold_train, fold_train["target"], feature_columns)
        fold_validation["prediction"] = fold_model.predict(fold_validation)
        volatility_threshold = float(
            fold_train.groupby("decision_at", sort=True)["rv20"].mean().median()
        )
        fold_validation["fold_id"] = fold.fold_id
        fold_validation["volatility_threshold"] = volatility_threshold
        validation_volatility = fold_validation.groupby("decision_at", sort=True)["rv20"].transform(
            "mean"
        )
        fold_validation["volatility_regime"] = np.where(
            validation_volatility <= volatility_threshold, "low", "high"
        )
        oof_parts.append(
            fold_validation[
                [
                    "decision_at",
                    "symbol",
                    "prediction",
                    "target",
                    "label_end",
                    "rv20",
                    "fold_id",
                    "volatility_threshold",
                    "volatility_regime",
                ]
            ]
        )
    oof = pd.concat(oof_parts, ignore_index=True)
    _assert_finite_columns(
        oof,
        ("prediction", "target", "rv20", "volatility_threshold"),
        name="development OOF predictions",
    )
    oof_path = run_dir / "development_oof_predictions.csv"
    _write_csv(oof_path, oof)
    fitted = fit_model(winner, development, development["target"], feature_columns)
    holdout = rows[
        (rows["decision_at"] >= HOLDOUT_START) & (rows["decision_at"] < HOLDOUT_END_EXCLUSIVE)
    ].copy()
    if holdout.empty:
        raise RuntimeError("final holdout produced no rows")
    _assert_complete_dates(holdout, name="holdout")
    holdout["prediction"] = fitted.predict(holdout)
    final_volatility_threshold = float(
        development.groupby("decision_at", sort=True)["rv20"].mean().median()
    )
    holdout["volatility_threshold"] = final_volatility_threshold
    holdout_volatility = holdout.groupby("decision_at", sort=True)["rv20"].transform("mean")
    holdout["volatility_regime"] = np.where(
        holdout_volatility <= final_volatility_threshold, "low", "high"
    )
    _assert_finite_columns(holdout, ("prediction", "target"), name="holdout predictions")
    prediction_columns = [
        "decision_at",
        "symbol",
        "prediction",
        "target",
        "label_end",
        "rv20",
        "volatility_threshold",
        "volatility_regime",
    ]
    predictions_path = run_dir / "predictions.csv"
    holdout_path = run_dir / "holdout_features.csv"
    _write_csv(predictions_path, holdout.loc[:, prediction_columns])
    _write_csv(holdout_path, holdout)
    artifact = run_dir / "model.joblib"
    artifact_hash = fitted.save(artifact)
    feature_schema_hash = sha256_json(
        {
            "columns": list(feature_columns),
            "schema": dataframe_schema_hash(development.loc[:, list(feature_columns)]),
        }
    )
    model_manifest = _write_hashed_json(
        run_dir / "model_manifest.json",
        {
            "contract_version": "finance-ml-v1",
            "run_id": run_id,
            "created_at": created_at,
            "artifact": str(artifact),
            "artifact_hash": artifact_hash,
            "model_name": winner.name,
            "model_family": winner.family,
            "model_params": winner.params,
            "feature_columns": list(feature_columns),
            "feature_schema_hash": feature_schema_hash,
            "feature_group": winner.feature_group,
            "data_manifest_hash": data_manifest_hash,
            "code_commit": code_commit,
            "predictions": str(predictions_path),
            "predictions_hash": sha256_file(predictions_path),
            "holdout_features": str(holdout_path),
            "holdout_features_hash": sha256_file(holdout_path),
            "development_oof_predictions": str(oof_path),
            "development_oof_predictions_hash": sha256_file(oof_path),
            "model_oof_index": str(run_dir / "model_oof_index.json"),
            "model_oof_index_hash": model_oof_index["manifest_hash"],
            "folds_hash": sha256_file(run_dir / "folds.json"),
            "experiment_results_hash": sha256_file(run_dir / "experiment_results.csv"),
            "fold_metrics_hash": sha256_file(run_dir / "fold_metrics.csv"),
            "candidate_fold_artifacts": candidate_fold_artifacts,
        },
    )
    holdout_reveal = _write_hashed_json(
        root / "holdout_reveal.json",
        {
            "contract_version": "finance-ml-v1",
            "run_id": run_id,
            "data_manifest_hash": data_manifest_hash,
            "model_manifest_hash": model_manifest["manifest_hash"],
            "predictions_hash": model_manifest["predictions_hash"],
            "holdout_start": HOLDOUT_START,
            "holdout_end_exclusive": HOLDOUT_END_EXCLUSIVE,
            "revealed_at": datetime.now(timezone.utc),
        },
    )
    final_record = ExperimentRecord(
        project="cross-sectional-equity-return-ranking",
        contract_version="finance-ml-v1",
        data_manifest_hash=data_manifest_hash,
        raw_response_hashes=raw_response_hashes,
        symbols=FROZEN_SYMBOLS,
        feature_group=winner.feature_group,
        feature_schema_hash=feature_schema_hash,
        model_name=winner.name,
        model_family=winner.family,
        model_params=winner.params,
        fold_ids=tuple(fold.fold_id for fold in folds),
        fold_ranges=fold_ranges,
        seed=RANDOM_STATE,
        runtime=runtime,
        code_commit=code_commit,
        execution_settings={
            "stage": "final_fit",
            "holdout_start": HOLDOUT_START,
            "holdout_end_exclusive": HOLDOUT_END_EXCLUSIVE,
            "embargo_start": EMBARGO_START,
        },
        metrics={"development_rows": float(len(development)), "holdout_rows": float(len(holdout))},
        output_artifact_hashes=(
            artifact_hash,
            sha256_file(predictions_path),
            sha256_file(holdout_path),
            sha256_file(oof_path),
            str(model_oof_index["manifest_hash"]),
            str(model_manifest["manifest_hash"]),
            str(holdout_reveal["manifest_hash"]),
        ),
        run_id=f"{run_id}-final",
    )
    write_experiment_record(run_dir / "experiment_records.jsonl", final_record)
    write_experiment_record(root / "experiment_records.jsonl", final_record)
    result = {
        "run_id": run_id,
        "run_directory": str(run_dir),
        "model_name": winner.name,
        "model_family": winner.family,
        "feature_group": winner.feature_group,
        "artifact": str(artifact),
        "artifact_hash": artifact_hash,
        "model_manifest_hash": model_manifest["manifest_hash"],
        "data_manifest_hash": data_manifest_hash,
        "holdout_reveal_hash": holdout_reveal["manifest_hash"],
        "dropped_features": list(fitted.dropped_feature_columns),
        "fold_count": len(folds),
        "holdout_rows": len(holdout),
        "experiment_rows": len(result_frame),
    }
    _write_hashed_json(run_dir / "train_summary.json", result)
    _write_hashed_json(root / "train_summary.json", result)
    _write_hashed_json(
        root / "active_run.json",
        {
            "run_id": run_id,
            "run_directory": str(run_dir),
            "model_manifest": str(run_dir / "model_manifest.json"),
        },
    )
    return result


def evaluate(args: argparse.Namespace, root: Path) -> dict[str, object]:
    del args
    active = _read_hashed_json(root / "active_run.json")
    run_dir = Path(str(active["run_directory"]))
    if (run_dir / "evaluation_manifest.json").exists():
        raise RuntimeError(f"holdout for run {active['run_id']} has already been evaluated")
    model_manifest = _read_hashed_json(Path(str(active["model_manifest"])))
    holdout_reveal = _read_hashed_json(root / "holdout_reveal.json")
    if (
        holdout_reveal["run_id"] != active["run_id"]
        or holdout_reveal["model_manifest_hash"] != model_manifest["manifest_hash"]
    ):
        raise RuntimeError("active run does not match the one-time holdout reveal registry")
    data_manifest_hash, raw_response_hashes, _ = _data_provenance(root)
    if model_manifest["data_manifest_hash"] != data_manifest_hash:
        raise RuntimeError("model and current data manifest hashes differ")
    path = Path(str(model_manifest["predictions"]))
    if sha256_file(path) != model_manifest["predictions_hash"]:
        raise RuntimeError("prediction artifact hash mismatch")
    oof_path = Path(str(model_manifest["development_oof_predictions"]))
    if sha256_file(oof_path) != model_manifest["development_oof_predictions_hash"]:
        raise RuntimeError("development OOF prediction artifact hash mismatch")
    oof = pd.read_csv(oof_path, parse_dates=["decision_at", "label_end"])
    if sha256_file(Path(str(model_manifest["artifact"]))) != model_manifest["artifact_hash"]:
        raise RuntimeError("model artifact hash mismatch")
    rows = pd.read_csv(path, parse_dates=["decision_at", "label_end"])
    _assert_complete_dates(rows, name="predictions")
    _assert_finite_columns(rows, ("prediction", "target"), name="predictions")
    result: dict[str, object] = prediction_metrics(rows, prediction="prediction", target="target")
    _, per_date = rank_ic(rows, prediction="prediction", target="target")
    valid_ic = pd.to_numeric(per_date["ic"], errors="coerce").dropna()
    if valid_ic.empty:
        raise RuntimeError("holdout has no estimable weekly rank IC values")
    rank_ic_std = float(valid_ic.std(ddof=1))
    bootstrap = block_bootstrap(valid_ic.to_numpy(), block_size=4, samples=2_000, seed=RANDOM_STATE)
    ci_lower, ci_upper = bootstrap["mean"].quantile([0.025, 0.975])
    result.update(
        {
            "rank_ic_dates": len(valid_ic),
            "rank_ic_ci_lower": float(ci_lower),
            "rank_ic_median": float(valid_ic.median()),
            "rank_ic_std": rank_ic_std,
            "rank_ic_information_ratio": float(valid_ic.mean() / rank_ic_std)
            if rank_ic_std > 0
            else None,
            "rank_ic_positive_fraction": float((valid_ic > 0).mean()),
            "rank_ic_ci_upper": float(ci_upper),
            "confidence_method": "moving-block bootstrap; 4 weeks; 2000 samples",
            "holdout_start": HOLDOUT_START,
            "holdout_end_exclusive": HOLDOUT_END_EXCLUSIVE,
            "revealed_at": datetime.now(timezone.utc),
        }
    )

    def predictive_slice(name: str, frame: pd.DataFrame) -> dict[str, object]:
        metrics = (
            prediction_metrics(frame, prediction="prediction", target="target")
            if not frame.empty
            else {}
        )
        _, diagnostics = (
            rank_ic(frame, prediction="prediction", target="target")
            if not frame.empty
            else (float("nan"), pd.DataFrame(columns=["ic"]))
        )
        values = pd.to_numeric(diagnostics["ic"], errors="coerce").dropna()
        cleaned = {
            key: (float(value) if np.isfinite(float(value)) else None)
            for key, value in metrics.items()
        }
        return {
            "slice": name,
            "rows": len(frame),
            "decision_dates": int(frame["decision_at"].nunique()) if not frame.empty else 0,
            "start": frame["decision_at"].min() if not frame.empty else None,
            "end": frame["decision_at"].max() if not frame.empty else None,
            **cleaned,
            "rank_ic_median": float(values.median()) if not values.empty else None,
            "rank_ic_std": float(values.std(ddof=1)) if len(values) > 1 else None,
            "rank_ic_positive_fraction": float((values > 0).mean()) if not values.empty else None,
        }

    complete_symbols = set(read_json(root / "complete_history_subset.json")["symbols"])
    robustness_rows = [
        predictive_slice(
            "development_2021_2022_oof", oof[oof["decision_at"].dt.year.between(2021, 2022)]
        ),
        predictive_slice(
            "development_2023_2024_oof", oof[oof["decision_at"].dt.year.between(2023, 2024)]
        ),
        predictive_slice("holdout_2025_full_basket", rows),
        predictive_slice("development_low_volatility_oof", oof[oof["volatility_regime"].eq("low")]),
        predictive_slice(
            "development_high_volatility_oof", oof[oof["volatility_regime"].eq("high")]
        ),
        predictive_slice("holdout_low_volatility", rows[rows["volatility_regime"].eq("low")]),
        predictive_slice("holdout_high_volatility", rows[rows["volatility_regime"].eq("high")]),
        predictive_slice(
            "holdout_complete_history_subset",
            rows[rows["symbol"].astype(str).str.upper().isin(complete_symbols)],
        ),
    ]
    result["robustness_slices"] = robustness_rows
    robustness_path = run_dir / "predictive_robustness.csv"
    _write_csv(robustness_path, pd.DataFrame(robustness_rows))
    per_date_path = run_dir / "holdout_rank_ic_by_date.csv"
    bootstrap_path = run_dir / "holdout_rank_ic_bootstrap.csv"
    summary_path = run_dir / "evaluation_summary.json"
    _write_csv(per_date_path, per_date)
    _write_csv(bootstrap_path, bootstrap)
    write_json(summary_path, result)
    write_json(root / "evaluation_summary.json", result)
    evaluation_manifest = _write_hashed_json(
        run_dir / "evaluation_manifest.json",
        {
            "contract_version": "finance-ml-v1",
            "run_id": active["run_id"],
            "data_manifest_hash": data_manifest_hash,
            "model_manifest_hash": model_manifest["manifest_hash"],
            "holdout_reveal_hash": holdout_reveal["manifest_hash"],
            "prediction_hash": model_manifest["predictions_hash"],
            "evaluation_summary_hash": sha256_file(summary_path),
            "rank_ic_by_date_hash": sha256_file(per_date_path),
            "bootstrap_hash": sha256_file(bootstrap_path),
            "predictive_robustness_hash": sha256_file(robustness_path),
            "holdout_start": HOLDOUT_START,
            "holdout_end_exclusive": HOLDOUT_END_EXCLUSIVE,
            "revealed_at": result["revealed_at"],
        },
    )
    folds = read_json(run_dir / "folds.json")["folds"]
    record = ExperimentRecord(
        project="cross-sectional-equity-return-ranking",
        contract_version="finance-ml-v1",
        data_manifest_hash=data_manifest_hash,
        raw_response_hashes=raw_response_hashes,
        symbols=FROZEN_SYMBOLS,
        feature_group=str(model_manifest["feature_group"]),
        feature_schema_hash=str(model_manifest["feature_schema_hash"]),
        model_name=str(model_manifest["model_name"]),
        model_family=str(model_manifest["model_family"]),
        model_params=dict(model_manifest["model_params"]),
        fold_ids=tuple(str(fold["fold_id"]) for fold in folds),
        fold_ranges=tuple(folds),
        seed=RANDOM_STATE,
        runtime=_runtime_versions(),
        code_commit=str(model_manifest["code_commit"]),
        execution_settings={
            "stage": "one-time final holdout",
            "bootstrap_block_weeks": 4,
            "bootstrap_samples": 2_000,
        },
        metrics={
            key: float(result[key])
            for key in (
                "rank_ic",
                "mae",
                "rmse",
                "top_tercile_excess",
                "rank_ic_median",
                "rank_ic_std",
                "rank_ic_information_ratio",
                "rank_ic_positive_fraction",
                "rank_ic_ci_lower",
                "rank_ic_ci_upper",
            )
            if result[key] is not None
        },
        output_artifact_hashes=(
            str(evaluation_manifest["manifest_hash"]),
            sha256_file(summary_path),
            sha256_file(per_date_path),
            sha256_file(bootstrap_path),
            sha256_file(robustness_path),
        ),
        run_id=f"{active['run_id']}-evaluation",
    )
    write_experiment_record(run_dir / "experiment_records.jsonl", record)
    write_experiment_record(root / "experiment_records.jsonl", record)
    return result


def _paper_metrics(replay: ReplayResult, config: PaperConfig) -> dict[str, Any]:
    events = pd.DataFrame(replay.events)
    marks = events[events["event_type"].eq("mark")].copy()
    if marks.empty:
        raise RuntimeError("paper replay emitted no NAV marks")
    net_weekly = weekly_returns(marks, initial_nav=config.initial_nav, nav="net_nav")
    gross_weekly = weekly_returns(marks, initial_nav=config.initial_nav, nav="gross_nav")
    metrics: dict[str, Any] = portfolio_summary(
        net_weekly, marks, gross_weekly=gross_weekly, initial_nav=config.initial_nav
    )
    trades = events[events["event_type"].isin(["fill", "exit"])].copy()
    final_nav = float(replay.summary["final_nav"])
    final_gross_nav = float(replay.summary["final_gross_nav"])
    metrics.update(
        {
            "initial_nav": config.initial_nav,
            "final_nav": final_nav,
            "final_gross_nav": final_gross_nav,
            "cost_drag": cost_drag(final_gross_nav, final_nav, config.initial_nav),
            "fee_total": float(replay.summary["fee_total"]),
            "slippage_total": float(replay.summary["slippage_total"]),
            "turnover": one_way_turnover(trades) if not trades.empty else 0.0,
            "number_of_rebalances": int(replay.summary["rebalances"]),
            "skip_counts": replay.summary["skip_counts"],
            "weekly_observations": len(net_weekly),
            "sample_start": pd.Timestamp(net_weekly["event_at"].min()).isoformat(),
            "sample_end": pd.Timestamp(net_weekly["event_at"].max()).isoformat(),
        }
    )
    return metrics


def _paper_weekly(replay: ReplayResult, config: PaperConfig) -> pd.DataFrame:
    events = pd.DataFrame(replay.events)
    marks = events[events["event_type"].eq("mark")].copy()
    net = weekly_returns(marks, initial_nav=config.initial_nav, nav="net_nav")[
        ["week", "event_at", "net_nav", "weekly_return"]
    ].rename(columns={"weekly_return": "net_weekly_return"})
    gross = weekly_returns(marks, initial_nav=config.initial_nav, nav="gross_nav")[
        ["week", "gross_nav", "weekly_return"]
    ].rename(columns={"weekly_return": "gross_weekly_return"})
    result = net.merge(gross, on="week", how="inner", validate="one_to_one")
    result["weekly_cost_drag"] = result["gross_weekly_return"] - result["net_weekly_return"]
    return result


def _top_tercile_excess(
    top: ReplayResult, equal_weight: ReplayResult, config: PaperConfig
) -> tuple[dict[str, float], pd.DataFrame]:
    top_weekly = _paper_weekly(top, config)[["week", "net_weekly_return"]].rename(
        columns={"net_weekly_return": "top_tercile_net_return"}
    )
    basket_weekly = _paper_weekly(equal_weight, config)[["week", "net_weekly_return"]].rename(
        columns={"net_weekly_return": "equal_weight_net_return"}
    )
    series = top_weekly.merge(basket_weekly, on="week", how="inner", validate="one_to_one")
    series["top_tercile_excess_return"] = (
        series["top_tercile_net_return"] - series["equal_weight_net_return"]
    )
    return {
        "top_tercile_excess_return_mean": float(series["top_tercile_excess_return"].mean()),
        "top_tercile_excess_return_median": float(series["top_tercile_excess_return"].median()),
    }, series


def paper_run(args: argparse.Namespace, root: Path) -> dict[str, object]:
    del args
    active = _read_hashed_json(root / "active_run.json")
    run_dir = Path(str(active["run_directory"]))
    if (run_dir / "paper_manifest.json").exists():
        raise RuntimeError(f"paper replay for run {active['run_id']} has already been emitted")
    model_manifest = _read_hashed_json(Path(str(active["model_manifest"])))
    evaluation_manifest = _read_hashed_json(run_dir / "evaluation_manifest.json")
    data_manifest_hash, raw_response_hashes, _ = _data_provenance(root)
    if (
        model_manifest["data_manifest_hash"] != data_manifest_hash
        or evaluation_manifest["data_manifest_hash"] != data_manifest_hash
    ):
        raise RuntimeError("paper prerequisites do not share the current data manifest")
    holdout_reveal = _read_hashed_json(root / "holdout_reveal.json")
    if holdout_reveal["manifest_hash"] != evaluation_manifest["holdout_reveal_hash"]:
        raise RuntimeError("paper evaluation does not match the one-time holdout reveal")
    if (
        sha256_file(run_dir / "evaluation_summary.json")
        != evaluation_manifest["evaluation_summary_hash"]
    ):
        raise RuntimeError("evaluation summary hash mismatch")
    model_path = Path(str(model_manifest["artifact"]))
    feature_path = Path(str(model_manifest["holdout_features"]))
    if sha256_file(feature_path) != model_manifest["holdout_features_hash"]:
        raise RuntimeError("holdout feature artifact hash mismatch")
    fitted = FittedModel.load(
        model_path,
        expected_hash=str(model_manifest["artifact_hash"]),
        expected_model_name=str(model_manifest["model_name"]),
        expected_feature_columns=tuple(model_manifest["feature_columns"]),
    )
    holdout = pd.read_csv(feature_path, parse_dates=["decision_at", "label_end"])
    scores = holdout[["decision_at", "symbol"]].copy()
    scores["score"] = fitted.predict(holdout)
    _assert_finite_columns(scores, ("score",), name="paper scores")
    bars = _read_bars(root / "label_fill_bars.csv")
    config = PaperConfig(code_commit=str(model_manifest["code_commit"]))

    def replay_with(
        replay_scores: pd.DataFrame,
        replay_bars: pd.DataFrame,
        replay_config: PaperConfig,
        suffix: str,
        artifact_hash: str = str(model_manifest["artifact_hash"]),
        schema_hash: str = str(model_manifest["feature_schema_hash"]),
        replay_symbols: tuple[str, ...] = FROZEN_SYMBOLS,
    ) -> ReplayResult:
        return PaperLedger(replay_config).replay(
            replay_scores,
            replay_bars,
            symbols=replay_symbols,
            run_id=f"{active['run_id']}-{suffix}",
            data_manifest_hash=data_manifest_hash,
            model_artifact_hash=artifact_hash,
            feature_schema_hash=schema_hash,
        )

    selected_replay = replay_with(scores, bars, config, "paper-selected")
    if selected_replay.failed:
        (run_dir / "paper_events_selected.jsonl").write_bytes(selected_replay.jsonl())
        raise RuntimeError("paper replay failed closed; inspect paper_events_selected.jsonl")
    selected_metrics = _paper_metrics(selected_replay, config)
    if "ret_20" not in holdout:
        raise RuntimeError("B1 paper benchmark requires ret_20")
    b1_scores = holdout[["decision_at", "symbol"]].copy()
    b1_scores["score"] = pd.to_numeric(holdout["ret_20"], errors="coerce")
    _assert_finite_columns(b1_scores, ("score",), name="B1 paper scores")
    b1_hash = sha256_json({"baseline": "B1", "signal": "twenty-session price momentum"})
    b1_schema_hash = sha256_json({"columns": ["ret_20"]})
    b1_replay = replay_with(b1_scores, bars, config, "paper-B1", b1_hash, b1_schema_hash)
    b1_metrics = _paper_metrics(b1_replay, config)
    b0_scores = holdout[["decision_at", "symbol"]].copy()
    b0_scores["score"] = 0.0
    b0_config = PaperConfig(
        top_n=len(FROZEN_SYMBOLS), code_commit=str(model_manifest["code_commit"])
    )
    b0_hash = sha256_json(
        {"baseline": "B0", "signal": "constant zero", "portfolio": "equal-weight basket"}
    )
    b0_replay = replay_with(
        b0_scores, bars, b0_config, "paper-B0", b0_hash, sha256_json({"columns": []})
    )
    b0_metrics = _paper_metrics(b0_replay, b0_config)
    selected_excess, holdout_excess = _top_tercile_excess(selected_replay, b0_replay, config)
    b1_excess, _ = _top_tercile_excess(b1_replay, b0_replay, config)
    selected_metrics.update(selected_excess)
    b1_metrics.update(b1_excess)
    b0_metrics.update(
        {"top_tercile_excess_return_mean": 0.0, "top_tercile_excess_return_median": 0.0}
    )
    zero_config = PaperConfig(
        fee_rate=0.0, slippage_rate=0.0, code_commit=str(model_manifest["code_commit"])
    )
    low_config = PaperConfig(
        fee_rate=0.00005, slippage_rate=0.00025, code_commit=str(model_manifest["code_commit"])
    )
    high_config = PaperConfig(
        fee_rate=0.0002, slippage_rate=0.0010, code_commit=str(model_manifest["code_commit"])
    )
    zero_replay = replay_with(scores, bars, zero_config, "paper-cost-0bps")
    low_replay = replay_with(scores, bars, low_config, "paper-cost-3bps")
    high_replay = replay_with(scores, bars, high_config, "paper-cost-12bps")
    cost_rows = [
        {"one_way_cost_bps": 0, **_paper_metrics(zero_replay, zero_config)},
        {"one_way_cost_bps": 3, **_paper_metrics(low_replay, low_config)},
        {"one_way_cost_bps": 6, **selected_metrics},
        {"one_way_cost_bps": 12, **_paper_metrics(high_replay, high_config)},
    ]
    first_decision = next(
        event for event in selected_replay.events if event["event_type"] == "decision"
    )
    stressed_bars = bars.copy()
    stressed_date = pd.Timestamp(first_decision["entry_at"]).date()
    stressed_symbol = str(first_decision["selected_symbols"][0])
    stressed_bars = stressed_bars[
        ~(
            stressed_bars["symbol"].astype(str).str.upper().eq(stressed_symbol)
            & stressed_bars["bar_end_at"].dt.date.eq(stressed_date)
        )
    ]
    missing_replay = replay_with(scores, stressed_bars, config, "paper-missing-bar")
    missing_skip_count = sum(
        event["event_type"] == "skip" and event.get("reason") == "entry_missing_bar"
        for event in missing_replay.events
    )
    if missing_skip_count != 1:
        raise RuntimeError("missing-bar sensitivity did not skip exactly one whole order batch")
    adjustment_rejected = False
    try:
        replay_with(
            scores, _read_bars(root / "feature_bars.csv"), config, "paper-invalid-adjustment"
        )
    except PaperError as exc:
        adjustment_rejected = "adjustment=all" in str(exc)
    if not adjustment_rejected:
        raise RuntimeError(
            "corporate-action sensitivity did not reject the split-adjusted execution stream"
        )
    complete_symbols = tuple(
        symbol
        for symbol in FROZEN_SYMBOLS
        if symbol in set(read_json(root / "complete_history_subset.json")["symbols"])
    )
    subset_replay: ReplayResult | None = None
    if len(complete_symbols) >= config.top_n:
        subset_scores = scores[
            scores["symbol"].astype(str).str.upper().isin(complete_symbols)
        ].copy()
        subset_replay = replay_with(
            subset_scores, bars, config, "paper-complete-history", replay_symbols=complete_symbols
        )
        subset_metrics: dict[str, Any] = {
            "status": "estimated",
            "symbol_count": len(complete_symbols),
            **_paper_metrics(subset_replay, config),
        }
    else:
        subset_metrics = {
            "status": "not_estimable",
            "symbol_count": len(complete_symbols),
            "reason": f"fewer than {config.top_n} eligible symbols",
        }
    model_oof_index = _read_hashed_json(Path(str(model_manifest["model_oof_index"])))
    if model_oof_index["manifest_hash"] != model_manifest["model_oof_index_hash"]:
        raise RuntimeError("model OOF index does not match its model manifest")
    training_results = pd.read_csv(run_dir / "experiment_results.csv")
    development_unavailable = {
        str(row["name"]): "; ".join(json.loads(str(row["errors"])))
        for row in training_results.to_dict("records")
        if json.loads(str(row["errors"]))
    }
    if "B1" in development_unavailable:
        raise RuntimeError(f"B1 development model failed: {development_unavailable['B1']}")
    development_scores: dict[str, pd.DataFrame] = {}
    complete_dates: dict[str, set[pd.Timestamp]] = {}
    for spec in registered_specs():
        artifact = model_oof_index["models"][spec.name]
        path = Path(str(artifact["path"]))
        if sha256_file(path) != artifact["hash"]:
            raise RuntimeError(f"development OOF prediction hash mismatch: {spec.name}")
        frame = pd.read_csv(path, parse_dates=["decision_at", "label_end"])
        valid_dates = {
            pd.Timestamp(decision_at)
            for decision_at, group in frame.groupby("decision_at", sort=True)
            if len(group) == len(FROZEN_SYMBOLS)
            and set(group["symbol"].astype(str).str.upper()) == set(FROZEN_SYMBOLS)
        }
        development_scores[spec.name] = frame
        complete_dates[spec.name] = valid_dates
    common_development_dates = complete_dates["B0"].intersection(complete_dates["B1"])
    if not common_development_dates:
        raise RuntimeError("B0 and B1 share no complete OOF decision dates")
    development_replays: dict[str, ReplayResult] = {}
    development_configs: dict[str, PaperConfig] = {}
    development_event_paths: dict[str, Path] = {}
    for spec in registered_specs():
        if spec.name != "B0" and spec.name in development_unavailable:
            continue
        if not common_development_dates.issubset(complete_dates[spec.name]):
            continue
        frame = development_scores[spec.name]
        paper_scores = frame[frame["decision_at"].isin(common_development_dates)][
            ["decision_at", "symbol", "prediction"]
        ].rename(columns={"prediction": "score"})
        paper_config = PaperConfig(
            top_n=len(FROZEN_SYMBOLS) if spec.name == "B0" else config.top_n,
            code_commit=str(model_manifest["code_commit"]),
        )
        artifact = model_oof_index["models"][spec.name]
        replay = replay_with(
            paper_scores,
            bars,
            paper_config,
            f"development-{spec.name}",
            str(artifact["hash"]),
            str(artifact["feature_schema_hash"]),
        )
        development_replays[spec.name] = replay
        development_configs[spec.name] = paper_config
        event_path = run_dir / "development_paper_events" / f"{spec.name}.jsonl"
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_bytes(replay.jsonl())
        development_event_paths[spec.name] = event_path
    if "B0" not in development_replays:
        raise RuntimeError("B0 development portfolio is not estimable")
    development_b0 = development_replays["B0"]
    development_rows: list[dict[str, Any]] = []
    for spec in registered_specs():
        if spec.name not in development_replays:
            development_rows.append(
                {
                    "model": spec.name,
                    "family": spec.family,
                    "feature_group": spec.feature_group,
                    "status": "not_estimable",
                    "decision_dates": len(complete_dates[spec.name]),
                    "reason": development_unavailable.get(
                        spec.name, "missing one or more complete baseline OOF decision dates"
                    ),
                }
            )
            continue
        metrics = _paper_metrics(development_replays[spec.name], development_configs[spec.name])
        if spec.name == "B0":
            metrics.update(
                {"top_tercile_excess_return_mean": 0.0, "top_tercile_excess_return_median": 0.0}
            )
        else:
            excess, _ = _top_tercile_excess(development_replays[spec.name], development_b0, config)
            metrics.update(excess)
        development_rows.append(
            {
                "model": spec.name,
                "family": spec.family,
                "feature_group": spec.feature_group,
                "status": "estimated",
                "decision_dates": len(common_development_dates),
                **metrics,
            }
        )
    development_comparison_path = run_dir / "development_portfolio_comparison.csv"
    _write_csv(
        development_comparison_path,
        pd.DataFrame(
            [
                {key: value for key, value in row.items() if key != "skip_counts"}
                for row in development_rows
            ]
        ),
    )
    replays: dict[str, ReplayResult] = {
        "selected": selected_replay,
        "B0": b0_replay,
        "B1": b1_replay,
        "cost_0bps": zero_replay,
        "cost_3bps": low_replay,
        "cost_12bps": high_replay,
        "missing_bar": missing_replay,
    }
    if subset_replay is not None:
        replays["complete_history"] = subset_replay
    event_paths = {name: run_dir / f"paper_events_{name}.jsonl" for name in replays}
    for name, replay in replays.items():
        event_paths[name].write_bytes(replay.jsonl())
    weekly_path = run_dir / "paper_weekly_returns.csv"
    excess_path = run_dir / "paper_top_tercile_excess.csv"
    _write_csv(weekly_path, _paper_weekly(selected_replay, config))
    _write_csv(excess_path, holdout_excess)
    comparison_path = run_dir / "paper_model_comparison.csv"
    cost_path = run_dir / "paper_cost_sensitivity.csv"
    skip_path = run_dir / "paper_skip_counts.csv"
    comparable_keys = [
        key
        for key, value in selected_metrics.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    comparison_rows = [
        {
            "model": str(model_manifest["model_name"]),
            **{key: selected_metrics[key] for key in comparable_keys},
        }
    ]
    if model_manifest["model_name"] != "B1":
        comparison_rows.append({"model": "B1", **{key: b1_metrics[key] for key in comparable_keys}})
    comparison_rows.append(
        {"model": "B0_equal_weight", **{key: b0_metrics[key] for key in comparable_keys}}
    )
    _write_csv(comparison_path, pd.DataFrame(comparison_rows))
    _write_csv(
        cost_path,
        pd.DataFrame(
            [
                {key: value for key, value in row.items() if key != "skip_counts"}
                for row in cost_rows
            ]
        ),
    )
    _write_csv(
        skip_path,
        pd.DataFrame(
            [
                {"reason": reason, "count": count}
                for reason, count in selected_metrics["skip_counts"].items()
            ],
            columns=["reason", "count"],
        ),
    )
    evaluation = read_json(run_dir / "evaluation_summary.json")
    summary: dict[str, object] = {
        "contract_version": "finance-ml-v1",
        "run_id": active["run_id"],
        "data_manifest_hash": data_manifest_hash,
        "model_manifest_hash": model_manifest["manifest_hash"],
        "evaluation_manifest_hash": evaluation_manifest["manifest_hash"],
        "selected_model": model_manifest["model_name"],
        "predictive": evaluation,
        "portfolio": selected_metrics,
        "B1_portfolio": b1_metrics,
        "B0_equal_weight_portfolio": b0_metrics,
        "complete_history_portfolio": subset_metrics,
        "cost_sensitivity": cost_rows,
        "missing_data_sensitivity": {
            "removed_symbol": stressed_symbol,
            "removed_session": stressed_date,
            "whole_batch_skip_count": missing_skip_count,
        },
        "development_portfolio_comparison": development_rows,
        "corporate_action_sensitivity": {
            "split_adjusted_execution_stream_rejected": adjustment_rejected
        },
        "paper_only": True,
        "live_trading": False,
    }
    summary_path = run_dir / "paper_summary.json"
    write_json(summary_path, summary)
    write_json(root / "paper_summary.json", summary)
    paper_manifest = _write_hashed_json(
        run_dir / "paper_manifest.json",
        {
            "contract_version": "finance-ml-v1",
            "run_id": active["run_id"],
            "data_manifest_hash": data_manifest_hash,
            "model_manifest_hash": model_manifest["manifest_hash"],
            "evaluation_manifest_hash": evaluation_manifest["manifest_hash"],
            "summary_hash": sha256_file(summary_path),
            "event_log_hashes": {name: sha256_file(path) for name, path in event_paths.items()},
            "development_event_log_hashes": {
                name: {"path": str(path), "hash": sha256_file(path)}
                for name, path in development_event_paths.items()
            },
            "comparison_hash": sha256_file(comparison_path),
            "cost_sensitivity_hash": sha256_file(cost_path),
            "skip_count_hash": sha256_file(skip_path),
            "development_comparison_hash": sha256_file(development_comparison_path),
            "weekly_returns_hash": sha256_file(weekly_path),
            "top_tercile_excess_hash": sha256_file(excess_path),
        },
    )
    folds = read_json(run_dir / "folds.json")["folds"]
    numeric_metrics = {
        key: float(value)
        for key, value in selected_metrics.items()
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
        and np.isfinite(float(value))
    }
    record = ExperimentRecord(
        project="cross-sectional-equity-return-ranking",
        contract_version="finance-ml-v1",
        data_manifest_hash=data_manifest_hash,
        raw_response_hashes=raw_response_hashes,
        symbols=FROZEN_SYMBOLS,
        feature_group=str(model_manifest["feature_group"]),
        feature_schema_hash=str(model_manifest["feature_schema_hash"]),
        model_name=str(model_manifest["model_name"]),
        model_family=str(model_manifest["model_family"]),
        model_params=dict(model_manifest["model_params"]),
        fold_ids=tuple(str(fold["fold_id"]) for fold in folds),
        fold_ranges=tuple(folds),
        seed=RANDOM_STATE,
        runtime=_runtime_versions(),
        code_commit=str(model_manifest["code_commit"]),
        execution_settings={
            "stage": "paper replay",
            "fee_rate": config.fee_rate,
            "slippage_rate": config.slippage_rate,
            "top_n": config.top_n,
        },
        metrics=numeric_metrics,
        output_artifact_hashes=(
            str(paper_manifest["manifest_hash"]),
            sha256_file(summary_path),
            sha256_file(comparison_path),
            sha256_file(development_comparison_path),
            sha256_file(weekly_path),
            sha256_file(excess_path),
            *(sha256_file(path) for path in event_paths.values()),
        ),
        run_id=f"{active['run_id']}-paper",
    )
    write_experiment_record(run_dir / "experiment_records.jsonl", record)
    write_experiment_record(root / "experiment_records.jsonl", record)
    return {
        "run_id": active["run_id"],
        "selected_model": model_manifest["model_name"],
        "paper_summary": str(summary_path),
        "paper_manifest_hash": paper_manifest["manifest_hash"],
        "net_return": selected_metrics["cumulative_return"],
        "top_tercile_excess_return_mean": selected_metrics["top_tercile_excess_return_mean"],
    }


def report(args: argparse.Namespace, root: Path) -> dict[str, object]:
    del args
    active = _read_hashed_json(root / "active_run.json")
    run_dir = Path(str(active["run_directory"]))
    if (run_dir / "report_manifest.json").exists():
        raise RuntimeError(f"report for run {active['run_id']} has already been emitted")
    data_manifest_hash, _, data_manifests = _data_provenance(root)
    model_manifest = _read_hashed_json(Path(str(active["model_manifest"])))
    evaluation_manifest = _read_hashed_json(run_dir / "evaluation_manifest.json")
    paper_manifest = _read_hashed_json(run_dir / "paper_manifest.json")
    model_oof_index = _read_hashed_json(Path(str(model_manifest["model_oof_index"])))
    if model_oof_index["manifest_hash"] != model_manifest["model_oof_index_hash"]:
        raise RuntimeError("model OOF index hash mismatch")
    if {
        model_manifest["data_manifest_hash"],
        evaluation_manifest["data_manifest_hash"],
        paper_manifest["data_manifest_hash"],
    } != {data_manifest_hash}:
        raise RuntimeError("report prerequisites do not share one data manifest")
    if {
        model_manifest["run_id"],
        evaluation_manifest["run_id"],
        paper_manifest["run_id"],
    } != {active["run_id"]}:
        raise RuntimeError("report prerequisites do not share one run")
    if (
        evaluation_manifest["model_manifest_hash"] != model_manifest["manifest_hash"]
        or paper_manifest["model_manifest_hash"] != model_manifest["manifest_hash"]
        or paper_manifest["evaluation_manifest_hash"] != evaluation_manifest["manifest_hash"]
    ):
        raise RuntimeError("report prerequisite manifest chain is inconsistent")
    model_artifacts = {
        model_manifest["artifact"]: model_manifest["artifact_hash"],
        model_manifest["predictions"]: model_manifest["predictions_hash"],
        model_manifest["holdout_features"]: model_manifest["holdout_features_hash"],
        model_manifest["development_oof_predictions"]: model_manifest[
            "development_oof_predictions_hash"
        ],
    }
    for path, digest in model_artifacts.items():
        if sha256_file(Path(str(path))) != digest:
            raise RuntimeError(f"model artifact hash mismatch: {path}")
    model_support_artifacts = {
        run_dir / "folds.json": model_manifest["folds_hash"],
        run_dir / "experiment_results.csv": model_manifest["experiment_results_hash"],
        run_dir / "fold_metrics.csv": model_manifest["fold_metrics_hash"],
    }
    for path, digest in model_support_artifacts.items():
        if sha256_file(path) != digest:
            raise RuntimeError(f"model support artifact hash mismatch: {path.name}")
    for name, artifact in model_manifest["candidate_fold_artifacts"].items():
        if sha256_file(Path(str(artifact["path"]))) != artifact["hash"]:
            raise RuntimeError(f"candidate fold artifact hash mismatch: {name}")
    for name, artifact in model_oof_index["models"].items():
        if sha256_file(Path(str(artifact["path"]))) != artifact["hash"]:
            raise RuntimeError(f"model OOF artifact hash mismatch: {name}")
    evaluation_artifacts = {
        "holdout_rank_ic_by_date.csv": evaluation_manifest["rank_ic_by_date_hash"],
        "holdout_rank_ic_bootstrap.csv": evaluation_manifest["bootstrap_hash"],
        "predictive_robustness.csv": evaluation_manifest["predictive_robustness_hash"],
    }
    for filename, digest in evaluation_artifacts.items():
        if sha256_file(run_dir / filename) != digest:
            raise RuntimeError(f"evaluation artifact hash mismatch: {filename}")
    paper_artifacts = {
        "paper_model_comparison.csv": paper_manifest["comparison_hash"],
        "paper_cost_sensitivity.csv": paper_manifest["cost_sensitivity_hash"],
        "paper_skip_counts.csv": paper_manifest["skip_count_hash"],
        "paper_weekly_returns.csv": paper_manifest["weekly_returns_hash"],
        "paper_top_tercile_excess.csv": paper_manifest["top_tercile_excess_hash"],
    }
    for filename, digest in paper_artifacts.items():
        if sha256_file(run_dir / filename) != digest:
            raise RuntimeError(f"paper artifact hash mismatch: {filename}")
    if (
        sha256_file(run_dir / "evaluation_summary.json")
        != evaluation_manifest["evaluation_summary_hash"]
    ):
        raise RuntimeError("evaluation summary hash mismatch")
    paper_summary_path = run_dir / "paper_summary.json"
    if sha256_file(paper_summary_path) != paper_manifest["summary_hash"]:
        raise RuntimeError("paper summary hash mismatch")
    for name, digest in paper_manifest["event_log_hashes"].items():
        if sha256_file(run_dir / f"paper_events_{name}.jsonl") != digest:
            raise RuntimeError(f"paper event log hash mismatch: {name}")
    for name, artifact in paper_manifest["development_event_log_hashes"].items():
        if sha256_file(Path(str(artifact["path"]))) != artifact["hash"]:
            raise RuntimeError(f"development paper event log hash mismatch: {name}")
    if (
        sha256_file(run_dir / "development_portfolio_comparison.csv")
        != paper_manifest["development_comparison_hash"]
    ):
        raise RuntimeError("development portfolio comparison hash mismatch")
    data_summary = read_json(root / "data_build_summary.json")
    train_summary = _read_hashed_json(run_dir / "train_summary.json")
    if (
        train_summary["model_manifest_hash"] != model_manifest["manifest_hash"]
        or train_summary["data_manifest_hash"] != data_manifest_hash
    ):
        raise RuntimeError("train summary does not match report prerequisites")
    evaluation = read_json(run_dir / "evaluation_summary.json")
    paper = read_json(paper_summary_path)
    input_diagnostics = read_json(root / "input_diagnostics.json")
    complete_history = read_json(root / "complete_history_subset.json")
    experiments = pd.read_csv(run_dir / "experiment_results.csv")
    fold_metrics = pd.read_csv(run_dir / "fold_metrics.csv")
    rejected: list[dict[str, object]] = []
    for row in experiments.to_dict("records"):
        if row["name"] == train_summary["model_name"]:
            continue
        errors = json.loads(row["errors"]) if isinstance(row["errors"], str) else []
        rejected.append(
            {
                "model": row["name"],
                "reason": errors
                or "did not beat B1 by at least 0.010 mean development IC on at least 60% of folds under the lowest-complexity tie-break",
                "mean_development_ic": row["mean_development_ic"],
                "nonnegative_fold_fraction": row["nonnegative_fold_fraction"],
            }
        )
    artifact_paths = [
        root / "feature_bars.csv",
        root / "label_fill_bars.csv",
        root / "sec_facts.csv",
        root / "feature_manifest.json",
        root / "label_manifest.json",
        root / "sec_manifest.json",
        root / "data_build_summary.json",
        root / "data_artifact_manifest.json",
        root / "complete_history_subset.json",
        root / "input_diagnostics.json",
        root / "development_rows.csv",
        root / "label_skips.csv",
        root / "holdout_reveal.json",
        root / "experiment_records.jsonl",
        root / "active_run.json",
        run_dir / "folds.json",
        run_dir / "experiment_results.csv",
        run_dir / "fold_metrics.csv",
        *(
            Path(str(artifact["path"]))
            for artifact in model_manifest["candidate_fold_artifacts"].values()
        ),
        run_dir / "experiment_records.jsonl",
        Path(str(model_manifest["artifact"])),
        Path(str(model_manifest["predictions"])),
        Path(str(model_manifest["holdout_features"])),
        Path(str(model_manifest["development_oof_predictions"])),
        Path(str(model_manifest["model_oof_index"])),
        *(Path(str(artifact["path"])) for artifact in model_oof_index["models"].values()),
        run_dir / "model_manifest.json",
        run_dir / "train_summary.json",
        run_dir / "evaluation_summary.json",
        run_dir / "evaluation_manifest.json",
        run_dir / "holdout_rank_ic_by_date.csv",
        run_dir / "holdout_rank_ic_bootstrap.csv",
        run_dir / "predictive_robustness.csv",
        run_dir / "paper_summary.json",
        run_dir / "paper_manifest.json",
        run_dir / "paper_model_comparison.csv",
        run_dir / "paper_cost_sensitivity.csv",
        run_dir / "paper_skip_counts.csv",
        run_dir / "development_portfolio_comparison.csv",
        run_dir / "paper_weekly_returns.csv",
        run_dir / "paper_top_tercile_excess.csv",
        *(run_dir / f"paper_events_{name}.jsonl" for name in paper_manifest["event_log_hashes"]),
        *(
            Path(str(artifact["path"]))
            for artifact in paper_manifest["development_event_log_hashes"].values()
        ),
    ]
    artifact_index = {str(path.relative_to(root)): sha256_file(path) for path in artifact_paths}
    generated_at = datetime.now(timezone.utc)
    report_data: dict[str, object] = {
        "generated_at": generated_at,
        "run_id": active["run_id"],
        "contract_version": "finance-ml-v1",
        "source_mode": data_summary["source_mode"],
        "data_manifest_hash": data_manifest_hash,
        "data_manifests": data_manifests,
        "data_build": data_summary,
        "complete_history_subset": complete_history,
        "input_diagnostics": input_diagnostics,
        "source_ledger": [
            {
                "source": "Alpaca Customer Agreement §23",
                "purpose": "market-data use and redistribution boundary",
                "url": "https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf",
                "obligation": "keep raw and normalized licensed bars outside version control; the default artifact directory is ignored",
            },
            {
                "source": "Alpaca Market Data",
                "purpose": "split-adjusted features and all-adjusted label/fill proxies",
                "url": "https://docs.alpaca.markets/reference/stockbars",
                "obligation": "credentials and use remain subject to Alpaca terms; do not redistribute raw licensed data",
            },
            {
                "source": "SEC EDGAR CompanyFacts",
                "purpose": "accepted-time fundamentals",
                "url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
                "obligation": "descriptive User-Agent, fair-access rate limits, attribution; no SEC endorsement",
            },
            {
                "source": "exchange_calendars XNYS",
                "purpose": "scheduled opens, closes, holidays, and early closes",
                "url": "https://github.com/gerrymanoim/exchange_calendars",
                "obligation": "pinned package version; calendar supplies time ordering, not prices",
            },
            {
                "source": "HKUDS/Vibe-Trading",
                "purpose": "architecture reference only; no code or data copied",
                "url": "https://github.com/HKUDS/Vibe-Trading/blob/main/LICENSE",
                "obligation": "root is MIT and factor families add obligations; preserve notices if reuse is ever approved",
            },
            {
                "source": "Packt ML4T Second Edition companion",
                "purpose": "learning reference only; no code or data copied",
                "url": "https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition",
                "obligation": "no repository LICENSE was verified, so do not copy or redistribute its code",
            },
        ],
        "temporal_contract": {
            "development": "2021-01-01 through decisions before 2024-12-27, with every label ending before 2025-01-01",
            "embargo_start": EMBARGO_START,
            "holdout_start": HOLDOUT_START,
            "holdout_end_exclusive": HOLDOUT_END_EXCLUSIVE,
            "fold_count": train_summary["fold_count"],
            "minimum_training_weeks": TemporalSpec().minimum_training_weeks,
            "validation_weeks": TemporalSpec().validation_weeks,
            "embargo_weeks": TemporalSpec().embargo_weeks,
        },
        "preprocessing": {
            "imputation": "training-fold medians only",
            "missingness": "drop a feature within a fold when its training-fold missing fraction exceeds 30%; add paired missing indicators",
            "scaling": "inside each fitted ElasticNet pipeline only",
            "dropped_final_features": train_summary["dropped_features"],
        },
        "model_comparison": experiments.to_dict("records"),
        "fold_metrics": fold_metrics.to_dict("records"),
        "selected_model": train_summary,
        "rejected_models": rejected,
        "predictive_evidence": evaluation,
        "paper_evidence": paper,
        "limitations": [
            "The frozen 30-symbol universe is selected from current large liquid US equities and does not reconstruct point-in-time index membership; survivorship and selection bias remain.",
            "The final holdout is one calendar year and was revealed once for this immutable run; it does not establish regime-invariant performance.",
            "Adjusted daily-bar opens and closes are execution proxies, not broker fills, and the simulator does not model intraday market impact.",
            "SEC CompanyFacts tags and issuer reporting practices vary; missingness indicators and fold-local feature drops expose but do not eliminate that measurement risk.",
            "This is paper trading only: no capital, broker routing, live trading, investment advice, guaranteed return, or claim about Looloo proprietary systems.",
        ],
        "artifact_hashes": artifact_index,
    }
    report_path = run_dir / "report.json"
    write_json(report_path, report_data)
    write_json(root / "report.json", report_data)

    def fmt(value: Any) -> str:
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return f"{value:.6f}" if np.isfinite(float(value)) else "N/A"
        return str(value)

    def outcome(row: dict[str, Any]) -> str:
        if row["name"] == train_summary["model_name"]:
            return "selected"
        if row["name"] == "B0":
            return "no-signal comparator"
        errors = json.loads(row["errors"]) if isinstance(row.get("errors"), str) else []
        return (
            f"failed: {errors[0]}".replace("|", "/")
            if errors
            else "rejected by frozen promotion rule"
        )

    selected = paper["portfolio"]
    baseline = paper["B1_portfolio"]
    no_signal = paper["B0_equal_weight_portfolio"]
    development_portfolios = paper["development_portfolio_comparison"]
    holdout_portfolios = [(str(model_manifest["model_name"]), selected)]
    if model_manifest["model_name"] != "B1":
        holdout_portfolios.append(("B1 twenty-session momentum", baseline))
    holdout_portfolios.append(("B0 equal-weight basket", no_signal))
    warning = (
        "\n> **SYNTHETIC FIXTURE RUN — pipeline validation only; not hiring or investment evidence.**\n"
        if data_summary["source_mode"] == "synthetic"
        else ""
    )
    lines = [
        "# Cross-sectional equity return-ranking evidence report",
        "",
        f"Run `{active['run_id']}` · contract `finance-ml-v1` · generated `{generated_at.isoformat()}`",
        warning,
        "## Reviewer path",
        "",
        "1. Read the result and limitation tables below.",
        "2. Inspect `experiment_results.csv` and `fold_metrics.csv` for every registered model and fold.",
        "3. Verify `model_manifest.json`, `evaluation_manifest.json`, and `paper_manifest.json` hashes.",
        "4. Trace any paper number to the immutable JSONL event logs; each event carries the run, data, model, feature-schema, contract, and code identifiers.",
        "",
        "## Reproduce",
        "",
        "Use a fresh artifact directory: `uv sync --locked --extra dev && uv run pytest -q && GIT_COMMIT=<commit> uv run looloo-finance-ml --artifacts artifacts all`.",
        "",
        "For licensed source data, set `ALPACA_API_KEY`, `ALPACA_API_SECRET`, and a descriptive `SEC_USER_AGENT`, then add `--live` after `all`. Raw licensed data remains outside version control.",
        "",
        "## Recruiter card and ownership",
        "",
        "**Problem:** rank the next five-session excess returns of a frozen 30-stock US equity panel without using future prices, late SEC filings, or holdout feedback.",
        "",
        "**Candidate-owned:** data contracts and manifests, point-in-time feature/label joins, model ladder, temporal validation, promotion rule, deterministic costed ledger, fail-closed tests, diagnosis, and evidence packaging.",
        "",
        "**Reused/reference-only:** Alpaca and SEC data services; Python/pandas/NumPy/scikit-learn; `exchange_calendars`; Vibe-Trading and Packt ML4T as learning references only. No reused repository is represented as candidate-authored evidence.",
        "",
        "**Boundary:** this artifact demonstrates programming, ML, data, experimentation, diagnosis, and production discipline. It does not replace a degree or professional tenure and makes no profitability claim.",
        "",
        "## Decision and headline evidence",
        "",
        f"- Selected model: **{model_manifest['model_name']}** ({model_manifest['model_family']}, `{model_manifest['feature_group']}`).",
        f"- Holdout rank IC: **{fmt(evaluation['rank_ic'])}**, 95% moving-block bootstrap CI **[{fmt(evaluation['rank_ic_ci_lower'])}, {fmt(evaluation['rank_ic_ci_upper'])}]** across {evaluation['rank_ic_dates']} weekly dates.",
        f"- Net cumulative paper return: **{fmt(selected['cumulative_return'])}**; gross: **{fmt(selected['gross_cumulative_return'])}**; cost drag: **{fmt(selected['cost_drag'])}**.",
        f"- Mean weekly top-tercile excess return over the costed equal-weight basket: **{fmt(selected['top_tercile_excess_return_mean'])}**.",
        f"- Paper sample: **{selected['sample_start']}** through **{selected['sample_end']}**; {selected['weekly_observations']} calendar-week observations.",
        "- Positive returns were not required for promotion. Failed candidates and unfavorable slices remain in the evidence tables.",
        "",
        "## Development portfolio comparison (out-of-fold predictions only)",
        "",
        "| Model | Status | Family | Features | Net return | Mean top-tercile excess | Cost drag | Max drawdown |",
        "|---|---|---|---|---:|---:|---:|---:|",
        *[
            f"| {row['model']} | {row['status']} | {row['family']} | {row['feature_group']} | {fmt(row.get('cumulative_return'))} | {fmt(row.get('top_tercile_excess_return_mean'))} | {fmt(row.get('cost_drag'))} | {fmt(row.get('maximum_drawdown'))} |"
            for row in development_portfolios
        ],
        "",
        "Every estimated row uses the same common OOF decision dates, split-adjusted feature/label history, all-adjusted replay bars, 6 bps one-way cost, and deterministic event ledger. B0 holds the equal-weight basket; every other estimated row holds its top tercile. Failed candidates remain explicitly not estimable.",
        "",
        "## Final-holdout paper portfolio comparison",
        "",
        "| Model | Net return | Gross return | Mean top-tercile excess | Volatility | Sharpe | Sortino | Max drawdown | Hit rate | Turnover | Avg exposure | Rebalances |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {name} | {fmt(metrics['cumulative_return'])} | {fmt(metrics['gross_cumulative_return'])} | {fmt(metrics['top_tercile_excess_return_mean'])} | {fmt(metrics['annualized_volatility'])} | {fmt(metrics['sharpe'])} | {fmt(metrics['sortino'])} | {fmt(metrics['maximum_drawdown'])} | {fmt(metrics['weekly_hit_rate'])} | {fmt(metrics['turnover'])} | {fmt(metrics['average_exposure'])} | {metrics['number_of_rebalances']} |"
            for name, metrics in holdout_portfolios
        ],
        "",
        "## Predictive evidence",
        "",
        "| Mean rank IC | Median | Std. dev. | IC information ratio | Positive fraction | 95% CI | MAE | RMSE | Mean top-tercile target excess |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {fmt(evaluation['rank_ic'])} | {fmt(evaluation['rank_ic_median'])} | {fmt(evaluation['rank_ic_std'])} | {fmt(evaluation['rank_ic_information_ratio'])} | {fmt(evaluation['rank_ic_positive_fraction'])} | [{fmt(evaluation['rank_ic_ci_lower'])}, {fmt(evaluation['rank_ic_ci_upper'])}] | {fmt(evaluation['mae'])} | {fmt(evaluation['rmse'])} | {fmt(evaluation['top_tercile_excess'])} |",
        "",
        "## Cost and failure sensitivities",
        "",
        "| One-way cost | Net return | Cost drag | Final NAV |",
        "|---:|---:|---:|---:|",
        *[
            f"| {row['one_way_cost_bps']} bps | {fmt(row['cumulative_return'])} | {fmt(row['cost_drag'])} | {fmt(row['final_nav'])} |"
            for row in paper["cost_sensitivity"]
        ],
        "",
        f"- Missing-bar stress removed `{paper['missing_data_sensitivity']['removed_symbol']}` on `{paper['missing_data_sensitivity']['removed_session']}` and produced {paper['missing_data_sensitivity']['whole_batch_skip_count']} whole-batch skip.",
        f"- Split-adjusted execution stream rejected: `{paper['corporate_action_sensitivity']['split_adjusted_execution_stream_rejected']}`.",
        f"- Normal-run skip counts: `{json.dumps(selected['skip_counts'], sort_keys=True)}`.",
        "",
        f"- Complete-history subset paper status: `{paper['complete_history_portfolio']['status']}`; net return: {fmt(paper['complete_history_portfolio'].get('cumulative_return'))}.",
        "",
        "## Predeclared robustness slices",
        "",
        "| Slice | Rows | Dates | Rank IC | Median IC | Positive fraction | MAE | Top-tercile excess |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {row['slice']} | {row['rows']} | {row['decision_dates']} | {fmt(row.get('rank_ic'))} | {fmt(row.get('rank_ic_median'))} | {fmt(row.get('rank_ic_positive_fraction'))} | {fmt(row.get('mae'))} | {fmt(row.get('top_tercile_excess'))} |"
            for row in evaluation["robustness_slices"]
        ],
        "",
        "## Data and leakage controls",
        "",
        f"- Data manifest hash: `{data_manifest_hash}`; source mode: **{data_summary['source_mode']}**.",
        f"- Frozen universe: {len(FROZEN_SYMBOLS)} symbols; complete-history sensitivity subset: {len(complete_history['symbols'])}.",
        "- Decision is the last valid XNYS close in each calendar week; entry is the next XNYS open; label and exit are the close five sessions after decision.",
        "- SEC facts become eligible only at `accepted_at`; amendments replace originals only after their own acceptance time.",
        "- Every development fold purges labels crossing validation and applies a one-week embargo. The 2025 holdout is excluded from fitting and model promotion.",
        "- Imputation, missing-feature drops, indicators, and scaling are fitted only on each training fold.",
        "",
        "### Source and obligation ledger",
        "",
        *[
            f"- [{item['source']}]({item['url']}): {item['purpose']}. Obligation: {item['obligation']}."
            for item in report_data["source_ledger"]
        ],
        "",
        "## Model ladder and negative results",
        "",
        "| Model | Mean development IC | Nonnegative vs B1 | Outcome |",
        "|---|---:|---:|---|",
        *[
            f"| {row['name']} | {fmt(row['mean_development_ic'])} | {fmt(row['nonnegative_fold_fraction'])} | {outcome(row)} |"
            for row in experiments.to_dict("records")
        ],
        "",
        "## Failure-diagnosis status",
        "",
        "- No historical diagnosis is included: no primary artifact establishes the claimed prior failure. The rank-IC missing-value regression is defended by a focused test, not presented as a run observation.",
        "",
        "## Formula appendix",
        "",
        "- Weekly rank IC: Spearman correlation of prediction and realized five-session excess-return ranks within each eligible decision date; headline is the mean across dates.",
        "- Net weekly return: `NAV_w / NAV_{w-1} - 1`, with the initial week divided by USD 100,000.",
        "- Cumulative return: `final_NAV / 100000 - 1`; cost drag: `(final_gross_NAV - final_net_NAV) / 100000`.",
        "- Annualized volatility: sample standard deviation of weekly returns × `sqrt(52)`; Sharpe: weekly mean / sample standard deviation × `sqrt(52)` at zero risk-free rate.",
        "- Sortino: weekly mean / root-mean-square downside return × `sqrt(52)`; maximum drawdown: minimum `NAV / running_peak - 1` including initial NAV.",
        "- One-way turnover: sum of absolute trade notional divided by NAV immediately before each fill event.",
        "- Cost model: 1 bp fee + 5 bps slippage per one-way fill; sensitivity reruns use 0, 3, 6, and 12 bps. The 0-bps row is a sensitivity, not the evidence headline.",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report_data["limitations"]],
        "",
        "## Artifact index",
        "",
        *[f"- `{name}` — `{digest}`" for name, digest in sorted(artifact_index.items())],
    ]
    markdown_path = run_dir / "evidence_report.md"
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report_manifest = _write_hashed_json(
        run_dir / "report_manifest.json",
        {
            "contract_version": "finance-ml-v1",
            "run_id": active["run_id"],
            "data_manifest_hash": data_manifest_hash,
            "model_manifest_hash": model_manifest["manifest_hash"],
            "evaluation_manifest_hash": evaluation_manifest["manifest_hash"],
            "paper_manifest_hash": paper_manifest["manifest_hash"],
            "report_hash": sha256_file(report_path),
            "evidence_report_hash": sha256_file(markdown_path),
        },
    )
    result = {
        "run_id": active["run_id"],
        "report": str(report_path),
        "evidence_report": str(markdown_path),
        "report_manifest_hash": report_manifest["manifest_hash"],
        "artifact_count": len(artifact_index),
    }
    write_json(root / "report_summary.json", result)
    return result


def webull_compare(args: argparse.Namespace, root: Path) -> dict[str, object]:
    if args.fixture:
        payload = {
            "bars": [
                {
                    "timestamp": "2021-01-04T21:00:00+00:00",
                    "open": 1,
                    "high": 2,
                    "low": 1,
                    "close": 1.5,
                    "volume": 100,
                    "adjustment": "forward_adjusted",
                }
            ]
        }
        comparison = normalize_webull_bars(
            payload, symbol=args.symbol, raw_body=json.dumps(payload).encode(), requested_count=1
        )
    else:
        comparison = WebullClient.from_config().historical_bars(args.symbol)
    _write_csv(root / f"webull_{args.symbol.upper()}.csv", comparison.frame)
    result = {
        "symbol": args.symbol.upper(),
        "rows": len(comparison.frame),
        "raw_response_hash": comparison.raw_response_hash,
        "diagnostics": list(comparison.diagnostics),
        "canonical_fallback": False,
    }
    write_json(root / "webull_compare_summary.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    root = Path(args.artifacts)
    live_build = bool(getattr(args, "live", False) and args.command in {"data-build", "all"})
    if not live_build:
        root.mkdir(parents=True, exist_ok=True)
    handlers = {
        "data-build": _live_data_build if live_build else data_build,
        "train": train,
        "evaluate": evaluate,
        "paper-run": paper_run,
        "report": report,
        "evidence-selfcheck": _selfcheck_evidence,
        "evidence-export": _export_evidence,
        "webull-compare": webull_compare,
    }
    if args.command == "all":
        result = {
            command: handlers[command](args, root)
            for command in ("data-build", "train", "evaluate", "paper-run", "report")
        }
        print(json.dumps(result, sort_keys=True, default=str))
        return 0
    result = handlers[args.command](args, root)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
