# Selected portfolio project and ML/data contract

**Status:** decision-complete contract for the selected **portfolio project**; no project implementation is included.

## Decision

Build **a point-in-time cross-sectional U.S. equity return ranker with a local paper-trading simulator**.

At a fixed weekly decision time, the model scores a fixed basket of liquid U.S. equities for their next five-session **excess return**. The paper-trading demo goes long the top tercile with nominal equal 10% targets from a cost-inclusive investable budget (all other symbols are unheld; residual cash from costs and share rounding is reported) and records simulated orders, positions, costs, and performance. The project is historical research plus a no-capital paper-trading demo; it is not an investment product or a promise of returns.

This is one project, not a menu.

## Selection evidence

| Decision input | Result | Basis |
|---|---|---|
| Compared directions | D1 cross-sectional ranking: **81/100**; D2 realized-volatility forecasting: 78; D3 Treasury yield-curve forecasting: 78; D4 bounded filing-drift agent: 66 | [Project-direction comparison](project-direction-comparison.md), all scores are `[INFERENCE]` rubric applications |
| Runner-up | D3, Treasury yield-curve forecasting and duration positioning | D2 and D3 both score 78; D3 takes the runner-up slot because its core signal has safer government-data reuse and fewer moving parts, after their modeling and ownership evidence are tied |
| Decisive tradeoff | D1 wins **outright on the rubric total** (81 vs. 78), not by breaking a tie. Its 18/18 modeling ceiling and richer panel/ablation/diagnosis evidence outweigh D3’s cleaner data rights and lower completion risk. The approved tie-break order is used only to assign D3 over D2 among the tied 78-point runners-up. | Stronger ML hiring evidence → clearer ownership → safer data/evaluation → lower completion risk |
| **Vibe-Trading role** | **Reference only** | [Vibe-Trading audit](vibe-trading-audit.md) |
| Framework choice | Python + pandas/NumPy + scikit-learn; no TensorFlow or PyTorch in the minimum project | Small tabular panel; deep learning would be decorative unless a measured limitation later warrants it |

`[INFERENCE]` The score is an evidence ceiling, not a result. The applicant still has to build, test, and defend the artifacts. The runner-up is recorded to show judgment, not to reopen selection.

## 1. Financial decision

**Decision:** `feature_cutoff_at = decision_at` is the scheduled close of the last valid XNYS session in each calendar week (normally Friday; holiday and early-close weeks use the schedule's actual session). After the complete historical snapshot is validated, rank the 30-symbol basket using only price bars whose `bar_end_at ≤ feature_cutoff_at` and SEC facts whose accepted/filed time is no later than that cutoff. In replay, `decision_event_at` is a deterministic logical event timestamp tied to that scheduled close; `retrieved_at`/`generated_at` are provenance wall-clock fields and never admit later data or determine causal ordering. The logical availability convention treats a complete validated daily bar ending at the scheduled close as available for that close event; this is an explicit historical-replay convention, not a claim about contemporaneous vendor publication. At the next valid session timestamp:

1. target equal weights in the top 10 symbols (top tercile), nominally 10% each of the cost-inclusive investable budget;
2. leave all other symbols unheld; residual cash from costs and six-decimal share rounding remains cash, while a whole-decision skip carries the active ledger state unchanged except for any exit/mark events due at that close; a missing entry bar cancels the pending target before any fill, with no partial order or cost;
3. rebalance weekly; and
4. do not use leverage, margin, short sales, options, or unexplained fractional position sizing.

**Capital and rounding:** start the synthetic ledger at `NAV=USD 100,000`. For the selected one-way cost `c` (baseline `0.0006` = 1 bp fee plus 5 bp slippage), after any prior exit compute `entry_budget = NAV / (1 + c)`; target `entry_budget / 10` notional per selected symbol; at the scheduled next-session open timestamp, validate all 30 entry bars before any fill, floor shares to six decimal places using that session's `label_fill_stream` adjusted IEX daily-bar open proxy, charge `c` on actual entry notional, and leave the rounding residual in cash. Exit fills use that same `label_fill_stream` adjusted IEX daily-bar close proxy and cost `c`, then zero positions. The ledger must assert post-fill cash ≥ 0 and gross notional ≤ NAV; cost sensitivities use the same sizing rule with `c ∈ {0, 0.0003, 0.0006, 0.0012}`.

The model is evaluated as an asset-selection signal. A long-short top-versus-bottom spread is an offline diagnostic only; it is not the paper-trading portfolio.

**Why ML is warranted.** The decision is a repeated cross-sectional ranking problem with heterogeneous, interacting price and filing features. A fixed momentum rule is a meaningful baseline, while a regularized linear model and a shallow tree ensemble test whether nonlinear interactions add out-of-sample ranking information. This is a small supervised-learning problem, not a claim that a complex model is needed. Gu, Kelly, and Xiu's asset-pricing study is the literature anchor for comparing linear and tree/nonlinear methods, not a promise that its results transfer here: [NBER Working Paper 25398](https://www.nber.org/papers/w25398).

## 2. Asset universe and calendar

**Fixed universe (committed before experiments):**

`AAPL, AMD, ABBV, AMZN, BAC, CAT, CSCO, CVX, DIS, GOOGL, HD, IBM, JNJ, JPM, KO, MA, META, MRK, MSFT, NFLX, NKE, NVDA, ORCL, PEP, PG, TMO, UNH, V, WMT, XOM`

The list is an applicant-authored fixed universe, not a reconstructed historical index. It intentionally carries a survivorship limitation: symbols that disappeared before the sample are not represented. The project must disclose this limitation and test whether conclusions change when the least-history symbols are removed. It must not claim survivorship-free results.

**Sample:** 2021-01-04 through 2025-12-31, using complete U.S. regular-session observations only. The end date is fixed to the last completed calendar year so the published report is not silently revised by an in-progress year. The data manifest records any missing symbol/date rows rather than silently filling them.

**Calendar:** use the frozen `exchange_calendars==4.13.2` XNYS schedule as the authoritative U.S. regular-session calendar, preserving each session's scheduled open and close timestamps after timezone normalization. Sessions normally run 09:30–16:00 America/New_York but early-close sessions use their scheduled close (for example, 13:00); never substitute universal boundaries. Generate decision, entry, and fifth-session timestamps from that schedule; downloaded bars validate expected sessions but never define holidays. No weekend or calendar-closed date is a decision row. If any of the 30 symbols lacks a bar on an expected decision, entry, or fifth-session close, fail the relevant build/replay step closed, log every missing symbol, and never treat a data outage as a market closure or forward-fill through it.

## 3. Prediction contract

| Field | Fixed contract |
|---|---|
| Decision timestamp | Scheduled close of the last valid XNYS session in each calendar week (normally Friday; holiday and early-close weeks use the calendar's actual close) |
| Feature cutoff | The scheduled decision close; all price features use bars through `t` only |
| Execution timestamp | Scheduled open of the next valid XNYS session after `t`; the signal is shifted one bar before any fill is simulated |
| Horizon | Holding window is the five-session interval from the next valid session's open (`t+1`) through the close of the fifth valid session (`t+5`) |
| Per-symbol target | `r_i(t) = log(label_fill_stream.close_proxy[i,t+5] / label_fill_stream.open_proxy[i,t+1])`; `r_basket(t) = mean_{j in the fixed 30-symbol universe} r_j(t)`; `y(i,t) = r_i(t) - r_basket(t)`; both proxies are from the same adjusted IEX daily-bar stream |
| Learning task | Regression of the five-session excess return `y(i,t)`; predictions are ranked cross-sectionally on each decision date |
| Label policy | Retain a decision date only when the required `label_fill_stream` IEX daily-bar open/close proxies exist for all 30 symbols; otherwise drop the entire date and log the missing symbols. Never impute a future label. Overlapping daily labels are not used: only weekly decision rows are eligible. |
| Paper overlap policy | At a decision close, if the next valid entry open is on or before an active position's fifth-session close, skip the paper rebalance, carry the active vintage through that close, emit no order or cost, and log the calendar-overlap skip; the next eligible decision enters at its following valid open. This calendar rule uses only the exchange calendar and current ledger state, not future market bars. |
| Exit fill policy | At each eligible vintage's fifth valid session close timestamp, submit deterministic `label_fill_stream` adjusted IEX daily-bar close-proxy exit fills for every held symbol, charge the same one-way cost, and set those positions to zero. If the close proxy is unavailable, fail closed without fabricating a price, cost, or return. |
| Valuation mark policy | At a fifth-session close timestamp, process the exit fill and cost first using the same `label_fill_stream` close proxy, update cash and positions, then emit the valuation mark and week-end state; at every other scheduled XNYS close timestamp, emit a non-mutating mark from that stream. Marks never create orders or fills. Derive one week-end NAV at the last XNYS close of every calendar week, including cash-only and calendar-skip weeks. |
| Primary output | A score and rank for every eligible symbol plus a deterministic top-tercile selection |
| Score-tie policy | Sort predicted scores descending, then ticker ascending; use this deterministic top-10 rule for paper orders and reports. Spearman metrics use average ranks for ties. B0 remains the equal-weight no-signal portfolio comparator and does not use the top-10 tie-break. |
| Primary benchmark | Equal-weight long-only basket with the same rebalance schedule, costs, and execution convention |
| ML baseline ladder | (1) no-signal constant-zero excess-return score, with equal-weight basket as the no-signal portfolio comparator; (2) 20-session momentum rank; (3) regularized linear model (ElasticNet) |
| Candidate alternative | `HistGradientBoostingRegressor` with a small, pre-registered depth/learning-rate grid; no unconstrained search |
| Model choice rule | Select the simplest model that passes the pre-registered development-fold rule; freeze that choice before opening the 2025 holdout. If no fitted candidate passes development, freeze momentum as the paper signal. Evaluate the frozen choice on the holdout once; holdout or robustness failures are reported negative results and never replace the frozen choice with momentum or another candidate. |
| Portfolio constraints | Top 10 nominal 10% targets from the cost-inclusive budget, six-decimal shares, residual cash retained, 100% gross long exposure maximum, no leverage, no shorting, no options |

The target uses the next-session open timestamp for entry and a deterministic simulated fill from that session's `label_fill_stream` adjusted IEX daily-bar open proxy; the vintage exits at the fifth valid session close timestamp using the same stream's adjusted IEX daily-bar close proxy. The exit is costed and sets the vintage's positions to zero; separate session-close valuation marks use that stream and preserve NAV, exposure, and cash-only weeks for risk metrics; the next weekly signal enters at the following valid regular-session timestamp, subject to the calendar-overlap skip.
**Same-timestamp decision ordering:** at a scheduled session open timestamp, validate all 30 entry bars and fill any pending target from the `label_fill_stream` adjusted IEX daily-bar open proxy; at a close timestamp that is both a vintage exit and a weekly decision, process `exit fill/cost → cash/position update → valuation mark/week-end state → decision score or calendar-overlap skip event → next-session entry scheduling`, using the same stream's close proxy for the exit and mark. The XNYS schedule supplies ordering timestamps, not an official opening or closing auction price; the IEX daily-bar OHLC are explicitly feed-limited research proxies. The decision cannot alter that close's NAV; the post-exit mark includes the fee and has zero exposure.

## 4. Inputs and information timing

### Price and volume inputs

The primary market-data source is the [Alpaca Market Data API](https://docs.alpaca.markets/docs/getting-started-with-alpaca-market-data) for daily U.S. equity bars. The project uses only the fields needed for the contract:

- `timestamp`, `open`, `high`, `low`, `close`, `volume`, and provider adjustment metadata;
- 1-, 5-, 20-, and 60-session close-to-close returns;
- 20-session realized volatility;
- 20-session volume z-score and dollar-volume proxy; and
- trailing drawdown and high/low range.

### Frozen feature dictionary

All rolling windows are XNYS-session windows ending at decision date `t`, inclusive, and use only the named `feature_stream` bars through `t`; `label_fill_stream` is never an input to features. The feature stream requests `adjustment=split`, which the stock-bars schema defines as adjusting price and volume for forward and reverse splits, but `asof` is treated only as symbol/entity mapping—not as a corporate-action knowledge cutoff. Every fixed feature is invariant to a split back-adjustment applied after `t`: price ratios/ranges/drawdowns cancel a common price factor, `close*volume` cancels inverse price/volume factors, and the volume z-score uses `log(volume)` so a common volume shift cancels. A synthetic future-split mutation must prove those invariants; any non-finite/invalid denominator or source-period failure is `NaN` with a paired missingness indicator and is never forward-filled. B2 scaling and all imputation are fitted inside each training fold only; M1 uses the same fold medians and masks without scaling. No cross-sectional normalization is applied before a temporal split.

**Price/volume features:**

- `ret_w` for `w ∈ {1, 5, 20, 60}` = `log(close[t] / close[t-w])`; minimum `w+1` valid closes; dimensionless log return.
- `rv20` = `sqrt(252) * sample_std(ret_1[t-19:t])` with `ddof=1`; minimum 21 valid closes; annualized dimensionless volatility.
- `volume_z20` = `(log(volume[t]) - mean(log(volume[t-19:t]))) / sample_std(log(volume[t-19:t]))` with `ddof=1`; minimum 20 positive valid volumes and nonzero standard deviation; dimensionless. Using `log` rather than `log1p` preserves invariance to a common split-volume factor.
- `dollar_volume20` = `log1p(median(close * volume over t-19:t))`; minimum 20 valid rows; `close*volume` is USD notional and `log1p` is the fixed normalization.
- `drawdown60` = `close[t] / max(close[t-59:t]) - 1`; minimum 60 valid closes; dimensionless trailing drawdown.
- `range20` = `(max(high[t-19:t]) - min(low[t-19:t])) / close[t]`; minimum 20 valid OHLC rows; dimensionless trailing high/low range.

**SEC accounting features:** facts are restricted to `us-gaap` tags from accepted `10-Q`, `10-Q/A`, `10-K`, or `10-K/A` filings with accepted/filed timestamp no later than the decision cutoff, except for the explicitly permitted `dei:EntityCommonStockSharesOutstanding` fallback named below. The DEI fallback is fetched from the SEC's `dei` taxonomy, never treated as a `us-gaap` fact, and is used only as a labeled share-count proxy. Flow facts use standalone quarterly values; when only same-fiscal-year cumulative year-to-date facts exist, derive a quarter by subtracting the prior cumulative value, otherwise mark missing. Instant facts use the latest common balance-sheet period. Every selected fact records taxonomy, accession, tag, unit, period/frame, fiscal year/period, filed/accepted time, and source URL.

- `revenue_growth_ttm`: sum the latest four aligned quarterly revenues and divide by the sum four quarters earlier, minus 1; minimum eight sequential quarters and nonzero prior TTM. Revenue tag priority: `RevenueFromContractWithCustomerExcludingAssessedTax` → `Revenues` → `SalesRevenueNet`; normalize all to USD.
- `operating_margin_ttm`: aligned four-quarter `OperatingIncomeLoss` sum divided by aligned four-quarter revenue sum; minimum four aligned quarters and nonzero revenue. Revenue uses the priority above; there is no operating-income fallback, so missing `OperatingIncomeLoss` remains missing.
- `debt_to_assets`: latest aligned instant debt proxy divided by `Assets`; minimum one common balance-sheet period. Debt tag priority is `LongTermDebtAndFinanceLeaseObligationsCurrent` + `LongTermDebtAndFinanceLeaseObligationsNoncurrent` → `LongTermDebtCurrent` + `LongTermDebtNoncurrent`; no cross-period mixing; normalize to USD.
- `cash_to_assets`: latest aligned `CashAndCashEquivalentsAtCarryingValue` divided by `Assets`, falling back to `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` only when the primary tag is absent; minimum one common balance-sheet period; normalize to USD.
- `diluted_share_change`: latest comparable quarterly `WeightedAverageNumberOfDilutedSharesOutstanding` divided by the value four quarters earlier, minus 1; fallback is `dei:EntityCommonStockSharesOutstanding` only as an explicitly labeled share-count proxy; minimum two comparable observations, same unit, and nonzero prior value.

Numerator/denominator facts must share the same period end and compatible unit; flow ratios never mix annual and quarterly periods, and instant ratios never mix balance-sheet dates. A later filing cannot rewrite an earlier row because accepted/filed time controls visibility. SEC features are stored as native ratios/changes (dimensionless); the fold-only model preprocessing owns any further scaling.

**Warm-up and sample boundary:** fetch raw price bars and SEC facts from `2018-01-01` through `2025-12-31` to satisfy the 60-session and eight-quarter minimums, but emit learning/decision rows only for `2021-01-04` through `2025-12-31`. The pre-2021 range is warm-up data, not an evaluation period. This dictionary is frozen; adding a feature or changing a formula, window, tag priority, period rule, or missingness rule requires a contract change.

**Frozen Alpaca request parameters.** Every daily-bar request uses `feed=iex`, `asof=2025-12-31`, `currency=USD`, `timeframe=1Day`, ascending sort, explicit start/end dates, and pagination until `next_page_token` is empty. The manifest records two separate streams with separate response hashes: (1) `feature_stream`, `adjustment=split`, used only for price/volume features; and (2) `label_fill_stream`, `adjustment=all`, used only for future labels and every simulator price—entry, mark, and exit. The stock-bars schema defines `adjustment=split` as split-only price/volume adjustment and `adjustment=all` as split, dividend, and spin-off adjustment. `asof=2025-12-31` fixes symbol mapping (including the FB→META rename) but is not a corporate-action vintage cutoff. The feature formulas and future-split mutation fixture provide the PIT protection for later split rewrites; no feature uses the total-return-adjusted stream. The label/fill stream is an explicitly retrospective total-return research proxy, not a literal historical executable quote and not a claim of point-in-time feature data. These settings are recorded in the manifest and are not caller-configurable.

**Update cadence and schema expectation.** Alpaca daily bars are requested after the scheduled session close; `bar_end_at` is the XNYS session timestamp, `retrieved_at`/`generated_at` record actual snapshot provenance, and `decision_event_at` is the deterministic logical replay timestamp tied to the scheduled close. The API has no assumed publication SLA. The historical replay convention treats a complete validated daily bar ending at the scheduled close as available for that close event; a missing current bar causes the contracted whole-date skip rather than a forward-fill. The expected bar schema is the fields listed above with symbol and timezone-normalized `bar_end_at` as the compound key; a schema, timestamp, or cadence change fails the build until reviewed.

`[INFERENCE]` The source is accessible but licensed, not freely redistributable. A public portfolio can remain compliant only by shipping the fetcher and metadata while requiring each reviewer to obtain permitted access. This is a deliberate ownership/data-rights tradeoff from the comparison, not an assertion that Alpaca data is public domain.


The data build MUST verify the two-stream corporate-action contract rather than trusting a column name: it records each stream's adjustment setting, checks known split/dividend/spin-off discontinuities, runs the future-split feature-invariance mutation fixture, rejects non-positive or internally inconsistent OHLC bars, and preserves a response hash for each stream. Raw Alpaca bars are not committed to the public repository. The code fetches both streams using the applicant's own credentials at build time and records each source URL, request parameters, retrieval time, response hash, and terms snapshot.

**Reuse obligation.** Alpaca's [Customer Agreement](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf), §23, states that market data must not be reproduced, distributed, sold, or commercially exploited without written consent. Therefore the public project ships ingestion code, schemas, checksums, and a tiny synthetic fixture—not a raw Alpaca dump. The README must state that a reviewer needs their own permitted access and must not imply Alpaca endorsement. If the current terms do not permit the intended public demonstration, stop and replace the source before publishing results; do not copy a different vendor into the contract silently.

### Filing and accounting inputs

The secondary source is the SEC's first-party [EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), specifically submissions metadata and XBRL `companyfacts`/`companyconcept` endpoints. SEC facts contain both fiscal period fields and filing/acceptance information. The build uses the **filed/accepted timestamp**, never the fiscal period end, to decide when a fact becomes visible.

For each decision timestamp, the as-of join takes the latest filing fact whose accepted time is no later than the cutoff. It preserves accession number, taxonomy, tag, unit, frame/period, filed time, and source URL. A later restatement cannot rewrite an earlier feature row. If a fact has no unambiguous unit or accepted timestamp, the row is missing and logged rather than guessed.

The initial accounting feature group is intentionally small:

- trailing revenue growth;
- operating-margin proxy when the required tags are available;
- debt-to-assets or an equivalent leverage proxy;
- cash-to-assets; and
- diluted-share-count change when the tag/unit is stable.

Tag mapping is explicit and versioned. No natural-language filing sentiment, analyst estimates, or post-filing revisions enter the minimum project.

**Reuse obligation.** SEC site information is described by the SEC as public information that may be copied or further distributed; the project still follows the SEC's [developer guidance](https://www.sec.gov/about/developer-resources), identifies itself with a descriptive User-Agent, obeys rate limits, and preserves SEC attribution. The project does not claim SEC endorsement.

### Timing invariants

- `feature_cutoff_at = decision_at` is the scheduled XNYS close; every price bar used has `bar_end_at <= feature_cutoff_at`, and every SEC fact used has accepted/filed time no later than `feature_cutoff_at`. `decision_event_at` is the deterministic logical replay timestamp for that close, ordered by `event_seq`; `retrieved_at` and `generated_at` record actual snapshot provenance only and are excluded from causal ordering and byte-equivalence.
- A filing accepted after `feature_cutoff_at` becomes eligible on the next decision, not retroactively on its fiscal period; an IEX daily bar retrieved later remains eligible only when its session `bar_end_at` is at or before the cutoff. The historical replay's close-availability convention is fixed and must not be changed per run.
- Any vendor timestamp without a reliable timezone is rejected until normalized and tested.
- The future label window is constructed after the feature table and is never joined back into features.
- The final holdout is frozen by date before any model comparison.

## 5. Evaluation benchmark and claims boundary

The benchmark ladder is fixed:

1. no-signal constant-zero excess-return prediction, with the equal-weight basket as its portfolio comparator;
2. 20-session momentum rank;
3. ElasticNet regression; and
4. HistGradientBoostingRegressor.

Every model sees the same rows, feature groups, temporal folds, execution delay, universe, costs, and missing-data policy. A model may be selected only when its improvement survives the pre-registered temporal holdout and robustness checks. The project claims **evidence about a forecasting/ranking pipeline**, not a profitable investment strategy.

If a P&L-like diagnostic is shown, it MUST be labeled a simulated historical result and include:

- explicit one-way commission/fee assumption;
- explicit one-way slippage assumption;
- turnover and cost drag;
- market calendar and next-open execution;
- cash/exposure/position limits; and
- cumulative return, annualized volatility, Sharpe convention, Sortino convention, maximum drawdown, hit rate, and the exact sample window.

The headline success criterion is reproducible evidence, not positive return. A weak or negative net result is acceptable when the candidate can reproduce it, diagnose it, and state what the data cannot support.

## 6. Candidate-owned boundary

### Candidate-authored

Problem framing; fixed universe decision; data manifest and as-of joins; feature definitions; labels; baseline and model training/evaluation code; temporal split implementation; cost/slippage simulator; focused tests; experiment records; failure diagnosis; packaging; paper-trading replay; logs; report; limitations; and every final claim.

### Reused dependencies or data

Python, pandas, NumPy, scikit-learn, plotting libraries, Alpaca API/SDK, SEC APIs, standard statistical formulas, and cited literature. Their code and data remain dependency/reused work; the candidate must not claim authorship of them.

### Reference-only material

[Vibe-Trading audit](vibe-trading-audit.md) recommends **reference only**. The candidate may study its PIT join, fee-schedule, run-card, and sandboxing patterns, then reimplement the needed ideas. No Vibe-Trading code, Alpha Zoo output, Packt notebook, or tutorial notebook is part of this project.

## 7. Minimum credible evidence package

The selected direction clears the rubric's minimum floor only when the implementation produces all of these candidate-owned artifacts:

- a concise problem brief, target, and evaluation metric committed before modeling;
- a re-runnable data build from the Alpaca/SEC sources with provenance, hashes, schema checks, and at least one documented corporate-action or point-in-time fix;
- the constant-zero and momentum baselines plus ElasticNet and one justified nonlinear alternative, with candidate-authored evaluation code;
- leakage-safe temporal validation, tracked experiments, and at least one negative result, as fixed in [experimental proof](experimental-proof.md);
- one observed performance failure investigated with symptom, hypotheses, root cause, fix, and before/after verification;
- packaged and focused-tested code plus a repeatable local paper-trading loop with useful logs;
- transaction costs and slippage in every P&L-like claim, with no cost-free result presented as evidence;
- specific limitations and visible iteration in the report and git history; and
- a run manifest from which the candidate can reproduce and defend every reported number live.

The package cannot substitute for a related degree or professional tenure. It reduces uncertainty about ability; it does not manufacture a credential.

## 8. Explicit non-goals

- No live brokerage integration, live orders, real-money execution, or capital.
- No investment advice, buy/sell recommendation to readers, or profitability guarantee.
- No copied Vibe-Trading or Packt foundation, agent layer, MCP server, or web UI.
- No TensorFlow/PyTorch requirement, deep neural network, reinforcement learning, custom architecture, or hyperparameter sweep for appearance.
- No intraday trading, options, leverage, shorting, borrow-cost modeling, or multi-country market support in the minimum project.
- No sentiment/news/LLM features in the minimum project.
- No claim of survivorship-free historical results; the fixed basket limitation must remain visible.
- No dashboard, API service, cloud deployment, broker connector, database, or MLOps platform unless the minimum evidence gate is already complete and a specific hiring signal cannot be shown by the local CLI/logs.
- No implementation, training, backtest, or paper-trading execution under this build-brief ticket set.

## 9. Contract acceptance gate

The implementing agent may begin only when the repository created from this contract can answer “yes” to all of the following without inventing another product decision:

- Is the selected project exactly one fixed weekly top-tercile long-only ranker over the named 30-symbol basket? **Yes.**
- Are target, horizon, execution delay, label construction, features, data sources, and timing fixed? **Yes.**
- Is there a simple baseline and one justified ML alternative? **Yes.**
- Is the data-rights boundary explicit, including no raw Alpaca redistribution? **Yes.**
- Are survivorship, corporate-action, filing-timing, and missing-data limitations visible? **Yes.**
- Is paper trading local, no-capital, no-broker, and cost-aware? **Yes.**
- Are TensorFlow/PyTorch, agent orchestration, dashboards, cloud, live trading, and profitability claims outside scope? **Yes.**

## Sources

- [Project-direction comparison](project-direction-comparison.md), accessed 2026-07-13.
- [Vibe-Trading audit](vibe-trading-audit.md), accessed 2026-07-13.
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [SEC developer resources](https://www.sec.gov/about/developer-resources), accessed 2026-07-13.
- [Alpaca market-data documentation](https://docs.alpaca.markets/docs/getting-started-with-alpaca-market-data), accessed 2026-07-13.
- [Alpaca stock historical-bars schema](https://docs.alpaca.markets/reference/stockbars), accessed 2026-07-13.
- [Alpaca Customer Agreement](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf), accessed 2026-07-13.
- [Gu, Kelly & Xiu, Empirical Asset Pricing via Machine Learning](https://www.nber.org/papers/w25398), accessed 2026-07-13.
- [Looloo project-evidence rubric](looloo-project-evidence-rubric.md), prior research.
- [exchange_calendars 4.13.2](https://pypi.org/project/exchange-calendars/), accessed 2026-07-13.
