# Grimes lifecycle reconstruction: ELF

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| ELF | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN / — |

## ELF (ELF-001)

Initial stop 110.50; latest source stop 109.20. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-21T13:30:00+00:00; modeled Open 115.31; original per-share R 4.81; hypothetical target 120.12. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 11 | OPEN_NEW_POSITION | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 110.50 | ENTERABLE |
| 28 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 108.60 | ENTERABLE |
| 52 | STOP_CHANGED | UNKNOWN | 2026-10-25T12:57:45+00:00 | 109.20 | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- POSSIBLE_TIME_STOP: 2026-10-22; .
- POSSIBLE_TIME_STOP: 2026-10-23; .

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-3:line-7 | — | 110.50 | INITIAL | ENTERABLE |
| alert-5:line-10 | 110.50 | 108.60 | WIDENING | ENTERABLE |
| alert-6:line-15 | 108.60 | 109.20 | TIGHTENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-3:line-7 | 2026-10-20 | 1.110328% | 6.083580% | 12.358010% | 36.578979% | 1.105194563395892177110773127 |
| alert-5:line-10 | 2026-10-22 | 1.063456% | -0.964603% | 14.338272% | 42.138443% | 1.681262920503791111664762548 |
| alert-6:line-15 | 2026-10-23 | -0.652231% | 0.616523% | 14.802532% | 38.876732% | 1.323082692668192530831226837 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-3:line-7 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-7 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-7 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-7 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-5:line-10 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-10 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-10 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-10 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-6:line-15 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-15 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-15 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-15 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | -0.32 | 0.57 | -0.08341091044497299449892627373 | 0.1485756842301081464512124251 | True |
| 3 | AVAILABLE | -1.07 | 0.94 | -0.2789052318003784503557847278 | 0.2450195494321081713405959291 | True |
| 5 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLP. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.054307349419 | AVAILABLE |
| close_sma50 | 0.101429042478 | AVAILABLE |
| close_sma150 | 0.435201121628 | AVAILABLE |
| close_sma200 | 0.416689505163 | AVAILABLE |
| sma50_slope20 | 0.098407877375 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-16', 'confirmed_session': '2026-10-21', 'price': 118.29} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-09-28', 'confirmed_session': '2026-10-01', 'price': 97.0} | AVAILABLE |
| realized_volatility20 | 0.020987574881 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.165216171343 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.213379974139 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.119237213301 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.173920945179 | AVAILABLE |
| Relative / sector, 20 sessions | 0.067379992008 | AVAILABLE |

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
