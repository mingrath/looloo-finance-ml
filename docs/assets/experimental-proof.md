# Experimental and backtest proof protocol

**Status:** implemented protocol for the selected **portfolio project**. Generated runs must satisfy this fixed evidence standard; positive performance is never assumed.

Related contract: [selected project and ML/data contract](selected-project-contract.md).

## Proof standard

The project succeeds when a reviewer can reproduce the data snapshot, trace each feature to its information timestamp, rerun the same temporal folds, inspect failed experiments, and explain one real performance failure. Positive returns are neither required nor promised. A result that disappears after the timing, cost, or robustness checks is a useful negative result.

`[INFERENCE]` The protocol treats backtest overfitting as a first-class risk. Bailey, Borwein, López de Prado, and Zhu's *The Probability of Backtest Overfitting* introduces PBO/CSCV for this risk ([publisher page](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting)); the minimum project does not need to implement every PBO variant, but it must limit search, preserve a final holdout, and report how many configurations were tried.

## 1. Baseline and model ladder

Run the same data rows and execution convention for every rung:

1. **B0 — no-signal:** constant-zero excess-return prediction; the matching no-signal portfolio comparator is the equal-weight basket, not a top-tercile tie-break.
2. **B1 — momentum:** 20-session price momentum rank, with no fitted parameters.
3. **B2 — regularized linear ML:** ElasticNet regression with scaling fitted inside each training fold.
4. **M1 — nonlinear ML:** `HistGradientBoostingRegressor(max_iter=200, min_samples_leaf=20, l2_regularization=1.0, random_state=20250713)` over exactly four configurations: `max_depth ∈ {2, 3}` × `learning_rate ∈ {0.05, 0.10}`. No other HGB parameter changes.

For B2, test exactly nine configurations: `ElasticNet(alpha ∈ {0.001, 0.01, 0.1}, l1_ratio ∈ {0.1, 0.5, 0.9}, max_iter=10000, tol=1e-4, random_state=20250713)`. The configuration order is the listed order; ties within `1e-6` select the lower-complexity model, then the first listed configuration.

For every fitted model, numeric missing values are imputed with the **training-fold median** and paired missingness indicators. A feature with more than 30% missing values in that training fold is dropped for that fold and recorded. Validation/holdout rows use only the training-fold medians and feature mask. Labels are never imputed. Each fold must contain at least 52 unique decision weeks and at least 20 eligible symbols per week; otherwise the run fails with `insufficient_training_history` rather than shrinking the rule.

Promotion is fixed and uses development data only. A candidate must improve B1's mean development-fold IC by at least **0.010** and be non-negative versus B1 in at least **60%** of development folds. Complexity order is B2 ElasticNet before M1 HGB; within either family, price/volume-only is simpler than fundamentals-only, which is simpler than combined. Choose the lowest-complexity development-passing candidate; ties choose highest mean development IC, then the listed configuration order. If no fitted candidate passes this development rule, freeze B1 as the paper signal and publish the rejection. Otherwise fit the single selected winner on all permitted development rows, freeze that model artifact, and evaluate it on the final holdout exactly once. The holdout reports whether the frozen choice meets the pre-registered evidence gates—IC improvement of at least **0.000**, seeded 95% block-bootstrap lower bound no worse than **-0.005**, and maximum drawdown no worse by more than **0.10** absolute under the 6-basis-point cost setting—but a holdout miss is a negative result and MUST NOT replace the frozen choice with B1 or another candidate.

Feature ablations are fixed before model selection:

- price/volume features only;
- SEC-as-of fundamentals only; and
- combined features.

No neural network, reinforcement-learning policy, transformer, agent, AutoML service, or unconstrained hyperparameter search enters the minimum project. TensorFlow/PyTorch is not technically warranted for this small tabular panel; adding it would not create independent hiring evidence.

The development promotion rule in §1 is the only selection rule: do not use the final holdout to choose a model, add a threshold, or replace a failed candidate with an unregistered configuration. The paper signal is the development-frozen winner, or B1 when no fitted candidate passes the development rule; publish the holdout outcome without changing that choice.

## 2. Experiment record

Every run writes one immutable record containing:

- project and contract version;
- data-manifest and raw-response hashes;
- exact symbol universe and date cutoff;
- feature-group name and column schema hash;
- model family and every hyperparameter;
- temporal-fold IDs and training/test date ranges;
- random seed and library/runtime versions;
- code commit identifier;
- execution, cost, slippage, and position-limit settings; and
- predictive and portfolio metrics, warnings, and output artifact hashes.

A human-readable CSV/JSONL index is enough. No experiment tracker service is required. The report includes every attempted configuration, including failed runs and model families rejected before the final choice.

## 3. Temporal validation contract

The observations are weekly Friday decision rows and each label covers the next five valid sessions. Use an expanding, date-based walk-forward splitter rather than random k-fold. Scikit-learn's [`TimeSeriesSplit`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) documents the core invariant: time-ordered data must not train on future observations, and its `gap` parameter excludes samples immediately before each test set. The project uses a custom date wrapper because panel rows share a decision date and each row has an explicit label end. Holiday calendars can make adjacent weekly label intervals overlap; the purge rule removes those overlaps during validation, while the paper-trading calendar-overlap policy below prevents overlapping positions.

Fixed schedule:

- **Development period:** decision dates in 2021–2024.
- **Final holdout:** decision dates in 2025, untouched until the model family, feature group, and thresholds are frozen.
- **Development folds:** minimum 52 weeks of training, 13-week validation window, one full weekly decision-period embargo, then advance 13 weeks. Use every eligible fold; do not select only favorable folds.
- **Purge rule:** remove every training row whose `[decision_at, label_end]` interval overlaps the validation interval. The one-period embargo remains even when the weekly schedule makes overlap unlikely.
- **Preprocessing rule:** scaling, imputation decisions, feature selection, and model fitting happen inside each training fold only. Missingness indicators are allowed; future values are not forward-filled into the past.
- **Holdout rule:** after freezing the choice, apply the development→holdout seam below, fit on the remaining permitted development rows, and evaluate 2025 once. Do not revise the model after seeing the holdout.
- **Development→holdout purge:** define `holdout_start` as the first 2025 decision timestamp and `embargo_start` as the immediately preceding scheduled weekly decision timestamp. A final-fit development row is retained only when `label_end < holdout_start` and `decision_at < embargo_start`; log both predicates, counts, and boundary dates. The fixture must reject the 2024-12-27 row whose five-session label ends 2025-01-06, despite its 2024 decision date.

The report prints the exact fold dates, row counts, purge counts, and embargo dates. A fold with fewer than the contract's minimum training rows is a data-quality failure, not a reason to quietly shrink the rule.

## 4. Execution, costs, and risk assumptions

The local simulator applies the same rule to every model:

- **Open stage:** at each scheduled XNYS session open timestamp, validate all 30 bars for any pending target; if any entry bar is missing, cancel that target before fills, emit no partial order/cost, preserve cash/positions, and log the entry-skip; otherwise fill six-decimal-share entries from the `label_fill_stream` adjusted SIP consolidated daily-bar open proxy using the cost-inclusive budget.
- **Close stage:** at every scheduled XNYS close timestamp, validate a close bar for every currently held symbol (fail closed if any is missing; cash-only marks require no symbol bar), process any due exit from the `label_fill_stream` adjusted SIP consolidated daily-bar close proxy, emit the valuation mark/week-end state from that same close proxy, and only then—if this is a weekly decision close—inspect decision bars; if the next valid entry timestamp is on or before the active position's fifth valid session close timestamp, skip that paper rebalance and log it; otherwise schedule the target for the next session timestamp. The same-close sequence is `exit fill/cost → cash/position update → valuation mark/week-end state → decision score or skip event → next-session entry scheduling`; marks include the fee and zero exposure after exit. XNYS supplies ordering timestamps; SIP consolidated daily-bar OHLC are feed-limited price proxies, not official auction quotes.
- synthetic starting NAV `USD 100,000`; top 10 positions have nominal equal 10% targets from the cost-inclusive entry budget, no leverage or shorting, and residual cash is retained;
- for selected one-way cost `c`, set `entry_budget = NAV / (1 + c)`, floor each target's shares to six decimal places using the `label_fill_stream` adjusted SIP consolidated daily-bar open proxy for the scheduled entry session, charge `c` on actual entry notional, and assert post-fill cash ≥ 0 and gross notional ≤ NAV;
- **illustrative one-way cost:** 1 basis point commission/fee plus 5 basis points slippage on every traded notional, including both exits and new entries at a rebalance;
- cost sensitivity runs at 0, 3, 6, and 12 basis points total one-way cost;
- if any of the 30 symbols lacks a current decision bar, skip the new decision before ranking or ordering, preserve any due exit/mark state, emit no partial new order/cost, and log every missing symbol; a missing pending-entry bar is handled at the open stage above; if a fifth-session exit bar is later missing, fail closed with an explicit event, invent no price, cost, or return, and halt replay until the data is corrected;
- the `label_fill_stream` uses `adjustment=all` for every simulator price (entry, mark, and exit), so split, cash-dividend, and spin-off adjustments are embedded in the explicitly synthetic historical proxy; the `feature_stream` uses split-only bars and split-invariant formulas, and no separate dividend cash ledger is added. Overnight financing, borrow, and tax are not modeled and are listed as limitations;
- no headline P&L number is reported without the full assumptions above.

The 1+5 basis-point setting is an applicant-defined simulator assumption, not an Alpaca quote or a market guarantee. The report labels it as such and shows sensitivity rather than presenting one cost choice as truth.

If a P&L-like result is shown, report gross and net cumulative return, annualized volatility, Sharpe, Sortino, maximum drawdown, weekly hit rate, turnover, average exposure, number of rebalances, and cost drag. Mark NAV and exposure at every scheduled XNYS session close; derive arithmetic weekly returns from the last scheduled close of every calendar week, including cash-only and calendar-overlap-skip weeks. State the annualization factor (52 weekly observations), risk-free/zero benchmark convention, sample dates, and whether returns are arithmetic or log. The primary evidence remains ranking quality and reproducibility; no profitability promise is made.

## 5. Metrics and uncertainty

### Predictive metrics

- weekly cross-sectional Spearman rank information coefficient (IC);
- mean, median, standard deviation, IC information ratio (`mean / standard deviation` when defined), and fraction of positive-IC weeks;
- top-tercile versus equal-weight-basket excess return;
- regression MAE and RMSE for models that emit return predictions; and
- fold-by-fold distribution, not only a pooled average.

IC is the Pearson correlation of within-date average ranks of predictions and realized excess returns, averaged across eligible weekly dates; a date with fewer than 3 symbols or a constant prediction/label vector is `NA` and counted in the coverage report, never converted to zero. NAV marks occur at every scheduled XNYS close timestamp and leave cash/positions unchanged; exit fills are separate costed events. Let `NAV_0=USD 100,000` and let `NAV_w` be the net NAV at the last scheduled XNYS close of calendar week `w`, including cash-only and calendar-overlap-skip weeks; the first week's denominator is `NAV_0`, and each later week's denominator is the prior week's mark. Net weekly portfolio return is `r_w = NAV_w / NAV_{w-1} - 1`. The metric definitions below use these arithmetic weekly returns and marks; no metric silently drops zero-exposure weeks.

### Portfolio metrics

- Use the cost-aware metrics in §4 and compare every model to B0, B1, and the equal-weight benchmark under identical schedules, bars, and proxy fills.
- **Gross/net construction:** the net ledger applies the selected one-way fee/slippage and cost-inclusive sizing. The gross shadow ledger replays the exact same decisions, timestamps, target share quantities, SIP consolidated proxy prices, and order batches with fee and slippage set to zero; it is not a separately resized `c=0` run. Every return, exposure, turnover, and drawdown table labels `gross` or `net`.
- **Cumulative return:** `(final_week_end_NAV / NAV_0) - 1`, reported separately for gross and net.
- **Annualized volatility:** sample standard deviation (`ddof=1`) of arithmetic weekly returns times `sqrt(52)`; `NA` when fewer than two weekly returns exist.
- **Sharpe:** `mean(r_w) / sample_std(r_w) * sqrt(52)` with zero weekly risk-free rate; `NA` when the denominator is zero.
- **Sortino:** `mean(r_w) / sqrt(mean(min(r_w, 0)^2)) * sqrt(52)` with a zero return target and all week-end weeks in the denominator; `NA` when downside deviation is zero.
- **Maximum drawdown:** minimum over all week-end marks, including `NAV_0`, of `NAV_w / max_{u≤w}(NAV_u) - 1`.
- **Weekly hit rate:** count of week-end weeks with `r_w > 0` divided by all week-end weeks; zero-return, cash-only, and calendar-overlap-skip weeks remain in the denominator and are not hits.
- **Gross exposure and average exposure:** at each scheduled close mark, `gross_exposure_w = sum_i(abs(position_i * close_proxy_i)) / NAV_w`; average exposure is the arithmetic mean across every scheduled close mark, including cash-only and skip marks.
- **Turnover:** one-way turnover at each fill event is `sum_i(abs(executed_trade_notional_i)) / NAV_before_event`; entries and exits both count, there is no one-half factor, and weekly turnover is the sum across that week's fill events. A zero-trade week has zero turnover.
- **Number of rebalances:** count decision events that produce at least one filled entry order batch; whole-date skips, calendar-overlap skips, and pending-entry cancellations are reported separately and are not rebalances.
- **Top-tercile excess return:** for each week, subtract the equal-weight benchmark's net weekly return from the top-tercile portfolio's net weekly return under the same proxy fills; report the resulting series and its mean/median.
- **Cost drag:** report the weekly gross-minus-net return difference and cumulative drag `(final_gross_NAV - final_net_NAV) / NAV_0`; also report the ledger's fee-plus-slippage total. These are diagnostics, not a profit claim.

### Uncertainty

- 95% percentile confidence intervals from exactly **2,000** seeded block-bootstrap resamples of contiguous weekly observations, block length fixed at four weeks, seed `20250713`;
- per-fold ranges and sign consistency;
- cost-sensitivity table; and
- a clearly labeled caveat that serial dependence and a small effective sample can make these intervals optimistic.

The report never turns a confidence interval into a claim of statistical certainty or future performance.

## 6. Required negative results and robustness

The report must include:

- every baseline and candidate model, even when it loses;
- price-only, fundamentals-only, and combined ablations;
- at least one model-complexity rejection (for example, the nonlinear model fails to beat ElasticNet after costs);
- separate 2021–2022, 2023–2024, and 2025 slices;
- low/high prior-volatility slices, where the threshold is the median of training-fold prior-20-session equal-weight-basket volatility and is frozen for that fold's validation/holdout rows;
- full 30-symbol basket versus the pre-registered complete-history sensitivity subset (symbols with at least 95% of expected sessions and no gap longer than five sessions, determined from the manifest before modeling);
- cost sensitivity from §4; and
- missing-data and corporate-action sensitivity outcomes.

A result may be called robust only when its direction and explanation survive these predeclared slices. A profitable-looking single slice is not a success criterion.

## 7. Correctness checks

### Look-ahead and timing

- mutate or blank future bars and future split adjustments and assert all earlier feature rows are unchanged;
- assert every price feature row has `bar_end_at <= feature_cutoff_at`, every SEC fact has accepted/filed time no later than that cutoff, and retrieval/generated wall-clock fields never alter inclusion;
- assert SEC joins use accepted/filed time, not fiscal period end;
- assert a feature row ending at the decision cutoff cannot create a fill at that same close; entry uses the next valid session's SIP consolidated daily-bar open proxy;
- assert labels are built after feature rows and never joined back; and
- assert every training row obeys the purge and embargo intervals.

### Survivorship and universe

- verify the exact 30-symbol manifest is committed before experiments;
- report missing-history symbols and delistings rather than silently replacing them;
- run the fixed complete-history sensitivity subset; and
- state that neither analysis is a survivorship-free index study.

### Data defects

- duplicate symbol/timestamp detection;
- frozen `exchange_calendars==4.13.2` XNYS session-calendar and timezone checks;
- OHLC invariants (`high >= max(open, close)`, `low <= min(open, close)`, positive prices/volume policy);
- split/dividend adjustment spot checks;
- SEC unit, accession, taxonomy, and duplicate-fact checks; and
- raw-response checksum and schema-version verification.

### Overfitting and implementation

- count all model/feature configurations and show the selection rule;
- preserve the final holdout and never tune on it;
- compare against a deterministic momentum control;
- rerun with the same seed and manifest hash;
- test that the simulated entry fill uses the scheduled next XNYS session's SIP consolidated daily-bar open proxy after the signal, that the fifth-session exit fill uses the same stream's SIP consolidated daily-bar close proxy, is costed, and zeroes positions, that every XNYS close emits a non-mutating NAV mark and every calendar week has a week-end NAV, that the post-exit mark includes the fee with zero exposure, that future-split mutations leave prior feature values unchanged, and that score ties sort by descending score then ticker ascending;
- test costs, turnover, cash, position caps, and the development→holdout label-end seam on synthetic fixtures;
- fail closed on missing credentials, malformed data, or an unverifiable timestamp.

## 8. Performance-diagnosis narrative

An observed failure is published only with its own primary artifacts. The required template is:

1. **Symptom:** metric, slice, dates, and run ID.
2. **Hypotheses:** data timing, corporate action, target construction, model/regularization, regime, execution, and cost hypotheses considered.
3. **Isolation:** the smallest experiments or checks that ruled hypotheses in or out.
4. **Root cause:** one evidenced cause, with the relevant raw row, code path, or invariant.
5. **Fix:** one minimal change; no simultaneous redesign that hides causality.
6. **Before/after:** rerun the same fold, holdout, and cost settings; report changed metrics and any regression.
7. **Residual limitation:** what remains unknown or still fails.

The prior rank-IC `dropna()` incident has no recoverable original run record, so it is not presented as an observed failure. Its focused regression test preserves the corrected behavior. A plausible incident is never evidence.

## 9. Numbers to reproduce in Looloo's live review

The candidate must be able to regenerate, without guessing:

- the 30-symbol list and its date cutoff;
- development/holdout dates and exact fold boundaries;
- training/validation/holdout row counts after purge and embargo;
- feature count by feature group and missingness policy;
- every baseline and candidate configuration;
- mean/median/standard deviation of weekly IC;
- top-tercile excess-return and cost-drag series;
- turnover, exposure, Sharpe convention, Sortino convention, and maximum drawdown;
- the number of tested configurations and the model-selection rule; and
- before/after values only for an observed diagnosis with its primary artifacts;

The interview explanation must distinguish source facts, applicant design choices, reused dependencies, observed results, and unknowns. A number not reproducible from the manifest and run record is not published.

## Sources

- [Selected ML/data contract](selected-project-contract.md), this project.
- [Looloo project-evidence rubric](looloo-project-evidence-rubric.md), especially the minimum credible evidence package.
- [Gu, Kelly & Xiu, *Empirical Asset Pricing via Machine Learning*](https://www.nber.org/papers/w25398), accessed 2026-07-13.
- [scikit-learn `TimeSeriesSplit` documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html), accessed 2026-07-13.
- [Bailey et al., *The Probability of Backtest Overfitting*](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting), accessed 2026-07-13.
- [SEC EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), accessed 2026-07-13.
- [Alpaca Customer Agreement](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf), accessed 2026-07-13.
