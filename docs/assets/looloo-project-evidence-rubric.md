# Looloo project-evidence rubric

Answers the research question: which observable portfolio artifacts evidence each demand in the supplied Looloo role, weighted for an ML hiring manager, with explicit vs. inferred claims separated and the company/role/"junior" context independently verified.

**Scope.** This is a scoring instrument for later tickets to evaluate *candidate project directions*. It does not evaluate Vibe-Trading, select a project, or implement anything. All research below was gathered 2026-07-12 against first-party Looloo sources where available, per the `research` and `firecrawl-search` skills.

**Tagging convention used throughout:** `[EXPLICIT]` = stated directly by a cited source. `[INFERENCE]` = my reasoning from explicit facts, flagged because a reasonable reader could disagree. Unmarked prose in the rubric criteria (artifacts/interview-proof/anchors) is rubric *design*, not a sourced claim — it draws on the explicit facts below but is my construction of what would evidence them.

---

## 1. Verification ledger — company, role, and "junior" status

### 1.1 At a glance

| Question | Answer | Status |
|---|---|---|
| Is the applicant's pasted listing real and current? | Yes — live on Looloo's own careers site today | `[EXPLICIT]` verified first-party |
| Is "Junior" a company designation or the applicant's gloss? | Company designation — a structured "Level: Junior Level" field on the same official listing | `[EXPLICIT]` verified first-party (reversal of the map's open caution) |
| Does the public company context match the role? | Yes — Looloo’s official site presents an AI/data consultancy with predictive-analytics work | `[EXPLICIT]` verified first-party |
| Is the applicant's brief a faithful copy of the JD? | Responsibilities and intro copy are word-for-word identical; competencies and values are a faithful paraphrase with no substantive additions/omissions | `[EXPLICIT]` verified by direct comparison |

### 1.2 Company identity

Looloo Technology Company Limited presents itself as an AI/data-analytics consultancy delivering customized solutions, with public product lines in predictive analytics, generative AI, NLP, OCR, and speech-to-text. Its public About page does not describe an internal trading operation. [`loolootech.com/about-us`](https://loolootech.com/about-us/) `[EXPLICIT]`


`[INFERENCE]` Do not infer Looloo’s internal trading team, strategy, or infrastructure from the project title. Finance knowledge stays a useful but lower-weight signal because the listing itself calls it “a plus”; the role’s required ML, data, experimentation, programming, and production duties remain the stronger evidence.

### 1.3 Role identity and currency

The applicant-supplied title, **"Machine Learning Engineer (Project Algorithmic Trading),"** is live today on Looloo's own official careers portal at [`careers.loolootech.com/job/41674`](https://careers.loolootech.com/job/41674) `[EXPLICIT]`. That page is a client-rendered (Vue/Nuxt) application; a plain HTTP fetch only returns the app shell and FAQ, so this was confirmed by rendering the page in a browser and reading the live DOM text directly on 2026-07-12.

Direct comparison of the rendered JD against the applicant-supplied brief:

- **Intro copy** ("What We're About," "What Your Work Looks Like") and **all seven Responsibilities bullets** are word-for-word identical between the brief and the live page.
- **Preferred requirements & competencies** and **What We Value** are a faithful editorial paraphrase in the brief — condensed wording, identical substance, no bullet added, dropped, or changed in meaning.


### 1.4 "Junior" — resolved

The map and role brief both flagged this as needing verification rather than trusting the applicant's paraphrase. **It is now resolved.** The same official listing page carries a structured metadata panel, separate from the JD prose, reading exactly:

> Level: **Junior Level** — Experience: **1 - 3 Years** — Type: **Full-time**

[`careers.loolootech.com/job/41674`](https://careers.loolootech.com/job/41674), confirmed by direct browser rendering 2026-07-12 `[EXPLICIT]`

This is a company-controlled designation, not the applicant's gloss — the rubric and any later ticket may now say "Looloo designates this role Junior Level" and cite this page directly.

One precision worth keeping: **the word "Junior" is a level *tag* on this posting, not part of the job-title *string*.** The title itself is "Machine Learning Engineer (Project Algorithmic Trading)," with no "Junior" prefix — targeted search for a distinctly-titled "Junior Machine Learning Engineer" at Looloo returned nothing Looloo-specific. Keep both facts distinct when citing this: the *level* is Junior; the *title* is not.

Also worth flagging rather than silently smoothing over: the metadata panel's **"1 - 3 Years"** does not exactly match the JD-prose bullet under Preferred requirements, **"At least 1-2 years of experience in creating AI models."** Both figures live on the same first-party page, in different UI regions (structured badge vs. free-text bullet); this rubric treats them as two data points from the same source rather than resolving them to one number. The applicant has not stated whether they meet either professional-experience range, so later tickets must not assume the answer.

### 1.5 How Looloo actually tests candidates (first-party — shapes "interview proof" throughout §3)

From Looloo's own application-process page, confirmed 2026-07-12:

1. **Submit application** — reviewed in 5–10 minutes.
2. **Technical Test 1** — for tech roles, a **90-minute programming assessment** on the "Job Passcard" platform, to be taken within 7 days of receiving instructions.
3. **Technical Test 2, "Live Proctored and Dynamic Review"** — coding/ML questions answered live, timed, and proctored, on Google Docs. **Senior programmers grade the answers and comment or ask follow-up questions; the candidate replies**; this back-and-forth can run **up to a week**.
4. **Partner interview** — 2–3 co-founders assess character and cultural fit; some roles add a short IQ/EQ/general-logic test first.
5. **Final decision** — roughly 5 business days on average.

[`careers.loolootech.com/application-process`](https://careers.loolootech.com/application-process) `[EXPLICIT]`

The same site's FAQ states the required supporting document is a Resume/CV; **Transcript and Portfolio are both listed as optional**. A separate FAQ entry: *"If you have no related working experience but are passionate and confident in your abilities, we encourage you to apply anyway. Our application process is designed to help reveal your ability to perform in the role."* [`careers.loolootech.com/job/41674`](https://careers.loolootech.com/job/41674) FAQ section `[EXPLICIT]`

`[INFERENCE]` Read together, these two facts reframe what "interview proof" should mean in this rubric: the actual gate is a **live, senior-programmer-graded, adversarial technical dialogue**, not a portfolio walkthrough — the portfolio never appears in the required-documents list at all. A project's job is not to look finished; it is to arm the candidate to defend every design choice, unprompted, under a week of live back-and-forth with a senior engineer looking for gaps. Every "Interview proof" entry in §3 is written against this specific mechanism, not a generic "talk about your project" interview.

### 1.6 What this research could not verify

`[INFERENCE / explicit limitation]` No public source describes Looloo's internal trading-project team structure, whether the "(Project Algorithmic Trading)" work is an in-house strategy desk or a client engagement, or its data/infrastructure stack. None of this changes the rubric below, which is built from the explicit JD text and explicit hiring-process mechanics, not from guessed internals — consistent with the map's standing boundary against reverse-engineering Looloo's proprietary details.

---

## 2. How to read this rubric

- **Weights sum to exactly 100** across eight scored criteria (§3). Two JD items — the degree and years-of-experience preferred-competency bullets — are deliberately **not** part of the 100-point scale; scoring them by a portfolio would misrepresent what a project can do. They get their own non-scored section (§5) instead.
- Each criterion states: the **role demand** (with its source), **observable candidate-owned artifacts/decisions** a hiring manager could actually check, **interview proof** (calibrated to Looloo's live, senior-programmer-graded process — §1.5), **weak or misleading substitutes** that look like evidence but aren't, and **scoring anchors** in points.
- Anchors reward **rigor and defensibility over volume**, per the map's own steer to value "a coherent end-to-end artifact over gratuitous scope" given there is no fixed time ceiling — a project that does less, correctly, with documented reasoning, should consistently outscore one that does more with unexamined assumptions.
- The rubric scores **project directions**, not the applicant. It is deliberately silent on which market, asset class, or technique to choose — that's out of scope here.
- "Historical research plus paper-trading only, no live money" (the map's stated boundary) is assumed throughout; no criterion rewards or expects live capital.

---

## 3. The 100-point rubric

| # | Criterion | Weight |
|---|---|---|
| 1 | Problem Formulation & Literature-Grounded Research | 12 |
| 2 | Data Corpus Engineering | 14 |
| 3 | Modeling Depth & ML Foundations | 18 |
| 4 | Experimentation Rigor & Reporting | 14 |
| 5 | Performance Diagnosis | 10 |
| 6 | Productionization & Engineering Fluency | 16 |
| 7 | Market/Domain Fluency (a plus, not a gate) | 8 |
| 8 | Ownership, Judgment & Culture-Fit Signal | 8 |
| | **Total** | **100** |

### Criterion 1 — Problem Formulation & Literature-Grounded Research (12 pts)

**Role demand.** "Formulate real-world problems into AI/ML problems" and "Research information to gain deeper understanding about the given problem and the appropriate solutions for solving it; may involve reading academic papers." [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** A concise problem brief, written before modeling, that names the target variable, prediction horizon, evaluation metric, baseline, and label-leakage risks. A short research log should show which sources changed a decision, including at least one technique adopted or rejected for a stated reason.

**Interview proof.** Under Looloo's live-proctored, senior-programmer review (§1.5), the candidate must justify the framing — regression vs. classification vs. ranking, the chosen baseline, and 2–3 sources that shaped the design — from memory, including candid critique of those sources, not a recital of a README.

**Weak/misleading substitutes.** A "References" list with no evidence any reading changed a decision; a problem statement written *after* modeling started (post-hoc rationalization); a problem framing lifted verbatim from a public notebook or tutorial.

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | Jumps straight to code; no stated problem, metric, or baseline |
| Weak | 3 | Problem stated, but no baseline and no leakage discussion |
| Solid | 8 | Clear problem statement + baseline + ≥2 literature-grounded design decisions |
| Exceptional | 12 | Solid, plus a documented instance of rejecting a popular technique on cited evidence |

### Criterion 2 — Data Corpus Engineering (14 pts)

**Role demand.** "Write programs to process, sanitize, clean, manipulate data, which may be unstructured" and "Build a database/corpus of relevant data for the purpose of machine learning." [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** A re-runnable data build from an authoritative raw source—API, filings, or a versioned download—with source provenance and checksums where appropriate; a documented schema/data contract; explicit handling of relevant financial-data traps such as corporate actions, survivorship bias, timezone/session alignment, and point-in-time correctness; focused automated checks for gaps, duplicate timestamps, and unexpected missing values.

**Interview proof.** Candidate describes a *specific* data bug they found and fixed (e.g., an unadjusted split producing a fake 10x return spike) and explains point-in-time vs. as-of-today risk unprompted — a natural target for the senior-programmer follow-up questions in Looloo's Test 2.

**Weak/misleading substitutes.** One vendor's pre-cleaned CSV re-labeled a "corpus"; "cleaning" that is just `dropna()`; a pipeline that only runs once, by hand, on the author's machine.

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | Single static file, no pipeline |
| Weak | 4 | Basic ingestion script, no data-quality checks |
| Solid | 9 | Ingestion + schema + ≥1 documented survivorship/look-ahead fix |
| Exceptional | 14 | Solid, plus automated data-quality tests and a data contract a stranger could follow |

### Criterion 3 — Modeling Depth & ML Foundations (18 pts)

**Role demand.** "Create machine learning algorithms using a combination of existing libraries/frameworks and own code"; "Good understanding of AI/ML foundations in theory and application"; "Experience developing and deploying ML models"; "Familiar[ity] with machine learning frameworks such as Tensorflow or PyTorch." [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** A simple baseline plus at least two justified model candidates, with results shown for all of them. Candidate-authored code should expose understanding—a baseline, feature transform, loss calculation, or training/evaluation loop—but a custom architecture is not required. TensorFlow/PyTorch should appear only when the chosen problem warrants it; otherwise the project should explain why a simpler model or library is the better technical decision.

**Interview proof.** Candidate can explain the loss, regularization, inductive bias, and failure modes of each serious model candidate; trace their own training/evaluation code; and justify why the final choice fits measured properties of the data rather than fashion. This is the kind of reasoning Looloo's Test 2 can probe (§1.5).

**Weak/misleading substitutes.** An unexplained AutoML or copied deep-learning pipeline; a custom loss or architecture added only to look advanced; unused TensorFlow/PyTorch boilerplate; one model with no baseline or rationale.

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | One unexplained library call; no baseline or comparison |
| Weak | 5 | One model family, explained only superficially |
| Solid | 12 | Baseline + ≥2 appropriate model candidates compared; candidate can explain and trace the implementation |
| Exceptional | 18 | Solid, plus measured ablations and a defensible final choice whose complexity is no greater than the evidence warrants |

### Criterion 4 — Experimentation Rigor & Reporting (14 pts)

**Role demand.** "Run experiments based on various solutions, analyze results, and produce/present reports to the team." [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** Tracked experiments using a simple structured log with versioned configs and seeds; a leakage-safe temporal validation scheme appropriate to the target—such as rolling/walk-forward or purged/embargoed splits, with the choice justified; a written comparison with uncertainty and a “what did not work” section. Random k-fold on time-dependent observations is a correctness red flag.

**Interview proof.** Candidate states the hypothesis behind one experiment, its result, and the next decision; then explains why the chosen temporal validation prevents leakage for this specific target.

**Weak/misleading substitutes.** One train/test split and one number; a cherry-picked best run with no failed runs; random k-fold applied to dependent time-series observations without justification.

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | One run, one number, no stated methodology |
| Weak | 4 | Multiple runs, but no leakage-safe validation scheme |
| Solid | 9 | Justified temporal validation + tracked, comparable experiments |
| Exceptional | 14 | Solid, plus a written report with negative results and uncertainty quantification, presentable to a team |

### Criterion 5 — Performance Diagnosis (10 pts)

**Role demand.** "Strong analytical skills. Can investigate and fix model[]s' performance issues." [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** Error analysis sliced by regime, sector, or volatility bucket rather than one aggregate number; a documented root-cause narrative for a real failure the candidate hit (traced to, e.g., a leakage bug, a data outage, or a regime shift) with before/after evidence; residual or calibration analysis, not just top-line accuracy.

**Interview proof.** Candidate walks a real debugging session end to end — symptom, hypotheses ruled out, root cause, fix, verification — the exact shape of question Looloo's senior-programmer reviewers are positioned to probe over the week-long Test 2 dialogue (§1.5).

**Weak/misleading substitutes.** Aggregate metrics only, never sliced; blaming "the market is efficient" without first checking for a leakage or implementation bug; re-running with a new random seed and calling it "fixed."

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | No error analysis at all |
| Weak | 3 | Aggregate metrics only |
| Solid | 7 | Sliced error analysis by a meaningful axis |
| Exceptional | 10 | Solid, plus a documented root-cause-and-fix narrative with verifiable before/after evidence |

### Criterion 6 — Productionization & Engineering Fluency (16 pts)

**Role demand.** "Productionize AI/ML systems in order to solve the assigned problems" and "Can write complex programs fluently and efficiently." [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** A packaged codebase (proper module layout, pinned dependencies, a real CLI or service entrypoint) with unit tests and CI, not a single notebook; a scheduled or automatable **paper-trading loop** — inference → simulated order → position/P&L tracking → logging — run **unattended for a real stretch of time** with logged results, not a single backtest pass; a git history showing iterative engineering rather than one giant commit.

**Interview proof.** Candidate navigates their own codebase live, explains a concrete design tradeoff (why this scheduler, how a 3am data-feed outage is handled), and shows real logs or monitoring output from an unattended run.

**Weak/misleading substitutes.** A single top-to-bottom notebook presented as "production"; a "live" demo that's actually a historical replay dressed up as real-time; "productionized" claimed with no evidence of run duration, monitoring, or any handled failure.

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | Notebook only |
| Weak | 4 | Scripts, but no tests or packaging |
| Solid | 10 | Packaged, tested code with a paper-trading loop that ran at least briefly |
| Exceptional | 16 | Solid, plus evidence of a multi-day/week unattended run with logs, monitoring, and ≥1 handled failure |

### Criterion 7 — Market/Domain Fluency — a plus, not a gate (8 pts)

**Role demand.** "Knowledge and understanding of the stock market, financial products, technical graphs, and securities trading theory **is a plus**" — the JD's own words, explicitly optional. [role brief / `careers.loolootech.com/job/41674`] Weighted lowest of the technical criteria deliberately, matching that explicit optionality and the `[INFERENCE]` from §1.2 that Looloo is a general AI consultancy rather than a proprietary trading shop.

**Observable artifacts/decisions.** Correct market-microstructure basics inside the paper-trading simulation itself: trading calendar/holidays, corporate actions, transaction-cost and slippage modeling, position sizing/risk limits; explicit and *correctly computed* use of concepts like look-ahead bias, survivorship bias, Sharpe/Sortino, and max drawdown — not just the vocabulary.

**Interview proof.** Candidate explains, unprompted, why raw price-prediction accuracy doesn't imply profitability, and what specifically their simulation does to avoid overstating results.

**Weak/misleading substitutes.** A backtest with zero transaction costs or slippage presented as a real return; "technical indicators" used as generic feature names with no understanding of what they measure; a Sharpe ratio quoted without stating the risk-free rate, period, or annualization convention used.

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | No domain awareness; costs/calendar ignored |
| Weak | 2 | Indicators used as generic features, no market-structure grounding |
| Solid | 5 | Correct handling of calendar/costs/leakage basics |
| Exceptional | 8 | Solid, plus correctly computed risk/performance metrics with stated assumptions and a candid discussion of why the strategy might not survive out-of-sample |

### Criterion 8 — Ownership, Judgment & Culture-Fit Signal (8 pts)

**Role demand.** Directly operationalizes "What We Value": not satisfied with surface-level answers; high ownership and active quality improvement; team players who help others; adaptive, thoughtful, introspective, willing to learn/teach/lead/follow. [role brief / `careers.loolootech.com/job/41674`]

**Observable artifacts/decisions.** A "known limitations / what I'd do with more time" section that names *specific* gaps, not generic boilerplate ("add more data," "try deep learning"); commit history or a changelog showing a design was revisited after a flaw was found, not one clean pass; a decision log explaining rejected alternatives in the candidate's own reasoning.

**Interview proof.** When pressed with "why not X instead" during the live-proctored review, the candidate has a substantive, specific answer rather than "I didn't think of that," and can teach the interviewer something from the project clearly — the partner interview (§1.5) is explicitly built to assess exactly this character/fit signal.

**Weak/misleading substitutes.** A polished README that hides every failed approach; generic future-work bullets with no specificity; ownership claims not backed by commit history (a team- or tutorial-derived repo lightly reskinned).

**Scoring anchors.**

| Band | Pts | Description |
|---|---|---|
| Absent | 0 | No visible self-critique; generic claims only |
| Weak | 3 | Some limitations noted, but generic |
| Solid | 6 | Specific, evidenced self-critique and iteration visible in history |
| Exceptional | 8 | Solid, plus interview-verified depth — candidate can go deeper than the README, unprompted |

---

## 4. Requirement coverage map

Every responsibility and preferred competency from the supplied brief, mapped to at least one scored criterion (or to §5 if it is a credential, not a portfolio-scorable skill).

| # | Source item (role brief) | Type | Mapped to |
|---|---|---|---|
| R1 | Formulate real-world problems into AI/ML problems | Responsibility | C1 |
| R2 | Research information … may involve reading academic papers | Responsibility | C1 |
| R3 | Write programs to process, sanitize, clean, manipulate data, which may be unstructured | Responsibility | C2 |
| R4 | Build a database/corpus of relevant data for the purpose of machine learning | Responsibility | C2 |
| R5 | Create machine learning algorithms using a combination of existing libraries/frameworks and own code | Responsibility | C3 |
| R6 | Run experiments … analyze results, and produce/present reports to the team | Responsibility | C4 |
| R7 | Productionize AI/ML systems in order to solve the assigned problems | Responsibility | C6 |
| P1 | Bachelor's degree or higher in Data Engineering, Computer Engineering, Data Science or other related fields | Preferred competency | §5 (credential — not portfolio-scored) |
| P2 | At least 1–2 years of experience in creating AI models (page metadata separately shows 1–3 years / Junior Level) | Preferred competency | §5 (credential — not portfolio-scored) |
| P3 | Knowledge of the stock market, financial products, technical graphs, securities trading theory — "is a plus" | Preferred competency | C7 |
| P4 | Good understanding of AI/ML foundations in theory and application | Preferred competency | C3 |
| P5 | Experience developing and deploying ML models | Preferred competency | C3 (developing) + C6 (deploying) |
| P6 | Familiarity with TensorFlow or PyTorch | Preferred competency | C3 |
| P7 | Ability to write complex programs fluently and efficiently | Preferred competency | C6 |
| P8 | Strong analytical skills; can investigate and fix model-performance issues | Preferred competency | C5 |
| V1 | Not satisfied with surface-level answers | Value | C8 (also threaded into C1's "rejected a technique on cited evidence" artifact) |
| V2 | High ownership and active quality improvement | Value | C8 |
| V3 | Team players who help others | Value | C8 (interview-only signal; no portfolio artifact directly proves this) |
| V4 | Adaptive, thoughtful, introspective; willing to learn, teach, lead, and follow | Value | C8 |

All 7 responsibilities and all 8 preferred competencies map to a named criterion. Six of the eight preferred competencies (P3–P8) are portfolio-scorable and sit inside the 100 points; two (P1, P2) are credentials a project cannot manufacture and are handled separately in §5, by design — scoring them inside the 100 would imply a project can buy back a degree or years of experience, which it cannot.

---

## 5. Credential constraints: non-technical degree and unverified experience

This section is deliberately **outside the 100-point scale.**

**What the listing prefers.** A Bachelor's degree "in Data Engineering, Computer Engineering, Data Science or other related fields," and separately, at least 1–2 years of experience creating AI models per the JD prose (or "1 - 3 Years" per the page's own level-metadata badge, tagged "Junior Level" — see §1.4). Both appear under the role’s preferred requirements or metadata rather than its Responsibilities. [`careers.loolootech.com/job/41674`] `[EXPLICIT]`

**What the applicant has stated.** The applicant-supplied tracker records a non-technical degree background and independent classical-ML project capability. It does not state whether the applicant meets either professional-experience range, so this research neither awards nor assumes that credential. This is applicant-supplied context, not independently verifiable.

**How the rubric treats this — three explicit rules:**

1. **No criterion in §3 gives points for having, or for appearing to have, a technical degree or professional tenure.** A project cannot be scored as "worth 1.5 years of experience" — that would misrepresent what a demonstration proves, which is the applicant's own stated constraint and the map's standing instruction.
2. **A strong project can still change the outcome, through a different, real mechanism: it lowers the hiring manager's *uncertainty about capability*, which is precisely what Looloo's own hiring process is built to test independently of the résumé.** Two first-party facts support this reading: Transcript and Portfolio are optional, and Looloo encourages candidates with no related work experience to apply because its process is designed to reveal ability. [`careers.loolootech.com/job/41674` FAQ, `careers.loolootech.com/application-process`] `[EXPLICIT]` The project should prepare the candidate for the 90-minute assessment and senior-programmer-graded live review, not try to impersonate listed credentials.
3. **A project must not be presented as a substitute for a degree or professional tenure.** Do not claim “professional-equivalent experience” or inflate scope to look senior. The honest claim is narrower: this is verifiable work the hiring team can interrogate. Overclaiming would itself be a negative Criterion 8 signal.

In short: portfolio evidence can move the needle on *ability*, which Looloo says it wants to see revealed regardless of background — it cannot, and should not try to, move the needle on the *credential itself*.

---

## 6. Minimum credible evidence package

The floor below which a project direction isn't worth a hiring manager's time — not a target score, a gate:

- A **concise problem brief and evaluation metric**, committed before modeling began (Criterion 1).
- A **re-runnable data build from an authoritative raw source**, with provenance and at least one documented fix for a relevant financial-data trap; a versioned static source is acceptable when it is the authoritative input (Criterion 2).
- A **simple baseline plus at least one appropriate ML alternative**, with candidate-authored training or evaluation code and no custom complexity added solely for appearance (Criterion 3).
- **Leakage-safe temporal validation**, tracked across multiple runs, with a written report including at least one negative result (Criterion 4).
- **One documented root-cause diagnosis** of a real performance problem, with before/after evidence (Criterion 5).
- **Packaged, tested code plus a repeatable paper-trading loop with useful logs**—not a notebook and not a one-off backtest (Criterion 6).
- **Transaction costs and slippage modeled** in any P&L claim; no cost-free backtest presented as a result (Criterion 7).
- **A specific, evidenced limitations section** and a git/commit history that shows the design was actually iterated, not authored in one pass (Criterion 8).
- The candidate must be able to **reproduce and defend every reported number live, unprompted** — this is a process requirement, not an artifact, but it is the literal shape of Looloo's Test 2 (§1.5), so nothing should be claimed in a write-up that the candidate cannot re-derive on a whiteboard under follow-up questioning.
- **No claim that the project substitutes for listed degree or experience preferences** (§5)—its job is to reduce uncertainty about ability, not impersonate a credential.

A direction that can't clear this floor isn't ready to compare against alternatives yet, regardless of raw scope.

---

## 7. Source ledger

| Source | Type | What it verified | Accessed |
|---|---|---|---|
| Applicant-supplied tracker context (not published) | Applicant-supplied | Applicant background and standing project constraints | given |
| [`careers.loolootech.com/job/41674`](https://careers.loolootech.com/job/41674) | First-party (Looloo, live SPA, rendered directly) | Exact JD text; **"Level: Junior Level," "Experience: 1 - 3 Years," "Type: Full-time"**; FAQ on optional portfolio/transcript and no-experience encouragement | 2026-07-12 |
| [`careers.loolootech.com/application-process`](https://careers.loolootech.com/application-process) | First-party (Looloo) | Five-step hiring process; 90-minute programming test; live-proctored, senior-programmer-graded ML/programming review | 2026-07-12 |
| [`loolootech.com/about-us/`](https://loolootech.com/about-us/) | First-party (Looloo) | Public AI/data-consultancy and product-line context | 2026-07-12 |
| Firecrawl web search ×6 | Search index | Discovery only; feedback sent for each query per the `firecrawl-search` skill | 2026-07-12 |

**Could not verify:** Looloo's internal trading-team structure, data, strategy, or infrastructure. No conclusion in this rubric depends on guessing those details.
