# AAPL: reported management and decision evidence

Source LONG, final CLOSED, setup UNDERWAY. Initial stop 339.00; latest source stop 344.70.

Source opening alert-1:line-7; source closing alert-7:line-21. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 6. Publication-based range: [6, 6]. Conditional ordered-publication bracket: [6, 6]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-1:line-7 | 2026-10-18T15:21:00-04:00 | 2026-10-16 | None | 339.00 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-2:line-10 | 2026-10-19T18:20:00-04:00 | 2026-10-19 | 339.00 | 337.80 | ENTERABLE | 0.6338 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| STOP_CHANGED / alert-3:line-14 | 2026-10-20T18:26:00-04:00 | 2026-10-20 | 337.80 | 336.25 | ENTERABLE | -0.3756 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| STOP_CHANGED / alert-5:line-14 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 336.25 | 343.50 | ENTERABLE | 2.1832 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| SETUP_CHANGED / alert-5:line-23 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 336.25 | 343.50 | ENTERABLE | 2.1832 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| STOP_CHANGED / alert-6:line-18 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 343.50 | 344.70 | UNDERWAY | 2.0394 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| DROPPED / alert-7:line-21 | 2026-10-26T18:11:00-04:00 | 2026-10-26 | 344.70 | 344.70 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-2:line-10 | 339.00 → 337.80 | WIDENING | -0.3540 | -0.1870 | 0.6139 | True | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-3:line-14 | 337.80 → 336.25 | WIDENING | -0.4589 | -0.2580 | 0.2830 | True | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-5:line-14 | 336.25 → 343.50 | TIGHTENING | 2.1561 | 1.1916 | 1.9674 | False | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-6:line-18 | 343.50 → 344.70 | TIGHTENING | 0.3493 | 0.1940 | 0.6838 | False | UNVERIFIED_STOP_NATIVE_BASIS |

Underway transition: 4 eligible sessions; progress 2.1832%, 1.1121 initial ATR, 4.1798 original hypothetical R. The transition is reported source evidence, not inferred from movement.

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-23: MFE 3.2132%, MAE 0.6104%, signed progress 2.0394%. Original-R progress 3.9045. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

SOURCE_REPORTED_DROPPED: alert-7:line-21. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-26 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: 2026-10-19 HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN.

Earlier nonprogress-window flags: True; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-1:line-7 | 0.0129 | 0.0179 | 0.0545 | 6.6900 | 0.0197 | 0.0559 |
| alert-2:line-10 | 0.0084 | 0.0158 | 0.0510 | 6.4179 | 0.0209 | 0.0600 |
| alert-3:line-14 | -0.0035 | 0.0056 | 0.0385 | 6.0079 | 0.0049 | 0.0576 |
| alert-5:line-14 | 0.0176 | 0.0285 | 0.0597 | 6.0843 | 0.0410 | 0.1069 |
| alert-5:line-23 | 0.0176 | 0.0285 | 0.0597 | 6.0843 | 0.0410 | 0.1069 |
| alert-6:line-18 | 0.0129 | 0.0260 | 0.0554 | 6.1857 | 0.0348 | 0.0921 |
| alert-7:line-21 | 0.0009 | 0.0139 | 0.0414 | 6.3957 | 0.0166 | 0.0611 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-1:line-7 | 348.15 | -0.7010 | 325.81 | 2.6383 |
| alert-2:line-10 | 348.15 | -0.8118 | 325.81 | 2.6691 |
| alert-3:line-14 | 348.15 | -1.4398 | 325.81 | 2.2787 |
| alert-5:line-14 | 348.15 | 0.0115 | 325.81 | 3.6833 |
| alert-5:line-23 | 348.15 | 0.0115 | 325.81 | 3.6833 |
| alert-6:line-18 | 348.15 | -0.0679 | 338.7 | 1.4598 |
| alert-7:line-21 | 348.15 | -0.6629 | 338.7 | 0.8146 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
