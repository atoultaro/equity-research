# PR 5E — live IBKR paper-TWS historical equity smoke test

The existing PR 5D adapter successfully retrieved, captured, validated, cached and
froze **five actual SPY daily bars for 2026-10-12 through 2026-10-16** from the
already running local paper TWS session. The frozen dataset subsequently loaded
with network, provider, data-library and cache-module access denied. No adapter
fix or new data infrastructure was necessary.

This is a narrowly scoped live integration result, not a strategy backtest,
execution-data certification, subscription inventory or claim of trading edge.
The normal pytest suite remains entirely offline and synthetic.

## Authority, revisions and environment

Authoritative task: the user's PR 5E instructions and subsequent explicit
confirmation that socket clients and Read-Only API were both enabled on port 7497.
Those instructions authorize the historical-data connection beyond the older
blanket broker/vendor exclusion in root AGENTS.md. Every other execution/research
boundary remains in force. Branch: `test/live-ibkr-equity-history-v1`.

| Reference | Exact inspected commit |
| --- | --- |
| equity-research latest main, including merged PR 5D | `dd0c2a133a9190621e69e4bbd55435b35f913366` |
| Read-only finwhaling reference | `98034e009ac2c062e5a23aad1ba1cf56f2c94001` |

Required repository guidance, PR 5D/data-preparation documentation, provider,
cache/CLI/dataset/normalization code and tests were inspected. The exact existing
`data history --help` and `data freeze --help` interfaces were inspected before
acquisition. finwhaling's ibkr-data backend and historical request/lifecycle code
were inspected in the unchanged temporary reference checkout; its account-sync
connection and futures assumptions were not reused. No reference repository,
adapter, strategy, execution/accounting code, immutable fixture, dependency or
pinned shared wheel changed in this PR.

Environment: Python 3.12.9; ib_async 2.1.0; pandas 2.2.3; numpy 2.2.4;
exchange-calendars 4.13.1; tzdata 2025.2; pyarrow 23.0.1; market-shared 0.2.0.
All were already installed in the target `.venv` environment. No package install,
TWS launch, authentication automation or settings change was performed.

## Phase A prerequisites and their evidence

| Check | Result and evidence |
| --- | --- |
| TWS Classic authenticated to paper | User confirmed the existing session. A matching JavaApplicationStub process and API listener were observed. Account type was not independently queried through a prohibited account API. |
| Socket clients enabled | User confirmed the current API setting; OS inspection found port 7497 listening, and the later API handshake succeeded. |
| Read-Only API enabled | Explicit user confirmation of the current checkbox, obtained **before any TWS connection**. This is a user attestation, not a programmatic settings query or an inference from paper login/port. No write request was used to test the setting. |
| Endpoint matches configuration | User-confirmed port and observed listener matched `127.0.0.1:7497`. No ports were guessed/probed to bypass settings. |
| Unique client ID | Explicit positive client ID 51837 completed the handshake; no client-ID collision/326 was observed. No query of other clients was made. |
| Client/data dependencies | Installed versions matched the pins above; installed client source hashes are retained in the evidence. |
| Localhost access | The approved host execution successfully connected to loopback. No firewall, TWS configuration or access restriction was changed. |
| Historical data entitlement | This particular SPY/TRADES/RTH historical request succeeded without a permission error. This establishes availability for this request only; no balance, account, position, execution or subscription-details query occurred. |

The initial local INI inspection did not establish the active session's read-only
setting, so live work waited for explicit user confirmation. A paper account or a
listening socket alone was never treated as sufficient evidence of Read-Only API.
No account identifier or authentication secret was collected into the artifacts.

## Actual request and interaction audit

Acquisition ran on **2026-10-22 UTC** (2026-10-21 evening in New York).
The real adapter recorded start `2026-10-22T02:38:46.222390+00:00` and completion
`2026-10-22T02:38:46.876133+00:00`. The server protocol version was 178;
the TWS application release/build was not separately queried.

| Parameter | Actual value |
| --- | --- |
| Security | SPY, STK, SMART routing, ARCA primary exchange, USD |
| Qualified contract | conId **756733**, localSymbol/tradingClass SPY; exactly one matching contract |
| Requested interval | 2026-10-12 through 2026-10-16, inclusive |
| Historical request | `endDateTime="20261017-00:00:00"`, `durationStr="5 D"` |
| Bar/data type | `barSizeSetting="1 day"`, `whatToShow="TRADES"`, `useRTH=True` |
| Other parameters | `formatDate=1`, `keepUpToDate=False`, client timeout 30 seconds |
| Bound | One configured maximum attempt, one actual request, zero retries |
| Result | Acquisition SUCCESS; five returned bars, expected/returned dates identical |

The live operation used the existing `history()` and `IBKRDailyProvider`, with
the actual `make_backend()` and ib_async socket client. No fake client, fabricated
return, clock injection, alternate adapter or adjusted data substitution was used.
The supported `max_attempts=1` setting kept this smoke request smaller than the
CLI default of three. The temporary invocation helper was retained locally with
its source hash; it is not a new production acquisition interface.

The helper wrapped only connection/disconnect observation and the real client's
typed outbound `send` method. It allowed message types 71 (start API), 9 (contract
details), 20 (historical data), and 25 (cancel a historical-data request on timeout).
Any other message type would have been blocked before transmission. Initial
version negotiation uses the client's normal connection handshake. No raw socket
payload or inbound account-list logging was enabled. Library log propagation was
suppressed while the adapter's safe error-category recorder remained active.

Observed interactions in this smoke process:

| Interaction | Count |
| --- | ---: |
| Connection / API handshake | 1 / 1 |
| Contract-details request | 1 |
| Historical-data request | 1 |
| Historical-data cancellation | 0 |
| Disconnect call | 1 |
| Blocked/unexpected typed outbound messages | 0 |
| Account, balance, portfolio, position, execution or order requests | 0 |

Only informational farm-status codes were captured: 2104 three times, 2106 twice
and 2158 once. There were no permission, pacing, timeout, identity or coverage
failures. The interaction audit covers this process, not other applications or
manual activity in TWS. Unsolicited account identifiers needed internally by the
client handshake were not requested by application code, logged or persisted.

## Validation, cache and freeze

The existing canonical conversion and independent pinned XNYS research calendar
reported five expected sessions, five returned observations and zero missing,
off-calendar, duplicate or outside-listing sessions. Numeric/range validation
reported zero canonical or source-capture issues. No incomplete session was
admitted, row repaired, duplicate removed or value forward filled.

The initial cache outcome was MISS → HIT, with a new immutable source snapshot
and cache version `8037e1b0725d4b0d9f5d64e44cbd2e06`. Both the explicit offline
cache CLI and a subsequent auto cache-hit CLI returned SUCCESS. For the auto-hit
check, provider imports and socket connections were explicitly denied; acquisition
was `NOT_REQUESTED` and no additional snapshot appeared.

The unmodified `data freeze` CLI returned exit 0 and produced a self-contained
`research_dataset_v1` bundle with `research_daily_v1` bars, original source captures,
quality, versions and hashes. The dataset records `source_origins=["ibkr_client"]`
and `synthetic_only=false`. Every original and embedded bundle passed integrity
verification. Frozen loading succeeded in a fresh process with socket connection
methods, provider/data/calendar imports and the cache module all denied.

An explicit second freeze to the existing output returned exit 2 as required;
exact frozen file bytes and bundle hashes were unchanged afterward. Cache reads
and the cache-hit check also left those frozen bytes unchanged. The cache and
original snapshots were retained, not deleted or modified to simulate independence.

Five bars are insufficient for SMA50, SMA200 or ATR14. The optional offline
indicator check correctly retained their missing warmup values instead of
manufacturing results. No longer data window or extra provider call was introduced
to satisfy an indicator demonstration.

PyArrow emitted sandbox CPU-feature/cache-probe diagnostics during local Parquet
operations; the operations returned success and all resulting files passed hash
checks. These were host capability-probe messages, not market-data errors.

## Artifacts and reproducibility

The committed [aggregate evidence JSON](evidence/ibkr-paper-equity-smoke-20261022.json)
contains environment/preflight evidence, exact request/contract, timestamps,
interaction counts, validation results, runtime source identities and hashes.
It contains **no bar prices/volumes, raw source snapshots, account identifiers or
authentication secrets**. Snapshot hashes demonstrate local integrity, not a
provider signature, data license or historical publication time.

```text
snapshot content SHA256
175d12a18e62c3edf7fbf71b63970efe59751e088f472a6704317806c0b078a3

snapshot bundle SHA256
dcb32a0885ead4bdf7aa26737d09e6f16c1d0a54e610eb9e20c6eb17709269ff

frozen dataset bundle SHA256
7a562cf738a68dbfc907ca271de91e68b5b8b9c8a0ba1207caa3edeefc3e5f45
```

Actual provider data are retained only in ignored local directories, relative to
the repository root:

- Cache, setup confirmation/mapping/helper and interaction/verification reports:
  `data/history_cache/pr5e-2bwjfyls-attempt1/`.
- Original immutable snapshot:
  `data/history_cache/pr5e-2bwjfyls-attempt1/snapshots/ibkr/1bc996f7a7d848499fd50ff05ddbc771/`.
- Offline frozen dataset:
  `data/research_datasets/pr5e-ibkr-SPY-20261012-20261016-2bwjfyls/`.

These existing artifacts can be inspected without reconnecting:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli data history \
  --provider ibkr --symbols SPY --start 2026-10-12 --end 2026-10-16 --mode offline \
  --mappings data/history_cache/pr5e-2bwjfyls-attempt1/setup/mappings.json \
  --cache data/history_cache/pr5e-2bwjfyls-attempt1

PYTHONPATH=src .venv/bin/python - <<'PY'
from equity_research.history import load_research_dataset
dataset = load_research_dataset(
    "data/research_datasets/pr5e-ibkr-SPY-20261012-20261016-2bwjfyls")
print(len(dataset.bars("SPY")), dataset.quality("SPY")["status"])
print(dataset.content_sha256)
PY
```

A later live repeat must still meet the current-session paper, socket, Read-Only
and port prerequisites; reconfirm settings if the session or configuration has
changed. Use a unique positive client ID, an explicitly reviewed mapping/window
and new output paths. The preflight is a dated record of this run. Do not
automatically rerun the live test from pytest, CI, offline loading or documentation
checks.

## Limits and regression

Successful live integration is established for this endpoint, pinned client,
qualified SPY contract and five-session request only. Other securities, delisted
or renamed coverage, other TWS builds, broader entitlements, failure/retry paths
and repeated retrieval stability were not tested live. Mocked coverage remains
separate. The request does not independently verify historical venue/identity
history or historical screening membership.

Price metadata remain `IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED`, volume metadata
`IBKR_NATIVE_UNITS_UNVERIFIED`, and basis verification remains false. All five
adjusted-close values remain absent. There is no IBKR corporate-action feed in
this adapter; absent events do not establish completeness. Historical availability
and action completeness remain unknown. No streaming market-data type was
requested; TRADES/RTH request metadata are explicit.

The dataset remains technical research input with
`NOT_EVALUATED_USE_EXISTING_EXPORT_GATES`. It is not a verified raw execution
dataset, is not automatically exported to the backtester, and does not relax the
PR 5B raw/no-actions/actual-availability gates. No real-stock strategy replay,
optimization, order, paid subscription, deployment or next milestone occurred.

The unchanged offline regression suite passed before and after this live test.
Final result: **180 passed in 19.30s**, with no failures or skips. Git whitespace,
the aggregate evidence schema and eight local documentation links also passed
verification. No new tests or mocks are presented as live provider evidence.
No canonical lint command is configured. Historical PR 5A–5D reports are unchanged;
this report records the subsequent live result.
