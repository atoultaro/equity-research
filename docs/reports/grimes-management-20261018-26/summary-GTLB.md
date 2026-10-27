# GTLB: reported management and decision evidence

Source LONG, final OPEN, setup ENTERABLE. Initial stop 51.60; latest source stop 52.10.

Source opening alert-6:line-10; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 1. Publication-based range: UNRESOLVED. Conditional ordered-publication bracket: [1, 2]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-6:line-10 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | None | 51.60 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-7:line-14 | 2026-10-26T18:11:00-04:00 | 2026-10-26 | 51.60 | 52.10 | ENTERABLE | 0.4433 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-7:line-14 | 51.60 → 52.10 | TIGHTENING | 0.9690 | 0.1812 | 1.8302 | False | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: AVAILABLE_AT_LAST_OBSERVABLE_SESSION.

Complete-session conditional path through 2026-10-26: MFE 1.3475%, MAE 0.9752%, signed progress 0.4433%. Original-R progress 0.0521. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-6:line-10 | 0.0339 | 0.0740 | 0.1573 | 2.8464 | 0.2195 | 0.2870 |
| alert-7:line-14 | 0.0394 | 0.0704 | 0.1582 | 2.7593 | 0.2263 | 0.2799 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-6:line-10 | 57.89 | -0.5656 | 50.3 | 2.1009 |
| alert-7:line-14 | 57.89 | -0.4494 | 50.3 | 2.3013 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
