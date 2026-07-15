# Finance ML portfolio-project direction comparison

Surveys feasible directions for the same goal as the [Looloo project-evidence rubric](looloo-project-evidence-rubric.md): decision-ready evidence for the later selection stage, which alone picks the **portfolio project** and applies the approved tie-break order. **This document does not select a project.** It compares four feasible, candidate-owned directions against the existing 100-point rubric so that later selection can choose without inventing a data source, validation family, or scope decision.

**Tagging convention** (matches the rubric asset): `[EXPLICIT]` = stated directly by a cited primary source. `[INFERENCE]` = my reasoning from explicit facts; a reasonable reader could disagree. `[APPLICANT CONSTRAINT]` = drawn from the map's applicant-supplied baseline, not independently verifiable. `[REUSED WORK]` = a dependency, library, dataset, or repository that is *not* candidate-authored. `[UNKNOWN]` = could not be verified with the tools available. Unmarked prose in the scoring tables is rubric-scoring *judgment* — see "How scores were assigned" below.

All primary sources were accessed **2026-07-13** unless a page's own last-updated metadata is quoted separately.

---

## 0. Scope and constraints carried from prior research

- Every direction stays inside the project's boundary: historical research plus a no-capital **paper-trading demo**. No live capital, brokerage execution, or investment-advice framing. `[APPLICANT CONSTRAINT]` / `[EXPLICIT]`.
- Every direction is sized against the applicant's stated baseline: a non-technical degree, independent capability on a classical-ML project, and persistence/initiative as the strongest differentiators — not against an imagined maximal build. `[APPLICANT CONSTRAINT]`.
- The 100-point scale and its eight weighted criteria are reused unchanged from the existing rubric; this document adds no new criteria and rebalances no weights: Problem Formulation & Literature-Grounded Research 12, Data Corpus Engineering 14, Modeling Depth & ML Foundations 18, Experimentation Rigor & Reporting 14, Performance Diagnosis 10, Productionization & Engineering Fluency 16, Market/Domain Fluency 8, Ownership/Judgment & Culture-Fit 8. **12+14+18+14+10+16+8+8 = 100.**
- Vibe-Trading's dedicated audit verdict is **reference repository** (of reject / reference repository / bounded component / foundation): no fitted-model dependencies worth inheriting — zero PyTorch/TensorFlow/XGBoost/LightGBM in its own dependency tree, since its 460-factor "Alpha Zoo" is deterministic closed-form formulas, not trained models — plus disproportionate multi-license attribution overhead and an open, unresolved "not yet safe for real trading" audit checklist. `[EXPLICIT]` (audit finding; see [vibe-trading-audit.md](vibe-trading-audit.md)) Where Vibe-Trading appears below it is illustrative context consistent with that verdict, not a re-derivation of it.
- This comparison is a research input the eventual **build brief** will link rather than duplicate; it does not itself constitute that brief.

### How scores were assigned

Each direction is scored as it would land **if built to its smallest complete implementation, competently** — not a hypothetical maximal version, and not a claim that any of this has been built. This is a deliberate separation of concerns: the rubric score approximates the *achievable evidence ceiling*; a direction's **completion risk** (a separate, explicitly labeled judgment per direction, not part of the 100-point total) approximates the *probability of falling short of that ceiling*. All eight scores per direction are therefore `[INFERENCE]` — my structured application of the rubric's own published band language (quoted from `looloo-project-evidence-rubric.md`) to each direction's concrete design, not a source-verified fact. Every score sits at one of the rubric's four published anchor points for that criterion (never an invented in-between number), so every cell is traceable back to the existing instrument.

### Proprietary / personal-use data limits, flagged explicitly

Every direction below touches at least one data source whose owner restricts reproduction/redistribution to personal or internal use. None of the four directions requires data the applicant could not legally use for a research/paper-trading portfolio project — but "usable for research" is not the same as "freely redistributable," and this document keeps that line explicit rather than blurring it:

- **Free for any purpose, no personal-use restriction at all** (the strongest tier): SEC EDGAR (filings/XBRL — a U.S. government work, explicit public-domain reuse statement) and the U.S. Treasury's own yield-curve data — `fiscaldata.treasury.gov`'s own API documentation states its data is "offered free, without restriction... for non-commercial or commercial purposes." `[EXPLICIT]` `home.treasury.gov`'s publication of the same yield-curve series, as a federal government work, defaults to the same public-domain status under 17 U.S.C. §105, though `home.treasury.gov`'s own site-policies page — unlike `fiscaldata`'s — does not carry its own dedicated reuse notice, a minor asymmetry worth naming rather than assuming away. `[INFERENCE]`
- **Free to access, personal/internal use only, redistribution requires written consent** (a real but bounded, fully disclosed limit present in every direction here): Alpaca's market data and paper-trading execution (all four directions use Alpaca for both) and Cboe's VIX index (Direction 2 only). `[EXPLICIT]` The practical implication, already reflected in every "smallest complete implementation" below: build a **re-runnable ingestion pipeline**, never commit raw vendor price dumps to the portfolio repository — which is also what the existing rubric's own Data Corpus Engineering criterion independently rewards.
- **Non-authoritative but openly licensed** (used only as an optional cross-check, never load-bearing): the community `fja05680/sp500` MIT-licensed CSV in Direction 1. `[EXPLICIT]`

No direction depends on Yahoo Finance/`yfinance` (excluded below on legal-ambiguity grounds) or on any dataset this research could not verify the license of.

---

## 1. Directions considered and not carried forward

Named briefly for judgment/originality evidence, not scored — carrying more than four would violate the ticket's "exactly four" bound.

- **Credit-risk / loan-default prediction.** Real Finance-ML territory, but has no natural **paper-trading demo** and is not a trading decision, which conflicts with the target role's explicit "(Project Algorithmic Trading)" title and this map's paper-trading boundary. `[INFERENCE]`
- **Deep reinforcement-learning trading agent** (e.g., an RL policy trained directly on account state/reward, FinRL-style). Legitimate ML depth, but reward-hacking, simulator-to-reality gap, and weak leakage-auditability make it a poor **smallest complete implementation** for a junior-level, live-interview-defensible portfolio project; better as a later extension on top of a proven supervised baseline than a starting direction. `[INFERENCE]`
- **Yahoo Finance / `yfinance`-based direction.** Excluded on the ticket's own legally-ambiguous-data criterion: Yahoo's Terms of Service prohibit "access[ing] or collect[ing] data... using any automated means... without our express, prior permission," and the official Yahoo Finance API was discontinued in 2017 after Yahoo found it violated those terms — `yfinance` and similar libraries scrape undocumented endpoints Yahoo has not authorized. `[EXPLICIT]` ([Yahoo ToS](https://guce.yahoo.com/terms?locale=en-US); [Yahoo Terms §4/§8](https://legal.yahoo.com/xw/en/yahoo/terms/otos/index.html)) Notably, Vibe-Trading itself routes two of its eighteen data loaders through Yahoo (`yahoo_loader.py`, `yfinance_loader.py`) — a concrete illustration of why "a reference repository uses it" is not the same as "it is safe for a candidate's own redistributable pipeline." `[EXPLICIT]` (direct repository read, §4 below)
- **Building directly on Vibe-Trading as the agentic direction's foundation.** Excluded from this comparison, and now confirmed by the dedicated audit's **reference repository** verdict: Vibe-Trading's own dependency tree has no PyTorch/TensorFlow/XGBoost/LightGBM at all — its 460-factor "Alpha Zoo" is deterministic closed-form formulas, not fitted models — so there is no verified ML-model work to inherit even for an agentic direction, on top of a ~1,900-file, actively developed framework (470+ closed PRs by mid-July 2026, 18 data loaders, 10 broker connectors) where a junior candidate's own contribution would be a small fraction of the system if adopted wholesale, disproportionate multi-license attribution overhead, and an open, unresolved "not yet safe for real trading" audit checklist. `[EXPLICIT]` (direct repository read; [Vibe-Trading audit](vibe-trading-audit.md)) Vibe-Trading is used below only as illustrative contrast for Direction 4's intentionally thin, candidate-authored agent layer.
- **Options-pricing / Greeks ML direction.** Considered; free, authoritative, point-in-time options-chain history (not just index-level implied vol) is materially harder to source for free than equity/ETF spot data in the sources checked here. Not exhaustively verified against every vendor, so this exclusion is held loosely. `[INFERENCE]` / `[UNKNOWN]`
- **ETF/equity pairs statistical arbitrage** (cointegration-based market-neutral relative value). A fully designed, fully scored candidate in an earlier pass of this comparison — reconsidered and cut in favor of the Treasury yield-curve direction below to keep exactly four directions and to sharpen the data-licensing contrast this research was specifically asked to surface. Its most useful finding is preserved here: a crypto-pair version (e.g., via a public exchange candle endpoint) was checked and rejected because Alpaca crypto positions are **non-marginable and cannot be shorted** — "Cryptocurrencies are non-marginable. This means that you cannot use leverage to buy them" — so a true market-neutral crypto pairs trade is not implementable on the same broker used for paper-trading execution elsewhere in this document. `[EXPLICIT]` ([Alpaca support](https://alpaca.markets/support/can-i-margin-or-short-with-cryptocurrency)) An equity/ETF pairs direction (e.g., Gatev, Goetzmann & Rouwenhorst's (2006) distance-rule strategy, *Review of Financial Studies* 19(3):797–827, extended with a trained entry/exit-timing classifier) remains a credible fifth direction a future revision could reinstate.

---

## 2. The four compared directions, at a glance

| # | Direction | Agentic? | Financial decision | Core data |
|---|---|---|---|---|
| D1 | Cross-Sectional Equity Return Ranking | No | Rank a fixed liquid-equity basket; long top / short bottom | Alpaca prices + SEC EDGAR fundamentals |
| D2 | Realized-Volatility Forecasting & Vol-Targeted Sizing | No | Size positions in 3–5 major ETFs by forecast volatility | Alpaca prices + Cboe VIX + FRED/ALFRED |
| D3 | Treasury Yield-Curve Forecasting & Duration Positioning | No | Rotate duration exposure across 2–3 Treasury-ETF tiers by forecast curve shape | U.S. Treasury par-yield data (execution via Alpaca) |
| D4 | Filing-Triggered Earnings-Drift Agent | Yes (thin, bounded) | Trade post-earnings drift on newly filed 8-Ks | SEC EDGAR filings/XBRL + Alpaca execution |

All four share one **paper-trading demo** endpoint (Alpaca's paper brokerage) so the eventual selection does not also have to resolve a second, direction-specific execution venue.

---

## 3. Direction 1 — Cross-Sectional Equity Return Ranking

**Financial decision.** Each rebalance, rank a fixed basket of large, liquid, continuously-listed US equities by predicted forward return; go long the top tercile and short the bottom tercile.

**Literature grounding.** Gu, Kelly & Xiu (2020), *"Empirical Asset Pricing via Machine Learning,"* *Review of Financial Studies* 33(5):2223–2273 — the canonical large-scale comparison of linear, tree, and neural-network models for exactly this cross-sectional return-prediction problem; finds trees/shallow nets beat linear benchmarks, and that *shallow* architectures dominate in this noisy, limited-signal setting (a citable, literature-backed reason to skip deep nets rather than add them decoratively). `[EXPLICIT]` López de Prado (2018), *Advances in Financial Machine Learning*, Wiley, ch. 7 — purged k-fold cross-validation with embargo, the standard fix for the overlapping-label leakage this direction's multi-day forward-return labels create. `[EXPLICIT]`

### Data sources

| Source | Provides | License / reuse / redistribution | Update cadence |
|---|---|---|---|
| Alpaca Market Data API (IEX/SIP-sourced free tier) | Daily OHLCV for the fixed basket, minute data to ~2016, 5+ years of history | `[EXPLICIT]` Personal/internal use is standard; Alpaca's Customer Agreement states "I agree not to reproduce, distribute, sell or commercially exploit the market data in any manner without written consent from Alpaca" — build a re-runnable ingestion script, never commit raw bar dumps to the repository. ([Customer Agreement PDF](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf); [data-provider FAQ](https://alpaca.markets/support/data-provider-alpaca)) | Same-day |
| SEC EDGAR XBRL `companyconcept`/`companyfacts` (`data.sec.gov`) | Point-in-time fundamentals (EPS, revenue, etc.); each fact carries a `filed` date distinct from the fiscal `end` date — e.g. Walmart's FY2007 `Revenues` fact shows `"end":"2008-01-31","filed":"2010-03-30"` in the live API | `[EXPLICIT]` U.S. government work; SEC states site information "is considered public information and may be copied or further distributed... without the SEC's permission." ([SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces); [privacy/reuse policy](https://www.sec.gov/about/privacy-information)) | XBRL facts typically processed "under one minute" after filing per official docs; nightly bulk ZIPs also published |
| fja05680/sp500 (community GitHub repo) — **optional secondary cross-check only** | S&P 500 historical membership snapshots, 1996–present | `[EXPLICIT]` MIT license. `[INFERENCE]` Explicitly non-authoritative: the maintainer's own README documents gaps in the earliest years and calls Wikipedia's "Selected Changes" table incomplete — treat as a documented limitation, not a load-bearing dependency. | Irregular, maintainer-driven (observed activity into mid-2026) |

### Schema & point-in-time semantics

No free, first-party, point-in-time S&P 500 (or comparable) constituent history exists — confirmed by targeted search plus a direct read of the best available free proxy (`fja05680/sp500`, MIT-licensed but self-described as imperfect). `[EXPLICIT]`/`[INFERENCE]` The smallest complete implementation therefore uses a **basket fixed once at project start** (e.g., ~30–50 large, liquid names spanning several sectors, selected from today's screen and held constant for the whole backtest) rather than a reconstructed month-by-month membership list. This is an explicit, named simplification, not a silent one: a basket chosen *today* still carries a mild survivorship flavor over a multi-year backtest (today's mega-caps partly earned that status by surviving), which is a materially smaller and fully disclosed bias next to the classic bug the rubric singles out — scoring *today's* full index membership as if it applied at every historical rebalance date. Fundamentals joins use the XBRL `filed` date as the availability timestamp, never the `end` (period-close) date, to prevent using information before it existed.

### Leakage & backtest risk

- **Overlapping-label leakage**: a 5-day forward-return label overlaps with neighboring observations' information sets — mitigated with purged, embargoed walk-forward validation (López de Prado 2018), not plain k-fold.
- **Point-in-time fundamentals leakage**: joining on `end` instead of `filed` would leak knowledge of a quarter's results before the 10-Q/10-K existed — the schema fix above addresses this directly.
- **Corporate-action leakage**: unadjusted splits/dividends can fabricate huge fake returns — requires verifying Alpaca's bars are adjusted (or adjusting them) and documenting the check, per the rubric's own worked example of this exact bug.
- **Basket-survivorship residual**: named above; the mitigation is disclosure plus a documented, one-time construction rule, not a false claim of full point-in-time correctness.

### Smallest complete implementation

- Fixed basket (~30–50 liquid names, ≥5 sectors) chosen once, held constant.
- Alpaca daily bars + SEC EDGAR XBRL fundamentals, joined on `filed` date.
- Target: next-5-trading-day forward return, cross-sectional tercile ranking.
- Baseline: cross-sectional momentum rank or ElasticNet; candidates: LightGBM/XGBoost, optionally a 1–3 hidden-layer PyTorch MLP as a literature-motivated comparison point (Gu-Kelly-Xiu's own finding that shallow nets suffice) — organic, not decorative, only if it stays shallow.
- Purged + embargoed walk-forward validation; tracked runs across feature/model combinations with a written negative-results note.
- Sector/regime-sliced diagnosis; one documented root-cause investigation.
- Packaged, tested Python pipeline; scheduled scoring; Alpaca paper long/short order submission with position/P&L logging.

### Candidate-owned vs. reused

`[REUSED WORK]`: Alpaca SDK, SEC EDGAR REST endpoints, LightGBM/XGBoost/scikit-learn/PyTorch, the optional `fja05680/sp500` cross-check file. Everything else — basket construction and its documented rationale, the ingestion/join pipeline, feature engineering, baseline and candidate model training code, the purge/embargo validation harness, diagnosis, packaging, scheduler, and paper-trading loop — is candidate-authored.

### Rubric scores

| # | Criterion (wt) | Score | Rationale |
|---|---|---|---|
| 1 | Problem Formulation (12) | **12 — Exceptional** | Gu-Kelly-Xiu (2020) is the direct canonical paper for this exact problem shape; gives a citable, literature-backed rejection of deep learning at this scale rather than an unexamined choice. |
| 2 | Data Corpus Engineering (14) | **9 — Solid** | Re-runnable pipeline, documented `filed`-date join, and a named, disclosed survivorship simplification — held below Exceptional only because no authoritative free point-in-time membership source exists to fully close that gap. |
| 3 | Modeling Depth (18) | **18 — Exceptional** | Baseline + ≥2 justified, literature-grounded candidates with a natural ablation surface (feature groups, tree depth, shallow-vs-linear) mapped directly onto the cited paper's own methodology. |
| 4 | Experimentation Rigor (14) | **14 — Exceptional** | Purged/embargoed walk-forward is a direct, textbook fit for the overlapping 5-day label; the larger feature/model grid naturally produces multiple comparable, trackable runs and genuine negative results. |
| 5 | Performance Diagnosis (10) | **7 — Solid** | Sector/volatility-bucket slicing is natural and gives several credible root-cause axes; Exceptional's full before/after bar is realistic but not guaranteed at minimal scope. |
| 6 | Productionization (16) | **10 — Solid** | Packaged pipeline + scheduled scoring + Alpaca long/short paper loop clears the Solid bar cleanly; a multi-week unattended run for Exceptional is a realistic near-term extension, not part of the minimum. |
| 7 | Market/Domain Fluency (8) | **5 — Solid** | Calendar, cost, and leakage basics are in scope by construction; deeper risk-metric fluency (Sharpe/drawdown with stated assumptions) is an added-rigor step beyond the floor, not automatic. |
| 8 | Ownership/Judgment (8) | **6 — Solid** | A specific, concrete iteration story is available and genuinely happened in this research: discovering no free point-in-time membership source exists and pivoting to a disclosed fixed basket. |
| | **Total** | **12+9+18+14+7+10+5+6 = 81** | |

**Completion risk, originality & live-interview defensibility.** *Risk*: Low–moderate — the point-in-time fundamentals join is the one piece likely to take longer than expected. *Originality*: basket construction, feature set, and model comparison are all candidate-specific design choices, not a copied notebook path. *Interview defensibility*: strong — every component (baseline, GBM, purge/embargo) is small and whiteboard-traceable, and the literature gives a ready answer to "why not deep learning first."

---

## 4. Direction 2 — Realized-Volatility Forecasting & Vol-Targeted Sizing

**Financial decision.** Forecast next-period realized volatility for 3–5 major, continuously-listed index ETFs (e.g., a broad-market and a couple of sector/style ETFs) and scale position size inversely with the forecast in a simple long paper-traded book.

**Literature grounding.** Corsi, F. (2009), *"A Simple Approximate Long-Memory Model of Realized Volatility,"* *Journal of Financial Econometrics* 7(2):174–196 — introduces HAR-RV, the field-standard, OLS-estimable realized-volatility baseline (daily/weekly/monthly RV components), reproducing long-memory and fat-tail stylized facts far more simply than fractionally-integrated alternatives. `[EXPLICIT]` This gives a direct, literature-backed reason to reject a black-box deep-learning volatility model as a *first* move: HAR-RV's own demonstrated forecasting edge at daily-data scale is the citable evidence for starting simple.

### Data sources

| Source | Provides | License / reuse / redistribution | Update cadence |
|---|---|---|---|
| Alpaca Market Data API | Daily (or intraday, for realized-vol construction) OHLCV for 3–5 ETFs | Same Alpaca terms as Direction 1 — no redistribution of raw bars without written consent | Same-day |
| Cboe official VIX historical CSV (direct file `cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`, linked from [`cboe.com/tradable_products/vix/vix_historical_data/`](https://www.cboe.com/tradable_products/vix/vix_historical_data/)) | Daily VIX close since 1990 (OHLC from ~1992) | `[EXPLICIT]` Cboe's own first-party, freely downloadable file; VIX data is Cboe's copyrighted intellectual property (confirmed via the FRED mirror's notes: "Copyright, 2016, Chicago Board Options Exchange, Inc. Reprinted with permission") — cite Cboe as source, do not claim ownership of the index. | Daily |
| FRED / ALFRED (Federal Reserve Bank of St. Louis) | Point-in-time macro vintages (e.g., yield-curve spread) via ALFRED's vintage-date API | `[EXPLICIT]` Free with a registered API key ([Terms of Use](https://fred.stlouisfed.org/docs/api/terms_of_use.html)); most series are public-domain federal data, but individual series can be separately copyrighted — e.g. `VIXCLS` itself is tagged "Copyrighted: Citation Required" on its own FRED page, which is exactly why this direction sources VIX from Cboe directly rather than through the FRED mirror. | Per-series (`VIXCLS` observed "Updated: Jul 10, 2026") |

### Schema & point-in-time semantics

The universe (3–5 of the largest, longest-continuously-listed US index ETFs) has **no membership-list problem at all** — unlike Direction 1, there is nothing to reconstruct point-in-time. ALFRED's vintage-date mechanism is *designed* for point-in-time correctness (it serves the value of a series exactly as it was known on a given historical date, before later data revisions), which is the single cleanest point-in-time story of the four directions. `[EXPLICIT]`

### Leakage & backtest risk

- **Realized-vol window construction**: computing "next 5-day RV" must only use returns strictly after the forecast date — a simple but easy-to-get-backwards indexing bug, worth a named unit test.
- **Macro-release timing**: FRED series are often revised after first release; ALFRED vintages must be used (not the latest revised value) to avoid leaking a later revision into an earlier forecast date.
- Simpler overall than Direction 1: a single (or few, non-overlapping) series means no cross-sectional purging is required — a genuine, direction-specific leakage-risk advantage worth stating plainly rather than treating all four directions as equally leakage-prone.

### Smallest complete implementation

- Universe: 3–5 major, liquid, long-lived ETFs (obvious, low-debate selection — no screening procedure needed).
- Data: Alpaca bars + Cboe VIX CSV + FRED/ALFRED macro vintages.
- Target: next-1-day or next-5-day realized volatility (regression).
- Baseline: HAR-RV OLS; candidate: HAR features + VIX + macro fed into LightGBM, compared against the baseline. A neural net is not obviously warranted for this low-dimensional regression — PyTorch/TensorFlow would likely be decorative here, and the honest technical choice is classical ML/statsmodels; this should be stated explicitly rather than added for appearance.
- Rolling-origin walk-forward validation.
- Regime-sliced (calm vs. crisis) diagnosis; one documented root-cause investigation of a missed volatility spike.
- Packaged pipeline, tests, scheduled forecast + inverse-vol position sizing + Alpaca paper rebalancing, logs.

### Candidate-owned vs. reused

`[REUSED WORK]`: Alpaca SDK, Cboe's static CSV, FRED/ALFRED API client, statsmodels/LightGBM. Candidate-owned: realized-vol computation, HAR-RV baseline implementation, the GBM extension and its feature engineering, the vol-targeting position-sizing rule, validation harness, diagnosis, packaging, and paper-trading loop.

### Rubric scores

| # | Criterion (wt) | Score | Rationale |
|---|---|---|---|
| 1 | Problem Formulation (12) | **12 — Exceptional** | Corsi (2009) is the field-standard baseline for exactly this target; a natural, citable rejection of GARCH-family/ARFIMA complexity in favor of HAR-RV's demonstrated parsimony advantage. |
| 2 | Data Corpus Engineering (14) | **14 — Exceptional** | Every source is first-party/official (Alpaca, Cboe's own CSV, FRED/ALFRED), the universe has zero membership-history problem, and ALFRED gives genuine point-in-time vintages — the cleanest, most fully-authoritative data story of the four directions. |
| 3 | Modeling Depth (18) | **12 — Solid** | Baseline + one strong ML alternative is well justified, but volatility forecasting is a lower-dimensional problem than Direction 1's cross-sectional feature space, so it naturally supports fewer additional candidates/ablations at minimum scope. |
| 4 | Experimentation Rigor (14) | **9 — Solid** | Rolling walk-forward is simple and low-leakage-risk by construction (a genuine advantage), but the smaller model/feature grid gives fewer natural negative-result branches than Direction 1's Exceptional bar requires. |
| 5 | Performance Diagnosis (10) | **7 — Solid** | Regime-sliced diagnosis is a strong, literature-anticipated axis (HAR-RV literature explicitly discusses jump/regime sensitivity), giving a clean, low-effort root-cause target. |
| 6 | Productionization (16) | **10 — Solid** | Same paper-trading-loop shape as Direction 1, on a smaller action space (position-size adjustment across a handful of ETFs); Solid is the honest floor, an extended run reaches Exceptional. |
| 7 | Market/Domain Fluency (8) | **8 — Exceptional** | Realized/implied-vol computation, the VIX risk premium, and vol-targeted sizing are inherent, unavoidable parts of building this direction at all — domain fluency is demonstrated by construction, not as an add-on. |
| 8 | Ownership/Judgment (8) | **6 — Solid** | A concrete, real decision-reversal story is available: discovering the FRED VIX mirror is separately copyrighted and switching to Cboe's own official CSV, exactly as this research did. |
| | **Total** | **12+14+12+9+7+10+8+6 = 78** | |

**Completion risk, originality & live-interview defensibility.** *Risk*: Low — fewest moving parts, smallest and cleanest data surface of the four (intraday bars for realized-vol construction are the main added mechanical step vs. daily-only directions). *Originality*: the HAR-RV-plus-ML extension and the vol-targeting sizing rule are candidate-specific engineering, not a copied tutorial. *Interview defensibility*: strong — HAR-RV's OLS baseline is fully hand-derivable on a whiteboard, and the whole pipeline is short enough to trace end-to-end from memory.

---

## 5. Direction 3 — Treasury Yield-Curve Forecasting & Duration Positioning

**Financial decision.** Forecast near-term changes in the shape of the US Treasury par yield curve (level, slope, curvature) and rotate exposure across a small, fixed set of Treasury-duration ETF tiers (e.g., a short-, intermediate-, and long-duration Treasury ETF) accordingly — long-only, no short leg required.

**Literature grounding.** Nelson, C.R. & Siegel, A.F. (1987), *"Parsimonious Modeling of Yield Curves,"* *Journal of Business* 60(4):473–489 — the original three-factor (level/slope/curvature) parametric model that explains ~96% of yield variation across maturities with only three interpretable parameters. `[EXPLICIT]` Diebold, F.X. & Li, C. (2006), *"Forecasting the Term Structure of Government Bond Yields,"* *Journal of Econometrics* 130(2):337–364 — reinterprets the three Nelson-Siegel factors as a dynamic latent time series (AR(1)/VAR(1)) and forecasts the curve forward, beating a random-walk benchmark with statistically significant gains **concentrated at longer, 6–12-month horizons** — a citable, literature-derived reason to set this direction's rebalance cadence at weeks-to-months rather than days, not an arbitrary choice. `[EXPLICIT]`

### Data sources

| Source | Provides | License / reuse / redistribution | Update cadence |
|---|---|---|---|
| U.S. Treasury Daily Par Yield Curve Rates (published on `home.treasury.gov`; XML feed and CSV export documented at `home.treasury.gov/treasury-daily-interest-rate-xml-feed`) | Official par yields across ~11–13 maturities (1 month to 30 years), since 1990 — the entire predictive-feature signal for this direction | `[EXPLICIT]` A U.S. federal government work; the sibling Bureau of the Fiscal Service site (`fiscaldata.treasury.gov`, same Department) states its open data is "offered free, without restriction, and available to copy, adapt, redistribute, or otherwise use for non-commercial or commercial purposes" — directly read on its API documentation page. `[INFERENCE]` `home.treasury.gov`'s own site-policies page does not carry an equivalent dedicated reuse notice, so this document treats the public-domain conclusion for the yield-curve series itself as inferred from the standard federal-government-work default (17 U.S.C. §105) and the sibling site's explicit statement, not as independently confirmed on `home.treasury.gov` itself. | Daily (~3:30pm ET on trading days) |
| Alpaca Market Data + Trading API (paper) | Daily OHLCV and paper-order execution for 2–3 Treasury-duration ETFs | Same Alpaca terms as every other direction in this document — no redistribution of raw bars without written consent. **This is the one place this otherwise fully public-domain direction touches restricted-reuse data.** `[EXPLICIT]` | Same-day |

### Schema & point-in-time semantics

The core signal has the cleanest point-in-time story of any source used in this document: each day's par-yield curve is published once, dated, and not later revised the way many macro series are — there is no vintage/ALFRED-style complexity to manage because there is nothing to revise. `[EXPLICIT]` The execution universe (2–3 large, continuously-listed Treasury-duration ETFs) has no membership-history problem, the same advantage Direction 2 has. The schema itself (a small, fixed set of named maturities per date) is simpler than either Direction 1's or Direction 4's fundamentals joins — there is no `filed`-vs-`end` distinction to manage because the published date *is* the availability date.

### Leakage & backtest risk

- **Horizon-mismatch risk**: Diebold & Li's own result shows forecasting gains concentrated at 6–12-month horizons and weaker/mixed at short horizons — using this model at a daily or weekly horizon without acknowledging that would overstate the literature's support. The smallest-complete design responds by setting the rebalance/decision horizon to weeks-to-months and testing (not assuming) shorter horizons as a named robustness check.
- **Curve-fit-then-forecast leakage**: the Nelson-Siegel factor fit for date *t* must only use maturity data observed as of date *t*; the *forecasting* model (AR(1)/VAR(1)/GBM on the three factors) must then be walk-forward validated on top of that — two stages that must each be kept leakage-safe, not just the second.
- **Execution-leg basis risk**: an ETF's duration/yield sensitivity is a related but imperfect proxy for the Treasury curve itself (fund flows, expense ratios, and roll effects create tracking differences) — any P&L claim must disclose this proxy gap rather than treat ETF returns as identical to the modeled curve.

### Smallest complete implementation

- Universe: 2–3 major, liquid, long-lived Treasury-duration ETFs (obvious, low-debate selection, like Direction 2's ETF universe).
- Data: `home.treasury.gov` daily par-yield curve (signal) + Alpaca bars (execution).
- Signal pipeline (two stages): (1) fit the Nelson-Siegel level/slope/curvature factors to each day's curve; (2) forecast those three factors forward.
- Baseline: a random-walk forecast of the curve (tomorrow's curve = today's), or independent AR(1) per factor; candidate: a VAR(1) across the three factors (testing whether cross-factor dynamics add value over independent AR(1)) or a gradient-boosted regressor on the factors plus macro context (optionally reusing Direction 2's FRED/ALFRED plumbing). A neural net is not warranted for a three-factor time series at this scale — PyTorch/TensorFlow would be decorative here, the same conclusion as Direction 2.
- Rolling-origin walk-forward validation at the chosen (weeks-to-months) horizon, **plus an explicit shorter-horizon robustness check** that is expected, per the cited literature, to show a weaker or negative result — a planned, literature-anticipated negative-result branch rather than an accidental one.
- Diagnosis sliced by which factor (level/slope/curvature) drove a forecast miss, and whether it lines up with an identifiable macro-policy event (e.g., an FOMC decision) — directly in the spirit of Nelson & Siegel's (1987) own worked example, which ties their factor movements to a documented 1982 Federal Reserve policy shift.
- Packaged pipeline, tests, scheduled forecast + duration-tier rebalance + Alpaca paper orders, logs.

### Candidate-owned vs. reused

`[REUSED WORK]`: the Treasury XML/CSV feed, Alpaca SDK, FRED/ALFRED client (if macro context is added), statsmodels/LightGBM. Candidate-owned: the Nelson-Siegel curve-fitting code, the factor-forecasting baseline and candidate model code, the horizon-robustness check, the duration-tier rebalancing rule, the validation harness, diagnosis, packaging, and the paper-trading loop.

### Rubric scores

| # | Criterion (wt) | Score | Rationale |
|---|---|---|---|
| 1 | Problem Formulation (12) | **12 — Exceptional** | Nelson-Siegel (1987) + Diebold-Li (2006) are both directly on-point, and the literature's own horizon-dependent finding gives an unusually concrete, evidence-based reason to reject a naive daily/weekly rebalance in favor of a longer horizon — a citable rejection decision, not an assumed one. |
| 2 | Data Corpus Engineering (14) | **14 — Exceptional** | The entire predictive signal comes from one first-party U.S. government source with an explicit free-for-any-purpose reuse statement and no revision/vintage complexity at all — arguably the single cleanest core-signal story in this document, with only the execution leg touching restricted-reuse data. |
| 3 | Modeling Depth (18) | **12 — Solid** | A genuine two-stage pipeline (parametric curve-fitting, then factor forecasting) gives real modeling texture, but the candidate-vs-baseline comparison itself happens only at the second, low-dimensional (three-factor) stage — a comparable ceiling to Direction 2, not Direction 1's larger from-scratch model bake-off. |
| 4 | Experimentation Rigor (14) | **9 — Solid** | Rolling walk-forward on a three-factor series is simple and low-cross-sectional-leakage-risk by construction, and the horizon-robustness check gives one genuine, literature-anticipated negative result — but the overall grid is narrower than Direction 1's, so Exceptional's full multi-axis bar isn't automatic at minimum scope. |
| 5 | Performance Diagnosis (10) | **7 — Solid** | Factor-attribution diagnosis (which of level/slope/curvature missed, and why) is a natural, literature-anticipated axis — Nelson & Siegel's own 1987 paper ties factor movements to an identifiable Fed policy shift — giving a clean, specific root-cause template. |
| 6 | Productionization (16) | **10 — Solid** | Mechanically the simplest execution loop of the four (long-only, 2–3 positions, one signal source, one execution source) — Solid is the honest floor, an extended run reaches Exceptional exactly as for the other directions. |
| 7 | Market/Domain Fluency (8) | **8 — Exceptional** | Duration, yield-curve shape, and level/slope/curvature vocabulary are unavoidable, inherent parts of building this direction at all — the same inherent-domain-fluency case as Direction 2. |
| 8 | Ownership/Judgment (8) | **6 — Solid** | A concrete, real provenance story happened in this very research: discovering the par-yield-curve dataset is not actually hosted on `fiscaldata.treasury.gov`'s API despite that site being the natural first guess, and tracing it to `home.treasury.gov`'s own XML/CSV feed instead. |
| | **Total** | **12+14+12+9+7+10+8+6 = 78** | |

**Completion risk, originality & live-interview defensibility.** *Risk*: Low — likely the lowest of the four: long-only, 2–3 positions, one signal source with no vintage complexity, one execution source. *Originality*: the two-stage curve-fit-then-forecast pipeline and the literature-derived horizon choice are candidate-specific engineering and judgment, not a copied tutorial path. *Interview defensibility*: strong — Nelson-Siegel's three-parameter functional form and a VAR(1)/AR(1) factor forecast are compact and fully whiteboard-derivable, and the literature gives an unusually specific, ready answer to "why this horizon and not daily."

---

## 6. Direction 4 — Filing-Triggered Earnings-Drift Agent (agentic)

Included only because it clears the ownership bar set for an agentic direction: the trading **decision** is made by a candidate-trained model, not by open-ended LLM judgment. The agent layer is a thin, candidate-authored retrieval/orchestration/reporting wrapper — explicitly not adopted from, or modeled tool-for-tool on, an existing framework such as Vibe-Trading.

**Financial decision.** On each new 8-K (Item 2.02 earnings-release) filing for a tracked universe, predict the direction/magnitude of the 1–3-day post-filing return ("post-earnings-announcement drift") and paper-trade accordingly.

**Literature grounding.** Bernard, V. & Thomas, J. (1989), *"Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium?,"* *Journal of Accounting Research* 27(Supplement):1–36 — the seminal paper documenting PEAD: a standardized-unexpected-earnings (SUE) hedge portfolio earns roughly +4.2% over the 60 trading days following an announcement, evidence pointing to delayed price response (underreaction) rather than a risk premium. `[EXPLICIT]` This grounds both the label (drift following a surprise) and the baseline (a SUE-decile sort).

### The agent layer, precisely

A scheduled job (1) polls SEC EDGAR Full-Text Search for same-day new 8-Ks in the tracked universe, (2) computes SUE and simple text features from the filing and calls the candidate's own trained model, (3) makes **one bounded LLM call** that produces a short natural-language rationale citing the filing and the model's output — the LLM is explicitly **not** given authority to change the trade decision; a deterministic rule reads the model's output plus a fixed position-size/risk-limit check, (4) submits the resulting Alpaca paper order and logs the filing ID, model output, LLM rationale text, and order together as one auditable trace. This split (trained model decides; LLM only narrates) is the concrete design choice that keeps the causal chain testable and is itself worth stating as a deliberate, defensible limitation rather than an unexamined one.

### Data sources

| Source | Provides | License / reuse / redistribution | Update cadence |
|---|---|---|---|
| SEC EDGAR Full-Text Search (`efts.sec.gov`; UI at [`sec.gov/edgar/search/`](https://www.sec.gov/edgar/search/)) | Retrieval of newly filed 8-K Item 2.02 exhibits for the tracked universe, full text since 2001 | `[EXPLICIT]` Public domain per SEC's own site policy (§5, above). `[UNKNOWN]` The JSON response shape of `efts.sec.gov` is not published as a formal, versioned schema the way `data.sec.gov`'s REST APIs are (per the official [EDGAR full-text-search FAQ](https://www.sec.gov/edgar/search/efts-faq.html), which documents *coverage* — "since 2001," including exhibits — but not a field-level schema) — treat it as documented-by-example, and add defensive parsing. | Same-day filing coverage; no published indexing-latency SLA found |
| SEC EDGAR XBRL `companyconcept` | SUE inputs, same `filed`-date discipline as Direction 1 | Same as Direction 1 | Same as Direction 1 |
| Alpaca Trading API (paper) | Executes the resulting paper trade | Same Alpaca terms as Directions 1–3 | Live |
| *(context only, not a dependency)* HKUDS/Vibe-Trading | Illustrates what an adopted, framework-scale agentic trading system looks like, motivating why this direction's own agent layer stays small and candidate-authored instead | `[EXPLICIT]`/`[REUSED WORK]` MIT-licensed; not proposed as a dependency here. The dedicated audit's verdict is **reference repository** — no PyTorch/TensorFlow/XGBoost/LightGBM in its own dependency tree (its 460-factor "Alpha Zoo" is deterministic closed-form formulas, not fitted models), so it offers no verified ML-model work to inherit even here. | Directly read 2026-07-13; audit verdict received 2026-07-13; daily-cadence commits observed through mid-July 2026 |

### Schema & point-in-time semantics

Reuses Direction 1's fixed basket and `filed`-date discipline for fundamentals. The filing-retrieval step adds one more timing subtlety: the **filing timestamp** (when EDGAR accepted the submission) can differ from when the full-text index actually makes it searchable — a live system must use the filing's own accepted-time metadata as the availability timestamp, not "whenever my poll happened to see it," or it risks a small, structural look-ahead advantage a real trader would not have had.

### Leakage & backtest risk

- **Filing-availability leakage**: as above — must anchor on EDGAR's accepted timestamp, not indexing/poll time, for any historical backtest.
- **Model/agent leakage boundary**: the trained model is validated with the same purged/embargoed discipline as Direction 1; the orchestration layer (retrieval, LLM call, logging) is not something walk-forward cross-validation evaluates at all — this must be tested separately (e.g., replayed against a historical filing feed) and the split documented explicitly, or the write-up risks implying more of the system was leakage-audited than actually was.
- **SUE-expectation leakage**: the "expected earnings" baseline used to compute the surprise must itself only use information available before the filing (e.g., a trailing seasonal random walk), not smoothed/revised figures.

### Smallest complete implementation

- Universe: reuses (a subset of) Direction 1's fixed basket.
- Core model: baseline = SUE-decile sort (directly from Bernard & Thomas 1989); candidate = SUE + filing-text features (TF-IDF, or a frozen pretrained sentence-embedding model with only a trained classifier head on top — a legitimate, non-decorative use of PyTorch/HuggingFace tooling, since the candidate trains the head, not the embedding model itself, which must be stated plainly as reused-vs-owned) feeding logistic regression / gradient boosting, predicting 1–3-day drift direction/magnitude.
- Thin, candidate-authored orchestration loop as described above — no third-party agent framework.
- Purged/embargoed walk-forward validation for the model; separate integration tests (replayed historical filings) for the orchestration loop.
- Root-cause diagnosis of one bad prediction, deliberately attempting to attribute the failure to data, model, or orchestration rather than defaulting to "the model was wrong," given the extra moving parts.
- Packaged pipeline (including agent/orchestration code), tests, scheduled run, Alpaca paper trading, full reasoning-trace logs (filing ID → model output → LLM rationale → order).

### Candidate-owned vs. reused

`[REUSED WORK]`: SEC EDGAR APIs, Alpaca SDK, an LLM API for the bounded rationale-only call, a pretrained sentence-embedding model (if used) as a frozen feature extractor, standard ML/NLP libraries. Candidate-owned: SUE computation, the text-feature pipeline, baseline and trained-model code, the purge/embargo validation harness, the *entire* orchestration loop (scheduling, tool calls, the deterministic risk gate that keeps the LLM non-authoritative, the logging schema), diagnosis, packaging, and the paper-trading loop. Explicitly **not** reused: Vibe-Trading or any comparable third-party trading-agent framework — consistent with its own dedicated audit's **reference repository** verdict, the orchestration loop here is kept small and candidate-authored specifically so the agent layer cannot dominate or obscure ownership.

### Rubric scores

| # | Criterion (wt) | Score | Rationale |
|---|---|---|---|
| 1 | Problem Formulation (12) | **8 — Solid** | Bernard & Thomas (1989) grounds the core prediction problem well, but the direction bundles a *second* framing burden the other three don't carry — justifying the agent/orchestration layer itself, which has no equivalent academic base — making Exceptional less likely to fall out of the smallest-complete write-up by default. |
| 2 | Data Corpus Engineering (14) | **9 — Solid** | Inherits Direction 1's authoritative-but-basket-limited fundamentals story and adds one further named risk: the full-text-search endpoint is documented by example rather than by a formal, versioned schema, unlike `data.sec.gov`'s REST APIs. |
| 3 | Modeling Depth (18) | **12 — Solid** | The trained text→drift model is genuine, candidate-authored modeling (baseline + one strong alternative), but part of the direction's complexity budget goes to the orchestration layer rather than additional model candidates/ablations, capping it below Direction 1's ceiling without expanding scope beyond "smallest complete." |
| 4 | Experimentation Rigor (14) | **9 — Solid** | The same purge/embargo logic as Direction 1 applies to the drift model itself, but the orchestration layer sits entirely outside that tracked-experiment framework and must be validated a different way — a real, direction-specific reporting split that must be disclosed, not glossed over. |
| 5 | Performance Diagnosis (10) | **7 — Solid** | The trained model is diagnosable the same way as Direction 1's; the qualifier is that a bad outcome can originate in data, model, *or* orchestration, which raises the risk of a shallow or conflated diagnosis unless the candidate deliberately separates the three, as the smallest-complete design above requires. |
| 6 | Productionization (16) | **10 — Solid** | Genuinely more components to package and test (retrieval, model call, LLM call, risk gate, execution, full trace logging) — more demonstrable engineering surface, but also more that can silently break (e.g., an LLM call timing out); a wash against the other three at minimum scope, not a clear advantage. |
| 7 | Market/Domain Fluency (8) | **5 — Solid** | SUE computation and earnings-calendar handling are solid domain grounding, but a meaningful share of the complexity budget goes to the orchestration layer instead of additional market-microstructure depth, so it does not reach Directions 2–3's "domain fluency is inherent to the whole build" bar. |
| 8 | Ownership/Judgment (8) | **6 — Solid** | A strong, specific, judgment-forward limitations story is available and load-bearing to the design itself: deliberately withholding trade-decision authority from the LLM and explaining why, rather than a generic "agents can hallucinate" caveat. |
| | **Total** | **8+9+12+9+7+10+5+6 = 66** | |

**Completion risk, originality & live-interview defensibility.** *Risk*: Moderate–high — most moving parts of the four (retrieval, model, LLM call, deterministic gate, execution, trace logging); LLM-call reliability/latency/cost is an external dependency outside the candidate's control, and "let's make the agent smarter" is a live scope-creep risk this design must actively guard against, echoing the map's standing caution against overbuilding an agent layer. *Originality*: high — the thin, bounded orchestration design (LLM narrates, never decides) is a specific, defensible architectural choice, not a copied agent-framework pattern. *Interview defensibility*: moderate — the trained model and its validation are as defensible as Direction 1's, but LLM-generated rationale text is harder to defend line-by-line under live follow-up than a GBM's feature importances; the candidate must be ready to explain this as a *designed* limitation (the LLM is explicitly non-authoritative) rather than be caught overclaiming the agent's reasoning is rigorous — a real, named interview risk that must be pre-empted, not discovered live.

---

## 7. Cross-direction score matrix

| # | Criterion | Weight | D1 Cross-Sectional | D2 Volatility | D3 Treasury Curve | D4 Filing Agent |
|---|---|---|---|---|---|---|
| 1 | Problem Formulation & Literature-Grounded Research | 12 | 12 | 12 | 12 | 8 |
| 2 | Data Corpus Engineering | 14 | 9 | 14 | 14 | 9 |
| 3 | Modeling Depth & ML Foundations | 18 | 18 | 12 | 12 | 12 |
| 4 | Experimentation Rigor & Reporting | 14 | 14 | 9 | 9 | 9 |
| 5 | Performance Diagnosis | 10 | 7 | 7 | 7 | 7 |
| 6 | Productionization & Engineering Fluency | 16 | 10 | 10 | 10 | 10 |
| 7 | Market/Domain Fluency | 8 | 5 | 8 | 8 | 5 |
| 8 | Ownership, Judgment & Culture-Fit | 8 | 6 | 6 | 6 | 6 |
| | **Total (max 100)** | **100** | **81** | **78** | **78** | **66** |

**Row arithmetic** (transparency check — every row sums to its printed total):
D1: 12+9+18+14+7+10+5+6 = 81. D2: 12+14+12+9+7+10+8+6 = 78. D3: 12+14+12+9+7+10+8+6 = 78. D4: 8+9+12+9+7+10+5+6 = 66.
**Column-max check**: 12+14+18+14+10+16+8+8 = 100, confirming the weights used are the existing rubric's unchanged weights.

---

## 8. Tradeoffs, not a selection

This section names the dimensions the later selection ticket must weigh; it does not weigh them for that ticket, and it does not name a winner. Per the approved tie-break order (stronger ML **hiring evidence** → clearer candidate ownership → safer data/evaluation → lower completion risk), the raw total above is a starting point, not the decision rule — the selection ticket must still apply that order explicitly rather than default to the highest number.

- **ML hiring evidence (Criterion 3, the single largest weight at 18 pts) is strongest for D1**, whose cross-sectional feature space naturally supports the richest baseline-vs.-candidates-vs.-ablations story; D2–D4 are all capped at Solid on this axis by a narrower modeling surface, for direction-specific reasons (lower-dimensional target, a two-stage-but-still-low-dimensional pipeline, complexity budget split with orchestration).
- **Data cleanliness and point-in-time safety are strongest for D2 and D3, which tie on total score (78) via genuinely different paths.** D3's entire predictive signal is one first-party U.S. government source with an explicit free-for-any-purpose reuse statement and zero revision/vintage complexity; D2 assembles three first-party sources (Alpaca, Cboe, FRED/ALFRED) that are each individually clean but individually license-encumbered in a small, named way (Cboe copyright-with-attribution; Alpaca's standard redistribution limit). Both still touch Alpaca for execution — neither is a "no proprietary data at all" direction, and this document does not claim otherwise. D1 and D4 share one disclosed, bounded basket-construction simplification instead.
- **This D2/D3 tie is itself informative for the later selection ticket**: the two directions reach the same total through different evidence profiles rather than identical ones, so the raw total cannot break the tie by itself — the selection ticket's approved order (ML hiring evidence → ownership → safer data/evaluation → completion risk) would need to, most likely on completion risk (D3 has the fewest moving parts of any direction here) or on which financial domain (equity-index volatility vs. rates) it weighs as more relevant to the target role.
- **Domain fluency (Criterion 7) is strongest for D2 and D3**, where risk/performance vocabulary (realized/implied vol, duration, curve shape) is inherent to building the direction at all, not an add-on.
- **Ownership clarity is comparable across all four (Criterion 8 ties at 6)**, but for different, concrete, already-discovered reasons — each direction has a real "hit a constraint and made a specific, defensible call" story, not a generic limitations section.
- **The agentic direction (D4) clears the ownership bar this ticket required** (a candidate-trained model makes the decision; the LLM only narrates) and is not a strawman — but it scores lowest primarily because its added orchestration surface dilutes, rather than adds to, the ML- and domain-evidence axes the rubric weights most heavily, and it carries the highest completion risk of the four. This is the concrete, direction-specific instance of the standing principle that an agent layer must earn its place with independent hiring evidence, not just added engineering surface — reinforced by Vibe-Trading's own **reference repository** verdict, where the same pattern shows up at framework scale.
- **Completion risk rises roughly with component count**: D3 (fewest moving parts — one signal source with no vintage complexity, one execution source, long-only) is lowest, then D2 (one more data source, intraday bars for realized-vol construction), then D1 (adds a cross-sectional fundamentals join), then D4 highest (most moving parts, one of them — the LLM call — outside the candidate's control).

---

## 9. Source ledger

| Source | Type | What it verified | Accessed |
|---|---|---|---|
| [Alpaca — Getting Started](https://docs.alpaca.markets/docs/getting-started), [Trading API](https://docs.alpaca.markets/docs/getting-started-with-trading-api), [Market Data API](https://docs.alpaca.markets/docs/getting-started-with-alpaca-market-data) | First-party (Alpaca) | Paper-trading endpoint, historical bar access pattern, stock + crypto data clients | 2026-07-13 |
| [Alpaca — data provider FAQ](https://alpaca.markets/support/data-provider-alpaca), [data-timeline FAQ](https://alpaca.markets/support/alpaca-data-timeline) | First-party (Alpaca) | IEX/SIP data source; minute history to ~2016 | 2026-07-13 |
| [Alpaca Customer Agreement PDF](https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf) | First-party legal doc | No-redistribution-without-written-consent clause | 2026-07-13 (via search synthesis quoting the PDF directly) |
| [Alpaca — crypto margin/short FAQ](https://alpaca.markets/support/can-i-margin-or-short-with-cryptocurrency) | First-party (Alpaca) | Crypto positions are non-marginable (cannot be shorted) — drove the D3 pivot away from crypto pairs | 2026-07-13, direct read |
| [SEC — EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [Developer Resources](https://www.sec.gov/about/developer-resources) | First-party (SEC), official docs | `data.sec.gov` submissions/XBRL endpoints, rate limits, JSON format | 2026-07-13 (via search synthesis of the official pages; direct fetch returned HTTP 403 in this environment) |
| [SEC — Privacy/reuse policy](https://www.sec.gov/about/privacy-information) | First-party (SEC) | Site information is public domain, redistributable without permission | 2026-07-13 (via search synthesis quoting the page directly) |
| [SEC — EDGAR full-text search FAQ](https://www.sec.gov/edgar/search/efts-faq.html) | First-party (SEC) | Full-text coverage since 2001, includes filing exhibits | 2026-07-13 (via search synthesis quoting the page directly) |
| [`data.sec.gov` XBRL `companyconcept` example (Walmart Revenues)](https://data.sec.gov/api/xbrl/companyconcept/CIK0000104169/us-gaap/Revenues.json) | First-party (SEC), live API response | Confirms the `filed` vs. `end` field distinction used for point-in-time joins | 2026-07-13 (via search synthesis showing the live JSON) |
| [FRED API docs](https://fred.stlouisfed.org/docs/api/fred/), [Terms of Use](https://fred.stlouisfed.org/docs/api/terms_of_use.html) | First-party (Federal Reserve Bank of St. Louis) | ALFRED vintage-date mechanism; per-series copyright caveat | 2026-07-13, direct read |
| [FRED — `VIXCLS` series page](https://fred.stlouisfed.org/series/VIXCLS) | First-party (FRED), mirrors Cboe | Confirms `VIXCLS` is separately copyrighted ("Citation Required") — drove the direct-to-Cboe sourcing decision | 2026-07-13, direct read |
| [Cboe — VIX historical data page](https://www.cboe.com/tradable_products/vix/vix_historical_data/) | First-party (Cboe) | Official free VIX CSV download exists and is Cboe's own IP | 2026-07-13, direct read (nav) + search-confirmed direct CSV link |
| [U.S. Treasury — Fiscal Data API documentation](https://fiscaldata.treasury.gov/api-documentation/) | First-party (U.S. Dept. of the Treasury, Bureau of the Fiscal Service) | Explicit open-data license: "offered free, without restriction... for non-commercial or commercial purposes" | 2026-07-13, direct read |
| [U.S. Treasury — interest-rate statistics / Daily Par Yield Curve Rates](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics), [XML feed docs](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed) | First-party (U.S. Dept. of the Treasury) | Official daily par-yield curve publication, XML/CSV access pattern, data since 1990 | 2026-07-13 (via search synthesis of the official pages) |
| [GitHub — fja05680/sp500](https://github.com/fja05680/sp500) | Community repository, MIT license | Best available free point-in-time S&P 500 membership proxy; maintainer's own documented limitations | 2026-07-13, direct read |
| [GitHub — HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | Community repository, MIT license | Scale/composition of an adopted agentic trading framework; motivates D4's thin, candidate-authored agent design instead | 2026-07-13, direct read |
| [Vibe-Trading audit](vibe-trading-audit.md) (sibling research asset) | Internal prior research | Authoritative verdict: **reference repository** — no fitted-model dependencies, multi-license overhead, open safety checklist | 2026-07-13 |
| [Yahoo — Terms of Service](https://guce.yahoo.com/terms?locale=en-US), [Yahoo Terms §4/§8](https://legal.yahoo.com/xw/en/yahoo/terms/otos/index.html) | First-party (Yahoo) | Automated data collection prohibited without express permission; official API discontinued 2017 | 2026-07-13 (via search synthesis quoting the terms directly) |
| Gu, Kelly & Xiu (2020), *Review of Financial Studies* 33(5):2223–2273 | Peer-reviewed paper | Cross-sectional ML return prediction; trees/shallow nets beat linear baselines (D1) | 2026-07-13 |
| López de Prado (2018), *Advances in Financial Machine Learning*, Wiley | Book | Purged/embargoed k-fold cross-validation for overlapping financial labels (D1, D4) | 2026-07-13 |
| Corsi (2009), *Journal of Financial Econometrics* 7(2):174–196 | Peer-reviewed paper | HAR-RV realized-volatility baseline (D2) | 2026-07-13 |
| Nelson & Siegel (1987), *Journal of Business* 60(4):473–489 | Peer-reviewed paper | Three-factor (level/slope/curvature) parametric yield-curve model (D3) | 2026-07-13 |
| Diebold & Li (2006), *Journal of Econometrics* 130(2):337–364 | Peer-reviewed paper | Dynamic Nelson-Siegel yield-curve forecasting; horizon-dependent forecasting gains (D3) | 2026-07-13 |
| Gatev, Goetzmann & Rouwenhorst (2006), *Review of Financial Studies* 19(3):797–827 | Peer-reviewed paper | Distance-based pairs-trading strategy and its empirical performance (cited in §1's excluded-direction note, not a scored direction) | 2026-07-13 |
| Bernard & Thomas (1989), *Journal of Accounting Research* 27(Supplement):1–36 | Peer-reviewed paper | Post-earnings-announcement drift (D4) | 2026-07-13 |
| [Looloo project-evidence rubric](looloo-project-evidence-rubric.md), [PRD](../PRD.md) | Internal prior research | Rubric weights/anchors, glossary terms, applicant constraints, scope boundary | given |

**Could not verify:** the formal response schema of `efts.sec.gov`; exact EDGAR full-text-search indexing-latency SLA; whether `home.treasury.gov` itself (as distinct from its sibling `fiscaldata.treasury.gov`) carries its own dedicated copyright/reuse notice. None of the four scores above depends on resolving these — each is named as an explicit, bounded risk in its direction's section instead.
