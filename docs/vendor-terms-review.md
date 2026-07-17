# Vendor-terms & data-governance review

**Status:** decided.
**Decision date (access date for all terms below):** 2026-07-16.
**Scope:** governs (a) whether the aggregate evidence package (README "public allowlist", line 52) may be published, and (b) retention/purge of the accepted real-derived archive. Resolves [issue #1](https://github.com/mingrath/looloo-finance-ml/issues/1).
**Method:** AFK review of primary sources (Alpaca disclosures library, IEX market-data policy, SEC EDGAR fair-access policy). This records the conservative outcome mandated by the project's own publish-gate (README line 42: publish aggregates *only if* current terms affirm that exact disclosure; otherwise code + synthetic only). It is not new human risk-acceptance: flipping to "publish real aggregates" requires the separate decision tracked in [issue #9](https://github.com/mingrath/looloo-finance-ml/issues/9).

## Outcome (plain statement)

**Code + synthetic verification only.** Do **not** publish the real-derived aggregate package, and do **not** privately redistribute it. The public repository ships candidate-authored code plus the synthetic-fixture evidence package; any real `--live` run's outputs remain local, access-controlled, and git-ignored. Independent attestation of a real run is done by a reviewer using their **own** permitted Alpaca access (they reproduce; they are not handed licensed-derived artifacts).

Rationale: current Alpaca terms do not *affirm* that the specific aggregate disclosure is permitted — they impose a blanket, consent-gated prohibition on reproducing/distributing/commercially exploiting market data, with no derived-data carve-out, reinforced by incorporated exchange subscriber agreements. Under the project's publish-gate, absence of an affirmative permission means the default-deny branch applies.

## Alpaca market-data terms

- **Current governing document:** Alpaca Account Application and Customer Agreement — <https://files.alpaca.markets/disclosures/library/AcctAppMarginAndCustAgmt.pdf> (linked from the authoritative index at <https://alpaca.markets/disclosures>). Accessed 2026-07-16.
- **Operative clause:** **§30 "Use of Market Data and Waiver or Limitation of Liability"** (renumbered from §23 in the repo-pinned snapshot). Verbatim operative sentence:
  > "I agree not to reproduce, distribute, sell or commercially exploit the market data in any manner without written consent from Alpaca."
  §30 also states each participating national securities exchange/association "asserts a proprietary interest in all of the market data it furnishes", and that the NASDAQ OMX Global Subscriber Agreement and NYSE Market Data Display Services Agreement are incorporated by reference.
- **Repo-pinned snapshot (for provenance):** `alpaca_customer_agreement_v20200403.pdf` (dated 2020-04-03), cited across `README.md`, `docs/build-brief.md`, `docs/assets/selected-project-contract.md`, and captured in the run source ledger. Its §23 carries the **identical** operative sentence.
- **Delta between snapshot and current terms:** the non-professional data provider named in §30 changed from **Polygon.io, LLC** (2020 snapshot) to **AlpacaDB, Inc.** (current), consistent with Alpaca's move to its own IEX/SIP-sourced feed. The redistribution restriction itself is unchanged. Section number moved 23 → 30. **The change does not affect the outcome.**
- **Alpaca's official position (corroborating):** developer support states "Unfortunately, you cannot redistribute Alpaca API data"; commercial redistribution requires a separate Broker API / partnership agreement, not the standard retail Customer Agreement.

### Why the aggregate allowlist is not exempt

1. **Sourced via Alpaca, not directly from IEX.** Data reaches this project through the Alpaca Market Data API. Alpaca's own position: data accessed *via* the Alpaca API is governed by the Alpaca agreement. IEX's separately favorable Derived Data policy (below) is available to **direct IEX Data Subscribers** under a signed IEX Data Subscriber Agreement — this project is not one — and IEX itself bars furnishing "IEX API data received through third parties" absent direct consumption.
2. **No derived-data carve-out in Alpaca's terms.** §30 restricts "the market data in any manner" without distinguishing raw vs. aggregated/derived output, and does not affirmatively permit publishing derived aggregates.
3. **Incorporated exchange agreements broaden the restriction.** Exchange market-data definitions (NASDAQ OMX, NYSE — incorporated by reference) typically sweep "all information that derives from" the data into "Market Data", keep it restricted to the non-professional subscriber's personal/non-business use, and name the exchanges (SROs) as third-party beneficiaries able to enforce.

The allowlist (aggregate report, provenance/hash index, model/fold/robustness aggregates, weekly portfolio returns, model comparison, cost sensitivity, skip counts — no bars, no SEC facts, no symbol-level features/predictions/fills, no per-date IC, no top-tercile return series) is deliberately non-reversible derived data. That design is exactly what *would* qualify under IEX's Derived Data policy **if** the data were sourced under a direct IEX subscription — but it is not, so the Alpaca restriction controls and there is no affirmative permission. This asymmetry is the basis for the escalation path below.

### IEX Derived Data policy (context; not currently available to this project)

IEX defines Derived Data as information generated from IEX Market Data that cannot be reverse-engineered to recreate the original, and permits subscribers to create/use/**distribute Derived Data externally free of charge** with attribution ("Data provided for free by IEX. By accessing or using IEX Historical Data, you agree to the IEX Historical Data Terms of Use."). This favorable path requires consuming data **directly from IEX** as a Data Subscriber, not via a third party such as Alpaca. Recorded here because it is the cleanest lawful route to publishable real aggregates (see escalation).

### Demonstrated feed revised to SIP (contract revision #14) — outcome unchanged

The frozen data contract was revised `feed=iex` → `feed=sip` ([issue #14](https://github.com/mingrath/looloo-finance-ml/issues/14), implementing [#12](https://github.com/mingrath/looloo-finance-ml/issues/12)) so the demonstrated run sources full-market SIP consolidated bars (free on the Alpaca Basic plan for historical data older than 15 minutes). **This does not change the outcome above.** The controlling restriction is §30's feed-agnostic prohibition — "reproduce, distribute, sell or commercially exploit the market data in any manner" (quoted above) — which draws no line between IEX and SIP; SIP is likewise consumed *via* the Alpaca Market Data API, so §30 governs it exactly as it governed IEX, and §30 alone is sufficient for the unchanged outcome. The incorporated NASDAQ OMX / NYSE exchange subscriber agreements (§30 header; "Why the aggregate allowlist is not exempt", point 3) reinforce this — their market-data definitions *typically* sweep consolidated/derived output into the restriction — but that point is corroborating, not load-bearing. The publish posture (#1 + #9(a)) is therefore **unchanged**: code + synthetic-fixture evidence + completed reviewer attestation public; real SIP-derived aggregates stay local-only and non-redistributable under the same Retention & purge policy.

Record one asymmetry for the escalation path: **route 2** (direct-IEX re-source under IEX's Derived Data policy) would now publish aggregates derived from a **different feed** — IEX single-exchange — than the one the project actually demonstrates (SIP consolidated). It stays documented and reversible as a lawful publish route, but it is no longer feed-parity with the accepted run, so any future pursuit must disclose that the published and demonstrated feeds differ. Route 1 (Alpaca §30 written consent) covers the demonstrated SIP feed directly.

## Retention & purge policy for the accepted real-derived archive

The accepted `artifacts/<live-run>` tree (raw + normalized Alpaca bars, predictions, model files, event logs, bootstrap samples, per-date IC, symbol-level series) is licensed, non-redistributable data. Posture is **data minimization**:

- **Storage:** local only, access-controlled, git-ignored (already enforced: `artifacts/` is ignored; public-evidence export is default-deny and gated on `source_mode`). Never committed; never placed in shared/cloud storage.
- **Retention duration:** retain an accepted archive no longer than **12 months** from its run date.
- **Purge triggers — delete within 30 days of the earliest of:**
  1. the active hiring/interview cycle for which the run was produced concludes;
  2. Alpaca account closure or loss of permitted access;
  3. a written request from Alpaca or a participating exchange;
  4. supersession by a newer accepted run (retain at most one accepted archive at a time).
- **Manual purge action:** delete the entire `artifacts/<live-run>` directory (and any local backups). Non-licensed provenance metadata already permitted for disclosure (request manifest, response hashes, terms snapshot) may be retained for reproducibility claims; licensed bars/derived symbol-level artifacts may not.

## SEC EDGAR — fair-access / User-Agent (re-confirmed for run cadence)

- **Public data APIs (`data.sec.gov`, `www.sec.gov`):** free, no API key. **Max 10 requests/second per IP**; exceeding it risks a temporary IP block.
- **Mandatory descriptive `User-Agent`** identifying the app and an administrative contact (format `Sample Company Name AdminContact@domain.com`). The project already requires `SEC_USER_AGENT` (README line 29); keep it descriptive with a real contact.
- **Reuse rights:** SEC site information is public government data, copyable/redistributable with attribution and no implied endorsement — so SEC-derived aggregates are *not* the constraint here (and the allowlist excludes symbol-level SEC facts regardless).
- **Cadence compliance:** the project's weekly decision cadence plus a bounded warm-up backfill is far below 10 req/s; obey the limit, download only what is needed, preserve attribution. Source: <https://www.sec.gov/os/webmaster-faq#developers> / <https://www.sec.gov/developer> (accessed 2026-07-16).

## Escalation path (how to flip the outcome later)

The outcome is reversible **only** by obtaining an affirmative permission. Two lawful routes, both tracked as a decision in [issue #9](https://github.com/mingrath/looloo-finance-ml/issues/9):

1. **Written consent from Alpaca** for the specific aggregate disclosure (§30 consent, or a Broker API / partnership arrangement), or
2. **Re-source daily bars directly from IEX** as a Data Subscriber and publish under IEX's Derived Data policy with required attribution. *(Post-#14 this re-sources a **different** feed — IEX single-exchange — than the demonstrated SIP consolidated run; see "Demonstrated feed revised to SIP" above. Still documented and reversible.)*

Absent either, the public posture stays code + synthetic only. This does not block the first real `--live` run ([issue #5](https://github.com/mingrath/looloo-finance-ml/issues/5)) — that run may proceed for transient local validation; only retention and publication are governed by this review.

## Publish-path decision (#9) — RESOLVED (a): synthetic-only public is final

**Decision date:** 2026-07-16. **Decided by:** @mingrath (human risk-acceptance, HITL). Resolves [issue #9](https://github.com/mingrath/looloo-finance-ml/issues/9) — the separate "flip the outcome" decision this document reserved in its intro.

**Outcome: (a) — accept the code + synthetic-verification public posture as final.** Do **not** pursue Alpaca written consent (b1) or direct-IEX re-sourcing (b2) at this time.

- **Public artifact (final):** candidate-authored code + the **synthetic**-fixture evidence package + a **completed** `review_attestation.json` (reviewer records CI URL/result, terms URL/version/access date, publication decision, and public contact; `status` → complete — no cryptographic signature mechanism exists or is implied).
- **Withheld (local-only, git-ignored):** the real `--live` run's aggregate numbers and all real-derived artifacts, governed by the Retention & purge policy above.
- **Trust mechanism:** a **distinct reviewer privately reproduces** a real run on their **own** permitted Alpaca access and completes the public attestation — the project never hands over licensed-derived artifacts.

**Escalation deferred, not abandoned.** The two routes in "Escalation path" above remain the sanctioned way to publish real aggregates later, and the outcome stays reversible — pursue one **only if a reviewer explicitly demands published real numbers**. Neither route's eligibility, effort, or fees have been assessed, so either would require scoping before commitment.

**Effect on the evidence package ([issue #6](https://github.com/mingrath/looloo-finance-ml/issues/6)):** its public output is now **finalized** as the synthetic package + completed attestation with real aggregates withheld — no longer "pending #9". (Still blocked by the first real `--live` run, [issue #5](https://github.com/mingrath/looloo-finance-ml/issues/5).)

## Re-verification

Alpaca may amend its agreement at any time (§30 header: terms revised on the website; continued use accepts them). Re-verify the live §30 text and capture a fresh terms snapshot **at each accepted live run**, and re-open this review if the market-data clause materially changes.

## Sources

- Alpaca Account Application and Customer Agreement (current), §30 — <https://files.alpaca.markets/disclosures/library/AcctAppMarginAndCustAgmt.pdf>, accessed 2026-07-16.
- Alpaca Disclosures & Agreements index — <https://alpaca.markets/disclosures>, accessed 2026-07-16.
- Alpaca Customer Agreement v20200403 (repo-pinned snapshot), §23 — <https://files.alpaca.markets/disclosures/alpaca_customer_agreement_v20200403.pdf>, accessed 2026-07-16.
- Alpaca developer support / redistribution position (corroborating), accessed 2026-07-16.
- IEX Exchange market-data & Derived Data policy — <https://exchange.iex.io/>, accessed 2026-07-16.
- SEC EDGAR fair-access policy & developer resources — <https://www.sec.gov/developer>, accessed 2026-07-16.
