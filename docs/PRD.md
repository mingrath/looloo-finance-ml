# Select and specify a Looloo-ready Finance ML portfolio project

Status: ready-for-agent

## Problem Statement

The applicant is targeting Looloo’s junior-level Machine Learning Engineer (Project Algorithmic Trading) role without a directly related technical degree. The role asks for strong programming, applied and theoretical ML understanding, data-corpus work, controlled experimentation, performance diagnosis, and productionization; finance knowledge is explicitly a plus. Looloo’s published hiring process tests programming and ML directly, while a portfolio is optional.

The applicant therefore needs hiring evidence that is candidate-owned, technically defensible, and easy to interrogate—not a visually impressive trading demo whose ML, data, or evaluation came from another repository. HKUDS/Vibe-Trading may be useful as a reference repository, but its relevance, originality ceiling, and methodological quality have not yet been established. The Packt Machine Learning for Algorithmic Trading repository is a knowledge source, not candidate-owned work.

Without one researched selection and a decision-complete build brief, the applicant risks copying an agent framework, overbuilding a dashboard, using a leaky backtest, or choosing model complexity that cannot be defended during Looloo’s technical review. The missing artifact is not project code. It is a build brief that selects exactly one portfolio project and settles the decisions required to implement it honestly.

## Solution

Produce one source-backed build brief for one candidate-owned Finance + ML portfolio project. Research and compare three to five feasible directions, audit Vibe-Trading as a possible reference or component, score every direction with the existing 100-point Looloo project-evidence rubric, and select the strongest direction rather than returning an undecided menu.

The build brief will define the selected project’s financial problem, ML contract, data and information-timing contract, baseline and model boundary, leakage-safe evaluation, backtesting assumptions, performance-diagnosis evidence, paper-trading demo, production boundary, implementation sequence, learning prerequisites, recruiter-readable narrative, and technical-interview proof. It will remain a planning artifact: it will not implement, train, deploy, or trade.

The deliverable will be one Markdown artifact with its comparison matrix, recommendation, source links, and implementation handoff in the same place. Existing research assets will be linked rather than copied.

## User Stories

1. As the applicant, I want one recommended portfolio project, so that I can commit to building instead of choosing among vague ideas.
2. As the applicant, I want the recommendation tied directly to the target role, so that the work addresses Looloo’s actual hiring signals rather than generic portfolio advice.
3. As the applicant, I want the recommendation to account for my non-technical degree, so that it emphasizes observable capability without pretending to replace a credential.
4. As the applicant, I want the recommendation calibrated to my classical-ML project baseline, so that I can complete and defend it independently.
5. As the applicant, I want several credible directions compared before one is selected, so that the recommendation is not anchored on the first fashionable idea.
6. As the applicant, I want a clear Vibe-Trading verdict, so that I know whether to reject it, study it, reuse a bounded component, or build on it.
7. As the applicant, I want reused work separated from candidate-owned work, so that I can describe my contribution honestly.
8. As the applicant, I want the project’s exact finance problem stated, so that the ML work has a real decision context.
9. As the applicant, I want the prediction or ranking target fixed, so that labels, metrics, and validation are coherent.
10. As the applicant, I want the asset universe and decision horizon fixed, so that the project does not expand indefinitely.
11. As the applicant, I want explicit project non-goals, so that attractive but irrelevant features do not delay completion.
12. As the applicant, I want accessible data sources and reuse terms identified, so that implementation is not blocked by unavailable or impermissible data.
13. As the applicant, I want information-availability timing documented, so that I do not accidentally train on future information.
14. As the applicant, I want a simple baseline before advanced models, so that model value is measured rather than assumed.
15. As the applicant, I want only justified model complexity, so that I can explain every component during a technical review.
16. As the applicant, I want TensorFlow or PyTorch used only when the selected problem warrants it, so that framework familiarity does not become decorative boilerplate.
17. As the applicant, I want a leakage-safe temporal validation design, so that reported performance is credible.
18. As the applicant, I want transaction costs and slippage included wherever P&L is reported, so that the project does not overstate trading results.
19. As the applicant, I want honest success criteria that do not require profitability, so that negative or weak market results can still demonstrate strong ML engineering.
20. As the applicant, I want required robustness and sensitivity checks listed, so that I know how to challenge the model rather than showcase one favorable run.
21. As the applicant, I want at least one planned failure-diagnosis narrative, so that I can demonstrate analytical debugging instead of reporting only final metrics.
22. As the applicant, I want a defined paper-trading demo, so that I can show repeatable model operation without using real capital.
23. As the applicant, I want the production boundary fixed, so that I build enough engineering evidence without turning the project into an infrastructure exercise.
24. As the applicant, I want an ordered implementation sequence, so that each phase produces evidence and unblocks the next phase.
25. As the applicant, I want learning prerequisites attached to the phases that need them, so that study directly supports implementation rather than becoming an open-ended curriculum.
26. As the applicant, I want acceptance evidence for every implementation phase, so that “done” means observable behavior rather than code volume.
27. As the applicant, I want a recruiter-readable project summary, so that a non-specialist can understand the problem, ownership, and result quickly.
28. As the applicant, I want technical-interview talking points tied to actual decisions, so that I can defend the project beyond its README.
29. As the applicant, I want explicit limitations and rejected alternatives, so that the project demonstrates judgment and introspection.
30. As the applicant, I want the build brief to identify which reported numbers I must reproduce live, so that I do not publish claims I cannot derive or explain.
31. As an ML hiring manager, I want the project to formulate a real-world decision as an ML problem, so that I can assess problem-solving rather than library usage.
32. As an ML hiring manager, I want a reproducible data build and documented schema, so that I can inspect data ownership and quality controls.
33. As an ML hiring manager, I want point-in-time and survivorship risks addressed, so that I can trust the evaluation setup.
34. As an ML hiring manager, I want baseline and model comparisons with rationale, so that I can assess theoretical and applied ML understanding.
35. As an ML hiring manager, I want tracked experiments and negative results, so that I can see scientific reasoning rather than cherry-picking.
36. As an ML hiring manager, I want uncertainty and regime sensitivity discussed, so that I can assess whether the candidate understands noisy financial data.
37. As an ML hiring manager, I want a real performance problem diagnosed and verified, so that I can inspect analytical depth.
38. As an ML hiring manager, I want packaged and tested software boundaries, so that productionization claims are inspectable.
39. As an ML hiring manager, I want a repeatable paper-trading loop with logs, so that I can distinguish production evidence from a notebook backtest.
40. As an ML hiring manager, I want candidate-authored decisions and code distinguished from dependencies, so that ownership is clear.
41. As an ML hiring manager, I want the simplest adequate model preferred, so that unnecessary sophistication does not hide weak fundamentals.
42. As an ML hiring manager, I want finance knowledge demonstrated through correct assumptions and metrics, so that domain vocabulary is backed by behavior.
43. As an ML hiring manager, I want limitations and failure conditions stated, so that I can evaluate judgment and honesty.
44. As a recruiter, I want a concise explanation of why the project matches the target role, so that I can recognize relevance without reading the implementation.
45. As a recruiter, I want the applicant’s ownership summarized clearly, so that an adapted repository is not mistaken for original work.
46. As a recruiter, I want profitability claims avoided, so that the portfolio reads as credible engineering rather than investment promotion.
47. As a technical interviewer, I want every major decision linked to evidence, so that I can probe the candidate’s reasoning.
48. As a technical interviewer, I want the candidate to explain the baseline, loss, validation, and failure modes, so that theoretical understanding is testable.
49. As a technical interviewer, I want one end-to-end debugging story, so that model-performance investigation is concrete.
50. As a technical interviewer, I want tradeoffs and rejected alternatives recorded, so that follow-up questions can go deeper than the final architecture.
51. As the implementing agent, I want one fixed project scope and set of non-goals, so that implementation does not require new product decisions.
52. As the implementing agent, I want a complete prediction and data contract, so that data and modeling code can be built without guessing semantics.
53. As the implementing agent, I want evaluation assumptions and success criteria fixed, so that tests and experiments have an external contract.
54. As the implementing agent, I want a defined reviewer journey through the artifacts, so that the repository presents evidence in a deliberate order.
55. As the implementing agent, I want the minimum production features identified, so that I do not add infrastructure that contributes no hiring evidence.
56. As the implementing agent, I want dependency-ordered milestones with stop conditions, so that the smallest complete version ships before optional depth.
57. As a future maintainer, I want primary sources distinguished from inference, so that assumptions can be revisited when evidence changes.
58. As a future maintainer, I want source and license obligations recorded, so that reused data and code remain lawful and attributable.
59. As a future maintainer, I want one canonical build brief, so that decisions do not drift across duplicate documents.
60. As a future maintainer, I want unresolved implementation details called out explicitly, so that hidden uncertainty is not mistaken for a decision.

## Implementation Decisions

- The output is a planning deliverable, not software: one canonical Markdown build brief containing the comparison, recommendation, contracts, implementation sequence, and source links.
- No new application, dashboard, database, agent framework, or deployment is created while producing the build brief.
- Existing domain language is normative: target role, hiring evidence, portfolio project, reference repository, paper-trading demo, and build brief retain their glossary meanings.
- The role is Looloo’s Machine Learning Engineer (Project Algorithmic Trading), tagged Junior Level. The title itself does not contain the word “Junior.”
- Candidate directions are scored against the existing 100-point rubric: Problem Formulation & Literature-Grounded Research 12; Data Corpus Engineering 14; Modeling Depth & ML Foundations 18; Experimentation Rigor & Reporting 14; Performance Diagnosis 10; Productionization & Engineering Fluency 16; Market/Domain Fluency 8; Ownership, Judgment & Culture-Fit 8.
- The related-degree and professional-experience preferences remain outside the 100-point score. The build brief may reduce uncertainty about capability but must not claim to replace either credential.
- The research compares three to five project directions. At least one must be non-agentic. An agentic direction is included only if it contains candidate-owned ML training, data, evaluation, and production evidence rather than primarily LLM orchestration.
- Each candidate direction is assessed for achievable rubric evidence, finance relevance, accessible and legally reusable data, point-in-time feasibility, leakage and backtest risk, engineering depth, originality, completion risk, and interview defensibility.
- The final deliverable selects exactly one direction. It may mention the runner-up and decisive tradeoff, but it must not return an unresolved menu.
- If candidates are close, tie-breaking priority is: stronger ML-hiring evidence; clearer candidate ownership; safer data and evaluation; lower completion risk. A non-agentic design wins when an agent layer adds no independent hiring evidence.
- Vibe-Trading receives an explicit verdict: reject, reference only, bounded component, or foundation. The verdict must examine architecture, actual model training, data, evaluation/backtesting, leakage and cost assumptions, reproducibility, maintenance, deployment, license, and remaining candidate-owned work.
- Packt’s Machine Learning for Algorithmic Trading repository remains a learning and knowledge source. Its notebooks or chapter implementations are not proposed as the portfolio project.
- Current-practitioner and public-X signals may be used for idea discovery only. Technical claims require repository source, official documentation, papers, official data documentation, or other primary evidence.
- Every material claim is marked or written so readers can distinguish source fact, applicant constraint, and inference. Unknown Looloo internals remain unknown.
- The selected project is historical research plus a paper-trading demo. Live capital, brokerage execution, and investment advice are prohibited.
- The selected project contract fixes the financial decision, asset universe, horizon, target, labels, data inputs, information-availability timing, benchmark, non-goals, and reason ML is appropriate.
- The data plan uses authoritative, accessible sources and records provenance, update cadence, schema, licensing/reuse constraints, point-in-time semantics, and relevant data-quality checks. A versioned static source is acceptable when it is the authoritative input; an API is not required for appearance.
- The model plan starts with a simple baseline and compares at least one appropriate ML alternative. Custom architecture is not required. Complexity is added only when a measured limitation justifies it.
- TensorFlow or PyTorch is recommended only when appropriate to the selected problem. If a simpler framework is more suitable, the build brief states that decision and how framework familiarity will be demonstrated or learned separately.
- The evaluation plan uses a leakage-safe temporal design appropriate to the target, such as rolling/walk-forward or purged/embargoed validation. It does not mandate one split method before the target and data are known.
- Any P&L evaluation includes transaction-cost and slippage assumptions, calendar/session handling, position/risk constraints, and clearly defined risk/performance metrics.
- Success is defined as trustworthy, reproducible evidence and demonstrated reasoning. Positive returns are neither required nor promised.
- The experiment plan includes a baseline ladder, tracked configurations, uncertainty, negative results, ablations or sensitivity checks, robustness across relevant periods/regimes, and explicit checks for leakage, survivorship, overfitting, and implementation errors.
- The performance-diagnosis plan requires one real failure investigation with symptom, hypotheses, root cause, fix, and before/after verification.
- The proposed implementation remains the smallest complete end-to-end artifact: reproducible data build, model experiments, report/model documentation, packaged and tested code, and a repeatable paper-trading loop with useful logs.
- A dashboard or API is included only if it materially improves the reviewer journey or demonstrates a role requirement not already visible through simpler artifacts.
- The build sequence is dependency ordered: problem and evidence contract; data build; baselines and experiments; diagnosis and robustness; packaging; paper-trading run; final report and portfolio presentation.
- Each sequence step names observable completion evidence and the next decision it unlocks. Optional enhancements appear only after the minimum credible package is complete.
- The final build brief contains a recruiter-readable summary and a separate technical-interview section, but both remain within the same canonical artifact.
- The recommendation states exactly what the applicant can claim, what came from reference repositories, what failed, and what remains limited.
- The build brief must be implementable without a further choice of project, target, data source, validation family, paper-trading boundary, or evidence standard.

## Testing Decisions

- Use one highest-level acceptance seam: review the final build brief as a whole and determine whether an implementing agent can begin without inventing product or methodological decisions. No lower-level document “unit tests” are needed.
- Good acceptance checks observe the deliverable’s behavior for its readers: whether it selects, explains, constrains, and hands off a project. They do not test exact wording, heading order, or incidental formatting.
- The comparison must contain three to five viable directions, all scored across the same eight criteria, with weights totaling 100 and evidence supporting each score.
- The selected project must clear every item in the existing minimum credible evidence package; a high aggregate score cannot compensate for a missing data, evaluation, diagnosis, or production floor.
- The final recommendation must name exactly one project and one Vibe-Trading verdict.
- The prediction and data contract is accepted only when the financial decision, universe, horizon, target, labels, inputs, availability timing, benchmark, and non-goals are all explicit and mutually coherent.
- The evaluation contract is accepted only when it specifies a target-appropriate temporal validation family, baselines, costs, metrics, uncertainty, robustness, failure checks, and non-profitability-based success criteria.
- The ownership contract is accepted only when candidate-authored work, dependency work, reference-repository work, and reused data are distinguishable.
- The production contract is accepted only when the reviewer journey and minimum paper-trading behavior are clear without requiring an unnecessary dashboard, API, or agent layer.
- The implementation sequence is accepted only when every phase has observable evidence, dependency order, and a stop condition.
- The recruiter narrative is accepted only when a non-specialist can identify the problem, candidate ownership, role relevance, and honest result without a profitability claim.
- The interview section is accepted only when it prepares the applicant to explain model choice, data timing, validation, one failure diagnosis, production tradeoffs, and limitations from first principles.
- Source validation checks that first-party or primary evidence supports technical and company claims; discovery-only X or community sources cannot stand alone.
- Automated checks may verify arithmetic, required-field presence, and link resolution. Semantic correctness, source quality, methodological coherence, and originality require human or agent review at the final seam.
- Prior art is the existing Looloo project-evidence rubric and the resolved role-evidence research. They are the acceptance oracle; the new build brief links them instead of copying them.
- No model, backtest, paper-trading loop, deployment, or software test suite is executed under this spec because project implementation is out of scope.

## Out of Scope

- Implementing the selected portfolio project.
- Training models, downloading the full dataset, running experiments, or producing backtest results.
- Building or deploying the paper-trading demo.
- Live trading, brokerage integration, real-money execution, investment advice, or profitability guarantees.
- Reverse-engineering Looloo’s internal trading team, strategy, models, data, or infrastructure.
- Claiming that a portfolio project substitutes for a related degree or professional tenure.
- Writing a complete resume, cover letter, application campaign, or general career-transition curriculum.
- Preparing answers for every possible Looloo programming or ML assessment question.
- Copying or lightly reskinning Vibe-Trading, the Packt repository, or another tutorial as candidate-owned work.
- An exhaustive survey of every finance-ML project idea or every trading-agent framework.
- Adding an agent, deep-learning model, dashboard, API, cloud deployment, or MLOps platform solely to increase apparent sophistication.
- Selecting proprietary or legally ambiguous data that the applicant cannot redistribute or explain.

## Further Notes

- As of 2026-07-12, Looloo’s first-party role page is live and tags the position Junior Level with 1–3 Years metadata. The preferred-competency prose on the same page separately says at least 1–2 years creating AI models; the build brief must preserve rather than smooth over that discrepancy.
- Looloo’s first-party application-process page describes a 90-minute programming assessment followed by deeper live-proctored programming/ML review with senior-programmer feedback. It also lists portfolio and transcript as optional and encourages applicants without related work experience to apply.
- Looloo’s public About page presents a general AI/data consultancy with predictive-analytics work. No public evidence establishes the internal structure or technology of the algorithmic-trading project.
- The existing wayfinding map remains the provenance for the destination and constraints. The resolved role-evidence research and 100-point rubric are authoritative inputs to this spec.
- The applicant has not stated whether they satisfy the listing’s professional-experience range. Do not infer either answer.
- There is no fixed time or resource ceiling, but completion risk remains part of project selection. Prefer the smallest project that produces the complete hiring-evidence package.
