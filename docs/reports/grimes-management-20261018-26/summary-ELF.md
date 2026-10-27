# ELF: reported management and decision evidence

Source LONG, final OPEN, setup ENTERABLE. Initial stop 110.50; latest source stop 109.20.

Source opening alert-3:line-7; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 4. Publication-based range: [4, 4]. Conditional ordered-publication bracket: [4, 4]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-3:line-7 | 2026-10-20T18:26:00-04:00 | 2026-10-20 | None | 110.50 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-5:line-10 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 110.50 | 108.60 | ENTERABLE | -0.2775 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| STOP_CHANGED / alert-6:line-15 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 108.60 | 109.20 | ENTERABLE | -0.9279 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-5:line-10 | 110.50 → 108.60 | WIDENING | -1.7195 | -0.4999 | 1.1814 | True | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-6:line-15 | 108.60 → 109.20 | TIGHTENING | 0.5525 | 0.1575 | 1.4806 | False | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: AVAILABLE_AT_LAST_OBSERVABLE_SESSION.

Complete-session conditional path through 2026-10-26: MFE 0.8152%, MAE 3.4863%, signed progress -2.0553%. Original-R progress -0.4927. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-3:line-7 | 0.0390 | 0.0799 | 0.1199 | 3.8364 | 0.1299 | 0.0593 |
| alert-5:line-10 | 0.0248 | 0.0685 | 0.1134 | 3.8007 | 0.1482 | 0.0381 |
| alert-6:line-15 | 0.0136 | 0.0543 | 0.1014 | 3.8093 | 0.1652 | 0.0674 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-3:line-7 | 99.8 | 3.8942 | 97.0 | 4.6241 |
| alert-5:line-10 | 118.29 | -0.8683 | 97.0 | 4.7333 |
| alert-6:line-15 | 118.29 | -1.0632 | 97.0 | 4.5258 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
