from __future__ import annotations


from argparse import Namespace
import pandas as pd
import json
import pytest

from looloo_finance_ml.cli import (
    _assert_complete_dates,
    _assert_finite_columns,
    _data_provenance,
    _code_commit,
    _drop_incomplete_dates,
    _top_tercile_excess,
    _attempt_summary,
    _parser,
    _write_hashed_json,
    data_build,
    _build_evidence_package,
    _export_evidence,
    _export_public_evidence,
    _write_procedural_journal,
)
from looloo_finance_ml.evidence import PublicEvidenceError, validate_public_evidence
from looloo_finance_ml.evidence import validate_git_history
from looloo_finance_ml.evidence import HASHED_PUBLIC_FILES, PUBLIC_CSV_HEADERS, PUBLIC_FILES
from looloo_finance_ml.hashing import sha256_file
from looloo_finance_ml.fixtures import FROZEN_SYMBOLS
from looloo_finance_ml.paper import PaperConfig, ReplayResult


def test_live_evidence_requires_verified_checked_out_commit(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_hashed_json(tmp_path / "data_artifact_manifest.json", {"source_mode": "live"})
    monkeypatch.delenv("GIT_COMMIT", raising=False)
    monkeypatch.delenv("CODE_COMMIT", raising=False)
    with pytest.raises(RuntimeError, match="GIT_COMMIT"):
        _code_commit(tmp_path)

    monkeypatch.setenv("GIT_COMMIT", "abc123")
    monkeypatch.setattr("looloo_finance_ml.cli._git_output", lambda *_: "def456")
    with pytest.raises(RuntimeError, match="match"):
        _code_commit(tmp_path)


def test_cli_parser_accepts_non_live_commands() -> None:
    assert _parser().parse_args(["train"]).command == "train"


def test_attempt_summary_rejects_noncanonical_acceptance(tmp_path) -> None:
    journal = tmp_path / "attempts.jsonl"
    journal.write_text(
        json.dumps({"outcome": "accepted", "data_manifest_hash": "wrong", "reason": "contract_valid"})
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="does not identify"):
        _attempt_summary(journal, "expected")


def test_public_evidence_rejects_unknown_files(tmp_path) -> None:
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()
    (evidence_root / "unexpected.csv").write_text("nope\n", encoding="utf-8")
    with pytest.raises(PublicEvidenceError, match="CANONICAL"):
        validate_public_evidence(evidence_root)


def _valid_pending_evidence(tmp_path, *, source_mode="synthetic"):
    evidence_root = tmp_path / "evidence"
    package = evidence_root / ("a" * 12)
    package.mkdir(parents=True)
    snapshot_hash = "a" * 64
    for filename in PUBLIC_FILES:
        (package / filename).write_text(PUBLIC_CSV_HEADERS.get(filename, "placeholder") + "\n", encoding="utf-8")
    provenance = {
        "allowlist_version": "public-evidence-v1",
        "attempt_summary": {
            "attempt_count": 1,
            "accepted_snapshot_hash": snapshot_hash,
            "attempts": [
                {
                    "started_at": "2026-01-01T00:00:00+00:00",
                    "finished_at": "2026-01-01T00:01:00+00:00",
                    "outcome": "accepted",
                    "reason": "contract_valid",
                }
            ],
            "rejected_reason_counts": {},
        },
        "code_commit": "b" * 40,
        "data_manifest_hash": snapshot_hash,
        "evidence_schema_version": "public-evidence-v1",
        "lockfile_hash": "c" * 64,
        "run_id": "run-1",
        "runtime": {},
        "source_mode": source_mode,
        "source_requests": [
            {
                "source": "alpaca",
                "stream": "feature_stream",
                "endpoint_family": "https://data.alpaca.markets/v2/stocks/bars",
                "params": {"adjustment": "split"},
                "response_hash": "d" * 64,
                "retrieved_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    }
    (package / "public_provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    index = {
        "evidence_schema_version": "public-evidence-v1",
        "files": {filename: sha256_file(package / filename) for filename in HASHED_PUBLIC_FILES},
    }
    (package / "public_artifact_index.json").write_text(json.dumps(index), encoding="utf-8")
    attestation = {
        "allowlist_version": "public-evidence-v1",
        "attestation": "",
        "ci_result": "pending",
        "ci_run_url": "",
        "code_commit": provenance["code_commit"],
        "evidence_schema_version": "public-evidence-v1",
        "public_artifact_index_hash": sha256_file(package / "public_artifact_index.json"),
        "public_contact": "",
        "reviewed_at": "",
        "reviewer_handle": "",
        "source_snapshot_hash": snapshot_hash,
        "status": "pending",
        "terms_accessed_at": "",
        "terms_publication_decision": "pending",
        "terms_url": "",
        "terms_version": "",
    }
    (package / "review_attestation.json").write_text(json.dumps(attestation), encoding="utf-8")
    (evidence_root / "CANONICAL.json").write_text(
        json.dumps(
            {
                "directory": package.name,
                "evidence_schema_version": "public-evidence-v1",
                "snapshot_manifest_hash": snapshot_hash,
            }
        ),
        encoding="utf-8",
    )
    return evidence_root


def test_public_evidence_accepts_pending_allowlisted_package(tmp_path) -> None:
    validate_public_evidence(_valid_pending_evidence(tmp_path), pending=True)


def test_public_evidence_rejects_header_and_source_request_drift(tmp_path) -> None:
    root = _valid_pending_evidence(tmp_path)
    package = next(entry for entry in root.iterdir() if entry.is_dir())
    good = (package / "paper_skip_counts.csv").read_text(encoding="utf-8")
    (package / "paper_skip_counts.csv").write_text("symbol,count\nAAPL,1\n", encoding="utf-8")
    with pytest.raises(PublicEvidenceError, match="header mismatch"):
        validate_public_evidence(root, pending=True)
    (package / "paper_skip_counts.csv").write_text(good, encoding="utf-8")

    provenance_path = package / "public_provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance["source_requests"][0]["symbol"] = "AAPL"
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")
    with pytest.raises(PublicEvidenceError, match="source request entry keys"):
        validate_public_evidence(root, pending=True)



def test_canonical_history_rejects_changed_evidence(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    def result(code: int) -> object:
        return type("Result", (), {"returncode": code})()

    calls: list[tuple[str, ...]] = []

    def run(command: tuple[str, ...], **_: object) -> object:
        calls.append(command)
        return result(0 if "cat-file" in command else 1)

    monkeypatch.setattr("looloo_finance_ml.evidence.subprocess.run", run)
    with pytest.raises(PublicEvidenceError, match="immutable"):
        validate_git_history(tmp_path / "evidence", "HEAD^")
    assert calls

def test_data_provenance_rejects_tampered_normalized_artifact(tmp_path) -> None:
    args = Namespace(live=False, start="2021-01-04", end="2021-01-15")
    data_build(args, tmp_path)
    with (tmp_path / "feature_bars.csv").open("a", encoding="utf-8") as stream:
        stream.write("\n")

    with pytest.raises(RuntimeError, match="data artifact hash mismatch"):
        _data_provenance(tmp_path)


def test_incomplete_cross_section_drops_the_whole_decision_date() -> None:
    dates = {
        pd.Timestamp("2025-01-03T21:00:00Z"),
        pd.Timestamp("2025-01-10T21:00:00Z"),
        pd.Timestamp("2025-01-17T21:00:00Z"),
    }
    absent_date, partial_date, complete_date = sorted(dates)
    rows = pd.DataFrame(
        [
            {"decision_at": decision_at, "symbol": symbol}
            for decision_at in (partial_date, complete_date)
            for symbol in FROZEN_SYMBOLS
        ]
    )
    rows = rows[~(rows["decision_at"].eq(partial_date) & rows["symbol"].eq(FROZEN_SYMBOLS[0]))]

    complete, diagnostics = _drop_incomplete_dates(
        rows, name="price_features", expected_dates=dates
    )

    assert set(complete["decision_at"]) == {complete_date}
    assert any(
        item["decision_at"] == absent_date and item["missing_symbols"] == sorted(FROZEN_SYMBOLS)
        for item in diagnostics
    )
    assert any(
        item["decision_at"] == partial_date and item["missing_symbols"] == [FROZEN_SYMBOLS[0]]
        for item in diagnostics
    )


def test_prediction_validation_rejects_partial_decision_date() -> None:
    rows = pd.DataFrame(
        [
            {
                "decision_at": "2025-01-03T21:00:00Z",
                "label_end": "2025-01-10T21:00:00Z",
                "symbol": symbol,
                "prediction": 0.0,
                "target": 0.0,
            }
            for symbol in FROZEN_SYMBOLS[:-1]
        ]
    )

    with pytest.raises(RuntimeError, match="incomplete cross-section"):
        _assert_complete_dates(rows, name="predictions")


def test_prediction_validation_rejects_nonfinite_values() -> None:
    rows = pd.DataFrame(
        [
            {
                "decision_at": "2025-01-03T21:00:00Z",
                "label_end": "2025-01-10T21:00:00Z",
                "symbol": symbol,
                "prediction": 0.0,
                "target": 0.0,
            }
            for symbol in FROZEN_SYMBOLS
        ]
    )
    rows.loc[0, "prediction"] = float("inf")

    with pytest.raises(RuntimeError, match="non-finite"):
        _assert_finite_columns(rows, ("prediction", "target"), name="predictions")


def test_top_tercile_excess_uses_aligned_weekly_net_returns() -> None:
    def replay(final_nav: float) -> ReplayResult:
        return ReplayResult(
            events=[
                {
                    "event_type": "mark",
                    "event_at": "2025-01-03T21:00:00Z",
                    "net_nav": 100.0,
                    "gross_nav": 100.0,
                },
                {
                    "event_type": "mark",
                    "event_at": "2025-01-10T21:00:00Z",
                    "net_nav": final_nav,
                    "gross_nav": final_nav,
                },
            ],
            summary={},
            failed=False,
        )

    metrics, weekly = _top_tercile_excess(
        replay(110.0), replay(105.0), PaperConfig(initial_nav=100.0)
    )

    assert weekly["top_tercile_excess_return"].tolist() == pytest.approx([0.0, 0.05])
    assert metrics == pytest.approx(
        {"top_tercile_excess_return_mean": 0.025, "top_tercile_excess_return_median": 0.025}
    )


def _approved_attestation(package, provenance):
    return {
        "allowlist_version": "public-evidence-v1",
        "attestation": "independently reproduced and verified",
        "ci_result": "passed",
        "ci_run_url": "https://ci.example.com/run/1",
        "code_commit": provenance["code_commit"],
        "evidence_schema_version": "public-evidence-v1",
        "public_artifact_index_hash": sha256_file(package / "public_artifact_index.json"),
        "public_contact": "reviewer@example.com",
        "reviewed_at": "2026-02-01T00:00:00+00:00",
        "reviewer_handle": "reviewer",
        "source_snapshot_hash": provenance["data_manifest_hash"],
        "status": "approved",
        "terms_accessed_at": "2026-01-15",
        "terms_publication_decision": "permitted",
        "terms_url": "https://alpaca.markets/terms",
        "terms_version": "2026-01",
    }


def test_public_mode_rejects_live_snapshot(tmp_path) -> None:
    root = _valid_pending_evidence(tmp_path, source_mode="live")
    with pytest.raises(PublicEvidenceError, match="synthetic source snapshot"):
        validate_public_evidence(root, mode="public", pending=True)


def test_private_mode_rejects_synthetic_snapshot(tmp_path) -> None:
    root = _valid_pending_evidence(tmp_path, source_mode="synthetic")
    with pytest.raises(PublicEvidenceError, match="live source snapshot"):
        validate_public_evidence(root, mode="private", pending=True)


def test_private_finalized_validation_rejects_pending_and_accepts_approved(tmp_path) -> None:
    root = _valid_pending_evidence(tmp_path, source_mode="live")
    package = next(entry for entry in root.iterdir() if entry.is_dir())
    provenance = json.loads((package / "public_provenance.json").read_text(encoding="utf-8"))
    with pytest.raises(PublicEvidenceError, match="must be approved"):
        validate_public_evidence(root, mode="private", pending=False)
    (package / "review_attestation.json").write_text(
        json.dumps(_approved_attestation(package, provenance)), encoding="utf-8"
    )
    validate_public_evidence(root, mode="private", pending=False)


def test_public_export_requires_synthetic_snapshot(tmp_path) -> None:
    (tmp_path / "data_build_summary.json").write_text(
        json.dumps({"source_mode": "live"}), encoding="utf-8"
    )
    args = Namespace(output=str(tmp_path / "out"), attempt_journal=None)
    with pytest.raises(RuntimeError, match="synthetic source snapshot"):
        _export_public_evidence(args, tmp_path)


def test_private_export_requires_live_snapshot(tmp_path) -> None:
    (tmp_path / "data_build_summary.json").write_text(
        json.dumps({"source_mode": "synthetic"}), encoding="utf-8"
    )
    args = Namespace(output=str(tmp_path / "out"), attempt_journal=None)
    with pytest.raises(RuntimeError, match="live source snapshot"):
        _export_evidence(args, tmp_path)


def _synthetic_run_dir(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "evidence_report.md").write_text(
        "# Evidence report\n\nSynthetic fixture summary.\n## Artifact index\nprivate index\n",
        encoding="utf-8",
    )
    for filename, header in PUBLIC_CSV_HEADERS.items():
        (run_dir / filename).write_text(header + "\n", encoding="utf-8")
    return run_dir


def test_synthetic_package_round_trips_public_validation(tmp_path) -> None:
    run_dir = _synthetic_run_dir(tmp_path)
    snapshot_hash = "a" * 64
    manifests = {
        "feature": {
            "source": "alpaca",
            "stream": "feature_stream",
            "params": {"adjustment": "split", "feed": "sip"},
            "response_hash": "d" * 64,
            "retrieved_at": "2026-01-01T00:00:00+00:00",
        }
    }
    journal = tmp_path / "attempts.jsonl"
    _write_procedural_journal(journal, snapshot_hash)
    output = tmp_path / "evidence"
    result = _build_evidence_package(
        output,
        run_dir=run_dir,
        run_id="run-1",
        data_manifest_hash=snapshot_hash,
        code_commit="working-tree",
        manifests=manifests,
        journal=journal,
        source_mode="synthetic",
    )
    assert result["data_manifest_hash"] == snapshot_hash
    validate_public_evidence(output, mode="public", pending=True)
    with pytest.raises(PublicEvidenceError, match="live source snapshot"):
        validate_public_evidence(output, mode="private", pending=True)


def test_public_and_private_modes_fail_closed_on_missing_root(tmp_path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(PublicEvidenceError, match="private evidence root does not exist"):
        validate_public_evidence(missing, mode="private")
    with pytest.raises(PublicEvidenceError, match="public evidence root does not exist"):
        validate_public_evidence(missing, mode="public")
