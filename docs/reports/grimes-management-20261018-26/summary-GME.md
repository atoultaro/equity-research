# GME: reported management and decision evidence

Source LONG, final CLOSED, setup ENTERABLE. Initial stop 25.01; latest source stop 24.40.

Source opening alert-4:line-7; source closing alert-7:line-20. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 3. Publication-based range: [3, 3]. Conditional ordered-publication bracket: [3, 3]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-4:line-7 | 2026-10-21T18:51:00-04:00 | 2026-10-21 | None | 25.01 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-5:line-11 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 25.01 | 24.78 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| STOP_CHANGED / alert-6:line-16 | 2026-10-25T12:57:45+00:00 | 2026-10-23 | 24.78 | 24.40 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |
| DROPPED / alert-7:line-20 | 2026-10-26T18:11:00-04:00 | 2026-10-26 | 24.40 | 24.40 | ENTERABLE | UNAVAILABLE | MODELED_CLOSED_BEFORE_DECISION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-5:line-11 | 25.01 → 24.78 | WIDENING | -0.9196 | -0.1848 | 0.3054 | True | UNVERIFIED_STOP_NATIVE_BASIS |
| alert-6:line-16 | 24.78 → 24.40 | WIDENING | -1.5335 | -0.3080 | 0.0324 | True | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: MODELED_CLOSED_BEFORE_DECISION.

No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions.

SOURCE_REPORTED_DROPPED: alert-7:line-20. Actual cause: EXIT_REASON_UNRESOLVED.

Conditional stop evidence: 2026-10-22 TRIGGER_OBSERVED_UNDER_ASSUMPTION.

Conditional target evidence: UNAVAILABLE / no supporting modeled observation.

Earlier nonprogress-window flags: False; terminal time-stop hypothesis: None (MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE). Earlier flags do not establish the cause of a later DROP or an expert rule.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-4:line-7 | -0.0171 | 0.0277 | 0.1901 | 1.1836 | 0.0789 | 0.0405 |
| alert-5:line-11 | -0.0511 | -0.0082 | 0.1422 | 1.2443 | 0.0191 | -0.0266 |
| alert-6:line-16 | -0.0664 | -0.0332 | 0.1103 | 1.2336 | 0.0770 | 0.0373 |
| alert-7:line-20 | -0.0896 | -0.0689 | 0.0642 | 1.2650 | -0.0022 | -0.0484 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-4:line-7 | 28.3 | -1.6982 | 24.04 | 1.9010 |
| alert-5:line-11 | 28.3 | -2.3387 | 24.04 | 1.0850 |
| alert-6:line-16 | 28.3 | -2.8211 | 24.04 | 0.6323 |
| alert-7:line-20 | 28.3 | -3.4783 | 24.04 | -0.1107 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
