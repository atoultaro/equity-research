# Grimes lifecycle reconstruction: GME

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| GME | LONG | CLOSED | ENTERABLE | UNRESOLVED_BASIS | MODELED_CLOSED / ASSUMED_STOP_TRIGGERED |

## GME (GME-001)

Initial stop 25.01; latest source stop 24.40. Source CLOSED, setup ENTERABLE; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-22T13:30:00+00:00; modeled Open 26.0; original per-share R 0.99; hypothetical target 26.99. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 19 | OPEN_NEW_POSITION | 2026-10-21T18:50:00-04:00 | 2026-10-21T18:51:00-04:00 | 25.01 | ENTERABLE |
| 29 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 24.78 | ENTERABLE |
| 53 | STOP_CHANGED | UNKNOWN | 2026-10-25T12:57:45+00:00 | 24.40 | ENTERABLE |
| 68 | DROPPED | 2026-10-26T18:10:00-04:00 | 2026-10-26T18:11:00-04:00 | — | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- ASSUMED_STOP_TRIGGERED: 2026-10-22; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-22; ASSUMED_STOP_TRIGGERED.
- SOURCE_MODEL_CONFLICT: alert-5:line-11; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: alert-6:line-16; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-4:line-7 | — | 25.01 | INITIAL | ENTERABLE |
| alert-5:line-11 | 25.01 | 24.78 | WIDENING | ENTERABLE |
| alert-6:line-16 | 24.78 | 24.40 | WIDENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-4:line-7 | 2026-10-21 | -0.680015% | -3.167587% | 8.636364% | 18.637184% | 1.081472540736661969537985514 |
| alert-5:line-11 | 2026-10-22 | -3.423355% | -9.386153% | 1.478817% | 16.254579% | 0.4902411021812881191499009671 |
| alert-6:line-16 | 2026-10-23 | -2.244978% | -7.422604% | 6.113724% | 13.436929% | 0.3404748118125097191008034197 |
| alert-7:line-20 | 2026-10-26 | -3.706688% | -9.606657% | -0.250417% | 10.036832% | 0.3952569169960474308300395257 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-4:line-7 | SPY | 2026-10-21 | 0.525323% | 0.453482% | 0.687670% | 4.350350% | 0.914974% |
| alert-4:line-7 | QQQ | 2026-10-21 | 1.054861% | -0.514439% | -2.159982% | 7.359102% | 1.553562% |
| alert-4:line-7 | RSP | 2026-10-21 | 0.361345% | 2.145316% | 2.522361% | -0.482337% | 0.930774% |
| alert-4:line-7 | IWM | 2026-10-21 | 0.253826% | 1.883038% | -1.929625% | -5.757235% | 1.403356% |
| alert-5:line-11 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-11 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-11 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-11 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-6:line-16 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-16 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-16 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-16 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |
| alert-7:line-20 | SPY | 2026-10-26 | 0.710554% | -0.144818% | -0.031348% | 2.455055% | 0.947908% |
| alert-7:line-20 | QQQ | 2026-10-26 | 1.107325% | -0.857509% | -3.303328% | 3.518946% | 1.735167% |
| alert-7:line-20 | RSP | 2026-10-26 | 0.346356% | 1.822868% | 3.599695% | 1.060416% | 0.952644% |
| alert-7:line-20 | IWM | 2026-10-26 | 0.449683% | 2.104836% | -1.082066% | -4.879808% | 1.310517% |

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
| close_sma20 | -0.068915812848 | AVAILABLE |
| close_sma50 | 0.064199267973 | AVAILABLE |
| close_sma150 | 0.069526693417 | AVAILABLE |
| close_sma200 | 0.055905560514 | AVAILABLE |
| sma50_slope20 | 0.105912130553 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-15', 'confirmed_session': '2026-10-20', 'price': 28.3} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-08', 'confirmed_session': '2026-10-13', 'price': 24.04} | AVAILABLE |
| realized_volatility20 | 0.026115502035 | AVAILABLE |
| Relative / SPY, 20 sessions | -0.002191385039 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.031572031735 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.037163354851 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.008407456234 | AVAILABLE |
| Relative / sector, 20 sessions | -0.048424251049 | AVAILABLE |

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
