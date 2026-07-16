# Operational runbook — recurring local live runs

How to operate `looloo-finance-ml` as a maintained side project: a repeatable
**local** procedure for recurring real (`--live`) runs. This is the steady-state
loop the first real run ([#5](https://github.com/mingrath/looloo-finance-ml/issues/5))
established; follow it for every subsequent refresh.

**Hard constraint (never violate):** live acquisition runs from a clean **local**
checkout only. CI never receives credentials or licensed data (`README.md` →
"Run with licensed source data"). There is deliberately **no** scheduled GitHub
Actions workflow with `secrets` — Alpaca market data is non-redistributable under
Customer Agreement §30 ([`docs/vendor-terms-review.md`](vendor-terms-review.md)),
so licensed data must never touch a shared runner. Recurrence is a human running
this loop locally, or (optionally, later) a self-managed runner under the same
terms review — see
[Optional: credential-safe self-hosted runner](#optional-credential-safe-self-hosted-runner).

## Cadence

Run **weekly**. The contract's decision point is the scheduled close of the last
valid XNYS session each week, and the label horizon is five sessions (`README.md`
summary; `docs/build-brief.md`) — so one refresh per week matches the horizon and
keeps the evidence current without redundant re-pulls.

There is no automatic scheduler (that would require credentialed automation). Put
the weekly run on your own calendar/reminder. A run takes roughly 15–20 minutes
end to end (the first real run was ~19 min).

## What "the frozen contract" means here

The data contract — feed, `adjustment` streams (`split` for features, `all` for
labels/fills), and `asof` — is frozen in `src/looloo_finance_ml/sources.py` and is
the single source of truth. **The operator never passes it on the command line.**
Changing it is a formal contract revision (build-brief Phase 0), not a runbook
step; the demonstrated feed is currently being revised `feed=iex`→`feed=sip`
([#12](https://github.com/mingrath/looloo-finance-ml/issues/12) /
[#14](https://github.com/mingrath/looloo-finance-ml/issues/14)). This runbook is
contract-agnostic: the procedure below is identical regardless of which feed the
frozen contract pins.

## Pre-run checklist

1. **Clean, known checkout.** Pull the intended commit on `main`. The worktree
   must be clean — `git status --porcelain` empty. `_live_data_build` refuses a
   dirty tree ("live evidence requires a clean Git worktree").
2. **`GIT_COMMIT` will be set to HEAD.** The run reads `GIT_COMMIT` from the
   environment and aborts unless it equals the checked-out HEAD ("GIT_COMMIT must
   match the checked-out HEAD"); the command below sets it inline. This stamps
   provenance onto the accepted snapshot.
3. **Credentials present, and exported into the shell.** `ALPACA_API_KEY`,
   `ALPACA_API_SECRET`, and a descriptive `SEC_USER_AGENT` (must include an
   application name and a contact email). Keep them in a git-ignored `.env` (copy
   `.env.example`; never commit `.env`) — but note **the code has no dotenv
   loader**: it reads credentials straight from the process environment
   (`config.py`), so you must `export`/`source` them into your shell before
   running (the command block does this). `.env`, `.env.*`, `artifacts/`,
   `.staging/`, and `.*.attempts.jsonl` are all git-ignored.
4. **Fresh artifact directory.** Pick the next unused `artifacts/live-00N`
   (the sequence so far: `live-001` overflow repro, `live-002` accepted). The
   target must not already exist — `_live_data_build` refuses to overwrite
   ("live evidence target must not exist; use a fresh artifact directory"). Each
   artifact root is immutable.
5. **Disk space.** Budget a few GB free. The pull writes raw + normalized Alpaca
   bars for the 30-symbol panel plus the SEC CompanyFacts corpus (~800k fact rows
   on the first real run), then model files, JSONL event logs, and 2,000 bootstrap
   samples per run. Full-market SIP coverage produces more bars than the thin IEX
   pull did. The retention policy below (keep at most one accepted archive) bounds
   long-run growth.
6. **Deps synced + green.** `uv sync --locked --extra dev && uv run ruff check . &&
   uv run pytest -q` before committing to a real pull, so a known-good build is
   what runs.

## The exact command

From the clean checkout, with the next free `live-00N`:

```sh
# 1. Load local creds into the shell — the code has no dotenv loader.
set -a; . ./.env; set +a

# 2. Choose the next unused artifact root (bump N each run; the CLI refuses an existing root).
ARTIFACT_ROOT=artifacts/live-003

# 3. Run the full live pipeline. The inline GIT_COMMIT overrides whatever .env
#    holds and must equal HEAD.
GIT_COMMIT="$(git rev-parse HEAD)" \
  uv run looloo-finance-ml --artifacts "$ARTIFACT_ROOT" all --live
```

`all --live` runs the full pipeline in order: **data-build (live) → train →
evaluate → paper-run → report** (the `all` branch of `cli.py`'s `main()`).
`--live` only changes the data-build stage (real Alpaca + SEC acquisition instead
of the synthetic fixture); every downstream stage is identical to a synthetic run.

## Where artifacts land

With `ARTIFACT_ROOT=artifacts/live-003` as the example (substitute your chosen root):

- `artifacts/live-003/` — promoted snapshot: `feature_bars.csv`,
  `label_fill_bars.csv`, `data_artifact_manifest.json`, `data_build_summary.json`,
  `complete_history_subset.json`, model files, event logs, bootstrap samples.
- `artifacts/live-003/runs/<run-id>/evidence_report.md` — the recruiter-facing
  report, plus `report_manifest.json`, `experiment_results.csv`, `fold_metrics.csv`,
  `predictive_robustness.csv`, and the other aggregate tables. `<run-id>` is a UTC
  timestamp + short hash, e.g. `20260716T030412507825Z-ede6fd03`.
- `artifacts/.live-003.attempts.jsonl` — the append-only attempt journal (sibling
  of the artifact root, git-ignored).
- `artifacts/.staging/live-003-<hex>/` — transient staging; discarded on rejection,
  atomically renamed into place on acceptance. It should not persist after a run.

All of the above is local and git-ignored. Open the `evidence_report.md` to read
the run.

## How to read the outcome

Live acquisition **stages every attempt outside the target root and promotes the
first contract-valid snapshot atomically** (`README.md` → "Run with licensed
source data"). The attempt journal `artifacts/.live-00N.attempts.jsonl` is the
record of what happened — one JSON line per attempt.

**Accepted** — the line reads `"outcome": "accepted"`, `"reason": "contract_valid"`,
with a `data_manifest_hash`. The staged snapshot was renamed into `artifacts/live-00N`
and the pipeline continued. This is the normal path.

**Rejected** — the line reads `"outcome": "rejected"` with one of the reasons in
`ATTEMPT_REJECTED_REASONS` (`evidence.py`):

- `transport_failure` — a network/API error (`HttpError`) during acquisition.
  Transient; check connectivity, credentials, and Alpaca/SEC availability, then
  re-run into the **same** fresh directory (the failed staging was already
  discarded, so the target name is free again).
- `contract_validation_failure` — the data failed a contract check (`DataError`):
  duplicate timestamps, malformed/non-positive OHLC, ambiguous units, unverified
  corporate-action handling, missing pages, or a changed schema (build-brief
  "Schema/failure policy"). This is a **real data problem** — understand it before
  re-running; do not blind-retry.
- `unexpected_failure` — anything else. Investigate before retrying.

Only **pre-evaluation integrity failures at data-build** are journaled. A crash
*after* acceptance (in `train`/`evaluate`/etc.) is a pipeline defect, not a
rejection — the snapshot was already promoted, so the fix is to the code, then a
fresh run. (This is exactly the shape of the int64-ns overflow the first real run
surfaced and fixed, [#5](https://github.com/mingrath/looloo-finance-ml/issues/5).)

**Coverage gate — check even on an accepted run.** Acceptance means the snapshot
is contract-valid, *not* that coverage is adequate. Read the evidence report's
complete-history lines and confirm:

- `complete_history_symbol_count` ≥ `top_n` (= 10). The `complete_history_portfolio`
  replay in `paper_run` only runs when there are at least `top_n` complete symbols;
  below that it reports `not_estimable` and the `holdout_complete_history_subset`
  predictive slice is empty.
- Ideally all 30 symbols clear the frozen thresholds (≥95% coverage over the
  window, longest missing run ≤ 5).

A thin feed can pass acceptance yet leave the complete-history evidence empty —
that is what happened on the IEX run (`complete_history_symbol_count: 0`), and is
the reason for the `feed=sip` revision. If a run is accepted but the coverage gate
is not met, treat the *evidence* as degraded and follow the coverage-gate
disposition in [#15](https://github.com/mingrath/looloo-finance-ml/issues/15).

## Archive retention (per #1)

The accepted `artifacts/live-00N` tree is licensed, non-redistributable data.
Apply the data-minimization policy from
[`docs/vendor-terms-review.md`](vendor-terms-review.md) ("Retention & purge"):

- **Store local only**, access-controlled, git-ignored. Never commit; never place
  in shared/cloud storage; never publish or privately redistribute the real numbers.
- **Retain at most one accepted archive at a time.** A newer accepted run
  supersedes the previous one — delete the old `artifacts/live-00N` when the new
  run is accepted.
- **Retention ceiling: 12 months** from the run date.
- **Purge within 30 days** of the earliest of: the hiring/interview cycle concludes;
  Alpaca account closure or loss of permitted access; a written request from Alpaca
  or a participating exchange; or supersession by a newer accepted run.
- **Manual purge = delete the entire `artifacts/live-00N` directory** (and any local
  backups). Non-licensed provenance metadata already permitted for disclosure
  (request manifest, response hashes, terms snapshot) may be retained for
  reproducibility claims; licensed bars and derived symbol-level artifacts may not.

When re-verifying a run for publication, re-snapshot the current Alpaca §30 terms
at that run (vendor-review re-verification requirement).

## CI stays synthetic-only — and why

CI (`.github/workflows/ci.yml`) runs on every push/PR with `GIT_COMMIT:
${{ github.sha }}` and **no secrets**: `ruff` → `pytest` → the **synthetic** `all`
pipeline (no `--live`) → `evidence-selfcheck` → `evidence --git-baseline HEAD^`.
It never acquires real data.

This is deliberate and permanent:

- **Terms.** Alpaca market data is non-redistributable under §30. A shared,
  publicly logged runner is not a permitted place for licensed data or the
  credentials that fetch it.
- **Contract.** The README ("Run with licensed source data") fixes live
  acquisition to a clean local checkout; CI never receives credentials or licensed
  data.

So CI's job is to prove the **code** is correct against the synthetic fixture and
that the public-evidence export stays default-deny (`evidence-selfcheck`). Proving
the code works on **real** data is this local runbook's job. The two are separated
on purpose; do not add a credentialed scheduled workflow.

## Optional: credential-safe self-hosted runner

If fully hands-off weekly recurrence is later wanted, the only terms-compatible
automation is a **self-managed** runner the maintainer owns and controls — not a
GitHub-hosted runner, and never with repository secrets exposed to fork PRs. It
would hold Alpaca credentials and the licensed accepted archive, so it inherits
every constraint above: private, access-controlled, local-equivalent storage, and
the same retention/purge policy.

This is **gated on the same vendor-terms review** ([#1](https://github.com/mingrath/looloo-finance-ml/issues/1)):
standing up such a runner is a governance decision, not a convenience, and should
be scoped as its own effort (including where credentials live, how the runner is
isolated, and how the §30 non-redistribution guarantee is preserved) before it is
built. Absent that, the weekly manual loop above is the supported path.
