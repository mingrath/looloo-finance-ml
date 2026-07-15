# Build brief: point-in-time equity return ranker

**Status:** implemented; canonical decision and delivery contract.

This is the single canonical **build brief** for one candidate-owned **portfolio project** aimed at producing verifiable **hiring evidence** for the **target role**. Detailed research stays in linked assets; this brief fixes the decisions an implementing agent must not invent.

## Executive decision

Build **a point-in-time cross-sectional U.S. equity return ranker with a local paper-trading simulator**.

At the scheduled close of the last valid XNYS session each week, the project scores a fixed 30-symbol basket for five-session excess return, goes long the top 10 at nominal equal 10% targets from a cost-inclusive entry budget (all other symbols unheld; residual cash from costs and six-decimal share rounding retained; whole-decision and calendar-overlap skips carry the prior active ledger state), exits each vintage at the fifth valid session close timestamp using a deterministic fill from the `label_fill_stream` adjusted IEX daily-bar close proxy, charges exit cost, sets positions to zero, and records a no-capital simulated position/order/cost ledger. The next eligible weekly signal schedules entry at the following valid session timestamp and uses that session's adjusted IEX daily-bar open proxy. The project is historical research plus a **paper-trading demo**. It is not live trading, investment advice, a broker integration, or a profitability promise.

**Final Vibe-Trading verdict: reference only.** Study its point-in-time joins, fee-schedule structure, run-card idea, and sandboxing patterns; import no Vibe-Trading code, data output, Alpha Zoo, or agent framework. The evidence is in the [Vibe-Trading audit](assets/vibe-trading-audit.md).

## Why this project wins

The comparison scored four feasible directions against the existing eight-criterion rubric:

| Direction | Agentic? | Score / 100 | Decision-relevant tradeoff |
|---|---:|---:|---|
| Cross-sectional equity return ranking | No | **81** | Richest candidate-owned panel modeling, ranking, feature ablation, and experimentation surface |
| Realized-volatility forecasting and vol-targeted sizing | No | 78 | Clean data/PIT story, but narrower modeling surface |
| Treasury yield-curve forecasting and duration positioning | No | 78 | Lowest completion risk and strongest open-data story, but low-dimensional and less direct equity-ranking evidence |
| Filing-triggered earnings-drift agent | Yes, bounded | 66 | Candidate-trained model is real, but orchestration adds failure surface without enough extra rubric evidence |

Source and score rationales: [project-direction-comparison.md](assets/project-direction-comparison.md). The weights remain 12 + 14 + 18 + 14 + 10 + 16 + 8 + 8 = **100**.

**Runner-up:** Treasury yield-curve forecasting and duration positioning. D2 and D3 tie at 78; D3 takes the runner-up slot because its core government-data signal has safer reuse and fewer moving parts after their modeling/ownership evidence ties. D1 wins **outright** at 81, with stronger ML **hiring evidence** from the richer cross-sectional feature, ablation, ranking, and diagnosis surface. The approved tie-break order is used only to break the D2/D3 runner-up tie. This is a decision, not an unresolved menu.

## Target role and evidence boundary

- **Target role:** Looloo’s *Machine Learning Engineer (Project Algorithmic Trading)*, official listing [`job/41674`](https://careers.loolootech.com/job/41674). The page labels it **Junior Level** and shows **1 - 3 Years** in structured metadata. Its prose separately says “At least 1-2 years of experience in creating AI models”; both facts remain visible rather than being reconciled by inference.
- Looloo’s application-process page documents a 90-minute programming assessment and a deeper live-proctored programming/ML review with senior-programmer follow-up: [`application-process`](https://careers.loolootech.com/application-process).
- Portfolio and transcript are optional supporting documents, and Looloo encourages applicants without related work experience to apply. Those facts mean the project should reduce uncertainty about ability, not impersonate a credential.
- Looloo’s public About page presents a general AI/data consultancy with predictive-analytics work. No public source verifies a proprietary trading team, strategy, data, model, or infrastructure: [`about-us`](https://loolootech.com/about-us/).
- Score directions with the [100-point Looloo project-evidence rubric](assets/looloo-project-evidence-rubric.md). Related degree and professional tenure stay outside that score. The applicant’s exact experience range is unknown.

## Fixed project contract

The full contract is [selected-project-contract.md](assets/selected-project-contract.md). The non-negotiable fields are summarized here.

### Financial decision

- Decision: weekly long-only top-tercile selection from the fixed basket.
- Position: top 10 symbols at nominal equal 10% targets from the cost-inclusive entry budget; all other symbols unheld; residual cash from entry costs and six-decimal share rounding is retained; eligible gross notional never exceeds 100% of NAV; calendar-overlap skips carry the active vintage through its fifth-session close; no leverage, shorting, options, or borrow assumptions.
- Signal: predicted next-five-session excess return; long-short spread is an offline diagnostic only, not the paper portfolio.
- **Execution:** signal at the scheduled close timestamp of the last valid XNYS session in the week; inspect only decision/entry bars; use the `label_fill_stream` adjusted IEX daily-bar open proxy for the scheduled next valid session timestamp unless the calendar-overlap rule skips the rebalance; use the same stream's adjusted IEX daily-bar close proxy for the fifth-session exit, charge the same one-way cost, set positions to zero, then schedule the next eligible weekly target. The XNYS calendar supplies ordering timestamps, not official auction prices; IEX OHLC are feed-limited research proxies.

### Universe, dates, and labels

The exact committed basket is:

`AAPL, AMD, ABBV, AMZN, BAC, CAT, CSCO, CVX, DIS, GOOGL, HD, IBM, JNJ, JPM, KO, MA, META, MRK, MSFT, NFLX, NKE, NVDA, ORCL, PEP, PG, TMO, UNH, V, WMT, XOM`

Sample: 2021-01-04 through 2025-12-31, complete U.S. regular-session observations only. A decision date is retained for learning only if required future open/close prices exist for all 30 symbols; otherwise the date and missing symbols are logged and dropped.

For symbol $i$ on decision date $t$:

- $r_i(t)=\log(\operatorname{close}_{i,t+5}/\operatorname{open}_{i,t+1})$;
- $r_{basket}(t)$ is the equal-weight mean of those 30 symbol returns; and
- $y_i(t)=r_i(t)-r_{basket}(t)$.

The model regresses $y_i(t)$ and ranks predictions cross-sectionally. Sort scores descending then ticker ascending for the top 10; use average ranks only for Spearman metrics. B0 remains the equal-weight no-signal portfolio comparator and does not use the top-10 tie-break. A 20-session momentum rank is the fixed non-ML baseline. The fixed basket carries survivorship limitations; the project must disclose and sensitivity-test them, never claim a survivorship-free index study.

### Data and point-in-time semantics

- **Prices/volume:** Request two separately hashed Alpaca daily-bar streams with frozen `feed=iex`, `asof=2025-12-31`, `currency=USD`, `timeframe=1Day`, ascending order, explicit dates, and complete pagination: `feature_stream` uses `adjustment=split` for price/volume features only; `label_fill_stream` uses `adjustment=all` for future labels and every simulator price (entry, mark, and exit) only. `asof` fixes symbol/entity mapping, not an adjustment-vintage cutoff. Feature formulas are invariant to later split back-adjustment and must pass a future-split mutation fixture. The `adjustment=all` simulator prices are research proxies, not literal executable historical quotes. The official schema is [`stockbars`](https://docs.alpaca.markets/reference/stockbars).
- **Frozen feature dictionary:** the selected contract fixes every price/volume formula and window, SEC tag priority and period-matching rule, unit/normalization, minimum history, missingness behavior, fold-only preprocessing, and the `2018-01-01` warm-up fetch boundary; no feature may be added or redefined without a contract change.
- **Accounting:** SEC submissions and XBRL `companyfacts`/`companyconcept` APIs. An accounting fact becomes visible at its filed/accepted timestamp, never at fiscal period end. Accession, taxonomy, unit, frame/period, filed time, and source URL are retained.
- **Price-data rights:** Alpaca’s [Customer Agreement §23](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf) restricts reproduction, distribution, sale, and commercial exploitation of market data without written consent. Raw Alpaca bars stay out of the public repository; the project ships a fetcher, schema, request manifest, response hashes, terms snapshot, and synthetic fixtures. A reviewer supplies permitted access. If terms do not permit the intended demonstration, stop and replace the source through a separately approved contract change.
- **SEC rights/operations:** use the [EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and [developer resources](https://www.sec.gov/about/developer-resources), identify the client with a descriptive User-Agent, obey rate limits, and preserve attribution. SEC site information is treated as public government data under the cited SEC policy; no SEC endorsement is implied.
- **Schema/failure policy:** duplicate timestamps, malformed OHLC, non-positive prices, ambiguous units/timestamps, unverified corporate-action handling, missing response pages, or changed schemas fail closed and are logged. If any of the 30 symbols lacks a current decision or execution bar, drop/skip the entire decision date before ranking or ordering, carry the prior ledger state unchanged, and log every missing symbol; never partially rebalance or forward-fill. If the next entry open is on or before an active vintage's fifth-session close, apply the deterministic calendar-overlap skip, carry the active vintage through that close, emit no order/cost, and log the skip. If a fifth-session close is later unavailable, fail closed without fabricating a price, cost, or return. No future value is forward-filled into the past.
- **Session source:** freeze `exchange_calendars==4.13.2` with calendar `XNYS`; use each scheduled session's actual open/close timestamps, including early closes. Bars validate expected sessions but never define holidays or mask outages.
- **Execution-stage semantics:** current decision-bar absence skips only the new ranking/order; a pending entry-bar absence cancels that next-open target before any fill; due exit and close-mark events still follow the deterministic ordering above, and no partial order/cost is emitted.

### Model boundary

1. B0: constant-zero excess-return score; equal-weight basket is the matching no-signal portfolio comparator.
2. B1: 20-session momentum rank.
3. B2: ElasticNet with fold-only scaling/imputation; exact nine-config grid.
4. M1: HistGradientBoostingRegressor; exact four-config shallow grid.

The project uses Python, pandas/NumPy, and scikit-learn. TensorFlow/PyTorch is not warranted for this small tabular panel and is not required as decorative evidence. No agent layer, custom architecture, reinforcement learning, AutoML, or unconstrained search enters the minimum project.

## Experimental and backtest proof

The full fixed protocol is [experimental-proof.md](assets/experimental-proof.md). Its key gates:

- Development dates: 2021–2024; final holdout: 2025, opened once after the model choice is frozen.
- Expanding walk-forward folds: minimum 52 training weeks, 13-week validation window, one-week embargo, advance 13 weeks. Purge any interval-overlapping training row.
- Development→holdout seam: final-fit rows must have `label_end < holdout_start` and `decision_at < embargo_start` (the prior scheduled weekly decision); log both predicates and reject the 2024-12-27 row whose label ends 2025-01-06.
- Fold-only preprocessing: training-fold medians and missingness indicators; features over 30% missing in a fold are dropped for that fold and recorded; labels are never imputed.
- Exact model grids, seeds, minimum-row failure, and promotion rule are fixed in the protocol. Select and freeze the development winner before viewing the final holdout; if no fitted candidate passes development, freeze B1 as the paper signal. Evaluate that frozen choice once on 2025 and report any holdout gate failure as a negative result—never fall back to B1 or shop another candidate after seeing the holdout.
- Metrics: weekly cross-sectional rank IC, IC distribution/IR, MAE/RMSE, top-tercile excess return, session-close NAV marks, calendar-week arithmetic returns including cash/skip weeks, gross/net simulated ledger, turnover, exposure, cost drag, Sharpe/Sortino conventions, maximum drawdown, and weekly hit rate; exact denominators, gross-shadow construction, zero-week treatment, and formulas are fixed in [experimental proof](assets/experimental-proof.md).
- Uncertainty: exactly 2,000 four-week block-bootstrap resamples, seed `20250713`, plus per-fold ranges and cost sensitivity.
- Robustness: 2021–2022, 2023–2024, and 2025 slices; training-fold-defined low/high volatility; full basket versus a pre-registered ≥95%-complete-history subset; missingness, corporate-action, and cost sensitivity.
- **Correctness checks:** future-row mutation, feature cutoff assertions, SEC filed-time joins, future-split feature-invariance mutation, scheduled-XNYS-open execution, per-close non-mutating NAV marks, fifth-session deterministic exit fills and costs, calendar-overlap skips, score-tie ordering, development→holdout label-end seam, purge/embargo intervals, survivorship disclosure, OHLC/schema/checksum tests, deterministic replay, and fail-closed errors.
- P&L-like diagnostics use the `label_fill_stream` adjusted IEX daily-bar open/close proxies with explicit 1 bp fee + 5 bp slippage baseline and 0/3/6/12 bp sensitivity. The XNYS schedule supplies timestamps and ordering, not auction prices; no cost-free result is reported as evidence and no return is promised.
* A prior rank-IC diagnostic cannot be presented as observed until its original run record is recovered. The focused regression test preserves the fixed behavior; a future observed failure must document symptom → hypotheses → isolation → root cause → minimal fix → before/after → residual limitation from its own primary artifacts.

## Reviewer and paper-trading boundary

The complete reviewer journey and sequence are [paper-trading-reviewer-experience.md](assets/paper-trading-reviewer-experience.md). The minimum reviewer path is:

1. recruiter card and one-page problem/ownership summary;
2. data manifest, source/license ledger, and timing contract;
3. baseline/model experiment report with negative results;
4. limitations and explicitly scoped regression evidence;
5. packaged CLI and focused tests;
6. deterministic local `paper-run` replay over the frozen holdout; and
7. technical interview trace from any number to its manifest, formula, fold, or log.

The local simulator creates decisions, orders, fills, positions, cash, turnover, costs, and structured JSONL events. It sends no brokerage orders and needs no live credentials. Every simulator price—entry, mark, and exit—comes from the same `label_fill_stream` adjusted IEX daily-bar proxy; `feature_stream` is split-only and never supplies simulator prices. A missing current decision/entry symbol causes a whole-decision skip with prior ledger state unchanged and no partial order/cost. A calendar-overlap skip carries the active vintage through its fifth-session close and logs the reason; each eligible vintage then receives a deterministic costed exit proxy at that close, sets positions to zero, and a missing exit bar fails closed without fabricated values. It also fails closed on hash mismatch, future timestamps, malformed data, model-schema mismatch, or risk-limit violations. Logical replay timestamps and `event_seq` determine ordering; `retrieved_at`/`generated_at` wall-clock provenance is excluded from byte-equivalence.
- **Capital contract:** synthetic starting `NAV=USD 100,000`; selected one-way cost `c`; `entry_budget= NAV/(1+c)`; equal nominal 10% targets; six-decimal shares floored using the scheduled entry session's `label_fill_stream` adjusted IEX daily-bar open proxy; residual cash retained; post-fill cash ≥ 0 and gross notional ≤ NAV.
- **Valuation ledger:** emit non-mutating NAV/exposure marks from the `label_fill_stream` adjusted IEX daily-bar close proxy at every scheduled XNYS session close timestamp, derive a week-end NAV at the last scheduled close of every calendar week including cash/skip weeks, and keep `label_end` only on the vintage-summary row.
- **Same-close/open ordering:** at a scheduled open timestamp, validate all 30 pending-entry bars then fill or cancel using the `label_fill_stream` open proxy before any close mark; at a close timestamp, process `exit fill/cost → cash/position update → valuation mark/week-end state → decision score or skip event → next-session entry scheduling` using the same stream's close proxy. The XNYS calendar supplies ordering timestamps, not official auction prices; IEX OHLC are feed-limited research proxies; the post-exit mark includes the fee and has zero exposure.
- **Event schema:** every JSONL event has deterministic logical UTC/source-timezone `event_at` and monotonic `event_seq`; `decision_at` is `feature_cutoff_at`, `decision_event_at` is the logical decision event at that close, and `execution_at`/`label_end` are nullable/event-specific, with `label_end` only on vintage summaries. `retrieved_at`/`generated_at` are wall-clock provenance fields excluded from causal ordering and byte-equivalence; replay compares the `event_seq`-ordered stream.

### Minimum production boundary

- normal Python package with pinned dependencies and a lock/constraints file;
- CLI commands: `data-build`, `train`, `evaluate`, `paper-run`, `report`;
- focused tests for timing, labels, as-of joins, purge/embargo, costs, caps, failure behavior, and deterministic replay;
- one CI smoke path on synthetic fixtures;
- structured logs and immutable run manifests.

### Thai execution boundary

Webull Thailand OpenAPI is retained as a future, separately approved **own-account execution integration** for a Thai-facing product. It is not a `finance-ml-v1` research-data replacement and this project remains local paper trading only. Its documented forward-adjusted daily bars do not satisfy the contract's distinct split-adjusted feature and all-adjusted label/fill streams. Before any execution implementation, approve current Webull terms and account eligibility, account/authorization model, sandbox validation, risk limits, idempotent orders, kill switch, reconciliation, audit trail, secret isolation, and Thai compliance review.

No dashboard, API service, cloud deployment, database, MLOps platform, broker connector, live scheduler, or agent framework is justified by the current hiring evidence. Add none before the minimum package passes.

## Candidate ownership

| Candidate-authored | Reused/reference-only |
|---|---|
| Problem framing, fixed universe, data manifests, as-of joins, features, labels, baselines, model/evaluation code, temporal splitter, costs, simulator, tests, diagnosis, packaging, logs, report, limitations, and final claims | Alpaca/SEC services and terms; Python/pandas/NumPy/scikit-learn; cited papers and formulas; standard libraries |
| Local paper-trading replay and fail-closed behavior | Vibe-Trading: **reference only**; Packt ML4T: learning source only, never candidate-owned hiring evidence |

The project must not claim upstream repository work, vendor data, pretrained models, or tutorials as applicant-owned.

## Dependency-ordered implementation sequence

| Phase | Deliverable and learning prerequisite | Acceptance evidence | Stop condition |
|---|---|---|---|
| 0. Freeze contract | Commit the selected contract, proof protocol, reviewer journey; read only the cited ML/timing/data-rights sources | One project, target, data source, validation family, paper boundary, and ownership boundary with no unresolved choice | No data acquisition until every contract field is fixed |
| 1. Build data corpus | Implement Alpaca/SEC fetchers, separate feature/label-fill manifests and hashes, schemas, split-invariance/corporate-action checks, filed-time joins; learn only needed pandas/timezone/SEC fields | Clean rebuild and failing timing/schema/future-split fixtures; no raw licensed dump | No model until timing/data tests pass |
| 2. Run baselines/experiments | Implement B0/B1/B2/M1 and fixed ablations/folds; learn only needed scikit-learn pipelines and metrics | Reproducible experiment index, negative result, untouched holdout | Freeze model choice without widening the grid |
| 3. Diagnose/robustness | Run predeclared slices/cost checks; retain regression evidence; investigate an observed failure only when its primary artifacts exist | Holdout once, uncertainty/robustness tables, honest limitations | Do not add complexity to hide an unresolved failure |
| 4. Package evidence | Package modules/CLI, pin dependencies, focused tests/CI, manifest-backed report | Clean synthetic smoke run; fail-closed checks; generated report | No paper run until package and tests pass |
| 5. Run local paper demo | Replay holdout with frozen artifact; inject one controlled failure; learn nothing beyond the contract | Complete deterministic ledger, logs, summaries, and failure evidence | Minimum project is complete here |
| 6. Publish/interview | Recruiter card, technical report, sources/licenses, limitations, reproducibility command, live-number sheet | Recruiter sees problem/ownership/relevance; interviewer can derive decisions and numbers | Stop; optional additions cannot delay the minimum package |

Optional enhancements after completion only: a pre-registered sector-neutral ablation with a licensed source, longer local replay with injected feed failures, or a second literature-grounded model if a measured limitation remains. An agent, dashboard, cloud/API layer, deep model, Vibe-Trading component, or live brokerage integration is not an enhancement for this build brief.

## Recruiter narrative

Use this only after the future implementation produces actual results:

> I built a reproducible Finance ML pipeline that ranks a fixed U.S. equity universe for five-session excess returns using split-invariant market features and point-in-time SEC filing data. I compared a no-signal control, momentum, ElasticNet, and a shallow tree model with leakage-safe temporal validation, cost-aware local paper trading from explicitly feed-limited IEX daily-bar proxies, and a focused regression check. I owned the data contract, model/evaluation code, simulator, packaging, tests, and evidence; Alpaca/SEC data and external repositories remain attributed dependencies. The honest result is the reproduced evidence—including any weak or negative return—not a profitability claim.

Do not say the project replaces a degree, proves professional tenure, or represents Looloo’s internal trading system.

## Technical-interview proof sheet

The candidate must be able to derive or reproduce these without opening an unexplained notebook:

- why ranking five-session excess return is a real decision and why momentum is the baseline;
- why the 30-symbol universe is fixed, what survivorship it leaves, and why it is disclosed;
- the two-stream Alpaca contract: `feature_stream` uses `adjustment=split` and split-invariant formulas, while `label_fill_stream` uses `adjustment=all` for every simulator entry, mark, and exit price; `asof=2025-12-31` fixes symbol mapping rather than corporate-action vintage;
- why SEC filed/accepted timestamps, not fiscal period ends, control feature visibility;
- why the scheduled XNYS weekly-close signal uses a logical close timestamp, the next valid session's IEX daily-bar open proxy, and the calendar's actual early-close timestamp;
- exact development/holdout dates, 52/13/gap-1 folds, purge counts, and minimum-row failure;
- the exact ElasticNet/HGB grids, fold-only imputation, promotion thresholds, seed, and why TensorFlow/PyTorch were rejected;
- the rank-IC regression behavior and why no unverified historical failure is claimed;
- how cost-inclusive sizing, six-decimal share rounding, residual cash, turnover, costs, exposure, risk metrics, and drawdown are computed;
- why a local simulator/CLI/log is sufficient evidence and a dashboard/API/cloud/agent is not; and
- the 30-symbol list, feature-group counts, experiment count, IC distribution, cost drag, and all reported numbers from the final run manifest.

Rejected alternatives are part of the proof: D3 was the runner-up, D2 tied it but had a different complexity/data profile, D4’s agent layer did not earn its cost, direct Vibe-Trading reuse would obscure ownership, Packt is learning material, Yahoo/yfinance was excluded for terms ambiguity, and deep learning was not warranted by the selected data/model boundary.

## Limitations, unknowns, and claim discipline

- `[APPLICANT CONSTRAINT]` The applicant has a non-technical degree background and independently capable classical-ML baseline; persistence, creativity, initiative, ownership, and completed evidence are the differentiators. Exact professional-experience eligibility is unknown.
- `[EXPLICIT]` The listing’s Junior Level/1–3 Years metadata and 1–2-years preferred-prose discrepancy are both retained. The project cannot substitute for either a degree or tenure.
- `[INFERENCE]` The selected project is likely more useful to an ML hiring manager than a polished agent demo because it exposes candidate-owned data, timing, modeling, experiments, diagnosis, and packaging; the hiring outcome is not guaranteed.
- `[UNKNOWN]` Looloo’s internal trading team, data, models, infrastructure, and strategy are not public and are not inferred.
- `[REUSED WORK]` Alpaca market data is licensed and non-redistributable under the cited agreement; SEC data, libraries, formulas, papers, and repository patterns remain attributed external work.
- The fixed basket has survivorship bias; the five-year sample may not generalize; the adjusted IEX fill/mark proxy is not an official XNYS auction quote or literal executable quote and has limited feed coverage; no live feed, broker, shorting, borrow, financing, tax, or real-money behavior is tested; and no result guarantees future returns.

## Whole-document acceptance review

This **build brief** passes its single acceptance seam when reviewed as a whole:

- one and only one **portfolio project** is selected;
- the runner-up and decisive tradeoff are recorded without reopening selection;
- one final Vibe-Trading verdict is **reference only**;
- the project, target, universe, dates, labels, inputs, timing, benchmark, models, validation, metrics, paper boundary, reviewer journey, and evidence floor are fixed;
- all four comparison directions use the same eight weighted criteria and totals are arithmetically transparent;
- data provenance, schema, cadence, point-in-time semantics, and reuse obligations are explicit;
- implementation phases have observable acceptance evidence and stop conditions;
- recruiter and technical-interview narratives do not claim results that do not yet exist;
- role metadata, credential limits, applicant constraints, source facts, inference, reused work, and unknowns are distinguished; and
- no live trading, proprietary Looloo-internal claim, credential-substitution claim, or guaranteed-profit claim appears.

An implementing agent can begin without choosing the project, target, data source, validation family, evidence standard, paper-trading boundary, or reviewer journey. The next work after this brief is implementation—not another planning decision.

## Linked research and provenance

- [Looloo project-evidence rubric](assets/looloo-project-evidence-rubric.md)
- [Vibe-Trading audit](assets/vibe-trading-audit.md)
- [Four-direction project comparison](assets/project-direction-comparison.md)
- [Selected project/data contract](assets/selected-project-contract.md)
- [Experimental/backtest proof](assets/experimental-proof.md)
- [Paper-trading reviewer experience](assets/paper-trading-reviewer-experience.md)
- [PRD](PRD.md)
