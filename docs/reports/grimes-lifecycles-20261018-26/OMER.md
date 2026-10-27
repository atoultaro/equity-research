# Grimes lifecycle reconstruction: OMER

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| OMER | SHORT | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN / — |

## OMER (OMER-001)

Initial stop 17.20; latest source stop 17.35. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-21T13:30:00+00:00; modeled Open 16.57; original per-share R 0.63; hypothetical target 15.94. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 15 | OPEN_NEW_POSITION | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 17.20 | ENTERABLE |
| 33 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 17.35 | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- POSSIBLE_TIME_STOP: 2026-10-22; .
- POSSIBLE_TIME_STOP: 2026-10-23; .

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-3:line-11 | — | 17.20 | INITIAL | ENTERABLE |
| alert-5:line-15 | 17.20 | 17.35 | WIDENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-3:line-11 | 2026-10-20 | 1.223242% | -12.341102% | -21.377672% | 45.943563% | 0.7291374544291427867327203695 |
| alert-5:line-15 | 2026-10-22 | 3.690037% | -10.271421% | -16.244411% | 44.473008% | 0.5529805328282701995941845585 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-3:line-11 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-11 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-11 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-11 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-5:line-15 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-15 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-15 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-15 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | -0.29 | 0.42 | -0.3253074796683867817730598571 | 0.4711349705542153391196039310 | True |
| 3 | AVAILABLE | -0.00 | 0.42 | -0E+10 | 0.4711349705542153391196039310 | True |
| 5 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLV. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | -0.083546230364 | AVAILABLE |
| close_sma50 | -0.090163403631 | AVAILABLE |
| close_sma150 | 0.216075859283 | AVAILABLE |
| close_sma200 | 0.262784191979 | AVAILABLE |
| sma50_slope20 | 0.172657317876 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-12', 'confirmed_session': '2026-10-15', 'price': 20.24} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-16', 'confirmed_session': '2026-10-21', 'price': 15.845} | AVAILABLE |
| realized_volatility20 | 0.036686195608 | AVAILABLE |
| Relative / SPY, 20 sessions | -0.158913915406 | AVAILABLE |
| Relative / QQQ, 20 sessions | -0.118894108109 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.192995597355 | AVAILABLE |
| Relative / IWM, 20 sessions | -0.147338016199 | AVAILABLE |
| Relative / sector, 20 sessions | -0.215247553889 | AVAILABLE |

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
