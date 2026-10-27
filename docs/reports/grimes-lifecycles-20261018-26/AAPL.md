# Grimes lifecycle reconstruction: AAPL

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| AAPL | LONG | CLOSED | UNDERWAY | UNRESOLVED_BASIS | MODELED_CLOSED / ASSUMED_STOP_TRIGGERED |

## AAPL (AAPL-001)

Initial stop 339.00; latest source stop 344.70. Source CLOSED, setup UNDERWAY; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-19T13:30:00+00:00; modeled Open 340.78; original per-share R 1.78; hypothetical target 342.56. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 0 | OPEN_NEW_POSITION | 2026-10-18T15:20:00-04:00 | 2026-10-18T15:21:00-04:00 | 339.00 | ENTERABLE |
| 6 | STOP_CHANGED | 2026-10-19T18:19:00-04:00 | 2026-10-19T18:20:00-04:00 | 337.80 | ENTERABLE |
| 16 | STOP_CHANGED | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 336.25 | ENTERABLE |
| 32 | STOP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | 343.50 | ENTERABLE |
| 39 | SETUP_CHANGED | 2026-10-22T18:27:00-04:00 | 2026-10-22T18:28:00-04:00 | — | UNDERWAY |
| 55 | STOP_CHANGED | UNKNOWN | 2026-10-25T12:57:45+00:00 | 344.70 | UNDERWAY |
| 69 | DROPPED | 2026-10-26T18:10:00-04:00 | 2026-10-26T18:11:00-04:00 | — | UNDERWAY |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- HYPOTHETICAL_TARGET_REACHED: 2026-10-19; HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN.
- ASSUMED_STOP_TRIGGERED: 2026-10-26; TRIGGER_OBSERVED_UNDER_ASSUMPTION.
- MODELED_CLOSED: 2026-10-26; ASSUMED_STOP_TRIGGERED.
- POSSIBLE_TIME_STOP: 2026-10-20; .

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-1:line-7 | — | 339.00 | INITIAL | ENTERABLE |
| alert-2:line-10 | 339.00 | 337.80 | WIDENING | ENTERABLE |
| alert-3:line-14 | 337.80 | 336.25 | WIDENING | ENTERABLE |
| alert-5:line-14 | 336.25 | 343.50 | TIGHTENING | ENTERABLE |
| alert-6:line-18 | 343.50 | 344.70 | TIGHTENING | UNDERWAY |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-1:line-7 | 2026-10-16 | 0.426901% | 2.025903% | 2.180704% | 6.777343% | 0.6666666666666666666666666667 |
| alert-2:line-10 | 2026-10-19 | -0.151400% | 0.577763% | 1.168211% | 2.978800% | 0.8008903728436460966137527801 |
| alert-3:line-14 | 2026-10-20 | -1.003091% | -0.518651% | -0.073584% | 0.768751% | 0.5409582689335522757881092273 |
| alert-5:line-14 | 2026-10-22 | 1.229687% | 1.818713% | 3.661586% | 2.965788% | 0.7757689598496935539347335199 |
| alert-5:line-23 | 2026-10-22 | 1.229687% | 1.818713% | 3.661586% | 2.965788% | 0.7757689598496935539347335199 |
| alert-6:line-18 | 2026-10-23 | -0.140716% | 1.243231% | 1.952678% | 4.288756% | 0.4898383371824706622788536938 |
| alert-7:line-21 | 2026-10-26 | -1.098553% | 0.282848% | 1.628251% | 11.330161% | 0.1235202144293108563866173469 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-1:line-7 | SPY | 2026-10-16 | -1.106519% | -1.967710% | 0.204808% | 3.396191% | 0.902531% |
| alert-1:line-7 | QQQ | 2026-10-16 | -2.500000% | -5.519986% | -1.614804% | 2.578184% | 1.420219% |
| alert-1:line-7 | RSP | 2026-10-16 | -0.423256% | 0.492865% | 0.847897% | 1.023971% | 0.951869% |
| alert-1:line-7 | IWM | 2026-10-16 | -1.686782% | -3.047250% | -4.808166% | -7.412099% | 1.465337% |
| alert-2:line-10 | SPY | 2026-10-19 | 0.423190% | -1.493381% | -0.907563% | 3.728364% | 0.922771% |
| alert-2:line-10 | QQQ | 2026-10-19 | 1.205974% | -3.710257% | -3.116782% | 4.988089% | 1.497856% |
| alert-2:line-10 | RSP | 2026-10-19 | -0.322294% | 0.098504% | 0.338537% | -0.079599% | 0.946579% |
| alert-2:line-10 | IWM | 2026-10-19 | 0.310605% | -2.382152% | -5.007353% | -6.831061% | 1.423411% |
| alert-3:line-14 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-14 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-14 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-14 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-5:line-14 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-14 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-14 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-14 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-5:line-23 | SPY | 2026-10-22 | -1.180975% | -1.014525% | -0.419719% | 4.729526% | 0.956482% |
| alert-5:line-23 | QQQ | 2026-10-22 | -2.858522% | -3.232143% | -4.942653% | 6.458828% | 1.708681% |
| alert-5:line-23 | RSP | 2026-10-22 | 0.729321% | 1.497674% | 3.785789% | 1.154221% | 0.953494% |
| alert-5:line-23 | IWM | 2026-10-22 | 0.068721% | 0.578014% | -1.771640% | -4.123783% | 1.356954% |
| alert-6:line-18 | SPY | 2026-10-23 | -0.522279% | -0.429741% | -1.475335% | 2.464642% | 0.945526% |
| alert-6:line-18 | QQQ | 2026-10-23 | -0.009937% | -0.760778% | -5.386165% | 3.050252% | 1.711893% |
| alert-6:line-18 | RSP | 2026-10-23 | -0.769865% | 1.144379% | 2.572119% | 0.538583% | 0.962871% |
| alert-6:line-18 | IWM | 2026-10-23 | -0.332526% | 1.963467% | -2.205908% | -5.755494% | 1.338687% |
| alert-7:line-21 | SPY | 2026-10-26 | 0.710554% | -0.144818% | -0.031348% | 2.455055% | 0.947908% |
| alert-7:line-21 | QQQ | 2026-10-26 | 1.107325% | -0.857509% | -3.303328% | 3.518946% | 1.735167% |
| alert-7:line-21 | RSP | 2026-10-26 | 0.346356% | 1.822868% | 3.599695% | 1.060416% | 0.952644% |
| alert-7:line-21 | IWM | 2026-10-26 | 0.449683% | 2.104836% | -1.082066% | -4.879808% | 1.310517% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | AVAILABLE | -1.28 | 5.22 | -0.1913303437967115097159940209 | 0.7802690582959641255605381166 | True |
| 3 | AVAILABLE | 3.21 | 5.22 | 0.4798206278026905829596412556 | 0.7802690582959641255605381166 | False |
| 5 | AVAILABLE | 6.95 | 10.95 | 1.038863976083707025411061286 | 1.636771300448430493273542601 | False |

Sector context choice: XLK. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.013940913641 | AVAILABLE |
| close_sma50 | 0.041437026234 | AVAILABLE |
| close_sma150 | 0.123438045124 | AVAILABLE |
| close_sma200 | 0.166441711747 | AVAILABLE |
| sma50_slope20 | 0.02578611429 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-13', 'confirmed_session': '2026-10-16', 'price': 348.15} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-20', 'confirmed_session': '2026-10-23', 'price': 338.7} | AVAILABLE |
| realized_volatility20 | 0.010229103648 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.016601185505 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.051000497161 | AVAILABLE |
| Relative / RSP, 20 sessions | -0.019029440887 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.027399643687 | AVAILABLE |
| Relative / sector, 20 sessions | 0.061063953814 | AVAILABLE |

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
