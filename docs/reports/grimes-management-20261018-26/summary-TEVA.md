# TEVA: reported management and decision evidence

Source LONG, final CLOSED, setup ENTERABLE. Initial stop 40.40; latest source stop 39.05.

Source opening alert-1:line-9; source closing alert-6:line-26. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 5. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [4, 5]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-1:line-9 | 2026-10-18T15:21:00-04:00 | 2026-10-16 | None | 40.40 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-4:line-14 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | 40.40 | 39.35 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| STOP_CHANGED / alert-5:line-13 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 39.35 | 39.05 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| DROPPED / alert-6:line-26 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 39.05 | 39.05 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-4:line-14 | 40.40 → 39.35 | WIDENING | -2.5990 | -0.9716 | 0.2036 | None | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-5:line-13 | 39.35 → 39.05 | WIDENING | -0.7624 | -0.2726 | 0.7813 | None | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-20: MFE 1.1106%, MAE 1.4969%, signed progress -1.3761%. Original-R progress -0.5588. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

SOURCE_REPORTED_DROPPED: alert-6:line-26. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-21 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: True; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-1:line-9 | 0.0270 | 0.0385 | UNAVAILABLE | 1.1314 | 0.0625 | 0.0145 |
| alert-4:line-14 | -0.0066 | 0.0112 | UNAVAILABLE | 1.0807 | 0.0342 | -0.0177 |
| alert-5:line-13 | -0.0189 | 0.0010 | UNAVAILABLE | 1.1007 | 0.0040 | -0.0633 |
| alert-6:line-26 | -0.0344 | -0.0192 | UNAVAILABLE | 1.1257 | 0.0207 | -0.0425 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-1:line-9 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| alert-4:line-14 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| alert-5:line-13 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| alert-6:line-26 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
