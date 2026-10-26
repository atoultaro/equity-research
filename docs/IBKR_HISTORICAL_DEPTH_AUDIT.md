# IBKR daily historical-depth audit

Authoritative task: the user's IBKR Daily Historical-Depth Audit, October 26,
2026. Branch `feat/ibkr-historical-depth-audit-v1`, from main
`7183c51776eec0fbcb2420692748a0c993142320`. The existing adapter, acquisition,
cache, canonical conversion, session calendar, tests and historical-data guides
were inspected at that revision. No execution simulator, strategy, outcome,
framework experiment or previously frozen research input is changed.

## What the command measures

This is an explicitly started, read-only local TWS/Gateway audit of completed
daily **TRADES**, regular trading hours, USD US stock contracts (ETFs use IBKR's
`STK` security type). It measures the data actually returned for the qualified
contract at retrieval time. It does not certify source completeness, historical
publication timestamps, action completeness or survivorship-free membership.

The initial configurable list is AAPL, MSFT, GOOG, NVDA, AMZN, META; SPY, QQQ,
IWM, RSP; XLK, XLF, XLE, XLI, XLV; SMH and XBI. The
[configuration example](examples/ibkr-depth-config-v1.json) uses a 1980-01-01
search boundary and windows of up to five years. This is a search boundary, not
an assertion that every instrument existed in 1980. Optional explicit listing
boundaries require the existing `Security` mapping's source reference.

Each mapping requires an explicit research identity, primary exchange and
currency. The example's `operator-map:*` keys are local labels, not historical
identity evidence. An optional reviewed `con_id` further constrains resolution.
Exactly one matching native contract is required. The resolved conId, symbol,
security type, SMART routing, primary exchange, local symbol, trading class and
currency are captured. Resume must resolve the identical contract before any
further bars; ambiguity or identity changes stop that instrument. It never
substitutes a present-day ticker for a delisted/renamed security.

## Local operator workflow

Install only the existing optional dependencies if needed:

```sh
.venv/bin/python -m pip install '.[data,ibkr,test]'
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-audit --help
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-report --help
```

The client remains pinned to `ib_async==2.1.0`; data/calendar versions retain the
project's existing pins. No paid service or new vendor is required. Availability
depends on the operator's existing entitlements; a permission error is reported,
not bypassed, and this command does not purchase subscriptions.

Open and authenticate local TWS/Gateway yourself. Confirm socket clients and
Read-Only API are enabled, choose the configured API port and an unused positive
nonzero client ID. The operator confirmed **non-paper TWS, port 7496, Read-Only
API enabled** in this session. Those settings are not changed programmatically;
the flag below records the operator's assertion, not an API inspection of TWS.

Use an unused output directory for a new run:

```sh
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-audit \
  --config docs/examples/ibkr-depth-config-v1.json \
  --output runs/ibkr-depth-YOUR-NEW-RUN/audit \
  --ibkr-host 127.0.0.1 --ibkr-port 7496 --ibkr-client-id 46126 \
  --connect --read-only-api-confirmed \
  --permission-reference 'operator-authorized historical access using existing entitlements; retention basis reviewed by operator'
```

All three explicit acquisition attestations are required. They are caller
assertions, not a license grant. No tests initiate this connection. The backend
reuses the existing low-level `IB.client.connectAsync` handshake, avoiding the
high-level startup account synchronization and automatic account-summary recovery
callback. It exposes qualification, historical bars, earliest-data metadata and
disconnect only. Historical cancellation messages cancel market-data requests,
never orders. No balance, position, portfolio, execution or order operation is
performed. Account identifiers received as part of the protocol handshake are
not retained in audit artifacts.

Stop with Ctrl-C. Completed checkpoints remain usable. Resume explicitly with
the **same configuration and output directory**:

```sh
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-audit \
  --config docs/examples/ibkr-depth-config-v1.json \
  --output runs/ibkr-depth-YOUR-NEW-RUN/audit --resume \
  --ibkr-host 127.0.0.1 --ibkr-port 7496 --ibkr-client-id 46126 \
  --connect --read-only-api-confirmed \
  --permission-reference 'operator-authorized continuation using existing entitlements'
```

Resume preserves the original as-of clock and final session; it does not refresh
the latest date. Use a new run for a new end date, configuration, cost/basis
experiment or source vintage. A completed resume does not reconnect. A failed
instrument can be retried on resume after its external condition is resolved;
prior failures remain in the record. A reached search boundary is not rescanned
automatically to repair gaps/revisions. A stale `.lock` after a hard process kill
requires inspection of the other writer before manual removal.

Freeze a report at any checkpoint, with **no provider access**:

```sh
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-report \
  --audit runs/ibkr-depth-YOUR-NEW-RUN/audit \
  --output runs/ibkr-depth-YOUR-NEW-RUN/report-v1
```

Use a new report version after resuming. A frozen report embeds the original
plan, calendar and checkpoint payloads, so the same command can also take a
previous frozen report as `--audit` and reproduce its bytes without the journal,
TWS, IBKR package, market-data files or network.

CLI exits: acquisition 0 when all instruments are complete/exhausted and the
invocation finished; 3 for failed, partial, inconclusive or resource-limited
audits; 130 for cooperative cancellation; 2 for invalid input/integrity errors
detected before acquisition. Setup/client failures during an invocation are
checkpointed as failed audits (exit 3). Report generation returns 0 when it writes a report, even if the data is
incomplete; inspect `coverage.json`. No output is overwritten.

## Backward acquisition and honest stopping rules

1. Freeze the request configuration, source hashes, runtime versions, as-of clock
   and independent XNYS calendar. Select the latest session whose close is no
   later than that clock, including early closes. A requested historical `end`
   can narrow the audit; future dates fail. Resume never moves this frozen end.
2. Qualify the exact stock contract. Optionally request `reqHeadTimeStamp` for
   TRADES/RTH as evidence of the provider's reported earliest data. This metadata
   request is explicitly cancelled after success, timeout or cancellation. A
   failed/unsupported head request does not establish exhaustion or prevent a
   subsequent bar request.
3. Walk backward using finite windows. Daily requests use explicit UTC end
   anchors, `barSizeSetting='1 day'`, `whatToShow='TRADES'`, `useRTH=True`,
   `formatDate=1`, `keepUpToDate=False`, and a 30-second request timeout. Durations
   over 365 days use IBKR year units; exact audit bounds remain separate. Extra
   returned rows are retained and explicitly excluded from that window's analysis.
4. Overlap successive windows. Advance from the **earliest actual bounded
   returned date**, not from the requested start. A provider returning only a
   truncated tail therefore cannot make the walk silently skip older windows.
   Identical overlap observations are deduplicated in the derived series;
   conflicting observations preserve both locators and fail clean coverage.
5. Retry only pacing, timeout, connection, empty and explicit no-data outcomes,
   up to the configured 1–3 attempts. Backoff is bounded at 60 seconds. Permission,
   ambiguity and other nontransient failures stop that instrument without
   subscription workarounds. Failed partial returns remain diagnostic captures
   and are not credited as successfully acquired sessions.
6. An empty/no-data window may advance to another older window after its bounded
   retries, but it **never proves exhaustion**. Consecutive-empty limits or an
   unconfirmed empty boundary stop with uncertainty. Exhaustion requires a
   successful provider head timestamp, an observation matching that boundary,
   and complete, nonconflicting calendar coverage above it. It is a claim about
   this provider/contract/retrieval, not all historical data everywhere.

The existing shared `Pacer` serializes requests, at least 2 seconds apart,
identical signatures at least 15 seconds apart, and at most 60/600 seconds. This
is intentionally conservative for daily bars. Qualification/head calls count too.
Recent checkpointed starts rebuild the pacing history on resume. Pacing across
other processes/client IDs is not coordinated: do not launch concurrent audits.
The historical head API has its own restrictions; see IBKR's
[earliest-data documentation](https://www.interactivebrokers.com/docs/tws-api/doc/md/earliest-data-point).

Defaults: 365-day windows (the supplied 17-instrument config explicitly chooses
1,825), five-calendar-day overlap, three attempts, 64 windows per instrument,
800 total requests and one hour per invocation, three consecutive empty windows.
The configured request/window/runtime budgets are per invocation, so explicit
resume can continue a bounded run. The search start, identities and captured end
cannot be changed in place. No single long request is assumed to return all
history. IBKR's [historical limitations](https://interactivebrokers.github.io/tws-api/historical_limitations.html)
describe soft throttling even for larger bars and gaps around exchange moves;
that legacy page is deprecated, and actual endpoint behavior remains empirical.

## Artifacts, quality and interpretation

The audit root is an append-only journal, not a mutable price cache:

- `plan/`: immutable `plan.json`, independent `calendar.json`, `hashes.json`.
- `events/NNNNNNNN/`: immutable chained request starts, qualifications, metadata,
  native returns, failures, stops and invocation outcomes. Each has a SHA256 seal.
- Every historical result captures exact parameters, retrieval timestamps,
  request linkage, attempt, status and safe diagnostics. Successful and failed
  client returns retain lossless tagged `returned_bars.json` and, when available,
  `returned_frame.json`. Timeout partial bars are retained without claiming
  successful coverage. An external cancellation may interrupt before a client
  return exists; the start and cancellation checkpoint remain visible.

An interrupted unsealed checkpoint directory is preserved and listed as
abandoned; it is never adopted as successful evidence. Resume validates the chain
and recomputes cursor advances from frozen observations. No saved coverage
counter can establish completed depth on its own.

Frozen reports use the existing `artifact_hashes_v1` convention:

| File | Meaning |
| --- | --- |
| `audit_manifest.json` | Search, origin, software/source identities, plan and checkpoint hashes, statuses and limitations |
| `coverage.json` | Per-instrument qualified identity, observed range, session counts, gaps, duplicate/revision locators, quality issues, errors, head evidence and resume position |
| `summary.md` | Human-readable table and warnings |
| `daily_bars.json` | Deduplicated diagnostic OHLCV, exact numeric strings and source locators; conflicting sessions remain flagged, not repaired |
| `calendar.json` | Pinned calendar with package version, explicit dates, UTC open/close and hash |
| `plan*.json`, `checkpoint-*` | Self-contained original input/request/return/error evidence for offline reproduction |
| `hashes.json` | Exact file hashes and canonical bundle SHA256 |

`complete` means all expected sessions in the requested range were observed with
no failing quality finding. `exhausted` means the evidenced provider boundary was
reached with complete coverage above it. `partial` retains observed bars but has
gaps, quality failures or unfinished search. `inconclusive` has no successful
coverage and insufficient exhaustion evidence. `failed` records a concrete
connection, qualification, permission or request failure without successful bars.
Separate stop reasons, search progress, diagnostics and head evidence prevent a
single status word from concealing uncertainty.

Internal gaps and missing trailing sessions are distinguished from leading
unobserved history. Holidays are absent from the independent expected calendar;
they are not missing sessions. Leading missing dates are not automatically
classified as pre-IPO or delisted. Security-specific halts/listing calendars are
not inferred from absence. XNYS is the project's pinned common US cash-session
reference; actual historical venue alignment is not independently certified.
The `observed_sessions` field counts unique dated bar observations, including
any separately flagged off-calendar dates; it is not a count of verified
exchange sessions. No observation is forward filled. Duplicate dates, chronological anomalies,
invalid/nonfinite OHLCV, negative/fractional volume and off-calendar dates are
retained as quality findings. Zero volume and large discontinuities are warnings,
not inferred corporate actions. Output labels do not certify raw as-traded data:
IBKR TRADES is documented split-adjusted, not dividend-adjusted. See IBKR's
[historical bar conventions](https://interactivebrokers.github.io/tws-api/historical_bars.html).
ADJUSTED_LAST comparison is optional in the brief and **not implemented** here;
the report marks it `NOT_REQUESTED` rather than inventing adjustment verification.

No existing cache pointer or frozen dataset is changed. Optional Parquet cache
promotion is intentionally omitted; the raw journal and immutable daily JSON are
the audit evidence. Any later cache/export must use the existing preparation
gates and preserve the native basis, uncertainty and source references.

## Offline example and validation

```sh
PYTHONPATH=src .venv/bin/python scripts/make_ibkr_depth_example.py \
  --output /tmp/ibkr-depth-offline-NEW-VERSION
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-report \
  --audit /tmp/ibkr-depth-offline-NEW-VERSION/report \
  --output /tmp/ibkr-depth-offline-REPLAY
.venv/bin/python -m pytest -q
```

The example has fictional COMPLETE/GAPPED contracts, fixed November 2024
sessions, Thanksgiving closure, a deliberate missing November 26 bar, virtual
throttling and zero connections. The committed [sample report](evidence/ibkr-depth-offline-v1/summary.md)
is self-contained and replays offline. Its bundle SHA256 is
`62447af19bd19b838938c8bec9d1dd88eb4843633213a5b49c43b651c37b31e6`.

Validation: `.venv/bin/python -m pytest -q` → **426 passed in 44.99s**, no skips.
The 26 new tests use mocked responses and virtual clocks; sockets are denied by
the existing offline test harness. They cover backward windows, overlap/conflict,
chronology/duplicates, calendar holidays/gaps, empty/no-data/permission/timeout
outcomes, head-versus-observation disagreement, truncated tails, native request
cancellation, budgets, identity ambiguity/change, pacing restoration, resumable
checkpoints, interrupted writes and report regeneration without IBKR installed.
Native qualification and low-level no-account synchronization tests remain intact.
There is no canonical lint command; `git diff --check` is run separately.
