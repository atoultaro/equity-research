# SIG: reported management and decision evidence

Source LONG, final OPEN, setup ENTERABLE. Initial stop 111.80; latest source stop 112.50.

Source opening alert-3:line-9; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 4. Publication-based range: [4, 4]. Conditional ordered-publication bracket: [4, 4]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-3:line-9 | 2026-10-20T18:26:00-04:00 | 2026-10-20 | None | 111.80 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-6:line-17 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 111.80 | 112.50 | ENTERABLE | 1.2179 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-6:line-17 | 111.80 → 112.50 | TIGHTENING | 0.6261 | 0.1687 | 1.2968 | False | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: AVAILABLE_AT_LAST_OBSERVABLE_SESSION.

Complete-session conditional path through 2026-10-26: MFE 2.6604%, MAE 1.9003%, signed progress -0.6651%. Original-R progress -0.1940. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-3:line-9 | 0.0465 | 0.0884 | 0.1975 | 4.4900 | 0.1588 | 0.1207 |
| alert-6:line-17 | 0.0278 | 0.0788 | 0.1955 | 4.1486 | 0.1631 | 0.1202 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-3:line-9 | 106.62 | 2.0267 | 100.16 | 3.4655 |
| alert-6:line-17 | 122.64 | -1.3161 | 100.16 | 4.1026 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
