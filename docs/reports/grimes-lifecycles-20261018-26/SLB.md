# Grimes lifecycle reconstruction: SLB

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| SLB | LONG | OPEN | ENTERABLE | NOT_YET_ACTIVE_RIGHT_CENSORED | NOT_YET_ACTIVE_RIGHT_CENSORED / — |

## SLB (SLB-001)

Initial stop 51.10; latest source stop 51.10. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-27T13:30:00+00:00; modeled Open UNAVAILABLE; original per-share R UNAVAILABLE; hypothetical target UNAVAILABLE. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 63 | OPEN_NEW_POSITION | 2026-10-26T18:10:00-04:00 | 2026-10-26T18:11:00-04:00 | 51.10 | ENTERABLE |

Primary modeled events:

- NOT_YET_ACTIVE_RIGHT_CENSORED; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- NOT_YET_ACTIVE_RIGHT_CENSORED.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-7:line-8 | — | 51.10 | INITIAL | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-7:line-8 | 2026-10-26 | 0.037693% | 8.127928% | 3.087978% | 7.037709% | 1.251467268622911831397867006 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-7:line-8 | SPY | 2026-10-26 | 0.710554% | -0.144818% | -0.031348% | 2.455055% | 0.947908% |
| alert-7:line-8 | QQQ | 2026-10-26 | 1.107325% | -0.857509% | -3.303328% | 3.518946% | 1.735167% |
| alert-7:line-8 | RSP | 2026-10-26 | 0.346356% | 1.822868% | 3.599695% | 1.060416% | 0.952644% |
| alert-7:line-8 | IWM | 2026-10-26 | 0.449683% | 2.104836% | -1.082066% | -4.879808% | 1.310517% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | NOT_YET_ACTIVE_RIGHT_CENSORED | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | NOT_YET_ACTIVE_RIGHT_CENSORED | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | NOT_YET_ACTIVE_RIGHT_CENSORED | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLE. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.070226021735 | AVAILABLE |
| close_sma50 | 0.011833958581 | AVAILABLE |
| close_sma150 | 0.017531393693 | AVAILABLE |
| close_sma200 | 0.034701889676 | AVAILABLE |
| sma50_slope20 | -0.005588201843 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-06', 'confirmed_session': '2026-10-09', 'price': 50.61} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-15', 'confirmed_session': '2026-10-20', 'price': 47.17} | AVAILABLE |
| realized_volatility20 | 0.024535719419 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.031203039401 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.06609644228 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.004939364086 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.042156600204 | AVAILABLE |
| Relative / sector, 20 sessions | -0.080734714358 | AVAILABLE |

Full MA, swing, volatility, sector and relative-strength measurements are retained in the event-context JSON. These are agent-selected diagnostics, not attributed Grimes entry/exit rules. Earnings completeness remains unknown. Exploratory 2/3/5-session progress/MFE flags never create a definitive time exit.

## Comparison and limits

```json
{
  "conditional_basis_model": "NOT_YET_ACTIVE_RIGHT_CENSORED",
  "model": "NOT_YET_ACTIVE_RIGHT_CENSORED",
  "source": "OPEN"
}
```

Source closures do not establish which stop, target or time rule was executed. Right-censored positions and unresolved basis/timing are not successful trades. This selected, short observation period cannot establish a trading edge.
