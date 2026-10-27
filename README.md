# equity-research

One offline daily-bar equity swing research slice:
candidate → qualification → buy-stop plan → replay → dollar risk/cost ledger →
reproducible artifacts. Python3.12+, one security, one manual candidate, long only.
The included SYNTH data is synthetic acceptance evidence, not a profitable-strategy
claim. Replay is fully offline. Optional historical acquisition and data preparation
are separate workflows; see below.

## Install

From this repository root, with Python3.12 or newer:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install setuptools==81.0.0 pytest==9.0.2
.venv/bin/python -m pip install --no-deps --no-index --require-hashes -r requirements-shared.txt
.venv/bin/python -m pip install --no-deps --no-index --no-build-isolation -e .
```

The first pip command bootstraps existing build/test tools; it may use a package
index. For an entirely offline setup, supply those wheels using `--no-index
--find-links /path/to/wheelhouse` on that command. Installation/replay after that
requires no network. The only runtime dependency is the committed, hash-pinned
market_shared0.2.0 wheel built from finwhaling commit
`57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`. Nothing is assumed published on PyPI.
See [vendor provenance](vendor/README.md). No finwhaling checkout is needed.

Tested development tooling: Python3.12.9, setuptools81.0.0, pytest9.0.2. The
installation acceptance test also creates a clean venv **without system packages**,
installs only the local equity/shared wheels, and exercises the installed command.

## Run the fixed experiment

```bash
.venv/bin/equity-research run \
  --data tests/fixtures/synthetic_daily.csv \
  --manifest tests/fixtures/data_manifest.json \
  --candidate tests/fixtures/candidate.json \
  --config tests/fixtures/swing_config.json \
  --output runs/example-v1
```

Run from this checkout to record its Git SHA automatically. From an installed wheel
outside the checkout, supply `--source-commit FULL_40_CHARACTER_SHA`; that asserted
revision is explicitly labeled user_supplied, together with the actual installed
source hash. A dirty checkout is recorded as dirty. Do not overwrite an experiment:
use a new output directory for each execution. Directory names are excluded from
canonical hashes, so repeated immutable inputs/config/code/runtime produce identical files.

Example: ELIGIBLE; signal2026-03-10, entry2026-03-11 at132.01, quantity15, stop125.50,
original risk$97.65. Target exit2026-03-13 at145.02. Gross$195.45 −slippage$0.30
−commission$0.15 −fees$1.00 =net$194.00, net realized R1.986687147977470558115719406.
This is an arithmetic/replay fixture, not historical stock performance.

Each run contains:

- `inputs/`: exact input CSV, candidate, configuration and data manifest bytes.
- `result.json`: qualification/reasons/as-of features, order activation/expiration,
  fills, outcome and complete one-trade ledger (or null trade).
- `trade_ledger.csv`: trade fields, header only for no trade.
- `run_manifest.json`: code/dependency identity, policies/conventions, inputs/hashes.
- `summary.md`: readable one-candidate economics, no portfolio statistics.
- `artifact_hashes.json`: SHA256 per file and canonical bundle hash (excluding self).

WATCH, REJECTED, EXPIRED and UNFILLED_END_OF_DATA remain visible. Malformed data,
unsupported actions/adjustments or invalid configuration fail explicitly with exit2
and no completed research run. Ordinary trade/no-trade outcomes return exit0.

## Test

The full suite also exercises the optional data-preparation subsystem. Install
its pinned extras in the development venv first (package installation may use a
package index; tests themselves use no network):

```bash
.venv/bin/python -m pip install '.[data,yahoo,history,test]'
```

```bash
.venv/bin/python -m pytest -q
```

Tests are deterministic and offline: no current-clock data, random prices,
broker, market-data fetch or parameter optimization. Network sockets are denied;
installation subprocesses use local artifacts and pip `--no-index --no-deps`.
The clean-install test requires the already installed build tools above.

The initial fixture can be regenerated explicitly with
`.venv/bin/python scripts/make_synthetic_fixture.py`; it uses fixed times/prices
and does not fetch data. Do not revise the fixture or shared artifact as a side
effect of an ordinary run.

## Research and execution boundaries

See [MVP specification](docs/MVP_SPEC.md) for exact data, qualification, sizing,
cost, gap, expiration and same-day ambiguity contracts, and
[research conventions](docs/RESEARCH_CONVENTIONS.md) for acceptance evidence and
hand calculations. The manifest supplies a complete versioned ET session schedule;
the replay loader has no automatic holiday calendar. Only raw prices with no declared corporate
actions are supported. Missing sessions are never forward filled. Daily OHLC does
not establish true intraday stop/target ordering; conservative collisions are flagged.

Maximum holding and explicit end-of-data full exits are modeled. Initial dollar
risk uses the actual entry and actual placed stop, before costs; no minimum-one-share
clamp exists. There is no trailing/partial exit, shorting, leverage, portfolio NAV,
vendor screening history or fundamental analysis. All results remain research evidence.

## Prepare historical daily data

PR 5B adds an optional single-security Yahoo adapter and offline validation,
comparison and export. `run` retains its existing input contract and never
imports the Yahoo client. The only core runtime dependency remains the pinned
shared wheel. The `data` extra pins pandas 2.2.3, numpy 2.2.4,
exchange-calendars 4.13.1 and tzdata 2025.2; the `yahoo` extra pins yfinance 0.2.66.
See [the pilot record](docs/YAHOO_PROVIDER_PILOT.md) for the unexecuted real-data
basket and the permitted-use blocker, and [data contracts](docs/DATA_PREPARATION.md)
for schemas and evidence requirements. No real-stock replay is certified.

A complete, offline, **synthetic** example creates a new directory and tests the
gates without making a Yahoo request. Substitute your own unused output name on
each execution:

```bash
PYTHONPATH=src .venv/bin/python scripts/make_yahoo_synthetic_example.py \
  --output /tmp/equity-synthetic-data-example-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data validate \
  --snapshot /tmp/equity-synthetic-data-example-v1/snapshot \
  --evidence /tmp/equity-synthetic-data-example-v1/evidence.json \
  --output /tmp/equity-synthetic-quality-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data export \
  --snapshot /tmp/equity-synthetic-data-example-v1/snapshot \
  --evidence /tmp/equity-synthetic-data-example-v1/evidence.json \
  --output /tmp/equity-synthetic-research-v1
```

That two-bar export satisfies `load_dataset` and demonstrates `EXPORT_READY`
using synthetic evidence only; it has insufficient strategy warmup. It does not
verify any actual Yahoo price basis or historical publication timestamp.

When retrieval and retention are permitted, acquisition is an explicit command:

```bash
equity-research data fetch-yahoo --symbol SPY --start 2024-11-20 --end 2024-12-06 \
  --output /tmp/equity-yahoo-snapshots
equity-research data validate --snapshot /tmp/equity-yahoo-snapshots/ATTEMPT_UUID \
  --output /tmp/equity-yahoo-quality-v1
equity-research data compare --before /tmp/equity-yahoo-snapshots/BEFORE_UUID \
  --after /tmp/equity-yahoo-snapshots/AFTER_UUID --output /tmp/equity-yahoo-diff-v1
equity-research data export --snapshot /tmp/equity-yahoo-snapshots/ATTEMPT_UUID \
  --output /tmp/equity-yahoo-export-v1
```

Dates are inclusive; the adapter explicitly converts the provider end to the next
calendar day. Fetch prints the new UUID directory and acquisition status. Without
affirmative evidence the export command writes immutable quality artifacts,
returns exit 3, and produces **no** `data.csv` or replay manifest. Validation
returns 0 when its report was successfully written, even for blocked data; inspect
the gates. Exit 2 means an invalid command/input, integrity problem or missing
optional dependency; fetch/compare also return 3 for failed/partial/unknown outcomes.
No command overwrites an existing snapshot/report/export directory. Snapshots
are client-return captures, not original HTTP payloads. Nothing fills gaps or
relabels adjusted prices raw; no availability model is automatically introduced.

## Yahoo and IBKR historical research datasets

PR 5D adds explicit multi-symbol acquisition, per-provider Parquet caches,
immutable research datasets, an offline loader/indicators and provider comparison.
These technical datasets preserve native bases and unknown availability; strict
execution replay and PR 5B export gates retain their existing contracts. See
[historical data infrastructure](docs/HISTORICAL_EQUITY_DATA_INFRASTRUCTURE.md)
for identity mappings, permissions, refresh policies, native semantics and all CLI
options. The `history` extra adds pyarrow 23.0.1; optional `ibkr` adds ib_async
2.1.0. Normal tests and the following example use only offline synthetic responses:

```bash
PYTHONPATH=src .venv/bin/python scripts/make_historical_equity_example.py \
  --output /tmp/equity-history-demo-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data freeze \
  --provider yahoo --symbols SPY,QQQ,AAPL \
  --mappings /tmp/equity-history-demo-v1/mappings.json --start 2024-01-02 --end 2024-12-31 \
  --cache /tmp/equity-history-demo-v1/yahoo-cache --output /tmp/equity-history-refrozen-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data compare-providers \
  --symbol AAPL --start 2024-01-02 --end 2024-12-31 \
  --yahoo-dataset /tmp/equity-history-demo-v1/yahoo-dataset \
  --ibkr-dataset /tmp/equity-history-demo-v1/ibkr-dataset \
  --output /tmp/equity-history-comparison-v1
```

Use a new output path for every example. `load_research_dataset(path).bars("SPY")`
returns canonical rows without provider parsing; `.indicators("SPY")` supplies
SMA50/200, EMA50, shared simple ATR14 and volume mean20. Frozen loading/indicators
work without acquisition libraries or a cache. Comparisons report discrepancies
and unresolved bases; they never select or combine providers.

Real acquisition is an explicit `data history --provider yahoo|ibkr` command with
reviewed `--mappings`, `--symbols`, `--start`, `--end`, `--cache` and
`--permission-reference`. Yahoo permissions identified in PR 5C remain unresolved
for unapproved access. IBKR additionally requires an existing local authenticated
TWS/Gateway and explicit `--ibkr-port`/`--ibkr-client-id`; the adapter requests
historical stock data only. `--mode offline` reads cache without provider access;
`--mode incremental` forces overlap refresh and `--mode full` refreshes the whole
requested interval. No live acquisition or account, position or order operation
was performed for PR 5D.

PR 5E subsequently verified one real, read-only paper-TWS historical request:
five SPY sessions were captured, validated, cached, frozen and loaded offline.
See [the live smoke-test record](docs/LIVE_IBKR_EQUITY_SMOKE_TEST.md) for the
confirmed prerequisites, exact scope, local artifacts and remaining data limits.

The [IBKR historical-depth audit](docs/IBKR_HISTORICAL_DEPTH_AUDIT.md) adds an
explicit operator-started backward daily-history walk with contract identities,
bounded retries/pacing, immutable resumable checkpoints and offline coverage
reports. Automated tests use mocks; the live command requires explicit local
connection and read-only confirmations. It does not query accounts or place orders.

The [expert trade-comprehension pilot](docs/EXPERT_TRADE_COMPREHENSION.md) preserves
four operator-reported Grimes new positions and builds immutable, descriptive
daily-price, market/sector, stop and event-evidence dossiers. `expert freeze-inputs`,
`expert study` and `expert replay` are offline; actual acquisition reuses the
separately invoked depth audit. Reference closes are not assumed entries. The
[October 26 report](docs/reports/GRIMES_20261026.md) separates reported facts,
observed prices and competing research hypotheses, with explicit daily/5/20/60-session
return horizons. A versioned operator-reported 1R convention and optional hypothetical
closing-reference targets preserve unknown actual entries/exits, without simulated
fills or P&L.

PR16 adds [Grimes source/model lifecycle reconstruction](docs/GRIMES_TRADE_LIFECYCLES.md)
for exactly 26 stocks across seven October 18–26 alerts. The offline `lifecycle`
commands preserve source positions, stop histories and underway transitions,
reconcile separate modeled triggers/1R outcomes, and produce immutable event-context
tables and one dossier per stock. The [research report](docs/reports/GRIMES_LIFECYCLES_20261018_26.md)
documents EBAY's old-stop crossing versus its later source revision, unresolved
weekly publication time, conditional price-basis scenarios and right censoring.
Actual fills, position sizes and profitability remain unknown.

PR17 adds [empirical Grimes management and decision analysis](docs/GRIMES_MANAGEMENT_DECISIONS.md)
using the unchanged PR16 captures. The [complete research report](docs/reports/grimes-management-20261018-26/report.md)
compares all stop revisions, underway transitions and source closures, with
counterexamples, matched ENTERABLE observations and explicit primary/conditional
evidence. `management study` and `management replay` are offline and produce
immutable studies and 26 individual summaries. They do not infer actual fills,
exit causes or a trading edge.

PR 6A adds the first actual AAPL individual-stock dataset: 703 IBKR daily sessions
plus independently sourced earnings, dividend declarations and historical splits.
[The AAPL event-aware study](docs/AAPL_EVENT_AWARE_RESEARCH.md) records acquisition
hashes, source evidence, unresolved ex-dates, session alignment, historical
knowledge safeguards and offline reproduction. `data events-freeze` and
`data event-study` compose immutable event sidecars with existing price datasets;
`equity_research.events.load_event_study` loads them offline. Actual payloads stay
in ignored local storage; committed tests use deterministic synthetic evidence.

PR 6B applies the same framework to Alphabet Class C (`GOOG`).
[The GOOG evidence study](docs/GOOG_EVENT_AWARE_RESEARCH.md) records all 703 IBKR
daily sessions after a user-authorized retry, independently
sourced corporate events and an offline AAPL/GOOG completeness comparison. Earlier
error-162 failures and partial artifacts are preserved. Unresolved release clocks,
unknown ex-dates and native-basis limitations remain explicit; no trading
conclusion is claimed.

PR 7A adds [historical MarketContext](docs/MARKET_CONTEXT_INFRASTRUCTURE.md):
continuous SPY/QQQ trend and volatility features, RSP/SPY participation proxies,
explicitly unavailable breadth, immutable offline bundles and an as-of reader.
Availability is reconstructed under a declared completed-session timing assumption.
The real demonstration uses 995 IBKR sessions per ETF, including warmup, and
703 complete evaluation observations. The user's non-paper/read-only TWS endpoint
was used for historical requests only; earlier synthetic evidence is preserved.
Context does not approve, reject, resize or execute trades.

PR 7B adds the [general swing strategy framework](docs/GENERAL_SWING_STRATEGY_FRAMEWORK.md):
typed setup, trigger, signal and provisional plan records; prior-N-session High
boundaries; continuation LONG and failed-breakout SHORT research inventories;
strictly eligible MarketContext links without a regime filter; and immutable,
self-contained offline bundles. `swing research` uses existing frozen studies.
`swing replay` admits raw/no-action inputs through the existing strict loader and
reuses PR 4's long buy-stop engine and actual-fill risk accounting. Actual AAPL/GOOG
signals have no fictional fills or P&L; SHORT execution remains unsupported.
See the framework document for fixed-window aggregate inventories, synthetic
arithmetic evidence, CLI examples, source hashes and limitations.

PR 7C adds [signal-outcome research](docs/SIGNAL_OUTCOME_RESEARCH.md).
The offline `outcomes` command consumes original frozen signals and captured
context links, measuring separate signal-Close and next-eligible-Open paths,
direction-normalized returns, MFE/MAE and original signal-ATR units. Every signal
and incomplete horizon remains represented. Immutable self-contained bundles
include descriptive context summaries and overlap-cluster diagnostics. The actual
AAPL/GOOG demonstration preserves all 128 signals; it does not regenerate detection,
fetch prices or imply fills, short sales, realized R or portfolio P&L.
