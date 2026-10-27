# SNDK: reported management and decision evidence

Source SHORT, final CLOSED, setup UNDERWAY. Initial stop 1458.00; latest source stop 1296.00.

Source opening alert-4:line-11; source closing alert-6:line-29. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 2. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [1, 2]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-4:line-11 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | None | 1458.00 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-5:line-20 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 1458.00 | 1296.00 | ENTERABLE | 4.2763 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| SETUP_CHANGED / alert-5:line-28 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 1458.00 | 1296.00 | ENTERABLE | 4.2763 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| DROPPED / alert-6:line-29 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 1296.00 | 1296.00 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-5:line-20 | 1458.00 → 1296.00 | TIGHTENING | -11.1111 | 1.7161 | 2.0876 | False | UNVERIFIED_STOP_NATIVE_BASIS |

Underway transition: 1 eligible sessions; progress 4.2763%, 0.6248 initial ATR, 0.4002 original hypothetical R. The transition is reported source evidence, not inferred from movement.

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-22: MFE 5.5160%, MAE 2.8650%, signed progress 4.2763%. Original-R progress 0.4002. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

SOURCE_REPORTED_DROPPED: alert-6:line-29. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-23 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-4:line-11 | -0.0411 | -0.1291 | -0.1391 | 90.1586 | -0.2465 | -0.2139 |
| alert-5:line-20 | -0.1009 | -0.1907 | -0.2116 | 94.4014 | -0.2779 | -0.2322 |
| alert-5:line-28 | -0.1009 | -0.1907 | -0.2116 | 94.4014 | -0.2779 | -0.2322 |
| alert-6:line-29 | -0.0951 | -0.1913 | -0.2231 | 95.0343 | -0.2932 | -0.2541 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-4:line-11 | 1801.0 | -4.6893 | 1276.0 | 1.1338 |
| alert-5:line-20 | 1801.0 | -5.7210 | 1276.0 | -0.1596 |
| alert-5:line-28 | 1801.0 | -5.7210 | 1276.0 | -0.1596 |
| alert-6:line-29 | 1801.0 | -5.9239 | 1276.0 | -0.3995 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
