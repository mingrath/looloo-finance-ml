# HKUDS/Vibe-Trading — reference-repository audit

**Scope.** This audit answers Ticket 1, "Audit Vibe-Trading as a reference repository," for the Looloo Finance ML portfolio build brief. The question is narrow: does [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading), adapted at any plausible scope, give the applicant defensible **hiring evidence** for the **target role** (Looloo's Machine Learning Engineer, Project Algorithmic Trading)? This file does not select the **portfolio project** and does not credit any upstream engineering to the applicant — separating those two things is the entire point of the exercise. Packt's *Machine Learning for Algorithmic Trading* repository ecosystem is examined only as a contrast case (§6) and stays a learning source, never candidate-owned hiring evidence, throughout. The project boundary assumed everywhere below is historical research plus a no-capital **paper-trading demo** — no live brokerage execution, real money, or profitability claim. Findings here feed the later **build brief**; this file does not itself choose anything.

**Method.** Primary sources only: repository source files, `LICENSE`/`NOTICE`, `pyproject.toml`, `CHANGELOG.md`, `CONTRIBUTING.md`, `AGENT_CONTRIBUTOR_GUIDE.md`, `SECURITY.md`, `Dockerfile`/`docker-compose.yml`, GitHub Releases/Issues/Discussions, and the compared repositories' own READMEs, license files, and file trees — read directly, not via search snippets. All URLs below were fetched 2026-07-13 unless a quoted date says otherwise.

**Tagging convention.** `[EXPLICIT]` — directly stated or shown in a primary source read for this audit. `[INFERENCE]` — reasoning beyond the literal text, flagged because a reasonable reader could disagree. `[REUSED WORK]` — content that Vibe-Trading (or Packt) itself adapted from a third-party upstream (a paper, another repository, a licensed dataset) — flagged because it is not even upstream's *own* original work, let alone the applicant's. `[UNKNOWN]` — looked for and not verifiable from available primary sources.

---

## 1. At a glance

| Question | Answer | Status |
|---|---|---|
| What is Vibe-Trading? | An LLM-agent product — "Your Personal Trading Agent" — built on LangChain/LangGraph with an MCP tool server, 87 "skills," 30 multi-agent "swarm" presets, broker/IM integrations, wrapped around a deterministic quant backtesting and factor library | `[EXPLICIT]` repo self-description |
| Does it contain genuine, shipped, tested ML model-training code? | No. The only `scikit-learn` usage anywhere in the codebase lives inside one documentation/prompt file meant for the LLM agent to copy-paste — not a committed or CI-tested module | `[EXPLICIT]` — §2 |
| Does its own dependency manifest declare TensorFlow/PyTorch/XGBoost/LightGBM/statsmodels? | No — `scikit-learn` + `joblib` are the *only* classical-ML libraries in `pyproject.toml`, core or optional | `[EXPLICIT]` — §2 |
| License | MIT (root) + an Apache-2.0 attribution obligation for one factor family + citation-request clauses for two more | `[EXPLICIT]` — §4 |
| Is it production-safe for real trading today? | No, by the maintainer's own admission — a dated, open tracking issue lists a 10-item "release criteria for real trading" checklist, all boxes unchecked | `[EXPLICIT]` issue #476 — §3.6 |
| Maintenance state | Actively maintained: near-daily commits, minor releases roughly every 2–3 weeks, test count grew 969 → 4,701+ over three months | `[EXPLICIT]` — §3.7 |
| Packt's role in this audit | Learning source only — book-companion notebooks, never candidate-owned hiring evidence | `[EXPLICIT]` — §6 |
| Verdict | **Reference only** | rubric impact in §7 |

---

## 2. Architecture: model, data, and evaluation work vs. LLM/agent orchestration

### 2.1 The project's own self-description

`agent/SKILL.md` [EXPLICIT] describes the system as a "Professional finance research toolkit with AI-powered backtesting (8 engines), multi-agent teams, 87 specialized skills, the Alpha Zoo…," documents itself as an MCP tool provider ("Available MCP Tools (54)") and an MCP *client* ("The built-in agent can load tools from your own external MCP servers…"). The root `AGENT_CONTRIBUTOR_GUIDE.md` [EXPLICIT] frames the whole repository around an agent/tool-calling loop with safety-critical "broker connector, mandate, order gate, halt, and audit-ledger logic." Neither document describes the project as a modeling or research-methodology codebase.

### 2.2 Dependency manifest — what is actually installed

[`pyproject.toml`](https://raw.githubusercontent.com/HKUDS/Vibe-Trading/main/pyproject.toml) `[EXPLICIT]`, package `vibe-trading-ai` v0.1.11:

| Category | Packages |
|---|---|
| LLM/agent orchestration | `langchain`, `langchain-core`, `langchain-openai`, `langgraph`, `langgraph-checkpoint`, `fastmcp`, `oauth-cli-kit`, `prompt_toolkit` |
| Classical ML | `scikit-learn`, `joblib` — **only these two.** No `torch`, `tensorflow`, `keras`, `xgboost`, `lightgbm`, or `statsmodels` anywhere in core or optional dependency groups |
| Quant/data science | `pandas`, `numpy`, `scipy`, `bottleneck`, `duckdb` |
| Market-data clients | `tushare`, `yfinance`, `akshare`, `ccxt` (+ optional `baostock`) |
| Web/product | `fastapi`, `uvicorn`, `websockets`, `pydantic`, `sse-starlette`, `jinja2`, `matplotlib`, `weasyprint` |
| Optional product surface | 16 IM-channel SDKs (Telegram, Discord, Slack, WhatsApp, WeCom, Feishu, Matrix, DingTalk, Teams, Mochat, NapCat, QQ, WeChat…), `ib_async` (IBKR), `langchain-deepseek` |
| Dev/CI | `pytest`, `pytest-cov`, `pytest-socket` |

This is the single most decisive fact for this section: the role's preferred competency "familiar[ity] with machine learning frameworks such as Tensorflow or PyTorch" has **nothing to inherit** from Vibe-Trading's own dependency footprint `[EXPLICIT]`.

### 2.3 Category breakdown by subsystem

| Layer | What it is | Category | Evidence |
|---|---|---|---|
| Alpha Zoo (`agent/src/factors/zoo/*`, 460 factor files: 154 `qlib158` + 101 `alpha101` + 191 `gtja191` + 10 `academic` + 4 `fundamental`) | Closed-form pandas/numpy rolling-window, cross-sectional rank/z-score formulas transcribed from papers/Qlib | Deterministic quant math, **not ML** | `[EXPLICIT]`/`[REUSED WORK]` `alpha101/alpha_001.py`: `rank(ts_argmax(signed_power(x,2.0),5))-0.5`; no `.fit(`/`.train(` anywhere under `agent/src/factors/zoo/**` |
| Portfolio optimizers (`agent/backtest/optimizers/*`) | Mean-variance (SLSQP), risk parity (Newton iteration), equal-volatility, max-diversification, turnover-aware | Classical convex/numerical optimization, **not ML** | `[EXPLICIT]` `mean_variance.py`: `scipy.optimize.minimize(neg_sharpe, …, method="SLSQP")` |
| `ml-strategy` skill (`agent/src/skills/ml-strategy/SKILL.md`) | A documentation/prompt template containing a full sklearn walk-forward `RandomForestClassifier`/`GradientBoostingClassifier`/`LogisticRegression` pipeline (feature engineering → label → `StandardScaler.fit_transform` → `model.fit` → `predict_proba`), for the LLM agent to paste into a user-generated file | The **only** place real ML-training code exists in the repo — but as unshipped, untested prose, not an application module | `[EXPLICIT]` frontmatter: "Machine-learning predictive strategy based on sklearn walk-forward training…"; `[INFERENCE]` `agent/tests/` has only `factors/` and `fixtures/` subdirectories — no `skills/`/`ml/` test coverage exists for this pipeline anywhere in the areas checked |
| 8 backtest engines + validation/metrics (`agent/backtest/*`) | Bar-by-bar execution simulator; Monte Carlo/bootstrap/walk-forward-consistency statistical suite; return/risk metrics | Quant/software engineering, **not ML** | `[EXPLICIT]` — full detail in §3 |
| Agent/tool layer (LangChain, LangGraph, MCP server+client, 87 skills, 30 swarm presets, 54 MCP tools, hypothesis registry/"Research Autopilot") | Natural-language chat loop that discovers a skill, writes strategy code, and calls deterministic tools | **LLM/agent orchestration — the architectural core** | `[EXPLICIT]` `agent/SKILL.md`; `agent/src/tools/autopilot_tool.py` explicitly hands off "Generate backtest code (signal_engine.py + config.json)" to the LLM rather than doing it itself |
| Product/integration layer (FastAPI+React 19 web UI, CLI, 16 IM adapters, 10 broker connectors, Docker) | Deployable software product | Product/platform engineering, orthogonal to ML | `[EXPLICIT]` `pyproject.toml` optional groups; `Dockerfile` |

**Conclusion `[INFERENCE]`, evidence-grounded:** across every concrete file opened for this audit (factor formulas in 3 zoos, the shared operator library, both requested optimizers, the factor-evaluation IC/IR code, the strategy-artifact schema, the hypothesis registry, and a 168-file scan of `agent/src/tools/`), the only `sklearn` call site in the entire codebase is inside one Markdown skill file. Vibe-Trading's real engineering weight sits in (a) deterministic, well-tested closed-form factor math and classical portfolio optimization, and (b) LLM-agent/MCP tool orchestration — which the project's own documentation names as its core identity. A candidate-relevant ML pattern (feature engineering → split → fit → evaluate a statistical/ML model, owned and verified by a contributor) does not exist in this codebase as shipped, tested work.

---

## 3. Data, timing, backtesting, leakage, costs, reproducibility, deployment, maintenance, limitations

### 3.1 Data sources & datasets

19 free market-data sources plus an optional premium marketplace (QVeris), routed through `agent/backtest/loaders/registry.py`'s `FALLBACK_CHAINS`, "ordered by IP-ban risk first… then by data quality" `[EXPLICIT]`. A `local` loader reads a candidate's own CSV/Parquet/DuckDB files `[EXPLICIT]`.

**Gap, not self-disclosed:** `yfinance_loader.py`'s `_download_history()` calls `yf.download(…, auto_adjust=False, …)` with no adjustment-factor merge anywhere in the 319-line file; `loaders/tushare.py` calls the raw (non-adjusted) `daily()` endpoint with no `adj_factor` merge either `[EXPLICIT]`. Unadjusted OHLCV flows into backtests through at least these two loaders — a stock split or large special dividend inside a backtest window would appear as an uncaught price jump `[INFERENCE]`, since `validate_ohlc()` (§3.3) only checks bar-internal invariants, not corporate-action continuity.

### 3.2 Information timing / point-in-time (PIT) correctness — the strongest engineering in the repo

Two parallel, independently-built PIT pipelines:

| Path | Anchor | Mechanism | Evidence |
|---|---|---|---|
| SEC/XBRL fundamentals (`agent/backtest/loaders/fundamentals_loader.py`) | SEC `filed` date, never `period_end` | Forward-fills a fact onto the daily panel only from its filing date; TTM/quarterly synthesis anchors on the *latest* of the four contributing quarters' filing dates | `[EXPLICIT]` docstring: "values become visible on their SEC filed date, never on period_end" |
| China A-share fundamentals (`agent/backtest/loaders/tushare_fundamentals.py`) | `ann_date`/`f_ann_date` per table (`TableSchema.point_in_time_column`) | `enrich_price_frames_with_fundamentals()` uses `merge_asof(direction="backward")` to attach the most recent fundamental row whose PIT date is ≤ the trading day | `[EXPLICIT]` docstring: "Each row becomes visible only on or after its announcement/disclosure date" |

This is a textbook-correct as-of join and is the single design pattern in this repository most worth studying independently `[INFERENCE]`. **Gap:** restatement de-duplication beyond "keep whichever row's PIT date already passed" is `[UNKNOWN]` — no dedup key beyond `(ts_code, end_date)` was found.

### 3.3 Backtesting & leakage controls

Two distinct control layers exist, and they answer different questions:

- **Factor-computation layer (real, CI-enforced):** an AST-based "purity gate" (`agent/tests/factors/test_alpha_purity.py`) statically bans any factor file from importing outside `{pandas, numpy, scipy, src.factors.base}` or referencing `os/sys/subprocess/socket/eval/exec` `[EXPLICIT]`; a "lookahead guard" (`agent/tests/factors/test_lookahead.py`) perturbs future rows with NaN/sentinel values for every registered alpha and asserts historical rows are numerically unchanged (`rtol=atol=1e-9`) `[EXPLICIT]`. These prove individual formulas are structurally causal and sandboxed.
- **Backtest-validation layer (`agent/backtest/validation.py`):** implements exactly three tools — Monte Carlo permutation test, bootstrap Sharpe CI, and a walk-forward *consistency* check `[EXPLICIT]`. The walk-forward function splits an **already-realized** equity curve into sequential windows to check consistency; it is not a train/test-split method used during model fitting. **No purge/embargo scheme exists anywhere in this file** `[EXPLICIT — absence confirmed by full read]`. Validation is opt-in (`config["validation"]` must be explicitly set) — not a default gate on every run `[EXPLICIT]`.

**Net finding `[INFERENCE]`:** because no trained ML model exists in tested application code (§2.3), there is also no leakage-safe *model-training* validation scheme to inherit — the rubric's "walk-forward/purged/embargoed CV for a fitted model" (Criterion 4) has nothing to copy from here, only a differently-scoped consistency check to learn the *name and idea* of.

### 3.4 Transaction costs & slippage — genuinely strong, worth studying

All 8 concrete engines hardcode a distinct, config-overridable, primary-source-plausible fee schedule (confirmed by direct code read, not README claims):

| Engine | Cost model | Evidence |
|---|---|---|
| `global_equity.py` (US/HK) | US commission = 0; HK: `commission=0.00015`, `stamp_tax=0.001`, `levy=0.0000565`, `settlement=0.00002`; `slippage_us=0.0005`, `slippage_hk=0.001` | `[EXPLICIT]` |
| `china_a.py` | `commission_rate=0.00025` (¥5 min), `stamp_tax=0.0005` (sell-only), `transfer_fee=0.00001`, `slippage=0.001`; T+1 enforced; board price limits (±10/20/30%) | `[EXPLICIT]` |
| `crypto.py` | `maker=0.0002`, `taker=0.0005`, `slippage=0.0005`, funding at UTC {0,8,16} | `[EXPLICIT]` |
| `forex.py` | per-pair spread table (default 2.0 pips) + `slippage_pips=0.3`; Wednesday triple-swap convention | `[EXPLICIT]` |
| `india_equity.py` | Full SEBI stack: STT, exchange fee, SEBI fee, stamp duty, GST=0.18, `slippage=0.001`; docstring caveat to "verify `in_*` rates against a current broker schedule" | `[EXPLICIT]` |
| `china_futures.py` / `global_futures.py` | Per-product commission/multiplier/margin dict lookups | `[EXPLICIT]` |
| `options_portfolio.py` | Flat `commission=0.001` scalar (the one engine without a fee-schedule model) | `[EXPLICIT]` |

The abstract `BaseEngine` (`agent/backtest/engines/base.py`) enforces next-bar-open signal execution (`shifted = raw.shift(1)`, comment: "Signal is shifted by 1 bar") and applies slippage to the open price before sizing `[EXPLICIT]` — correct backtest mechanics.

### 3.5 Reproducibility

`agent/backtest/run_card.py`'s "Trust Layer" run card records `backtest{codes, start_date, end_date, interval, engine, initial_cash, source}` and `reproducibility{config_hash, strategy_hash}` (both SHA-256) `[EXPLICIT]`. **Gap:** no `seed`, no git commit hash, and no package-version pin exists anywhere in the run-card schema `[EXPLICIT — absence confirmed by full read]` — `validation.py`'s Monte Carlo/bootstrap functions default `seed=42` and are deterministic, but that seed is never surfaced in the card's output.

### 3.6 Deployment behavior

pip package + multi-stage Docker (non-root user, `EXPOSE 8899`, `docker-compose.yml` binds `127.0.0.1:8899:8899` by default) + CLI + FastAPI/React-19 web UI + MCP server `[EXPLICIT]`. The **decisive** deployment-risk fact: [issue #476](https://github.com/HKUDS/Vibe-Trading/issues/476) (opened 2026-07-12 by the maintainer) tracks a third-party external security audit ([discussion #468](https://github.com/HKUDS/Vibe-Trading/discussions/468)) with 10 findings (VT-001…VT-010), including a **Critical**: "LLM-generated backtest code runs in the same container/UID as the API process with normal network access… needs real isolation." `[EXPLICIT]` Two findings (VT-002: `build-essential` installed in the runtime image stage; VT-007: no `read_only`/`cap_drop`/`no-new-privileges` in `docker-compose.yml`) were independently re-verified against the primary `Dockerfile`/`docker-compose.yml` source for this audit, not merely taken on the maintainer's word `[EXPLICIT]`. The issue states an explicit "release criteria for real trading" checklist; **all 10 items remain unchecked as of the fetch date** `[EXPLICIT]`. This is a materially stronger signal than the generic README disclaimer — the maintainer is on record, dated one day before this audit, that the product is not yet safe for real-money use by its own stated bar.

### 3.7 Maintenance state

| Release | Date | Signal |
|---|---|---|
| v0.1.8 | 2026-05-17 | "Alpha Zoo v1"; 969 tests passing |
| v0.1.9 | 2026-06-01 | Connectors + Research Goal runtime |
| v0.1.10 | 2026-06-19 | Global data layer; 4,167 backend tests passing |
| v0.1.11 | 2026-07-11 | India equity, fundamental factors, IM channels; changelog references 4,701 passed / 47 skipped (2026-07-05 entry) |

`[EXPLICIT]` Cadence is roughly every 2–3 weeks for minor releases, with near-daily commits between them; one lead maintainer (@warren618) plus a wide community-contributor base. CI (`.github/workflows/test.yml`) `[EXPLICIT]` runs on push/PR to `main` only (single Python-3.11/Ubuntu job): syntax-compile check, `pytest --cov=agent` (coverage collected, **no threshold gate enforced**), and a separate frontend build+`vitest` pass — **no lint or type-check step exists**.

### 3.8 Documented limitations

**Self-disclosed by the project:** the v0.1.8 release notes carry an explicit "Caveats / Known limitations" section `[EXPLICIT]` — e.g., "SP500 universe uses today's constituent list… introducing survivorship bias," and a single-asset universe IC caveat. The root README Disclaimer states: "Vibe-Trading is research and trading software. It is not investment advice, holds no funds, and runs no execution venue… This broker-trading capability is experimental and not verified by us against a real broker account — use it at your own risk." `[EXPLICIT]` Individual engine docstrings self-disclose scope gaps, e.g. `global_futures.py`: "Roll/expiry: not modeled (assumes continuous front-month data)"; `china_futures.py`: "Night session… not enforced in bar-level sim" `[EXPLICIT]`.

**Identified by this audit, not self-disclosed:** the unadjusted-OHLCV gap (§3.1) and the absence of any independent trading-calendar/session validation anywhere in the 12 files under `agent/backtest/engines/` — calendar correctness is entirely outsourced to whatever bars an upstream data vendor happens to return `[EXPLICIT — absence confirmed by full read of all 12 files]`.

---

## 4. License and reuse obligations

| Component | Basis | Obligation if copied into a separate project | Evidence |
|---|---|---|---|
| Root repository | MIT, "Copyright (c) 2026 Vibe-Trading Contributors" | Retain copyright + permission notice | [`LICENSE`](https://github.com/HKUDS/Vibe-Trading/blob/main/LICENSE) `[EXPLICIT]` |
| `qlib158` zoo (154 factors) | Apache-2.0 — `[REUSED WORK]` adapted from Microsoft's `qlib` at a pinned commit | Per-file headers read "Adapted from microsoft/qlib@\<sha\>…(Apache-2.0). Copyright (c) Microsoft Corporation." Apache-2.0 §4 obligations (license copy, note-of-modification, retained notice) attach to that code by the license's own terms independent of any Vibe-Trading instruction — stripping the header to reuse the code elsewhere would be a license violation | `NOTICE`, `agent/src/factors/zoo/qlib158/LICENSE.md` + `NOTICE` `[EXPLICIT]` |
| `alpha101` zoo (101 factors) | `[REUSED WORK]` reimplemented from Kakushadze (2015), arXiv:1601.00991; project's own "facts of mathematics aren't copyrightable" theory | Explicit redistribution request: "Keep the arXiv citation intact… keep the display name **'Kakushadze 101 Formulaic Alphas'**… do not introduce [certain] trademark strings" (CI-enforced via `tools/ci_grep_gates.sh`) | `agent/src/factors/zoo/alpha101/LICENSE.md` `[EXPLICIT]` |
| `gtja191` zoo (191 factors) | `[REUSED WORK]` reimplemented from Guotai Junan Securities (2014); same copyrightability theory | Formula-only reproduction; per-alpha operator-substitution deviations from the original report are disclosed in-file | `agent/src/factors/zoo/gtja191/LICENSE.md` `[EXPLICIT]` |
| `academic` zoo (10 factors) | `[REUSED WORK]` Fama-French/Carhart/Hou-Xue-Zhang proxies; same theory | Explicit note to use Kenneth French's own data library as the authoritative series for research-grade claims, not this repo's price-based proxy | `agent/src/factors/zoo/academic/LICENSE.md` `[EXPLICIT]` |
| `fundamental` zoo (4 factors) | Not covered by a dedicated `LICENSE.md` found in this audit | — | `[UNKNOWN]` |

**Net assessment `[INFERENCE]`:** copying Alpha-Zoo code into a separate portfolio project means importing and tracking three or four distinct license/attribution regimes for content whose own `NOTICE` states the underlying formulas are not independently copyrightable in the first place. Since the formulas are "facts of mathematics," a candidate can reimplement 3–5 of them directly from the same cited primary sources (Kakushadze's paper, Fama-French) at low cost — converting `[REUSED WORK]` into genuinely candidate-owned code, with zero attribution bookkeeping and a much cleaner story to defend live. This is the cheaper and safer path relative to importing Vibe-Trading's own implementation.

---

## 5. Candidate-owned work remaining under each plausible adaptation

| Adaptation | What is already done upstream (not creditable to the applicant) | What would remain genuinely candidate-owned | Verdict-relevant risk |
|---|---|---|---|
| **Foundation** — fork the repo / build the portfolio project directly on its agent+backtest architecture | ~All visible engineering surface: the LLM-agent loop, 87 skills, MCP tooling, 8 backtest engines with real fee schedules, the PIT pipeline, the 460-factor Alpha Zoo, portfolio optimizers, web/CLI/Docker deployment, CI | Little to nothing that maps to the target role's "own code" ask — at most a new skill or data source | Untenable: this is the rubric's own explicit Criterion-8 weak-substitute example, "a team- or tutorial-derived repo lightly reskinned." A 20k-star public repo is trivially recognizable to a live reviewer |
| **Bounded component** — reuse one narrow, attributed piece (a loader, the OHLC-guard pattern, a handful of factor formulas) as an imported dependency | The specific loader's HTTP/parsing code, or the specific factor's closed-form implementation | Nearly everything the rubric scores: labels, model selection/training, validation-scheme design, diagnosis, packaging, the paper-trading demo | Low value for real cost: each reusable piece is individually cheap to reimplement from primary sources (§4), while formal reuse imports multi-license bookkeeping and "why does this look like a scoped clone of a public repo" interview risk for marginal time savings |
| **Reference only** — study design choices (PIT anchoring, per-market cost modeling, run-card idea, validation-suite naming, AST-sandboxing of generated code); import no code or data output | Nothing — no code crosses the boundary | Everything: 100% of the data pipeline, labeling, baseline + model comparison, leakage-safe validation, cost assumptions, diagnosis, packaging, and paper-trading loop, all independently defensible live | None of the license, ownership, or inherited-risk problems above apply. Cost: a smaller, from-scratch factor set than the Alpha Zoo's 460 — explicitly not a loss under this rubric's own stated preference for "a project that does less, correctly, with documented reasoning" over "one that does more with unexamined assumptions" |
| **Reject** — do not read it at all | — | — | Forfeits real, low-risk design-pattern learning (PIT anchoring, cost-schedule structure, run-card concept, generated-code sandboxing) that costs nothing to extract by reading only, with no license or ownership exposure. Not more defensible than reference only, only more wasteful |

---

## 6. Contrast with Packt's *Machine Learning for Algorithmic Trading* — a learning source only

Two repositories carry this lineage and were both examined: [`PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition`](https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition) (the Packt-branded 2nd-edition companion, itself a fork of the author's repository) and [`stefan-jansen/machine-learning-for-trading`](https://github.com/stefan-jansen/machine-learning-for-trading) (the author-maintained, currently-active 3rd-edition continuation of the same book lineage).

| | `stefan-jansen/machine-learning-for-trading` | `PacktPublishing/…-Second-Edition` | HKUDS/Vibe-Trading |
|---|---|---|---|
| Nature | Book companion (3rd ed., 10 of 27 planned chapters shipped) | Book companion (2nd ed., complete: 24 chapters), forked from stefan-jansen's own repo | LLM-agent trading product |
| Structure | Numbered notebook chapters + an installable `utils`/`data`/`case_studies` package | 24 numbered chapters, pure `.ipynb` notebooks, **no packaging** (no `setup.py`/`pyproject.toml`) | Full agent framework + web/CLI/MCP product |
| License | MIT | **None** — no `LICENSE` file on either `main` or `master`; the repo summary shows no License field at all `[EXPLICIT]` | MIT root + Apache-2.0/citation-request factor subsets (§4) |
| Real ML/DL/RL training content | Yes, shipped: Kalman filter, ARIMA/GARCH, Word2Vec, BERT fine-tuning, FinBERT, financial NER (Ch.9–10); XGBoost/LightGBM/CatBoost/PyTorch/`transformers`/`gymnasium`/`stable-baselines3` pinned for planned later chapters | Yes, extensively, all 24 chapters shipped: linear/logistic regression → random forests → XGBoost/LightGBM/CatBoost → CNN/RNN/BERT → GANs → deep Q-learning (`trading_env.py`) | **No** — see §2; `sklearn` appears exactly once, in a documentation file |
| LLM/agent orchestration or deployable product | No shipped agent/product code; an unpublished Ch.24 "Autonomous Agents" pins `langgraph`/`crewai`/`anthropic` as forward-declared teaching deps with no corresponding notebook yet | None anywhere in the tree or the 24-chapter table of contents | Yes — the architectural core |
| Role in this audit | Learning source | Learning source (the book referenced by the ticket) | Reference repository under audit |

**Why this matters for the build brief:** the two Packt-lineage repositories are the mirror image of Vibe-Trading — they are dense with exactly the trained-model, TensorFlow/PyTorch-adjacent content the target role's preferred competencies name, and Vibe-Trading is not. That makes them *more* useful to read for technique validation, and *no more* usable as a source of candidate-owned artifacts. The Packt fork's missing `LICENSE` file `[INFERENCE]` means its code carries **less** formal reuse permission than any part of Vibe-Trading (absent an explicit grant, default copyright applies) — reinforcing "read, don't copy" even more strongly here. If a chapter's gradient-boosting or deep-learning notebook were adapted into a submitted project, it would trip the same rubric red flag as any tutorial reuse: "problem framing lifted verbatim from a public notebook or tutorial" and "a team- or tutorial-derived repo lightly reskinned" (Criterion 1 / Criterion 8 weak substitutes). The correct use of Packt throughout the rest of this project: read a chapter to validate a technique choice or compare against a credible worked example, then implement the candidate's own version on the candidate's own data and labels — never submit adapted notebook code as the **portfolio project**'s own artifact.

---

## 7. Rubric impact and verdict

Impact of the reference-only posture against each of the eight scored criteria in [`looloo-project-evidence-rubric.md`](looloo-project-evidence-rubric.md) (weights sum to 100):

| # | Criterion | Wt | Reference-only impact |
|---|---|---|---|
| 1 | Problem Formulation & Literature-Grounded Research | 12 | Positive — citing this audit's reasoning in the candidate's own problem brief is itself the Exceptional-band artifact: "a documented instance of rejecting a popular technique on cited evidence." |
| 2 | Data Corpus Engineering | 14 | Neutral-to-positive — the PIT-anchoring and OHLC-integrity *patterns* (§3.1–3.2) are safe, valuable design references; full credit still requires the candidate to build and run their own data pipeline. |
| 3 | Modeling Depth & ML Foundations | 18 | No transferable content exists to reuse — Vibe-Trading's own ML layer is unshipped and untested (§2). The candidate supplies 100% of this criterion under every adaptation; reference-only costs nothing here relative to deeper reuse. |
| 4 | Experimentation Rigor & Reporting | 14 | Vibe-Trading's validation suite targets a different problem (post-hoc backtest consistency, not leakage-safe model-fit CV, §3.3); its naming/structure is a useful reference, not a drop-in leakage-safe validator. |
| 5 | Performance Diagnosis | 10 | The project's own issue-tracker discipline (e.g. #482, #476) is a good structural example of symptom→root-cause→fix write-ups — a pattern to emulate, not code to reuse. |
| 6 | Productionization & Engineering Fluency | 16 | The maintainer's own open, unchecked "release criteria for real trading" (§3.6) means importing Vibe-Trading code as a component would import its currently-unresolved risk profile. Reference-only still lets the candidate borrow the Docker/run-card/fee-schedule *design ideas* independently. |
| 7 | Market/Domain Fluency | 8 | The per-market fee-schedule constants (§3.4) are a strong, well-researched reference to verify against primary exchange sources and reimplement for the candidate's chosen market. |
| 8 | Ownership, Judgment & Culture-Fit Signal | 8 | Reference-only is the only posture that avoids the rubric's explicit "tutorial-/team-derived repo lightly reskinned" red flag; documenting this evaluation, as this audit does, is itself Exceptional-band self-critique evidence. |

**Why not the other three options, briefly:** *Reject* would forfeit real, low-risk design-pattern value (PIT anchoring, cost modeling, the run-card idea, generated-code sandboxing) that costs nothing to extract by reading only. *Bounded component* looked plausible for a single small loader or factor file, but every such piece is individually cheap to reimplement from the same primary sources Vibe-Trading itself cites (§4), while formal reuse adds multi-license bookkeeping and live-defensibility risk for marginal time saved. *Foundation* is untenable on its own terms — the bulk of what a hiring manager would see is upstream product engineering, not the target role's requested "own code," and it is the rubric's own worked example of a Criterion-8 red flag.

**Verdict.** `[EXPLICIT — this audit's own conclusion]` This audit's finding on HKUDS/Vibe-Trading, tied to the rubric impact above, is **reference only**. Study its point-in-time data-timing pattern, its per-market transaction-cost modeling, its run-card reproducibility idea, and its generated-code sandboxing approach — all worth learning from and reimplementing independently — but treat none of its code, data output, or Alpha Zoo as an imported component or foundation of the applicant's own portfolio project. Every criterion the rubric scores must be built, run, and defended by the candidate from primary sources.

---

## 8. Source ledger

| Source | Type | What it verified | Accessed |
|---|---|---|---|
| [`github.com/HKUDS/Vibe-Trading`](https://github.com/HKUDS/Vibe-Trading) (root + README, full) | Primary (repo) | Self-description, feature set, changelog, disclaimer, roadmap, contributor credits, repo stats (20,342 stars / 3,570 forks / 11 open issues at fetch) | 2026-07-13 |
| [`LICENSE`](https://github.com/HKUDS/Vibe-Trading/blob/main/LICENSE), [`NOTICE`](https://raw.githubusercontent.com/HKUDS/Vibe-Trading/main/NOTICE) | Primary (repo) | Root MIT license; Apache-2.0/academic-attribution disclosures | 2026-07-13 |
| [`pyproject.toml`](https://raw.githubusercontent.com/HKUDS/Vibe-Trading/main/pyproject.toml) | Primary (repo) | Full dependency manifest; confirmed absence of torch/tensorflow/xgboost/lightgbm/statsmodels | 2026-07-13 |
| `agent/src/factors/zoo/{alpha101,gtja191,fundamental,qlib158,academic}/**` incl. per-zoo `LICENSE.md`/`NOTICE` | Primary (repo) | Deterministic factor formulas; per-family license/attribution obligations | 2026-07-13 |
| `agent/src/skills/ml-strategy/SKILL.md`, `agent/SKILL.md`, `AGENT_CONTRIBUTOR_GUIDE.md` | Primary (repo) | Sole sklearn usage; project self-description as an agent/tool framework | 2026-07-13 |
| `agent/backtest/{validation.py,metrics.py,run_card.py,runner.py,engines/**,loaders/**,optimizers/**}` | Primary (repo) | Validation methods, cost/slippage schedules, PIT fundamentals mechanism, reproducibility schema, OHLC/calendar handling | 2026-07-13 |
| `agent/tests/factors/{test_alpha_purity.py,test_lookahead.py}`, `.github/workflows/test.yml` | Primary (repo) | Factor-layer leakage/sandboxing tests; CI scope | 2026-07-13 |
| `CONTRIBUTING.md`, `SECURITY.md`, `Dockerfile`, `docker-compose.yml`, `CHANGELOG.md`, `frontend/package.json` | Primary (repo) | Governance, security posture, deployment image, release history, frontend stack | 2026-07-13 |
| [Issue #476](https://github.com/HKUDS/Vibe-Trading/issues/476) / [Discussion #468](https://github.com/HKUDS/Vibe-Trading/discussions/468); Issues #482, #477 | Primary (GitHub) | Maintainer-tracked external security audit and open release-readiness gate; live correctness bugs | 2026-07-12/13 |
| Releases v0.1.8–v0.1.11 (`/releases/tag/…`) | Primary (GitHub) | Release cadence, dated "Caveats / Known limitations," test-count growth | 2026-07-13 |
| [`github.com/stefan-jansen/machine-learning-for-trading`](https://github.com/stefan-jansen/machine-learning-for-trading) (README, tree, `LICENSE`, `pyproject.toml`) | Primary (repo) | Book-companion self-description, chapter/notebook structure, MIT license, ML/DL/RL dependency breadth | 2026-07-13 |
| [`github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition`](https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition) (README, tree, `LICENSE` check) | Primary (repo) | Packt 2nd-edition companion structure, chapter content, confirmed absence of a `LICENSE` file | 2026-07-13 |
| [`looloo-project-evidence-rubric.md`](looloo-project-evidence-rubric.md) | Internal (this project) | Eight-criterion scoring rubric used in §7 | given |

**Could not verify:** per-file universality of the Qlib attribution header across all 154 `qlib158` factor files beyond the one file directly opened (the license file's own claim, not independently checked line-by-line); restatement-vs-original de-duplication behavior in the Tushare PIT path beyond "keep whichever row's PIT date already passed"; a dedicated license file for the 4-factor `fundamental` zoo; 8 of the 10 external-audit findings (VT-001, VT-003–VT-006, VT-008–VT-010) beyond the maintainer's own line-by-line confirmation — only VT-002 and VT-007 were independently re-verified against primary source for this audit. None of these gaps changes the verdict in §7.
