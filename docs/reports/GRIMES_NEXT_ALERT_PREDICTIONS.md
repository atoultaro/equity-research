# Grimes next-alert predictions — PR9C

**Unevaluated forward registration.** No genuine later source alert has been imported or scored. The target is a complete alert published strictly after registration, not an already-past October27 alert. The predictor uses the last verified seven-alert ledger and October26 market observations; these are stale inputs, not a claim about current broker positions or today’s market.

Registered: **2026-10-28T23:02:03.944237-04:00**. Information cutoff: **2026-10-26T18:11:00-04:00**. Last admitted market session: **2026-10-26**. Target deadline: **2026-11-04T23:59:59.999999-05:00** (five following XNYS sessions). All displayed clocks are America/New_York; machine artifacts retain aware timestamps.

Prediction bundle SHA256: `36b732cdb82e74a9c90f8add9d6e66015f31bcf9da156cb6213a858bf7676135`. Unobserved completed sessions between market end and registration: 2026-10-27, 2026-10-28. No missing price is forward filled. All confidences are LOW_HEURISTIC_NOT_A_CALIBRATED_PROBABILITY.

## Predictions for every source-open episode

The source OPEN/ENTERABLE/UNDERWAY columns are authoritative as of the information cutoff. A predicted DROP is a hypothesis about a later report, never an alteration to that ledger. CONTINUATION is a broad set including omission, continued management or UNDERWAY. ABSTAIN can carry a predeclared time/next-Open condition; it is not a conveniently correct forecast.

| Episode | Direction | Source status | Reported stop | A | B | C | D | E: action; direction; level; interval | All model actions timing-stable? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CDE | SHORT | OPEN / UNDERWAY | 13.90 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 13.9000; [13.9, 13.9] | yes |
| ELF | LONG | OPEN / ENTERABLE | 109.20 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 109.2000; [109.2, 109.2] | yes |
| HUM | LONG | OPEN / ENTERABLE | 408.10 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 408.1000; [408.1, 408.1] | yes |
| SIG | LONG | OPEN / ENTERABLE | 112.50 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 112.5000; [112.5, 112.5] | yes |
| OMER | SHORT | OPEN / ENTERABLE | 17.35 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 17.3500; [17.35, 17.35] | yes |
| ABBV | LONG | OPEN / ENTERABLE | 276.30 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 276.3000; [276.3, 276.3] | yes |
| CNQ | LONG | OPEN / ENTERABLE | 53.30 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 53.3000; [53.3, 53.3] | yes |
| EBAY | LONG | OPEN / ENTERABLE | 117.50 | DROPPED | DROPPED | DROPPED | ABSTAIN | NOT_MENTIONED; NO_ADJUSTMENT; 117.5000; [117.5, 117.5] | yes |
| GTLB | LONG | OPEN / ENTERABLE | 52.10 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 52.1000; [52.1, 52.1] | yes |
| MMM | LONG | OPEN / ENTERABLE | 169.90 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 169.9000; [169.9, 169.9] | yes |
| SAIL | LONG | OPEN / ENTERABLE | 20.90 | ABSTAIN | ABSTAIN | ABSTAIN | ABSTAIN | NOT_MENTIONED; NO_ADJUSTMENT; 20.9000; [20.9, 20.9] | yes |
| SLB | LONG | OPEN / ENTERABLE | 51.10 | ABSTAIN | ABSTAIN | ABSTAIN | ABSTAIN | NOT_MENTIONED; NO_ADJUSTMENT; 51.1000; [51.1, 51.1] | yes |
| GE | SHORT | OPEN / ENTERABLE | 295.80 | ABSTAIN | ABSTAIN | ABSTAIN | ABSTAIN | NOT_MENTIONED; NO_ADJUSTMENT; 295.8000; [295.8, 295.8] | yes |
| SCCO | SHORT | OPEN / ENTERABLE | 191.70 | ABSTAIN | ABSTAIN | ABSTAIN | ABSTAIN | NOT_MENTIONED; NO_ADJUSTMENT; 191.7000; [191.7, 191.7] | yes |

## Price-structure evidence and conditions

| Episode | Feature session | Close | ATR14 | SMA20 | SMA50 | Opening-reference progress / ATR | Stop anchor | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CDE | 2026-10-26 | 13.6400 | 0.8016 | 16.0410 | 18.6128 | 2.3689 | confirmed_swing_high | Fixed no-change baseline |
| ELF | 2026-10-26 | 112.9400 | 3.7907 | 108.9125 | 104.1498 | -0.4692 | confirmed_swing_low | Fixed no-change baseline |
| HUM | 2026-10-26 | 417.2200 | 19.5879 | 410.7500 | 398.3522 | -0.4949 | confirmed_swing_low | Fixed no-change baseline |
| SIG | 2026-10-26 | 115.0000 | 4.2371 | 109.2050 | 98.5056 | -0.1604 | confirmed_swing_low | Fixed no-change baseline |
| OMER | 2026-10-26 | 16.2900 | 0.8704 | 18.0645 | 18.4972 | 0.2917 | confirmed_swing_high | Fixed no-change baseline |
| ABBV | 2026-10-26 | 286.7400 | 6.9864 | 276.1120 | 266.8702 | 0.1515 | confirmed_swing_low | Fixed no-change baseline |
| CNQ | 2026-10-26 | 55.1100 | 1.4036 | 50.9960 | 50.3314 | 0.0356 | confirmed_swing_low | Fixed no-change baseline |
| EBAY | 2026-10-26 | 118.6200 | 3.5893 | 114.3640 | 109.4616 | -0.7963 | confirmed_swing_low | Fixed no-change baseline |
| GTLB | 2026-10-26 | 56.6500 | 2.7593 | 52.9240 | 48.9114 | 0.1300 | confirmed_swing_low | Fixed no-change baseline |
| MMM | 2026-10-26 | 172.7900 | 4.2350 | 165.9085 | 168.9416 | -0.1603 | confirmed_swing_low | Fixed no-change baseline |
| SAIL | 2026-10-26 | 21.7500 | 1.0850 | 20.0380 | 19.6524 | 0.0000 | — | NO_POST_ALERT_COMPLETED_SESSION |
| SLB | 2026-10-26 | 53.0800 | 1.5821 | 49.5970 | 52.4592 | 0.0000 | — | NO_POST_ALERT_COMPLETED_SESSION |
| GE | 2026-10-26 | 288.4300 | 8.7400 | 305.4530 | 321.9466 | -0.0000 | — | NO_POST_ALERT_COMPLETED_SESSION |
| SCCO | 2026-10-26 | 186.0100 | 7.9586 | 200.1865 | 201.1788 | -0.0000 | — | NO_POST_ALERT_COMPLETED_SESSION |

CDE remains source **SHORT / OPEN / UNDERWAY /13.90** and EBAY remains source **LONG / OPEN / ENTERABLE /117.50**. Hypothetical A/B closure for EBAY never replaces those source facts. For EBAY, C’s prior Close-breach commitment survives a later stop revision. D needs the missing next Open versus the then-known stop to decide whether its one permitted review retains exposure. That absence is unresolved evidence, not proof that D is correct.

The newly added SAIL/SLB/GE/SCCO episodes have no observed post-alert entry session in these inputs. A–D abstain rather than fabricate entries or future stop touches. E’s no-change projection is a low-confidence source-management hypothesis from pre-alert structure.

## Reveal protocol

Supply the original complete later alert and displayed publication metadata through the offline reveal command. A fresh score also needs an explicit operator attestation that it is the next complete alert after registration and that the source chain since the known ledger is complete. Missing attestations, unknown publication, window-boundary ambiguity or an outside-window alert remain unresolved or ineligible. Earlier October27–28 alerts, if they exist, may be imported as non-scoring backfill and advanced into a new history before a new forecast is sealed. They cannot be relabeled as outcomes of this forward registration.

Append evaluation to a new immutable directory. Do not update this forecast, its outcome field, or prior source artifacts. A later evaluation references the original prediction hash; observations and model results remain separate. No subscriber fetch, broker connection, order placement, account query or scheduled monitor is part of this workflow.

See [method and CLI](../GRIMES_PROSPECTIVE_PREDICTION_METHOD.md), [sealed prediction](../evidence/pr9c-next-alert-v1/prediction.json) and [validation record](../evidence/pr9c-validation-v1/validation.json).
