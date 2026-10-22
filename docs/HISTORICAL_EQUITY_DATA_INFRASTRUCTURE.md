# Historical equity data infrastructure v1 — PR 5D

Branch: `feat/historical-equity-providers-v1`. Authoritative task: the user's
PR 5D two-provider brief. Base: `afa944dcb9b993d45808e5156d1ef4d6093e01a5`,
latest fetched main including merged PR 5C. This task authorizes optional historical
acquisition infrastructure beyond the older root AGENTS.md/MVP provider exclusion.
It does not authorize an account query, order, strategy change or PR 6.

## Result and evidence

Yahoo is the primary explicitly selected provider; IBKR is a secondary explicitly
selected provider. Both produce immutable client-return snapshots and feed the
same daily research representation. Neither is an automatic fallback. Mutable
per-provider Parquet caches accelerate acquisition; self-contained frozen datasets
support offline technical diagnostics without provider parsing or client imports.

All demonstrated prices, identities, corrections and cross-provider discrepancies
are **synthetic engineering fixtures**. No Yahoo market-data request, IBKR
connection, account/position/order operation, real equity replay, subscription,
optimization or deployment was performed for this PR. Mocked integration does not
establish live compatibility, subscriptions, data rights, accuracy or an edge.
PR 5A–5C historical audit reports remain unchanged. In particular, Yahoo access
restrictions identified in PR 5C have not been resolved by writing this adapter.

## Inspected references and selective reuse

| Read-only reference | Exact inspected commit | Inspected scope and reuse |
| --- | --- | --- |
| equity-research main | `afa944dcb9b993d45808e5156d1ef4d6093e01a5` | Root guidance, README/MVP/conventions, PR 5A–5C reports, PR 5B preparation contracts, providers/ingestion, replay loader/reporting and tests. Existing Yahoo request/capture, canonical converter, hashes and pinned calendar are reused. |
| cannoslim | `6f1a01d1db2cbc24abc845c190af7acaf6701834` | `prices.py`, `universe.py`, `test_prices.py`: explicit windows, per-symbol Parquet persistence, overlap refresh, cache hits and per-symbol orchestration. Inspected working-file bytes match that commit. |
| finwhaling | `98034e009ac2c062e5a23aad1ba1cf56f2c94001` | `ibkr-data` README, fetch/backend/pacing/contracts/quality/write and associated contract, pacing, acquisition and transform/quality/write tests: async connection lifecycle, explicit contracts, historical requests, serial pacing, bounded retries and reporting. Inspected in a temporary checkout. |

Neither reference application is imported or modified. No reference application
becomes a dependency. cannoslim's last-row deduplication, dropping bad/zero-volume
rows, manufactured adjusted close, volume fill and latest/earliest-only completeness
test are deliberately excluded. Conflicting observations remain in snapshots and
prevent cache promotion. Missing sessions are tested against an independent calendar.

Futures expiry/retention rules, continuous-contract rolling or back adjustments,
CME identity, ES/MES contract multipliers, minute VWAP, 390-minute validation,
18:00–17:00 ETH sessions, partial current-day acceptance and overwriting daily
files are not copied. This adapter requests US USD **STK** contracts, daily TRADES
and RTH; ETFs use the same stock contract type. There is no intraday/futures support.

## Modules and dependencies

| Module | Responsibility |
| --- | --- |
| `history/contracts.py` | Explicit `Security` mapping, bounded inclusive interval, small `DailyProvider` protocol. |
| `providers/yahoo.py` | Additive `YahooDailyProvider` wrapper around the unchanged PR 5B fetch/capture. |
| `providers/ibkr.py` | Optional local-session backend, strict stock qualification, bounded chunking/retries, pacing and snapshots. |
| `history/normalize.py` | Reuse canonical conversion, retain native bases/locators, filter incomplete sessions explicitly, reconcile independent calendar. |
| `history/cache.py` | Per-provider Parquet versions, atomic current pointer, cache reads/refresh, per-symbol batch reports. |
| `history/dataset.py` | Freeze with embedded source captures, integrity-checking offline reader and indicator/ratio access. |
| `history/comparison.py` | Explicit identity comparison, differences, tolerances, ratios and unresolved-basis/action diagnostics. |
| `history/cli.py` | New commands, registered alongside all four PR 5B commands. |

Core runtime dependencies remain only the committed `market-shared==0.2.0` wheel.
Its source, wheel and indicator hash pins are unchanged. Optional extras:

```bash
.venv/bin/python -m pip install '.[data,yahoo,history,test]'
# Only for an explicitly configured real IBKR acquisition:
.venv/bin/python -m pip install '.[ibkr]'
```

`data` retains pandas 2.2.3, numpy 2.2.4, exchange-calendars 4.13.1 and tzdata
2025.2. `yahoo` retains yfinance 0.2.66. `history` adds pyarrow 23.0.1; `ibkr`
adds ib_async 2.1.0. Installation may contact a package index; normal tests do not.
IBKR tests inject a fake client and do not require ib_async, a login or TWS.
Loading an already frozen dataset and calculating indicators need only the core
runtime. Freezing/cache operations require the data/history extras. Replay still
installs and runs without any data, Yahoo, Arrow or IBKR library.

## Explicit identities and acquisition

Commands require a JSON array of mappings. For example, this is a **synthetic**
mapping; substitute reviewed actual identifiers/references for real research:

```json
[
  {
    "symbol": "SPY",
    "security_id": "synthetic-SPY",
    "reference": "synthetic:identity-only",
    "yahoo_symbol": "SPY",
    "ibkr_symbol": "SPY",
    "primary_exchange": "ARCA",
    "listing_venue": "ARCX",
    "currency": "USD",
    "con_id": null,
    "first_session": null,
    "last_session": null,
    "listing_reference": null
  }
]
```

Mappings are user assertions, not independently authenticated identities or
historical listing records. `security_id` and a nonempty reference are mandatory;
matching tickers alone do not establish identity. Optional first/last sessions
require a listing reference and actual XNYS-convention sessions. The actual listing
venue is separate from the XNYS research calendar and from IBKR routing exchange.
Date-specific historical venue changes are not reconstructed in v1; select a
reviewed interval/mapping rather than treating today's venue as historical proof.

Yahoo retains the requested research symbol and exact class-share mapping, such
as BRK.B → BRK-B. An unrelated ticker substitution/rename is rejected. Alias
collisions within a request fail before acquisition. A different identity mapping
for an already cached provider key is rejected, including on full refresh; use a
separate reviewed cache root. IBKR retains symbol, SMART routing, primary exchange,
currency, requested conId and all qualified identity fields. Contract details must
yield exactly one STK matching every supplied identity constraint. A different
qualified conId on a later refresh cannot silently replace the original security.

Only `data history` (and the preserved explicit `fetch-yahoo`) can acquire data.
`history --mode offline`, cache reads, freeze, load, comparison and indicators
make no provider calls. Acquisition is bounded to 20 explicitly selected symbols
and at most 3661 calendar days per interval; there is no universe download,
scanner, scheduler or concurrent acquisition. Each symbol has its own outcome,
including actual acquisition status, requested identity/window/parameters,
returned coverage, retrieval time, errors and snapshot reference/hash. Cache hits
say `NOT_REQUESTED`; they never invent a new retrieval timestamp.

Real acquisition requires applicable permission to access and retain the data.
The new acquisition CLI requires `--permission-reference` recording the caller's
basis in batch/cache/frozen metadata. This string is an assertion, not a license
grant, and does not bypass the PR 5C restriction or provider limits. Direct Python
callers are responsible for the same permission boundary. No new permission or
licensed data is asserted in this PR. No credentials are accepted/stored.

The following commands are conditional operational examples, **not executed live**:

```bash
equity-research data history --provider yahoo --symbols SPY,QQQ,AAPL \
  --mappings /path/to/reviewed-security-map.json --start 2024-01-01 --end 2024-12-31 \
  --cache data/history_cache --permission-reference 'reference establishing permitted access and retention'

equity-research data history --provider ibkr --symbols SPY,QQQ,AAPL \
  --mappings /path/to/reviewed-security-map.json --start 2024-01-01 --end 2024-12-31 \
  --cache data/history_cache --ibkr-port 7497 --ibkr-client-id 17 \
  --permission-reference 'reference establishing entitled historical data use and retention'
```

IBKR requires an already running, authenticated local TWS/Gateway; port and
positive nonzero client ID are explicit. No automatic launch, authentication,
account selection, balance/position/execution query, trading operation or streaming
subscription exists. The backend uses `IB.client.connectAsync` for the handshake,
**not** high-level `IB.connectAsync`, which can request positions even with startup
flags disabled. A pinned narrow subclass disables `_onError`'s automatic account
summary resubscription on error 1102. Unsolicited account identifiers sent in the
TWS handshake are neither requested nor persisted. The adapter does not verify or
configure TWS's own read-only setting; configure that independently if used.

Contract details have a 15-second timeout, connection 10 seconds. Historical
requests use explicit UTC end anchors, at most 30 calendar days per chunk,
`barSizeSetting="1 day"`, `whatToShow="TRADES"`, `useRTH=True`, `formatDate=1`,
`keepUpToDate=False`, client timeout 30 seconds and outer bound 35 seconds. Every
attempt/chunk parameter is retained. At most three attempts retry only pacing,
timeout or connection categories; backoff is 15/30 seconds. Permission/no-data/
unclassified failures are not retried. Permission failures stop remaining chunks.
The adapter records both numeric IB codes and safe categories; arbitrary messages,
URLs and account identifiers are excluded. Client timeout warnings are captured
as `TIMEOUT`, since the public historical method can return an empty container on
timeout. Empty/partial responses are distinct and independent coverage is checked.

One adapter shares a conservative serial pacer across symbols: at least 2 seconds
between requests, at least 15 seconds between identical requests and at most 60
requests per 600 seconds. Waits are in increments of at most 60 seconds. This
does not coordinate other processes or TWS clients; avoid overlapping acquisition
jobs. No restriction workaround or subscription fallback is implemented.

## Cache versions and refresh policy

Provider caches live under separate `yahoo/` and `ibkr/` directories with SHA256
keys derived from exact provider identities. Each entry contains `versions/UUID/`
with `bars.parquet`, `metadata.json`, `hashes.json`, and a mutable atomic
`current.json` pointer. Decimal strings/nulls and source row JSON remain exact in
Parquet; no floating-point or integer-volume conversion is hidden in persistence.
The logical rows hash and exact byte bundle hash are both checked on reads.

| Mode | Behavior |
| --- | --- |
| `auto` | Complete interval: hit, no request. Otherwise initial population or refresh from earliest missing session/overlap through requested end. Default overlap is seven calendar days. |
| `incremental` | Force an overlap refresh even for a complete cache. Earlier requested history/interior missing sessions move the refresh start back as needed. |
| `full` | Re-fetch the entire requested interval. Replace that interval; preserve valid cached observations outside it. Required to recover a corrupt cache, where prior untrusted rows cannot be preserved. |
| `offline` | Report hit/miss/incomplete/corrupt without importing either client or requesting data. |

A fresh requested interval replaces the old interval, including removed sessions.
Old bars are never used to conceal a hole in a fresh response. Corrections and
removed dates are explicit in both version metadata and batch reports. Duplicate,
conflicting, malformed, off-calendar or outside-listing rows prevent promotion;
the native snapshot remains available. Valid partial responses can populate a
diagnostic incomplete cache. Failed/empty responses never erase an existing valid
version. No value is forward filled, repaired or sourced from the other provider.

Per-entry exclusive writer locks prevent concurrent lost updates. Readers see
one completely sealed generation via atomic pointer replacement. Interrupted
unpublished generations do not replace a valid pointer. A stale `.lock` must be
inspected before manual removal. Corruption is reported, never interpreted as a
cache miss that triggers an implicit request; explicit full refresh creates a new
generation and leaves damaged evidence intact. No garbage collection is included;
retain source snapshots needed for future freezes. Batch reports are immutable
under `reports/UUID`; acquisition snapshots are under `snapshots/PROVIDER/UUID`.

The cache is an acquisition optimization and never evidence of historical
availability. As with any latest-vintage cache, an incremental merge can combine
provider vintages. Each row records its actual source snapshot; use a full refresh
when a single requested acquisition window matters. Neither mode proves PIT data.

## Snapshots, calendar and native semantics

Yahoo snapshots retain PR 5B `request.json`, `acquisition.json`, tagged lossless
`returned_frame.json` and `hashes.json`. No request defaults or PR 5B schemas/gates
are changed. IBKR has separate `ibkr_request_v1`/`ibkr_acquisition_v1` schemas,
tagged `returned_bars.json` (date, OHLCV, average, barCount and chunk bounds),
`returned_frame.json` for canonical conversion and the same immutable hash bundle.
Native daily dates remain in `returned_bars.json`; conversion accepts date labels
and normalizes IB YYYYMMDD strings. No unsupported timestamp is guessed into a day.
Snapshots capture public client returns, **not original HTTP/TWS wire payloads**.
Client version is actual when available, null on an unavailable client; the
expected pinned version is separate. Synthetic backends are labeled explicitly.

Stable content identity covers request and returned content, excluding acquisition
timing/outcome. Bundle identity covers all stored files, including acquisition
metadata. No acquisition snapshot/output directory can be overwritten. Hashes
establish local integrity, not provider authentication or permission.

The provider-neutral `research_daily_v1` rows contain:

```text
security_id, symbol, provider, provider_symbol, session_date,
open, high, low, close, adj_close, volume,
price_basis, volume_basis, source_snapshot_sha256, source_row
```

Numbers are decimal strings; absent adjusted close is JSON null, never copied
from close. `source_row` identifies the original frame hash and row position.
Provider-specific request/identity/action details remain in sidecars and embedded
source snapshots. Native semantics are preserved:

| Source | Price metadata | Volume metadata |
| --- | --- | --- |
| Yahoo `auto_adjust=False` | `YAHOO_NATIVE_UNVERIFIED`; flag alone is not raw-price evidence. Optional adjusted close stays separate. | `YAHOO_NATIVE_UNVERIFIED`; no adjustment/unit claim. |
| IBKR daily RTH TRADES | `IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED`; documented split adjustment, no dividend adjustment; not execution-verified. ADJUSTED_LAST is unsupported. | `IBKR_NATIVE_UNITS_UNVERIFIED`; feed filtering/unit settings can differ; no automatic factor of 100 or Yahoo equivalence. |

[IBKR historical documentation](https://www.interactivebrokers.com/docs/tws-api/doc/md/historical-bars)
and its [legacy adjustment explanation](https://interactivebrokers.github.io/tws-api/historical_bars.html)
were checked on 2026-10-21. Client connection/timeout behavior was checked against
the [pinned ib_async interface](https://github.com/ib-api-reloaded/ib_async/blob/v2.1.0/ib_async/ib.py)
and locally installed 2.1.0. Documented native semantics do not certify an actual
retrieved series. Streaming market-data type is recorded as unknown/not requested;
historical data type TRADES and RTH parameters are recorded explicitly.

The unchanged pinned exchange-calendars 4.13.1 XNYS schedule is generated
independently of bars, with UTC timestamps, DST, early closes, holidays and
exceptional closures. Each interval quality report records missing/off-calendar/
duplicate/outside-listing sessions and any explicit listing exclusions. No unknown
listing history excuses a missing bar. Only sessions closed by acquisition start
enter the cache; excluded incomplete sessions are listed, while original captures
retain those rows. Retrieval time never becomes historical `available_at`.
Corporate-action and historical-availability completeness remain **unknown**.

## Frozen datasets and offline analysis

Freeze reads a selected provider and explicit securities/window from cache. Default
freeze fails before output creation for missing sessions or invalid calendar
coverage. `--allow-incomplete` is an explicit diagnostic escape hatch: the quality
FAIL is retained and indicators still reject the gaps. This is never a forward-fill
or execution-export waiver. There is no data substitution.

`research_dataset_v1` contains `dataset.json`, per-symbol canonical JSON bars and
quality JSON, original source capture files under safe flat hash-prefixed names,
and a final `hashes.json`. The manifest records identities, source origins,
`synthetic_only`, provider, interval, creation time, calendar/schema/configuration
versions, converter/implementation hashes, verified shared-wheel identity,
actual data dependency versions, bases, cache versions,
source bundle/file hashes, qualification and permission references. Every source
needed by selected rows is copied and verified. No frozen dependency points to a
mutable cache or original snapshot path. Existing output paths are rejected.

```python
from equity_research.history import load_research_dataset

dataset = load_research_dataset("/tmp/equity-history-demo-v1/yahoo-dataset")
spy = dataset.bars("SPY")  # tuple of independent row dictionaries; no provider parsing
indicators = dataset.indicators("SPY")
ratios = dataset.relative_strength("SPY", "QQQ")
```

Loading verifies bundle hashes and embedded source/row lineage without calendar
regeneration, cache access or optional packages. Returned data/metadata are copies.
SMA50/200 and mean volume20 require full windows; EMA50 uses the shared first-value
seed; simple ATR14 uses shared true range and ATR with fourteen prior-close ranges
(fifteen bars). ATR is not duplicated or changed to Wilder smoothing. Relative
strength is a native-close ratio over exactly matching session lists, never an
inferred ranking, total-return series or historical screening membership. All
outputs retain diagnostic basis/availability limitations. No strategy is added.

These files deliberately do **not** have the replay CSV/manifest contract. A
technical dataset says `NOT_EVALUATED_USE_EXISTING_EXPORT_GATES` for execution.
The strict PR 5B raw/no-actions/identity/calendar/actual-availability gates and all
PR 4 strategy, execution, accounting and reporting remain unchanged. IBKR technical
datasets have no new automatic path through those Yahoo-specific export gates.

## Comparison and synthetic demonstration

`compare-providers` loads two frozen datasets offline and requires the same
explicit security ID/currency and an interval within both datasets. It reports
common/one-sided/missing expected sessions, every OHLC/volume/adjusted-close value,
signed/absolute difference, percentage difference relative to Yahoo, IBKR/Yahoo
ratio, tolerance exceedance, native bases, adjusted-close observations, ratio
changes and provider action observations. Unknown action coverage remains explicit.
It never infers a split/dividend solely from a ratio or empty action response.

Tolerance units are price dollars, native volume units and **percentage points**.
A difference exceeds tolerance only when outside both the absolute and percentage
allowances; a nonzero difference from zero uses the absolute allowance with null
percentage/ratio. Missing/invalid values yield null diagnostics, not zero prices.
Different/unknown or unverified bases produce `DIAGNOSTIC_ONLY_BASIS_UNRESOLVED`,
even for identical numbers. No transformation, averaging or source selection occurs.
Duplicate session keys and different identified securities reject comparison.

Run the fully offline example with a new output directory:

```bash
PYTHONPATH=src .venv/bin/python scripts/make_historical_equity_example.py \
  --output /tmp/equity-history-demo-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data history \
  --provider yahoo --symbols SPY,QQQ,AAPL --mode offline \
  --mappings /tmp/equity-history-demo-v1/mappings.json --start 2024-01-02 --end 2024-12-31 \
  --cache /tmp/equity-history-demo-v1/yahoo-cache
PYTHONPATH=src .venv/bin/python -m equity_research.cli data freeze \
  --provider yahoo --symbols SPY,QQQ,AAPL \
  --mappings /tmp/equity-history-demo-v1/mappings.json --start 2024-01-02 --end 2024-12-31 \
  --cache /tmp/equity-history-demo-v1/yahoo-cache --output /tmp/equity-history-refrozen-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data compare-providers \
  --symbol AAPL --start 2024-01-02 --end 2024-12-31 \
  --yahoo-dataset /tmp/equity-history-demo-v1/yahoo-dataset \
  --ibkr-dataset /tmp/equity-history-demo-v1/ibkr-dataset \
  --price-absolute 0.01 --price-percent 0.01 --volume-percent 1 \
  --output /tmp/equity-history-comparison-v1
```

The script creates 252 synthetic sessions for each symbol/provider, separate
caches, native snapshots, two frozen multi-symbol datasets, indicator/ratio output
and three comparisons. Synthetic Yahoo-style SPY final SMA50=157.125,
SMA200=138.375, ATR14=2.0. For the first synthetic AAPL session, Yahoo-style
close=100.5 versus IBKR-style close=50.25: absolute difference50.25, percentage50%,
ratio0.5. Interpretation is unresolved; neither source is declared correct. The
deliberate factor is not evidence of an actual historical AAPL event.

CLI exits: new history 0 for all complete successful/cache-hit results, 3 for
partial/failed/incomplete results; freeze/comparison 0 for a successfully written
artifact (inspect its quality/interpretation), 2 for invalid input/integrity/error.
All preexisting fetch-yahoo/validate/compare/export exit semantics remain unchanged.

## Validation and confirmed limitations

Run `.venv/bin/python -m pytest -q` with optional test/data/history/Yahoo extras.
The new tests cover real adapter call boundaries with mocked Yahoo/IBKR returns,
cache hit/miss/overlap/full refresh, correction/removal/gap detection, aliases,
partial multi-symbol failures, corruption recovery/locks, explicit contracts,
qualification ambiguity/mismatch, exact historical parameters, native Decimal/date
capture, chunking, completion filtering, retries/pacing/permissions, safe diagnostics,
frozen hashes/immutability/source independence, calendar/listing rules, indicator
warmups/gaps, comparisons/zero/null/tolerances/bases and the full synthetic demo.
A fresh process loads frozen data/calculates shared indicators while imports of
Yahoo, IBKR, pandas, numpy, Arrow and the calendar library are denied. Existing
replay and PR 5B gate tests remain unmodified and pass. Final full-suite result:
**180 passed in 15.11s** (112 existing and 68 new tests), with no skips or failures.
Both providers' offline history/freeze commands and the comparison CLI also ran
successfully against the synthetic demonstration. Git whitespace and six local
documentation-link checks pass. No canonical lint command exists.

Live connectivity, exact IBKR subscriptions/TWS version, actual volume units,
provider coverage of delisted/renamed securities, native basis correctness, event
completeness and historical publication times remain unverified. A current conId
or venue does not establish historical screening or listing membership. Yahoo
retains its single-request logged-error limitations. No adjusted/raw reconciliation
transform, provider priority selection, cache garbage collector or cross-process
pacing service is added. There is no verified real execution dataset or claim of
stock-selection/PIT suitability. PR 6 has not begun.
