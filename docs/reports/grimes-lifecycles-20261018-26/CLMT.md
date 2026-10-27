# Grimes lifecycle reconstruction: CLMT

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| CLMT | LONG | CLOSED | ENTERABLE | UNRESOLVED_BASIS | MODELED_CLOSED / ASSUMED_STOP_TRIGGERED |

## CLMT (CLMT-001)

Initial stop 55.25; latest source stop 53.02. Source CLOSED, setup ENTERABLE; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-19T13:30:00+00:00; modeled Open 57.47; original per-share R 2.22; hypothetical target 59.69. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 1 | OPEN_NEW_POSITION | 2026-10-18T15:20:00-04:00 | 2026-10-18T15:21:00-04:00 | 55.25 | ENTERABLE |
| 7 | STOP_CHANGED | 2026-10-19T18:19:00-04:00 | 2026-10-19T18:20:00-04:00 | 53.40 | ENTERABLE |
| 17 | STOP_CHANGED | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 53.02 | ENTERABLE |
| 26 | DROPPED | 2026-10-21T18:50:00-04:00 | 2026-10-21T18:51:00-04:00 | — | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- ASSUMED_STOP_TRIGGERED: 2026-10-19; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-19; ASSUMED_STOP_TRIGGERED.
- SOURCE_MODEL_CONFLICT: alert-2:line-11; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: alert-3:line-15; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-1:line-8 | — | 55.25 | INITIAL | ENTERABLE |
| alert-2:line-11 | 55.25 | 53.40 | WIDENING | ENTERABLE |
| alert-3:line-15 | 53.40 | 53.02 | WIDENING | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-1:line-8 | 2026-10-16 | -0.841346% | 2.357320% | -2.118644% | 34.866885% | 1.235439463466551805039915260 |
| alert-2:line-11 | 2026-10-19 | -3.826840% | -2.851146% | -4.439092% | 33.221396% | 0.9787651094411671809651536425 |
| alert-3:line-15 | 2026-10-20 | 0.918257% | -4.335211% | -0.655796% | 35.780039% | 1.397233201581303801027980495 |
| alert-4:line-21 | 2026-10-21 | -6.173060% | -8.586824% | -3.291651% | 26.783992% | 0.1835925587069116442477153454 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-1:line-8 | SPY | 2026-10-16 | -1.106519% | -1.967710% | 0.204808% | 3.396191% | 0.902531% |
| alert-1:line-8 | QQQ | 2026-10-16 | -2.500000% | -5.519986% | -1.614804% | 2.578184% | 1.420219% |
| alert-1:line-8 | RSP | 2026-10-16 | -0.423256% | 0.492865% | 0.847897% | 1.023971% | 0.951869% |
| alert-1:line-8 | IWM | 2026-10-16 | -1.686782% | -3.047250% | -4.808166% | -7.412099% | 1.465337% |
| alert-2:line-11 | SPY | 2026-10-19 | 0.423190% | -1.493381% | -0.907563% | 3.728364% | 0.922771% |
| alert-2:line-11 | QQQ | 2026-10-19 | 1.205974% | -3.710257% | -3.116782% | 4.988089% | 1.497856% |
| alert-2:line-11 | RSP | 2026-10-19 | -0.322294% | 0.098504% | 0.338537% | -0.079599% | 0.946579% |
| alert-2:line-11 | IWM | 2026-10-19 | 0.310605% | -2.382152% | -5.007353% | -6.831061% | 1.423411% |
| alert-3:line-15 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-15 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-15 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-15 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-4:line-21 | SPY | 2026-10-21 | 0.525323% | 0.453482% | 0.687670% | 4.350350% | 0.914974% |
| alert-4:line-21 | QQQ | 2026-10-21 | 1.054861% | -0.514439% | -2.159982% | 7.359102% | 1.553562% |
| alert-4:line-21 | RSP | 2026-10-21 | 0.361345% | 2.145316% | 2.522361% | -0.482337% | 0.930774% |
| alert-4:line-21 | IWM | 2026-10-21 | 0.253826% | 1.883038% | -1.929625% | -5.757235% | 1.403356% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLE. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | -0.053183062077 | AVAILABLE |
| close_sma50 | -0.018389105407 | AVAILABLE |
| close_sma150 | 0.265326352665 | AVAILABLE |
| close_sma200 | 0.40300797012 | AVAILABLE |
| sma50_slope20 | 0.107740404099 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-14', 'confirmed_session': '2026-10-19', 'price': 59.16} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-09-29', 'confirmed_session': '2026-10-02', 'price': 51.33} | AVAILABLE |
| realized_volatility20 | 0.022846905423 | AVAILABLE |
| Relative / SPY, 20 sessions | -0.039521437571 | AVAILABLE |
| Relative / QQQ, 20 sessions | -0.011566531874 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.056709695585 | AVAILABLE |
| Relative / IWM, 20 sessions | -0.013888250378 | AVAILABLE |
| Relative / sector, 20 sessions | -0.11506753143 | AVAILABLE |

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
