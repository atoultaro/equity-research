# Reverse-Engineering Adam Grimes' Trading Decisions: Research Charter and Roadmap

Living charter, established October 30, 2026. **Next priority: structural-stop case studies using existing evidence.** Update this document when evidence changes our understanding, rather than whenever engineering work finishes. Historical PR names below identify evidence, not future milestone numbers.

Five-minute route: A–D for the question and semantics, H for priorities, and J for findings and interpretation corrections. F/G supply the theoretical references and competing hypotheses.

## A. Mission

Infer the latent trading decision rules behind Adam Grimes' published MarketLife alerts from partial observations, financial time series and his educational writing. Explain why a stock is ADDED, which structures justify its initial stop, why stops change, why entry remains attractive or becomes UNDERWAY, when eligibility returns, and why a setup is DROPPED. Relate these decisions to trend, volatility, market regime and anticipated price behavior.

This is scientific reverse-engineering of a partially observed policy. It does not reconstruct a personal brokerage account or establish a production trading system. Explaining published decisions and demonstrating an independent trading edge are separate achievements.

## B. Governing causal model

**Price structure → Structural invalidation → Stop placement → Risk assessment → Decision**

1. Identify market context and the candidate setup.
2. Identify pre-existing structural levels whose violation could invalidate that setup.
3. Choose a stop consistent with that structure, potentially with a buffer.
4. Evaluate a causally defined candidate entry, its stop distance and available completed ATR14.
5. Assess remaining opportunity quality, including plausible reward relative to risk.
6. Publish ADDED, retain ENTERABLE, mark UNDERWAY, revise the stop or DROP the setup.

This ordering is our working causal hypothesis, not a verified deterministic account of Grimes' private process. Competing explanations, including volatility-based construction, can challenge it. ATR14 normalizes volatility and risk; it does not dictate a stop one ATR from entry. Exact stop-price prediction is secondary to explaining structural rationale. Rejecting a universal multiplier as an assumption does not exclude individual stops at that distance.

## C. Observable and latent variables

| Observed evidence | Latent variables we seek to infer |
| --- | --- |
| Captured OHLCV and technical structure derived under declared availability assumptions | Grimes' perception of the setup and its quality |
| Published initial/revised stops | Chosen structural invalidation level and buffer |
| ADDED, STOP_CHANGED, ENTERABLE/UNDERWAY and DROPPED states/actions | Preferred entry timing and setup-specific risk tolerance |
| Source ordering and available publication-time evidence | Anticipated price movement/reward and discretionary judgment |

The inference problem is **P(latent decision rationale \| observed market structure, published stops, source decisions)**. This expresses the question, not an already calibrated probability model. Several latent explanations can generate the same alert. Unknown publication times, source gaps and later vendor revisions limit identification.

A candidate Close/Open reference is not an observed fill. Expected reward is latent; a favorable move observed afterward cannot be inserted into the expert's earlier information set. Even retained historical prices do not prove identical vendor vintages were available at the original decision time.

## D. MarketLife setup semantics

The user attributes the UNDERWAY guidance to **Tom at MarketLife**: setups become UNDERWAY when they have moved too far for attractive fresh entry. This is user-supplied attribution, not independently verified publisher documentation. The statement is retained in the [setup/opportunity model](../MARKETLIFE_SETUP_AND_OPPORTUNITY_MODEL.md). Entry/re-entry using the latest stop is an additional user-reported interpretation.

| Source state/action | Research interpretation |
| --- | --- |
| ADDED | Begins a monitored setup and initial entry opportunity; does not establish a fill |
| ENTERABLE | Remains suitable for fresh entry |
| Stop revision while ENTERABLE | Defines an updated opportunity version using the newly published stop |
| UNDERWAY | Too extended for attractive fresh entry; proves neither entry, continued investment nor profit |
| Explicit UNDERWAY → ENTERABLE | Reopens eligibility and creates an opportunity using the then-current stop |
| DROPPED | Removes the setup from the active list; does not prove executed liquidation |

Keep **setup lifecycle**, **entry-opportunity versions** and **hypothetical subscriber executions** separate. An UNDERWAY-only stop revision does not restore eligibility. Co-published stop/UNDERWAY actions are one assessment, not an invented intermediate entry window. A later version never retroactively changes an older hypothetical execution's stop. A subscriber may enter, stop out, re-enter, hold or never trade; those executions remain unobserved.

## E. Scientific reasoning principles

**Observation → Competing explanations → Discriminating evidence → Counterexamples → Revised understanding**

Use abductive inference: seek explanations that account for observations with explicit assumptions, then actively look for evidence that separates or contradicts them. For every hypothesis record:

| Required field | Question |
| --- | --- |
| Statement | What decision mechanism is proposed? |
| Supporting / contradictory evidence | Which dated source events and price structures support or challenge it? |
| Latent variables / assumptions | What entry, timing, structure or information is unobserved? |
| Alternatives | What else explains the same observation? |
| Discriminating test | Which observation would change the ranking or falsify the explanation? |
| Confidence / uncertainty | How strong is support, and what remains unidentified? |

Do not reward a rule merely for reproducing examples used to invent it. Preserve failures, distinguish compatibility from identification and declare retrospective hypothesis selection. Repeated alerts about one setup and different setups in a shared alert cluster are dependent. Conditional publication clocks are sensitivity cases, not additional observations. Compare LONG/SHORT separately and use controls; do not manufacture statistical independence or calibrated confidence.

## F. Grimes' published work: reading and citation register

The following original articles were accessible and their displayed titles and quoted passages checked on **October 30, 2026**. Links use the verified canonical `www` URLs. These are dated educational teachings, not proof of the policy behind the 2026 alerts. Quotations are deliberately brief.

**S1. [Trailing stops: 9 ideas you can use today](https://www.adamhgrimes.com/trailing-stops-9-ideas-you-can-use-today/)** — September 25, 2018. Grimes refers to “previous pivot highs and lows.” He discusses structural pivots, different buffer locations, recent-bar extremes and other trailing approaches. **Motivates H2/H3:** compare competing structural anchors and buffers. **Does not establish:** one mandatory trailing method, a universal lookback/buffer, or which alert revised an existing execution.

**S2. [Chart of the Day: Moving Stops with Confirmation](https://www.adamhgrimes.com/chart-of-the-day-moving-stops-with-confirmation/)** — December 12, 2012. He describes “a sharp upside breakout.” In that USDJPY example, consolidation discouraged premature tightening; the breakout justified closer protection. His use of stop can denote an exit-decision level without specifying a resting order. **Motivates H3:** test revisions against newly confirmed structure and expected follow-through. **Does not establish:** MarketLife's order type, a closing-price convention, or identical treatment of every setup.

**S3. [Patterns within patterns](https://www.adamhgrimes.com/patterns-within-patterns/)** — March 16, 2016. He discusses a “nested pullback”: a small pause within a larger active move. Context and subsequent confirmation/contradiction matter; tight entries involve tradeoffs, and discretionary recognition is difficult to quantify. **Motivates H1/H5:** examine nested structures and renewed opportunities. **Does not establish:** that our cases are nested pullbacks, a universal detector, or entries in the MarketLife ledger.

**S4. [Exits: know when to hold 'em, know when to fold 'em](https://www.adamhgrimes.com/trade-exits/)** — March 29, 2016. His personal initial stops are described around “3-4 ATRs”; he also discusses time-based risk reduction, style-dependent targets and combining partial profit-taking with trailing. **Motivates H2/H3/H6:** compare structural invalidation and management explanations as parts of a coherent plan. **Does not establish:** a universal 3–4 ATR rule, a mandatory full exit at +1R, actual entries/sizing, or the convention behind any 2026 alert.

**S5. [Small Stops, Big Risks?](https://www.adamhgrimes.com/small-stops-big-risks/)** — October 17, 2011. His distinction is “not necessarily a very tight stop.” He argues that nominal stop distance alone misses the likelihood of being stopped and the resulting repeated-outcome implications. **Motivates H2/H4:** compare risk geometry with setup quality and plausible price behavior. **Does not establish:** the best distance, a known success probability, or evidence of profitable expectancy in our sample.

**S6. [My Approach to Markets and Trading](https://www.adamhgrimes.com/my-approach-to-markets-and-trading/)** — October 4, 2011. “Markets evolve.” Grimes emphasizes pervasive randomness, rare context-dependent patterns, small possible edges and transaction costs. **Motivates H1/H6 and later independent edge testing:** compare context/regimes and counterexamples. **Does not establish:** an edge for our inferred rules, stable parameters across cycles, or endorsement of our causal model.

Keep four attribution layers distinct: **Grimes' published teachings; user-supplied MarketLife statements; user interpretations; repository research hypotheses**. Citation motivates a hypothesis; it does not make Grimes its author or confirm it.

## G. Primary research hypotheses

| Family | Competing explanations and discriminating evidence |
| --- | --- |
| **H1: Setup identification** | Pullbacks, breakouts, anti/reversal patterns, failed breakouts/breakdowns, continuation and second-leg setups, conditional on trend/regime. Compare pre-ADDED structure across families and observed controls; do not assume one structure or unobserved screening membership. |
| **H2: Structural stop placement** | Swing highs/lows, pullback extremes, consolidation boundaries, breakout/signal bars with buffers, versus alternative volatility-based rules. Compare published-stop residuals from levels available at that decision, in price/ticks and completed ATR14 units. ATR normalization is diagnostic, not the assumed construction rule. |
| **H3: Stop revisions** | Newly confirmed swings, breakouts/breakdowns, consolidation changes, fresh entry opportunities or changed thesis invalidation. Compare the old/new structural rationale. Publishing a revised entry opportunity is distinct from modifying an order for a hypothetical existing execution. |
| **H4: ENTERABLE versus UNDERWAY** | Distance from a reasonable entry region, structurally justified stop distance, ATR-normalized risk, recent directional extension, remaining structure quality and plausible reward/risk. Compare same-direction setups remaining ENTERABLE; assume neither universal 1R nor 1ATR. |
| **H5: Return to ENTERABLE** | Pullback, consolidation, a new structural stop, improved entry-to-stop geometry, or a renewed continuation/reversal setup. Use explicit state transitions; an isolated stop update is not a return. |
| **H6: DROPPED decisions** | Structural invalidation, failed expected behavior, declining attractiveness, time decay, regime change or discretionary removal. Compare alternatives and counterexamples; never automatically map a stop touch to DROPPED. |

## H. Research roadmap

| Milestone | Status and scientific output |
| --- | --- |
| **Phase 1 — Evidence interpretation** | **Substantially established** by PR9A–PR9D: source reconstruction, setup/execution separation, independent opportunities, publication uncertainty, market features and exploratory retrospective studies. Source coverage, vintage and identifiability limits remain. No successful operational forecast was achieved. Use the existing infrastructure. |
| **Phase 2 — Structural-stop inference** | **Next priority; proposed.** Select representative LONG/SHORT cases, reconstruct pre-decision structure, enumerate plausible invalidation levels and compare published stops/buffers. Examine revisions and contradictory examples. Start with CLMT, TEVA, GME, EBAY and SAIL; include a well-observed SHORT such as CDE. Deliver annotated case studies and a hypothesis comparison matrix. |
| **Phase 3 — Entry-eligibility inference** | **Proposed extension of initial descriptives.** Compare ENTERABLE/UNDERWAY transitions, structural risk and extension, explicit returns, and same-direction controls. Separate initial historical measurements from any newly performed analysis. |
| **Phase 4 — Setup selection and removal** | **Proposed.** Compare ADDED/DROPPED cases, setup families and market context. Investigate differently treated but observably similar securities and counterexamples. Do not infer a complete candidate population from alert omissions. |
| **Phase 5 — Prospective hypothesis evaluation** | **Not yet demonstrated.** Freeze hypotheses and available inputs before new observations; predict observable decisions, then score subsequent supplied observations. Track target eligibility, coverage, uncertainty and failures. Revise explicitly rather than silently tune. |
| **Phase 6 — Independent trading-edge evaluation** | **Deferred until explanatory maturity.** Define executable rules and realistic entries/exits/costs; evaluate expectancy, risk, drawdown and regime dependence. Imitating decisions and finding a profitable strategy require separate evidence. |

The first Phase 2 packet should annotate candidate structural levels **before** revealing the published stop where practical, retain competing annotations, and mark historical selection honestly. Record available confirmed pivots, invalidation, plausible buffers, entry-reference geometry and a discriminating counterexample. Use existing snapshots and conditional publication scenarios; do not launch another acquisition project. Do not implement that experiment in this documentation change.

## I. Engineering scope discipline

Before engineering, answer five questions: **Which hypothesis? Which missing observable evidence? What smallest implementation? What new explanation or falsification? What is outside scope?** Every Grimes-related PR must state the specific scientific question it advances or preserves.

Missing alerts, unknown timestamps and incomplete historical coverage are limitations, **not universal prerequisites that halt retrospective hypothesis generation**. Work conditionally with observed intervals, mark unknowns and identify which comparisons need additional evidence. Do not invent observations, fills, publication times or unavailable information.

Preserve minor vendor revisions and assess their **materiality to the scientific conclusion**, rather than halt all research. Compare retained/fresh vintages: do they change a structural level, invalidation, ATR/risk interpretation or hypothesis ranking? Small numerical size alone does not prove immateriality near a decision boundary. Retain immutable versions and report sensitivity; do not silently overwrite or waive discrepancies.

This charter changes research priorities, **not code or existing registration policy**. PR9D's formal gate remains failed for six vintage conflicts and unverified source completeness. That restricts operational forecast registration; it does not prohibit annotated structural studies. Prospective work still needs an honest, declared information set and an eligible subsequent target; no backdating or scoring against already-known alerts. Revisit any gate policy separately with evidence, not as an implicit documentation exception.

## J. Research progress and decision log

| Milestone / hypothesis | Evidence and findings | Counterexamples / uncertainty | Next experiment |
| --- | --- | --- | --- |
| Setup semantics / H3–H6 | [Opportunity reassessment](../reports/GRIMES_ENTRY_OPPORTUNITIES.md): 34 captured episodes, 72 versions, 58 nonempty windows | CLMT/TEVA/GME/EBAY continuations contradict the old equation of source setup with one continuous execution; actual fills remain unknown | Compare structural reasons for successive stops |
| Policy forensics / H3,H6 | [PR9B comparison](../reports/GRIMES_CROSS_TRADE_INFERENCE.md) tested conditional hard-stop, closing and deferred explanations | Compatibility was not identification; its personal-position inferences are superseded by corrected setup semantics | Reassess explanations at the source-decision level |
| Extension / H4,H5 | [Initial UNDERWAY study](../reports/GRIMES_UNDERWAY_TRANSITIONS.md): 14 reports; seven daily-measurable under its October 26 cutoff | Only one measured LONG and six SHORT across two clusters; reference prices matter; SAIL explicitly returns ENTERABLE at 20.70 | Structural-risk comparison and return case study; later data is not an already-completed reanalysis |
| Structural predictor / H2,H3 | [Historical exploratory evaluation](../reports/GRIMES_WALK_FORWARD_EVALUATION.md): Model E matched 4/26 offered actual revision directions and 3/26 intervals | Same alerts informed hypotheses; weak results do not justify retuning to fit | Replace numerical imitation with competing structural explanations |
| Market evidence / H2–H5 | [PR9D audit](../reports/MARKETLIFE_CURRENT_DATA_AUDIT.md): 11 qualified instruments, 65 sessions each through October 29; current features available | Six revised October 26 observations; incomplete source/publication evidence; [no operational forecast](../reports/MARKETLIFE_PROSPECTIVE_READINESS.md) | Use existing evidence; assess revision materiality in chosen cases |

Foundational interpretation decisions, retained alongside the unchanged historical artifacts:

| Lesson | Rejected assumption | Continuing interpretation |
| --- | --- | --- |
| PR9B → PR9C | Every source setup corresponds to an executed position | Source lifecycle is observed; executions are latent |
| PR9C | UNDERWAY proves a holding or profit | UNDERWAY concerns fresh-entry attractiveness |
| PR9C | Every revised stop adjusts an existing execution | ENTERABLE revisions can define independent opportunities |
| Charter, informed by S1/S4 | Grimes universally places stops one ATR from entry | Compare structural and volatility alternatives; no universal multiplier is established |
| PR9B → PR9C | A hypothetical stop-out requires MarketLife to DROP | A setup may remain eligible for another subscriber or later entry |
| Charter following PR9D | Complete external subscriber history is necessary before research can proceed | Conditional retrospective inference can proceed; preserve uncertainty and prospective integrity |

These corrections must not silently regress. Keep historical findings readable as dated experiments, identify superseded interpretations, and update this charter when a discriminating observation changes the explanation.
