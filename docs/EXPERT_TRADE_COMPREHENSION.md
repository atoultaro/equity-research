# Expert trade comprehension — Grimes, October 26, 2026

This descriptive pilot preserves four operator-reported **OPEN_NEW_POSITION**
observations and produces four reproducible dossiers. The original text, stops
and LONG/SHORT directions are in
[`experiments/grimes-20261026-observations-v1.json`](../experiments/grimes-20261026-observations-v1.json).
“Added” means a newly opened position under the operator's explicit interpretation.
Publication time, execution time, entry, quantity and profit targets remain null.

The analysis cutoff is **2026-10-26 17:00 America/New_York / 21:00 UTC**.
Completed daily bars are reconstructed as available at cash close plus 60 minutes,
following the existing MarketContext convention. This is a research assumption,
not the actual recommendation or fill timestamp. October 27 prices never enter
these features. Later retrievals can contain revisions; this is a captured-vintage
reconstruction, not proof of the historical dissemination vintage.

Read the [complete real-data report](reports/GRIMES_20261026.md) for all four
dossiers, supporting and opposing observations, sector evolution and stop levels.
The machine-readable outputs remain in local immutable research storage.

## Inspected revisions and scope

- `equity-research` main / merged PR #14:
  `0b4be335e53e646e4de0216d307607810434280d`.
- PR #14 inspected head: `c85a8c731915f7fc102feda28f6928df23a428cd`.
- Read-only local `finwhaling` and `ibkr-data` interfaces:
  `57fc6c30836d13a7fcfc3c1a9b6b496fe472d555` in the shared finance checkout.
- Branch: `research/grimes-trade-comprehension-20261026-v1`, based on main because
  PR #14 had merged. The task brief's four-stock comprehension mission supersedes
  the older one-symbol strategy-development scope in AGENTS.md for this task.

The existing PR #14 depth-audit command did all acquisition. No new broker adapter,
execution policy, accounting rule or simulator change was introduced. The existing
MarketContext measure function supplies the overlapping calculations, including
ATR through the pinned market_shared wheel. A separate offline comprehension layer
adds the requested daily diagnostics, operator observations, proxy mappings and reports.

## Actual acquisition and coverage

The operator explicitly authorized historical access to the already running
non-paper TWS at `127.0.0.1:7496` with Read-Only API enabled. Client ID `46151`
performed **27 bounded, serial requests**: nine qualifications, nine head timestamps
and nine completed-daily `TRADES`, RTH windows. Account synchronization was disabled.
The capture ran **2026-10-27 01:33:02.623367–01:33:57.811680 UTC**, on the evening
of October 26 in New York, and disconnected. No order, position, balance, execution
or account-setting request was made. The complete bounded windows satisfied their
calendar boundaries, so no further backward request was needed.

| New capture | IBKR conId | Primary exchange | First session | Last session | Sessions |
| --- | ---: | --- | --- | --- | ---: |
| SAIL | 760966616 | NASDAQ | 2025-02-13 | 2026-10-26 | 427 |
| SLB | 12200 | NYSE | 2022-01-03 | 2026-10-26 | 1,208 |
| GE | 498843743 | NYSE | 2022-01-03 | 2026-10-26 | 1,208 |
| SCCO | 1812968 | NYSE | 2022-01-03 | 2026-10-26 | 1,208 |
| CIBR | 199295926 | NASDAQ | 2022-01-03 | 2026-10-26 | 1,208 |
| OIH | 415578515 | ARCA | 2022-01-03 | 2026-10-26 | 1,208 |
| ITA | 39046959 | BATS | 2022-01-03 | 2026-10-26 | 1,208 |
| XLB | 4215200 | ARCA | 2022-01-03 | 2026-10-26 | 1,208 |
| COPX | 211651700 | ARCA | 2022-01-03 | 2026-10-26 | 1,208 |

There were no unexpected missing sessions or failed native-row checks in these
windows. SAIL's [current Nasdaq listing began February 13, 2025](https://www.sec.gov/Archives/edgar/data/2030781/000203078125000011/spparent-20250131x10k.htm).
Its 781 pre-listing reference-calendar sessions are explicitly excluded; the
three-year target is unmet. No history from the previous SAIL listing was spliced.

Existing PR #14 SPY, QQQ, RSP, IWM, XLK, XLE and XLI captures supplied the other
seven identities. Each selected 2022-01-03–2026-10-26 slice has 1,208 sessions.
The combined input has **16 identities and 18,547 daily observations**. Old gaps
and quality findings outside these selected slices remain in the hash-bound
original audit summary claims; they are not silently repaired or reclassified.
Selected-window native frames are independently reconverted and validated.

Data basis is `IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED`, not dividend-adjusted or
verified contemporaneous raw execution prices. Volume is
`IBKR_NATIVE_UNITS_UNVERIFIED`. Relative dollar-volume measurements are native-unit
proxies, not verified tradable liquidity. Original request, capture, native-frame
and row locators remain attached. Reported-stop adjustment basis is unknown,
so stop/ATR calculations are descriptive native-price comparisons.

## Findings and competing interpretations

| Symbol | Reported direction | Reference close | Stop | Absolute distance | Close distance | ATR units | Narrow geometric hypothesis |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| SAIL | LONG | 21.75 | 20.90 | 0.85 | 3.908% | 0.783 | Failed-breakout geometry opposes the reported direction |
| SLB | LONG | 53.08 | 51.10 | 1.98 | 3.730% | 1.251 | Bullish pullback heuristic |
| GE | SHORT | 288.43 | 295.80 | 7.37 | 2.555% | 0.843 | Other / uncertain |
| SCCO | SHORT | 186.01 | 191.70 | 5.69 | 3.059% | 0.715 | Other / uncertain |

All stops are on the conventional side of the reference close. None of these
distances is actual entry risk, realized R or evidence of a fill.

SAIL rose 5.74% over 20 sessions and 29.70% over 60, with strong relative performance
against SPY and QQQ. Its current High nevertheless exceeded the preceding 20-session
High and then closed back below that boundary. The framework preserves this bearish
geometric contradiction rather than relabeling it as a bullish setup. SLB's positive
momentum and energy-sector alignment coexist with weaker performance than XLE.
GE has negative 20/60-session momentum and trades below SMA20/50/200, but did not
make a fresh 20-session closing breakdown. SCCO has negative 20-session momentum
and underperforms SPY and broad materials while outperforming the even weaker copper
proxy over that interval. Both SHORTs remain uncertain under the deliberately narrow
taxonomy. Their evidence does not require inventing a precise trigger or expert motive.

Market context is mixed: SPY's 20-session price return is approximately −0.03%,
QQQ −3.30%, RSP +3.60%, IWM −1.08%. SPY and QQQ remain above SMA200 while IWM is
slightly below it. Snapshot tables and explicit deltas at 5/20/60/120 sessions
show the trajectory without assigning an entire year a regime label. RSP/SPY
is an equal-weight/cap-weight participation proxy, not constituent breadth.

## Classification and event evidence

The dated business descriptions and primary URLs are captured in
[`experiments/grimes-20261026-research-v1.json`](../experiments/grimes-20261026-research-v1.json).
Mappings bind both stock and proxy to qualified conIds. They are **analyst broad-sector
and business-industry mappings**, not licensed GICS or reconstructed ETF membership:

- SAIL: identity-security software, XLK/CIBR, based on its
  [March 19, 2026 annual filing](https://www.sec.gov/Archives/edgar/data/2030781/000203078126000003/sail-20260131.htm).
- SLB: energy / oilfield services, XLE/OIH, supported by its
  [October 23 results](https://investorcenter.slb.com/news-releases/news-release-details/slb-announces-third-quarter-2026-results)
  and the SEC's oil-and-gas-field-services issuer identification.
- GE: industrials / aerospace propulsion, XLI/ITA, supported by its
  [October 20 issuer description](https://www.geaerospace.com/news/press-releases/ge-aerospace-announces-third-quarter-2026-results).
  The [April 2, 2024 separation](https://www.geaerospace.com/news/press-releases/ge-aerospace-launches-independent-investment-grade-public-company-following-0)
  means the entire captured history is not a constant-business aerospace series.
- SCCO: materials / copper mining, XLB/COPX, based on its
  [2025 annual filing, filed February 27, 2026](https://www.sec.gov/Archives/edgar/data/1001838/000110465926021492/scco-20251231x10k.htm).

Proxy limitations include business mix, concentration, geography, currency exposure
and different dividends. No actual historical constituent membership is assumed.
Missing, multiple or mismatched identity/classification records cause explicit
uncertainty; missing proxies make relative features unavailable.

Company earnings records cover SAIL September 9, SLB October 23, GE October 20 and
SCCO October 20, with separate GE business-separation evidence. The
[SCCO filing](https://www.sec.gov/Archives/edgar/data/1001838/000110465926117588/scco-20261020x8k.htm)
also documents a dividend declaration; its ex-date remains unknown. Neither record
nor payment dates establish an ex-date.

Every real captured event is currently `UNKNOWN_OR_MISSING` for strict historical
publication availability. Dated issuer documents and SEC acceptance times are retained,
but neither is invented into an exact dissemination timestamp. The implementation
also supports `VERIFIED_PRE_DECISION` and `RETROSPECTIVE_ONLY` when verified SECOND
or MINUTE publication evidence is supplied; minute precision uses the conservative
end-of-minute bound, strictly before cutoff. Research capture time never establishes
historical knowledge. Macro and industry news coverage remain explicitly incomplete.

## Immutable artifacts and validation

Local root: `runs/grimes-comprehension-20261026-v1/`.

| Bundle | Canonical SHA256 |
| --- | --- |
| Reused PR #14 report | `b2b8f5a15856a9ed4521b2c07f270e269501835b35ca3383305260c568b26043` |
| New nine-instrument audit-report-v1 | `00f001c3a9cd76dc10c1f4c282ea6177399900f6e556df9f8b386061c8d3e02b` |
| inputs-v1 | `01968c15438d78b47217d1402e95cb4b097eea297c0b5aef2921e8903e0e8a49` |
| Accepted study-final-v2 / study-replayed-v2 | `762e71789143e4f19ec6f3f9e2e8b7155131febefe1cca86eb7f4eb2addf7e85` |

The 17 study members include all ten requested JSON/Markdown artifacts,
four `dossier-SYMBOL.md` reports, embedded input bytes and input hashes; `hashes.json`
seals the bundle. Inputs retain the original report's file hash registry, plan,
calendar, complete checkpoint event/hash chain, original global coverage claims,
and native bytes for all selected intersecting windows. Unneeded old native frames
and aggregate daily_bars are not duplicated. Original hashes bind the subset to its
parent; hashes establish integrity, not provider authenticity.

Loading reconverts selected native frames, validates identity/basis/calendar,
deduplicates only identical cross-window observations, rejects conflicting observations,
then recomputes every derived feature, stop comparison, quality record and Markdown
file. Resealing altered outputs does not make them semantically valid. Full source
and shared-math hashes plus Python version are pinned in the study manifest. This
is one selected-input recomputation at bundle load, not a full-universe query.
Loading and replay need the existing optional data dependencies but no brokerage
library, connection, original cache or original audit directory.

The final real bundle was replayed with socket connections and imports of ib_async,
ib_insync and yfinance denied; **every file and the bundle hash matched**. Existing
fixture, data and PR #14 artifact bytes were inventoried before work and verified
afterward. All old outputs and development previews were left intact. The superseded
study-final-v1 hash is `8599f0ca45d4de5b31e8813c6bf30dbda2037eee3f3068ba711a4dcfebce40b5`;
v2 makes opposing setup geometry explicit in the hypothesis text. Price inputs did
not change.

Tests cover new-position source semantics, hand-checked LONG/SHORT stops, independent
trend arithmetic, missing sessions and warmup, cutoff/future poisoning, historical
snapshot causality, incompatible bases, ambiguous classification, source integrity,
resealed semantic corruption, unavailable ES/proxies, publication clocks and
deterministic offline reproduction. The complete suite is run with:

```bash
.venv/bin/python -m pytest -q
```

Final result: **458 passed in 197.30s (0:03:17)**, no skips. The exact output is
saved in local `offline-regression-final.txt` and recorded in the draft PR.
No canonical lint command is configured; `git diff --check` also passed.

## Reproduction

Install the repository's pinned shared wheel and optional `data,history,test` extras
as described in README. All following expert commands are offline and require new
output names. No command overwrites a sealed input or run directory.

Reproduce the actual accepted study directly from its self-contained local bundle:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli expert replay \
  --study runs/grimes-comprehension-20261026-v1/study-final-v2 \
  --output /tmp/grimes-replayed-v3
```

Or rebuild from the sealed input subset:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli expert study \
  --inputs runs/grimes-comprehension-20261026-v1/inputs-v1 \
  --output /tmp/grimes-refrozen-v3
```

For a clean, fully synthetic example without any local licensed captures:

```bash
PYTHONPATH=src .venv/bin/python scripts/make_comprehension_example.py \
  --output /tmp/grimes-synthetic-demo-v1
```

This synthetic example exercises the same native-capture, input-proof and report
paths. Its absent classification/news/futures fields remain unavailable. Its prices
are arithmetic fixtures, not evidence about the four actual stocks.

To rebuild input proofs from the original local audit reports, create an explicit
source-selection file (paths below are repository-relative):

```json
[
  {"path":"runs/ibkr-depth-20261026-v1/report-final-v1","symbols":["SPY","QQQ","RSP","IWM","XLK","XLE","XLI"]},
  {"path":"runs/grimes-comprehension-20261026-v1/audit-report-v1","symbols":["SAIL","SLB","GE","SCCO","CIBR","OIH","ITA","XLB","COPX"]}
]
```

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli expert freeze-inputs \
  --research experiments/grimes-20261026-research-v1.json \
  --audits /tmp/grimes-audits.json --output /tmp/grimes-inputs-v3
```

Future actual refreshes are separate, explicit operator actions through the existing
PR #14 CLI, with current TWS read-only prerequisites confirmed. Inspect its interface
first. The committed acquisition config is the exact original bounded request:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-audit --help
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-audit \
  --config experiments/grimes-20261026-audit-v1.json \
  --output runs/grimes-new-capture-v1 --connect --read-only-api-confirmed \
  --permission-reference 'Operator authorized historical research; read-only TWS confirmed' \
  --ibkr-host 127.0.0.1 --ibkr-port 7496 --ibkr-client-id 46152
PYTHONPATH=src .venv/bin/python -m equity_research.cli data ibkr-depth-report \
  --audit runs/grimes-new-capture-v1 --output runs/grimes-new-audit-report-v1
```

New captures are new vintages and need not reproduce the old hash. Qualify the
declared issuer/exchange mappings and verify returned conIds against the identities
above before selecting them. Do not substitute a changed contract or overwrite old
captures. For resumption, use the exact original configuration and existing PR #14
`--resume` convention.

## Optional local ES path

Read-only inspection found Databento GLBX.MDP3 `ohlcv-1m` raw metadata for parent
`ES.FUT` with instrument-ID output, plus aggregated daily files ending May 4, 2026
and contract-specific March 2026 ES files. These are not a verified October 26
continuous series. The existing conversion filters prefixes then sorts/deduplicates
timestamps and drops contract identities in its output; that does not establish a
roll or price-adjustment policy. Metadata and inspected aggregate hashes are in the
research input. No data was downloaded, modified or reprocessed in those repositories.
ES-specific findings are therefore **NOT_AVAILABLE**.

The optional `expert import-es` command accepts local **identified five-minute** CSV
only. It aggregates complete NY cash-session windows separately, preserving contract
identity and rejecting an intraday contract splice. It does not calculate continuous
returns or feed the equity panel. Raw parent-contract one-minute files and existing
identity-free CSVs intentionally fail this contract. An independently verified
conversion/export must first supply:

- CSV header `timestamp,contract_id,open,high,low,close,volume`, aware timestamps and
  exact contract identity per bar.
- Metadata schema `verified_es_import_v1`, `verified: true`, source SHA256,
  `bar_minutes: 5`, `analysis_cutoff`, `contract_identities` keyed by ID with
  `root: ES`, `exchange: CME`, explicit `expiry`.
- `identity_evidence`, `roll_methodology`, `roll_evidence`, `session_hours`,
  `timezone: America/New_York`, `price_adjustment: UNADJUSTED_CONTRACT_PRICES`,
  `adjustment_evidence`.
- A separately supplied, vetted cash-session calendar with `sessions` containing
  `session_date`, aware `opens_at` and `closes_at`. Missing five-minute bars make
  the session unavailable; no forward fill or incomplete-day aggregation occurs.

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli expert import-es \
  --csv /path/to/verified-identified-es-5m.csv --metadata /path/to/es-metadata.json \
  --calendar /path/to/cash-calendar.json --output /tmp/es-cash-context-v1
```

This path requires actual evidence, not filling metadata fields with guesses.
Neither the optional import nor ordinary offline study commands can initiate a
broker connection or paid data request.
