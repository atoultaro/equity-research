# Grimes lifecycle reconstruction: EBAY

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| EBAY | LONG | OPEN | ENTERABLE | MODELED_CLOSED | MODELED_CLOSED / ASSUMED_STOP_TRIGGERED |

## EBAY (EBAY-001)

Initial stop 119.20; latest source stop 117.50. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-26T13:30:00+00:00; modeled Open 121.24; original per-share R 2.04; hypothetical target 123.28. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 48 | OPEN_NEW_POSITION | UNKNOWN | 2026-10-25T12:57:45+00:00 | 119.20 | ENTERABLE |
| 66 | STOP_CHANGED | 2026-10-26T18:10:00-04:00 | 2026-10-26T18:11:00-04:00 | 117.50 | ENTERABLE |

Primary modeled events:

- ASSUMED_STOP_TRIGGERED: 2026-10-26; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-26; ASSUMED_STOP_TRIGGERED.
- SOURCE_MODEL_CONFLICT: alert-7:line-13; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: final reconciliation; SOURCE_NOT_REPORTED_DROPPED_MODEL_CLOSED.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- ASSUMED_STOP_TRIGGERED: 2026-10-26; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-26; ASSUMED_STOP_TRIGGERED.
- SOURCE_MODEL_CONFLICT: alert-7:line-13; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: final reconciliation; SOURCE_NOT_REPORTED_DROPPED_MODEL_CLOSED.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-6:line-9 | — | 119.20 | INITIAL | ENTERABLE |
| alert-7:line-13 | 119.20 | 117.50 | WIDENING | ENTERABLE |

EBAY priority case: original 119.20 stop versus operator/native October 26 Low 117.87. Original email availability evidence precedes Monday RTH; exact weekly publication is still unknown. Under the explicitly documented session-scale corroboration, the 119.20 trigger closes the modeled episode. The evening source revision to 117.50 remains in the OPEN source episode and cannot rescue or re-enter the closed model. This is a source/model conflict; the actual discretionary execution history is unknown. Without email-bound or quote-basis evidence the result must remain unresolved.

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-6:line-9 | 2026-10-23 | -0.516224% | 0.939475% | 12.520853% | 6.950317% | 0.6307849133537978534042838489 |
| alert-7:line-13 | 2026-10-26 | -2.297999% | -1.535652% | 10.529258% | 4.043505% | 0.3120398009950000366327566169 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-6:line-9 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-9 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-9 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-9 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |
| alert-7:line-13 | SPY | 2026-10-26 | 0.710554% | -0.144818% | -0.031348% | 2.455055% | 0.947908% |
| alert-7:line-13 | QQQ | 2026-10-26 | 1.107325% | -0.857509% | -3.303328% | 3.518946% | 1.735167% |
| alert-7:line-13 | RSP | 2026-10-26 | 0.346356% | 1.822868% | 3.599695% | 1.060416% | 0.952644% |
| alert-7:line-13 | IWM | 2026-10-26 | 0.449683% | 2.104836% | -1.082066% | -4.879808% | 1.310517% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLY. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.037214508062 | AVAILABLE |
| close_sma50 | 0.083667697165 | AVAILABLE |
| close_sma150 | 0.098645972712 | AVAILABLE |
| close_sma200 | 0.146613734136 | AVAILABLE |
| sma50_slope20 | 0.015425032561 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-15', 'confirmed_session': '2026-10-20', 'price': 124.59} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-09-30', 'confirmed_session': '2026-10-05', 'price': 104.61} | AVAILABLE |
| realized_volatility20 | 0.017844232054 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.105639173755 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.143051314385 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.06688787493 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.117383403993 | AVAILABLE |
| Relative / sector, 20 sessions | 0.054410043229 | AVAILABLE |

Full MA, swing, volatility, sector and relative-strength measurements are retained in the event-context JSON. These are agent-selected diagnostics, not attributed Grimes entry/exit rules. Earnings completeness remains unknown. Exploratory 2/3/5-session progress/MFE flags never create a definitive time exit.

## Comparison and limits

```json
{
  "conditional_basis_model": "MODELED_CLOSED",
  "model": "MODELED_CLOSED",
  "source": "OPEN"
}
```

Source closures do not establish which stop, target or time rule was executed. Right-censored positions and unresolved basis/timing are not successful trades. This selected, short observation period cannot establish a trading edge.
