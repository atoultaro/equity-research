# Grimes trade lifecycle evidence: October 18–26, 2026

Seven original alerts reconcile to 26 new source positions, 27 stop revisions, seven underway transitions and 12 source closures. Final source states are 12 CLOSED and 14 not reported dropped. PLTR and PEP remain in the originals and are excluded from structured analysis.

See [method, CLI and limitations](../GRIMES_TRADE_LIFECYCLES.md). All tables derive from the local immutable `study-v5`. Actual entries, fills, quantities and realized profitability remain unknown.

## Findings

- Source directions: 14 LONG and 12 SHORT. Final setup availability: 19 ENTERABLE and seven UNDERWAY. Continued enterability and stop revisions do not create additional positions.
- Of 27 revisions, 16 tighten and 11 widen. All 11 widenings occur while enterable; four tightenings occur after underway. The ledger permits widening.
- EBAY source OPEN versus modeled CLOSED is an explicit conflict under the declared email-availability and session-quote-scale assumptions. Its original 119.20 stop is crossed by October 26 Low 117.87; the later 117.50 revision cannot rescue or re-enter the model. Actual fill is unknown.
- Primary model states: one EBAY closure, 21 active episodes with unresolved stop/price basis, and four right-censored before eligible entry. These are evidence classifications, not performance results.
- The separate conditional basis scenario has 14 modeled closures, eight open episodes and four not yet active. Ten stop-trigger closures and three full SHORT 1R closures have daily observations with resolved order under its assumptions. ASST later has a source closure with an unresolved earlier stop/target order.
- AAPL hypothetically touches +1R on October 19 and retains an unspecified long runner until a subsequent assumed stop trigger. No exact partial size, runner quantity or realized return is inferred.
- ASST touches both its initial stop and hypothetical target in the October 21 bar. Candidate observations are counted separately; its later DROP cannot identify which exit happened first.
- Nonpositive progress flags occur in six of nine available 2-session windows and three of six available 3-session windows in the conditional scenario. The one available 5-session window has no flag. These agent-defined exploratory diagnostics are not verified Grimes time stops and never close positions.

## All 26 source dossiers

Model columns contain analytical outcomes, not confirmed Grimes executions.

| Symbol / dossier | conId | Direction | Source | Setup | Primary model | Conditional basis outcome |
|---|---|---|---|---|---|---|
| [AAPL](grimes-lifecycles-20261018-26/AAPL.md) | 265598 | LONG | CLOSED | UNDERWAY | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [CLMT](grimes-lifecycles-20261018-26/CLMT.md) | 715002751 | LONG | CLOSED | ENTERABLE | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [TEVA](grimes-lifecycles-20261018-26/TEVA.md) | 922990633 | LONG | CLOSED | ENTERABLE | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [CAT](grimes-lifecycles-20261018-26/CAT.md) | 5437 | SHORT | CLOSED | ENTERABLE | UNRESOLVED_BASIS | HYPOTHETICAL_SHORT_FULL_1R |
| [CDE](grimes-lifecycles-20261018-26/CDE.md) | 60532895 | SHORT | OPEN | UNDERWAY | UNRESOLVED_BASIS | HYPOTHETICAL_SHORT_FULL_1R |
| [T](grimes-lifecycles-20261018-26/T.md) | 37018770 | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | HYPOTHETICAL_SHORT_FULL_1R |
| [ELF](grimes-lifecycles-20261018-26/ELF.md) | 248682005 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [HUM](grimes-lifecycles-20261018-26/HUM.md) | 8251 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [SIG](grimes-lifecycles-20261018-26/SIG.md) | 53747825 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [ASST](grimes-lifecycles-20261018-26/ASST.md) | 852120292 | SHORT | CLOSED | ENTERABLE | UNRESOLVED_BASIS | SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN |
| [OMER](grimes-lifecycles-20261018-26/OMER.md) | 69342644 | SHORT | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [GME](grimes-lifecycles-20261018-26/GME.md) | 36285627 | LONG | CLOSED | ENTERABLE | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [AAOI](grimes-lifecycles-20261018-26/AAOI.md) | 135423662 | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [AMD](grimes-lifecycles-20261018-26/AMD.md) | 4391 | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [ANET](grimes-lifecycles-20261018-26/ANET.md) | 740948854 | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [SNDK](grimes-lifecycles-20261018-26/SNDK.md) | 760250490 | SHORT | CLOSED | UNDERWAY | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [ABBV](grimes-lifecycles-20261018-26/ABBV.md) | 118089500 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [CNQ](grimes-lifecycles-20261018-26/CNQ.md) | 11926119 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [EBAY](grimes-lifecycles-20261018-26/EBAY.md) | 4347086 | LONG | OPEN | ENTERABLE | MODELED_CLOSED | ASSUMED_STOP_TRIGGERED |
| [GTLB](grimes-lifecycles-20261018-26/GTLB.md) | 520512263 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [MMM](grimes-lifecycles-20261018-26/MMM.md) | 9720 | LONG | OPEN | ENTERABLE | UNRESOLVED_BASIS | MODELED_OPEN |
| [SNOW](grimes-lifecycles-20261018-26/SNOW.md) | 444884769 | SHORT | CLOSED | ENTERABLE | UNRESOLVED_BASIS | ASSUMED_STOP_TRIGGERED |
| [SAIL](grimes-lifecycles-20261018-26/SAIL.md) | 760966616 | LONG | OPEN | ENTERABLE | NOT_YET_ACTIVE_RIGHT_CENSORED | NOT_YET_ACTIVE_RIGHT_CENSORED |
| [SLB](grimes-lifecycles-20261018-26/SLB.md) | 12200 | LONG | OPEN | ENTERABLE | NOT_YET_ACTIVE_RIGHT_CENSORED | NOT_YET_ACTIVE_RIGHT_CENSORED |
| [GE](grimes-lifecycles-20261018-26/GE.md) | 498843743 | SHORT | OPEN | ENTERABLE | NOT_YET_ACTIVE_RIGHT_CENSORED | NOT_YET_ACTIVE_RIGHT_CENSORED |
| [SCCO](grimes-lifecycles-20261018-26/SCCO.md) | 1812968 | SHORT | OPEN | ENTERABLE | NOT_YET_ACTIVE_RIGHT_CENSORED | NOT_YET_ACTIVE_RIGHT_CENSORED |

## Market evolution at alert availability bounds

Completed RTH price returns, not total returns. All four fixed ETFs are context proxies. The weekly row uses the separately disclosed email bound; its original publication date remains null. Every action links to its own cutoff in the frozen event tables.

| Availability bound | Session | ETF | Daily | 5 sessions | 20 sessions | 60 sessions | ATR14 / Close |
|---|---|---|---|---|---|---|
| 2026-10-18T15:21:00-04:00 | 2026-10-16 | IWM | -1.6868% | -3.0473% | -4.8082% | -7.4121% | 1.4653% |
| 2026-10-18T15:21:00-04:00 | 2026-10-16 | QQQ | -2.5000% | -5.5200% | -1.6148% | 2.5782% | 1.4202% |
| 2026-10-18T15:21:00-04:00 | 2026-10-16 | RSP | -0.4233% | 0.4929% | 0.8479% | 1.0240% | 0.9519% |
| 2026-10-18T15:21:00-04:00 | 2026-10-16 | SPY | -1.1065% | -1.9677% | 0.2048% | 3.3962% | 0.9025% |
| 2026-10-19T18:20:00-04:00 | 2026-10-19 | IWM | 0.3106% | -2.3822% | -5.0074% | -6.8311% | 1.4234% |
| 2026-10-19T18:20:00-04:00 | 2026-10-19 | QQQ | 1.2060% | -3.7103% | -3.1168% | 4.9881% | 1.4979% |
| 2026-10-19T18:20:00-04:00 | 2026-10-19 | RSP | -0.3223% | 0.0985% | 0.3385% | -0.0796% | 0.9466% |
| 2026-10-19T18:20:00-04:00 | 2026-10-19 | SPY | 0.4232% | -1.4934% | -0.9076% | 3.7284% | 0.9228% |
| 2026-10-20T18:26:00-04:00 | 2026-10-20 | IWM | 1.6588% | -0.3325% | -3.9797% | -5.8482% | 1.4784% |
| 2026-10-20T18:26:00-04:00 | 2026-10-20 | QQQ | -0.1016% | -3.4886% | -3.9908% | 5.2058% | 1.5510% |
| 2026-10-20T18:26:00-04:00 | 2026-10-20 | RSP | 1.1528% | 1.2002% | 1.4380% | 0.3160% | 0.9629% |
| 2026-10-20T18:26:00-04:00 | 2026-10-20 | SPY | 0.3353% | -1.1517% | -0.5599% | 4.0536% | 0.9274% |
| 2026-10-21T18:51:00-04:00 | 2026-10-21 | IWM | 0.2538% | 1.8830% | -1.9296% | -5.7572% | 1.4034% |
| 2026-10-21T18:51:00-04:00 | 2026-10-21 | QQQ | 1.0549% | -0.5144% | -2.1600% | 7.3591% | 1.5536% |
| 2026-10-21T18:51:00-04:00 | 2026-10-21 | RSP | 0.3613% | 2.1453% | 2.5224% | -0.4823% | 0.9308% |
| 2026-10-21T18:51:00-04:00 | 2026-10-21 | SPY | 0.5253% | 0.4535% | 0.6877% | 4.3503% | 0.9150% |
| 2026-10-22T18:28:00-04:00 | 2026-10-22 | IWM | 0.0687% | 0.5780% | -1.7716% | -4.1238% | 1.3570% |
| 2026-10-22T18:28:00-04:00 | 2026-10-22 | QQQ | -2.8585% | -3.2321% | -4.9427% | 6.4588% | 1.7087% |
| 2026-10-22T18:28:00-04:00 | 2026-10-22 | RSP | 0.7293% | 1.4977% | 3.7858% | 1.1542% | 0.9535% |
| 2026-10-22T18:28:00-04:00 | 2026-10-22 | SPY | -1.1810% | -1.0145% | -0.4197% | 4.7295% | 0.9565% |
| 2026-10-25T12:57:45+00:00 | 2026-10-23 | IWM | -0.3325% | 1.9635% | -2.2059% | -5.7555% | 1.3387% |
| 2026-10-25T12:57:45+00:00 | 2026-10-23 | QQQ | -0.0099% | -0.7608% | -5.3862% | 3.0503% | 1.7119% |
| 2026-10-25T12:57:45+00:00 | 2026-10-23 | RSP | -0.7699% | 1.1444% | 2.5721% | 0.5386% | 0.9629% |
| 2026-10-25T12:57:45+00:00 | 2026-10-23 | SPY | -0.5223% | -0.4297% | -1.4753% | 2.4646% | 0.9455% |
| 2026-10-26T18:11:00-04:00 | 2026-10-26 | IWM | 0.4497% | 2.1048% | -1.0821% | -4.8798% | 1.3105% |
| 2026-10-26T18:11:00-04:00 | 2026-10-26 | QQQ | 1.1073% | -0.8575% | -3.3033% | 3.5189% | 1.7352% |
| 2026-10-26T18:11:00-04:00 | 2026-10-26 | RSP | 0.3464% | 1.8229% | 3.5997% | 1.0604% | 0.9526% |
| 2026-10-26T18:11:00-04:00 | 2026-10-26 | SPY | 0.7106% | -0.1448% | -0.0313% | 2.4551% | 0.9479% |

## Immutable provenance

Local root: `runs/grimes-lifecycle-20261018-26-v1/`. Subscriber originals and raw prices remain local; these public dossiers contain derived facts. All 74 operator action lines, including the two excluded drops, reconcile numerically to the seven original emails. The weekly original publication date remains unresolved.

| Local artifact | SHA-256 bundle |
|---|---|
| source-alerts-v1 | `a37064614b310d2a92a98283d846c4671aecbbf9d9e799a89f79a1a01e5e9966` |
| operator-corroboration-v1 | `e0c565d4777418aa196a1592c2d02a013990c48f3e0c401e1935432a86a9d2da` |
| audit-report-1-v1 | `65bc1bf21501833dec07455bcda5f995198ee0098c9255210c3e5fa657a676f3` |
| audit-report-2-v1 | `1ecf8888edcc62a73d68a4b4c3883d84ffe1152df89e27ea8435804eb6b44013` |
| audit-report-3-v1 | `95884ef0a2791e9e3693cc4dbcbf7bd5aee00f518a28cfe656d2eee683145b7a` |
| inputs-v2 | `8a51b7b0437059034bfa20947a3b62f5211e96c35e4cf40d2193ed6730558d35` |
| study-v5 | `4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604` |

Reused PR14 source report: `b2b8f5a15856a9ed4521b2c07f270e269501835b35ca3383305260c568b26043`. Reused PR15 source report: `00f001c3a9cd76dc10c1f4c282ea6177399900f6e556df9f8b386061c8d3e02b`. Prior dated-event input: `01968c15438d78b47217d1402e95cb4b097eea297c0b5aef2921e8903e0e8a49`.

New live checkpoints record 24 successful contract qualifications and 30 successful historical-window responses, including bounded boundary checks. Every stock covers the alert period. Older TEVA/SNDK coverage remains explicitly partial; no exhaustion claim is invented. No account queries or trading actions were used.

`inputs-v1`, `study-v1`, `study-v2`, `study-v3` and `study-v4` remain preserved as earlier development freezes. The authoritative study is `study-v5`; older source-code identities are not represented as compatible with the final implementation.

## Validation

- Complete offline suite: `.venv/bin/python -m pytest -q` → **507 passed in 143.76s (0:02:23)**, exit 0. This includes 29 new lifecycle cases and all previous regressions.
- Final `offline-replay-v5` is byte-identical to `study-v5` with socket connect/connect_ex/create_connection blocked. Bundle SHA-256: `4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604`.
- All 26 public dossiers are byte-identical to their frozen generated versions.
- **7,057 prior frozen files checked; zero changed.**
- `git diff --check` passed. Local immutable verification bundle: `verification-v1`, SHA-256 `1c6fc2763a9fae225141135fea9a0fa3f293ea28b043a8abd557e64137f82503`.
- Tests cover exact scope/source inventory, stop widening and underway, fixed original R, directional touches, EBAY/no rescue/no re-entry, after-hours activation, partial candles and same-bar ordering, quote-basis mismatches, LONG partial/SHORT full exits, exploratory windows, future poisoning/missing sessions, and resealed semantic corruption.

## Limits

The weekly email supplies a separate modeling bound, not a resolved publication date. EBAY unit evidence is a single-session numerical corroboration, not a full corporate-action audit. Other stop scales remain unverified; conditional outcomes must stay separate. TEVA has only 31 sessions under its current ordinary-share contract. ASST has business/split and sector-proxy uncertainty. Five reused dated event records lack verified publication clocks; earnings/action completeness stays unknown. No ES prices, inferred fills, portfolio curve, prediction model or strategy-profitability claim is included.
