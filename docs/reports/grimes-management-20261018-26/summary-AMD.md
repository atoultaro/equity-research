# AMD: reported management and decision evidence

Source SHORT, final CLOSED, setup UNDERWAY. Initial stop 569.90; latest source stop 519.35.

Source opening alert-4:line-9; source closing alert-6:line-28. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 2. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [1, 2]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-4:line-9 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | None | 569.90 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-5:line-17 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 569.90 | 519.35 | ENTERABLE | 2.9019 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| SETUP_CHANGED / alert-5:line-25 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 569.90 | 519.35 | ENTERABLE | 2.9019 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| DROPPED / alert-6:line-28 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 519.35 | 519.35 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-5:line-17 | 569.90 → 519.35 | TIGHTENING | -8.8700 | 1.7356 | 2.1277 | False | UNVERIFIED_STOP_NATIVE_BASIS |

Underway transition: 1 eligible sessions; progress 2.9019%, 0.5486 initial ATR, 0.3244 original hypothetical R. The transition is reported source evidence, not inferred from movement.

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-22: MFE 3.9208%, MAE 1.3133%, signed progress 2.9019%. Original-R progress 0.3244. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

SOURCE_REPORTED_DROPPED: alert-6:line-28. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-23 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-4:line-9 | -0.0330 | -0.0772 | 0.0215 | 27.6693 | -0.1068 | -0.0683 |
| alert-5:line-17 | -0.0935 | -0.1433 | -0.0622 | 29.1257 | -0.1894 | -0.1381 |
| alert-5:line-25 | -0.0935 | -0.1433 | -0.0622 | 29.1257 | -0.1894 | -0.1381 |
| alert-6:line-28 | -0.0624 | -0.1199 | -0.0470 | 29.2736 | -0.1682 | -0.1222 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-4:line-9 | 658.52 | -3.8237 | 596.07 | -1.5667 |
| alert-5:line-17 | 658.52 | -5.1703 | 596.07 | -3.0262 |
| alert-5:line-25 | 658.52 | -5.1703 | 596.07 | -3.0262 |
| alert-6:line-28 | 658.52 | -4.8416 | 596.07 | -2.7082 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
