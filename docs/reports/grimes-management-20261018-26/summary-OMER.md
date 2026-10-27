# OMER: reported management and decision evidence

Source SHORT, final OPEN, setup ENTERABLE. Initial stop 17.20; latest source stop 17.35.

Source opening alert-3:line-11; source closing not observed, right-censored. Actual entry, holding duration, fill prices, size and realized P&L are unknown.

Eligible sessions under the PR16 availability-bound entry scenario: 4. Publication-based range: [4, 4]. Conditional ordered-publication bracket: [4, 4]. The weekly exact publication stays null; email availability is separate evidence.

All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.

| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |
|---|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION / alert-3:line-11 | 2026-10-20T18:26:00-04:00 | 2026-10-20 | None | 17.20 | ENTERABLE | UNAVAILABLE | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| STOP_CHANGED / alert-5:line-15 | 2026-10-22T18:28:00-04:00 | 2026-10-22 | 17.20 | 17.35 | ENTERABLE | -1.7502 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |

## Stop decisions

| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |
|---|---|---|---|---|---|---|---|
| alert-5:line-15 | 17.20 → 17.35 | WIDENING | 0.8721 | -0.1693 | 0.3837 | True | UNVERIFIED_STOP_NATIVE_BASIS |

## Exit and exposure interpretation

Primary analytical path: UNVERIFIED_BASIS. Conditional analytical path: AVAILABLE_AT_LAST_OBSERVABLE_SESSION.

Complete-session conditional path through 2026-10-26: MFE 2.5347%, MAE 1.9010%, signed progress 1.6898%. Original-R progress 0.4444. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision.

No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger.

## Context and alternative explanations

Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.

| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |
|---|---|---|---|---|---|---|
| alert-3:line-11 | -0.0933 | -0.1190 | -0.1013 | 0.8915 | -0.2094 | -0.2572 |
| alert-5:line-15 | -0.0516 | -0.0835 | -0.0902 | 0.8861 | -0.1589 | -0.2152 |

Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.

| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |
|---|---|---|---|---|
| alert-3:line-11 | 20.24 | -4.1393 | 18.02 | -1.6490 |
| alert-5:line-15 | 20.24 | -3.8144 | 15.845 | 1.1455 |

Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.
