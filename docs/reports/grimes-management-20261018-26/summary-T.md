# T: reported management and decision evidence

Source SHORT, final CLOSED, setup UNDERWAY. Initial stop 24.00; latest source stop 22.20.

Source opening alert-1:line-12; source closing alert-5:line-31. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 4. Publication-based range: [4, 4]. Conditional ordered-publication bracket: [4, 4]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-1:line-12 | 2026-10-18T15:21:00-04:00 | 2026-10-16 | None | 24.00 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-2:line-13 | 2026-10-19T18:20:00-04:00 | 2026-10-19 | 24.00 | 23.80 | ENTERABLE | 0.2151 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| SETUP_CHANGED / alert-2:line-16 | 2026-10-19T18:20:00-04:00 | 2026-10-19 | 24.00 | 23.80 | ENTERABLE | 0.2151 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| STOP_CHANGED / alert-4:line-15 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | 23.80 | 22.20 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| DROPPED / alert-5:line-31 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 22.20 | 22.20 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-2:line-13 | 24.00 → 23.80 | TIGHTENING | -0.8333 | 0.3135 | 1.2542 | False | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-4:line-15 | 23.80 → 22.20 | TIGHTENING | -6.7227 | 2.1435 | 2.5321 | False | UNVERIFIED_STOP_NATIVE_BASIS |

Underway transition: 1 eligible sessions; progress 0.2151%, 0.0766 initial ATR, 0.0667 original hypothetical R. The transition is reported source evidence, not inferred from movement.

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-20: MFE 0.7742%, MAE 1.8495%, signed progress -0.7312%. Original-R progress -0.2267. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

SOURCE_REPORTED_DROPPED: alert-5:line-31. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: UNAVAILABLE / no supporting modeled observation.

Conditional target evidence: 2026-10-21 HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN.

Earlier nonprogress-window flags: True; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-1:line-12 | -0.0048 | -0.0326 | -0.0598 | 0.6529 | -0.0791 | -0.0731 |
| alert-2:line-13 | -0.0106 | -0.0380 | -0.0690 | 0.6379 | -0.0801 | -0.0498 |
| alert-2:line-16 | -0.0106 | -0.0380 | -0.0690 | 0.6379 | -0.0801 | -0.0498 |
| alert-4:line-15 | -0.0511 | -0.0818 | -0.1184 | 0.7464 | -0.1399 | -0.1055 |
| alert-5:line-31 | -0.0060 | -0.0416 | -0.0839 | 0.7971 | -0.1027 | -0.0518 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-1:line-12 | 24.97 | -2.3435 | 21.96 | 2.2670 |
| alert-2:line-13 | 24.97 | -2.7749 | 21.96 | 1.9440 |
| alert-2:line-16 | 24.97 | -2.7749 | 21.96 | 1.9440 |
| alert-4:line-15 | 23.85 | -2.5990 | 21.96 | -0.0670 |
| alert-5:line-31 | 23.85 | -1.3925 | 21.96 | 0.9785 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
