# PR 8A pilot evidence

Implementation: `aea28ae31494ed75da63e88b73344df5796002bb` (clean worktree for all three evidence runs).
Base: `7183c51776eec0fbcb2420692748a0c993142320`, merged PR7C/#11.

All inputs are **synthetic**. Real securities acquired: **0**. A licensed historical
population/vintage source remains unavailable. The [provider matrix](HISTORICAL_UNIVERSE_PROVIDER_EVALUATION.md)
documents the CRSP recommendation, Norgate alternative and access/platform/license blockers.

## Pilot

The master contains **100 stable IDs**, **114 assertions** and **10 lifecycle events**.
The panel contains **67,249 generated daily bars** in **485 ID/year/capture partitions**.
Materialized windows: January–June 2008, 2015, 2020 and 2022; January 1–October 23, 2026.
This is sparse scenario coverage, not real or continuous 2007–2026 market history.

| Selection session | Eligible / generated catalogue | Selected | Universe quality |
|---|---:|---:|---|
| 2008-04-30 | 90 / 100 | 50 | PIT_UNVERIFIED |
| 2008-05-30 | 90 / 100 | 50 | PIT_UNVERIFIED |
| 2015-04-30 | 89 / 100 | 50 | PIT_UNVERIFIED |
| 2015-05-29 | 89 / 100 | 50 | PIT_UNVERIFIED |
| 2020-04-30 | 89 / 100 | 50 | PIT_UNVERIFIED |
| 2020-05-29 | 89 / 100 | 50 | PIT_UNVERIFIED |
| 2022-04-29 | 89 / 100 | 50 | PIT_UNVERIFIED |
| 2022-05-31 | 88 / 100 | 50 | PIT_UNVERIFIED |
| 2026-08-31 | 88 / 100 | 50 | PIT_UNVERIFIED |
| 2026-09-30 | 88 / 100 | 50 | PIT_UNVERIFIED |

One weak identity and one unknown knowledge assertion deliberately make the
population/ranking evidence incomplete. Selected usable rows remain reconstructed;
neither code causality nor synthetic clocks establish `PIT_VERIFIED`.
Four bankruptcy/delisting/merger events have **no verified terminal value**.
The cash-merger fixture preserves USD25 consideration independently of terminal
proceeds. The inventory includes a ticker change, reused ticker across issuers,
two share classes, reorganization/new listing, venue transfer, recent IPO, halt,
split and two dividends, including one unresolved ex-date. Missing history remains
missing. There are no delisting fills, carried-forward prices or automatic zeros.

Ranking uses `median(Close * Volume)` across the last **60 completed eligible
sessions**, raw price/share units, Close >=USD5 and stable-ID tie-breaking. The
month-end decision is Close +2h; fixture bars are available Close +1h.
Membership begins at the next Open, using no next-session observations.
Coverage gaps between nonconsecutive pilot months return unavailable.

One selected 2026 stock reaches existing unmodified swing/outcome interfaces:
**5 illustrative signals and 9 first-signal path rows**. Context is explicitly
unavailable and strict execution is **NOT_ADMITTED**. No broad strategy study,
edge claim or portfolio simulation is made.

## Scale and environment

Fresh sequential subprocesses, with no concurrent regression run for either scale case.
Python 3.12.9, macOS 26.6.2 arm64, PyArrow 23.0.1, exchange-calendars 4.13.1,
market-shared 0.2.0. Peak RSS includes Python and native Arrow allocations.
The sandbox denied Arrow CPU/cache sysctl probes; Arrow continued successfully.

| Case | IDs | Rows | Partitions | Monthly members | Total seconds | Freeze seconds | Build seconds | Peak RSS MiB |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| scale100 | 100 | 12,400 | 101 | 100, 100 | 2.693 | 0.927 | 0.550 | 150.17 |
| scale1000 | 1000 | 124,000 | 1012 | 1000, 1000 | 17.626 | 9.402 | 4.478 | 195.31 |

Each scale panel has 124 sessions per security and two monthly selections. These
are bounded-depth engineering measurements, not a five-million-bar benchmark or
proof of actual data completeness. Scale-source quality is `PIT_RECONSTRUCTED`;
synthetic inputs cannot be verified market evidence. Full stage timings, raw RSS
bytes and capture hashes are in the committed [evidence bundle](evidence/pr8a/hashes.json).

## Immutable hashes

| Pilot artifact | SHA256 |
|---|---|
| security_master | `a098a60f981261e31377edb2bdd8e7cb5085b65f40b86e333524f255758592d5` |
| research_panel | `53bc1723d67d7726ff3d28f382049f95259410c24ec0b48d0c67c7af2119cd2d` |
| universe | `a1cfec4dc56f68fb2052d9277feb1fcd4ccad42f78edb360c3b25fbfccf6900e` |
| integration | `e95ebacf441515cd808f6b78889e4c83506fffda20251802e759b86272149394` |
| Pilot report bundle | `e485544e7e0c9122735a47ae9b8a29e14fb1420b9dc06f1b70919206eaf41aef` |
| Committed evidence bundle | `924b04246eb5bf355042d93814323786f1860d1d10969ad60ba17f17cbf40c7a` |

The complete input-capture hash inventory and output hashes for all three runs
are in [pilot_report.json](evidence/pr8a/pilot_report.json),
[scale100_report.json](evidence/pr8a/scale100_report.json) and
[scale1000_report.json](evidence/pr8a/scale1000_report.json).
Per-report artifact hashes are preserved alongside them. Full payloads remain
in ignored local directories:

```text
data/research_datasets/pr8a-pilot-8xc4tbfk-v1/
data/research_datasets/pr8a-scale100-8xc4tbfk-v1/
data/research_datasets/pr8a-scale1000-8xc4tbfk-v1/
```

Master/panel bundles embed source bytes; universe bundles explicitly require the
master/panel dependency hashes and verify all bytes on loading. Development
snapshots named `pr8a-dev-*` were retained, not overwritten; final evidence refers
only to the three clean-commit runs above.

## Regression and preservation

**`.venv/bin/python -m pytest -q`: 456 passed in 51.62s**, including 56 new
universe tests and all 400 preceding regression tests. The suite blocks sockets.
The clean-runtime installation regression also passes with optional libraries absent.
See [exact pytest output](evidence/pr8a/pytest.txt). No canonical lint command exists;
`git diff --check` passed.

**All 1,259 pre-existing files remain byte-for-byte unchanged** under
`data/history_cache` and `data/research_datasets`, including AAPL, GOOG, SPY, QQQ,
RSP and prior event/context/swing/outcome bundles.
Original inventory SHA256:
`0fc7dbce1cca3b202bbacdd664475e035a08b20e9ab56014fa00defe7274dba6`.
See [preservation check](evidence/pr8a/preservation.json).

The shared wheel remains pinned to finwhaling source
`57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`, wheel SHA256
`e425124219d7be06ff8b82f2e0b7bcda2f293c6c26825ece19347e9316083df7`.
No finwhaling source, prior inputs, execution accounting or strategy definitions
were changed. Broker connections, account queries and orders: **0**.
No paid subscription, registration, vendor-data fetch, VM, deployment, merge or
PR8B work occurred. Public documentation research and authorized GitHub
operations are the only network work.

Reproduce with the commands in [the infrastructure guide](POINT_IN_TIME_HISTORICAL_UNIVERSE.md).
Use the pinned implementation commit for exact source identity and unused output
directories. Data hashes are reproducible; resource measurements and report metadata
are environment-dependent.

## PR #12 semantic-load review fix

The loader now recomputes all derived universe records from frozen dependencies
and compares canonical JSON before accepting the bundle. Valid byte hashes alone
are insufficient. Regression coverage includes 22 resealed-output mutation cases,
a coherently forged liquidity score with matching candidate/summary records, and
proof that repeated member queries do not recompute selection. Full regression:
**480 passed in 67.54s (0:01:07)**; focused universe suite: **80 passed in 19.28s**.

The original pilot and both scale universe bundles pass the stronger semantic
validation with their original hashes. All **3,614 frozen local files** present
before this amendment remain unchanged, including earlier development snapshots.
No price/master/universe artifacts were regenerated. The measurements and original
456-test output above remain evidence of their pinned earlier implementation;
universe loading now additionally incurs one full semantic recomputation.

[Review-fix evidence](evidence/pr8a-semantic-load-v1/hashes.json), including exact
test output, validated bundle hashes, preservation and validation-source hashes.
Evidence bundle SHA256: `c2c75831bfb0b038e838fb2cbe87fb862a5c3db1927fc288c707dba2b5799dba`.
