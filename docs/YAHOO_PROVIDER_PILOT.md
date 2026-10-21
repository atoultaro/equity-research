# PR 5B Yahoo provider-quality pilot record

Date: 2026-10-21 (America/New_York). Branch: `feat/yahoo-historical-data-v1`.
Status: **offline implementation validated; real acquisitions NOT RUN because
permitted retrieval/retention has not been established**. This is the fallback
explicitly allowed by the PR 5B brief, not a successful provider pilot.

Inspected equity base: `d874f15c712fa32096435e30ef56b048565409db` (merged PR 5A).
Read-only cannoslim reference: `6f1a01d1db2cbc24abc845c190af7acaf6701834`.
No changes were made to cannoslim, finwhaling, the shared wheel, existing replay
logic, accounting or synthetic inputs.

## Access and permitted-use finding

**VERIFIED:** the [yfinance project's usage notice](https://github.com/ranaroussi/yfinance)
describes personal research use and directs users to Yahoo terms for data rights.
The [Yahoo terms endpoint](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)
returned status 999 to the documentation retrieval tool. That is a documentation
access observation, **not** a Yahoo historical-price API acquisition result.
No account-specific entitlement or affirmative permission to archive the requested
provider data was supplied or established. This report does not infer either
permission or a universal prohibition from those facts.

**UNKNOWN:** whether this user's intended retrieval, retention and any later
sharing are permitted. Under the brief's instruction to stop provider activity
when retention permission is unclear, no Yahoo price request was made. No
restrictions were bypassed, no subscription was purchased and no data was
redistributed. No provider snapshot directories or licensed market-data files
were generated in the tracked source tree. Offline diagnostic fixtures are
explicitly synthetic and run in isolated temporary directories.

## Pinned request contract

Adapter: yfinance **0.2.66**, installed/imported and checked against its public
download signature offline. Calendar: exchange-calendars **4.13.1**; pandas
**2.2.3**, numpy **2.2.4**, tzdata **2025.2**. These are optional extras; core
replay still runs without them. Client network compatibility remains unmeasured.

Each proposed call uses one ticker and the following explicit parameters; table
entries below supply `tickers`, inclusive `start` and exclusive provider `end`:

```json
{
  "interval": "1d",
  "auto_adjust": false,
  "back_adjust": false,
  "actions": true,
  "repair": false,
  "keepna": true,
  "rounding": false,
  "prepost": false,
  "group_by": "ticker",
  "threads": false,
  "ignore_tz": false,
  "multi_level_index": true,
  "progress": false,
  "period": null,
  "timeout": 15.0
}
```

No supported original-payload hook was established in the pinned public download
interface. Any future acquisition therefore declares `capture_level="client_return"`
and archives the full returned frame; it does not claim wire fidelity. Actual
request UTC times, installed version, outcome, coverage and safe error codes
would be recorded in each immutable attempt. They do not exist for this unrun
network pilot; no fabricated timestamps, ranges or result counts appear here.

## Basket disposition

Expected counts below were computed **offline from the pinned exchange calendar**,
not observed from Yahoo. They are full exchange sessions over the inclusive range,
before security-specific listing exclusions. FB and META are separate requests
for an alias comparison; their data must not be stitched automatically.

| Provider symbol | Inclusive research interval | Exclusive request end | Expected XNYS sessions | Yahoo outcome | Returned range/count |
| --- | --- | --- | --- | --- | --- |
| SPY | 2024-11-20–2024-12-06 | 2024-12-07 | 12 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |
| AAPL | 2014-05-27–2014-06-20 | 2014-06-21 | 19 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |
| AAPL | 2020-08-17–2020-09-11 | 2020-09-12 | 19 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |
| MSFT | 2024-02-01–2024-03-01 | 2024-03-02 | 21 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |
| FB | 2022-05-23–2022-06-24 | 2022-06-25 | 23 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |
| META | 2022-05-23–2022-06-24 | 2022-06-25 | 23 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |
| TWTR (conditional) | 2022-10-03–2022-11-04 | 2022-11-05 | 25 | NOT_RUN_TERMS_UNRESOLVED | UNKNOWN / not measured |

Independent event references establish cases to investigate; they do **not**
establish how Yahoo represents them:

- SPY interval includes Thanksgiving closure and November 29 early close; these
  are calendar checks. No SPY distribution feed or issuer price comparison was
  acquired; the distribution/adjustment assessment remains UNKNOWN.
- [Apple's issuer history](https://investor.apple.com/dividend-history/default.aspx)
  identifies first split-adjusted trading dates June 9, 2014 (7:1) and August 31,
  2020 (4:1). These differ from record dates; Yahoo price/volume factors were not
  measured.
- [Microsoft's issuer-authored dividend announcement](https://www.prnewswire.com/news-releases/microsoft-announces-quarterly-dividend-301999937.html)
  identifies a $0.75 dividend with February 14, 2024 ex-date and March 14 payment.
  No API event or adjusted-close factor was observed.
- [Meta's issuer announcement](https://investor.atmeta.com/investor-news/press-release-details/2022/Meta-Platforms-Inc.-to-Change-Ticker-Symbol-to-META-on-June-9/default.aspx)
  dates the FB-to-META symbol change to June 9, 2022. Current metadata cannot
  establish historical query identity or stitching.
- [Twitter's issuer SEC filing](https://www.sec.gov/Archives/edgar/data/1418091/000119312522272772/d411753d8k.htm)
  records suspension before October 28, 2022 open after the merger. The reference
  calendar still has 25 exchange sessions in the full proposed interval; this is
  not a claim that TWTR should return 25 bars. Retention, terminal bar and symbol
  reuse remain UNKNOWN. Never fabricate merger settlement as a price bar.

Offline schedule hashes (the schedule record excludes its own hash field):

| Inclusive interval | `schedule_sha256` |
| --- | --- |
| 2024-11-20–2024-12-06 | `bd37697031a62036e3cdded6c07e23e4dbbee71ed5697c7f3667a58fa373c1c5` |
| 2014-05-27–2014-06-20 | `34ab42e0ab6b388717df47f07ba186c0441b6d70419d81d1eaf37ff6e8dcd36b` |
| 2020-08-17–2020-09-11 | `a1e24e74721fe1ad1e8f5b7b64aa8a34c957cc12d33ff8e5c69dfb9b57582cd9` |
| 2024-02-01–2024-03-01 | `ce53f428bbc241b25217342f231cf6a394fe32741a617717fa1963510a2e90dc` |
| 2022-05-23–2022-06-24 | `db40f995fdb61d0c12c870e2406a75a4c8813998da9d535c5874f67cfa4f388a` |
| 2022-10-03–2022-11-04 | `21faf87971082690d06999933916a6c675dde65e2e0e24b667331fb1f50c7b57` |

## Findings and export gates

| Area | Real-provider evidence | Offline implementation evidence |
| --- | --- | --- |
| Acquisition | NOT RUN; live success, empty/error and partial behavior UNKNOWN | Mocked complete, empty, partial, schema, exception/timeout, logged error and version-mismatch records. |
| Snapshot fidelity | Wire access not exposed through supported download return; actual response UNKNOWN | Tagged frame round trips retain index hierarchy, duplicate rows/columns, nulls, exact finite floats and dtypes; overwrites/hash corruption reject. |
| Coverage/OHLCV | Missing sessions, fields, duplicates, zero volume and discontinuities unmeasured | Canonical diagnostics retain anomalies; independent calendar catches interior gaps and off-calendar rows without filling prices. |
| Calendar | Reference dates known; security-specific schedule alignment UNKNOWN | Holiday, early close, DST and January 9, 2025 tests pass; actual listing venue remains distinct from XNYS. |
| Corporate actions | Returned events/completeness UNKNOWN; issuer event references above are separate facts | 4:1 split, dividend, rename and later split fixtures block current raw export; absent events alone do not pass. |
| Basis | API OHLC/dividend/split/volume basis UNKNOWN; `auto_adjust=False` supplies no attestation | RAW_VERIFIED requires affirmative separate basis/volume evidence and horizon coverage; SPLIT_ADJUSTED/OTHER_ADJUSTED/UNKNOWN block. |
| Historical availability | UNKNOWN; no publication/finalization evidence or approved model | Missing/model-labeled/out-of-session timestamps block; no close-plus-latency model introduced. |
| Revisions | No repeated real downloads; NOT_APPLICABLE to observed results | Fixed snapshots with corrections/null/schema/date changes produce byte and semantic diffs; old snapshots remain unchanged. |
| Export | No real dataset exists; no real EXPORT_READY decision or replay performed | Explicitly synthetic evidenced fixture is EXPORT_READY and accepted by unchanged loader; unknown evidence blocks and writes reports without replay files. |

No actual Yahoo event behavior, price factors, volume units or repeat-download
stability is claimed. No ten-year history query, universe acquisition, strategy
comparison, broker operation or optimization ran. Synthetic acceptance results
are evidence of mechanics only, not a trading edge.

## Validation and next review

The final full regression command was `.venv/bin/python -m pytest -q`:
**112 passed in 25.55s**, including all 58 unchanged existing regression cases
and 54 new data-preparation cases. Git whitespace checks and local documentation
link checks passed. Protected strategy/replay/accounting/loader/model/reporting,
fixtures and shared-wheel paths were compared to the base and are unchanged.
Focused data tests use hand-authored synthetic responses
under the existing no-network fixture, plus an offline pinned-client signature
check. The synthetic README workflow is exercised in a subprocess. Clean-runtime
installation and all existing PR 4 accounting/replay tests remain in the suite.

The [data contracts](DATA_PREPARATION.md) document exact schemas, gate requirements
and known scope limits. No discrepancy with PR 5A source findings was observed.
The PR 5B brief explicitly permits honest `client_return` capture; this implements
that fallback rather than claiming PR 5A's aspirational wire-payload gate passed.

Recommended next review: settle permitted retrieval/retention before running
these same seven bounded requests, preserve failures without substituting symbols,
and compare real responses to independent issuer/exchange evidence. Repeated
retrievals must be explicitly recorded as performed, with semantic and byte diffs.
Historical availability and raw-basis approval remain separate decisions. Do not
start PR 6 or relax the replay contract automatically.
