# Grimes lifecycle reconstruction: AAOI

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| AAOI | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | MODELED_CLOSED / ASSUMED_STOP_TRIGGERED |

## AAOI (AAOI-001)

Initial stop 89.82; latest source stop 70.70. Source CLOSED, setup UNDERWAY; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-22T13:30:00+00:00; modeled Open 72.33; original per-share R 17.49; hypothetical target 54.84. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 20 | OPEN_NEW_POSITION | 2026-10-21T18:50:00-04:00 | 2026-10-21T18:51:00-04:00 | 89.82 | ENTERABLE |
| 34 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 70.70 | ENTERABLE |
| 40 | SETUP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | — | UNDERWAY |
| 59 | DROPPED | UNKNOWN | 2026-10-25T12:57:45+00:00 | — | UNDERWAY |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- ASSUMED_STOP_TRIGGERED: 2026-10-23; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-23; ASSUMED_STOP_TRIGGERED.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-4:line-8 | — | 89.82 | INITIAL | ENTERABLE |
| alert-5:line-16 | 89.82 | 70.70 | TIGHTENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-4:line-8 | 2026-10-21 | 0.755799% | -10.322431% | -23.490995% | -12.275925% | 1.329428611582701340334132276 |
| alert-5:line-16 | 2026-10-22 | -11.963270% | -18.702974% | -32.623973% | -11.042865% | 0.2804361154799669447924719431 |
| alert-5:line-24 | 2026-10-22 | -11.963270% | -18.702974% | -32.623973% | -11.042865% | 0.2804361154799669447924719431 |
| alert-6:line-27 | 2026-10-23 | -0.822683% | -10.665608% | -33.422091% | -25.080457% | 0.3537131565295615606330804893 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-4:line-8 | SPY | 2026-10-21 | 0.525323% | 0.453482% | 0.687670% | 4.350350% | 0.914974% |
| alert-4:line-8 | QQQ | 2026-10-21 | 1.054861% | -0.514439% | -2.159982% | 7.359102% | 1.553562% |
| alert-4:line-8 | RSP | 2026-10-21 | 0.361345% | 2.145316% | 2.522361% | -0.482337% | 0.930774% |
| alert-4:line-8 | IWM | 2026-10-21 | 0.253826% | 1.883038% | -1.929625% | -5.757235% | 1.403356% |
| alert-5:line-16 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-16 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-16 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-16 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-5:line-24 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-24 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-24 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-24 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-6:line-27 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-27 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-27 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-27 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |

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
| close_sma20 | -0.297242998194 | AVAILABLE |
| close_sma50 | -0.356613792919 | AVAILABLE |
| close_sma150 | -0.482672213983 | AVAILABLE |
| close_sma200 | -0.403261334587 | AVAILABLE |
| sma50_slope20 | -0.060617617515 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-06', 'confirmed_session': '2026-10-09', 'price': 131.15} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-09-28', 'confirmed_session': '2026-10-01', 'price': 93.62} | AVAILABLE |
| realized_volatility20 | 0.066547891488 | AVAILABLE |
| Relative / SPY, 20 sessions | -0.324251347874 | AVAILABLE |
| Relative / QQQ, 20 sessions | -0.296319513747 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.350916115912 | AVAILABLE |
| Relative / IWM, 20 sessions | -0.319203152242 | AVAILABLE |
| Relative / sector, 20 sessions | -0.286839150114 | AVAILABLE |

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
