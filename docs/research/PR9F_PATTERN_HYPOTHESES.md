# PR9F revised scientific protocol — initial stops and trading patterns

Status: protocol and attribution register for the revised study. The subsequently supplied 118-row log reconciles to 42 initial episodes; the scientific findings and validation are recorded in the final report.

Authoritative task: the user-supplied **PR9F — Initial Stop Inference from Grimes' Trading Patterns** brief, received November 3, 2026. Work continues on `research/grimes-initial-structural-stops-v1`. The interrupted draft is preserved at commit `8566b72`; its 34- and provisional 37-episode artifacts remain unchanged. The original PR9E cohort is a historical comparison, not a filter on the revised population.

## Scientific question and causal ordering

Which observed trading patterns make a particular structural invalidation level relevant, and why might the first published protective stop leave room beyond that level?

**Pattern and context → structurally meaningful entry → protective stop → entry-to-stop risk normalization → decision filter.** The entry remains latent where it is not observed; this study does not build an entry predictor. A structural boundary and a protective stop are separate observations/hypotheses. Positive distance beyond a boundary is compatible with protective room, but does not identify the reason for that room. Volatility expansion, a larger structural scale, rounding, a different entry plan and price-basis uncertainty can remain competing explanations. No optimum buffer or ATR multiplier will be estimated.

## Theory and attribution

The following primary sources were read on November 3, 2026:

- [Grimes, Fundamental Trading Patterns](https://www.adamhgrimes.com/fundamental-trading-patterns/): a simple pullback is a countertrend correction; a complex pullback includes a failed resumption and further countertrend legs. A failure test probes an earlier level and reverses. An Anti is the first pullback after a potential trend change; a breakout crosses previously defined support/resistance.
- [Grimes, Patterns within patterns](https://www.adamhgrimes.com/patterns-within-patterns/), March 16, 2016: a nested pullback is a small pause during an active larger pattern. His example combines a daily pause with a larger weekly structure. He cautions against overly tight stops and notes the difficulty of quantifying this discretionary pattern.
- [Grimes, How to trade Complex Consolidations](https://www.adamhgrimes.com/trade-complex-consolidations/), November 6, 2014: a second corrective leg follows a failed trend-resumption attempt. He warns that apparent pattern structure depends on timeframe and can be hidden within a few bars.

These teachings motivate hypotheses; they do not establish the private rationale behind any captured alert. MarketLife TYPE labels are separately attributed source observations. In particular, Tight pullback will not be silently recoded as Complex pullback, and Nested pullback is not another name for Complex pullback.

The user subsequently supplied Chapter 3 and Chapter 10/Figure 10.9 text, preserved in [book-excerpts.txt](../evidence/pr9f-expanded-source-20261103-v1/book-excerpts.txt). The nested-pullback excerpt distinguishes the small pause from its larger driving pattern and discusses deeper protective room for anticipated volatility expansion. It also distinguishes decisive pattern violation from mandatory holding to a protective stop. The complex-pullback excerpt describes the failed resumption and second countertrend leg. These are user-provided excerpts attributed to the book, not independently authenticated edition/page scans; the figure images themselves were not supplied.

## Source reconciliation before population statistics

The user subsequently supplied all 118 visible rows spanning October 20–November 2, preserved in [the dated log](../evidence/pr9f-expanded-source-20261103-v1/change-log-20261102.txt). Its 36 NEW SETUP rows overlap 28 PR9E openings and add eight episodes: five October 30 openings and three November 2 openings. Together with the preserved 34, the captured population is 42 episodes (22 LONG, 20 SHORT). This reconciles the provided evidence; it does not certify complete external MarketLife history.

For each source row, retain the literal event description, source identifier, reported log date, publication evidence/precision, intended trading session where explicitly supplied, direction, TYPE evidence and attached stop/reference. Keep the following distinctions:

| Source event | Population treatment |
| --- | --- |
| NEW SETUP | Establish an initial-stop observation; deduplicate overlapping reports using identity, chronology and corroborating evidence. |
| TRIGGERED | Record a reported entry-condition event; do not create another opening or substitute its stop for the initial stop. |
| STOP MOVED | Preserve a later source fact; do not infer an initial stop from its previous-stop field. |
| STOPPED OUT | Record a source-tracked termination; no subscriber brokerage execution or fill mechanics are established. |
| DROPPED / TAKEN OFF | Record removal of a source episode; do not infer that a market stop caused removal. |

A new SLB opening after its reported termination receives a distinct episode ID. The earlier SLB 51.10 initial stop remains separate from the new 51.90 initial stop. The three November 3 summary openings are reconciled with November 2 log rows, not counted twice. Preserve both date labels; distinguish the intended Tuesday session from the log's Monday date. The user reports the latest snapshot/batch was published at 5 p.m. November 2. Retain that hour-precision assertion in the session's New York timezone; do not assign it to every historical row. Earlier log dates are not exact publication timestamps. The original 34 conditional cutoffs remain unchanged.

Unmatched non-opening actions remain visible as unmatched source evidence. They do not expand the initial-stop population or justify a subscriber-history acquisition project. TYPE labels observed only later remain later observations, with historical applicability UNKNOWN.

## Pattern-conditioned candidate protocol

All candidate construction receives admitted pre-decision prices and direction, never the published stop. The strict PR9E pivots, existing market-data admission, pinned shared ATR14 and the draft's contracting-range detector are reusable baselines. Any new scale or segmentation convention is a declared repository hypothesis, not a recovered Grimes rule or a parameter selected by residual fit.

| Hypothesis | Price-only evidence and candidate boundary | Important competing explanation / discriminating observation |
| --- | --- | --- |
| H1 Swing invalidation | Retain strict three-left/three-right confirmed pivots. Separately document local/provisional structures at other scales, with confirmation dates. | A broad pivot may be irrelevant to a local setup. A later pivot confirmation cannot explain an earlier stop. Compare cases where local and broad levels differ. |
| H2 Simple pullback invalidation | Identify the relevant driving leg and subsequent countertrend correction; retain its opposing extreme. A provisional extreme is not a confirmed pivot. | The largest extreme in a fixed window may select the wrong correction. Compare a local correction with the existing 20-bar baseline without choosing by stop proximity. |
| H3 Complex pullback invalidation | Require an ordered correction, failed resumption and another corrective leg. Retain first-leg and full-correction extremes separately. | A small pause within a continuing drive is not sufficient evidence of this sequence. A stop protecting the first leg may differ from one protecting the full correction. |
| H4 Breakout/failure structure | Distinguish the signal candle, preceding base, breakout threshold and a failed-test extreme. All tested levels must pre-exist the test. | Breach and reclaim can support a different thesis from an untouched boundary. A close back across a level does not establish intraday entry order. |
| H5 Nested pullback / compression | Require evidence of a larger active drive separately from a local pause. Retain local compression boundary, driver/base boundary and larger confirmed structure. | Contracting ranges alone do not identify nesting. Compare positive protective room with larger-pattern protection; future volatility expansion cannot be inserted into the initial information set. |
| H6 Volatility-derived alternative | Preserve the possibility of an independently specified volatility stop. ATR14 normalizes measured distances. | Unknown entry/anchor/multiplier leaves this unidentified. Fitting a multiplier to the observed stop is not a discriminating test. |

The draft contraction baseline uses maximal sequences of at least three strictly decreasing daily High–Low ranges, ending in the last 20 of up to 60 available bars. It retains all intervals and selects the most recent as primary. Shared price overlap, prior-range comparison, age and subsequent **pre-decision** tests are diagnostics, not optimized admission thresholds. A fixed ten-bar box remains a descriptive baseline, not proof of consolidation. These conventions may miss visually meaningful patterns; failures will be retained.

## Explanation quality and protective room

Each candidate must keep separate axes: observed pattern evidence; structural boundary; relevance to the proposed thesis; signed stop-to-boundary distance; ATR14-normalized distance; prior tests/reclaims; larger-pattern context; alternatives; latent assumptions; and a discriminating observation. There is no single “closest candidate wins” score.

Outward distance is `boundary − stop` for LONG and `stop − boundary` for SHORT. A positive distance describes room beyond a level, not proof that the amount was justified by anticipated volatility. A boundary already tested before publication contradicts an **untouched-boundary** subhypothesis, but does not by itself exclude a reclaim thesis or a deeper protective stop. Those alternatives require explicit evidence rather than being silently accepted or rejected.

Entry references, current stops, first published stops, tracked stop-outs and actual subscriber executions remain separate. LAST is never an entry substitute. A later AE/AHE reference may support explicitly retrospective reference-to-initial-stop arithmetic, but does not become information available at the original decision. Actual subscriber risk remains UNKNOWN without independent documentation.

After reconciling the supplied log, freeze new versioned source/episode records and stop-masked candidate annotations. Compare published stops only afterward, retain the original cohort separately, and select detailed cases from the completed inventory. Generate new immutable output versions; do not overwrite the interrupted draft or revise PR9E's findings. The final report will distinguish explanatory correspondence from retrospective hypothesis selection and predictive accuracy.
