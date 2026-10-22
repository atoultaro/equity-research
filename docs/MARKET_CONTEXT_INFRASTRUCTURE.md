# Historical MarketContext infrastructure (PR 7A)

MarketContext supplies continuous daily trend, volatility and participation
measurements to future research consumers. It does not approve, suppress, resize,
execute or liquidate a trade, change stops, select a strategy or filter a setup.
Minervini-style and JLaw-style consumers can inspect the same observations in
every descriptive state. No universal bull-market filter or profitability claim
is implemented. No PR 7B work is included.

Branch: `feat/market-context-infrastructure-v1`. Base:
`9e03cff0374c35b67fb3acca36cc77ea99636c3b`, latest main containing merged PR 6B.
The authoritative PR 7A brief permits the specifically confirmed historical-only
acquisition beyond the older AGENTS.md provider restriction, and requires a fresh
paper/read-only preflight before broker access. For the real demonstration, the
user explicitly changed the session to a **non-paper, Read-Only API connection on
port 7496**. This current instruction replaces the paper-mode prerequisite for
this historical-only run; no trading/account activity is authorized or implemented.
Execution admission/accounting,
event publication and corporate-action window policies remain unchanged.

## Current demonstration and live status

**Real reference acquisition and context generation passed.** SPY, QQQ and RSP
each have 995 observed daily sessions, including 292 preceding the evaluation
interval. The real MarketContext has 703 complete core rows. Results, exact
request parameters, audits and hashes are in the
[current real-data evidence](evidence/market-context-v2.json).

The user replied to the explicit current-session/authorization check with:
“Now the non-paper account with port 7496. Read-only.” The current endpoint is
`127.0.0.1:7496`, client ID `51971`; a local TWS listener was observed before
connecting. No paper-account claim is made. Session/settings evidence comes from
the user's reply, not an account query or programmatic settings inspection.
Successful guarded connections and smoke requests establish scoped connectivity
and historical access. No TWS settings were changed, no new TWS session was
started and no account identifier or authentication secret was persisted.

The [initial evidence](evidence/market-context-v1.json) preserves the earlier
synthetic-only outcome while preflight was pending. Real acquisitions and context
outputs use new immutable paths; the synthetic demonstration and older AAPL/GOOG
artifacts remain intact. Normal tests and the synthetic example still require no
TWS or IBKR SDK. Previous PR 5E/6A/6B sessions were not treated as current proof.

## Reference instruments and identity

| Role | Independently reviewed issuer description/source | Actual PR 7A IBKR identity |
| --- | --- | --- |
| SPY | [SPDR S&P 500 ETF Trust](https://www.ssga.com/us/en/institutional/etfs/state-street-sp-500-etf-trust-spy): large-cap US equity ETF proxy | conId **756733**, primary **ARCA**, trading class SPY |
| QQQ | [Invesco QQQ Trust, Series 1](https://www.invesco.com/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html): Nasdaq-100 ETF proxy | conId **320227571**, primary **NASDAQ**, trading class NMS |
| RSP | [Invesco S&P 500 Equal Weight ETF](https://www.invesco.com/us/en/financial-products/etfs/invesco-sp-500-equal-weight-etf.html): equal-weight S&P 500 ETF proxy | conId **319359375**, primary **ARCA**, trading class RSP |

Issuer product descriptions were reviewed separately from broker qualification;
the Invesco product bodies were dynamic, with indexed issuer descriptions supplying
the fund/index names. This does not prove historical constituent membership or
legal-structure/listing continuity. SPY is an ETF, not the S&P 500 index itself;
QQQ is not a technology-sector index. The synthetic mappings/contract IDs in the
example are fixtures and are never represented as actual qualification.

Discovery qualified exactly these USD/STK symbols on SMART, without supplying
a conId or primaryExchange. Each returned one exact-symbol contract; actual
primary designations and conIds then became explicit mappings for the existing
strict historical adapter. The values above were observed, not guessed or copied
from old instruments. Research identities are `research:SPY:ETF:USD:v1`,
`research:QQQ:ETF:USD:v1` and `research:RSP:ETF:USD:v1`. Qualified long names,
all contract fields and source identities are sealed in the acquisition setup.
Context validation checks distinct qualified identities and exact role mappings.

## Acquisition and warmup

Evaluation is fixed at **2024-01-02 through 2026-10-20**, the same 703 expected
XNYS-convention sessions as AAPL and GOOG. Wider acquisition:
**2022-11-01 through 2026-10-20**, 995 expected and **995 observed sessions per
instrument**, independently reconciled to the pinned calendar.

The exact largest window is **220 observations including the evaluation session**:
SMA200 at t uses t−199…t; SMA200 at t−20 uses t−219…t−20. Therefore 219 preceding
expected sessions are required. The acquired buffer supplies 292 preceding
sessions; the minimum start for the first evaluation session is February 16, 2023.
`required_history_sessions()` derives the maximum from the versioned feature
definitions. Warmup is counted in exchange sessions, not approximate calendar days.

Other required counts are SMA50/150/200: 50/150/200; ATR14: 15; 20-return realized
volatility: 21; trailing 60-session return: 61; ratio average: 50. Synthetic tests
check availability immediately before and at observation 220. A short or gapped
history does not get a seeded SMA200 or a forward-filled session.

The existing `IBKRDailyProvider`, normalization, native capture, cache and price
freeze are reused. Live workflow: fresh explicit preflight; actual independent
qualification; five completed sessions (October 14–20) for all three instruments;
then bounded 30-calendar-day chunks over the wider interval. One provider
instance/pacer covered all instruments and both phases, using the existing two-second,
15-second identical-request and 60/600-second limits. Do not run overlapping jobs.
No Yahoo fallback, account/portfolio/position/balance/execution request or order
operation is permitted. Raw historical responses remain ignored/local.

## Repeated provider failures

Known DATA_PERMISSION still stops immediately. Pacing, timeout and connection
failures retain their existing bounded transient retries. NO_DATA can be specific
to an old chunk and is not treated as a global fatal condition.

Two consecutive failed chunks with the same integer code and PROVIDER_ERROR
category stop subsequent chunks for that instrument. A success, changed numeric
code or another category resets the streak. Duplicate error callbacks are not
additional failures. This is an **apparent-persistence heuristic**, not proof that
every code 162 has the same cause or means permission failure. No new string-based
classification is inferred from GOOG's single “different IP” observation.

Snapshots and batch reports retain `termination`: reason, code/category where
applicable, last attempted end, unattempted start and original requested end.
Every attempted request/parameter and safe numeric error observation survives.
Native bars returned alongside a request error are now retained but explicitly
not selected into research rows. Native-row indices for successful chunks remain
exact. No automatic broker reconfiguration, access workaround or retry restart
is added. Deterministic tests cover exception and callback failure paths, reset
conditions, transient retries, date-specific no-data and report propagation.

## Schema and shared provenance

`market_context_v1` has a shared manifest, feature definitions and daily rows.
The manifest records the market-reference-set ID, exact source dataset hashes,
`market_features_v1`, evaluation interval, warmup requirement, availability
configuration, native-price interpretation and unchanged execution admission.
It records historical input-vintage availability as UNKNOWN.

Each daily row contains:

- Schema/session label, last included observation, `available_at`, availability
  status and the explicit reconstructed/not-verified dissemination label.
- `trend_features`, `volatility_features`, `participation_proxies`,
  `breadth_features` and `leadership_features`.
- Each feature's numeric value or null, AVAILABLE/UNAVAILABLE status, reason and
  last included observation (null when no valid calculation exists).
- Quality counts by group, exact `missing_features` and an optional descriptive
  state. Missing optional fields do not invalidate usable core features.

`feature_definitions.json` binds each feature to instruments, input security IDs,
source dataset hashes, formula/version, units, exact observation count and window
convention. Its availability inherits the daily row. Instrument mapping,
qualification and native basis are retained once in shared reference lineage;
large native metadata is not repeated in every observation. As-of results include
the shared identities/hashes and feature-definition version.

## Formulas and units

All continuous changes/normalized values are **fractions**, not percentage points:
0.01 means 1%. The ratio level has native-price-ratio units. Current completed
session t is included. All windows require consecutive expected sessions.

| Group | Instruments/features | Exact definition |
| --- | --- | --- |
| Trend | SPY Close/SMA50, /SMA150, /SMA200; QQQ and RSP Close/SMA50, /SMA200 | Close[t] / mean(last N closes through t) − 1 |
| Trend | SPY SMA50/SMA200, SMA50/SMA150, SMA150/SMA200; QQQ SMA50/SMA200 | Short SMA[t] / long SMA[t] − 1 |
| Trend | SPY and QQQ SMA200 slope20 | SMA200[t] / SMA200[t−20] − 1 |
| Trend | SPY and QQQ return20/60; RSP return20 | Close[t] / Close[t−N] − 1 |
| Volatility | SPY and QQQ ATR14/Close | Shared simple ATR14[t] / Close[t]; 14 true ranges from 15 bars |
| Volatility | SPY and QQQ realized volatility20 | Population standard deviation (`ddof=0`) of 20 simple close-to-close returns, not annualized |
| Volatility | SPY range20/Close | (max High[t−19…t] − min Low[t−19…t]) / Close[t] |
| Participation | RSP/SPY level | RSP Close[t] / SPY Close[t] |
| Participation | Ratio change20 | Ratio[t] / Ratio[t−20] − 1 |
| Participation | Ratio relative_sma50 | Ratio[t] / mean(Ratio[t−49…t]) − 1 |

SMA uses the same arithmetic-mean convention as the historical indicator reader.
ATR calls the pinned market-shared `true_range` and `atr_simple_series`; no ATR
formula is copied. The RV window includes return t−1→t and needs the preceding
21 closes. No annualized, implied or intraday volatility is mixed into these fields.
The optional separate ratio slope is omitted; the existing 20-session ratio change
already expresses that endpoint-relative measurement.

## Timing and as-of lookup

Default configuration is **regular-session close plus 60 minutes**. This is a
research availability assumption, not verified historical vendor publication.
Regular 16:00 New York closes become model-eligible after 17:00; a 13:00 early
close after 14:00. UTC timestamps come from the pinned XNYS schedule, handling
DST, holidays and exceptional closures. The model never equates the session's
date label or close timestamp with actual dissemination.

`context.context_as_of(offset_aware_timestamp)` returns the latest frozen row whose
modeled `available_at` is **strictly earlier** than the decision. Equality is not
eligible. Before the first eligible evaluation row, it returns UNAVAILABLE with
`NO_HISTORICALLY_ELIGIBLE_SNAPSHOT`. It never substitutes a later row. A daytime
query uses the latest permissible completed-session row; holidays/weekends retain
the most recent eligible session. There is no strategy freshness/expiry rule.

The latest row can have missing features; lookup does not silently skip it to
find an older complete row. Consumers must inspect quality. Naive timestamps are
rejected. `availability="UNKNOWN"` preserves retrospective measurements but sets
row availability to null; no as-of snapshot is admitted. A VERIFIED mode is
explicitly rejected because no historical dissemination evidence is provided.

These are latest-vintage reconstructed features. Frozen historical inputs do not
prove historical availability or a complete correction/revision archive. The
source hashes, UNKNOWN vintage status and reconstruction label remain visible
to future backtesting consumers. The bundle does not grant execution admission.

## Native basis, participation and true breadth

IBKR inputs retain `IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED`, RTH TRADES,
`IBKR_NATIVE_UNITS_UNVERIFIED`, overall basis verified=false. No independently
verified dividend-adjusted total-return series or price adjustment is created.
Context requires identical provider/basis metadata, distinct identities and valid
finite OHLCV; duplicates, off-calendar rows, conflicting sources and basis mixing
are errors. Missing sessions remain visible and affect only dependent windows.

RSP/SPY is an equal-weight versus cap-weighted **native ETF price proxy**, affected
by differing distributions, adjustment conventions and ETF mechanics. It is not
a pure concentration/total-return measure or the percentage of stocks above an
average. No proxy value is copied into a true-breadth field.

Six breadth extension fields (above SMA50/200, new 52-week highs/lows,
advance-decline participation, explicitly defined Trend Template) and one
leadership field (valid setup share) remain null/UNAVAILABLE with
`HISTORICAL_CONSTITUENT_DATA_NOT_PROVIDED`. Implementing them later requires PIT
membership, constituent histories, inclusion/exclusion/denominator rules and
versioned definitions. No present-day constituent list is fetched or used.

## Optional descriptive states

`spy_qqq_long_trend_v1` uses only SPY/QQQ Close/SMA200 and SMA200 slope20:
all four positive → UPTREND; all four negative → DOWNTREND; otherwise MIXED.
If any required value is missing → UNCLASSIFIED. Equality is MIXED. Underlying
continuous features and quality remain available; breadth is not required.
`--no-state` omits the label. These are project descriptions, not official
Weinstein/O'Neil/Minervini classifications. No score or five-state template is
invented from missing breadth. No label carries a trading permission.

## Immutable bundles and reproduction

The bundle contains `market_context_manifest.json`,
`reference_dataset_lineage.json`, `feature_definitions.json`,
`market_context_daily.json`, `feature_quality.json`, `configuration.json`,
`calendar.json`, `provenance.json` and the **complete embedded frozen price
datasets**, including their native captures. Repeated references to one dataset
are embedded once. There are no mutable external input/cache dependencies.

The existing flat SHA-256 bundle convention and exclusive directory creation are
reused. Readers verify outer hashes, embedded dataset lineage/identity, definitions,
configuration, frozen calendar hash and quality; they recompute causal windows
against frozen inputs without a calendar/provider library. Provenance retains
implementation and pinned shared-math identities. Same inputs/config/code/runtime
give identical bytes. Formula/data changes require a new immutable version.

Freezing needs the existing data/history extras; loading needs the installed
project and pinned market-shared wheel, with no pandas, numpy, Arrow, calendar,
Yahoo, IBKR SDK, TWS or network access. A clean clone has only synthetic fixtures.

```bash
PYTHONPATH=src .venv/bin/python scripts/make_market_context_example.py \
  --output /tmp/equity-market-context-example-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data market-context \
  --spy-dataset /path/to/frozen-references \
  --qqq-dataset /path/to/frozen-references \
  --rsp-dataset /path/to/frozen-references \
  --start 2024-01-02 --end 2026-10-20 --output /tmp/context-review-v1
```

The three roles may reference one multi-instrument frozen dataset or separate
datasets. Use new output paths. The command has no broker/acquisition flags.

```python
from equity_research.market_context import load_market_context
context = load_market_context("/tmp/equity-market-context-example-v1/context")
result = context.context_as_of("2024-01-03T09:30:00-05:00")
assert result["context"]["session_date"] == "2024-01-02"
assert result["historical_dissemination_verified"] is False
```

## Real demonstration and safety audit

The acquisition ran October 22, 2026, approximately **10:57–11:18 EDT**, on the
user-confirmed non-paper/read-only TWS endpoint. Python 3.12.9, ib_async 2.1.0
and server protocol 178 are recorded. All three five-session smoke requests
passed: seven native bars, five selected sessions and two exclusions each.

| Instrument | Full requests | Native bars | Explicit exclusions | Selected / expected | Pre-evaluation sessions |
| --- | --- | --- | --- | --- | --- |
| SPY | 49 | 1,450 | 455 | 995 / 995 | 292 |
| QQQ | 49 | 1,450 | 455 | 995 / 995 | 292 |
| RSP | 49 | 1,450 | 455 | 995 / 995 | 292 |

Each full capture passes calendar/numeric validation: no missing, duplicate,
off-calendar or outside-listing sessions, and no canonical/source-capture issues.
All selected rows retain distinct native indices; exclusions do not overlap those
indices. The three-instrument price dataset passed strict freezing without
`--allow-incomplete`. No forward fill, native-price repair, provider substitution
or volume rescaling occurred. Full captures replaced the overlapping smoke rows
in new cache versions; the original smoke snapshots/versions remain intact.

There were **zero retries, failed chunks, noninformational errors or fail-fast
terminations**. Informational codes 2104, 2106 and 2158 are retained. The historical
access conclusion applies to these requests; subscription/account details were
never queried. Sequential captures have different retrieval timestamps and are
not a synchronized historical dissemination archive.

The outgoing-message guard allowed only API start (71), contract details (9),
historical data (20) and historical cancellation (25). Actual totals: **seven
API connections/start handshakes, nine contract-details requests, 150 historical
requests and seven disconnects**; zero cancellations or blocked messages. These
were API handshakes to the user's existing TWS, not new TWS application sessions.
No account, portfolio, position, balance, execution or order request occurred.
Unsolicited handshake account identifiers and authentication secrets were not
persisted/logged by this workflow. No settings were changed or access workaround
used. Raw responses and feature rows remain in ignored local artifacts.

All **703** evaluation observations, **2024-01-02 through 2026-10-20**, have all
26 core features: complete trend rows 703, volatility rows 703 and participation
rows 703; incomplete core rows **zero**. All seven optional breadth/leadership
features remain unavailable on every row, so **703 rows have missing optional
features**. This distinction does not certify historical breadth completeness.

The optional rule gives **640 UPTREND, 15 DOWNTREND, 48 MIXED and zero
UNCLASSIFIED** observations. These are descriptive counts reconstructed from the
captured native prices under the declared timing assumption, not official market
classifications, historical dissemination proof, strategy filters or performance.

| Real immutable artifact | Local path | SHA-256 bundle identity |
| --- | --- | --- |
| SPY/QQQ/RSP prices | `data/research_datasets/pr7a-market-jfyafm7i-prices-v1` | `6b15fa426119634f34b5469654853593d405318909bf103bfbcd650d0d4a9d52` |
| Self-contained MarketContext | `data/research_datasets/pr7a-market-jfyafm7i-context-v1` | `d9a5547daf856364fdb398431ce17498d26c039ff926d44016bc4f5a9cddf271` |

All three roles reference the same combined price bundle; it faithfully embeds
their three separate full native captures. Smoke captures, setup, qualification,
preflight and the guarded audit remain under
`data/history_cache/pr7a-market-jfyafm7i`. Exact source snapshot and file hashes,
request windows/parameters and the verification bundle hash are in the v2 evidence.
The verification helpers/test output and preservation hashes are sealed under
`data/research_datasets/pr7a-real-evidence-jfyafm7i-v1`.

Real loading, core features, strict as-of boundaries, next session, early close,
holiday/weekend and DST checks passed with network sockets, provider/data SDKs,
cache and calendar imports denied. Actual SMA50/200 and normalized ATR outputs
also reconcile with the existing research-dataset indicators. For local real-data
inspection use:

```python
from equity_research.market_context import load_market_context
context = load_market_context("data/research_datasets/pr7a-market-jfyafm7i-context-v1")
assert context.quality["complete_core_rows"] == 703
assert context.quality["incomplete_core_rows"] == 0
result = context.context_as_of("2024-01-03T09:30:00-05:00")
assert result["context"]["session_date"] == "2024-01-02"
assert result["historical_dissemination_verified"] is False
```

## Synthetic example, preservation and next integration

The ignored deterministic example supplies 995 **synthetic** observations per
instrument, 292 preceding evaluation sessions and 703 complete trend/volatility/
participation rows, January 2, 2024–October 20, 2026. No core row is incomplete.
All 703 rows lack the seven optional breadth/leadership fields. The synthetic
UPTREND count is an engineering-fixture result, not actual market frequency.
It remains distinct from the real demonstration and its observed state counts.

| Synthetic local artifact | Path | SHA-256 bundle identity |
| --- | --- | --- |
| SPY/QQQ/RSP fixture prices | `data/research_datasets/pr7a-synthetic-jfyafm7i-v2/prices` | `4839030570c84aa2d015bad1919a18cd3879764b0d70524c4a49144c331579ee` |
| Self-contained fixture context | `data/research_datasets/pr7a-synthetic-jfyafm7i-v2/context` | `d7c3990fa0f3abd6927e5e069f3eb71433ecdb9dafc95246236adb7dba4b927e` |

The earlier synthetic v1 remains untouched. Verification code, final pytest output
and preservation hashes are sealed under
`data/research_datasets/pr7a-evidence-jfyafm7i-v1`. These paths are ignored by Git.

The evidence records local paths, exact source/context hashes, the final regression
result and offline verification. All **459** files present before the live capture
are byte-for-byte unchanged, including the 297 pre-existing historical files,
all AAPL/GOOG versions and the synthetic examples. The initial evidence report is
also unchanged. No finwhaling side effect occurred.
Full offline regression after authorization: **284 passed in 34.75 seconds**, zero failures, using
`.venv/bin/python -m pytest -q`. This includes all prior 254 tests and 30 new
MarketContext/provider regressions. The actual frozen synthetic artifact was also
loaded with optional/provider imports and network sockets denied.
Tests cover continuous formulas, exact warmup, data conflicts/bases/identity,
missing sessions, causal-window poisoning, availability equality, intraday/next-day,
early close, holiday/weekend/DST, unknown availability, symmetric descriptors,
immutable corrections, offline loading and existing execution/event/accounting
contracts. No lint command is configured.

Future PR 7B can read this same context as optional descriptive input while
generating signals in every regime. It must keep feature quality, the reconstructed
availability label and source lineage visible, and define its own research rules.
This PR adds no strategy eligibility, exposure or execution policy. Primary
historical dissemination/revision evidence, independently verified ETF adjustment
bases and PIT breadth/leadership data remain separate research requirements.
