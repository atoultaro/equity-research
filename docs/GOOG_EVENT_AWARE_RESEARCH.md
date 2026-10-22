# GOOG historical prices and corporate events (PR 6B)

**Partial real-data outcome:** five GOOG sessions were acquired successfully, but
IBKR subsequently rejected all 35 chunks of the fixed historical target with error
162. A single diagnostic request matched the broker's “different IP” condition.
The complete target was not acquired. The immutable study explicitly contains
five of 703 expected sessions; missing data and unsupported timing remain missing.
This is a generalization and evidence-quality study, with no trading conclusion.

Branch: `feat/goog-event-aware-research-v1`. The authoritative PR 6B brief permits
the narrowly bounded historical-only broker/source work for this task, overriding
the older generic no-broker/no-fetch instruction in AGENTS.md for that scope.
The [aggregate evidence](evidence/goog-event-aware-v1.json) records actual requests,
errors, environment, identities, source references, audits and complete file hashes.
Real OHLCV and joined event/source assertions remain in ignored local storage.

## Inspected revisions and reuse

| Repository | Exact inspected commit | Role |
| --- | --- | --- |
| equity-research main | `b3fe6aa879ce3bb58744efe82081dffd397c286d` | Merged PR 6A, including the corporate-action overlap correction |
| finwhaling | `98034e009ac2c062e5a23aad1ba1cf56f2c94001` | Read-only historical adapter reference |
| cannoslim | `6f1a01d1db2cbc24abc845c190af7acaf6701834` | Read-only prices and earnings-overlay reference |

PR 6A was merged before this branch was created; there is no open dependency.
Neither reference repository was changed. Independent cannoslim working-tree
changes were left untouched. Inspected source-file hashes are in the evidence.
Its current earnings cache is not used as a historical publication archive.

The PR 5D/5E/6A provider, request chunking/pacing, cache, native capture, normalization,
price/event schemas, session alignment, immutable composition and offline loaders
are reused. There are no GOOG branches in the production implementation. The only
diagnostic additions expose the reaction Close and native Open-minus-prior-Close
change. A generic comparison function checks identical intervals, expected
sessions, calendar, schemas, diagnostic implementation and calculation definitions
before reporting observed evidence counts. Shared ATR still comes from the pinned
market-shared 0.2.0 wheel, source `57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`.
Acquisition, price adjustment, publication rules and execution/accounting policies
are unchanged.

## Security identity and live qualification

The selected instrument is **Alphabet Inc. Class C nonvoting capital stock, GOOG**,
ISIN `US02079K1079`, research identity `research:GOOG:ClassC:USD:v1`.
Issuer identity: `SEC:CIK:0001652044`. The
[issuer-filed 8-K cover](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000047/goog-20240425.htm)
separately identifies Class A common stock (`GOOGL`) and Class C capital stock
(`GOOG`). The same-ISIN exchange notice below corroborates the Class C identity.
GOOGL prices were neither requested nor substituted.

All three actual qualifications returned the same single contract:

```json
{"conId":208813720,"symbol":"GOOG","secType":"STK","exchange":"SMART",
 "primaryExchange":"NASDAQ","currency":"USD","localSymbol":"GOOG","tradingClass":"NMS"}
```

The contract ID was obtained from TWS, not guessed. The sealed setup sidecar
deliberately has a null pre-qualification contract ID; source captures, frozen
price provenance and the aggregate identity record retain the actual result.
Contract symbol, security type, currency, SMART routing and primary exchange are
checked before requesting bars. A deterministic regression rejects a qualified
GOOGL substitution before historical acquisition.

The existing security-bound `corporate_events_v1` schema is retained. Event
payloads add `issuer_id`, `issuer_event_id`, `event_scope`, applicable share classes
and the selected Class C identity. An Alphabet earnings release is one issuer
occurrence, with prices/outcomes bound to the selected security. These payloads
describe a projection; v1 is not a normalized, multi-security issuer-event store.
Synthetic Class A/C projections share an issuer event/document while keeping
distinct security prices and rejecting cross-security joins. No actual GOOGL
price instrument or duplicate independently published Alphabet release was added.

## Actual acquisition and safety audit

Before any connection, the user freshly confirmed the current authenticated paper
TWS Classic session, socket clients, Read-Only API and port 7497. Endpoint:
`127.0.0.1:7497`; client ID `51867`. A local listener was observed. All three API
handshakes succeeded without a client-ID conflict. Installed ib_async is 2.1.0,
Python 3.12.9, TWS server protocol 178. No settings were changed. UTC captures are
dated October 22, 2026 (October 21 in New York); the fixed target was not advanced.

| Attempt | Requested scope | Observed outcome |
| --- | --- | --- |
| Five-session smoke | October 14–20, 2026 | SUCCESS: seven native bars, five selected sessions, two earlier native bars explicitly excluded |
| Full fixed target | January 2, 2024–October 20, 2026 | PARTIAL_RESPONSE: 35 failed chunks, zero returned bars; error 162 for each request |
| Bounded diagnostic | January 2–31, 2024 | PARTIAL_RESPONSE: one failed request, zero bars; allowlisted error term `different ip` matched |

The diagnostic retains only known error terms, numeric codes and categories, not
arbitrary broker error text. The adapter's generic category remains PROVIDER_ERROR;
the diagnostic supplies narrower observed evidence without inventing an entitlement
finding. Requests then stopped. There was no login, account-setting change or
workaround for the competing-session/data-access condition. The smoke establishes
historical access only for that successful request; it does not prove continuing
entitlements or access to the full target.

All requests used the existing daily `TRADES`, RTH, USD workflow: `1 day`,
`formatDate=1`, `keepUpToDate=false`, 30-second timeout; at most 30 calendar days
per chunk. Actual request windows, duration/end parameters and attempt numbers
are in the evidence. Each failed chunk had one attempt; no retry amplification
occurred. Existing serial pacing remains two seconds between requests, at least
15 seconds for identical requests and 60 requests per 600 seconds per adapter.
Across this run only 37 historical requests occurred. Callback and request-level
error observations can repeat the same 162; they are not additional requests.
Informational codes 2104, 2106 and 2158 were also retained.

The failed responses were sealed and withheld from cache promotion. The successful
smoke remains the cached input: **five valid numeric OHLCV rows, 698 missing
sessions**, zero duplicate/off-calendar/outside-listing rows and zero canonical
numeric issues. Independent XNYS 4.13.1 reconciliation expects **703** sessions in
the unchanged target. Price quality is **FAIL for completeness**, and the price
freeze explicitly uses `--allow-incomplete`. No missing bar was filled, repaired
or obtained from Yahoo. All seven native smoke bars, including the two excluded
ones, survive in the embedded source snapshot with original indices/hashes.

The outgoing-message guard permitted only API startup (71), contract details (9),
historical bars (20) and historical cancellation (25). Observed totals: **three
startups, three qualifications, 37 historical requests, three disconnects; zero
blocked messages or cancellations**. No account, balance, portfolio, position,
execution, order, streaming subscription or trade request occurred. The low-level
handshake avoids ib_async's automatic account synchronization; no account IDs or
authentication secrets were persisted/logged by the workflow. No second TWS
session was started.

## Source inventory and evidence precision

The timeline contains **22 occurrences: 11 earnings, 10 dividend announcements
and one historical split**, backed by 25 source references. Full local assertions
bind manually reviewed extracted facts, explicit unknowns and source IDs. These
are not original page-byte captures or an independently archived revision history.
Public access does not establish redistribution permission for the joined table.

Starting points were [Alphabet Investor Relations](https://abc.xyz/investor/) and
[SEC issuer filings](https://www.sec.gov/edgar/browse/?CIK=1652044).
The following issuer-filed exhibits supply the earnings inventory. Revenue uses
the financial table's millions-of-USD precision; EPS is GAAP diluted EPS. Fiscal
period ends are retained separately from release dates; unusual reported gains
are not removed or normalized.

| Fiscal earnings release | Reviewed issuer source |
| --- | --- |
| FY2023 Q4 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000014/googexhibit991q42023.htm) |
| FY2024 Q1 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000047/googexhibit991q12024.htm) |
| FY2024 Q2 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000076/googexhibit991q22024.htm) |
| FY2024 Q3 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000115/googexhibit991q32024.htm) |
| FY2024 Q4 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000010/googexhibit991q42024.htm) |
| FY2025 Q1 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000040/googexhibit991q12025.htm) |
| FY2025 Q2 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000056/googexhibit991q22025.htm) |
| FY2025 Q3 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000087/googexhibit991q32025.htm) |
| FY2025 Q4 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000012/googexhibit991q42025.htm) |
| FY2026 Q1 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000043/googexhibit991q12026.htm) |
| FY2026 Q2 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm) |

Only actual releases inside the fixed interval are counted. Exact announcement
clocks and before/after-session relations were not independently established:
**all 22 timestamps are null, DATE precision, relation UNKNOWN**. Conference-call
starts and EDGAR acceptance timestamps are not substituted for original release
times. Thus all 11 earnings have ambiguous same/next-session reaction alignment.
Verified synthetic examples still exercise before-open, after-close and unknown
precision through the same functions; existing tests cover nontrading days.

Dividend amount, announcement, record and payment facts use the corresponding
issuer 8-K bodies and releases (all ten body URLs and evidence notes are in the
aggregate source inventory). Some dividend facts appear in Item 8.01 rather than
the earnings exhibit. The initial April 2024 board-declaration day is explicit;
the other nine exact board days remain null. A dated public announcement is not
silently treated as the actual board-meeting day.

**One ex-date is independently source-reported; nine remain unknown.**
The [Nasdaq-hosted BNK Invest report](https://www.nasdaq.com/articles/ex-dividend-reminder-alphabet-constellation-energy-and-viatris)
explicitly names US GOOG's March 9, 2026 ex-date. This is contributed market
reporting, **not an official Nasdaq corporate-action notice**. The
[Deutsche Boerse notice for ISIN US02079K1079](https://www.cashmarket.deutsche-boerse.com/cash-en/Stay-Informed/newsroom/Xetra-Frankfurt-Newsboard/XETR-DIVIDEND-INTEREST-INFORMATION-09.03.2026-US02079K1079-4997284)
independently corroborates the same Class C security/date; its public indexed
notice text was inspected, while direct full-page retrieval returned a cache
miss. A foreign-venue notice alone is not used to determine a US ex-date. The
local record explicitly retains this verification scope and its partial status.
Obtaining an official US notice remains desirable. No ex-date is inferred from
record/payment dates, holiday arithmetic or settlement conventions.

The Nasdaq dividend-history table was unavailable. Alphabet's dynamic IR pages
and older asset redirects did not provide a complete usable archive. One SEC
submissions-JSON request was denied and was stopped without changing identity,
headers or access methods to bypass the denial; ordinary public filing pages
supplied the cited facts. These source limitations are recorded explicitly.

The [February 1, 2022 issuer 8-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204422000015/goog-20220201.htm)
announces the **20-for-1 split**, July 1 record date and distribution **after close
July 15**. [OCC memo 50543](https://infomemo.theocc.com/infomemos?number=50543)
independently identifies Class C and **July 18, 2022** as the ex-distribution/
first adjusted trading date. These dates retain distinct meanings. The issuer
tax-form PDF was identified but its text layer was unreadable; no extracted PDF
claim is asserted. No 2022 bars were requested, and the target's bars do not
empirically validate this older split or its volume/price ratio.

## Alignment, knowledge and descriptive results

Both companies use `corporate_events_v1`, `regular_session_events_v1`, the pinned
XNYS 4.13.1/New York regular-session convention and the same diagnostics file hash.
Calendar bounds extend to documented old splits, but the 703 expected price
sessions match exactly. Verified dividend ex-dates align independently of their
announcement clock: the one reviewed ex-date maps to its exact session with no
calendar error. Unknown ex-dates have no reaction session. No date is shifted to
repair an invalid effective day.

`retrospective` includes all evidence, alignments and outcomes. `as_known(cutoff)`
requires a source-bound full assertion with verified publication strictly before
the cutoff. The later ex-date report is partial support, not proof that the entire
joined dividend record was known at its earlier announcement. All full GOOG
assertions lack a verified publication timestamp; **zero records are admitted at
the study-end cutoff**, with 22 records' knowledge unknown. Capture times never
become publication times. Historical source/revision completeness remains UNKNOWN.

All **22 actual GOOG diagnostics are UNAVAILABLE**:

- Eleven earnings: ambiguous announcement timing; there is no defensible reaction
  open or earnings gap/volume/ATR/future-return calculation.
- Nine dividends: unknown ex-dates.
- One verified-ex-date dividend: aligned, but both preceding and ex-session prices
  are outside the five acquired sessions. Prior Close, ex Open/Close, native Open/
  Close changes, volume/ATR and outcomes remain unavailable. Nominal cash remains in the
  local event inventory; it does not replace a price observation.
- One split: price/share/volume basis is unverified, and its effective date is
  outside the fixed target.

No numeric GOOG event-window result or total return is claimed. The actual partial
study's all-session review has zero observed absolute gaps at the fixed 5% flag
and zero volume flags, **but 698 adjacent session pairs cannot be evaluated**.
These counts do not characterize discontinuities throughout the missing history.
No causal price-move attribution is made.

For valid windows the shared definitions remain: prior completed Close to reaction
Open gap; reaction High minus Low; reaction volume divided by the previous 20
sessions; shared simple ATR14 from the 15 preceding completed bars; and Close
returns from reaction Close to exactly 1/5/10 later expected sessions. Missing
warmup or intervening observations stay null. New `first_post_close` and dividend
`open_change_dollars` expose native inputs/changes alongside existing cash and
Close-change fields without applying an adjustment.

The basis remains `IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED`, not dividend-adjusted,
with `IBKR_NATIVE_UNITS_UNVERIFIED`, overall `verified=false`. No RAW_VERIFIED
label, total-return conversion, split back-adjustment or execution export is added.
Native changes cannot establish a mechanical dividend effect even with full bars.

The PR 6A window correction is unchanged: all nine unknown ex-dates remain global
evidence gaps, not repeated overlap claims. There are no source-backed effective
date bounds in these actual inputs and no computable GOOG windows. Zero overlap
annotations does not establish absence or completeness. Deterministic cases cover
genuinely overlapping verified actions and separate bounded uncertainty.

## AAPL versus GOOG: observed evidence completeness

The generic comparison uses the new AAPL v4 study and GOOG v1; both were composed
using the same current implementation and unchanged underlying source inputs.
This compares evidence and calculation availability, not company performance.

| Dimension | AAPL | GOOG |
| --- | --- | --- |
| Requested interval | 2024-01-02–2026-10-20 | Same |
| Selected / expected price sessions | 703 / 703 | 5 / 703 |
| Price completeness | PASS | FAIL: 698 missing |
| Duplicate / off-calendar rows | 0 / 0 | 0 / 0 |
| Earnings records | 11 | 11 |
| Dividend announcements | 11 | 10 |
| Verified / unknown ex-dates | 0 / 11 | 1 / 9, with source-grade limitation above |
| Historical splits | 2, both outside price interval | 1, outside price interval |
| Minute / date-only announcement precision | 22 / 2 | 0 / 22 |
| Ambiguous earnings reactions | 0 | 11 |
| Available earnings / dividend / split diagnostics | 11 / 0 / 0 | 0 / 0 / 0 |
| Source references | 25 | 25 |
| Basis independently verified | No | No |
| Historical publication/revision archive completeness | UNKNOWN | UNKNOWN |

All 150 pre-existing research/cache files were checked byte-for-byte unchanged.
All original AAPL bars, event/source inputs, alignments, checked as-known views and
existing numeric diagnostic fields match v3 exactly. The new reaction-Close field
requires a new combined-study hash; v3 and every earlier version remain intact.
Historical PR 5/6A reports and aggregate evidence are unchanged.

## Immutable local artifacts and offline reproduction

Paths below are ignored local artifacts. Complete per-file hashes, source
references, failed-capture hashes and software/implementation identities are in
the aggregate evidence. Hashes establish integrity, not truth or licensing.

| Artifact | Local path | SHA-256 bundle identity |
| --- | --- | --- |
| Successful smoke native snapshot | `data/history_cache/pr6b-goog-5b2nlv7/snapshots/ibkr/355c2a6e710741a682c8e2e7bc230c1e` | `186f4a81ce613012778ae975ccd1a461186fd810017c8803c851487b2cc0e442` |
| Failed full-target snapshot | `data/history_cache/pr6b-goog-5b2nlv7/snapshots/ibkr/d39476cd3fff4c10ba56802d4fcce82b` | `53751e597e12ede577d4d175d22f96f847e440be647850e9b5e3a146fb34d169` |
| Failed diagnostic snapshot | `data/history_cache/pr6b-goog-5b2nlv7/snapshots/ibkr/d691c22673fe4c69b914585b8ab1b58b` | `0f9770db57f7d711a45f390c12365a76af8a1798e2b1aba9e47aa6d537753cba` |
| Incomplete GOOG prices v1 | `data/research_datasets/pr6b-goog-5b2nlv7-prices-v1` | `ce85202197ddc980a98348e54cf8d5bef3e521be5ca61a26785f9298133620b6` |
| GOOG events v1 | `data/research_datasets/pr6b-goog-5b2nlv7-events-v1` | `6cf0647c5a4847a52c6fde94650ffe8da4569aafc45300e5441bbd04dea4ac2a` |
| GOOG combined study v1 | `data/research_datasets/pr6b-goog-5b2nlv7-study-v1` | `776e554da69aa17925284d578c584fea3622753159e228d75e3a6ca11bf14483` |
| New AAPL comparison study v4 | `data/research_datasets/pr6b-aapl-5b2nlv7-study-v4` | `d967ba2ce3da7f04816486bc737c69f34199fd3aa0ccb384e637fac1a7f9ca4f` |
| Comparison and offline verification | `data/research_datasets/pr6b-evidence-comparison-5b2nlv7-v1` | `497febe828d82529e9ee73c69eb3f62433b9d8efd57eabd2b8381125628cc91a` |

Manually reviewed event inputs/build helper are sealed under
`data/research_datasets/pr6b-goog-5b2nlv7-event-inputs-v1`, hash
`781ceec91e36f1a5b3e35548cf94f87db1a9ace3705cd950431f3be0a3ae8040`.
Setup, message audits, immutable outcomes/reports and diagnostic helper are under
`data/history_cache/pr6b-goog-5b2nlv7`. No sealed directory may be overwritten.
A later successful acquisition or evidence correction needs new immutable versions.

Offline loading and comparison require the standard library and installed project,
with no broker, network, provider SDK, calendar library, cache or original inputs:

```python
from equity_research.events import load_event_study
from equity_research.events.comparison import compare_event_studies

goog = load_event_study("data/research_datasets/pr6b-goog-5b2nlv7-study-v1")
aapl = load_event_study("data/research_datasets/pr6b-aapl-5b2nlv7-study-v4")
assert len(goog.bars()) == 5
assert len(goog.retrospective["events"]) == 22
assert goog.as_known("2026-10-21T00:00:00-04:00")["events"] == []
report = compare_event_studies({"AAPL": aapl, "GOOG": goog})
assert len(report["studies"]["GOOG"]["missing_sessions"]) == 698
```

Actual loading, comparison, AAPL preservation and as-known checks passed with
network sockets and all optional/provider imports denied. Frozen event quality,
alignment, diagnostic and completeness reports remain inspectable offline.
With the existing pinned extras, recompose reviewed local inputs to a **new** path:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli data event-study \
  --prices data/research_datasets/pr6b-goog-5b2nlv7-prices-v1 \
  --events data/research_datasets/pr6b-goog-5b2nlv7-events-v1 --symbol GOOG \
  --output data/research_datasets/goog-offline-review-v2
```

A new clone contains no real dataset; use deterministic fixtures for reproducible
framework validation. Full offline regression: **254 passed in 33.55 seconds**,
zero failures, `.venv/bin/python -m pytest -q`. Focused new regressions:
**12 passed in 3.45 seconds**, `tests/test_goog_events.py`. Existing 242 tests,
including AAPL overlap/timing, offline loading and execution/accounting tests,
remain passing. Normal tests deny network sockets; live attempts are outside CI.
No lint command is configured.

Further work within a separately confirmed live session can retry the unchanged
target after the TWS data-access conflict is resolved. Freeze any success as new
versions. Seek primary US ex-date notices and verified release/publication clocks,
then verify native price/share/volume semantics and historical revision evidence.
PR 6B does not start PR 6C, strategy development or deployment.
