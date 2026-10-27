# EBAY: reported management and decision evidence

Source LONG, final OPEN, setup ENTERABLE. Initial stop 119.20; latest source stop 117.50.

Source opening alert-6:line-9; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 1. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [1, 2]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-6:line-9 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | None | 119.20 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-7:line-13 | 2026-10-26T18:11:00-04:00 | 2026-10-26 | 119.20 | 117.50 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-7:line-13 | 119.20 → 117.50 | WIDENING | -1.4262 | -0.4736 | -0.1616 | True | BOUNDED_PR16_QUOTE_SCALE |

## Exit and exposure interpretation

Primary analytical path: MODELED_CLOSED_BEFORE_DECISION. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

EBAY: the PR16 original 119.20 stop is crossed by the corroborated October 26 low 117.87 under its email-availability/session-scale assumptions. The later source revision to 117.50 remains an OPEN-source fact and cannot rescue the closed model. Progress at that revision is unavailable, and the October 26 exit-day Close/High/Low are excluded from held-exposure metrics. No re-entry or intraday revision is inferred.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-6:line-9 | 0.0125 | 0.0669 | 0.1123 | 3.5036 | 0.1421 | 0.0999 |
| alert-7:line-13 | -0.0141 | 0.0372 | 0.0837 | 3.5893 | 0.1056 | 0.0544 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-6:line-9 | 124.59 | -0.9076 | 104.61 | 4.7951 |
| alert-7:line-13 | 124.59 | -1.6633 | 104.61 | 3.9033 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
