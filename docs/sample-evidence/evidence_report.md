# Cross-sectional equity return-ranking evidence report

Run `20260714T115337558131Z-d5871533` · contract `finance-ml-v1` · generated `2026-07-14T11:56:20.596765+00:00`

> **SYNTHETIC FIXTURE RUN — pipeline validation only; not hiring or investment evidence.**
>
> **Report-only preview.** This file is a copy of a generated `evidence_report.md`, published so reviewers can read a full run without installing anything. The CSVs, JSON manifests, and JSONL event logs named in "Reviewer path" below are produced locally by an actual run — `artifacts/` is git-ignored and intentionally not committed (the public-evidence allowlist also excludes symbol-level data and event logs). Reproduce a run to inspect them.

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

- Data manifest hash: `d5871533d495fab0d10668cf86a803356647934e20815e54b05cf0dc4221510b`; source mode: **synthetic**.
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

## Artifact index

- `active_run.json` — `f396820b83f7a2a604672f5f60ca021a8ee2b5c68d4eab3625a7f18061b3f999`
- `complete_history_subset.json` — `0518625dd7fdaa603ac55a09bb64a2a520710530db130a4379b4d827ed9a9531`
- `data_artifact_manifest.json` — `1e444f1be6ae8b859d0aee3bc03aa51c48a95b4bf469b5c922962cab3b8c8e4e`
- `data_build_summary.json` — `f4f93191ab2584543e630fdfbbbf4290be9559477ea855b449df901ad4b50443`
- `development_rows.csv` — `4b94697f93aa114faa47ef2f1e29fd14aba764b88db8124c88efc4bf65e74c25`
- `experiment_records.jsonl` — `79b59eb0ca7a392f097360fceb48faacd96483d76668411b4ac39607c364c82d`
- `feature_bars.csv` — `47f495560ae5c081d0a02f62a0cc3378e34ba31c0c0b519f0f61ca07fe49fd51`
- `feature_manifest.json` — `6b7d456be406ebbe3a8c74a8374f036729fdf50eb624f7b7223cfda8a88e34b9`
- `holdout_reveal.json` — `368cd2aec77ae164d048325cd515b73dcbbe2fecd1d5bdafd3d89ea1bc0d9408`
- `input_diagnostics.json` — `0932c102203b1096681bb2f7c812db1be0acb074add531634a4ed305b33aa103`
- `label_fill_bars.csv` — `44d7db6c55e5a96db9aa60dc4b4f95ef37a4f9c19af8d31cffbb76115e651416`
- `label_manifest.json` — `8e4914356653fafa678be2643602ee19699948369c46ace40a0d51baf2722adf`
- `label_skips.csv` — `87d265a9b930ed15ee5dab09fc3ca8b656ea378eb0a0531d004cb4888e5f12a6`
- `runs/20260714T115337558131Z-d5871533/B0_fold_metrics.csv` — `60c91b0e8e22dd68414521f0416ec8ff9ed0da4b6bbd2418dba68f9e46239dd7`
- `runs/20260714T115337558131Z-d5871533/B1_fold_metrics.csv` — `7ad7f6b6ec91305bd3da1182f37557ceb52b413cbec83586f653e3650ea6d036`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.001-l0.1_fold_metrics.csv` — `b34d2d77b94fa206d545c2bfca7acf5fec50570df511ea3c97ea1dabeaa0ba37`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.001-l0.5_fold_metrics.csv` — `4ef44d8c963192d13a236cf12321bb3aea6e12972bd674cb7a3a24f4df61452d`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.001-l0.9_fold_metrics.csv` — `bbf72af7c65cf46dcc5a95d806a6209ff562899aaa889bbcaf569300ca00679e`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.01-l0.1_fold_metrics.csv` — `40e9b32cc6dd19def66ae378961b5907bb0a5b883c376403f2556502c529a63e`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.01-l0.5_fold_metrics.csv` — `704299451445a64f98bac255894d177196fd492eaf5540c60f25453483157cbf`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.01-l0.9_fold_metrics.csv` — `5d517523249d095f23ebd2d05b67cb0fe722099d6baa323c4f1f9454e8edb4c5`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.1-l0.1_fold_metrics.csv` — `d7eece6961a390813430d69b82c0311874aec554a6f24702c698f2ce924c2cec`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.1-l0.5_fold_metrics.csv` — `4ac7390f719bda59c194684f92426899179d66e1ff8db6a3350c3d742c3c8907`
- `runs/20260714T115337558131Z-d5871533/B2-combined-a0.1-l0.9_fold_metrics.csv` — `e4c17a34afc92210f03dce37edd73c2537ccc1ebe59b6d2a9b76b0957992f844`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.001-l0.1_fold_metrics.csv` — `27e5a8849f5cc50b35ba87175601d20a916d344bb4875efba4852ded947b5c4d`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.001-l0.5_fold_metrics.csv` — `5ad2adc8873ce5317bc23a91582bcd3c5c0fdec1e31dfffc020558f8783e7072`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.001-l0.9_fold_metrics.csv` — `a6c30ffd4a07052922bebe0fac810f765216d02a9202ec0329cfa4abdca1e7e2`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.01-l0.1_fold_metrics.csv` — `67ae3178d4589b0b2fa80242db421f141e4841bbf5f5da47093d1477c77fe82a`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.01-l0.5_fold_metrics.csv` — `1ca64943c3d6e2879e8932f6f47adefa047073d701304fa37d0efe17a726f04c`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.01-l0.9_fold_metrics.csv` — `c33ac0b8de1b03c195969e1f7bccd470c83011636d23488eceb4fb1b0c7de3d3`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.1-l0.1_fold_metrics.csv` — `65089c958f7acab117c7ef14f0a7129cf76f59797313b64260f44cfede8c89de`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.1-l0.5_fold_metrics.csv` — `8905c65c55830f1587bd3503e03968576c97e0d1de3a591c718c355e1869139f`
- `runs/20260714T115337558131Z-d5871533/B2-fundamentals-a0.1-l0.9_fold_metrics.csv` — `a8d4dec4d6a6752e87ae0bcb666ea0eac10d7619a47b5c4d36a3d6b6ac15e9c1`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.001-l0.1_fold_metrics.csv` — `022118649aa8366c2e9cdc5becdf3c74f26ed5974f293a0c6c03f04a284c245d`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.001-l0.5_fold_metrics.csv` — `9354019bc0c3d91141bcc12ce31bbc6f0f49d676429a5a0dd4b9bdbb18607e87`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.001-l0.9_fold_metrics.csv` — `4f7a312279831e2af165ece50fdeb68e470b7134988f73271ab150edca0076cf`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.01-l0.1_fold_metrics.csv` — `f8e14804274e7bc8b681c71a128b3ddf665f2a4e4da03ebef55f192df37710a4`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.01-l0.5_fold_metrics.csv` — `da613854a7363b7932074fb23bf267727cc14106e2fc467461bb8fff37e60b37`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.01-l0.9_fold_metrics.csv` — `2cdefba29915afd6b305c3882a56bd4e31dcb9d2937ee929eb5bb8cd2a0f6466`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.1-l0.1_fold_metrics.csv` — `efede02e3d2507ee763a19ec6ce7648e959f57116ab4d5679eea900bdfc488db`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.1-l0.5_fold_metrics.csv` — `f4e406d082c5f69fa01651c0ba6864ee93d19b39c4ffd2b96ec2e55e4f363e07`
- `runs/20260714T115337558131Z-d5871533/B2-price_volume-a0.1-l0.9_fold_metrics.csv` — `02637db8b9777fee9f0cb626a672f660b15260f6829a5ef1fb5faa468cc1edb3`
- `runs/20260714T115337558131Z-d5871533/M1-combined-d2-r0.05_fold_metrics.csv` — `99113f19e0dbe653d23049e34029c1ecbb7602b7c7b803d0e17e82671cd79cfa`
- `runs/20260714T115337558131Z-d5871533/M1-combined-d2-r0.1_fold_metrics.csv` — `69ab2e03e0aa57924f0da24922993adbd7092990dd4a41b968d37387aed947f1`
- `runs/20260714T115337558131Z-d5871533/M1-combined-d3-r0.05_fold_metrics.csv` — `0eed598726cf3bbdf0596565e9cde63b02f4d3c9ed89a8cef3041b76482d6ab5`
- `runs/20260714T115337558131Z-d5871533/M1-combined-d3-r0.1_fold_metrics.csv` — `bbcdcf0f6c2f38535700ec3e3c7664c356121737066521964ef929bed29e845c`
- `runs/20260714T115337558131Z-d5871533/M1-fundamentals-d2-r0.05_fold_metrics.csv` — `c88b87845a83e2403015bbbdff757c3447a6c8aedc5df1065483ac994e3bae06`
- `runs/20260714T115337558131Z-d5871533/M1-fundamentals-d2-r0.1_fold_metrics.csv` — `13351cf1e4022524de7ca118c37028a9dc847353d8d1a5d02fb3cdf8f9c1d98a`
- `runs/20260714T115337558131Z-d5871533/M1-fundamentals-d3-r0.05_fold_metrics.csv` — `e800e027134c723a6bfeb581861805fc20063a8b7644264fc116f9caa8f6af51`
- `runs/20260714T115337558131Z-d5871533/M1-fundamentals-d3-r0.1_fold_metrics.csv` — `9d547fb3a8968ccd70b260eb1a49ab730aef85e501be1c4493f26d0f674c256d`
- `runs/20260714T115337558131Z-d5871533/M1-price_volume-d2-r0.05_fold_metrics.csv` — `d0569665e532f69d8036de20a6f7c7b00a27c5c967fc5607bf04971ab0022d19`
- `runs/20260714T115337558131Z-d5871533/M1-price_volume-d2-r0.1_fold_metrics.csv` — `1910cef0545d2017fdea49610560ad5aa5e401d978abe01b8b8cde6d6e2f1b74`
- `runs/20260714T115337558131Z-d5871533/M1-price_volume-d3-r0.05_fold_metrics.csv` — `4494daa6ab21ef67eba794cd37062821f89c95da2e63f3825efb8b0ab9b5f40a`
- `runs/20260714T115337558131Z-d5871533/M1-price_volume-d3-r0.1_fold_metrics.csv` — `4fe10e4f05ac0c822bd92eb75e08a1377d72d6cb36e4bd2182ebe4d6db911286`
- `runs/20260714T115337558131Z-d5871533/development_oof_predictions.csv` — `000279afbce5d1d57e9af1f29ecc0cf2aa842bcf929a6e2fe3d720f4067caaed`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/B0.jsonl` — `3bb01d12fefcb3a25b60d3c7ddeae4538824067af0212d55ff3d3d5f44f1aa0e`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/B1.jsonl` — `161e47249562225a33318751d6a2ea788bf9b414f817dc1dcd41a60d048adda0`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/B2-combined-a0.001-l0.1.jsonl` — `fb3f80850744f1421baac9490b26962d5d9614ed8336464cae0d8260309cf8d2`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/B2-fundamentals-a0.001-l0.1.jsonl` — `01166d600ba2d420e2c18043a92c44fc87676fd7b4ba76d899f577c2eeec5a2e`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/B2-price_volume-a0.001-l0.1.jsonl` — `c72babd3ddcb6113db0540cb28b8fdc8b274b1275a90c619712bae108960ed14`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-combined-d2-r0.05.jsonl` — `caa2fd4f8741044dd6b0a025bb0eec3b575c2a8a610fa47338f038ecc6584170`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-combined-d2-r0.1.jsonl` — `be8f2a16fa473b20d0615b598cf2da8eac08ffe77bce28fd97d38c469610113a`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-combined-d3-r0.05.jsonl` — `a62e9b270f732fc9f6bcfbc116064e822fe6b10288b463aefac7527a996a80c3`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-combined-d3-r0.1.jsonl` — `082554920cb2928e64a52f95eb9a6d915aa3acc0c6dd8bfcb6b527faab1b1fc3`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-fundamentals-d2-r0.05.jsonl` — `8f36135d340dc404603a74df69eb166a4ed690c7b44ca533bc7b46d6066e5156`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-fundamentals-d2-r0.1.jsonl` — `3b627bdb457893a3fec01921d924959a5ccddf2c4f2177c2e56b6f2747a36576`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-fundamentals-d3-r0.05.jsonl` — `ca7bc18bfa09fc5604f0f0fabf251213a965099471ea72e3390dd3403aae79a7`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-fundamentals-d3-r0.1.jsonl` — `42dccc74c7276339c9595aaf07081035c29cedb6c6bcab56b845971f62c21ce2`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-price_volume-d2-r0.05.jsonl` — `ac3051bb60a2f3f2a39d6cede3bf26a758f9ec58f9cb048c3f242d89c8bbd737`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-price_volume-d2-r0.1.jsonl` — `383b0049438f2ebe2b2910b658ad1b7af742149f1d499fb6ba4387fa36a2dd75`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-price_volume-d3-r0.05.jsonl` — `1bd816bc9564a4b2cacbdcf9ca88f82a4257a4b318240a0f7aa8bfc48f4593d2`
- `runs/20260714T115337558131Z-d5871533/development_paper_events/M1-price_volume-d3-r0.1.jsonl` — `d91b34cdb73efb4d29657cbb169cc076355d791a68be44eb0580edd45cb349e1`
- `runs/20260714T115337558131Z-d5871533/development_portfolio_comparison.csv` — `9fd118c8750d642cb4ef54aa97f0c2eec8e88f27975028f8a7d2b71f77e5090d`
- `runs/20260714T115337558131Z-d5871533/evaluation_manifest.json` — `ebaad6a3d47233c1b725e2e92296fc999208905783c61588797c96f7998e7625`
- `runs/20260714T115337558131Z-d5871533/evaluation_summary.json` — `aa57d85291bdad6160b89b0e4e6b6d52b4aba9980c9ebb19eda5196b42102f80`
- `runs/20260714T115337558131Z-d5871533/experiment_records.jsonl` — `79b59eb0ca7a392f097360fceb48faacd96483d76668411b4ac39607c364c82d`
- `runs/20260714T115337558131Z-d5871533/experiment_results.csv` — `e61d1ea2865da681d293a3502c558a50f42f53f35dba64b2f353669953c6df3f`
- `runs/20260714T115337558131Z-d5871533/fold_metrics.csv` — `544c9cd1772339cce736c7b164856e98525e9a9f5f5f8c6478fc8019fa4be32f`
- `runs/20260714T115337558131Z-d5871533/folds.json` — `0a936270720541acbcda6132a5da2b15a331fe4e6980b114c7c4e26a593c3cf1`
- `runs/20260714T115337558131Z-d5871533/holdout_features.csv` — `8c96ce62c9f3958929fe1a755397b8e78c29b26631c293a3af710168c588814d`
- `runs/20260714T115337558131Z-d5871533/holdout_rank_ic_bootstrap.csv` — `b0cdbaaf96d921314c7db4c517edd8dfde1f3c0a64f9a0333c85bb7a96acf8d5`
- `runs/20260714T115337558131Z-d5871533/holdout_rank_ic_by_date.csv` — `813fb1e3e45ef5f2009b389f01aafd39bdaee450209a9cfa73d0167bfbbcd570`
- `runs/20260714T115337558131Z-d5871533/model.joblib` — `f56bd6c4c1df33ce79cefb3c885edbd66d942457e03f1649b16a24045a3e2486`
- `runs/20260714T115337558131Z-d5871533/model_manifest.json` — `823bc21e5081eece80f7bf18175c958cffe3032b38e5463cb51ca8c9c034ce11`
- `runs/20260714T115337558131Z-d5871533/model_oof/B0.csv` — `f7c3c41d96e0cb5fc64893dc5e9401ed99a149d883d685178f8fe7d481a2be69`
- `runs/20260714T115337558131Z-d5871533/model_oof/B1.csv` — `70f04b271ac233f981156b596b84b829e42feccbcc92d7afb37555be73a54590`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.001-l0.1.csv` — `18b16a898680dad52031524f3926ca7ff33049eb924822560927f575c1726040`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.001-l0.5.csv` — `36dd53e2ccb8bae68764f209722d9c3d71c91d3a3ced6df17e916edc24615960`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.001-l0.9.csv` — `b4c4f409771a708a915093ef7ee00ebc1e8b2d19ea8219dc4cb622050963fd53`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.01-l0.1.csv` — `244f47aad6e91b4d1686b84462871dc1e7b2b6b30489febe860579a93d2728db`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.01-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.01-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.1-l0.1.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.1-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-combined-a0.1-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.001-l0.1.csv` — `e96573fbfcf5bae85082d92205c231f3bbd64d639cc54a2d3306873aad76e9ac`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.001-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.001-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.01-l0.1.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.01-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.01-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.1-l0.1.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.1-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-fundamentals-a0.1-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.001-l0.1.csv` — `ec000edaf07a3085f810c363c6997092a4f65d4710f66c5eb56ed0957e04ae4f`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.001-l0.5.csv` — `0fe352f822bd0da1d32fb96cdaceebdc27f89d51d9fe1043e31a66e0b60a9d7b`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.001-l0.9.csv` — `b4c4f409771a708a915093ef7ee00ebc1e8b2d19ea8219dc4cb622050963fd53`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.01-l0.1.csv` — `244f47aad6e91b4d1686b84462871dc1e7b2b6b30489febe860579a93d2728db`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.01-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.01-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.1-l0.1.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.1-l0.5.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/B2-price_volume-a0.1-l0.9.csv` — `376d03d20d56aa9d12d837f25081bdb568e7744dd78673cf76709576c0953168`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-combined-d2-r0.05.csv` — `83e1045d9ffb73f167e7170ea5fa1e3957147c6e132c0ba8ee7cfa777dd61c13`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-combined-d2-r0.1.csv` — `63d72c23578b2fcfe85f7f44f03fbe2755e98ec6a15c29bc10917ca42ce1c290`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-combined-d3-r0.05.csv` — `07fbe0b293c2d44c4958c301091d2788609b3b6ef85f4bfc09ae5af1467d5588`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-combined-d3-r0.1.csv` — `3cf33e150cfa4616b48c92d6ec61f700018a54ba5863f2042adc1f444852a2eb`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-fundamentals-d2-r0.05.csv` — `f5715f3fe94c28cb9f7748d299850ccc18f8e7f5478590d7a0ff990531e6bdf9`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-fundamentals-d2-r0.1.csv` — `409c3f5cbd9a98825788449e07ad7fbc527d280235cf951edb0207780f9022b3`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-fundamentals-d3-r0.05.csv` — `19b93ff0b04e4a7f5b82ff4aaf6ecb4ef1b8567a5c439dc2bb1d544b4cbc0709`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-fundamentals-d3-r0.1.csv` — `aa7c5599fef7fec40e060344b932841994fb1dc26ca13e899def0ec99fed784b`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-price_volume-d2-r0.05.csv` — `344af552d28937ed22a67a8280f530ded3db26519f8737c021f64091dffb9d7e`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-price_volume-d2-r0.1.csv` — `711e8db1aa2e0323d2e140c0884e56f595657e2eef7cb988e61fb749f6d1676a`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-price_volume-d3-r0.05.csv` — `2dffd747d783b2ffd2694e9a809b72287af9bdfe4ab140f9e86a2e157ffa01cc`
- `runs/20260714T115337558131Z-d5871533/model_oof/M1-price_volume-d3-r0.1.csv` — `aac80b76e3f382744a84f1740dfc559f3015f056dfa09527cd565e00ada22e42`
- `runs/20260714T115337558131Z-d5871533/model_oof_index.json` — `b71dc4f14cc773d398359cc3e6e8d15b2bf5db8027c1f5a8a6ceb977f11f4d17`
- `runs/20260714T115337558131Z-d5871533/paper_cost_sensitivity.csv` — `41317566fed4c0571b3f5da49940036cd99e3e4216c810630c3b5e8c0dcb8731`
- `runs/20260714T115337558131Z-d5871533/paper_events_B0.jsonl` — `c2d12b28ca83a6b0aba7a15a5ebabc3f107ab66d4efda44fdce7d9a5e7915700`
- `runs/20260714T115337558131Z-d5871533/paper_events_B1.jsonl` — `7f0dcbd921831bdf3e492a9bf2bf42aa32e4092b3803c4d17920a652be53af8f`
- `runs/20260714T115337558131Z-d5871533/paper_events_complete_history.jsonl` — `b2baf0b4537395424adff1543090fc6afa6361ffad30775df5afa26686df3a05`
- `runs/20260714T115337558131Z-d5871533/paper_events_cost_0bps.jsonl` — `6d16be18c8549b2daa4c0a3ce2ac8a3685e0f03c8513f28e20cab4cf633488df`
- `runs/20260714T115337558131Z-d5871533/paper_events_cost_12bps.jsonl` — `d4a459d4249f7d797d03a6d96f7e016fbbfd6723b6e90af71338ffae1aee715a`
- `runs/20260714T115337558131Z-d5871533/paper_events_cost_3bps.jsonl` — `e9fb65a363e903bff94baf61caf4b95a8619315f16276ef504f51cb468fc0202`
- `runs/20260714T115337558131Z-d5871533/paper_events_missing_bar.jsonl` — `231566032813865de9a14091f5179569225974da8e801aee93955f2d93fbd339`
- `runs/20260714T115337558131Z-d5871533/paper_events_selected.jsonl` — `d6a5c96ede2a1ca9ebb77e4153fbf7fe7f1fab4885f454aae6f7ef9728e78327`
- `runs/20260714T115337558131Z-d5871533/paper_manifest.json` — `45420ca706fb799c7ae2c5b05afed57b995cb472f9dcc9b52143ba8562a504a8`
- `runs/20260714T115337558131Z-d5871533/paper_model_comparison.csv` — `94db5f1df68d793ae123dec59af651265333536927b1d52f6974e7ce568818c1`
- `runs/20260714T115337558131Z-d5871533/paper_skip_counts.csv` — `f8bb0f01253f4a5e7aa302aac8b841e6149185294ddf327e392366b080d52cde`
- `runs/20260714T115337558131Z-d5871533/paper_summary.json` — `64eb5a18111a8f256b7506734288501a00da426f6c3d94d637e82856df527129`
- `runs/20260714T115337558131Z-d5871533/paper_top_tercile_excess.csv` — `45bfbae6a20fa6505d0ce5a3a307f013c4fd352a6efad4b078101601788254d2`
- `runs/20260714T115337558131Z-d5871533/paper_weekly_returns.csv` — `73ad16417bcbc6d65a24ae71f26526bdaa2086d2d2acae14b6777909400f5aab`
- `runs/20260714T115337558131Z-d5871533/predictions.csv` — `02f3e56adf179aa7d3105d136c91463f653626bf033ff1a408fd4d690050427c`
- `runs/20260714T115337558131Z-d5871533/predictive_robustness.csv` — `f21b565cc8d5a7d41d87f5233808de37377c6ef8563cde5655be93bb39576af6`
- `runs/20260714T115337558131Z-d5871533/train_summary.json` — `19a13ab8b171b1d7a771adbcbc35dc0585289dcd88154188d7c7498ce44a21ea`
- `sec_facts.csv` — `c254b2be0093996254b5bec0f60f5e3a6482fa7ce27dceaab6f9311bc544794c`
- `sec_manifest.json` — `317bccd0956847a73044319f2228afdeb2b39833fc95d35385c313e179a05fe7`
