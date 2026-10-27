# Grimes lifecycle reconstruction: GTLB

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| GTLB | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN / — |

## GTLB (GTLB-001)

Initial stop 51.60; latest source stop 52.10. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-26T13:30:00+00:00; modeled Open 56.4; original per-share R 4.80; hypothetical target 61.20. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 49 | OPEN_NEW_POSITION | UNKNOWN | 2026-10-25T12:57:45+00:00 | 51.60 | ENTERABLE |
| 67 | STOP_CHANGED | 2026-10-26T18:10:00-04:00 | 2026-10-26T18:11:00-04:00 | 52.10 | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- MODELED_OPEN.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-6:line-10 | — | 51.60 | INITIAL | ENTERABLE |
| alert-7:line-14 | 51.60 | 52.10 | TIGHTENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-6:line-10 | 2026-10-23 | 3.209243% | 6.671721% | 20.153715% | 66.903915% | 1.644165621078798870922798675 |
| alert-7:line-14 | 2026-10-26 | 0.657427% | 6.305123% | 22.592512% | 64.155317% | 1.648977478643370543362294241 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-6:line-10 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-10 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-10 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-10 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |
| alert-7:line-14 | SPY | 2026-10-26 | 0.710554% | -0.144818% | -0.031348% | 2.455055% | 0.947908% |
| alert-7:line-14 | QQQ | 2026-10-26 | 1.107325% | -0.857509% | -3.303328% | 3.518946% | 1.735167% |
| alert-7:line-14 | RSP | 2026-10-26 | 0.346356% | 1.822868% | 3.599695% | 1.060416% | 0.952644% |
| alert-7:line-14 | IWM | 2026-10-26 | 0.449683% | 2.104836% | -1.082066% | -4.879808% | 1.310517% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLK. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.070402841811 | AVAILABLE |
| close_sma50 | 0.158216693859 | AVAILABLE |
| close_sma150 | 0.617105253142 | AVAILABLE |
| close_sma200 | 0.683929545458 | AVAILABLE |
| sma50_slope20 | 0.160429329955 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-13', 'confirmed_session': '2026-10-16', 'price': 57.89} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-14', 'confirmed_session': '2026-10-19', 'price': 50.3} | AVAILABLE |
| realized_volatility20 | 0.030656705281 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.226309542465 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.267804874892 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.183328895018 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.239335547649 | AVAILABLE |
| Relative / sector, 20 sessions | 0.279944259638 | AVAILABLE |

Full MA, swing, volatility, sector and relative-strength measurements are retained in the event-context JSON. These are agent-selected diagnostics, not attributed Grimes entry/exit rules. Earnings completeness remains unknown. Exploratory 2/3/5-session progress/MFE flags never create a definitive time exit.

## Comparison and limits

```json
{
  "conditional_basis_model": "MODELED_OPEN",
  "model": "UNRESOLVED_BASIS",
  "source": "OPEN"
}
```

Source closures do not establish which stop, target or time rule was executed. Right-censored positions and unresolved basis/timing are not successful trades. This selected, short observation period cannot establish a trading edge.
