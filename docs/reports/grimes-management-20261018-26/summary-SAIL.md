# SAIL: reported management and decision evidence

Source LONG, final OPEN, setup ENTERABLE. Initial stop 20.90; latest source stop 20.90.

Source opening alert-7:line-7; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 0. Publication-based range: [0, 0]. Conditional ordered-publication bracket: [0, 0]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-7:line-7 | 2026-10-26T18:11:00-04:00 | 2026-10-26 | None | 20.90 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| No reported revision | — | — | — | — | — | — | — |

## Exit and exposure interpretation

Primary analytical path: NO_ELIGIBLE_COMPLETED_ENTRY_SESSION. Conditional analytical path: NO_ELIGIBLE_COMPLETED_ENTRY_SESSION.

No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-7:line-7 | 0.0953 | 0.0854 | 0.1067 | 1.0850 | 0.0577 | 0.1040 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-7:line-7 | 20.08 | 1.5392 | 18.32 | 3.1613 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
