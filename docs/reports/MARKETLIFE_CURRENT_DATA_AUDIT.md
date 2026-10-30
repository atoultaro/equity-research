# MarketLife current market-data audit

Latest eligible completed XNYS session: **2026-10-29**. This is derived from the actual audit clock using cash Close + 60 minutes, strictly before the cutoff; it is not a permanent October 29 end date. Sixty consecutive sessions are required for each active source setup and SPY.

Audit as of 2026-10-30T04:29:06.369653+00:00. Native current archive SHA256: `7bad57dffed892962140f42d39370fe9002a65c724126506f27c9e54b7c35add`. Public evidence SHA256: `2b4f2a01a7964dcd0e5d9ba6a817b18e93c6091d2b91702cafcb855f9431501e`. [Input registry](../evidence/pr9d-current-readiness-v2/manifest.json); [regression and replay record](../evidence/pr9d-validation-v1/validation.json).

The required list comes from the latest supplied reconciled ledger, with SPY added as benchmark. It is a conditional source snapshot until completeness is confirmed, not an assumed current universe or complete historical stock population. Historical setup episodes and all opportunity versions remain retained.

| Symbol | Qualified conId | Primary exchange | Last observed session | Missing required sessions | Last observed ATR14 (stale if older) | ATR session |
| --- | --- | --- | --- | --- | --- | --- |
| CNQ | 11926119 | NYSE | 2026-10-26 | 3 | 1.404 | 2026-10-26 |
| CRWV | MISSING | MISSING | NONE | 60 | UNAVAILABLE | UNAVAILABLE |
| DUK | MISSING | MISSING | NONE | 60 | UNAVAILABLE | UNAVAILABLE |
| FCX | MISSING | MISSING | NONE | 60 | UNAVAILABLE | UNAVAILABLE |
| MMM | 9720 | NYSE | 2026-10-26 | 3 | 4.235 | 2026-10-26 |
| NBIS | MISSING | MISSING | NONE | 60 | UNAVAILABLE | UNAVAILABLE |
| PAA | MISSING | MISSING | NONE | 60 | UNAVAILABLE | UNAVAILABLE |
| SAIL | 760966616 | NASDAQ | 2026-10-26 | 3 | 1.085 | 2026-10-26 |
| SIG | 53747825 | NYSE | 2026-10-26 | 3 | 4.237 | 2026-10-26 |
| SLB | 12200 | NYSE | 2026-10-26 | 3 | 1.582 | 2026-10-26 |
| SPY | 756733 | ARCA | 2026-10-26 | 3 | 7.255 | 2026-10-26 |

There are 6 recorded qualified identities and 5 missing/incompatible identities. 11 instruments lack required completed sessions. The machine coverage audit lists every missing date. ATR values from a session older than 2026-10-29 are explicitly stale descriptive evidence; no current feature or forecast substitutes them for missing sessions.

Acquisition status: **NOT_ATTEMPTED_CURRENT_PAPER_CONFIGURATION_UNCONFIRMED**. Current paper-authenticated local TWS with socket clients and Read-Only API has not been confirmed for PR9D; previous confirmation was non-paper 7496.

The pre-acquisition audit is required before connecting. PR9D specifies a paper-authenticated local TWS with socket clients and Read-Only API enabled. The previous non-paper 7496 confirmation does not establish that current prerequisite. See the access-status record for actual attempts; a missing confirmation is an access/configuration blocker, not evidence that IBKR lacks the requested history.

Existing declared research datasets additionally include a real SPY five-session smoke capture and the SPY market-context panel through October 20; they do not supply October 27–29. The PR9C archive is the broader selected-window baseline through October 26. Synthetic examples are excluded as real evidence. No newly usable current export or newly qualified identity was found in those inspected sources.

## Basis and intake checks

Existing prices use IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED and IBKR_NATIVE_UNITS_UNVERIFIED. These are native research conventions, not raw execution prices or verified share volumes. Corporate-action completeness and full historical ticker/listing identity remain UNKNOWN. Qualified conId, STK, USD, SMART, primary exchange and symbol must reconcile; a changed instrument, ambiguous match or inconsistent basis fails.

Native acquisition reuses the pinned ib_async 2.1.0 low-level market-only backend and IBKRDailyProvider. It requests bounded daily TRADES/RTH history, conservatively paces requests, retains raw client returns and safe error diagnostics, and disconnects. It does not request positions, balances, executions or orders. Every imported response is independently normalized from its frozen native bytes. Duplicate, off-calendar, future, malformed and incompatible rows cannot be promoted. Conflicting overlap is retained as a blocker; existing canonical rows are never replaced or rescaled.

Current ATR14, SMA10/20/50, confirmed swings, previous-20 extremes, volatility, compression and relative SPY diagnostics are recomputed by the existing Evidence/Panel/shared-ATR implementation. The registration audit records actual per-symbol availability and feature sessions. A confirmed swing can legitimately be unavailable even with complete observations; absence of a pivot is not a missing-price substitution.
