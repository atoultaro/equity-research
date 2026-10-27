# Grimes lifecycle reconstruction: CNQ

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| CNQ | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN / — |

## CNQ (CNQ-001)

Initial stop 53.30; latest source stop 53.30. Source OPEN, setup ENTERABLE; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-26T13:30:00+00:00; modeled Open 54.59; original per-share R 1.29; hypothetical target 55.88. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 47 | OPEN_NEW_POSITION | UNKNOWN | 2026-10-25T12:57:45+00:00 | 53.30 | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- MODELED_OPEN.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-6:line-8 | — | 53.30 | INITIAL | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-6:line-8 | 2026-10-23 | 2.114243% | 2.342007% | 16.135836% | 16.455161% | 1.254582484725178674387446556 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-6:line-8 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-8 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-8 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-8 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | RIGHT_CENSORED_OR_MISSING_SESSION | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLE. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.087755343949 | AVAILABLE |
| close_sma50 | 0.097061882579 | AVAILABLE |
| close_sma150 | 0.17180516735 | AVAILABLE |
| close_sma200 | 0.212147897014 | AVAILABLE |
| sma50_slope20 | 0.037923846237 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-09-10', 'confirmed_session': '2026-09-15', 'price': 52.31} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-09-29', 'confirmed_session': '2026-10-02', 'price': 46.58} | AVAILABLE |
| realized_volatility20 | 0.013991486988 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.178748863068 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.227472034942 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.132235910493 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.187554733184 | AVAILABLE |
| Relative / sector, 20 sessions | 0.039242360505 | AVAILABLE |

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
