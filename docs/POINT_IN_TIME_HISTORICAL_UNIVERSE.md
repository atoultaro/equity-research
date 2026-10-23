# Point-in-time historical universe — PR 8A

PR 8A adds offline identity, liquidity selection and research-panel infrastructure
on base **7183c51776eec0fbcb2420692748a0c993142320** (merged PR7C/#11), branch
`feat/pit-historical-universe-v1`. The authoritative task is PR8A's attached brief.
It does not change PR4 execution, source adapters, event publication rules,
MarketContext, signal definitions, outcome mathematics or research admission.
No strategy edge or real survivorship-free dataset is established.

## Scope and source decision

The eventual target is the top 1,000 historically eligible US common stocks by
60-session median daily dollar volume, with a later 3,000-security configuration.
PR8A demonstrates 50 selected securities from an invented 100-security catalogue.
No authorized broad listed/delisted source was supplied. See the
[17-criterion provider matrix](HISTORICAL_UNIVERSE_PROVIDER_EVALUATION.md).
CRSP is preferred for canonical research if legitimate access is available;
Norgate Platinum is a conditional individual alternative requiring Windows
acquisition tooling and acceptable license/retention arrangements. Sharadar is
an HTTP alternative requiring further vintage, basis and classification audits.
IBKR and Yahoo cannot supply the required canonical historical population here.
Only public documentation was consulted; no broker or vendor data was requested.

## Three independently versioned objects

| Object | Meaning | Offline interface |
|---|---|---|
| Security master | Stable identity assertions, effective intervals, publication clocks and lifecycle evidence | `import_master`, `SecurityMaster.as_of`, `resolve_symbol`, `lifecycle_as_of` |
| Research panel | Observations actually materialized; source bytes, bases, revisions, calendar and QA | `freeze_panel`, `ResearchPanel.observations`, `rows_as_of` |
| Historical universe | Rule and monthly ranked decisions, daily-queryable effective membership, exclusions and changes | `default_definition`, `build_universe`, `HistoricalUniverse.members_as_of` |

They are separate bundles. A monthly top-N list is neither a permanent ticker list
nor a promise of complete price coverage. Across decades many different stable
IDs can enter a fixed-size monthly universe. The panel may contain rejected or
inactive securities and incomplete acquisition attempts.

## Identity and lifecycle

Each master assertion names a permanent `security_id`, separate `issuer_id` and
`share_class_id`, provider ID, historical symbol, venue, classification, currency,
trading status, listing dates, evidence/confidence and source locator. Full-state
assertions use `[effective_from, effective_to)` intervals. A ticker change retains
the security ID; reuse by another issuer has a different ID. Multiple common-stock
classes are independent securities. Reorganization/relisting fixtures use a new
security ID with an explicit predecessor/successor relationship. Merger
counterparties and cash consideration remain source assertions, never fills.

`fact_id` and increasing `revision` preserve corrections. Later publication may
close an earlier effective interval, without changing how that interval looked
before the correction was known. Unknown fields are explicit nulls; incomplete
identity, listing, classification or status evidence excludes selection and
appears in QA. Ambiguous effective identity fails rather than joining on ticker.
`resolve_symbol` requires date and decision timestamp and refuses missing or
ambiguous resolution. All price joins use stable ID.

Lifecycle records retain effective date or null, independent `known_at`, evidence,
source hash, cash consideration, successor links and optional terminal value.
Bankruptcy, acquisition, trading halt and delisting are represented even when
terminal proceeds are unknown. A payment date never creates an ex-dividend date.
Unknown ex-dates stay unresolved. No prices or terminal returns are synthesized
from lifecycle records.

## Knowledge time and quality

All decision timestamps are timezone-aware and compared in UTC. Source capture
SHA256 identifies exact original bytes; capture time is not substituted for
historical publication time. `known_at` means documented source availability or
an explicitly labeled fixture/reconstruction assumption, independently of the
fact's effective date. `available_at` bounds completed-bar dissemination; revised
rows additionally require their revision's `known_at` before the decision.
Comparisons are strictly **earlier than** the decision. A bar exactly at the
cutoff is not admitted. Source-vintage assertions and evidence references survive
in manifests, including unknown evidence.

| Quality | Requirement |
|---|---|
| `PIT_VERIFIED` | Nonsynthetic source, explicit reviewed attestation with identity, availability, vintage and coverage evidence; required row timing documented and identity verified |
| `PIT_RECONSTRUCTED` | Causally calculated under declared source/availability assumptions, with no independent verification of original historical dissemination |
| `PIT_UNVERIFIED` | Missing required timing/identity/classification or candidate-ranking evidence; incomplete/unknown population coverage |

A boolean attestation is an import contract for reviewed documentation, not an
automated verification of a vendor. Importers must supply truthful references.
Synthetic data is categorically capped below `PIT_VERIFIED`. The master report's
source-level quality and selected rows' quality are separate from the universe's
population/ranking quality. An excluded candidate with unknown identity timing or
missing required ranking observations can make the universe unverified even when
the selected members' individual rows are reconstructed.

Default `unknown_knowledge_policy=EXCLUDE` rejects unknown historical timing.
Explicit `RECONSTRUCT_EXPLICITLY` permits retrospective effective-history use;
unknown timestamps remain null and downstream quality remains unverified. For an
unknown bar availability, that option uses a labeled close-plus-60-minute query
assumption; it never writes an invented timestamp back into source observations.
Future prices, later-published delistings, retrospective index additions, revised
volume and late action corrections cannot become earlier knowledge. Index
membership, future performance and present capitalization never rank stocks.

## Liquidity and security policy

The versioned default uses USD common stock on XNYS, XNAS and XASE. Ordinary REIT
common shares are included. ADRs, BDCs, SPAC common/units, ETFs, ETNs, closed-end
funds, preferreds, warrants, rights, debt and other instruments are excluded.
Dual classes compete independently. A recent IPO or transfer from an ineligible
venue needs all **60 consecutive eligible expected sessions**, with historical
classification/venue/status checked as known at the decision. Halts, missing
prices and unavailable volume do not compress the lookback.

```
daily_dollar_volume = Close * Volume
liquidity_score = median(last 60 eligible completed sessions' daily_dollar_volume)
```

The selection-day Close must be **>= USD5**. Every window price and volume must be
valid and positive. Eligible candidates rank by descending exact-Decimal score;
ties break by ascending stable security ID. Top-N is configurable from 1 through
3,000; 1,000 is the eventual default, 50 is the controlled pilot. USD5 and 60
sessions are declared engineering policies, never optimized against outcomes.

The first admitted liquidity basis is **RAW_TRADED / RAW_SHARES**. Other native
bases remain storable and auditable, but are rejected for this definition. No
split/dividend adjustment, raw-price imputation or double adjustment occurs.
A later basis policy requires a distinct reviewed definition rather than silently
promoting an adjusted source. Existing IBKR/yfinance prices and strict execution
admission rules are unchanged.

## Monthly reconstitution and daily queries

Observe through the last completed session of a **fully covered calendar month**.
The default decision is that session's Close plus two hours; synthetic bar
availability is Close plus one hour. The month's last bar is admissible only if
its availability and known time precede the decision. Membership starts on the
first eligible market Open strictly after the decision; no next-session OHLCV
enters selection. A caller may supply explicit delayed decision timestamps.
Frozen calendars must contain the lookback, entire selection month and next Open.

Snapshots retain every candidate, rejection reasons, identity evidence, score,
rank, input-observation hash, source captures, cutoffs and PIT quality. Intervals
are `[effective_start, effective_end)`. Missing monthly snapshots expire at the
next scheduled reconstitution; the reader returns unavailable for coverage gaps.
Consecutive explicit delayed reconstitutions retain the prior membership until
the next declared activation, without making the delayed list knowable earlier.
Dates are queried in the New York market calendar with an aware decision clock:

```python
from equity_research.universe import HistoricalUniverse
u = HistoricalUniverse("NEW/universe", master="NEW/security_master", panel="NEW/research_panel")
result = u.members_as_of("2008-05-15", decision_timestamp="2008-05-15T09:20:00-04:00")
```

Changes record entrants, exits and persisting IDs, plus turnover between recorded
snapshots. Comparison-month counts distinguish consecutive monthly turnover from
changes across intentionally unmaterialized years. Queries outside the frozen
calendar are unavailable. An exit never
liquidates a position. A midmonth delisting remains in the already-published
monthly list, with separately known lifecycle diagnostics. Before publication its
later failure cannot remove the stock. Later IPOs do not exist in early selections.
No survivor filter is applied. Missing future liquidation evidence remains a
limitation for later position-accounting work.

## Panels, integrity and immutable resume

A daily observation has stable ID, session date, exact-text OHLCV, currency,
price/volume basis, provider, capture SHA, original locator, revision, knowledge and
availability clocks/status, and quality status. Invalid OHLCV, negative/fractional
volume, duplicate `(ID, session, revision)` or off-calendar rows fail freezing.
Missing volume can be retained explicitly but cannot rank. Native source JSON
(including additional provider fields) is embedded unchanged. Raw, split-adjusted,
dividend-adjusted, total-return and vendor-unverified bases remain distinct.

Parquet partitions use **hashed stable ID, year and capture SHA**, with exact JSON
observations and projected ID/date/revision columns. PyArrow 23.0.1 is loaded only
for panel I/O; the core CLI and security-master reader have no broker SDK or
Parquet import requirement. Capture batches are bounded to 25,000 rows / 32MiB.
Writers exclusively claim a new directory and seal with the existing
`artifact_hashes_v1` convention. Verification hashes files in streams and loads
only metadata until a security/year is requested, avoiding a whole-panel read.
One security's history is the audit bound; very long/high-revision single-security
histories still require proportional memory. Universe candidate records scale
with securities times months; the performance evidence is not a 20-year benchmark.

`freeze_panel(..., base=SEALED_PANEL)` copies prior accepted partitions and source
bytes unchanged into a **new** snapshot and records its parent hash. New captures
can fill gaps. Conflicting observations require increasing revisions and strictly
increasing known times; unknown-time corrections cannot be ordered and fail.
Failed/partial acquisitions retain status and failure codes after resume.
An interrupted unsealed directory cannot load, be overwritten or be resumed in
place. Resume from the last sealed version into another new directory instead.
Accepted-capture replay is rejected; it is not silently overwritten or deduplicated.

Master and panel bundles are self-contained. A universe explicitly is **not**:
its manifest lists the exact master and panel bundle hashes; both dependency paths
are required on load and all member bytes are verified. There are no mutable cache
pointers. The integration bundle records those lineage hashes; using it for a
new experiment requires loading and verifying its referenced universe/panel.
Source hashes are byte integrity, not signatures or proof of economic correctness.

## Quality audit

Master QA reports unique security count, assertion count, listing/delisting dates,
reused tickers, classes per issuer across history, venue changes, incomplete/weak
identity, unknown knowledge clocks, lifecycle inventory, terminal evidence and
coverage assertions. Panel QA reports per-ID sessions, bases, missing volume,
unknown availability, revisions, volume discontinuities and failed acquisitions.
Missing sessions within the materialized span are counted with at most 50 example
dates per security; intentionally unmaterialized decades are gaps, not filled
history. Monthly QA adds known/effective candidates, eligible and selected counts,
rejection counts, incomplete ranking evidence, median/mean selected liquidity,
turnover and PIT classification. Corporate-action completeness remains explicitly
incomplete; retaining a split/dividend inventory is not proof of a full archive.

## Pilot, scale evidence and limitations

The reproducible runner is `scripts/pilot_historical_universe.py`. Pilot mode
creates 100 stable IDs, 114 bitemporal assertions and 10 lifecycle events, with
67,249 generated daily rows in explicit windows during 2008, 2015, 2020, 2022 and
2026. Ten monthly top-50 selections use the same fixed rule. Generated liquidity
rotates mechanically by ID and period, not future returns. Four terminal events
lack verified terminal values; one merger retains illustrative USD25 cash
consideration without treating it as an execution. Fixtures include bankruptcy,
reorganization/relisting, ticker change/reuse, dual classes, exchange transfer,
IPO, halt, weak identity, unknown knowledge and an unresolved dividend ex-date.
All ten pilot universes are **PIT_UNVERIFIED**, due to deliberately incomplete
candidate evidence; the source and individually usable rows are reconstructed.
These dates are engineering scenarios, not actual financial-crisis/pandemic or
2022/2026 stock histories. Actual 2007–2026 broad-market coverage is unavailable.

The scale runner's `--scale 100` and `--scale 1000` modes generate complete
catalogues for two monthly decisions from 124 sessions each. They test 12,400 and
124,000 observations, respectively, selecting 100 / 1,000 members per month.
Fresh subprocess wall times and peak process RSS (including native Arrow memory)
are recorded with Python, OS, architecture and dependency pins. No extrapolated
5-million-bar performance or actual provider completeness is claimed. Final
source commits, hashes, measurements and preservation checks are recorded in
[the pilot evidence](PR8A_PILOT_EVIDENCE.md).

## Existing single-security research integration

`single_security_inputs` verifies historical membership and returns one security's
complete contiguous prices, frozen calendar and `universe_research_manifest_v1`.
It records universe/definition/price hashes, selection date, stable ID, source-row
hash, optional frozen MarketContext hash (null means unavailable), strategy and
outcome configuration hashes, price cutoff and separate admission statuses.
A `history_start` can isolate an explicitly materialized contiguous segment;
gaps inside that segment fail. Late revisions are rejected by this static adapter
rather than inserted into earlier strategy features. They require a future causal
vintage replay adapter. Historical symbols are display aliases only after stable
identity has been resolved.

The pilot passes one selected invented stock into existing `swing.engine.evaluate`
and `outcomes.model.measure`. It uses existing shared-wheel ATR and unchanged
signal/outcome configurations, producing five illustrative signals and nine
first-signal path rows. It does not run a broad strategy study, create fills,
charge fictitious costs, synthesize terminal P&L or establish execution admissibility.
MarketContext is explicitly unavailable in this fixture. Universe selection,
signal research, price-outcome research and strict execution remain separate;
strict execution admission is **NOT_ADMITTED**.

## CLI and reproduction

Inspect the interface first with `python -m equity_research.cli universe --help`.
From a checkout use `PYTHONPATH=src` and the project's Python environment. The
`data` and `history` extras supply the pinned calendar and Parquet dependencies;
no commercial provider SDK is installed or needed.

```sh
PYTHONPATH=src .venv/bin/python scripts/pilot_historical_universe.py --output NEW_PILOT
PYTHONPATH=src .venv/bin/python scripts/pilot_historical_universe.py --scale 100 --output NEW_SCALE_100
PYTHONPATH=src .venv/bin/python scripts/pilot_historical_universe.py --scale 1000 --output NEW_SCALE_1000

PYTHONPATH=src .venv/bin/python -m equity_research.cli universe import-master --capture SOURCE.json --output NEW_MASTER
PYTHONPATH=src .venv/bin/python -m equity_research.cli universe audit-master --master NEW_MASTER
PYTHONPATH=src .venv/bin/python -m equity_research.cli universe freeze-panel --capture BATCH.json --calendar CALENDAR.json --output NEW_PANEL
PYTHONPATH=src .venv/bin/python -m equity_research.cli universe build --master NEW_MASTER --panel NEW_PANEL --definition DEFINITION.json --month 2008-04 --output NEW_UNIVERSE
PYTHONPATH=src .venv/bin/python -m equity_research.cli universe members --bundle NEW_UNIVERSE --master NEW_MASTER --panel NEW_PANEL --date 2008-05-15 --decision-timestamp 2008-05-15T09:20:00-04:00
PYTHONPATH=src .venv/bin/python -m equity_research.cli universe changes --bundle NEW_UNIVERSE --master NEW_MASTER --panel NEW_PANEL
PYTHONPATH=src .venv/bin/python -m equity_research.cli universe validate --bundle NEW_UNIVERSE --master NEW_MASTER --panel NEW_PANEL
.venv/bin/python -m pytest -q
```

The generator writes example capture contracts. `--capture` may be repeated for
bounded panel batches; `--base` resumes from a sealed panel into a new snapshot.
`build --decisions` accepts a month-to-aware-timestamp JSON map. Import, freeze,
build, audit, query and validation are offline. Output paths must be unused.

## From 100 to 1,000 to 3,000

Authorize and audit a licensed source first: permanent identities, candidate
population coverage by date, raw price/volume units, publication/vintage evidence,
actions, terminal gaps and permitted retention/output rights. Preserve dated
snapshots and partial failures rather than substituting a current winners list.
Use bounded incremental batches and stable-ID/year partitions to add histories,
then materialize each monthly selection with recorded evidence and quality.
The 1,000-security test demonstrates this storage/query path at bounded depth;
3,000 is a supported selection limit, not measured full-history capacity. A
constant 1,000-security twenty-year panel would be roughly five million daily
bars before extra identities, warmup and revisions. More profiling and real
source QA are required at that depth. This PR adds no scheduler, paid environment,
portfolio optimizer, strategy threshold search, order API or PR8B work.
