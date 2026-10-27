# Grimes lifecycle reconstruction: HUM

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| HUM | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN / — |

## HUM (HUM-001)

Initial stop 404.00; latest source stop 408.10. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-21T13:30:00+00:00; modeled Open 431.52; original per-share R 27.52; hypothetical target 459.04. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 12 | OPEN_NEW_POSITION | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 404.00 | ENTERABLE |
| 30 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 408.10 | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- POSSIBLE_TIME_STOP: 2026-10-22; .
- POSSIBLE_TIME_STOP: 2026-10-23; .

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-3:line-8 | — | 404.00 | INITIAL | ENTERABLE |
| alert-5:line-12 | 404.00 | 408.10 | TIGHTENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-3:line-8 | 2026-10-20 | 2.988096% | 1.665160% | 14.887097% | 12.129083% | 1.138821237213833414515343400 |
| alert-5:line-12 | 2026-10-22 | -1.046025% | -2.598334% | 10.688368% | 15.204838% | 0.6291640477687077193106748894 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-3:line-8 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-8 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-8 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-8 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-5:line-12 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-12 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-12 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-12 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | -10.55 | 2.61 | -0.5138821237213833414515343400 | 0.1271310277642474427666829031 | True |
| 3 | AVAILABLE | -9.45 | 2.61 | -0.4603019970774476376035070628 | 0.1271310277642474427666829031 | True |
| 5 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLV. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.031375906959 | AVAILABLE |
| close_sma50 | 0.060252846768 | AVAILABLE |
| close_sma150 | 0.250124229431 | AVAILABLE |
| close_sma200 | 0.384224470788 | AVAILABLE |
| sma50_slope20 | 0.027268300685 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-09', 'confirmed_session': '2026-10-14', 'price': 456.5} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-19', 'confirmed_session': '2026-10-22', 'price': 407.5} | AVAILABLE |
| realized_volatility20 | 0.033892815227 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.111549059174 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.164437794304 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.066507936513 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.126847350405 | AVAILABLE |
| Relative / sector, 20 sessions | 0.037100552651 | AVAILABLE |

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
