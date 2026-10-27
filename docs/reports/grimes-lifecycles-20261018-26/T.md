# Grimes lifecycle reconstruction: T

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| T | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | MODELED_CLOSED / HYPOTHETICAL_SHORT_FULL_1R |

## T (T-001)

Initial stop 24.00; latest source stop 22.20. Source CLOSED, setup UNDERWAY; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-19T13:30:00+00:00; modeled Open 23.25; original per-share R 0.75; hypothetical target 22.50. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 5 | OPEN_NEW_POSITION | 2026-10-18T15:20:00-04:00 | 2026-10-18T15:21:00-04:00 | 24.00 | ENTERABLE |
| 9 | STOP_CHANGED | 2026-10-19T18:19:00-04:00 | 2026-10-19T18:20:00-04:00 | 23.80 | ENTERABLE |
| 10 | SETUP_CHANGED | 2026-10-19T18:19:00-04:00 | 2026-10-19T18:20:00-04:00 | — | UNDERWAY |
| 25 | STOP_CHANGED | 2026-10-21T18:50:00-04:00 | 2026-10-21T18:51:00-04:00 | 22.20 | UNDERWAY |
| 45 | DROPPED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | — | UNDERWAY |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- HYPOTHETICAL_TARGET_REACHED: 2026-10-21; HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN.
- MODELED_CLOSED: 2026-10-21; HYPOTHETICAL_SHORT_FULL_1R.
- SOURCE_MODEL_CONFLICT: alert-4:line-15; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- POSSIBLE_TIME_STOP: 2026-10-20; .

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-1:line-12 | — | 24.00 | INITIAL | ENTERABLE |
| alert-2:line-13 | 24.00 | 23.80 | TIGHTENING | ENTERABLE |
| alert-4:line-15 | 23.80 | 22.20 | TIGHTENING | UNDERWAY |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-1:line-12 | 2026-10-16 | -0.255319% | 5.680794% | -7.716535% | 2.090592% | 0.8577680525165990739721042886 |
| alert-2:line-13 | 2026-10-19 | -1.023891% | 3.156959% | -8.840864% | -3.854123% | 0.9406494960808377714436911171 |
| alert-2:line-16 | 2026-10-19 | -1.023891% | 3.156959% | -8.840864% | -3.854123% | 0.9406494960808377714436911171 |
| alert-4:line-15 | 2026-10-21 | -6.447481% | -4.945770% | -13.399209% | -11.151663% | 0.3885167464112601817723954487 |
| alert-5:line-31 | 2026-10-22 | 3.788225% | -3.234043% | -10.648330% | -5.012531% | 0.6774193548385882761012834071 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-1:line-12 | SPY | 2026-10-16 | -1.106519% | -1.967710% | 0.204808% | 3.396191% | 0.902531% |
| alert-1:line-12 | QQQ | 2026-10-16 | -2.500000% | -5.519986% | -1.614804% | 2.578184% | 1.420219% |
| alert-1:line-12 | RSP | 2026-10-16 | -0.423256% | 0.492865% | 0.847897% | 1.023971% | 0.951869% |
| alert-1:line-12 | IWM | 2026-10-16 | -1.686782% | -3.047250% | -4.808166% | -7.412099% | 1.465337% |
| alert-2:line-13 | SPY | 2026-10-19 | 0.423190% | -1.493381% | -0.907563% | 3.728364% | 0.922771% |
| alert-2:line-13 | QQQ | 2026-10-19 | 1.205974% | -3.710257% | -3.116782% | 4.988089% | 1.497856% |
| alert-2:line-13 | RSP | 2026-10-19 | -0.322294% | 0.098504% | 0.338537% | -0.079599% | 0.946579% |
| alert-2:line-13 | IWM | 2026-10-19 | 0.310605% | -2.382152% | -5.007353% | -6.831061% | 1.423411% |
| alert-2:line-16 | SPY | 2026-10-19 | 0.423190% | -1.493381% | -0.907563% | 3.728364% | 0.922771% |
| alert-2:line-16 | QQQ | 2026-10-19 | 1.205974% | -3.710257% | -3.116782% | 4.988089% | 1.497856% |
| alert-2:line-16 | RSP | 2026-10-19 | -0.322294% | 0.098504% | 0.338537% | -0.079599% | 0.946579% |
| alert-2:line-16 | IWM | 2026-10-19 | 0.310605% | -2.382152% | -5.007353% | -6.831061% | 1.423411% |
| alert-4:line-15 | SPY | 2026-10-21 | 0.525323% | 0.453482% | 0.687670% | 4.350350% | 0.914974% |
| alert-4:line-15 | QQQ | 2026-10-21 | 1.054861% | -0.514439% | -2.159982% | 7.359102% | 1.553562% |
| alert-4:line-15 | RSP | 2026-10-21 | 0.361345% | 2.145316% | 2.522361% | -0.482337% | 0.930774% |
| alert-4:line-15 | IWM | 2026-10-21 | 0.253826% | 1.883038% | -1.929625% | -5.757235% | 1.403356% |
| alert-5:line-31 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-31 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-31 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-31 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | -0.17 | 0.18 | -0.2603938730853961474558173733 | 0.2757111597374782737767478071 | True |
| 3 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLC. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | -0.041618375303 | AVAILABLE |
| close_sma50 | -0.08393625421 | AVAILABLE |
| close_sma150 | -0.075299016472 | AVAILABLE |
| close_sma200 | -0.092966903663 | AVAILABLE |
| sma50_slope20 | 0.005354090898 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-16', 'confirmed_session': '2026-10-21', 'price': 23.85} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-09', 'confirmed_session': '2026-10-14', 'price': 21.96} | AVAILABLE |
| realized_volatility20 | 0.030734894263 | AVAILABLE |
| Relative / SPY, 20 sessions | -0.102717234602 | AVAILABLE |
| Relative / QQQ, 20 sessions | -0.060023527002 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.139076064439 | AVAILABLE |
| Relative / IWM, 20 sessions | -0.090367898377 | AVAILABLE |
| Relative / sector, 20 sessions | -0.051834215548 | AVAILABLE |

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
