# AAPL historical prices and corporate events (PR 6A)

This is an acquisition and temporal-correctness study, with descriptive event
windows. It supplies no strategy, prediction, execution admission or trading edge.
Branch: `feat/aapl-event-aware-research-v1`. Authoritative scope: the PR 6A brief;
its explicit historical-only acquisition authorization overrides the older generic
no-broker/no-fetch guidance in AGENTS.md for this task alone.

## Inspected revisions and reuse

| Repository | Inspected commit | Role |
| --- | --- | --- |
| equity-research latest main, including PR 5E | `af49e474a15101c938f7812ffb164fdd773e5ca0` | Implementation base |
| finwhaling | `98034e009ac2c062e5a23aad1ba1cf56f2c94001` | Read-only historical acquisition reference |
| cannoslim | `6f1a01d1db2cbc24abc845c190af7acaf6701834` | Read-only prices/universe/earnings-overlay reference |

Reference repositories were not changed. Cannoslim had independent working-tree
changes outside the inspected source files; those were left untouched. Inspected
source-file hashes are recorded in the evidence. Cannoslim's current earnings-calendar
cache is not a historical publication archive and is not used to assert historical
knowledge. Existing PR 5D provider, pacing, cache, native snapshots, normalization,
freeze and offline price loader are reused. Shared ATR comes from the pinned
market-shared 0.2.0 wheel; its original source pin remains
`57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`.

## Actual acquisition

The user reconfirmed the **current** authenticated paper TWS Classic session,
enabled socket clients and **Read-Only API**, port 7497. Confirmation was recorded
before connecting. No TWS settings were changed or queried programmatically.
Explicit endpoint: `127.0.0.1:7497`, client ID `51847`; successful handshakes and no
326 error established its scoped availability. Installed ib_async: 2.1.0;
Python: 3.12.9; server protocol: 178. Other dependency versions, every chunk,
parameters, errors, audit and hashes are in the committed
[aggregate evidence record](evidence/aapl-event-aware-20261022.json).

Actual qualification returned one contract:

```json
{"conId":265598,"symbol":"AAPL","secType":"STK","exchange":"SMART",
 "primaryExchange":"NASDAQ","currency":"USD","localSymbol":"AAPL","tradingClass":"NMS"}
```

The explicitly reviewed research identity is `research:AAPL:common:USD:v1`, Apple
common stock, issuer CIK 320193. Symbols alone are not join keys. Qualification is
retained, rather than assuming the contract ID from a reference repository.

Acquisition ran October 21, 2026 in America/New_York (capture timestamps are UTC
October 22). The fixed requested target remained **2024-01-02 through 2026-10-20**;
it was not extended to the execution day's latest completed session.

| Attempt | Requested scope | Outcome |
| --- | --- | --- |
| Original smoke | Oct 14–20, 2026: five exchange sessions | Native response included Oct 12–13; original adapter correctly withheld cache promotion |
| Repeated smoke, new cache | Same five sessions | PASS; seven native bars preserved, five bounded research rows |
| Full target | Jan 2, 2024–Oct 20, 2026 | PASS; **703/703 expected sessions**, 35 successful calendar chunks, zero retries |

The live smoke exposed one narrow integration defect: IBKR can return a longer
lookback than a requested calendar-day chunk. The adapter now captures **every
native bar**, explicitly records excluded out-of-chunk rows, and selects only the
requested interval into its daily research frame. Original native indices and
hashes follow each selected canonical row. In-window duplicates/conflicts remain
errors; no boundary deduplication or price repair was introduced. The first failed
attempt was retained unchanged.

Full response: **1,023 native bars**, **320 out-of-chunk exclusions**, **703 selected
rows**, first Jan 2, 2024, last Oct 20, 2026. Missing, duplicate, off-calendar and
outside-listing sessions: **none**. Canonical issues: **zero**. Noninformational
provider/entitlement errors: **none**. Each connection received informational farm
status codes 2104 (three), 2106 (two), 2158 (one). Success establishes access to this
specific AAPL historical request; no subscription or account details were queried.

All three attempts used an outgoing-message guard around the existing real
backend. Across them: three API startup handshakes, three contract-details
requests, 37 historical requests, three disconnects, no blocked messages. No
account, position, balance, portfolio, execution or order request was invoked.
The wrapper permitted historical cancellation for timeout cleanup; it was unused.
No new TWS session, streaming subscription or Yahoo fallback was started.

## Local immutable artifacts

These paths are ignored by Git. Licensed OHLCV, actual extracted event rows and
source assertions are local only. Redistribution permission for the event table
was not established; public access is not a redistribution license. The committed
evidence contains identities, references, hashes, counts and aggregate diagnostics.

| Artifact | Local path | SHA-256 bundle identity |
| --- | --- | --- |
| Full native capture | `data/history_cache/pr6a-aapl-gzfik0eg-v2/snapshots/ibkr/28521d410be14a64973c5efe9096eb04` | `1a6739798e098e43ac569389d7dc4cd0e5bd00b3ea1dd7ae5a1b1b90b690b0ed` |
| Frozen prices | `data/research_datasets/pr6a-aapl-gzfik0eg-prices-v1` | `e32427f6db1c0cf6bbb21104a460c4d7f4f4bb29274b28144606facec056ecdf` |
| Frozen events | `data/research_datasets/pr6a-aapl-gzfik0eg-events-v1` | `dbab45eac84ea3c657b60959cdd87b16abc7526641c3efdbd15a0dc1720ed9cd` |
| Previous combined study (preserved) | `data/research_datasets/pr6a-aapl-gzfik0eg-study-v2` | `ea56e33109a45c9d2dcd7d55216971ebcfcc1126aed31d85b96d7d96af479b67` |
| Corrected combined study | `data/research_datasets/pr6a-aapl-gzfik0eg-study-v3` | `5c0f21aa7d197313d2776e5ba5341512c1526e886f9f2d11f9ff1d6a37233fe7` |

The cache is `data/history_cache/pr6a-aapl-gzfik0eg-v2`; original failed cache
`data/history_cache/pr6a-aapl-gzfik0eg` remains intact. Manually transcribed inputs
and their build helper are sealed under
`data/research_datasets/pr6a-aapl-gzfik0eg-event-inputs-v1`. The earlier combined
studies v1 and v2 are preserved; v2 records stricter exclusion of unverified events
from historical knowledge. Review version v3 corrects corporate-action window
annotations using the same frozen prices, events and source assertions. All 131
pre-existing local research/cache files were verified byte-for-byte unchanged.
Changes/corrections require a new exclusive bundle. The original acquisition
evidence retains its original v2 study hash; the separate
[window-review evidence](evidence/aapl-corporate-action-window-review-v1.json)
records v3, its parent and preservation checks.

## Event evidence and inventory

**24 occurrences:** 11 earnings releases (FY2024 Q1 through FY2026 Q3), 11 cash
dividend declarations and two requested older splits. Earnings/core dividend
facts/split identities are directly checked against primary issuer material.
Dividend records are PARTIAL because ex-date evidence is missing; they are not
11 fully verified corporate-action adjustment records.

**22 minute-level announcement times, zero second-level times, two unknown times.**
The minute timestamps describe publication of Apple's issuer-distributed release
on Nasdaq, explicitly marked in each payload. They do not prove globally earliest
publication or a complete historical revision archive. Apple Newsroom supplies
dates; the earnings-call start is a different event and is not used as a release
timestamp. Unknown split release/publication times remain null.

Source references, document identities, capture times, extraction notes and
revision assertions are retained in `event_sources.json`. These are **manual fact
extractions**, not raw HTTP/page captures or an original historical wire archive.
No protected page scraping, undocumented data endpoint or access-limit bypass was
used. Only fields actually read from primary sources were transcribed. The source
inventory below links to issuer releases as distributed by Nasdaq; each is also
cross-checked against the corresponding dated Apple Newsroom release.

| Fiscal release | Primary issuer distribution with publication heading |
| --- | --- |
| FY2024 Q1 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-first-quarter-results-2024-02-01) |
| FY2024 Q2 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-second-quarter-results-2024-05-02) |
| FY2024 Q3 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-third-quarter-results-2024-08-01) |
| FY2024 Q4 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-fourth-quarter-results-2024-10-31) |
| FY2025 Q1 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-first-quarter-results-2025-01-30) |
| FY2025 Q2 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-second-quarter-results-2025-05-01) |
| FY2025 Q3 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-third-quarter-results-2025-07-31) |
| FY2025 Q4 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-fourth-quarter-results-2025-10-30) |
| FY2026 Q1 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-first-quarter-results-2026-01-29) |
| FY2026 Q2 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-second-quarter-results-2026-04-30) |
| FY2026 Q3 | [Apple/Nasdaq](https://www.nasdaq.com/press-release/apple-reports-third-quarter-results-2026-07-30) |

GAAP diluted EPS and headline revenue were checked separately from non-GAAP growth
comparisons. Revenue precision is explicitly the rounded issuer headline (0.1
billion USD), not an invented exact financial-statement amount. Fiscal period end
is distinct from release date. The FY2024 Q4 one-time tax charge is not removed.

[Apple's dividend/split history](https://investor.apple.com/dividend-history/default.aspx)
corroborates all eleven declaration/record/payment dates and nominal cash amounts.
It lists **Record**, not **Ex-date**. The [Nasdaq dividend page](https://www.nasdaq.com/market-activity/stocks/aapl/dividend-history)
displayed unavailable data during inspection. **All eleven ex-dates are null**;
no record/payment date or settlement-rule inference substitutes for evidence.
Ex-date price comparisons are therefore unavailable. This is the main unresolved
corporate-action evidence item.

The requested split inventory has the June 9, 2014 7-for-1 and August 31, 2020
4-for-1 first adjusted trading dates, separately from announcement/record dates.
The [2014 issuer announcement](https://www.apple.com/newsroom/2014/04/23Apple-Expands-Capital-Return-Program-to-Over-130-Billion/)
and [2020 issuer announcement](https://www.apple.com/newsroom/2020/07/apple-reports-third-quarter-results/)
verify these. Distribution dates and exact release times remain unknown. Apple's
history marks first adjusted trading dates with an asterisk; those are not silently
relabeled distribution dates. No 2014/2020 price request was made.

## Schema and composition

`corporate_events_v1` contains an array of revision records. Required concepts:

- `event_id`, positive integer `revision`, `security_id`, `event_type`.
- `event_date`: New York announcement date; `announced_at`: offset-aware timestamp
  or null; precision DATE/MINUTE/SECOND/UNKNOWN; relation and its evidence status.
- `effective_date`: verified ex-date or first split-adjusted date, independently
  from announcement. Alignment supplies `effective_session` and reaction session.
- `fiscal_period`: earnings year/quarter/period end, otherwise null.
- Typed `payload`: earnings GAAP EPS/revenue/precision; dividend cash/ex-date,
  ex-date evidence status, record/payment dates; split new/old share ratio and
  record/distribution dates. Unknown values are explicit nulls.
- `currency`, `source_ids`, `captured_at`, `evidence_status`, `unresolved_fields`.

`event_sources_v1` records HTTPS URL, source/document ID, publication timestamp and
precision/status, capture timestamp, extraction evidence note and a map of full
reviewed revision assertions. Partial supporting sources may have no full
assertion. A claimed full assertion must exactly equal its event revision (apart
from source references/capture time). Source bytes and quality reports are hashed.
Hashes prove retained extraction integrity, not source truth or publication rights.

Duplicate source documents are reported; nothing is silently merged. Distinct
revisions remain visible. Conflicting revisions are excluded from historical
knowledge and event diagnostics until reviewed into a new bundle; v1 does not
invent a chronological correction history. Synthetic examples of every type,
unknowns, conflict and source binding live in `tests/test_events.py`.

`event_aware_research_v1` embeds complete original **research_dataset_v1** and event
bundles under flat prefixes. It adds `calendar.json`, `event_alignment.json`,
`diagnostics.json`, `combined_provenance.json` and outer `hashes.json`. Provenance
binds both input bundle hashes, sources, quality reports, event/alignment schemas,
calendar version and schedule hash, software/shared identity and implementation
hashes. Readers verify both outer integrity and embedded original lineage.
The existing price schema, strict export gates and execution backtester are unchanged.

## Alignment and historical knowledge

Use the existing pinned exchange-calendars 4.13.1 XNYS schedule, New York regular
sessions, including holidays, early closes and DST. This is the project's shared
US-equity session convention; it does not model venue-specific halts or extended
hours. The complete calendar is frozen so offline reading needs no calendar library.

- Before-open earnings map to that session; after-close earnings to the next
  exchange session. At/after the official early close counts as after close.
- Intraday releases map to that date but the full daily bar contains pre-event
  trading. Overnight-open diagnostics are withheld rather than attributing its
  earlier open/high/low/volume to the release.
- Date-only releases on trading days retain same/next possible reaction sessions.
  Verified after-close classification works with a null exact time. Unsupported
  relation guesses do not remove ambiguity.
- Weekend/holiday announcements can map to the next session with unknown exact
  time retained. Timestamp precision crossing a session boundary and contradictory
  timing evidence remain explicit issues.
- Dividends use only verified ex-dates; splits use first new-basis trading dates.
  Invalid nontrading effective dates are flagged, not shifted automatically.

`study.retrospective` returns all event evidence and alignments. It is not a signal
feature view. `study.as_known(offset_aware_cutoff)` returns only revisions whose
full assertions have verified publication evidence **strictly before** cutoff.
Minute stamps use the end of that minute as a conservative bound. The first
February 2024 release is absent at 16:00 and present after 16:31, based on the
issuer distribution evidence. Today's capture timestamp alone never admits an
old event. Missing publication proof, unverified events and conflicting revisions
are excluded, with UNKNOWN knowledge reported. No retrospective alignment or
price outcome is returned by this method. This is an evidence-backed subset;
**archive completeness and historical revision completeness remain UNKNOWN**.

## Descriptive diagnostics and limitations

All eleven earnings windows have complete previous/reaction sessions, warmup and
future observations. Calculations use the native returned price basis:

- Gap = `(first_post_open / previous_completed_close - 1) * 100`.
- Reaction-session range = High − Low, in USD.
- Relative volume = reaction volume / arithmetic mean of the **20 preceding
  exchange sessions**, excluding reaction day. Native volume units remain unverified.
- ATR14 uses shared `true_range` and `atr_simple_series` on the 15 preceding
  completed bars, ending at previous close; no release-day/future value enters it.
- Subsequent returns anchor at **reaction-session Close**, ending at Close exactly
  1, 5 or 10 later exchange sessions. They are retrospective outcomes, not pre-event
  features, total returns, entry prices or executable fills.

Each component verifies all required expected sessions, including intervening
future sessions. Missing warmup or outcomes stay null with reasons; other complete
components can remain available. Previous/reaction missing means no gap. No fill,
calendar compression, provider mixing or guessed ex-date is permitted.

Across eleven earnings windows, native overnight gaps range **−8.6165% to
+7.8715%**, with mean −0.0397%; mean relative volume is **2.0788×**, and mean
pre-event ATR14 is **$5.2551**. Mean subsequent close returns are −0.9625%,
+1.8800%, +2.8980% at the defined 1/5/10-session horizons. These are small-sample
historical descriptions with corporate-action/basis uncertainty, not strategy
results or evidence of predictive value. Detailed per-event prices/outcomes stay local.

The fixed all-session review flags seven absolute overnight gaps ≥5%; five have no
aligned event in this incomplete timeline. Their causes remain **UNKNOWN**, including
for the two aligned observations. Four volume ratios trigger the fixed ≥3× or
≤0.25× review threshold. These are review flags, not repaired observations or
optimized thresholds. All original bars remain unchanged.

Dividend comparisons are implemented and tested on synthetic verified ex-dates,
reporting nominal cash beside native Close changes without mechanical equality
claims. Actual ex-date comparisons: **zero**. Split comparisons on the actual
study: **zero**, with unverified share/price basis flagged; both requested splits
also predate acquired prices. No extra ancient history was forced.

Prices remain **IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED**; volume remains
**IBKR_NATIVE_UNITS_UNVERIFIED**, overall basis verified=false. There is no
RAW_VERIFIED relabel, total-return transformation, independent vendor correction or
execution export. Price historical publication availability is also unknown.

### Corporate-action window review correction

Missing ex-date evidence is a **global evidence gap**, not evidence of overlap with
an earnings window. `corporate_action_evidence` records all unresolved effective
dates with revision/source references and unresolved fields, plus the full action
inventory count. Every dividend remains in the frozen event inventory; no ex-date
is filled or inferred from announcement, record or payment dates.

For each computable price window, `corporate_action_window` records its boundaries:
**after the previous completed session, through the tenth subsequent session after
the reaction session**, inclusive of that last session. The previous-close anchor
session is excluded. Missing outcome bars remain missing; the window uses the
independent exchange schedule, without compressing it to available prices.

- `potential_corporate_action_effects` contains only actions with verified effective
  exchange sessions inside that window. A matching date is not causal attribution.
- If a reviewed source provides an explicit effective-date interval, an unknown-date
  action can carry `payload.effective_date_bounds`: nullable ISO `not_before` and
  `not_after` endpoints (inclusive), `evidence_status="VERIFIED"`, and nonempty
  `source_ids` referencing its event sources. At least one endpoint must be present
  and the bounds must be ordered; the full payload is bound by the existing source
  assertion/provenance mechanism. No endpoints are derived from record/payment dates.
- Bounds intersecting an actual window session produce an entry in the separate
  `corporate_action_overlap_uncertainty` list, labeled overlap **UNDETERMINED**.
  Disjoint bounds produce no window-specific entry. Neither case invents an ex-date.
  Unverified/conflicting effective-session claims inside a window also stay in the
  uncertainty list, rather than the verified-session list.
- Without defensible bounds, an unknown ex-date is reported only in the global
  evidence-gap inventory. Empty window lists do **not** certify absence of corporate
  actions or completeness of the archive.

In the actual corrected AAPL study, 121 unsupported entries (eleven unknown-ex-date
dividends repeated across eleven earnings windows) become **zero** window overlap
entries. All eleven unknown ex-dates remain explicit global evidence gaps; no
source-backed bounds are available for them. All 24 event records, source assertions,
703 price bars, numeric diagnostics and checked as-known views are unchanged.
Fourteen deterministic regressions cover unrelated unknown-date dividends,
intersecting/disjoint/one-sided bounds, a holiday-only interval, sourced-bound
validation, and verified dividends/splits at both window boundaries.

## Offline reproduction

Use the existing pinned data/history extras for freezing/calculation. Loading a
sealed study requires only the standard library and the installed project; it does
not import pandas, pyarrow, calendar, Yahoo, IBKR or a provider, and needs no cache.
Actual 703-bar/24-event loading was verified with network sockets and all optional
provider/data imports denied. Synthetic tests also delete original inputs/cache
before loading a composed study.

With this workspace's ignored artifacts, inspect entirely offline:

```python
from equity_research.events import load_event_study
study = load_event_study("data/research_datasets/pr6a-aapl-gzfik0eg-study-v3")
assert len(study.bars()) == 703
assert len(study.retrospective["events"]) == 24
report = study.diagnostics
known = study.as_known("2024-02-01T16:00:00-05:00")
assert known["events"] == []
```

To create a **new** immutable version from reviewed local inputs, without web or
broker access (replace outputs if those paths already exist):

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli data events-freeze \
  --events data/research_datasets/pr6a-aapl-gzfik0eg-event-inputs-v1/events.json \
  --sources data/research_datasets/pr6a-aapl-gzfik0eg-event-inputs-v1/event_sources.json \
  --output data/research_datasets/aapl-events-review-v3
PYTHONPATH=src .venv/bin/python -m equity_research.cli data event-study \
  --prices data/research_datasets/pr6a-aapl-gzfik0eg-prices-v1 \
  --events data/research_datasets/aapl-events-review-v3 --symbol AAPL \
  --output data/research_datasets/aapl-study-review-v3
```

Do not edit sealed directories; prepare corrections as new reviewed input bytes.
A new clone does not contain the licensed/source-derived dataset. Reproduce the
schema, timing and calculation behavior with deterministic synthetic tests:

```bash
.venv/bin/python -m pytest -q tests/test_events.py tests/test_history.py
.venv/bin/python -m pytest -q
```

The full regression includes PR 4–5E execution/accounting behavior and denies
network sockets. The initial PR passed 228 tests; the review adds fourteen
corporate-action window regressions. Updated full regression: **242 passed in
17.48 seconds**, zero failures. Focused event tests: **60 passed in 4.29 seconds**.
Exact commands/results are recorded in the window-review evidence and PR description.
No lint command is configured.

The next research step is to obtain authorized primary ex-date notices and
historical revision/publication evidence, then freeze a new event/study version.
Independently verify share/volume and price-adjustment semantics before execution
research. No PR 6B strategy development or deployment is part of this change.
