# AAOI: reported management and decision evidence

Source SHORT, final CLOSED, setup UNDERWAY. Initial stop 89.82; latest source stop 70.70.

Source opening alert-4:line-8; source closing alert-6:line-27. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 2. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [1, 2]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-4:line-8 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | None | 89.82 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-5:line-16 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 89.82 | 70.70 | ENTERABLE | 5.8897 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| SETUP_CHANGED / alert-5:line-24 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 89.82 | 70.70 | ENTERABLE | 5.8897 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| DROPPED / alert-6:line-27 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 70.70 | 70.70 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-5:line-16 | 89.82 → 70.70 | TIGHTENING | -21.2870 | 2.0388 | 2.3192 | False | UNVERIFIED_STOP_NATIVE_BASIS |

Underway transition: 1 eligible sessions; progress 5.8897%, 0.4531 initial ATR, 0.2436 original hypothetical R. The transition is reported source evidence, not inferred from movement.

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-22: MFE 8.3644%, MAE 1.1337%, signed progress 5.8897%. Original-R progress 0.2436. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

SOURCE_REPORTED_DROPPED: alert-6:line-27. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-23 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-4:line-8 | -0.1330 | -0.2222 | -0.2813 | 9.4025 | -0.2401 | -0.2073 |
| alert-5:line-16 | -0.2029 | -0.3037 | -0.3589 | 9.3782 | -0.3234 | -0.2805 |
| alert-5:line-24 | -0.2029 | -0.3037 | -0.3589 | 9.3782 | -0.3234 | -0.2805 |
| alert-6:line-27 | -0.1684 | -0.2972 | -0.3566 | 9.0186 | -0.3243 | -0.2868 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-4:line-8 | 131.15 | -5.7251 | 93.62 | -1.7336 |
| alert-5:line-16 | 131.15 | -6.7262 | 93.62 | -2.7244 |
| alert-5:line-24 | 131.15 | -6.7262 | 93.62 | -2.7244 |
| alert-6:line-27 | 131.15 | -7.0565 | 93.62 | -2.8951 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
