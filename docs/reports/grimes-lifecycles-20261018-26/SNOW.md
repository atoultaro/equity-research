# Grimes lifecycle reconstruction: SNOW

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| SNOW | SHORT | CLOSED | ENTERABLE | UNRESOLVED_BASIS | MODELED_CLOSED / ASSUMED_STOP_TRIGGERED |

## SNOW (SNOW-001)

Initial stop 330.70; latest source stop 330.70. Source CLOSED, setup ENTERABLE; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-26T13:30:00+00:00; modeled Open 324.7; original per-share R 6.00; hypothetical target 318.70. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 51 | OPEN_NEW_POSITION | UNKNOWN | 2026-10-25T12:57:45+00:00 | 330.70 | ENTERABLE |
| 70 | DROPPED | 2026-10-26T18:10:00-04:00 | 2026-10-26T18:11:00-04:00 | — | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- ASSUMED_STOP_TRIGGERED: 2026-10-26; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-26; ASSUMED_STOP_TRIGGERED.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-6:line-12 | — | 330.70 | INITIAL | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-6:line-12 | 2026-10-23 | 3.653332% | 6.058532% | -3.128535% | 9.168064% | 0.3015367009972183951552967368 |
| alert-7:line-22 | 2026-10-26 | 2.925360% | 6.215316% | 2.081556% | 14.208265% | 0.2418305966509471333019565770 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-6:line-12 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-12 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-12 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-12 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |
| alert-7:line-22 | SPY | 2026-10-26 | 0.710554% | -0.144818% | -0.031348% | 2.455055% | 0.947908% |
| alert-7:line-22 | QQQ | 2026-10-26 | 1.107325% | -0.857509% | -3.303328% | 3.518946% | 1.735167% |
| alert-7:line-22 | RSP | 2026-10-26 | 0.346356% | 1.822868% | 3.599695% | 1.060416% | 0.952644% |
| alert-7:line-22 | IWM | 2026-10-26 | 0.449683% | 2.104836% | -1.082066% | -4.879808% | 1.310517% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLK. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | -0.000168653444 | AVAILABLE |
| close_sma50 | 0.009532616086 | AVAILABLE |
| close_sma150 | 0.316856842191 | AVAILABLE |
| close_sma200 | 0.414221422446 | AVAILABLE |
| sma50_slope20 | 0.04264251883 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-12', 'confirmed_session': '2026-10-15', 'price': 370.55} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-16', 'confirmed_session': '2026-10-21', 'price': 302.24} | AVAILABLE |
| realized_volatility20 | 0.034081031073 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.021135656325 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.055688403445 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.014653897715 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.031982280194 | AVAILABLE |
| Relative / sector, 20 sessions | 0.065796747368 | AVAILABLE |

Full MA, swing, volatility, sector and relative-strength measurements are retained in the event-context JSON. These are agent-selected diagnostics, not attributed Grimes entry/exit rules. Earnings completeness remains unknown. Exploratory 2/3/5-session progress/MFE flags never create a definitive time exit.

## Comparison and limits

```json
{
  "conditional_basis_model": "MODELED_CLOSED",
  "model": "UNRESOLVED_BASIS",
  "source": "CLOSED"
}
```

Source closures do not establish which stop, target or time rule was executed. Right-censored positions and unresolved basis/timing are not successful trades. This selected, short observation period cannot establish a trading edge.
