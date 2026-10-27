# Grimes lifecycle reconstruction: ASST

Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.

Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.

The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.

Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.

Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.

| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |
|---|---|---|---|---|---|
| ASST | SHORT | CLOSED | ENTERABLE | UNRESOLVED_BASIS | MODELED_CLOSED / SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN |

## ASST (ASST-001)

Initial stop 28.45; latest source stop 28.45. Source CLOSED, setup ENTERABLE; SOURCE_OPEN_AND_CLOSURE_OBSERVED.

Scenario first eligible time: 2026-10-21T13:30:00+00:00; modeled Open 27.9; original per-share R 0.55; hypothetical target 27.35. Actual values remain unknown.

| Source order | Action | Publication | Effective bound | Stop | Availability |
|---|---|---|---|---|---|
| 14 | OPEN_NEW_POSITION | 2026-10-20T18:25:00-04:00 | 2026-10-20T18:26:00-04:00 | 28.45 | ENTERABLE |
| 27 | DROPPED | 2026-10-21T18:50:00-04:00 | 2026-10-21T18:51:00-04:00 | — | ENTERABLE |

Primary modeled events:

- UNRESOLVED_BASIS; no validated execution claim.

Conditional scenario (assumes unverified stop/native-bar unit compatibility):

- ASSUMED_STOP_TRIGGERED: 2026-10-21; CANDIDATE_ORDER_UNKNOWN.
- HYPOTHETICAL_TARGET_REACHED: 2026-10-21; CANDIDATE_ORDER_UNKNOWN.
- MODELED_CLOSED: 2026-10-21; SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN.

| Stop event | Previous | Reported | Change | Availability at revision |
|---|---|---|---|---|
| alert-3:line-10 | — | 28.45 | INITIAL | ENTERABLE |

| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |
|---|---|---|---|---|---|---|
| alert-3:line-10 | 2026-10-20 | 5.951449% | -1.920986% | -7.802385% | 121.985234% | 0.7170228445101069320953227945 |
| alert-4:line-22 | 2026-10-21 | 13.636364% | 24.594814% | 6.071059% | 156.677796% | 1.071547420964844283376845622 |

Market context at every source event (price-return fractions rendered as percentages):

| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |
|---|---|---|---|---|---|---|---|
| alert-3:line-10 | SPY | 2026-10-20 | 0.335299% | -1.151656% | -0.559880% | 4.053634% | 0.927397% |
| alert-3:line-10 | QQQ | 2026-10-20 | -0.101620% | -3.488575% | -3.990849% | 5.205829% | 1.551038% |
| alert-3:line-10 | RSP | 2026-10-20 | 1.152765% | 1.200188% | 1.437970% | 0.316014% | 0.962926% |
| alert-3:line-10 | IWM | 2026-10-20 | 1.658803% | -0.332490% | -3.979666% | -5.848213% | 1.478404% |
| alert-4:line-22 | SPY | 2026-10-21 | 0.525323% | 0.453482% | 0.687670% | 4.350350% | 0.914974% |
| alert-4:line-22 | QQQ | 2026-10-21 | 1.054861% | -0.514439% | -2.159982% | 7.359102% | 1.553562% |
| alert-4:line-22 | RSP | 2026-10-21 | 0.361345% | 2.145316% | 2.522361% | -0.482337% | 0.930774% |
| alert-4:line-22 | IWM | 2026-10-21 | 0.253826% | 1.883038% | -1.929625% | -5.757235% | 1.403356% |

Exploratory scenario windows; never a definitive time exit:

| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |
|---|---|---|---|---|---|---|
| 2 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 3 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |
| 5 | MODELED_CLOSED_BEFORE_OR_DURING_HORIZON | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | None |

Sector context choice: UNRESOLVED. Fixed agent selection; no historical GICS or ETF membership assertion.

Latest event stock structure and relative strength:

| Measurement | Value | Status |
|---|---|---|
| close_sma20 | 0.089382506111 | AVAILABLE |
| close_sma50 | 0.229704870831 | AVAILABLE |
| close_sma150 | 0.76463836869 | AVAILABLE |
| close_sma200 | 0.895973630244 | AVAILABLE |
| sma50_slope20 | 0.346914152132 | AVAILABLE |
| confirmed_swing_high | {'session_date': '2026-10-02', 'confirmed_session': '2026-10-07', 'price': 32.08} | AVAILABLE |
| confirmed_swing_low | {'session_date': '2026-10-15', 'confirmed_session': '2026-10-20', 'price': 22.48} | AVAILABLE |
| realized_volatility20 | 0.048692705814 | AVAILABLE |
| Relative / SPY, 20 sessions | 0.053466217386 | AVAILABLE |
| Relative / QQQ, 20 sessions | 0.084127545931 | AVAILABLE |
| Relative / RSP, 20 sessions | 0.034613897447 | AVAILABLE |
| Relative / IWM, 20 sessions | 0.081581052853 | AVAILABLE |

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
