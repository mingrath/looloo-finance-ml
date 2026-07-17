# Cross-sectional equity return-ranking evidence report

Run `20260717T051422501995Z-4626e6cc` · contract `finance-ml-v1` · generated `2026-07-17T05:17:05.439623+00:00`

> **SYNTHETIC FIXTURE RUN — pipeline validation only; not hiring or investment evidence.**

## Reviewer path

1. Read the result and limitation tables below.
2. Inspect `experiment_results.csv` and `fold_metrics.csv` for every registered model and fold.
3. Verify `model_manifest.json`, `evaluation_manifest.json`, and `paper_manifest.json` hashes.
4. Trace any paper number to the immutable JSONL event logs; each event carries the run, data, model, feature-schema, contract, and code identifiers.

## Reproduce

Use a fresh artifact directory: `uv sync --locked --extra dev && uv run pytest -q && GIT_COMMIT=<commit> uv run looloo-finance-ml --artifacts artifacts all`.

For licensed source data, set `ALPACA_API_KEY`, `ALPACA_API_SECRET`, and a descriptive `SEC_USER_AGENT`, then add `--live` after `all`. Raw licensed data remains outside version control.

## Recruiter card and ownership

**Problem:** rank the next five-session excess returns of a frozen 30-stock US equity panel without using future prices, late SEC filings, or holdout feedback.

**Candidate-owned:** data contracts and manifests, point-in-time feature/label joins, model ladder, temporal validation, promotion rule, deterministic costed ledger, fail-closed tests, diagnosis, and evidence packaging.

**Reused/reference-only:** Alpaca and SEC data services; Python/pandas/NumPy/scikit-learn; `exchange_calendars`; Vibe-Trading and Packt ML4T as learning references only. No reused repository is represented as candidate-authored evidence.

**Boundary:** this artifact demonstrates programming, ML, data, experimentation, diagnosis, and production discipline. It does not replace a degree or professional tenure and makes no profitability claim.

## Decision and headline evidence

- Selected model: **B1** (momentum, `price_volume`).
- Holdout rank IC: **0.006391**, 95% moving-block bootstrap CI **[-0.035532, 0.063559]** across 51 weekly dates.
- Net cumulative paper return: **0.075897**; gross: **0.127429**; cost drag: **0.051532**.
- Mean weekly top-tercile excess return over the costed equal-weight basket: **0.000366**.
- Paper sample: **2025-01-03T21:00:00+00:00** through **2025-12-29T21:00:00+00:00**; 53 calendar-week observations.
- Positive returns were not required for promotion. Failed candidates and unfavorable slices remain in the evidence tables.

## Development portfolio comparison (out-of-fold predictions only)

| Model | Status | Family | Features | Net return | Mean top-tercile excess | Cost drag | Max drawdown |
|---|---|---|---|---:|---:|---:|---:|
| B0 | estimated | constant_zero | price_volume | -0.010820 | 0.000000 | 0.141150 | -0.053466 |
| B1 | estimated | momentum | price_volume | 0.123332 | 0.000904 | 0.153005 | -0.043321 |
| B2-price_volume-a0.001-l0.1 | estimated | elastic_net | price_volume | -0.019128 | -0.000038 | 0.136584 | -0.119786 |
| B2-price_volume-a0.001-l0.5 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.001-l0.9 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.01-l0.1 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.01-l0.5 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.01-l0.9 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.1-l0.1 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.1-l0.5 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-price_volume-a0.1-l0.9 | not_estimable | elastic_net | price_volume | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.001-l0.1 | estimated | elastic_net | fundamentals | -0.050963 | -0.000268 | 0.134578 | -0.117883 |
| B2-fundamentals-a0.001-l0.5 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.001-l0.9 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.01-l0.1 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.01-l0.5 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.01-l0.9 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.1-l0.1 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.1-l0.5 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-fundamentals-a0.1-l0.9 | not_estimable | elastic_net | fundamentals | N/A | N/A | N/A | N/A |
| B2-combined-a0.001-l0.1 | estimated | elastic_net | combined | 0.039782 | 0.000365 | 0.138971 | -0.118822 |
| B2-combined-a0.001-l0.5 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.001-l0.9 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.01-l0.1 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.01-l0.5 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.01-l0.9 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.1-l0.1 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.1-l0.5 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| B2-combined-a0.1-l0.9 | not_estimable | elastic_net | combined | N/A | N/A | N/A | N/A |
| M1-price_volume-d2-r0.05 | estimated | hist_gradient_boosting | price_volume | -0.034834 | -0.000156 | 0.137192 | -0.100135 |
| M1-price_volume-d2-r0.1 | estimated | hist_gradient_boosting | price_volume | -0.047552 | -0.000244 | 0.136731 | -0.092141 |
| M1-price_volume-d3-r0.05 | estimated | hist_gradient_boosting | price_volume | 0.132456 | 0.000958 | 0.149715 | -0.084045 |
| M1-price_volume-d3-r0.1 | estimated | hist_gradient_boosting | price_volume | 0.056718 | 0.000473 | 0.145624 | -0.073142 |
| M1-fundamentals-d2-r0.05 | estimated | hist_gradient_boosting | fundamentals | -0.020141 | -0.000046 | 0.134337 | -0.138007 |
| M1-fundamentals-d2-r0.1 | estimated | hist_gradient_boosting | fundamentals | -0.045559 | -0.000227 | 0.133677 | -0.142665 |
| M1-fundamentals-d3-r0.05 | estimated | hist_gradient_boosting | fundamentals | 0.008697 | 0.000156 | 0.138306 | -0.116939 |
| M1-fundamentals-d3-r0.1 | estimated | hist_gradient_boosting | fundamentals | -0.042109 | -0.000201 | 0.134132 | -0.135378 |
| M1-combined-d2-r0.05 | estimated | hist_gradient_boosting | combined | -0.058417 | -0.000325 | 0.135409 | -0.106261 |
| M1-combined-d2-r0.1 | estimated | hist_gradient_boosting | combined | -0.093417 | -0.000583 | 0.129813 | -0.135231 |
| M1-combined-d3-r0.05 | estimated | hist_gradient_boosting | combined | -0.001330 | 0.000083 | 0.137863 | -0.101081 |
| M1-combined-d3-r0.1 | estimated | hist_gradient_boosting | combined | -0.042967 | -0.000209 | 0.134705 | -0.110118 |

Every estimated row uses the same common OOF decision dates, split-adjusted feature/label history, all-adjusted replay bars, 6 bps one-way cost, and deterministic event ledger. B0 holds the equal-weight basket; every other estimated row holds its top tercile. Failed candidates remain explicitly not estimable.

## Final-holdout paper portfolio comparison

| Model | Net return | Gross return | Mean top-tercile excess | Volatility | Sharpe | Sortino | Max drawdown | Hit rate | Turnover | Avg exposure | Rebalances |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 | 0.075897 | 0.127429 | 0.000366 | 0.057822 | 1.270486 | 2.072018 | -0.037930 | 0.584906 | 83.974815 | 0.680162 | 42 |
| B0 equal-weight basket | 0.056313 | 0.108161 | 0.000000 | 0.036374 | 1.496297 | 2.902516 | -0.021019 | 0.509434 | 83.974813 | 0.680162 | 42 |

## Predictive evidence

| Mean rank IC | Median | Std. dev. | IC information ratio | Positive fraction | 95% CI | MAE | RMSE | Mean top-tercile target excess |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.006391 | -0.004672 | 0.179832 | 0.035536 | 0.490196 | [-0.035532, 0.063559] | 0.048638 | 0.061024 | 0.000887 |

## Cost and failure sensitivities

| One-way cost | Net return | Cost drag | Final NAV |
|---:|---:|---:|---:|
| 0 bps | 0.131512 | 0.000000 | 113151.170800 |
| 3 bps | 0.103354 | 0.026099 | 110335.389104 |
| 6 bps | 0.075897 | 0.051532 | 107589.678006 |
| 12 bps | 0.023015 | 0.100466 | 102301.534384 |

- Missing-bar stress removed `MRK` on `2025-01-06` and produced 1 whole-batch skip.
- Split-adjusted execution stream rejected: `True`.
- Normal-run skip counts: `{"calendar_overlap": 9}`.

- Complete-history subset paper status: `estimated`; net return: 0.075897.

## Predeclared robustness slices

| Slice | Rows | Dates | Rank IC | Median IC | Positive fraction | MAE | Top-tercile excess |
|---|---:|---:|---:|---:|---:|---:|---:|
| development_2021_2022_oof | 1530 | 51 | 0.018229 | 0.042492 | 0.568627 | 0.048306 | 0.001276 |
| development_2023_2024_oof | 2760 | 92 | 0.016550 | 0.033370 | 0.543478 | 0.049206 | 0.001446 |
| holdout_2025_full_basket | 1530 | 51 | 0.006391 | -0.004672 | 0.490196 | 0.048638 | 0.000887 |
| development_low_volatility_oof | 2190 | 73 | -0.019891 | -0.010456 | 0.465753 | 0.048621 | 0.000364 |
| development_high_volatility_oof | 2100 | 70 | 0.055776 | 0.067631 | 0.642857 | 0.049160 | 0.002452 |
| holdout_low_volatility | 720 | 24 | 0.003263 | 0.002447 | 0.500000 | 0.047095 | 0.001161 |
| holdout_high_volatility | 810 | 27 | 0.009171 | -0.004672 | 0.481481 | 0.050009 | 0.000644 |
| holdout_complete_history_subset | 1530 | 51 | 0.006391 | -0.004672 | 0.490196 | 0.048638 | 0.000887 |

## Data and leakage controls

- Data manifest hash: `4626e6cc69a268713d10b7381a45d0fb2cf5e5b8b228e16c69419581c60a8c3d`; source mode: **synthetic**.
- Frozen universe: 30 symbols; complete-history sensitivity subset: 30.
- Decision is the last valid XNYS close in each calendar week; entry is the next XNYS open; label and exit are the close five sessions after decision.
- SEC facts become eligible only at `accepted_at`; amendments replace originals only after their own acceptance time.
- Every development fold purges labels crossing validation and applies a one-week embargo. The 2025 holdout is excluded from fitting and model promotion.
- Imputation, missing-feature drops, indicators, and scaling are fitted only on each training fold.

### Source and obligation ledger

- [Alpaca Customer Agreement §23](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf): market-data use and redistribution boundary. Obligation: keep raw and normalized licensed bars outside version control; the default artifact directory is ignored.
- [Alpaca Market Data](https://docs.alpaca.markets/reference/stockbars): split-adjusted features and all-adjusted label/fill proxies. Obligation: credentials and use remain subject to Alpaca terms; do not redistribute raw licensed data.
- [SEC EDGAR CompanyFacts](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): accepted-time fundamentals. Obligation: descriptive User-Agent, fair-access rate limits, attribution; no SEC endorsement.
- [exchange_calendars XNYS](https://github.com/gerrymanoim/exchange_calendars): scheduled opens, closes, holidays, and early closes. Obligation: pinned package version; calendar supplies time ordering, not prices.
- [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading/blob/main/LICENSE): architecture reference only; no code or data copied. Obligation: root is MIT and factor families add obligations; preserve notices if reuse is ever approved.
- [Packt ML4T Second Edition companion](https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition): learning reference only; no code or data copied. Obligation: no repository LICENSE was verified, so do not copy or redistribute its code.

## Model ladder and negative results

| Model | Mean development IC | Nonnegative vs B1 | Outcome |
|---|---:|---:|---|
| B0 | N/A | N/A | no-signal comparator |
| B1 | 0.017149 | 1.000000 | selected |
| B2-price_volume-a0.001-l0.1 | -0.003549 | 0.545455 | rejected by frozen promotion rule |
| B2-price_volume-a0.001-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.001-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.01-l0.1 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.01-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.01-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.1-l0.1 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.1-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-price_volume-a0.1-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.001-l0.1 | -0.000702 | 0.454545 | rejected by frozen promotion rule |
| B2-fundamentals-a0.001-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.001-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.01-l0.1 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.01-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.01-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.1-l0.1 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.1-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-fundamentals-a0.1-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.001-l0.1 | -0.005876 | 0.545455 | rejected by frozen promotion rule |
| B2-combined-a0.001-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.001-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.01-l0.1 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.01-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.01-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.1-l0.1 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.1-l0.5 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| B2-combined-a0.1-l0.9 | N/A | N/A | failed: RuntimeError: undefined rank IC from constant or missing validation predictions |
| M1-price_volume-d2-r0.05 | -0.006536 | 0.454545 | rejected by frozen promotion rule |
| M1-price_volume-d2-r0.1 | -0.006056 | 0.454545 | rejected by frozen promotion rule |
| M1-price_volume-d3-r0.05 | 0.013891 | 0.454545 | rejected by frozen promotion rule |
| M1-price_volume-d3-r0.1 | 0.011974 | 0.545455 | rejected by frozen promotion rule |
| M1-fundamentals-d2-r0.05 | 0.003763 | 0.454545 | rejected by frozen promotion rule |
| M1-fundamentals-d2-r0.1 | -0.001523 | 0.545455 | rejected by frozen promotion rule |
| M1-fundamentals-d3-r0.05 | 0.000975 | 0.545455 | rejected by frozen promotion rule |
| M1-fundamentals-d3-r0.1 | -0.002560 | 0.454545 | rejected by frozen promotion rule |
| M1-combined-d2-r0.05 | -0.005552 | 0.454545 | rejected by frozen promotion rule |
| M1-combined-d2-r0.1 | -0.003962 | 0.454545 | rejected by frozen promotion rule |
| M1-combined-d3-r0.05 | 0.003623 | 0.454545 | rejected by frozen promotion rule |
| M1-combined-d3-r0.1 | 0.008695 | 0.545455 | rejected by frozen promotion rule |

## Failure-diagnosis status

- No historical diagnosis is included: no primary artifact establishes the claimed prior failure. The rank-IC missing-value regression is defended by a focused test, not presented as a run observation.

## Formula appendix

- Weekly rank IC: Spearman correlation of prediction and realized five-session excess-return ranks within each eligible decision date; headline is the mean across dates.
- Net weekly return: `NAV_w / NAV_{w-1} - 1`, with the initial week divided by USD 100,000.
- Cumulative return: `final_NAV / 100000 - 1`; cost drag: `(final_gross_NAV - final_net_NAV) / 100000`.
- Annualized volatility: sample standard deviation of weekly returns × `sqrt(52)`; Sharpe: weekly mean / sample standard deviation × `sqrt(52)` at zero risk-free rate.
- Sortino: weekly mean / root-mean-square downside return × `sqrt(52)`; maximum drawdown: minimum `NAV / running_peak - 1` including initial NAV.
- One-way turnover: sum of absolute trade notional divided by NAV immediately before each fill event.
- Cost model: 1 bp fee + 5 bps slippage per one-way fill; sensitivity reruns use 0, 3, 6, and 12 bps. The 0-bps row is a sensitivity, not the evidence headline.

## Limitations

- The frozen 30-symbol universe is selected from current large liquid US equities and does not reconstruct point-in-time index membership; survivorship and selection bias remain.
- The final holdout is one calendar year and was revealed once for this immutable run; it does not establish regime-invariant performance.
- Adjusted daily-bar opens and closes are execution proxies, not broker fills, and the simulator does not model intraday market impact.
- SEC CompanyFacts tags and issuer reporting practices vary; missingness indicators and fold-local feature drops expose but do not eliminate that measurement risk.
- This is paper trading only: no capital, broker routing, live trading, investment advice, guaranteed return, or claim about Looloo proprietary systems.
