"""Default-deny validation for committed public evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import re
from typing import Any, Sequence

from .hashing import sha256_file


EVIDENCE_SCHEMA_VERSION = "public-evidence-v1"
ALLOWLIST_VERSION = "public-evidence-v1"
PUBLIC_SOURCE_MODE = "synthetic"
PRIVATE_SOURCE_MODE = "live"
_MODE_SOURCE_MODES = {"public": PUBLIC_SOURCE_MODE, "private": PRIVATE_SOURCE_MODE}
PUBLIC_FILES = (
    "evidence_report.md",
    "public_provenance.json",
    "public_artifact_index.json",
    "review_attestation.json",
    "experiment_results.csv",
    "fold_metrics.csv",
    "predictive_robustness.csv",
    "development_portfolio_comparison.csv",
    "paper_weekly_returns.csv",
    "paper_model_comparison.csv",
    "paper_cost_sensitivity.csv",
    "paper_skip_counts.csv",
)
HASHED_PUBLIC_FILES = tuple(name for name in PUBLIC_FILES if name not in {"public_artifact_index.json", "review_attestation.json"})
ATTEMPT_ACCEPTED_REASON = "contract_valid"
ATTEMPT_REJECTED_REASONS = ("transport_failure", "contract_validation_failure", "unexpected_failure")
ATTEMPT_REASONS = frozenset((ATTEMPT_ACCEPTED_REASON, *ATTEMPT_REJECTED_REASONS))
_SOURCE_REQUEST_KEYS = {"source", "stream", "endpoint_family", "params", "response_hash", "retrieved_at"}
_SOURCE_PARAM_KEYS = {"adjustment", "asof", "currency", "feed", "forms", "sort", "timeframe"}
PUBLIC_CSV_HEADERS = {
    "experiment_results.csv": "name,family,feature_group,mean_development_ic,nonnegative_fold_fraction,completed_fold_count,fold_ics,errors",
    "fold_metrics.csv": "model,fold_id,train_start,train_end,validation_start,validation_end,embargo_start,train_rows,validation_rows,purged_rows,rank_ic,mae,rmse,top_tercile_excess,dropped_features,error,rank_ic_dates",
    "predictive_robustness.csv": "slice,rows,decision_dates,start,end,rank_ic,mae,rmse,top_tercile_excess,rank_ic_median,rank_ic_std,rank_ic_positive_fraction",
    "development_portfolio_comparison.csv": "model,family,feature_group,status,decision_dates,cumulative_return,annualized_volatility,sharpe,sortino,maximum_drawdown,weekly_hit_rate,average_exposure,gross_cumulative_return,gross_annualized_volatility,gross_sharpe,gross_sortino,gross_maximum_drawdown,gross_weekly_hit_rate,initial_nav,final_nav,final_gross_nav,cost_drag,fee_total,slippage_total,turnover,number_of_rebalances,weekly_observations,sample_start,sample_end,top_tercile_excess_return_mean,top_tercile_excess_return_median,reason",
    "paper_weekly_returns.csv": "week,event_at,net_nav,net_weekly_return,gross_nav,gross_weekly_return,weekly_cost_drag",
    "paper_model_comparison.csv": "model,cumulative_return,annualized_volatility,sharpe,sortino,maximum_drawdown,weekly_hit_rate,average_exposure,gross_cumulative_return,gross_annualized_volatility,gross_sharpe,gross_sortino,gross_maximum_drawdown,gross_weekly_hit_rate,initial_nav,final_nav,final_gross_nav,cost_drag,fee_total,slippage_total,turnover,number_of_rebalances,weekly_observations,top_tercile_excess_return_mean,top_tercile_excess_return_median",
    "paper_cost_sensitivity.csv": "one_way_cost_bps,cumulative_return,annualized_volatility,sharpe,sortino,maximum_drawdown,weekly_hit_rate,average_exposure,gross_cumulative_return,gross_annualized_volatility,gross_sharpe,gross_sortino,gross_maximum_drawdown,gross_weekly_hit_rate,initial_nav,final_nav,final_gross_nav,cost_drag,fee_total,slippage_total,turnover,number_of_rebalances,weekly_observations,sample_start,sample_end,top_tercile_excess_return_mean,top_tercile_excess_return_median",
    "paper_skip_counts.csv": "reason,count",
}

_SECRET_PATTERNS = (
    re.compile(r"(?i)bearer\s+[a-z0-9._~-]{12,}"),
    re.compile(r"(?i)(?:x-access-token|apca-api-key-id|apca-api-secret-key|x-app-key|x-signature)\s*[:=]\s*\S+"),
    re.compile(r"(?i)[?&](?:access_token|api_key|api_secret|signature|sig|token)="),
    re.compile(r"(?:/Users/|/home/|[A-Za-z]:\\\\Users\\\\)"),
)


class PublicEvidenceError(ValueError):
    """Raised when an evidence package is not safe or complete for publication."""


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PublicEvidenceError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PublicEvidenceError(f"JSON object required: {path}")
    return value


def _require_exact_keys(value: dict[str, Any], expected: set[str], *, name: str) -> None:
    if set(value) != expected:
        raise PublicEvidenceError(f"{name} keys must be exactly {sorted(expected)}")


def _require_text(value: Any, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicEvidenceError(f"{name} must be non-empty text")
    return value


def _scan(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
        raise PublicEvidenceError(f"forbidden secret, signed identifier, or local path in {path}")


def _validate_attestation(
    attestation: dict[str, Any], provenance: dict[str, Any], index_hash: str, *, pending: bool
) -> None:
    expected = {
        "allowlist_version",
        "attestation",
        "ci_result",
        "ci_run_url",
        "code_commit",
        "evidence_schema_version",
        "public_contact",
        "reviewed_at",
        "public_artifact_index_hash",
        "reviewer_handle",
        "source_snapshot_hash",
        "status",
        "terms_accessed_at",
        "terms_publication_decision",
        "terms_url",
        "terms_version",
    }
    _require_exact_keys(attestation, expected, name="review attestation")
    if attestation["evidence_schema_version"] != EVIDENCE_SCHEMA_VERSION:
        raise PublicEvidenceError("review attestation schema version mismatch")
    if attestation["allowlist_version"] != ALLOWLIST_VERSION:
        raise PublicEvidenceError("review attestation allowlist version mismatch")
    if attestation["code_commit"] != provenance["code_commit"]:
        raise PublicEvidenceError("review attestation code commit mismatch")
    if attestation["source_snapshot_hash"] != provenance["data_manifest_hash"]:
        raise PublicEvidenceError("review attestation snapshot hash mismatch")
    if attestation["public_artifact_index_hash"] != index_hash:
        raise PublicEvidenceError("review attestation public artifact index hash mismatch")
    if pending:
        if attestation["status"] != "pending":
            raise PublicEvidenceError("pending review attestation status mismatch")
        return
    if attestation["status"] != "approved":
        raise PublicEvidenceError("review attestation must be approved")
    if attestation["ci_result"] != "passed":
        raise PublicEvidenceError("review attestation must record a passed CI result")
    if attestation["terms_publication_decision"] != "permitted":
        raise PublicEvidenceError("review attestation must confirm publication is permitted")
    for name in (
        "reviewer_handle",
        "public_contact",
        "reviewed_at",
        "ci_run_url",
        "terms_url",
        "terms_version",
        "terms_accessed_at",
        "attestation",
    ):
        _require_text(attestation[name], name=f"review attestation {name}")
    if not str(attestation["ci_run_url"]).startswith("https://"):
        raise PublicEvidenceError("review attestation CI URL must be HTTPS")
    if not str(attestation["terms_url"]).startswith("https://"):
        raise PublicEvidenceError("review attestation terms URL must be HTTPS")


def mode_for_source_mode(source_mode: str) -> str:
    """Map a package's ``source_mode`` to the validation mode that must accept it."""
    for mode, required in _MODE_SOURCE_MODES.items():
        if required == source_mode:
            return mode
    raise PublicEvidenceError(f"unsupported source mode: {source_mode!r}")


def validate_public_evidence(root: str | Path, *, mode: str = "public", pending: bool = False) -> None:
    """Reject every public evidence shape except the committed canonical package.

    ``mode`` fixes the required snapshot provenance: ``"public"`` (the committed
    artifact) requires ``source_mode == "synthetic"`` so no real aggregate can pass
    as the public package; ``"private"`` (the reviewer's local reproduction, never
    committed) requires ``source_mode == "live"``.
    """
    required_source_mode = _MODE_SOURCE_MODES.get(mode)
    if required_source_mode is None:
        raise PublicEvidenceError(f"unknown validation mode: {mode!r}")
    root = Path(root)
    if not root.exists():
        raise PublicEvidenceError(f"{mode} evidence root does not exist")
    if not root.is_dir():
        raise PublicEvidenceError("evidence root must be a directory")
    entries = {entry.name: entry for entry in root.iterdir()}
    canonical = entries.pop("CANONICAL.json", None)
    directories = [entry for entry in entries.values() if entry.is_dir()]
    if set(entries) != {entry.name for entry in directories} or len(directories) != 1:
        raise PublicEvidenceError("evidence root must contain CANONICAL.json and one package directory")
    if canonical is None:
        raise PublicEvidenceError("evidence root is missing CANONICAL.json")
    canonical_payload = _read_object(canonical)
    _require_exact_keys(
        canonical_payload,
        {"directory", "evidence_schema_version", "snapshot_manifest_hash"},
        name="canonical pointer",
    )
    package = directories[0]
    if canonical_payload["evidence_schema_version"] != EVIDENCE_SCHEMA_VERSION:
        raise PublicEvidenceError("canonical pointer schema version mismatch")
    if canonical_payload["directory"] != package.name:
        raise PublicEvidenceError("canonical pointer directory mismatch")
    if len(package.name) < 12 or not re.fullmatch(r"[0-9a-f]+", package.name):
        raise PublicEvidenceError("evidence package directory must be a 12+ character hexadecimal prefix")
    files = {path.name for path in package.iterdir() if path.is_file()}
    if files != set(PUBLIC_FILES):
        raise PublicEvidenceError(f"public evidence files must be exactly {list(PUBLIC_FILES)}")
    if any(path.is_dir() for path in package.iterdir()):
        raise PublicEvidenceError("public evidence package must not contain directories")
    for filename in PUBLIC_FILES:
        _scan(package / filename)
    for filename, header in PUBLIC_CSV_HEADERS.items():
        lines = (package / filename).read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != header:
            raise PublicEvidenceError(f"public CSV header mismatch: {filename}")
    provenance = _read_object(package / "public_provenance.json")
    _require_exact_keys(
        provenance,
        {
            "allowlist_version",
            "attempt_summary",
            "code_commit",
            "data_manifest_hash",
            "evidence_schema_version",
            "lockfile_hash",
            "run_id",
            "runtime",
            "source_mode",
            "source_requests",
        },
        name="public provenance",
    )
    if provenance["evidence_schema_version"] != EVIDENCE_SCHEMA_VERSION:
        raise PublicEvidenceError("public provenance schema version mismatch")
    if provenance["allowlist_version"] != ALLOWLIST_VERSION:
        raise PublicEvidenceError("public provenance allowlist version mismatch")
    if provenance["source_mode"] != required_source_mode:
        raise PublicEvidenceError(
            f"{mode} evidence must originate from a {required_source_mode} source snapshot"
        )
    snapshot_hash = _require_text(provenance["data_manifest_hash"], name="data manifest hash")
    if not snapshot_hash.startswith(package.name):
        raise PublicEvidenceError("package directory does not match data manifest hash")
    if canonical_payload["snapshot_manifest_hash"] != snapshot_hash:
        raise PublicEvidenceError("canonical pointer snapshot hash mismatch")
    _require_text(provenance["code_commit"], name="code commit")
    _require_text(provenance["lockfile_hash"], name="lockfile hash")
    source_requests = provenance["source_requests"]
    if not isinstance(source_requests, list) or not source_requests:
        raise PublicEvidenceError("public provenance requires source request summaries")
    for entry in source_requests:
        if not isinstance(entry, dict) or set(entry) != _SOURCE_REQUEST_KEYS:
            raise PublicEvidenceError("source request entry keys are invalid")
        for key in ("source", "stream", "endpoint_family", "response_hash", "retrieved_at"):
            _require_text(entry[key], name=f"source request {key}")
        if not isinstance(entry["params"], dict) or not set(entry["params"]).issubset(_SOURCE_PARAM_KEYS):
            raise PublicEvidenceError("source request params contain undeclared keys")
    runtime = provenance["runtime"]
    if not isinstance(runtime, dict) or not all(isinstance(value, str) for value in runtime.values()):
        raise PublicEvidenceError("public provenance runtime values must be strings")
    attempts = provenance["attempt_summary"]
    if not isinstance(attempts, dict) or set(attempts) != {
        "attempt_count",
        "accepted_snapshot_hash",
        "attempts",
        "rejected_reason_counts",
    }:
        raise PublicEvidenceError("public provenance attempt summary shape is invalid")
    if attempts["accepted_snapshot_hash"] != snapshot_hash:
        raise PublicEvidenceError("attempt summary snapshot hash mismatch")
    if not isinstance(attempts["attempt_count"], int) or attempts["attempt_count"] < 1:
        raise PublicEvidenceError("attempt summary requires a positive attempt count")
    reason_counts = attempts["rejected_reason_counts"]
    if not isinstance(reason_counts, dict):
        raise PublicEvidenceError("attempt summary rejected reasons must be an object")
    for reason, count in reason_counts.items():
        if (
            reason not in ATTEMPT_REJECTED_REASONS
            or not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            raise PublicEvidenceError("attempt summary rejected reason counts are invalid")
    if not isinstance(attempts["attempts"], list) or len(attempts["attempts"]) != attempts["attempt_count"]:
        raise PublicEvidenceError("attempt summary entries must match attempt count")
    allowed_reasons = ATTEMPT_REASONS
    for attempt in attempts["attempts"]:
        if not isinstance(attempt, dict) or set(attempt) != {"finished_at", "outcome", "reason", "started_at"}:
            raise PublicEvidenceError("attempt summary entry shape is invalid")
        if attempt["reason"] not in allowed_reasons or attempt["outcome"] not in {"accepted", "rejected"}:
            raise PublicEvidenceError("attempt summary contains an invalid outcome or reason")
    index = _read_object(package / "public_artifact_index.json")
    _require_exact_keys(index, {"evidence_schema_version", "files"}, name="public artifact index")
    if index["evidence_schema_version"] != EVIDENCE_SCHEMA_VERSION or not isinstance(index["files"], dict):
        raise PublicEvidenceError("public artifact index is invalid")
    if set(index["files"]) != set(HASHED_PUBLIC_FILES):
        raise PublicEvidenceError("public artifact index allowlist mismatch")
    for filename in HASHED_PUBLIC_FILES:
        if index["files"][filename] != sha256_file(package / filename):
            raise PublicEvidenceError(f"public artifact hash mismatch: {filename}")
    _validate_attestation(
        _read_object(package / "review_attestation.json"),
        provenance,
        sha256_file(package / "public_artifact_index.json"),
        pending=pending,
    )

def validate_git_history(root: str | Path, revision: str) -> None:
    """Lock evidence after a canonical package exists in the baseline revision."""
    root = Path(root)
    baseline_pointer = subprocess.run(
        ("git", "cat-file", "-e", f"{revision}:{root}/CANONICAL.json"),
        capture_output=True,
        check=False,
    )
    if baseline_pointer.returncode:
        return
    changed = subprocess.run(
        ("git", "diff", "--quiet", revision, "--", str(root)),
        capture_output=True,
        check=False,
    )
    if changed.returncode == 1:
        raise PublicEvidenceError("canonical evidence is immutable; add a replication schema first")
    if changed.returncode:
        raise PublicEvidenceError("could not verify canonical evidence history")




def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m looloo_finance_ml.evidence")
    parser.add_argument("root", nargs="?", default="evidence")
    parser.add_argument("--mode", choices=("public", "private"), default="public")
    parser.add_argument("--git-baseline")
    args = parser.parse_args(argv)
    validate_public_evidence(args.root, mode=args.mode)
    if args.git_baseline:
        validate_git_history(args.root, args.git_baseline)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
