# CLMT: reported management and decision evidence

Source LONG, final CLOSED, setup ENTERABLE. Initial stop 55.25; latest source stop 53.02.

Source opening alert-1:line-8; source closing alert-4:line-21. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 3. Publication-based range: [3, 3]. Conditional ordered-publication bracket: [3, 3]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-1:line-8 | 2026-10-18T15:21:00-04:00 | 2026-10-16 | None | 55.25 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-2:line-11 | 2026-10-19T18:20:00-04:00 | 2026-10-19 | 55.25 | 53.40 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| STOP_CHANGED / alert-3:line-15 | 2026-10-20T18:26:00-04:00 | 2026-10-20 | 53.40 | 53.02 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| DROPPED / alert-4:line-21 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | 53.02 | 53.02 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-2:line-11 | 55.25 → 53.40 | WIDENING | -3.3484 | -0.8461 | 0.1326 | True | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-3:line-15 | 53.40 → 53.02 | WIDENING | -0.7116 | -0.1752 | 1.2220 | True | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions.

SOURCE_REPORTED_DROPPED: alert-4:line-21. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-19 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-1:line-8 | 0.0097 | 0.0353 | 0.0914 | 2.0236 | -0.0232 | -0.0776 |
| alert-2:line-11 | -0.0282 | -0.0020 | 0.0433 | 2.1864 | -0.0356 | -0.1197 |
| alert-3:line-15 | -0.0190 | 0.0075 | 0.0488 | 2.1686 | -0.0010 | -0.0970 |
| alert-4:line-21 | -0.0735 | -0.0532 | -0.0184 | 2.3421 | -0.0395 | -0.1151 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-1:line-8 | 59.87 | -1.0477 | 51.33 | 3.1726 |
| alert-2:line-11 | 59.16 | -1.6557 | 51.33 | 1.9255 |
| alert-3:line-15 | 59.16 | -1.4341 | 51.33 | 2.1765 |
| alert-4:line-21 | 59.16 | -2.8051 | 51.33 | 0.5380 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
