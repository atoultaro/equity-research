# MarketLife current market-data audit

Latest eligible completed XNYS session: **2026-10-29**. This is derived from the actual audit clock using cash Close + 60 minutes, strictly before the cutoff; it is not a permanent October 29 end date. Sixty consecutive sessions are required for each active source setup and SPY.

Audit as of 2026-10-30T13:12:59.892784+00:00. Native current archive SHA256: `07882253d2207a3117a115d40e04f469b207eccfd99f8b67a0375377e4ec5184`. Public evidence SHA256: `97068d3bcf0d6216bf064f89765a12a9e72239129931022096be14e614d24080`. [Input registry](../evidence/pr9d-current-readiness-v3/manifest.json); [regression and replay record](../evidence/pr9d-validation-v2/validation.json).

The required list comes from the latest supplied reconciled ledger, with SPY added as benchmark. It is a conditional source snapshot until completeness is confirmed, not an assumed current universe or complete historical stock population. Historical setup episodes and all opportunity versions remain retained.

| Symbol | Qualified conId | Primary exchange | Last observed session | Missing required sessions | Last observed ATR14 (stale if older) | ATR session |
| --- | --- | --- | --- | --- | --- | --- |
| CNQ | 11926119 | NYSE | 2026-10-29 | 0 | 1.334 | 2026-10-29 |
| CRWV | 771759702 | NASDAQ | 2026-10-29 | 0 | 6.517 | 2026-10-29 |
| DUK | 110176011 | NYSE | 2026-10-29 | 0 | 2.169 | 2026-10-29 |
| FCX | 7089 | NYSE | 2026-10-29 | 0 | 2.431 | 2026-10-29 |
| MMM | 9720 | NYSE | 2026-10-29 | 0 | 4.111 | 2026-10-29 |
| NBIS | 88819736 | NASDAQ | 2026-10-29 | 0 | 16.219 | 2026-10-29 |
| PAA | 6608417 | NASDAQ | 2026-10-29 | 0 | 0.464 | 2026-10-29 |
| SAIL | 760966616 | NASDAQ | 2026-10-29 | 0 | 1.116 | 2026-10-29 |
| SIG | 53747825 | NYSE | 2026-10-29 | 0 | 4.335 | 2026-10-29 |
| SLB | 12200 | NYSE | 2026-10-29 | 0 | 1.593 | 2026-10-29 |
| SPY | 756733 | ARCA | 2026-10-29 | 0 | 7.109 | 2026-10-29 |

There are 11 recorded qualified identities and 0 missing/incompatible identities. 0 instruments lack required completed sessions. The machine coverage audit lists every missing date. ATR values from a session older than 2026-10-29 are explicitly stale descriptive evidence; no current feature or forecast substitutes them for missing sessions.

Acquisition status: **ATTEMPTS_RETAINED**. See retained native status/error diagnostics.

The operator explicitly authorized the non-paper TWS on 127.0.0.1:7496 with Read-Only API. The acquisition recorded non-paper mode without claiming paper authentication. Account mode was supplied by the operator; no account query established or stored account identifiers. All broker interactions were contract qualification and historical data requests, followed by disconnect.

The earlier SPY smoke/context panels and PR9C captures remain intact. The new live run captured 11 instruments over 2026-07-30–2026-10-29: 715 selected canonical observations and 1012 native returned rows across 44 historical requests, including explicitly excluded over-return. The 60 required sessions are complete for every selected instrument and benchmark. Historical data access succeeded for this bounded scope; no broader entitlement claim is made.

## Basis and intake checks

Existing prices use IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED and IBKR_NATIVE_UNITS_UNVERIFIED. These are native research conventions, not raw execution prices or verified share volumes. Corporate-action completeness and full historical ticker/listing identity remain UNKNOWN. Qualified conId, STK, USD, SMART, primary exchange and symbol must reconcile; a changed instrument, ambiguous match or inconsistent basis fails.

Native acquisition reuses the pinned ib_async 2.1.0 low-level market-only backend and IBKRDailyProvider. It requests bounded daily TRADES/RTH history, conservatively paces requests, retains raw client returns and safe error diagnostics, and disconnects. It does not request positions, balances, executions or orders. Every imported response is independently normalized from its frozen native bytes. Duplicate, off-calendar, future, malformed and incompatible rows cannot be promoted. Conflicting overlap is retained as a blocker; existing canonical rows are never replaced or rescaled.

Current ATR14, SMA10/20/50, confirmed swings, previous-20 extremes, volatility, compression and relative SPY diagnostics are recomputed by the existing Evidence/Panel/shared-ATR implementation. The registration audit records actual per-symbol availability and feature sessions. A confirmed swing can legitimately be unavailable even with complete observations; absence of a pivot is not a missing-price substitution.

## Overlapping native revisions

| Symbol | Session | Field | Earlier capture | Fresh capture | Retained canonical value |
| --- | --- | --- | --- | --- | --- |
| CNQ | 2026-10-26 | volume | 26070.0 | 26076.0 | 26070.0 |
| MMM | 2026-10-26 | volume | 10871.0 | 10872.0 | 10871.0 |
| SAIL | 2026-10-26 | volume | 23820.0 | 23981.0 | 23820.0 |
| SIG | 2026-10-26 | high | 118.85 | 118.86 | 118.85 |
| SLB | 2026-10-26 | volume | 74502.0 | 74532.0 | 74502.0 |
| SPY | 2026-10-26 | volume | 518208.0 | 517926.0 | 518208.0 |

The audit identifies 6 changed fields in the overlapping native observations. Both vintages and their source hashes are retained. Earlier canonical rows remain unchanged, no adjustment policy is changed, and no revision conflict is waived. Current features can be calculated on the retained series, but they are conditional on that unresolved vintage choice and cannot establish forecast readiness.
