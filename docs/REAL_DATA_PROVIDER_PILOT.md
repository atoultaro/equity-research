# PR 5C: Real historical data pilot and provider decision

Review date: **2026-10-21, America/New_York**. Branch:
`research/real-data-provider-validation-v1`. Status: documentation and permissions
evaluation completed; **no real market-data acquisition was authorized or run**.
Repeatability: **NOT_TESTED**. This is not successful empirical provider validation.

## 1. Executive recommendation

**Recommend EODHD as the next candidate for a separately reviewed, licensed
acquisition pilot, conditional on retention/publication and data-basis clarification.**
Do not purchase a plan, create an account or implement its adapter in PR 5C.
Keep the Yahoo adapter dormant: the permission prerequisite for the scoped
automated route has not been satisfied. Standard Tiingo plans are a poor fit for
the requested archival lifecycle. The permission findings below distinguish these
decisions from technical capabilities and from a legal guarantee.

No source is approved for the current execution simulator. No real price series,
corporate-action feed, historical availability record or survivorship-free
universe was validated. A paid subscription or an adjusted historical series
would not by itself satisfy those research contracts.

## 2. Revisions and implementation inspected

| Repository | Exact inspected SHA | Boundary |
| --- | --- | --- |
| `atoultaro/equity-research` | `e699201aa0bbdafba59e12b55b8751581ed252a7` | Clean starting research branch; latest remote `main` matched; includes merged GitHub PR #3 / project PR 5B. |
| `atoultaro/cannoslim` | `6f1a01d1db2cbc24abc845c190af7acaf6701834` | Read-only reference. Relevant price/universe/calendar/test paths matched HEAD; unrelated pre-existing worktree changes were not used or changed. |

Read [AGENTS.md](../AGENTS.md), [README](../README.md),
[MVP specification](MVP_SPEC.md), [research conventions](RESEARCH_CONVENTIONS.md),
[PR 5A audit](YAHOO_DATA_SOURCE_AUDIT.md),
[PR 5B pilot record](YAHOO_PROVIDER_PILOT.md) and
[data-preparation contracts](DATA_PREPARATION.md). Actual source inspected:

- [Yahoo request boundary](../src/equity_research/providers/yahoo.py): one symbol,
  inclusive research dates converted to exclusive next-day provider end; pinned
  yfinance 0.2.66, explicit flags, client-return capture and safe outcome records.
- [Snapshot/comparison](../src/equity_research/ingestion/snapshots.py),
  [storage](../src/equity_research/ingestion/storage.py) and
  [frame serialization](../src/equity_research/ingestion/frames.py): immutable
  exclusive directories, byte hashes and semantic comparisons; no wire-payload claim.
- [Canonical conversion](../src/equity_research/ingestion/canonical.py),
  [calendar](../src/equity_research/ingestion/calendar.py),
  [quality](../src/equity_research/ingestion/quality.py) and
  [export](../src/equity_research/ingestion/export.py): anomalies retained,
  independent XNYS schedule, affirmative evidence gates and strict existing loader.
- [Data CLI](../src/equity_research/ingestion/cli.py) and
  [ingestion tests](../tests/test_ingestion.py): separate `fetch-yahoo`, `validate`,
  `compare`, `export`; successful validation-command execution does not mean
  replay eligibility. No production or test change was justified by this review.

Evidence labels: **VERIFIED_CODE** = inspected implementation/test evidence;
**VERIFIED_DOC** = primary publisher's documentation claim, not an independently
observed response; **OBSERVED** = actual activity in this PR; **INFERRED** = review
judgment; **UNKNOWN** = insufficient evidence. Neither synthetic tests nor
documentation examples count as our empirical market-data acquisition.

## 3. Phase A: permissions for the intended workflow

Scope: one individual's own investment research, private code repository, local
immutable snapshots and repeatable offline analysis; only code and safe aggregate
findings proposed for publication. No raw data distribution, account sharing,
business service, public data hosting or commercial redistribution is assumed.
Private GitHub hosting alone does not resolve data licensing or collaborator access.
Timezone is not proof of jurisdiction or non-professional status.

Classifications are operational review decisions: `PERMITTED_FOR_SCOPED_PILOT`
means the described use has supporting terms subject to the stated conditions;
`RESTRICTED` means an unmet express restriction applies; `UNRESOLVED` means no
sufficient grant/interpretation was established. They are not legal guarantees.

### 3.1 Yahoo and yfinance are different permission boundaries

**VERIFIED_DOC:** [yfinance 0.2.66 README][Y-client] identifies an Apache software
license, describes research/personal use and directs data-rights questions to
Yahoo. This supports using the client software; it is not Yahoo's authorization
to collect or retain licensed data.

**VERIFIED_DOC, indexed official text:** [Yahoo general terms][Y-terms], §2(b)(9),
requires prior permission for automated collection: “without our express, prior
permission.” No grant was established. **INFERRED:** this route is `RESTRICTED`;
personal intent does not establish the exception.

Direct terms retrieval returned **999**; Finance supplement retrieval failed;
Help returned **429**. Official indexed text was crawled last month. These are
documentation-access observations, not API outcomes or a universal prohibition.
Supplemental/account-specific authorization remains **UNRESOLVED**.

| Required distinction | Yahoo data route / client conclusion |
| --- | --- |
| API/client authorization | Client software: PERMITTED_FOR_SCOPED_PILOT; collection route: RESTRICTED. |
| Underlying data rights | UNRESOLVED. |
| Local storage/retention | UNRESOLVED. |
| Repeated downloading | RESTRICTED on the same prerequisite. |
| Internal computation | UNRESOLVED for this acquisition route. |
| Derived statistics/publication | UNRESOLVED. |
| Redistribution | UNRESOLVED; excluded. |
| Commercial use | UNRESOLVED/out of scope. |

### 3.2 EODHD permission assessment

**VERIFIED_DOC:** [EODHD terms][E-terms], Personal Use, permit eligible
non-professionals to “store, manipulate, and analyze” privately and noncommercially;
account/data sharing is restricted. Access uses a registered account/API key.
**INFERRED:** a correctly entitled private pilot is `PERMITTED_FOR_SCOPED_PILOT`;
the complete workflow is **UNRESOLVED** until post-cancellation archival rights
and publication of these particular diagnostics are confirmed. Silence is not
perpetual-retention permission. No account was registered or entitlement assumed.

| Required distinction | EODHD conclusion for this workflow |
| --- | --- |
| API/client and underlying access | PERMITTED_FOR_SCOPED_PILOT conditional on valid account, plan and user eligibility. |
| Local storage | PERMITTED_FOR_SCOPED_PILOT privately; post-termination retention UNRESOLVED. |
| Repeated downloads | Conditional on plan limits; no unlimited-use assumption. |
| Internal computation | PERMITTED_FOR_SCOPED_PILOT under the stated personal scope. |
| Derived statistics | Private analysis supported; publication UNRESOLVED. |
| Redistribution | RESTRICTED for original/repackaged data; not proposed. |
| Commercial limitations | Separate classification/licensing required; see [official license guidance][E-license]. |

### 3.3 Tiingo permission assessment

**VERIFIED_DOC:** [Tiingo terms][T-terms], updated **October 6, 2026**, §1.6:
Starter/trial data **and derived products** cannot persist. Eligible paid-plan
data can persist while active, but must be deleted on termination/downgrade,
including backups. Qualifying non-substitutable, non-reconstructible paid-plan
derived products may survive; statistics are not an automatic exemption.
Cross-dataset validation, reconstructible series and hash construction have
specific restrictions; generic bundle hashes are not automatically licensed.
Starter/Power cannot receive the archival exception;
written exceptions require specified higher-tier accounts starting at $250/month.
§7.3 limits API redistribution; §1.4 also constrains published provider analysis.
**INFERRED:** `RESTRICTED` for the proposed standard-plan durable archive;
`UNRESOLVED` for the precise diagnostic publication. A different agreement or
explicitly accepted subscription-limited retention lifecycle would be a separate
decision, not an implicit change to PR 5B immutability.

This covers API access, data rights, retention, repeated plan-limited access,
internal computation, derived results, redistribution and commercial distinctions;
[general API documentation][T-general] separately identifies internal-use licenses
and redistribution arrangements. No free-plan data was fetched into our durable
snapshot format. We did not contact providers or send messages on the user's behalf.

## 4. Phases B–D: executed activity and pilot disposition

**OBSERVED: market-data API calls = 0** across Yahoo, Tiingo and EODHD.
No price, action, ticker-metadata, demo-key or account endpoint was queried.
Official documentation retrieval/search is distinct from those calls. Indexed
field labels were consulted as definitions; displayed price rows were neither
captured as datasets nor interpreted as this pilot's observations.

SPY-first acquisition was not authorized by Phase A, so the remaining basket was
not attempted. There were no rate-limit, timeout, empty-series or schema outcomes
from a market-data API. The table preserves cases without replacing failed or
unrun tickers with survivors. Counts are the **existing PR 5B offline calendar
expectations**, not returned observations or freshly validated provider coverage.

| Symbol | Inclusive interval | Expected XNYS sessions | PR 5C disposition | Returned range/rows |
| --- | --- | --- | --- | --- |
| SPY | 2024-11-20–2024-12-06 | 12 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |
| AAPL | 2014-05-27–2014-06-20 | 19 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |
| AAPL | 2020-08-17–2020-09-11 | 19 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |
| MSFT | 2024-02-01–2024-03-01 | 21 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |
| FB | 2022-05-23–2022-06-24 | 23 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |
| META | 2022-05-23–2022-06-24 | 23 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |
| TWTR | 2022-10-03–2022-11-04 | 25 | NOT_RUN_PERMISSION_PREREQUISITE | UNKNOWN / NOT_MEASURED |

Consequently request start/completion times, snapshot IDs/content/bundle/frame
hashes, actual coverage, canonical rows, corporate actions, quality reports and
export decisions for real data are **NOT_CREATED / NOT_MEASURED**. No synthetic
timestamp or fixture hash is substituted. No real `validate`, `export` or
`compare` command was run without a real snapshot.

Repeatability is **NOT_TESTED**: zero independent acquisitions, no frame-hash
equality result, no observed dates/OHLCV/adjustment/action revisions and no schema
comparison. Were two responses later identical, that would establish only the
observed retrieval comparison, not permanent immutability or historical PIT access.

## 5. Price semantics, actions and calendar findings

**VERIFIED_DOC:** Yahoo's indexed [field definitions][Y-fields] distinguish
split-adjusted Close from Adj Close adjusted for splits/distributions. This is
documentation evidence, not proof of specific API OHLC or volume behavior.
`auto_adjust=False` does not establish contemporaneous raw execution prices.
Actual Yahoo O/H/L split basis, dividend treatment, volume units, corrections and
complete event coverage remain **UNKNOWN**. No volume spike or price jump was
interpreted as proof of a split adjustment.

Independent event anchors were checked separately from any provider results:

- [Apple issuer history][I-apple]: first split-adjusted trading dates June 9,
  2014 (7:1), and August 31, 2020 (4:1). Record/payment dates must not replace these.
- [Microsoft issuer-authored announcement][I-msft]: $0.75 dividend, February 14,
  2024 ex-date; March 14 payment. No observed Adj Close factor is available to compare.
- [Meta issuer announcement][I-meta]: FB becomes META before June 9, 2022 open.
- [Twitter issuer filing][I-twitter]: trading suspended before October 28, 2022
  open. A full exchange-calendar count is not an expected TWTR security-bar count.

SPY's proposed interval covers Thanksgiving and an early close. PR 5B tests cover
independent expected sessions, DST and the [January 9, 2025 exceptional closure][I-nyse].
Those tests do not establish SPY completeness or security-specific suspensions.
Warmup, signal, holding dates and the subsequent adjustment horizon through
retrieval still need action evidence. No historical publication/finalization
timestamp or latency model was established or approved in PR 5C.

## 6. Phase E: alternatives, current documentation only

Prices below are published USD monthly list prices checked on the review date,
not purchases or binding quotes. Account-specific fees/taxes/entitlements require
confirmation. Documentation claims and observed coverage remain separate.

| Dimension | Tiingo | EODHD |
| --- | --- | --- |
| Personal/internal use and retention | See §3.3; archival lifecycle is a deciding limitation. | See §3.2; strongest explicit private-storage starting point, with unresolved lifecycle/publication questions. |
| Monthly cost / free access | [Pricing][T-price]: Starter $0, individual Power $30/month ($300/year); commercial internal $50/month. Starter lists 500 unique symbols/month, 50/hour, 1,000/day, 1 GB/month. | [Pricing][E-price]: Sandbox $0, 20 calls/day, one-year history; Historian EOD $19.99/month ($199/year), 100,000/day; EOD+Intraday $29.99/month. A one-year free window does not cover this 2014–2024 basket on the review date. |
| Daily history | [EOD product][T-product] advertises 80,000+ tickers and history to 1962; per-security availability UNKNOWN. | EOD pricing advertises 30+ years; actual requested security/date completeness UNKNOWN. |
| Raw / adjusted / volume | [EOD specification][T-eod] supplies raw and adjusted OHLC, `volume`/`adjVolume`, `divCash` and `splitFactor`. Separate share-unit convention still needs an independent check. | [EOD specification][E-eod] describes raw as-traded OHLC, split/dividend-adjusted `adjusted_close`, and **split-adjusted volume**. That is a mixed basis requiring explicit review before our contemporaneous-share-unit gate. |
| Splits / dividends | Documented event fields and adjusted-series methodology; feed completeness UNKNOWN. | [Action API][E-actions] documents historical per-security splits/dividends and richer dates in JSON. Completeness and difficult reorganization treatment UNKNOWN. |
| Delisted history | No specific old-security availability independently established; UNKNOWN. Do not confuse fundamental-data coverage with EOD guarantees. | [Delisted documentation][E-delisted] describes retained EOD, with pre-2018 delistings limited to EOD and broader later datasets. This is a vendor claim, not a measured TWTR result or completeness guarantee. |
| Ticker changes | Current metadata/supported-symbol files are not PIT identity histories; UNKNOWN for the basket aliases. | [Rename API][E-rename] documents US history starting **2022-07-22**, on Extended/All-in-One plans. It cannot itself establish the earlier June 9 FB/META event. External identity evidence remains necessary. |
| API / Python / reliability | Documented authenticated REST JSON/CSV and Python examples. Operational reliability/SLA and integration behavior untested here. | Documented REST JSON/CSV, official Python tools and error handling. Operational reliability/SLA and integration behavior untested here. |
| Historical PIT | Current corrected history is not an as-known-at-the-time archive. Tiingo describes evening corrections, not historical vintage access. | Adjusted history can be recomputed after events; no original-publication/vintage guarantee established. |
| Integration effort (INFERRED) | Moderate: narrow HTTP boundary, per-field units/action mapping, calendar/identity checks and evidence/provenance; licensed storage lifecycle is additional work. | Moderate: narrow HTTP boundary, exchange-suffixed identity, event requests and mixed-volume-basis assessment. Existing snapshot/gate concepts are reusable; Yahoo-specific parsing is not a generic EODHD adapter. |

**INFERRED:** no advertised API uptime or history depth substitutes for a small
empirical pilot. EODHD's broad [site disclaimer][E-license] also raises a
dataset-specific source/provenance question: clarify the US equity EOD feed
versus indicative/CFD pricing language before claiming execution-price fidelity.
Do not infer that every equity bar is a CFD or that the raw-field description
independently proves exchange tape values.

## 7. Phase F: three fitness-for-purpose decisions

These assess documented technical prospects **conditional on lawful access**.
They do not override §3 or claim empirical acceptance. No unconditional SUITABLE
rating is justified. Execution means the existing raw/no-action dollar simulator,
not merely computing percentage returns from an adjusted chart.

| Provider | Level 1: technical signal research | Level 2: current execution simulation | Level 3: historical stock selection |
| --- | --- | --- | --- |
| Yahoo | UNKNOWN: consistent per-field basis and actual coverage not observed; adjusted data may be useful after verification under a separately reviewed signal-study contract. | NOT_SUITABLE for admission now: no verified raw/no-action input or historical availability; existing export evidence gates cannot be satisfied by the request flag. | UNKNOWN: prices/current tickers do not establish dated selection membership, delisted completeness or reuse-safe identities. |
| Tiingo | SUITABLE_WITH_LIMITATIONS, documentation-only prospective assessment: coherent adjusted OHLC fields could support indicators after permitted validation. | UNKNOWN: raw fields documented, but per-security actions, share units, finalization evidence and admissible archive remain untested. | UNKNOWN: neither current supported symbols nor a product breadth claim proves historical membership/completeness. |
| EODHD | SUITABLE_WITH_LIMITATIONS, documentation-only prospective assessment: explicit adjustment fields could support exploratory signals after independent checks. | UNKNOWN: empirical price/volume identity and historical availability unresolved; no existing-compatible export demonstrated. | UNKNOWN: delisted/rename endpoints are useful ingredients, not a verified PIT universe or original screening archive. |

No inference about historical DeepVue/Mantis lists, predictive edge, portfolio
performance or historically executable fills follows from these ratings.

## 8. Replay-export disposition

No actual real-data export gate evaluation exists in this PR. The operational
decision is **DO_NOT_EXPORT_REAL_DATA**, not a fabricated `quality.json` outcome.
On code inspection, a successful future acquisition without affirmative evidence
would still have unresolved identity/venue alignment, raw price/volume basis,
complete actions and historical availability. Calendar/numeric PASS would not
waive those gates. PR 5B's distinct `BLOCKED_*` reasons remain unchanged.

The offline suite exercises both synthetic EXPORT_READY and blocked cases,
immutable-directory rejection, corruption detection and byte-identical downstream
reporting after a new synthetic vintage. These are **engineering observations**,
not measurements of Yahoo, Tiingo or EODHD prices. No frozen real inputs were
created, edited, overwritten or deleted; previously generated local artifacts
were not used as evidence or refreshed.

## 9. Commands and validation record

Executed from the target checkout, without market-data acquisition:

```bash
git status --short --branch
git rev-parse HEAD
git log -3 --oneline
git ls-remote origin refs/heads/main refs/heads/research/real-data-provider-validation-v1
PYTHONPATH=src .venv/bin/python -m equity_research.cli data --help
.venv/bin/python -m pytest -q
git diff --check
```

An `importlib.metadata.version` inspection confirmed installed yfinance 0.2.66,
exchange-calendars 4.13.1, pandas 2.2.3, numpy 2.2.4, tzdata 2025.2 and pytest 9.0.2;
no package or dependency was installed/changed for PR 5C. Source reads and an
offline local-link/changed-path validation script supplement these commands.
There are **no executed `fetch-yahoo`, real `validate`, real `export` or real
`compare` commands to report**. The full suite passed **112 tests in 9.80s**,
including the original PR 4 cases. Whitespace/local-link/reference checks passed.
Tests remain network-free, cover overwrite rejection and frozen-input stability,
and are not empirical data evidence.

Only this report and an append-only dated pointer in the PR 5B report are intended
changes. No licensed raw data, snapshots or provider-derived price tables are in
the commit. No observed integration defect exists to justify a code/test fix.

## 10. Residual risks and recommended next PR

Recommend a reviewed **PR 5D: EODHD licensed one-security quality pilot**, with
implementation contingent on these unanswered questions:

1. Confirm eligibility for the proposed personal plan, immutable local retention
   during/after cancellation, backups and any required deletion obligations.
2. Confirm whether safe hashes, missing-session/error counts and aggregate
   diagnostic findings may appear in the intended private repository or be
   published, and whether collaborator access changes the license classification.
3. Confirm actual US EOD feed provenance, documented raw OHLC and volume units,
   event/adjustment horizon, action revisions and limitations of supplied history.
4. Establish an entitled bounded SPY request before the remainder of the same
   basket. Preserve every failure and snapshot; do not choose only successful names.
5. Compare AAPL/MSFT event cases to independent evidence, explicitly handle the
   rename-history start-date gap, and test delisted coverage rather than assuming it.
6. Separately decide historical availability evidence or a reviewed, labeled
   modeling assumption. Do not weaken raw/volume/action/export gates to complete
   the pilot. Signal-only adjusted research would require its own explicit contract.

This is a proposed review sequence, not permission to purchase, register, contact
providers or start another adapter/milestone now. A different licensed source may
be needed if those questions cannot be resolved. Core replay remains offline;
no broker, orders, trades, strategy backtest, optimization or deployment occurred.

## Primary-source register

All sources below were checked on **2026-10-21**. A source's factual assertions
are publisher claims unless independently tested. No full terms or market-data
payload was copied into Git. Yahoo's direct-access failures and reliance on
indexed official text are explicit; there is no assertion that every link
returned HTTP 200 or that these pages settle all jurisdiction/account terms.

| Ref | Exact primary source / section used | Access and uncertainty |
| --- | --- | --- |
| Y-terms | [Yahoo US-path general terms, §2(b)(9)][Y-terms] | Official indexed text available; direct canonical/indexed-variant opens returned 999; indexed crawl last month. Current supplemental applicability unresolved. |
| Y-client | [Pinned client README, Legal Stuff][Y-client] | Direct primary repository text; software notice is not data permission. |
| Y-fields | [Yahoo historical field labels][Y-fields] | Indexed official definitions; price rows not used as pilot data. |
| T-terms | [Tiingo terms, §§1.4, 1.6, 7.3][T-terms] | Directly read; effective 2022-01-16, updated 2026-10-06. |
| T-general | [Tiingo API overview, licensing][T-general] | Directly read; confirms API/internal-use boundary. |
| T-price | [Tiingo current pricing][T-price] | Directly read; list prices/limits, not a purchased entitlement. |
| T-product | [Tiingo EOD product][T-product] | Direct/indexed documentation; advertised breadth, not observed coverage. |
| T-eod | [Tiingo EOD specification][T-eod] | Directly read; fields, corrections and current metadata. |
| E-terms | [EODHD terms, Personal Use / Access / Termination][E-terms] | Directly read; no clear post-termination retention duration or diagnostic-publication grant established. |
| E-license | [EODHD commercial/personal guidance][E-license] | Directly read; classification guidance and broad disclaimer need dataset-specific interpretation. |
| E-price | [EODHD current pricing][E-price] | Directly read; distinguishes free from historical paid entitlements. |
| E-eod | [EODHD EOD fields / adjustments][E-eod] | Directly read; vendor's raw/adjusted/volume definitions, not independently verified prices. |
| E-actions | [EODHD action specification][E-actions] | Directly read; not queried, including demo endpoints. |
| E-delisted | [EODHD delisted coverage][E-delisted] | Directly read; no sample downloaded or completeness independently proven. |
| E-rename | [EODHD symbol-change history][E-rename] | Directly read; start-date/plan limitations recorded. |
| Issuers/exchange | [Apple][I-apple], [Microsoft][I-msft], [Meta][I-meta], [Twitter SEC filing][I-twitter], [NYSE closure memo][I-nyse] | Independent event anchors only; no provider-price validation. |

[Y-terms]: https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html?bt_ts=1741912561771
[Y-client]: https://github.com/ranaroussi/yfinance/blob/0.2.66/README.md
[Y-fields]: https://finance.yahoo.com/quote/%5EGSPC/history/?frequency=1d
[T-terms]: https://app.tiingo.com/tos/
[T-general]: https://www.tiingo.com/documentation/
[T-price]: https://www.tiingo.com/about/pricing
[T-product]: https://www.tiingo.com/products/end-of-day-stock-price-data
[T-eod]: https://www.tiingo.com/documentation/end-of-day
[E-terms]: https://eodhd.com/financial-apis/terms-conditions
[E-license]: https://eodhd.com/financial-apis/commercial-vs-personal-license-use
[E-price]: https://eodhd.com/pricing
[E-eod]: https://eodhd.com/financial-apis/api-for-historical-data-and-volumes
[E-actions]: https://eodhd.com/financial-apis/api-splits-dividends
[E-delisted]: https://eodhd.com/financial-apis/delisted-stock-companies-data-2
[E-rename]: https://eodhd.com/financial-apis/us-stock-symbol-rename-history-api
[I-apple]: https://investor.apple.com/dividend-history/default.aspx
[I-msft]: https://www.prnewswire.com/news-releases/microsoft-announces-quarterly-dividend-301999937.html
[I-meta]: https://investor.atmeta.com/investor-news/press-release-details/2022/Meta-Platforms-Inc.-to-Change-Ticker-Symbol-to-META-on-June-9/default.aspx
[I-twitter]: https://www.sec.gov/Archives/edgar/data/1418091/000119312522272772/d411753d8k.htm
[I-nyse]: https://www.nyse.com/publicdocs/nyse/markets/american-options/rule-interpretations/2025/National_Day_of_Mourning_20250102.pdf
