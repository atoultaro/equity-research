# ASST: reported management and decision evidence

Source SHORT, final CLOSED, setup ENTERABLE. Initial stop 28.45; latest source stop 28.45.

Source opening alert-3:line-10; source closing alert-4:line-22. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 1. Publication-based range: [1, 1]. Conditional ordered-publication bracket: [1, 1]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-3:line-10 | 2026-10-20T18:26:00-04:00 | 2026-10-20 | None | 28.45 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| DROPPED / alert-4:line-22 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | 28.45 | 28.45 | ENTERABLE | UNAVAILABLE | AMBIGUOUS_EXIT_PATH |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| No reported revision | — | — | — | — | — | — | — |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: AMBIGUOUS_EXIT_PATH.

No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions.

SOURCE_REPORTED_DROPPED: alert-4:line-22. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-21 CANDIDATE_ORDER_UNKNOWN.

Conditional target evidence: 2026-10-21 CANDIDATE_ORDER_UNKNOWN.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-3:line-10 | 0.0152 | -0.0383 | 0.0981 | 1.9386 | -0.0728 | UNAVAILABLE |
| alert-4:line-22 | 0.1427 | 0.0894 | 0.2297 | 2.1464 | 0.0535 | UNAVAILABLE |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-3:line-10 | 32.08 | -2.5895 | 22.48 | 2.3626 |
| alert-4:line-22 | 32.08 | -0.6196 | 22.48 | 3.8529 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
