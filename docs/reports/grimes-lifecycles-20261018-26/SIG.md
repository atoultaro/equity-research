# Grimes lifecycle reconstruction: SIG

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| SIG | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN / — |

## SIG (SIG-001)

Initial stop 111.80; latest source stop 112.50. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-21T13:30:00+00:00; modeled Open 115.77; original per-share R 3.97; hypothetical target 119.74. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 13 | OPEN_NEW_POSITION | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 111.80 | ENTERABLE |
| 54 | STOP_CHANGED | UNKNOWN | 2026-10-25T12:57:45+00:00 | 112.50 | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- MODELED_OPEN.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-3:line-9 | — | 111.80 | INITIAL | ENTERABLE |
| alert-6:line-17 | 111.80 | 112.50 | TIGHTENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-3:line-9 | 2026-10-20 | -0.890716% | 6.989645% | 15.236009% | 20.869020% | 0.8730512249443207126948775056 |
| alert-6:line-17 | 2026-10-23 | 0.205233% | -1.105579% | 14.590260% | 22.215269% | 1.128099173553835547435284487 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-3:line-9 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-9 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-9 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-9 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-6:line-17 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-17 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-17 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-17 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | 1.17 | 2.38 | 0.2605790645879732739420935412 | 0.5300668151447661469933184855 | False |
| 3 | AVAILABLE | 1.41 | 2.38 | 0.3140311804008908685968819599 | 0.5300668151447661469933184855 | False |
| 5 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLY. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.078806849567 | AVAILABLE |
| close_sma50 | 0.195506901864 | AVAILABLE |
| close_sma150 | 0.285320350211 | AVAILABLE |
| close_sma200 | 0.283353585379 | AVAILABLE |
| sma50_slope20 | 0.063614838543 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-16', 'confirmed_session': '2026-10-21', 'price': 122.64} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-01', 'confirmed_session': '2026-10-06', 'price': 100.16} | AVAILABLE |
| realized_volatility20 | 0.024707883361 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.163061662231 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.211136409146 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.117167720246 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.171750340758 | AVAILABLE |
| Relative / sector, 20 sessions | 0.120167918568 | AVAILABLE |

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
