# PR 5A: Yahoo Finance data source and reuse audit

Audit date: 2026-10-21 (America/New_York). Status: documentation-only proposal
for review. No provider probes, historical downloads, strategy backtests, adapter,
dependency changes, or changes to either application's Python were made.

## Executive recommendation

**INFERRED — conditional go for a small provider-quality pilot; no direct reuse
of the existing cache as research input.** Yahoo may supply useful historical
prices for an individually identified candidate, but the inspected pipeline does
not establish raw execution prices, complete sessions, historical availability,
or a survivorship-free universe. These are separate requirements.

PR 5B should implement a narrow, optional acquisition boundary with immutable
snapshots, explicit identity and adjustment metadata, calendar reconciliation,
and offline validation. Keep replay offline and its current raw/no-action contract
unchanged. Initially permit export to that contract only for a **verified
no-action period whose entire history and provider adjustment horizon have been
checked**, including splits after the experiment and before retrieval. Require
independent evidence that its OHLC and volume equal the contemporaneous basis.
If that cannot be established, PR 5B should deliver diagnostics and refuse replay
export; adapter completion need not mean a real-stock experiment is admissible.

**VERIFIED — `auto_adjust=False` is not a raw-price attestation.** Yahoo labels
Close as split adjusted and Adj Close as adjusted for splits and distributions
([Yahoo field labels][Y-fields], [Yahoo adjustment explanation][Y-adjust]). A
future adjusted-basis contract is an alternative requiring explicit review,
versioning, share-unit/cost/risk treatment, and corporate-action accounting. Do
not relabel Yahoo values `raw`, substitute Adj Close for execution prices, or
silently relax the existing loader. Obtaining independently verified unadjusted
bars and events is another route; no paid provider is selected here.

## Evidence status and inspected revisions

**VERIFIED** means inspected source/test assertions or cited primary documentation.
It does not imply a test ran or a provider response was observed. **INFERRED**
means a consequence or design judgment not independently measured. **UNKNOWN**
means further source, provider access, or empirical comparison is needed. All
architecture and acceptance proposals below are recommendations, not implemented
capabilities. Primary web documentation was consulted on the audit date; no Yahoo
API was invoked and no quoted historical price values were used as pilot evidence.

| Repository | Exact inspected revision | Inspection boundary |
| --- | --- | --- |
| `atoultaro/equity-research` | `fa212bad89705802d0cc0b635d28b3a20323cf03` | Clean starting tree on `research/yahoo-data-source-audit-v1`; local and remote `main` both matched this SHA; merge message identifies the project PR 4 slice (GitHub PR #1). |
| `atoultaro/cannoslim` | `6f1a01d1db2cbc24abc845c190af7acaf6701834` | Read-only local checkout on `task/execution-ledger-summary`. Unrelated pre-existing changes exist. Every audited source/test/instruction file listed below matched HEAD (`git diff HEAD --name-only -- <audited paths>` was empty). Unrelated modified files and generated/private datasets were not used. |

All reference-repository links below pin that inspected commit, rather than its
moving branch. Target-repository relative links refer to unchanged files at the
inspected equity revision. No code, data, or generated artifacts were copied
between repositories. The audit document is new synthesis.

## Existing equity contracts PR 5B must preserve

**VERIFIED** from [data.py](../src/equity_research/data.py),
[models.py](../src/equity_research/models.py),
[qualification.py](../src/equity_research/qualification.py),
[execution.py](../src/equity_research/execution.py),
[reporting.py](../src/equity_research/reporting.py),
[MVP_SPEC.md](MVP_SPEC.md), and [RESEARCH_CONVENTIONS.md](RESEARCH_CONVENTIONS.md):

| Boundary | Exact requirement / implication for adapter export |
| --- | --- |
| Bars | CSV field set exactly `symbol,session_date,open,high,low,close,volume`, no duplicate headers or extra action/Adj Close columns. One symbol, one ascending row per supplied session; no sorting, merging, deduplication, or imputation inside `load_dataset`. |
| Numbers | Finite positive OHLC; finite nonnegative volume, consistent high/low bounds. `DailyBar` uses Decimal via `number`; zero volume is allowed by this loader, unlike the Yahoo normalizer. |
| Manifest | Required keys: `symbol`, `source`, `source_revision`, `dataset_version`, `created_at`, `adjustment`, `corporate_actions`, `availability_convention`, `exchange`, `timezone`, `calendar_version`, `sessions`, `data_sha256`. Identity/convention fields checked in code must be nonempty; hash covers exact CSV bytes. `created_at` is aware or null, never an invented retrieval timestamp. |
| Basis | Only `adjustment="raw"` and `corporate_actions=[]`. Empty actions are a source attestation, not evidence that the loader discovered no actions. |
| Schedule | Only `exchange="XNYS"`, `timezone="America/New_York"`. Session has `session_date`, aware `opens_at`, `closes_at`, `available_at`; local weekday open 09:30, close 16:00 or 13:00; open < close <= available, ascending unique dates, previous availability strictly before next listed open. ZoneInfo resolves ET/DST. No holiday database establishes authenticity/completeness. |
| Candidate and timing | One manual breakout candidate with observed/available timestamps, candidate session and provenance kind/reference. Availability cannot precede observation. `qualify` freezes history at signal session and decision availability; signal must be complete/available, defaults require 55 history bars. Source membership remains user-supplied/unverified; price retrieval cannot prove it. |
| Replay and economics | Next eligible listed open after signal and candidate availability; gap-aware fills, conservative daily ambiguity, fixed actual initial risk, separate gross dollars, slippage, commission, fees and net dollars. Raw dollar sizing, fixed dollar buffers and per-share costs make arbitrary split rescaling economically material. Shared ATR/TR stay in the pinned wheel. |
| Artifacts | `run_experiment` captures input bytes once, hashes inputs/source/runtime/shared artifact, writes only a new run directory. Invalid input fails before completed output. Canonical artifacts must not depend on later cache contents. |

Relevant inspected assertions are in [test_data.py](../tests/test_data.py),
[test_qualification.py](../tests/test_qualification.py),
[test_execution.py](../tests/test_execution.py), and
[test_end_to_end.py](../tests/test_end_to_end.py); the offline socket guard is in
[conftest.py](../tests/conftest.py). Synthetic tests validate mechanics, not edge
or provider quality. The supplied schedule and undeclared actions remain trust
boundaries even when every existing assertion passes.

## A. Implementation inventory: ingestion

**VERIFIED — source behavior** in [prices.py][C-prices] and
[universe.py][C-universe]; provider/runtime details are distinguished below.

| Component | Actual behavior and consequence |
| --- | --- |
| Client/dependencies | Lazy import `yfinance` inside `fetch_yahoo_daily_ohlcv`; missing import raises RuntimeError. [pyproject.toml][C-project] specifies `yfinance>=0.2.40`, `pandas>=2.1.0`, `pyarrow>=14.0.0`, with no upper bounds for these. That constraint does not identify the version that created any cache. No runtime package or cache was used as provider evidence. |
| Download arguments | `interval="1d"`, `group_by="ticker"`, `auto_adjust=False`, `progress=False`, caller `threads` (default True), `timeout` (default 15 seconds); `start` and `end` strings. Actions, repair, keepna, back_adjust, timezone handling, rounding and pre/post are not explicitly passed. |
| Range | Defaults: 90 **calendar** days, batches of 100. Explicit target normalized to naive midnight; otherwise ET today or previous pandas `BDay`, which skips weekends but not exchange holidays. Lookback starts `target-max(1,lookback_days)` days; download end is target+1 day. Slicing includes both endpoints. Inclusive start/exclusive end are documented by [yfinance][Y-download], not a completeness guarantee. |
| Batching and symbols | Exact input duplicates removed preserving order; no strip/uppercase here. `yahoo_symbol` replaces dot and slash with dash. Output dictionary keys remain original inputs. Each batch downloads from its earliest member's fetch start. Alias collisions and casing mismatches are not rejected. |
| Extraction | `_extract_one_symbol` accepts ticker-level MultiIndex using mapped/original symbol, otherwise assumes flat columns belong to requested symbol. Requires only Close and Volume. Open/High/Low/Adj Close can be absent; present OHLC nulls can survive. No finite/positive price or OHLC-consistency validation here. |
| Current day | For newly fetched frames, `drop_current_or_future_daily_bars` removes dates >= current wall-clock ET date, even after close. It does not use historical target or actual exchange completion/availability. Cache-hit branch returns without this filter; a cache created with current-day inclusion can bypass it for an explicit current target. |
| Errors/partial symbols | Outer download exceptions and empty batches are skipped; warning text exists only if `progress_fn` is supplied. Per-symbol failures can result in an omitted dictionary key. No structured success/failure status or retries/backoff at this layer. Cache write errors propagate; read failures return empty (see below). |
| Unavailable range | Empty or endpoint-insufficient merged history is omitted with an optional stale warning. A holiday lookback start or target can make a valid exchange-complete response fail endpoint checks. An IPO within lookback can fail earliest-date requirement. No listing-boundary diagnosis. |
| Completeness | `_cache_satisfies` tests only min date <= start and max date >= target. Missing interior sessions and bad OHLC pass. Thus **a partial response can be mistaken for complete**. A cache hit has no fresh provider observation; a stale cached symbol omitted by refresh remains excluded if its endpoints still fail. |

**VERIFIED — upstream version-specific evidence.** The permitted lower-bound
[yfinance 0.2.40 `download` source][Y-multi] defaults actions/repair/keepna/back_adjust
off, ignores timezone for daily batches, uppercases/deduplicates symbols, and
catches individual errors into empty frames plus logs. Its [history source][Y-history]
normalizes dates, deduplicates before repair, casts missing volume to zero, drops
action columns when not requested and may remove wholly empty/zero rows. A
returned DataFrame is already a client interpretation, not the original HTTP
payload. `timeout_s` is passed through; this wrapper provides no whole-job deadline.
**UNKNOWN:** behavior of all versions allowed by the unbounded dependency and
the actual version behind historical caches. PR 5B must pin and characterize one
version instead of relying on current defaults.

**INFERRED — additional failure modes:** lower-case input can miss upper-case
MultiIndex output; multiple input aliases can refer to one Yahoo ticker; cache
filename sanitation can collide. A response with valid endpoints can combine
fresh and cached rows without identifying their different vintages. These
deductions follow control flow; they were not reproduced against Yahoo.

## B. Price basis and corporate actions

| Field/topic | Status and evidence | Research interpretation |
| --- | --- | --- |
| Open | **VERIFIED:** lower-bound client `parse_quotes` maps Yahoo quote `open`; no auto-adjust multiplication on this path ([utils.py][Y-utils]). **INFERRED:** commonly shares split basis with Close. **UNKNOWN:** exact provider basis per period. | Do not call it contemporaneous raw Open without external comparison. |
| High | **VERIFIED:** maps quote `high`; same client qualification as Open. **UNKNOWN:** independent split/dividend basis evidence. | Validate basis and OHLC consistency together. |
| Low | **VERIFIED:** maps quote `low`; same client qualification as Open. **UNKNOWN:** independent split/dividend basis evidence. | Same requirement. |
| Close | **VERIFIED:** Yahoo's displayed field definition says split adjusted ([field labels][Y-fields]). **INFERRED:** provider Close is generally split adjusted, excluding dividend adjustment represented separately. **UNKNOWN:** equality of specific API responses to that documented convention. | It is not established raw execution-price history. |
| Adj Close | **VERIFIED:** Yahoo documents adjustment for splits and dividend distributions ([explanation][Y-adjust]); labels also mention capital gains. Client `parse_quotes` falls back to Close when adjusted values are absent. | Diagnostic series; equality to Close is not proof of no actions. Never mix adjusted close with a different OHLC basis for fills. |
| Volume | **VERIFIED:** maps quote `volume`; no independent split conversion in the inspected wrapper. **UNKNOWN:** provider's historical share-unit convention around splits, precision and corrections. | Hypothesis to test: split-adjusted share counts. Do not assert it, rescale it automatically, or infer integrity from price continuity. |
| Splits | **VERIFIED:** wrapper neither retains events nor reconstructs contemporaneous prices. **INFERRED:** later splits can rescale an earlier action-free research interval. | Checking only actions inside holding dates is insufficient; include indicator warmup and the adjustment horizon through retrieval. |
| Dividends/distributions | **VERIFIED:** no cash-flow accounting or retained event feed here. **UNKNOWN:** event completeness, special-distribution treatment and revisions. | Exclude all such events for current replay, including actions within warmup/holding span. An adjusted series is not a cash ledger. |
| Ticker changes/reorganizations | **VERIFIED:** symbol punctuation conversion is the only wrapper mapping; no dated aliases, merger/spinoff/share-class continuity. **UNKNOWN:** provider stitching. | Verify identity before joining any series; do not concatenate old/new tickers by name. |
| Delisting/symbol reuse | **VERIFIED:** neither ingestion nor master establishes historical listing intervals or reuse-safe identifiers. **UNKNOWN:** accessible history and terminal prices for any delisted symbol. | A successful current query does not prove the intended historical security. A last bar is not a realizable delisting payoff. |
| Historical revisions | **VERIFIED:** overlap merging replaces prior values without revision records. **UNKNOWN:** actual revision frequency/magnitude. **INFERRED:** subsequent events/corrections can change historical values. | Archive every retrieval separately and compare common dates. No point-in-time vintage is established by today's history. |

There are **no empirically observed Yahoo results in this audit**. Field labels
were checked as documentation via indexed primary-page text; Yahoo Help direct
opens returned HTTP 429 while indexed Help content was available. That access
limitation and the distinction between webpage definitions and API behavior are
intentional. O/H/L and volume basis remain unresolved rather than promoted to
VERIFIED. Disabling the client's adjustment only prevents its optional additional
OHLC transformation; it cannot undo provider-side adjustments.

**INFERRED — policy decision:** keep current raw/no-action replay unchanged and
make the first export conditional on independently verified raw equivalence,
complete action evidence, and a declared historical availability assumption. A
purely action-free holding interval does not satisfy these gates. A future
`yahoo_split_adjusted_v1` contract could support separate diagnostic experiments
after evidence, but requires new engine semantics and approval, and is deferred.
Blindly reversing splits from an incomplete event list is not an acceptable
unadjusted-price source.

## C. Cache and provenance audit

**VERIFIED** from [prices.py][C-prices]:

| Function | Transformation / storage behavior |
| --- | --- |
| `_normalize_daily_frame` | Coerces dates/numbers, strips timezone without conversion, normalizes to date, drops invalid dates and null Close/Volume. Drops Volume <= 0 except `^TNX`, where zero is allowed. Keeps last duplicate date and sorts. Selects only six price columns. Null O/H/L may survive. No record of removed rows or original tokens. |
| `_read_cached_ohlcv` | Reads `<sanitized_yahoo_symbol>.parquet`, optionally sets Date index, normalizes again. Any Parquet read exception becomes an empty frame; corruption is indistinguishable from cache miss. |
| `_write_cached_ohlcv` | Normalizes, resets Date, writes the same symbol file with `to_parquet(index=False)`. No immutable name, exclusive creation, atomic-write protocol or sidecar provenance. |
| `_merge_ohlcv` | Concatenates existing then fresh and normalizes; valid fresh overlapping rows win. Removed/filtered fresh rows can leave old cached values in place. No correction ledger. |
| `_cache_satisfies` | Checks earliest/latest calendar dates only; no expected-session set or row validation. |
| `_fetch_start_for_symbol` | Empty/insufficient early coverage fetches full lookback; otherwise overlaps latest cached date by seven calendar days, bounded by lookback start. Interior holes/older corrections outside overlap need not be fetched. |
| `refresh_cache=True` | Skips old cache reads, fetches requested lookback and writes over the same file. Can discard previously cached older history; it is not a new immutable full-history revision. |
| `daily_ohlcv_frames_to_table` | Re-normalizes; skips empty symbols, uppercases ticker, renames into a sorted long table; synthesizes missing Adj Close from Close, fills null volume with zero then casts int. Selecting required table columns can fail when O/H/L columns are absent. No diagnostics or provenance survives. |

[Price tests][C-price-tests] assert cache reuse/incremental refresh, explicit end
date, omission of a stale symbol absent from a partial refresh, table conversion,
current-day filtering and the `^TNX` exception. Those assertions use mocked
downloads, not provider coverage. [Daily-report call sites][C-report] pass a
resolved historical report date; they do not establish historical publication
availability or cache vintage. Its report outputs were not inspected or used.

**VERIFIED — preservation matrix:** selected normalized numeric values may be
retained, but original provider values/row order/types/missingness are **not
preserved faithfully**. No download timestamp, requested/returned range record,
provider identity field, adjustment convention, explicit symbol mapping, source
revision, content hashes, or before/after correction history is written by this
cache code. Directory naming suggests Yahoo; it is not an attestation. No hidden
Parquet metadata is assumed because this writer adds none of these fields.

**INFERRED:** dropped zero-volume days could be legitimate observations or data
errors; silently deleting either hides an expected session. Last-row-wins
deduplication hides conflicting prices. Mixed old/new split bases outside the
seven-day overlap can create artificial discontinuities. Refreshing must never
change previously frozen research input bytes.

Recommended layout (new directories, no existing inputs overwritten):

```text
provider_snapshots/yahoo/<request-id>/
  request.json  response-*.json  client-frame.json  retrieval.json  hashes.json
canonical/<dataset-content-hash>/
  bars.csv  actions.json  identities.json  schedule.json  quality.json  manifest.json
research_datasets/<immutable-version>/
  data.csv  data_manifest.json  provenance.json  hashes.json
```

`response-*.json` means original response bytes, not reserialized parsed JSON;
the extension does not promise valid JSON on an error. Exclude cookies, tokens,
credentials and personal paths. Retain all market-data payload rows/nulls and
safe HTTP status metadata. If the chosen pinned client cannot expose payloads
through a supported boundary, mark `capture_level="client_return"`, preserve a
lossless frame (index/columns/order/dtypes/nulls), and explicitly record that wire
fidelity and already-dropped rows are unavailable. Do not claim a raw-provider
archive or pass the raw-payload acceptance gate with only `yf.download` output.
Resolve capture capability before choosing the PR 5B fetch implementation.

Use versioned `yahoo_snapshot_v1`, `canonical_daily_v1`, and
`yahoo_provenance_v1` schemas; retain the current replay manifest field contract.
SHA-256 hashes cover exact payload, frame, request, mapping, schedule, action
evidence, canonical CSV, quality report, converter/config and dependency identity.
The snapshot manifest records safe request parameters, actual client version and
artifact hash, provider/endpoint, retrieval start/end UTC, status/errors, requested
range and returned min/max/count, currency, exchange/timezone, adjustment facts
and unknowns. Retrieval time, dataset creation time, event observation time and
historical bar availability must remain different fields.

Conversion is deterministic for the same snapshot/config: explicit schema and
column order, UTF-8/LF CSV, locale-independent round-trip numeric representation
without price rounding, validated exchange-local dates, and recorded sorting
only after detecting duplicates/order anomalies. Reject conflicts/null required
fields rather than choosing a row. Do not fabricate Adj Close or cast fractional
volume away. Emit every rejection into quality diagnostics. New retrieval creates
a new snapshot and revision-diff report, never mutates an old canonical dataset.
Dataset content hashes should exclude wall-clock retrieval metadata but reference
the separate hashed provenance; preserve both identities.

## D. Calendar integrity

**VERIFIED — comparison:** [cannoslim market_calendar.py][C-calendar] implements
weekends and recurring US holidays, special Saturday New Year handling, and
Juneteenth starting 2022. It returns dates/booleans, not open/close timestamps;
there is no early-close schedule, DST handling, exceptional-closure table, listing
history, or security suspension logic. MLK is applied to every year without a
historical effective-date boundary. [Calendar tests][C-calendar-tests] cover only
2026 Juneteenth and the preceding session. Ingestion does not call this module;
it uses pandas BDay even though report-date call sites use the manual calendar.

The equity loader validates explicit hours/offset conversions and missing rows
against supplied sessions, including 13:00 closes; it cannot detect a real session
omitted from **both** bars and manifest. Nor does it independently reject a weekday
holiday falsely supplied as a session. Neither repository has an authoritative
historical reconciliation capability.

**VERIFIED — primary calendar evidence:** [NYSE hours/calendar][X-hours] documents
09:30–16:00 ET and specified 13:00 closes. [NYSE's January 2025 closure memo][X-carter]
documents the exceptional January 9 closure absent from the manual rules.
[exchange_calendars XNYS source][X-library] has historical holiday, special-close
and adhoc-closure definitions. **INFERRED recommendation:** use a pinned release
of `exchange_calendars` as schedule generator, reconcile with archived exchange
notices and date its supported range. The library is not the exchange authority;
freeze its version, overrides, notice references and exact schedule hash. Confirm
Nasdaq/Arca session alignment explicitly for non-NYSE listings rather than lying
about listing venue to meet the current XNYS schedule contract. Do not add a
dependency or broaden supported sessions in this PR.

Proposed reconciliation algorithm, independent of returned bar dates:

1. Generate the full authoritative exchange schedule over requested inclusive
   dates, with UTC open/close derived from ET, early-close and closure evidence.
   Compare this schedule independently to the manifest, not just to the CSV.
2. Resolve security identity and independently evidenced first/last tradable
   session intervals. Missing first/last Yahoo rows do not establish IPO/delisting.
3. Classify each date using schedule and listing evidence:

   | Classification | Rule / action |
   | --- | --- |
   | Expected session with a bar | Listed, exchange open, exactly one valid bar: eligible for remaining checks. |
   | Expected session without a bar | Listed and open, no observation: explicit missing-session failure. |
   | Legitimate exchange closure | Closed by schedule/notice; no bar expected. A returned bar is an off-calendar error. |
   | Pre-listing/post-delisting | Independent dated identity evidence places date outside trading interval; report separately, never infer from absent rows. |
   | Unknown security-specific gap | Listing boundary uncertain, unexplained missing day, or suspected suspension: quarantine for evidence. A confirmed suspension is separately annotated and still blocks contiguous current replay. |

4. Also diagnose bars outside identity interval, duplicate dates, invalid local
   timestamps, and schedule disagreements. Stop export on any unresolved gap.
   Do not remove a session from the manifest to make input pass; no forward fill.
5. A pre-listing boundary can yield insufficient warmup (WATCH), not eligibility.
   Delisting/reorganization crossing the experiment blocks current replay; forced
   end-of-data exit is not delisting settlement accounting.

## E. Historical coverage and selection bias

**VERIFIED — [universe.py][C-universe]** reads current Nasdaq Trader directories,
filters names/ETF/test issues and non-normal Nasdaq financial status, deduplicates
by symbol, or supplies a fixed starter list. There are no historical membership
intervals. Excluding distressed issues today is especially material to survival
bias. **VERIFIED — [security_master.py][C-master]** uses requested tickers, live
metadata, locally inferred SEC filenames or sample tickers. It assigns
`security_id=ticker` and `is_active=True` to all rows. Optional SEC resolution
silently catches exceptions. [SEC helpers][C-sec] use a current ticker map/cache;
CIK metadata is not a dated share-class/listing identity. No valid-from/to or
known-at fields make this master point-in-time safe. [Dataset call site][C-dataset]
joins current metadata and uses Adj Close returns/dollar volume; its file named
`raw_market/daily_prices.parquet` is already normalized client data.

| Capability / experiment | Finding and permissible conclusion |
| --- | --- |
| >=10 years daily history | **VERIFIED:** API documents `10y`/`max` and wrapper accepts calendar-day lookback without a ten-year cap. **UNKNOWN:** actual usable span and completeness per security. Endpoint logic can reject a request starting on a holiday or before IPO. |
| Active stocks | **INFERRED:** plausible initial Yahoo use case. **UNKNOWN:** present availability for any basket member; no request ran. |
| Delisted/renamed stocks | **UNKNOWN:** retention, alias stitching, endpoints, licensing/usable access. Wrapper/master supply no evidence or recovery path. No blanket claim that all delisted prices are either available or unavailable. |
| Stable identities | **VERIFIED:** missing from inspected ingestion/master; ticker identity is mutable and reusable. |
| Historical index or screening universes | **VERIFIED:** neither Yahoo price wrapper nor inspected master supplies dated index/screen membership. **UNKNOWN:** existence of any separately licensed archive; not inferred here. |
| Known historical candidate | **INFERRED:** bounded mechanics experiment can proceed after identity/basis/calendar gates, with authentic dated observation or an explicit hindsight case-study label. Historical bars alone do not establish candidate availability or an unbiased selection process. |
| Manually curated watchlist | **INFERRED:** defensible conditional results for the frozen named list; today-chosen list carries selection/survival bias and cannot represent historical opportunity set. Retain all retrieval failures. |
| Broad-universe strategy comparison | **INFERRED:** current directory/master is unsuitable for survival-free inference; needs archived membership, delisted coverage and dated identities before comparing strategies. |
| DeepVue/Mantis reconstruction | **VERIFIED:** unsupported in current equity qualification. **INFERRED:** impossible to establish historical screening membership from OHLCV or today's metadata. Require original dated candidate records; never manufacture ratings or membership. |

## Reuse matrix

Classifications: REUSE = retain under documented contract; ADAPT = useful but
change behavior; REIMPLEMENT = current design fails integrity needs;
KEEP_CANNOSLIM = application-specific; MISSING = required capability absent in
the inspected scopes of both repositories. Owners below are proposed PR 5B
components, not new packages or approved extraction work.

| Source/function | Actual behavior | Classification | Reason | Future owner | Required acceptance test |
| --- | --- | --- | --- | --- | --- |
| [universe.py][C-universe] `yahoo_symbol` | Dot/slash to dash only | REUSE | Narrow syntax helper, only after verified mapping; not identity resolution | Optional provider boundary | BRK.B/BRK/B alias collision is detected; original and provider symbols both retained. |
| [prices.py][C-prices] `drop_current_or_future_daily_bars` | Keeps dates before explicit ET cutoff | ADAPT | Pure predicate useful with explicit cutoff; current clock/completion logic insufficient | Snapshot validator | Fixed-clock early-close/current-day/cache-hit cases; exclusion logged, payload retained. |
| [prices.py][C-prices] `_extract_one_symbol`, `fetch_yahoo_daily_ohlcv` | Batched yfinance with optional warnings/omissions | ADAPT | Reuse parameter and frame-shape knowledge, replace result/error/provenance boundary | Optional Yahoo adapter | Mixed successful/failed batch produces per-request-symbol statuses; no alias/case mix-up. |
| [prices.py][C-prices] `_normalize_daily_frame` | Drops/coerces/deduplicates/sorts | REIMPLEMENT | Lossy behavior conflicts with auditability | Canonical validator | Preserve raw null/zero/duplicate rows; reject canonical conflicts with diagnostic row references. |
| [prices.py][C-prices] `_read_cached_ohlcv`, `_write_cached_ohlcv`, `_merge_ohlcv` | Mutable per-ticker normalized Parquet | REIMPLEMENT | No immutable vintages or correction history | Snapshot store | Changed overlap yields new hash and diff; prior bytes unchanged; corruption explicit. |
| [prices.py][C-prices] `_cache_satisfies`, `_fetch_start_for_symbol`, `_target_end_date` | Endpoints/BDay/seven-day overlap | REIMPLEMENT | Interior holes, holidays and revision horizon unvalidated | Coverage validator | Missing interior session fails even with correct endpoints; holiday endpoints resolve from schedule. |
| [prices.py][C-prices] `daily_ohlcv_frames_to_table` | Long table, fabricated Adj Close, integer volume | ADAPT | Retain layout idea, remove silent transformations | Canonical converter | Null required columns/fractional volume diagnosed; no manufactured adjusted values. |
| [market_calendar.py][C-calendar] holiday/trading-day helpers | Manual recurring rules | REIMPLEMENT | No exceptional closures or session times | Calendar adapter | DST, observed holidays, 13:00 close, January 9 2025 closure, omitted-from-both failure. |
| [universe.py][C-universe] `load_us_common_stocks`, `starter_common_stocks` | Current filtered or fixed universe | KEEP_CANNOSLIM | Useful current-app input, not historical inclusion evidence | cannoslim | Future equity path rejects current-list metadata as historical membership. |
| [security_master.py][C-master] `build_security_master` | Ticker identity/current metadata/all active | KEEP_CANNOSLIM | Do not port current master as historical identities | cannoslim; separate equity mapping | Renames/reuse require dated evidence; no ticker-only continuity assertion. |
| [dataset.py][C-dataset] `curate_market_data`, `build_breakout_dataset`; [prices.py][C-prices] `rolling_high_and_ratio` | Adj Close features, application labels/ranks or rolling highs | KEEP_CANNOSLIM | Outside one-candidate source audit and current policy | cannoslim | Equity adapter has no dependency/import on complete application or these features. |
| [data.py](../src/equity_research/data.py) `load_dataset` | Strict CSV/schedule/raw checks | REUSE | Keep last offline gate; augment upstream independent evidence | Existing equity data layer | Unsupported basis/actions and missing bars still fail. |
| [reporting.py](../src/equity_research/reporting.py) `canonical`, `run_experiment` | Immutable captured inputs/hashes | REUSE | Already deterministic/exclusive; provenance sidecar must be linked by hash | Existing equity reporting | Same frozen inputs reproduce; later provider refresh cannot change run. |
| No existing provider snapshot/calendar reconciliation/action attestation/datum-vintage identity functions | Required capabilities not present in audited paths | MISSING | Needed before real data may be admitted | New optional data preparation modules | Payload-to-manifest lineage, independently complete schedule, event-horizon and historical-availability gates. |

No component is approved for extraction here. Favor a small local adapter and
explicit mapping rule over importing the whole cannoslim package. Shared
mathematics remain in the hash-pinned vendor wheel; do not duplicate ATR or touch
finwhaling.

## F. Proposed provider-quality pilot (not executed)

Each interval is inclusive in the proposal; encode its end as next calendar day
for the documented exclusive API end. Five securities plus two short AAPL windows
are quality cases, not a strategy universe. Access/retention/terms must permit
use; unavailable cases remain visible as failures/unknowns, not replacements
chosen after seeing results.

| Proposed security | Interval(s) | Purpose and independent reference |
| --- | --- | --- |
| SPY | 2024-11-20–2024-12-06; optional later range audit 2014-01-01–2024-12-31 | ETF liquidity baseline, holiday/early close and distributions. Long interval is a separately authorized, one-symbol coverage check for >=10 years, not evidence already obtained; verify issuer distribution and exchange records before execution. |
| AAPL | 2014-05-27–2014-06-20 and 2020-08-17–2020-09-11 | Seven-for-one and four-for-one cases; compare all price fields and volume units with issuer/exchange contemporaneous references. [Apple dividend/split history][P-apple] identifies split-adjusted trading dates June 9 2014 and August 31 2020; do not confuse record/payment dates with sessions. |
| MSFT | 2024-02-01–2024-03-01 | Dividend-paying-stock case; establish ex-date/amount from issuer notice first, then test Adj Close factor and unadjusted OHLC hypothesis. Coverage/action values are UNKNOWN in this audit. |
| FB / META (one security, two aliases) | 2022-05-23–2022-06-24 | Rename continuity, duplicate overlap and historical query identity. [Issuer announcement][P-meta] specifies June 9 2022 ticker change; query outcomes/stitching remain UNKNOWN. |
| TWTR (conditional) | 2022-10-03–2022-11-04 | Delisted case, only if accessible and legally usable. [Issuer SEC filing][P-twitter] says trading was suspended before October 28 2022 open following merger. Record failure if unavailable; never fabricate terminal bars/payoff or substitute another security silently. |

For **every security and interval**, save request identity, retrieval UTC,
provider/endpoint/client versions, safe errors, original snapshot and hashes.
Measure requested vs available min/max, row counts and independently expected
sessions; list missing/extra sessions, duplicate/conflicting dates, missing OHLCV,
nonfinite/range errors, zero/negative/fractional volume and price discontinuities.
Separate legitimate closure and evidenced listing boundaries from unknown gaps.
Do not count only retained/normalized rows.

Compare pre/post split price factors to issuer ratios and contemporaneous quotes;
compare volume to independent share-count units (a volume jump alone cannot prove
adjustment because activity changes). Check Adj Close/Close factors against
independently dated dividends/distributions and explain every mismatch, including
later actions outside a short query. Preserve tolerances, precision and reference
hashes in the pilot configuration before examining results. Unexplained factors
or action-event disagreements block replay export.

Retrieve each short request twice in separate snapshots (same arguments/client,
proposed 24–48 hours apart), compare exact payload hashes and semantic common-date
values separately, and report every revision. Two equal downloads demonstrate
only that interval of stability, never permanent immutability or historical PIT
availability. Test explicit error/omitted-symbol handling with offline fixtures;
do not force network failures or run probes in PR 5A. Long-range availability
remains UNKNOWN until the separately authorized coverage check.

## Proposed PR 5B architecture and sequencing

1. **Provider fetch boundary.** Optional ingestion command, never invoked by
   replay/tests. Explicit security/request/date range, pinned optional client
   dependencies and all behavior-changing flags, small bounded requests and
   per-symbol typed outcome. Capture transport responses through supported
   instrumentation if possible; no private client-global error state as an API.
   Validate client shape/default changes with fixtures and fail closed.
2. **Raw immutable snapshots.** Implement the snapshot/provenance design above
   with exclusive creation, hashes and structured error records. Capture failures
   too. Resolve wire-vs-client-return capture honestly before calling it raw.
3. **Security identity.** For first experiment, a reviewed one-security mapping
   with stable local ID, provider symbol, historical alias, venue/currency,
   validity interval, known-at/evidence references and listing boundaries. No
   automatic current-universe import; no CIK-as-share-class shortcut.
4. **Canonical OHLCV.** Single-security daily table with explicit session key,
   OHLCV, source snapshot hash/row locator and separate optional Adj Close/action
   diagnostics. Exact replay CSV only at export; no extra columns leak to loader.
5. **Adjustment basis.** Per-field metadata: split basis, dividend/capital-gain
   basis, volume units, adjustment anchor/horizon, evidence and UNKNOWNs. Preserve
   `auto_adjust=False` as a request fact, not a basis label. Reject raw export on
   UNKNOWN; never fabricate raw prices by incomplete inverse adjustments.
6. **Calendar validation.** Pin generator/authoritative references, freeze full
   schedule, reconcile identity intervals and returned dates with the algorithm
   above. Retain listing exchange separately from XNYS session convention.
7. **Corporate actions.** Snapshot provider events plus independent issuer/
   exchange evidence, including warmup and later split adjustment horizon.
   Distinguish missing event feed from an evidenced empty action set. Actions or
   uncertain raw equivalence block the current contract.
8. **Quality diagnostics.** Structured findings by security/session/source row;
   requested and returned counts, fields, errors, revisions and reconciliation
   categories. No symbol omission, silent repair or success-only report.
9. **Manifest/export.** Freeze accepted CSV, existing manifest fields and a
   hashed provenance sidecar linking payloads, converter version, dependencies,
   mapping, actions and schedule. Fill `source_revision` from captured snapshot
   identity, never a fictitious Yahoo revision. Actual creation/retrieval times
   remain separate; retain immutable versions on refresh.
10. **Replay integration/timing.** Call existing `load_dataset` then existing
    CLI only on explicit frozen paths; no cache refresh/network from replay.
    Snapshot retrieval today proves availability today, not on a historical
    decision date. If historical publication latency is unknown, actual PIT bar
    availability stays UNKNOWN. A proposed model (for example close+30 minutes,
    including early closes) must be reviewed and labeled an assumption in
    provenance/`availability_convention`, not measured vendor publication. The
    current loader needs concrete `available_at` before next open, so refuse
    historical export until that model or genuine timestamp evidence is accepted.
    A prospective recorded candidate cannot be manufactured from a later scan.
11. **Failure policies.** Fail export for hash/schema errors, identity ambiguity,
    incomplete sessions, required nulls, conflicts, unsupported/unknown basis,
    actions, unresolved availability and acquisition failures. Preserve failed
    snapshots/reports; retries create attempts rather than overwriting. Warnings
    cannot waive correctness. No forward fill or hidden date truncation.
12. **Offline acceptance.** Use tiny deterministic hand-authored provider-like
    fixtures with fixed timestamps and event ratios; label them synthetic. Keep
    socket denial and existing deterministic replay tests. Provider pilot evidence
    is a separate manual artifact and must not be described as an offline test.

**Required for first real-stock experiment:** reviewed identity and candidate
evidence; full warmup/holding schedule; snapshot/provenance capture; basis/action
proof; latency evidence or accepted labeled model; strict quality gates; frozen
CSV/manifest; existing engine/reproducibility/accounting regression checks. If any
gate lacks evidence, stop at adapter diagnostics.

**Defer:** broad-universe ingestion, historical membership reconstruction,
automated rename/delisting coverage, event-aware replay, adjusted-price engine
contracts, portfolio statistics, cache-refresh optimization and vendor selection.
None is needed to assess a single verified candidate, and the pilot basket does
not expand the one-symbol long-swing engine into a portfolio.

## PR 5B acceptance criteria

| Gate | Concrete offline evidence required |
| --- | --- |
| Boundary/errors | Fake client verifies exact inclusive/exclusive request and every explicit flag; partial/empty/timeout/symbol-case/alias fixtures yield structured outcomes and no successful incomplete export. |
| Snapshot fidelity | Original payload bytes and hashes survive parsing, duplicate/null/zero rows included; client-return-only fixture cannot satisfy wire-capture claim. Reusing snapshot/dataset path fails. |
| Revisions | Two fixed responses differing on an old overlapping date produce separate immutable snapshots and semantic diffs; refreshing cannot alter an already frozen dataset/run. Corrections outside a seven-day window are detectable by full comparison. |
| Canonical validity | Missing O/H/L/Volume, NaN/inf, inconsistent OHLC, conflicting dates, off-calendar dates and ambiguous mappings reject with source locators. Zero-volume row remains observable and policy is explicit; no invented Adj Close. |
| Calendar | Hand fixtures cover observed holiday, early close, winter/summer UTC offsets, exceptional closure, IPO boundary, suspension and delisting. A real expected session removed from both candidate CSV and manifest is caught against independent schedule. |
| Basis/actions | Split 4:1 fixture, later split outside query, dividend/distribution, rename and missing-event evidence all block current raw/no-action export. Only evidenced raw-equivalent no-action fixture passes. Volume basis UNKNOWN cannot become verified by inference. |
| Timing | Retrieval time cannot masquerade as historical availability. Unknown latency blocks absent reviewed model; accepted model stays labeled. Post-close/late observation and poisoned future bars preserve existing qualification/entry behavior. |
| Manifest/replay | Exact CSV hash, provenance hashes, versioned converter/config and schedule; existing loader remains strict. Same frozen input bytes produce identical artifacts; later retrieval has no effect. No production replay network path. |
| Accounting/scope | Existing actual-initial-risk and gross/slippage/commission/fees/net reconciliation stays intact; shared wheel unchanged; one candidate/symbol/policy. |
| Provider evidence (separate from tests) | Pilot reports observed coverage/errors/factors/revisions and missing evidence honestly. Synthetic passes alone cannot authorize real-price raw equivalence, PIT claims, survival-free research or an edge claim. |

## Open questions requiring evidence

- **UNKNOWN:** Exact API OHLC split/dividend convention and adjustment anchor for
  each security/vintage; volume share units and consistency with split-adjusted
  prices. Can independent contemporaneous quotes prove raw equivalence?
- **UNKNOWN:** Event completeness, revisions, special distributions/spinoffs,
  and later splits outside the requested range. Can genuinely unadjusted prices
  be obtained without unreliable inverse reconstruction?
- **UNKNOWN:** Per-security ten-year completeness, legacy alias queries, delisted
  retention, stable identifiers and symbol reuse handling. No survival-free
  membership archive has been established.
- **UNKNOWN:** Historical publication/finalization latency and vintage revisions;
  today's response cannot reconstruct what was known at a past close.
- **UNKNOWN:** Supported transport-level capture in the client version selected
  for PR 5B and rights to retrieve, retain and share pilot snapshots. Do not assume
  public access grants redistribution rights; no subscription purchase proposed.
- **UNKNOWN:** Which exchange/calendar evidence and historical supported range
  will be frozen for the first selected security. All exceptional closures need
  explicit coverage; today's published calendar is not a full historical archive.

## PR 5A validation record

Required reading completed: root [AGENTS.md](../AGENTS.md),
[README.md](../README.md), the two project specifications linked above; required
equity modules/tests; cannoslim [AGENTS.md][C-agents], project/dependency file,
prices/universe/calendar/master and price tests, plus relevant call sites and
calendar/SEC helpers linked below. Validation performed:

- Target regression: `python -m pytest -q`, using the existing local PR 4 Python
  environment (Python 3.12.9, pytest 9.0.2; no new installation), **58 passed in
  6.33s**. Pytest resolves this checkout's `src` via project configuration. This
  includes the offline installation test and is not a provider/strategy probe.
- Relative links resolved against this document; reference labels resolved;
  pinned cannoslim paths checked with `git show SHA:path` and compared byte for
  byte to inspected files. Named source functions/classes checked against ASTs.
  Both repository revisions were also confirmed accessible through GitHub.
- Primary documentation links checked through web retrieval/indexed source
  text. Yahoo Help direct HTTP 429 is recorded above; no claim of universal
  HTTP-200 link availability. No strategy-price evidence was taken from search.
- Git whitespace checks and changed-path review confirm this document is the
  sole target change; no production/test/dependency changes are included.

Source/test inspection of cannoslim is not a claim of executing its tests; they
were not run, preserving that read-only checkout.

Only this audit document is intended for the PR. No provider probe or strategy
backtest ran, no existing run directory or immutable input was revised, and no
production/test code, dependency, cannoslim or finwhaling file was changed.
Do not start PR 5B or merge this PR before review.

## Source references

[C-agents]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/AGENTS.md
[C-project]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/pyproject.toml
[C-prices]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/prices.py
[C-universe]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/universe.py
[C-calendar]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/market_calendar.py
[C-master]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/breakout_ml/security_master.py
[C-sec]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/breakout_ml/sec_fundamentals.py
[C-dataset]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/breakout_ml/dataset.py
[C-calendar-tests]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/tests/test_market_calendar.py
[C-price-tests]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/tests/test_prices.py
[C-report]: https://github.com/atoultaro/cannoslim/blob/6f1a01d1db2cbc24abc845c190af7acaf6701834/src/cannoslim/daily_stock_report.py
[Y-download]: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
[Y-multi]: https://raw.githubusercontent.com/ranaroussi/yfinance/0.2.40/yfinance/multi.py
[Y-history]: https://raw.githubusercontent.com/ranaroussi/yfinance/0.2.40/yfinance/scrapers/history.py
[Y-utils]: https://raw.githubusercontent.com/ranaroussi/yfinance/0.2.40/yfinance/utils.py
[Y-fields]: https://finance.yahoo.com/quote/%5EGSPC/history/
[Y-adjust]: https://in.help.yahoo.com/kb/adjusted-close-sln28256.html
[X-hours]: https://www.nyse.com/trade/hours-calendars
[X-carter]: https://www.nyse.com/publicdocs/nyse/markets/american-options/rule-interpretations/2025/National_Day_of_Mourning_20250102.pdf
[X-library]: https://raw.githubusercontent.com/gerrymanoim/exchange_calendars/master/exchange_calendars/exchange_calendar_xnys.py
[P-apple]: https://investor.apple.com/dividend-history/default.aspx
[P-meta]: https://investor.atmeta.com/investor-news/press-release-details/2022/Meta-Platforms-Inc.-to-Change-Ticker-Symbol-to-META-on-June-9/default.aspx
[P-twitter]: https://www.sec.gov/Archives/edgar/data/1418091/000119312522272772/d411753d8k.htm
