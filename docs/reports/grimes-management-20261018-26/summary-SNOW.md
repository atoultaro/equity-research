# SNOW: reported management and decision evidence

Source SHORT, final CLOSED, setup ENTERABLE. Initial stop 330.70; latest source stop 330.70.

Source opening alert-6:line-12; source closing alert-7:line-22. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 1. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [1, 2]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-6:line-12 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | None | 330.70 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| DROPPED / alert-7:line-22 | 2026-10-26T18:11:00-04:00 | 2026-10-26 | 330.70 | 330.70 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| No reported revision | — | — | — | — | — | — | — |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions.

SOURCE_REPORTED_DROPPED: alert-7:line-22. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-26 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-6:line-12 | -0.0115 | -0.0276 | -0.0188 | 17.4771 | -0.0168 | 0.0377 |
| alert-7:line-22 | 0.0253 | -0.0002 | 0.0095 | 17.5743 | 0.0211 | 0.0658 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-6:line-12 | 370.55 | -2.5817 | 302.24 | 1.3269 |
| alert-7:line-22 | 370.55 | -2.0257 | 302.24 | 1.8612 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
