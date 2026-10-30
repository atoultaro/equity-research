# MarketLife setup eligibility and entry opportunities

The authoritative interpretation is the user-supplied MarketLife guidance:

> Setups are moved to 'underway' when they've gone what we consider too far for entry. Those setups (ZETA, CCL) may have triggered entries for some traders but the setup remains attractive to monitor for a fresh entry.

The user also reports that an ENTERABLE setup permits entry or re-entry using the latest published stop. These are attributed source guidance, not independently verified subscriber documentation. ZETA/CCL are examples only, not additions to the studied market data.

A setup exists from ADDED to DROPPED. Its entry eligibility is ENTERABLE or UNDERWAY while active. Subscriber executions are a separate, unobserved process. ADDED does not prove a fill, UNDERWAY does not prove a profitable holding, DROPPED does not prove a sale, and STOP_CHANGED does not prove modification of a resting broker order. Historical field names such as `OPEN_NEW_POSITION` are retained as parser provenance and interpreted as source ADDED in this layer.

| Source action | Setup and opportunity effect | Execution inference |
| --- | --- | --- |
| ADDED | New captured setup episode; initial ENTERABLE opportunity | UNKNOWN |
| STOP_CHANGED while ENTERABLE | End previous future-entry window; create immutable next version at new stop | UNKNOWN |
| STOP_CHANGED while UNDERWAY | Update monitored stop; no eligibility reset | UNKNOWN |
| ENTERABLE → UNDERWAY | Suspend fresh entry | No automatic exit |
| UNDERWAY → ENTERABLE | Explicit return creates new eligible version at current stop | No automatic re-entry |
| DROPPED | End setup and fresh-entry eligibility | No executed exit inferred |
| ADDED after DROPPED | New setup ID/episode | No assumed continuation of prior execution |

Each opportunity retains setup/opportunity IDs, version, source alert/event IDs, published stop, effective interval, source state, supersession link, publication bounds and `observed_execution=UNKNOWN`. Actual entry and quantity remain null. Intervals include their start and exclude their end. An assessment is atomic: a stop revision co-published with UNDERWAY has a zero-duration, ineligible version, not an invented tradable intermediate state. Source order is preserved without inventing intrareport delays. Supersession closes future eligibility, never a subscriber position. Recorded versions remain intact in the final immutable study.

Timing scenarios are conditional. Original minute publication uses its conservative upper bound. The original weekly publication date/time remains UNKNOWN within its inherited bracket. The three newly supplied alerts have operator dates in America/New_York, not publisher timestamps: EARLY is date start, CLOSE_BOUNDARY is cash Close and LATE is date end capped by receipt. These clocks bound possible timing rather than establish actual publication. No future source action chooses which clock is preferred.

The source ledger never reads prices. A separate research layer measures available Close, signed distance to stop, completed shared ATR14, SMA10/20/50, confirmed swings, prior-20 extremes, realized volatility, compression and relative SPY movement. Daily admission requires cash Close + 60 minutes strictly before the decision. Missing sessions/features remain unavailable, with no last-price substitution. Native IBKR split-adjusted price compatibility and unverified volume units remain inherited limitations; no raw execution certification is added.

A hypothetical next regular Open must occur strictly after assumed publication and before eligibility ends, with positive protective stop distance. It is a post-decision observation, not information available at the source decision. Current Close is a known reference, never a retroactive fill. ATR at the opportunity decision and ATR before the candidate Open are distinct. Reference risk is per-share geometry, not actual initial risk, quantity, dollars or realized R.

Independent candidates use their own fixed contemporary stop. Later versions cannot retroactively protect an older candidate. One candidate's stop-out cannot invalidate the next source opportunity. Underway/removal/supersession do not liquidate a hypothetical subscriber who entered earlier. Independent opportunities are alternative explanations, not a sequential executed portfolio. Closing confirmation is an exploratory convention, not evidence of an actual stop-order policy.

The [opportunity reassessment](reports/GRIMES_ENTRY_OPPORTUNITIES.md) revisits CLMT/TEVA/GME/EBAY. The [UNDERWAY study](reports/GRIMES_UNDERWAY_TRANSITIONS.md) compares several causal anchors and same-direction controls; it fits no threshold. The machine [opportunity ledger](evidence/pr9c-setup-opportunities-v1/opportunity-ledger.json) contains all three timing scenarios. Original PR16–PR20 artifacts, the October 26 CSV and the original PR9C experiments remain unchanged as historical evidence; their personal-execution interpretation is superseded here.

Current registration uses the [amended prospective method](GRIMES_PROSPECTIVE_PREDICTION_METHOD.md). A new forecast is blocked until source completeness and current completed price/feature coverage are verified. No brokerage, vendor or automatic subscriber access is performed by this workflow.
