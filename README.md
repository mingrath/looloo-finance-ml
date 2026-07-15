# Cross-sectional equity return-ranking evidence project

[![CI](https://github.com/mingrath/looloo-finance-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/mingrath/looloo-finance-ml/actions/workflows/ci.yml)

Candidate-owned Finance + ML portfolio project for Looloo's junior Machine Learning Engineer (Project Algorithmic Trading) role. It ranks the next five-session excess return of a frozen 30-stock US equity panel, evaluates one untouched 2025 holdout, and replays a deterministic paper-only portfolio. It does not place orders or claim profitability.

The approved decision contract is [selected-project-contract.md](docs/assets/selected-project-contract.md); the full implementation and evidence standard is [build-brief.md](docs/build-brief.md).

## See it without running

Read a full sample run (synthetic fixture) without installing anything: [docs/sample-evidence/evidence_report.md](docs/sample-evidence/evidence_report.md). To verify the code quickly, `uv run pytest -q` finishes in seconds (53 tests). To reproduce end to end, run the self-contained check below and open the generated `artifacts/<run>/runs/<run-id>/evidence_report.md`; the synthetic pipeline takes roughly 15 minutes on a standard CI runner.

## Run the self-contained check

```sh
uv sync --locked --extra dev
uv run pytest -q
uv run looloo-finance-ml --artifacts artifacts/synthetic-001 all
```

The default is a deterministic synthetic fixture. It validates the complete workflow but is **not hiring or investment evidence**. Each artifact root is immutable; use a new directory for every run.

## Run with licensed source data

Set local-only environment variables (copy `.env.example`; do not commit `.env`):

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `SEC_USER_AGENT` — descriptive application/contact string
- `GIT_COMMIT` — exactly `git rev-parse HEAD`

Canonical live acquisition requires a clean Git checkout. It stages every attempt outside the target root, logs only pre-evaluation integrity failures, and promotes the first contract-valid snapshot atomically. CI never receives credentials or licensed data; it runs the synthetic workflow only.

```sh
GIT_COMMIT="$(git rev-parse HEAD)" uv run looloo-finance-ml --artifacts artifacts/live-001 all --live
```

Raw and normalized Alpaca data, predictions, model files, and event logs remain local and ignored. Keep the accepted archive access-controlled; the current vendor-terms review determines retention and any manual purge condition.

## Publish canonical evidence

Only publish an aggregate package after the current Alpaca terms affirm that exact disclosure is permitted. Otherwise publish code and **synthetic verification** only; do not privately redistribute the real-derived package.

From the exact clean commit that produced the accepted live run:

```sh
uv run looloo-finance-ml --artifacts artifacts/live-001 evidence-export --output evidence
```

This creates one hash-named, default-deny package and a pending `review_attestation.json`. A distinct reviewer must complete the attestation with the checked CI URL/result, terms URL/version/access date, publication decision, and public contact before the evidence-only PR is merged. The package is all rights reserved; `LICENSE` applies only to candidate-authored code.

The public allowlist is the report, provenance and hash index, model/fold/robustness aggregates, weekly portfolio returns, model comparison, cost sensitivity, and skip counts. It excludes bars, SEC facts, symbol-level features/predictions/fills, model files, event logs, bootstrap samples, per-date IC, and top-tercile return series.

## Review the evidence

Open `artifacts/<run>/runs/<run-id>/evidence_report.md`, then inspect the generated aggregate tables and immutable manifests. Synthetic runs are pipeline checks, not hiring or investment evidence. A prior rank-IC regression is covered by a focused test; no unverified historical incident is presented as an observed run failure.

## Contract in one screen

- **Universe:** frozen 30-stock liquid US equity panel; survivorship and selection bias remain explicit limitations.
- **Target:** stock five-session return minus equal-weight basket return, ranked cross-sectionally.
- **Features:** split-invariant price/volume history plus point-in-time SEC fundamentals.
- **Validation:** expanding walk-forward folds, purge, embargo, train-fold-only preprocessing, frozen promotion rule.
- **Models:** no-signal and momentum baselines; Elastic Net and histogram gradient boosting over fixed feature/configuration groups.
- **Holdout:** 2025, revealed once after model selection.
- **Replay:** next-session open entry, fifth-session close exit, 1 bp fee + 5 bps slippage per side, cash-only, no broker integration.
- **Evidence:** predictive metrics, 2,000-sample moving-block bootstrap, robustness slices, cost sensitivity, fail-closed replay, immutable manifests, and event logs.

## Code map

- `src/looloo_finance_ml/sources.py` — Alpaca/SEC adapters and source capture
- `features.py` — point-in-time features and labels
- `validation.py` — temporal folds, purge, embargo, holdout seam
- `models.py` — frozen candidate ladder and fold-local preprocessing
- `evaluation.py`, `metrics.py` — predictive evidence and uncertainty

- `paper.py` — deterministic fail-closed paper ledger
- `cli.py` — immutable workflow and recruiter-facing report

## Webull Thailand boundary

Webull Thailand OpenAPI is retained as a future, separately governed own-account execution integration. It is not a research-data fallback and this package never places orders. The frozen research corpus stays Alpaca + SEC because its split-adjusted feature stream and all-adjusted label/fill stream are part of the contract. Before any Webull execution work: approve the account/authorization model, current API and commercial terms, sandbox validation, risk caps, idempotency, kill switch, reconciliation, audit logs, secret isolation, and Thai compliance review.

## Reuse boundary

[HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) and [Packt's Machine Learning for Algorithmic Trading repository](https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition) were studied as references only. No code, data, trained artifact, generated strategy, or runtime component from either repository is used here. Vibe-Trading publishes an MIT license; no repository-level license was verified for the Packt repository, so its code is not copied or redistributed.
