# PR8B — Historical equity research using existing sources

The real pilot imports **13,625 daily observations for 31 stock contracts** into
PR8A's unchanged security master and price panel. It demonstrates two dated
observed-data cohorts and both existing universe-admission policies. It does
**not** reconstruct a complete historical equity population. Strict admitted
membership is zero because the required identity, availability and native-unit
evidence is incomplete. No prices, dates or identity fields were invented to
make the universe pass.

Authoritative scope: the revised PR8B existing-source task. Branch:
`research/existing-source-historical-universe-v1`. Inspected base:
`fda110095638d7990864c080d70d1b22efb8e758`, merged PR8A including its semantic-load
fix and the PR16/PR17 research. Only IBKR, Yahoo/yfinance and Databento were in
scope. No subscription, new provider evaluation, broker connection or market-data
request was performed. This is an offline experiment, not a trading strategy or
platform expansion.

## Existing-source inventory

The audited scope is this repository's `data/` and `runs/`. Credentials, external
machines and account entitlements were not inspected. Installing a client library
does not establish retained data or permission. The machine-readable local
inventory verifies existing standard datasets through the original history loader.

| Source | Actual retained evidence inspected | Research use and limitation |
|---|---|---|
| IBKR | Five selected immutable native-checkpoint audit reports: **50 distinct conIds, 31 stocks and 19 ETFs**, **135,482 observed sessions** across their different spans. Five older real research datasets and two separately labeled synthetic datasets also remain in `data/research_datasets`; overlapping captures are not added as independent coverage. | Native frames, request parameters, checkpoint chains and contract qualifications are replayed independently. These are selected contracts, not an all-market archive. |
| Yahoo / yfinance | **Zero identified real Yahoo research datasets and zero retained standalone Yahoo requests** in the audited local formats. Prior code and synthetic examples do not become real evidence. | No Yahoo bars enter this pilot. No acquisition, permissions workaround or source substitution was attempted. |
| Databento | **Zero DBN files and no identified Databento equity dataset** in the audited directories. Access and holdings outside this checkout are unknown. | No existing equity coverage or entitlement was established, so no use, download or new cost was justified. |

The frozen input configuration is
[experiments/pr8b-existing-sources-v1.json](../experiments/pr8b-existing-sources-v1.json).
It pins the exact five existing source bundle hashes and disjoint selected symbol
sets. Original proofs retain native frames, retrieval timestamps, request failures
and sanitised diagnostics. The original report summaries are not trusted in place
of native-bar recomputation. Local paths are explicit run inputs; normalized output
hashes do not depend on output-directory names.

The [generated coverage report](reports/PR8B_EXISTING_SOURCE_COVERAGE.md) gives all
50 contract identities, first/last observed sessions, counts, internal gaps and
fixed cycle-window coverage. The committed verification evidence preserves the
machine-readable report, coverage inventory, local-source census and bundle hashes.

## The bounded real-data pilot

The materialized stock panel spans **January 2, 2025 through October 26, 2026**.
It contains the 26 source-study stocks plus MSFT, GOOG, NVDA, AMZN and META, joined
by qualified conId rather than a symbol-only join. The prior deep audit and later
Grimes acquisition baskets determine this sample retrospectively. Its membership
must not be described as a stock list screened or knowable on the historical dates.
The 19 ETFs remain contextual coverage, outside the stock selection panel.

| Observation date | Capture catalogue | Observed by date | Complete prior 60-session native windows | Strict admitted | Explicit reconstruction admitted |
|---|---:|---:|---:|---:|---:|
| 2026-08-31 | 31 | 30 | 30 | 0 | 0 |
| 2026-09-30 | 31 | 31 | 30 | 0 | 0 |

The new TEVA ordinary-share contract has no observed bars before September 14,
2026, then 31 through the fixed end; it does not have a 60-session window at either
observation. This is not filled with the former ADS's history. SAIL and SNDK each
begin their captured current-contract history on February 13, 2025; neither is
spliced to an older security that used the same ticker. Their observed starts do
not independently prove regular-way listing dates. SNDK's existing when-issued
identity cautions remain relevant.

All other pilot stocks have complete 60-session bar presence on both dates. The
whole 31-stock, 455-session rectangular panel would have 14,105 cells; **480 are
unobserved before individual captured spans**, leaving 13,625 actual observations.
There are **zero internal missing sessions within these individual pilot spans**.
Unobserved leading cells are not classified as missing trades, inferred IPO dates
or provider errors. Across the wider 50-instrument inventory there are **20 internal
missing session observations in 10 instruments**, including three older AAPL dates
and repeated ETF gaps. They remain in the coverage inventory and are never filled.
Holiday exclusions use the frozen XNYS calendar, not weekday counting.

### Identity and time interpretation

Stable keys are scoped as `ibkr:conid:N`. Original qualification metadata and frame
locators are retained, but a current conId qualification is not independent proof
of historical issuer continuity, share class, ticker, exchange or trading status.
Those unresolved master fields remain null and historical identity confidence is
WEAK. The current capture alias is a separate display field. In particular, META
is not asserted to have been the ticker used throughout its 2012-onward history,
and GOOG Class C's observed start is **2014-03-27**, not an inferred 2004 history.
ASST's existing business-change/reverse-split cautions remain unresolved.

The master's effective start bounds the observed panel, **not** the listing date;
`listing_start` stays null. Historical knowledge/availability timestamps stay
null. Native IBKR split-adjusted prices map to PR8A's `SPLIT_ADJUSTED` storage tag;
native unverified volume maps to `VENDOR_UNVERIFIED`. Exact native basis labels
and source locators survive alongside them. Nothing is relabeled raw shares or
raw traded prices. An empty imported action inventory means actions were not
supplied, not that no actions occurred. Existing AAPL/GOOG event sidecars remain
separate, incomplete evidence rather than a 31-stock action archive.

### Why admission is zero

The unchanged default definition requires historically known eligible identities,
raw prices/share units, 60 eligible completed sessions and minimum Close USD5.
With `unknown_knowledge_policy=EXCLUDE`, all 31 identities are unavailable at the
historical decision clock. Running the existing explicit reconstruction policy
still excludes incomplete listing/classification/status evidence and unadmitted
native price/volume units. TEVA also lacks history. Both universes are
`PIT_UNVERIFIED`. Their semantic loaders validate the frozen outputs against the
master, panel and definition.

The separate observed snapshots use `SecurityMaster.as_of` and
`ResearchPanel.rows_as_of` with explicit reconstruction to count bar presence,
without liquidity ranking or eligibility promotion. PR8A's Close +60-minute query
assumption is disclosed; it is not written back as an actual source timestamp.
Observations after the month-end date do not enter either 60-session window.

## What we can reliably study now

| Fixed window | Stocks with any / full-window bars | ETFs with any / full-window bars | Practical interpretation |
|---|---:|---:|---|
| January–June 2008 | 4 / 4 | 10 / 10 | Selected surviving-name and proxy price histories; this window does not cover the entire 2008 crisis. |
| January–June 2015 | 6 / 6 | 11 / 11 | Six-stock and proxy context; no contemporaneous all-stock cross section. |
| January–June 2020 | 6 / 6 | 11 / 11 | Descriptive crash/rebound paths for the selected contracts and proxies. |
| January–June 2022 | 9 / 9 | 16 / 16 | Wider context plus three additional selected stocks; still a retrospective cohort. |
| 2026 through October 26 | 31 / 30 | 19 / 19 | Useful source-study chart/context coverage; TEVA has only its recent ordinary-share capture. |

These are coverage measurements, not strategy results. Existing native prices can
support descriptive chart paths, within-name price changes and market/sector
context for explicitly chosen contracts, with declared split-adjustment and
publication assumptions. Missing sessions must break any path requiring them.
These data cannot establish historically available screening opportunities,
cross-sectional strategy performance, verified liquidity ranks, raw execution
prices, terminal recoveries or total returns. There is no verified delisted-stock
history imported, and the missing-security count is **UNKNOWN**, not zero: a
complete historical denominator is unavailable. The chosen stocks overrepresent
survivors and later expert mentions. No bias magnitude can be honestly estimated
from this catalogue alone.

The practical next step within the existing-source workflow is to reuse the
well-covered dated chart/context intervals for explicitly documented trade studies,
preserving missing history, ticker/contract breaks and corporate-action caveats.
Any later broadening should use separately authorized captures and dated identity
evidence; additional selected tickers alone would enlarge the observed catalogue,
not repair historical population coverage. This task incurs **no new subscription
or provider-request cost**, and introduces no new provider, engine or dependency.

## Reproduction and readable trade status

All actual payloads stay in ignored local storage. Use unused output directories:

```sh
PYTHONPATH=src .venv/bin/python scripts/pilot_existing_source_universe.py --help
PYTHONPATH=src .venv/bin/python scripts/pilot_existing_source_universe.py capture-inputs --config experiments/pr8b-existing-sources-v1.json --output NEW_INPUTS
PYTHONPATH=src .venv/bin/python scripts/pilot_existing_source_universe.py study --inputs NEW_INPUTS --output NEW_PILOT
PYTHONPATH=src .venv/bin/python scripts/pilot_existing_source_universe.py study --inputs NEW_INPUTS --output NEW_REPLAY
.venv/bin/python -m pytest -q
```

The script blocks network sockets and reuses the existing PR14 native-proof and
PR8A import/freeze/build/load APIs. Repeating the study from the same frozen inputs
reproduces the master, panel, both universes and report hashes. Implementation
bytes, Python/dependency versions and the pinned shared wheel are recorded.
Reproducing the actual-data pilot requires the existing local captures; automated
tests instead use small explicitly synthetic broker-response fixtures.

[reports/grimes_trade_status.csv](../reports/grimes_trade_status.csv) is the separate,
versioned, source-only 26-episode table. Its [README](../reports/README.md) explains
reported versus modeled histories and deterministic generation. CDE remains
SHORT / OPEN / UNDERWAY at 13.90; EBAY remains LONG / OPEN / ENTERABLE at 117.50.
Their modeled histories never replace those facts. The weekly publication date
remains UNKNOWN; closed source episodes remain visible.

Frozen PR8A, PR16 and PR17 inputs/outputs, execution/accounting policy and shared
mathematics are unchanged. Preservation inventories, actual-data byte-identical
replays and exact full-suite results are recorded in the PR's committed evidence.
No GitHub Actions, live/paper orders, optimization, deployment or automatic merge.

## Validation record

`.venv/bin/python -m pytest -q`: **634 passed in 113.34s (0:01:53)**, exit 0,
with no skips or failures: the 620 merged-main regressions and 14 new status/pilot
cases. [Exact output](evidence/pr8b-existing-sources-v1/pytest.txt) is committed.
The tests cover retained source states/stops, weekly date uncertainty, CSV
reproducibility, missing expected sessions, unknown identities/native units,
synthetic/real separation, native-proof tampering, non-splicing and immutable replay.

The final real pilot is `runs/pr8b-existing-sources-20261027-v1/pilot-v3`;
`offline-replay-v3` has identical master, panel, both universe and report hashes.
Report bundle SHA256:
`4f4bb5661bc4123997198fb8121629f75d607a56d62f4792b7a878ba97882998`.
The captured input bundle is
`64f26510e7e9e1fae5c8982fbf2c1ba3d093015996f5321ccf6a97931a39b08f`.
Earlier development outputs `pilot-v1` and `pilot-v2` were preserved separately.

All **67,261 pre-existing files** under `data/` and `runs/` retain their original
SHA256 values. The original inventory is retained in the new local run directory,
hash `d753f6eec0ea1b8911493191bc10b60bd1d7dd57a0d938a83bc08ed4f9f52b10`.
Actual PR16 and PR17 CLI semantic replays reproduce their original bundle hashes
`4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604` and
`fb2fd81dc3eeef6b10a185057930776a1534230a3534d63793d72d3e257342ca`.
Those modules, the PR8A implementation, execution/accounting, shared wheel and
dependency declarations are byte-identical to main. All replay/pilot commands
explicitly denied network sockets.

See the [sealed verification evidence](evidence/pr8b-existing-sources-v1/hashes.json),
[preservation/replay inventory](evidence/pr8b-existing-sources-v1/preservation_and_replay.json)
and [CSV checks](evidence/pr8b-existing-sources-v1/grimes_status_verification.json).
The generated CSV SHA256 is
`a32c812f95a51a56dc90fd8f49634b4976cd7f175fb1b326faf773ff22e4c527`.
Git attributes preserve its exact CRLF bytes and treat those row endings correctly
in whitespace checks. `git diff --check` passes. All raw price/source payloads
remain local; the public evidence contains derived coverage and source-status facts.
