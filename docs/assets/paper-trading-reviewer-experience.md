# Paper-trading reviewer experience and implementation sequence

**Status:** implemented reviewer journey and delivery boundary for the selected **portfolio project**. The packaged CLI now produces the local paper-trading evidence defined here.

Related contracts:

- [Selected project and ML/data contract](selected-project-contract.md)
- [Experimental and backtest proof](experimental-proof.md)
- [Looloo project-evidence rubric](looloo-project-evidence-rubric.md)

## Reviewer journey

The repository should make the evidence legible in this order:

1. **30-second recruiter view:** one project card states the decision (weekly cross-sectional equity ranking), the target role, candidate ownership, and the honest outcome boundary: historical research plus a no-capital paper-trading demo, not an investment product or profitability claim.
2. **Five-minute technical overview:** the problem/data contract, one architecture diagram, the baseline/model table, the evaluation report, and the limitations section. The first screen links to the exact source and license obligations.
3. **Reproducibility path:** a clean checkout runs the documented setup; a reviewer with permitted Alpaca access can build the exact 2021-01-04–2025-12-31 snapshot, see source hashes and SEC accession/filed timestamps, and rerun the report without editing code.
4. **Model path:** the reviewer opens the experiment index, compares constant-zero, momentum, ElasticNet, and HistGradientBoosting runs, sees the temporal folds and untouched 2025 holdout, and reads at least one negative result.
5. **Diagnosis path:** the reviewer follows one real failure from symptom through hypotheses, root cause, fix, and before/after verification. The raw row/code invariant that proves the cause is linked.
6. **Paper-trading path:** the reviewer runs a deterministic local historical replay. Each weekly decision produces a score file, simulated orders/fills, positions, cash, turnover, cost, and structured logs. The replay is clearly labeled a **paper-trading demo** and cannot reach a live broker.
7. **Interview path:** the candidate can navigate from any reported number to its manifest, configuration, source snapshot, fold, and formula, then explain rejected alternatives and limitations from first principles.

The order deliberately shows evidence before presentation polish. A dashboard is not part of the reviewer journey because files, a CLI, and logs expose the same behavior with less infrastructure.

## Paper-trading behavior

### Local simulation only

The minimum loop is a historical replay over the frozen final holdout using the selected model artifact. It is not a live feed and does not send an order to Alpaca or any other brokerage.

Replay is chronological over every scheduled XNYS session as `open → close`; the weekly decision branch is anchored to the last valid session close of each calendar week and emits a deterministic logical decision event at that close after the complete historical snapshot is validated under the fixed close-availability convention. `retrieved_at`/`generated_at` are provenance wall-clock fields only; they never alter replay order or admit later data.

1. load the data snapshot whose manifest hash matches the model contract;
2. at the scheduled open timestamp, if a pending target exists, validate all 30 entry bars; if any is missing, cancel that target before fills, emit no partial order/cost, preserve cash/positions, and log the entry-skip; otherwise fill deterministic six-decimal-share entries from the `label_fill_stream` adjusted IEX daily-bar open proxy using `entry_budget= NAV/(1+c)` and apply entry fees/slippage;
3. at the scheduled close timestamp, validate a close bar for every currently held symbol (cash-only marks require no symbol bar); if any required close bar is missing, fail closed without fabricated values; if an active vintage reaches its fifth valid session close, submit deterministic `label_fill_stream` adjusted IEX daily-bar close-proxy exit fills, charge exit cost, set positions to zero, and update cash;
4. emit the non-mutating valuation mark after the update from the same `label_fill_stream` adjusted IEX daily-bar close proxy, and derive the week-end NAV state at the last scheduled close of every calendar week, including cash-only and calendar-overlap-skip weeks;
5. if this close is not a weekly decision close, continue to the next scheduled open;
6. assert every price feature row has `bar_end_at <= feature_cutoff_at`, every SEC fact has accepted/filed time no later than that cutoff, and the complete snapshot passed validation under the fixed historical close-availability convention; no later bar or filing is admitted by retrieval time;
7. if a current decision bar is missing, skip only the new decision before ranking or ordering, preserve the state produced by any due exit/mark events, emit no partial new order or cost, and log every missing symbol;
8. score the fixed 30-symbol basket;
9. select the top 10 by predicted score descending, then ticker ascending, and target nominal equal 10% weights from the cost-inclusive entry budget, respecting the 100% gross-long cap and retaining residual cash;
10. consult the frozen `exchange_calendars==4.13.2` XNYS schedule and active vintage: if the next entry timestamp is on or before the active vintage's fifth-session close timestamp, skip this paper rebalance, carry the active positions through that close, emit no order or cost, and log the calendar-overlap skip; otherwise schedule deterministic entry orders for the next valid timestamp. The schedule supplies ordering timestamps; IEX daily-bar OHLC supply the explicitly feed-limited price proxies.
11. write the decision/skip event now; write the separate vintage-summary row with `label_end` when that vintage reaches its fifth-session exit.

The output is a position-and-execution ledger. Any P&L-like series is explicitly synthetic historical simulation and includes all costs, slippage, calendar assumptions, risk limits, and metrics from [experimental proof](experimental-proof.md). No output uses words such as “guaranteed,” “safe,” or “investment advice.”

The simulator uses two contract streams: `feature_stream` with `feed=iex`, `adjustment=split` for features only, and `label_fill_stream` with `feed=iex`, `adjustment=all` for every simulator price—entry, mark, and exit—at `asof=2025-12-31`. Split, cash-dividend, and spin-off adjustments are therefore embedded only in the explicitly synthetic label/fill proxy; features use split-invariant formulas and never consume this stream. Every simulator price is a research proxy, not an official XNYS auction quote or literal historical executable quote, and no separate dividend ledger is added.

### Required structured log fields

Each JSONL event includes:

- `run_id`, `event_id`, `contract_version`, and `code_commit`;
- `event_at` in UTC plus source timezone is the deterministic logical replay timestamp, with monotonic `event_seq` within a run; `decision_at` is the scheduled `feature_cutoff_at`, `decision_event_at` is the logical decision event at that close, and `execution_at`/`label_end` are nullable and event-specific (`label_end` is populated only on vintage-summary rows); `retrieved_at` and `generated_at` are wall-clock provenance fields, not causal inputs;
- `data_manifest_hash`, `model_artifact_hash`, and feature-schema hash;
- symbol, score, rank, target weight, previous weight, and order quantity;
- simulated fill price, fee, slippage, turnover, cash, NAV, gross exposure, entry budget, and residual cash;
- event type (`decision`, `order`, `fill`, `exit`, `mark`, `skip`, `error`, `summary`); and
- error code and remediation text when the loop fails closed.

A deterministic replay with the same manifest, model artifact, seed, and command must produce byte-equivalent JSONL events and summary files, ordered by `event_seq`, apart from explicitly excluded wall-clock provenance fields (`retrieved_at`, `generated_at`);
The same-timestamp ordering is part of the contract: the post-exit mark includes the fee and has zero exposure, while the decision schedules only a following-session entry.

### Failure behavior

The loop fails closed—no simulated order is emitted for the affected decision—when any of these occurs:

- data manifest or model hash mismatch;
- a feature timestamp is after the decision cutoff;
- a missing or duplicate OHLC bar violates the contract;
- an SEC fact has no unambiguous accepted timestamp/unit;
- the model artifact cannot be loaded or its feature schema differs;
- the execution session is absent; or
- an order would exceed the no-leverage, 10%-per-symbol, or 100%-gross limits.

Every skip/error is logged and counted in the report. Silent fallback, forward-filling across a closure, or using the previous model without a hash match is prohibited.

## Minimum production boundary

Build only what demonstrates the target role's packaging, testing, data, model, and operational judgment:

- a normal Python package with pinned direct dependencies and a lock/constraints file;
- a small module layout separating `data`, `features`, `labels`, `models`, `evaluation`, `paper`, and `cli` without speculative plugin interfaces;
- reproducible CLI entry points: `data-build`, `train`, `evaluate`, `paper-run`, and `report`;
- focused tests for as-of joins, feature cutoff, future-split feature invariance, label formula, temporal purge/embargo, IEX proxy selection, cost accounting, position caps, fail-closed behavior, and deterministic replay;
- one CI job running the focused tests and a smoke command on synthetic fixtures;
- structured logs and immutable run manifests; and
- a short report generated from committed configuration and run artifacts.

No API server, database, cloud deployment, MLOps platform, message queue, dashboard, broker connector, live scheduler, or agent framework is required. A local command and JSONL logs expose the observable behavior the reviewer needs. Add infrastructure only if a completed minimum package demonstrates a specific role signal that the simpler boundary cannot show.

## Ownership boundary

| Artifact | Candidate-owned claim | Reused/dependency boundary |
|---|---|---|
| Problem/data contract | Financial decision, 30-symbol universe, timing, target, benchmark, and non-goals | Role rubric and cited papers inform decisions; they are not candidate code |
| Raw-data build | Request parameters, schema checks, hashes, as-of SEC joins, corporate-action checks, and manifests | Alpaca/SEC services, their terms, and raw data remain external/reused |
| Features and labels | All transformations, formulas, and tests | pandas/NumPy/scikit-learn are dependencies |
| Models and evaluation | Baselines, training/evaluation loops, temporal splitter, metrics, uncertainty, negative results | Model libraries and cited literature remain reused |
| Simulator | Portfolio constraints, fill timing, costs/slippage, logs, failure behavior | No Vibe-Trading engine or broker connector is imported |
| Presentation | Report, limitations, diagnosis, reproducibility instructions, and recruiter/interview narrative | Vibe-Trading and Packt are named as reference/learning sources only |

The **reference repository** verdict is **reference only**: Vibe-Trading's PIT and cost patterns may be studied and independently reimplemented, but no code, Alpha Zoo output, data output, or agent framework crosses the ownership boundary. Packt's notebooks remain a learning source, not candidate-owned hiring evidence.

## Dependency-ordered implementation sequence

### Phase 0 — Freeze problem and evidence contract

**Work:** commit [selected project and ML/data contract](selected-project-contract.md), [experimental proof](experimental-proof.md), and this reviewer journey before downloading data or fitting models.

**Learning prerequisite:** read the cited Gu–Kelly–Xiu paper, the scikit-learn temporal-split documentation, the Alpaca data-use clause, and SEC as-of fields. Write a one-page decision glossary; do not start a general finance curriculum.

**Acceptance evidence:** the repository names one project, one universe, one target, one benchmark, one validation family, one paper boundary, and one ownership boundary; a reviewer cannot find an unresolved choice in these fields.

**Stop condition:** if any contract field is still a choice, stop here. Do not acquire data or add a model.

### Phase 1 — Build and verify the data corpus

**Work:** implement the Alpaca daily-bar fetcher and SEC submissions/XBRL fetcher; normalize timestamps; write manifests, checksums, schema checks, corporate-action checks, and filed-time as-of joins; create small synthetic fixtures.

**Learning prerequisite:** only the pandas time-indexing, timezone, HTTP retry/rate-limit, and SEC XBRL fields needed by the fixture. Stop studying when the fixture proves the join.

**Acceptance evidence:** a clean environment rebuilds the same source manifest; tests fail on period-end joins, future timestamps, duplicate bars, malformed OHLC, and raw-data hash changes; no raw licensed market-data dump is committed.

**Stop condition:** no baseline or feature expansion until the timing/data checks pass and the source terms are recorded.

### Phase 2 — Establish baselines and controlled experiments

**Work:** implement B0 constant-zero, B1 momentum, B2 ElasticNet, and M1 HistGradientBoosting with the fixed feature-group ablations and temporal folds.

**Learning prerequisite:** scikit-learn pipelines, regularization, tree depth/learning rate, rank IC, and the stated metrics. No deep-learning framework is required.

**Acceptance evidence:** the experiment index contains reproducible configs, seeds, hashes, fold dates, row counts, baseline/model metrics, and at least one model/feature group that does not improve. The final holdout remains unopened.

**Stop condition:** freeze the model family and configuration only after the development walk-forward and negative-result report are complete; never widen the grid to rescue a weak result.

### Phase 3 — Diagnose and challenge the result

**Work:** run the predeclared period/regime/cost/universe/missingness checks; investigate one actual performance failure using the symptom→hypotheses→root-cause→fix→before/after template.

**Learning prerequisite:** corporate-action and survivorship concepts, temporal leakage, turnover/cost accounting, and the difference between forecast quality and portfolio return. No open-ended course list.

**Acceptance evidence:** the final holdout is evaluated once; robustness tables and uncertainty intervals exist; one diagnosis is backed by raw data/code evidence; limitations name the fixed-basket and licensed-data boundaries.

**Stop condition:** if the failure cannot be isolated honestly, publish it as unresolved and do not add model complexity or a dashboard.

### Phase 4 — Package the evidence

**Work:** turn the tested modules into a package and CLI, pin dependencies, add focused CI, write run manifests and a report command.

**Learning prerequisite:** Python packaging, pytest assertions, structured logging, and basic CI syntax only as needed to ship the package.

**Acceptance evidence:** a clean checkout runs the synthetic smoke path; the CLI fails clearly on missing credentials/schema/hash mismatch; tests cover the money/timing boundaries; the report is generated from artifacts rather than hand-edited numbers.

**Stop condition:** no paper run until package installation, smoke path, and focused CI pass.

### Phase 5 — Run the local paper-trading demo

**Work:** replay the frozen final holdout with the development-frozen selected model artifact (B1 only when no fitted candidate passed the development choice rule); generate deterministic weekly decision/order/fill/position/cost logs; inject one controlled missing-data or hash-mismatch failure to demonstrate fail-closed behavior.

**Learning prerequisite:** none beyond the contract; do not add broker SDKs or live credentials.

**Acceptance evidence:** a reviewer can run one command and inspect the full ledger, summary metrics, skipped/error events, and byte-equivalent rerun result. The run is clearly marked historical paper trading with no capital.

**Stop condition:** the minimum project is complete here. Optional enhancements cannot block publication.

### Phase 6 — Publish the portfolio and interview evidence

**Work:** publish the recruiter card, technical report, source/license ledger, limitations, reproducibility command, and a short list of numbers to re-derive live. Publish a diagnosis narrative only when its own primary run artifacts exist; otherwise state the scope of regression evidence without inventing an incident.

**Learning prerequisite:** rehearse actual choices and evidence boundaries; no claim is memorized without a derivation path.

**Acceptance evidence:** a non-specialist can identify the problem, ownership, target-role relevance, and honest outcome in one page; a technical interviewer can trace data timing, baseline, model, validation, limitations, production tradeoff, and rejected alternatives.

**Stop condition:** stop after the minimum credible evidence package is complete and reviewed. Do not add a dashboard, API, cloud deployment, agent, TensorFlow, PyTorch, live broker, or profitability claim for appearance.

## Optional enhancements, only after the stop gate

None is required for the target role evidence. If the minimum package is already complete, the only defensible additions are:

- a pre-registered sector-neutral ranking ablation using a clearly licensed sector source;
- a longer unattended **local** replay with injected data-feed failures; or
- a second literature-grounded model comparison if a measured limitation remains.

An agent layer, Vibe-Trading component, dashboard, API, cloud deployment, deep model, and live brokerage integration remain out of scope unless a later, separately approved brief proves a unique hiring signal and reopens the data/legal contract.
