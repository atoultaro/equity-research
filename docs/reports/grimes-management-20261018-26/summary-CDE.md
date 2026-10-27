# CDE: reported management and decision evidence

Source SHORT, final OPEN, setup UNDERWAY. Initial stop 16.40; latest source stop 13.90.

Source opening alert-1:line-11; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 6. Publication-based range: [6, 6]. Conditional ordered-publication bracket: [6, 6]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-1:line-11 | 2026-10-18T15:21:00-04:00 | 2026-10-16 | None | 16.40 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-2:line-12 | 2026-10-19T18:20:00-04:00 | 2026-10-19 | 16.40 | 16.24 | ENTERABLE | 0.8409 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| STOP_CHANGED / alert-5:line-19 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 16.24 | 14.30 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| SETUP_CHANGED / alert-5:line-27 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 16.24 | 14.30 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| STOP_CHANGED / alert-6:line-20 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 14.30 | 13.90 | UNDERWAY | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-2:line-12 | 16.40 → 16.24 | TIGHTENING | -0.9756 | 0.2168 | 1.4501 | False | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-5:line-19 | 16.24 → 14.30 | TIGHTENING | -11.9458 | 2.3592 | 2.8700 | False | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-6:line-20 | 14.30 → 13.90 | TIGHTENING | -2.7972 | 0.5010 | 1.0647 | False | UNVERIFIED_STOP_NATIVE_BASIS |

Underway transition: 4 eligible sessions; progress UNAVAILABLE%, UNAVAILABLE initial ATR, UNAVAILABLE original hypothetical R. The transition is reported source evidence, not inferred from movement.

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

Complete-session conditional path through 2026-10-21: MFE 3.9133%, MAE 2.7814%, signed progress 2.1345%. Original-R progress 0.3511. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-1:line-11 | -0.0544 | -0.1150 | -0.1894 | 0.7725 | -0.2187 | -0.2314 |
| alert-2:line-12 | -0.0530 | -0.1124 | -0.1950 | 0.7379 | -0.2075 | -0.2338 |
| alert-5:line-19 | -0.1073 | -0.1609 | -0.2623 | 0.8223 | -0.2641 | -0.2957 |
| alert-5:line-27 | -0.1073 | -0.1609 | -0.2623 | 0.8223 | -0.2641 | -0.2957 |
| alert-6:line-20 | -0.1140 | -0.1724 | -0.2814 | 0.7984 | -0.2897 | -0.3208 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-1:line-11 | 17.495 | -2.6214 | 16.23 | -0.9838 |
| alert-2:line-12 | 17.495 | -2.9342 | 16.23 | -1.2197 |
| alert-5:line-19 | 17.495 | -4.3962 | 14.675 | -0.9668 |
| alert-5:line-27 | 17.495 | -4.3962 | 14.675 | -0.9668 |
| alert-6:line-20 | 17.495 | -5.0665 | 14.675 | -1.5344 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
