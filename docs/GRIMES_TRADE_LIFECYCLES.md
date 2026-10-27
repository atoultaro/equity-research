# Grimes trade lifecycles: October 18–26, 2026

PR16 extends the PR15 comprehension study to exactly 26 stocks across seven
alerts. It reconstructs source-reported positions and a separate analytical
daily-bar scenario. It does not change the execution simulator or calculate
execution P&L, portfolio returns or a strategy edge.

Authoritative task: the operator's **PR #16: Grimes Trade Lifecycle
Reconstruction**, including the subsequent seven-alert transcription. Branch:
`research/grimes-trade-lifecycles-20261018-26-v1`, based on main
`c44dfd836ff4304f7b89d0d76616bc91cfc0e452`. PR15's inspected pre-merge head was
`0adb9c128589760e8043c366f2157b25458de729`. No finwhaling changes or framework
changes are involved.

## Source and analytical states

`lifecycle/source.py` parses all four action sections strictly. Every included
action has an original alert/body hash, line number, character offset and source
text. PLTR and PEP remain in the originals and excluded-action inventory, outside
the 26 structured positions. Exact subscriber originals and MIME bodies stay in
ignored local bundles; the public reports contain derived facts and measurements.

| Source action | Position consequence | Setup consequence |
|---|---|---|
| OPEN_NEW_POSITION | New trade episode, OPEN | ENTERABLE |
| STOP_CHANGED | Same episode, stop revised | Unchanged |
| SETUP_CHANGED to underway | Same OPEN episode | UNDERWAY |
| DROPPED | Source CLOSED | Last observed availability retained |

Source stops can widen or tighten. A fresh explicit opening after a closure gets
a new episode ID; neither a stop revision nor continued enterability implies
another entry. Actual entry, quantity, execution clock and closure cause remain
unknown. Modeled outcomes never rewrite this ledger.

`lifecycle/model.py` applies the operator-reported PR15 1R convention to analytical
episodes as explicitly requested in PR16. `one_r()` and methodology validation
are reused; the frozen PR15 methodology record is unchanged. This extension is
an operator-directed scenario, not a claim of verified trade-specific exit
instructions across all 26 stocks.

The entry scenario is the **next eligible regular-session Open**, after the
opening event's conservative availability bound. Minute-resolution publication
times use the end of that minute. The exact first eligible timestamp, qualified
contract, native bar field and source bundle hash are retained. Missing entry
bars never cause entry to jump to a later session. A source closure before the
first eligible Open produces no fictitious modeled entry.

Original R uses this hypothetical entry and the **initial** reported stop.
Revisions never reset it. An invalid/nonpositive scenario R leaves its target
unavailable. Actual Grimes entry, original risk, target and fills are unknown.

After activation, LONG Low <= stop and SHORT High >= stop produce an assumed
trigger and modeled closure. Stops revised after hours first apply to the next
eligible RTH session. A daily candle crossing an intraday revision/closure
boundary is timing-ambiguous unless an already-active opening gap resolves it.
No intraday data is fetched in this study. A trigger records a level, not an
assumed stop-price fill; gap/slippage and costs remain unknown.

SHORT +1 original R closes the whole modeled position. LONG +1R takes at least
one-third off and retains an unspecified runner; exact size, remaining fraction
and discretionary subsequent management remain unknown. If both stop and target
are touched in one daily candle, candidate observations preserve unknown order.
A later source DROP establishes source closure, not the cause/order of that
earlier ambiguous path. Candidate observations are counted separately from
resolved conditional triggers/targets in `comparison.json`.

After modeled closure, subsequent source management emits a conflict. It cannot
rescue that episode or create a re-entry. No time-window flag closes a position.

## Weekly clock and EBAY

The weekly alert's original display remains **“Yesterday at 8:57 AM”** and its
`published_at` remains null everywhere in the source ledger. The matching
original email independently carries a provider email timestamp of
`2026-10-25T12:57:45Z`. The real study explicitly enables that timestamp as a
separate conservative content-availability bound. It is not used to manufacture
the web/chat publication date. Without this optional clock assumption, weekly
openings remain timing-unresolved.

EBAY's qualified contract is conId **4347086**, NASDAQ, USD/STK/SMART. Its native
October 26 RTH Low **117.87** exactly matches the operator's nominal quote. That
provides narrow numerical unit-scale corroboration for this session, not a
complete independent corporate-action/adjustment audit. It must not validate
other stocks, earlier sessions or a mismatching quote/contract.

Under these declared timing and session-scale decisions:

1. The original 119.20 stop is active before Monday RTH.
2. Scenario entry is October 26 Open 121.24; hypothetical original R is 2.04 and
   +1R target is 123.28. These are not actual entry/target facts.
3. High 121.61 does not touch that target; Low 117.87 crosses 119.20.
4. `ASSUMED_STOP_TRIGGERED` closes the modeled episode, actual fill unknown.
5. The evening source revision to 117.50 remains in the source OPEN episode.
   It emits a source/model conflict and cannot rescue or reopen the model.

Disabling email-bound timing or removing/mismatching the quote-scale evidence
leaves timing/basis unresolved. No discretionary intraday adjustment or unreported
re-entry is invented. See the [EBAY dossier](reports/grimes-lifecycles-20261018-26/EBAY.md).

## Historical data and context

Actual acquisition reused PR14's restricted low-level IBKR adapter and immutable
checkpoint/report format. The operator-authorized existing non-paper TWS at
`127.0.0.1:7496`, with Read-Only API enabled, supplied only contract qualification
and bounded daily `TRADES`/RTH historical requests. Client IDs were 46161–46163.
No orders, account synchronization, positions, balances, executions or settings
operations were added. The two larger batches shared conservative pacing. The
additional bounded XLP request supplies ELF's broad sector context.

Five stock captures were reused: AAPL, SAIL, SLB, GE and SCCO. New captures cover
the other 21 stocks and XLY/XLC/XLP. Requested warmup is January 2, 2025 through
October 26, 2026. Every stock has bars throughout the alert observation period.
No October 27 bars enter this fixed study, even though acquisition/review ran
across midnight. The last four source openings are right-censored before their
next eligible modeled entry.

Identity limitations are explicit:

- TEVA's current conId 922990633 supplies 31 sessions beginning September 14,
  2026. Teva's [issuer announcement](https://ir.tevapharm.com/news-and-events/press-releases/press-release-details/2026/Teva-Begins-Trading-Ordinary-Shares-Directly-on-the-NYSE-Marking-a-Milestone-in-its-Pivot-to-Growth-Strategy/default.aspx)
  documents the ADS-to-ordinary-share listing transition. We do not stitch the
  old ADS contract onto the new identity. Long warmups remain unavailable.
- SNDK is the current separated SanDisk conId 760250490, not a stitch to the
  pre-2016 ticker. Its native capture contains 427 sessions including pre-regular-
  way February 2025 data; the [SEC filing](https://www.sec.gov/Archives/edgar/data/106040/000119312525033383/d847507d8k.htm)
  documents regular-way trading beginning February 24, 2025. All October rolling
  windows used here are after that date.
- ASST conId 852120292 is Strive. Its business transition and
  [February 2026 1-for-20 reverse split](https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2026-70)
  prevent assuming unchanged historical business/nominal units. Its conventional
  sector proxy remains unresolved; long historical features span that caveat.

Native prices retain `IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED`; volumes retain
`IBKR_NATIVE_UNITS_UNVERIFIED`. Twenty-five stocks lack independently corroborated
reported-stop scale. Twenty-one have active historical scenarios classified
`UNRESOLVED_BASIS` in primary results; four have no eligible entry before cutoff.
A separately labeled **conditional basis scenario** measures what would happen
if reported stops and native bars share units. It is not a validated execution
history and must not be combined with primary outcomes as verified evidence.

For every source action, the study records SPY/QQQ/RSP/IWM daily and trailing
5/20/60-session price returns, trend/MA relationships and volatility. Stock
features include confirmed swings, MA relationships, relative strength, and
reported-stop/ATR distances, with explicit stop-unit caveats. ATR comes through
the existing MarketContext implementation and pinned shared wheel.

The independent pinned XNYS calendar and cash-close-plus-60-minute availability
assumption govern features. Every snapshot has its own event cutoff. Missing
expected observations and insufficient warmup produce unavailable fields; no
forward fill or stale substitution occurs. Future poison tests protect this
boundary. Exact historical bar publication clocks remain unknown, and revised
native historical prices are retrospective observations, not evidence of a
contemporaneously captured feed.

Sector ETFs are fixed **agent-selected context choices**, not Grimes's choices,
historical GICS classifications, screening membership or ETF constituents.
Mappings bind both stock and ETF conIds. Five prior PR15 corporate-event records
are retained, but all lack verified publication clocks and stay unknown for
point-in-time availability; earnings/action completeness remains unknown for the
entire universe. Expert commentary is preserved separately from computed features.
Stale Databento ES prices are not used.

Exploratory 2/3/5-session windows measure signed Close progress and MFE from the
scenario Open, in price units, fixed original R and pre-entry ATR. The explicit
agent-defined flag is nonpositive signed Close progress. It is not a verified
Grimes parameter. Missing/right-censored windows and horizons after an already
closed episode remain unavailable; no definitive time-stop exit is inferred.

## Offline interface

All lifecycle commands are offline. Live capture remains the separately invoked
PR14 command; automated tests never connect to TWS.

```bash
equity-research lifecycle capture-alerts --input seven-original-alerts.json \
  --output runs/my-alert-capture-v1
equity-research lifecycle freeze-inputs \
  --spec experiments/grimes-lifecycle-20261018-26-v1.json \
  --alerts runs/my-alert-capture-v1 \
  --methodology experiments/grimes-current-methodology-v1.json \
  --audit runs/frozen-audit-report 'AAPL,CLMT,...' \
  --audit runs/another-frozen-report 'SPY,QQQ,RSP,IWM,...' \
  --output runs/my-lifecycle-inputs-v1
equity-research lifecycle study --inputs runs/my-lifecycle-inputs-v1 \
  --output runs/my-lifecycle-study-v1
equity-research lifecycle replay --study runs/my-lifecycle-study-v1 \
  --output runs/my-lifecycle-replay-v1
```

The audit selections above are placeholders: replace each CSV with explicit,
disjoint captured symbols totaling the exact 26 stocks plus ETF context. The
real selections and all conIds are recorded in the frozen source proofs and
experiment config. Each source must be an existing sealed PR14 report; this
command does not acquire missing data.

`seven-original-alerts.json` has schema `grimes_alerts_v1`, origin `operator` or
`connected_gmail`, and seven ordered alerts. Each has `alert_id`, zero-based
`source_sequence`, exact `text`, optional original `html`, `source_reference`,
`original_publication_display`, aware `published_at` or null, and explicit
`publication_precision` (`MINUTE`, `SECOND`, or `UNKNOWN`). Optional aware
`email_received_at` remains separate evidence. Preserve the four underscored
action-section headers. Full input bytes and text/HTML bodies are retained;
missing HTML is explicitly recorded, never reconstructed.

Input freezing independently replays selected native-return checkpoints through
the existing source loader. Every study embeds the sealed source capture, source
proofs, config and unchanged operator methodology. `load_study()` verifies hashes,
implementation/shared dependency identities, then **recomputes every semantic
output and Markdown dossier**. Resealing changed source stops, modeled results
or quality/count summaries cannot bypass that comparison. Loading is a batch
offline validation; no brokerage connection or mutable cache access is required.
All output directories are exclusively created; replay cannot overwrite a run.

The actual local run is `runs/grimes-lifecycle-20261018-26-v1/`. Its final hashes,
test evidence, source inventory and public dossier links appear in the
[research report](reports/GRIMES_LIFECYCLES_20261018_26.md).

Reproduce the actual final study locally into a new directory:

```bash
equity-research lifecycle replay \
  --study runs/grimes-lifecycle-20261018-26-v1/study-v5 \
  --output runs/grimes-lifecycle-20261018-26-v1/review-replay-v5
```

This requires the local frozen bundle; public Git intentionally excludes raw
subscriber text and provider frames. The committed offline tests construct their
own synthetic provider evidence and source bodies.
