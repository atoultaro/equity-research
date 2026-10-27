# Grimes lifecycle reconstruction: CDE

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| CDE | SHORT | OPEN | UNDERWAY | UNRESOLVED_BASIS | MODELED_CLOSED / HYPOTHETICAL_SHORT_FULL_1R |

## CDE (CDE-001)

Initial stop 16.40; latest source stop 13.90. Source OPEN, setup UNDERWAY; RIGHT_CENSORED_SOURCE_OPEN.

Scenario first eligible time: 2026-10-19T13:30:00+00:00; modeled Open 15.46; original per-share R 0.94; hypothetical target 14.52. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 4 | OPEN_NEW_POSITION | 2026-10-18T15:20:00-04:00 | 2026-10-18T15:21:00-04:00 | 16.40 | ENTERABLE |
| 8 | STOP_CHANGED | 2026-10-19T18:19:00-04:00 | 2026-10-19T18:20:00-04:00 | 16.24 | ENTERABLE |
| 37 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 14.30 | ENTERABLE |
| 43 | SETUP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | — | UNDERWAY |
| 57 | STOP_CHANGED | UNKNOWN | 2026-10-25T12:57:45+00:00 | 13.90 | UNDERWAY |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- HYPOTHETICAL_TARGET_REACHED: 2026-10-22; HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN.
- MODELED_CLOSED: 2026-10-22; HYPOTHETICAL_SHORT_FULL_1R.
- SOURCE_MODEL_CONFLICT: alert-5:line-19; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: alert-5:line-27; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: alert-6:line-20; SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY.
- SOURCE_MODEL_CONFLICT: final reconciliation; SOURCE_NOT_REPORTED_DROPPED_MODEL_CLOSED.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-1:line-11 | — | 16.40 | INITIAL | ENTERABLE |
| alert-2:line-12 | 16.40 | 16.24 | TIGHTENING | ENTERABLE |
| alert-5:line-19 | 16.24 | 14.30 | TIGHTENING | ENTERABLE |
| alert-6:line-20 | 14.30 | 13.90 | TIGHTENING | UNDERWAY |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-1:line-11 | 2026-10-16 | 0.389358% | -9.690601% | -21.710526% | 1.509186% | 1.203883495145631067961165049 |
| alert-2:line-12 | 2026-10-19 | -0.904977% | -8.532220% | -21.465164% | 1.321877% | 1.233301064859870919857668900 |
| alert-5:line-19 | 2026-10-22 | -8.261732% | -9.928618% | -26.715945% | -5.126452% | 0.5107580587720109375292117146 |
| alert-5:line-27 | 2026-10-22 | -8.261732% | -9.928618% | -26.715945% | -5.126452% | 0.5107580587720109375292117146 |
| alert-6:line-20 | 2026-10-23 | -3.097983% | -13.057531% | -30.020812% | -12.662338% | 0.5636423823281667438206034552 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-1:line-11 | SPY | 2026-10-16 | -1.106519% | -1.967710% | 0.204808% | 3.396191% | 0.902531% |
| alert-1:line-11 | QQQ | 2026-10-16 | -2.500000% | -5.519986% | -1.614804% | 2.578184% | 1.420219% |
| alert-1:line-11 | RSP | 2026-10-16 | -0.423256% | 0.492865% | 0.847897% | 1.023971% | 0.951869% |
| alert-1:line-11 | IWM | 2026-10-16 | -1.686782% | -3.047250% | -4.808166% | -7.412099% | 1.465337% |
| alert-2:line-12 | SPY | 2026-10-19 | 0.423190% | -1.493381% | -0.907563% | 3.728364% | 0.922771% |
| alert-2:line-12 | QQQ | 2026-10-19 | 1.205974% | -3.710257% | -3.116782% | 4.988089% | 1.497856% |
| alert-2:line-12 | RSP | 2026-10-19 | -0.322294% | 0.098504% | 0.338537% | -0.079599% | 0.946579% |
| alert-2:line-12 | IWM | 2026-10-19 | 0.310605% | -2.382152% | -5.007353% | -6.831061% | 1.423411% |
| alert-5:line-19 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-19 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-19 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-19 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-5:line-27 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-27 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-27 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-27 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-6:line-20 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-20 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-20 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-20 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | 0.33 | 0.48 | 0.4271844660194174757281553398 | 0.6213592233009708737864077670 | False |
| 3 | AVAILABLE | 0.33 | 0.605 | 0.4271844660194174757281553398 | 0.7831715210355987055016181230 | False |
| 5 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: XLB. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | -0.172435009998 | AVAILABLE |
| close_sma50 | -0.281371218517 | AVAILABLE |
| close_sma150 | -0.248978163598 | AVAILABLE |
| close_sma200 | -0.295130636662 | AVAILABLE |
| sma50_slope20 | 0.003861790798 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-09', 'confirmed_session': '2026-10-14', 'price': 17.495} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-15', 'confirmed_session': '2026-10-20', 'price': 14.675} | AVAILABLE |
| realized_volatility20 | 0.030966035668 | AVAILABLE |
| Relative / SPY, 20 sessions | -0.289729240229 | AVAILABLE |
| Relative / QQQ, 20 sessions | -0.26037044686 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.317756236649 | AVAILABLE |
| Relative / IWM, 20 sessions | -0.284423146409 | AVAILABLE |
| Relative / sector, 20 sessions | -0.320802264743 | AVAILABLE |

Full MA, swing, volatility, sector and relative-strength measurements are retained in the event-context JSON. These are agent-selected diagnostics, not attributed Grimes entry/exit rules. Earnings completeness remains unknown. Exploratory 2/3/5-session progress/MFE flags never create a definitive time exit.

## Comparison and limits

```json
{
  "conditional_basis_model": "MODELED_CLOSED",
  "model": "UNRESOLVED_BASIS",
  "source": "OPEN"
}
```

Source closures do not establish which stop, target or time rule was executed. Right-censored positions and unresolved basis/timing are not successful trades. This selected, short observation period cannot establish a trading edge.
