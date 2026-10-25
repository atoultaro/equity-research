# LEAN and NautilusTrader: local framework evaluation

Evaluation date: October 23, 2026. All prices, signals, trades and returns below
are **synthetic engineering controls**, not investment results.

## Decision

**Retain the PR4 simulator temporarily. Neither evaluated prototype is ready to
become the primary equity backtester.** NautilusTrader is the stronger candidate
for the next bounded adapter experiment (3.20/5 versus LEAN's 2.35/5). LEAN
demonstrated more native equity lifecycle machinery, but its Python launcher
failed at shutdown on this Mac and this prototype's daily bracket overclosed a
long position. Nautilus completed cleanly and repeated deterministically, but its
generic equity/bar setup did not supply split, dividend or halt enforcement.

These are ratings of the pinned implementations and tests here. They do not rank
every possible configuration of either engine. Throughput alone does not satisfy
our historical correctness requirements.

Authoritative task: the user's **Framework Evaluation Spike: LEAN vs
NautilusTrader**. Branch: `spike/backtest-engine-evaluation-v1`, based on reviewed
PR8A semantic-validation fix `2b6ffa0daf2becdb5d2616d2bb1e82a3bb134f5c`.
The common-case/scale adapter revision is
`01692c8fc1235d65d8fa31547d9f6a380664aed7`; later identity, compatibility and
analysis sources are individually pinned in the evidence's source-code hashes.
This spike changes no PR4, PR7B, PR7C or PR8A implementation, acquisition policy,
shared mathematics or original frozen data. No broker connection, paid service,
parameter search or deployment was used.

## Reproduce and inspect

The [experiment instructions](../experiments/backtest_engines/README.md) contain
the exact isolated installation and execution commands. Framework packages are
outside the core `.venv`; no framework dependency was added to `pyproject.toml`.
Every experiment refuses an existing output path and verifies its sealed inputs.

The immutable [evidence bundle](evidence/backtest-engine-spike-v1/hashes.json)
contains 108 payload files. Its SHA256 is
`2b915746f2dd4522a239864f0c7c4b45d075691cdda76b0f028fa10a6d627930`.
Useful entry points are:

- [Environment and software hashes](evidence/backtest-engine-spike-v1/environment.json): wheel URLs/hashes, installed Python packages, NuGet package identities, DLL hashes, release references and build audit warnings.
- [Shared fixtures and intents](evidence/backtest-engine-spike-v1/fixture-cases.json) and [input hashes](evidence/backtest-engine-spike-v1/input-hashes.json).
- [Native fills and cost reconciliation](evidence/backtest-engine-spike-v1/comparison.json), with separate common-cost and native-cost records.
- [Scale measurements](evidence/backtest-engine-spike-v1/scale-summary.json), [repeat comparisons](evidence/backtest-engine-spike-v1/repeatability.json), and [scores](evidence/backtest-engine-spike-v1/scores.json).
- Raw `cases-*`, `compatibility-*`, `identity-*` and `scale-*` result JSON, process indices and compressed launcher logs in the same directory. Published logs replace the local repository path and hostname; numeric results are unchanged.

The complete shared input seal is
`b26c59b95e90e930fe8690601d1de9342890fc68c6e87540fc0184b4825373ef`.
The unchanged PR4 price CSV hashes to
`3aa3ca9d16306c6833551e6aed84c2af3c1eb9ff5114010478283c813ae18410`.
PR8A dependencies include:

| Frozen input | SHA256 |
| --- | --- |
| Pilot security master | `a098a60f981261e31377edb2bdd8e7cb5085b65f40b86e333524f255758592d5` |
| Pilot price panel | `53bc1723d67d7726ff3d28f382049f95259410c24ec0b48d0c67c7af2119cd2d` |
| Pilot universe | `a1cfec4dc56f68fb2052d9277feb1fcd4ccad42f78edb360c3b25fbfccf6900e` |
| 1,000-stock universe | `3d7b6c00e1b0a152f5fb1866fa3210d3cf56e83c8e4505ca2ec45799ecb839f3` |

Full panels and toolchains remain in ignored local directories. A fresh checkout
can regenerate the PR8A synthetic inputs using its existing generator into new
directories, then freeze a new transport bundle. The committed evidence includes
the shared small cases, source identities, outputs and exact dependency hashes;
it does not pretend that the large ignored panel is committed.

## Environment, installation and local operations

Hardware: Apple M1, eight cores, 16 GiB RAM; macOS 26.6.2, arm64. Runs were local
and sequential. Software installation used the network; final engine processes
used a macOS `sandbox-exec` profile denying all network operations. There were no
market-data downloads or account credentials. Docker client 20.10.12 exists but
its daemon was unavailable and was neither started nor used.

| | LEAN | NautilusTrader |
| --- | --- | --- |
| Evaluated software | Assembly 2.5.0.0; source `f3d841e60dfd010ee5fc293ea893e56952484108` | **Stable 1.231.0**, release `v1.231.0` |
| Source reference | Unmodified official source build | Tag object `d3e1685e979925d7b0ffacd1b3f442547686e18f`, source commit `27a8e54e7ac3c57d6cbf8891f0283dfbaee97317` |
| Runtime | .NET SDK 10.0.402; Python 3.11.6; QuantConnect.pythonnet 2.0.66 | CPython 3.13.3; native macOS arm64 wheel |
| Isolated dependencies | Separate Python venv, SDK and NuGet cache | Separate venv; PyArrow 26.0.0 and pandas 3.1.0, separate from core pins |
| License | Apache-2.0 | LGPL-3.0 |
| Account/Docker/cloud required for this experiment | None | None |
| Actual offline computation | Completed and wrote outputs | Completed and wrote outputs |
| Clean process exit | **Failed**, including a zero-order identity control | **Passed** |

The direct open-source LEAN launcher computed with local synthetic CSV/map/factor
files and an empty API token. This establishes an account-free computational
route, with an unresolved process failure. It does not establish a clean local
Python deployment. The separately operated LEAN CLI documentation currently
requires membership in a paid organization and uses Docker for local workflows;
neither CLI nor hosted QuantConnect was used. See the official
[CLI prerequisites and engine distinction](https://www.quantconnect.com/docs/v2/lean-cli/key-concepts/getting-started).

LEAN aborted after results with `System.InvalidOperationException: GIL must
always be released, and it must be released from the same thread that acquired
it`, at `Python.Runtime.Py.GILState.Finalize()`. The native return code was -6
(some shell timing wrappers report 134); the experiment wrapper returns failure.
Python 3.12.9 reproduced the shutdown failure. No source patch suppressed it.
This is an observed compatibility problem for this Mac/toolchain, not proof of
failure on other platforms. The pinned upstream Python README recommends
3.11.11; that patch version and Linux/Docker remain **NOT_VERIFIED**. The source
build also produced upstream NuGet vulnerability warnings, retained in the
environment manifest. Resolving those dependencies is a maintenance gate.

Nautilus 1.231.0 was installed explicitly, with matching installed 1.x APIs.
Its latest website documentation describes **2.x release candidates**, whose
APIs differ; those examples were not mixed into this implementation. This split
is explicitly described in the official
[installation documentation](https://nautilustrader.io/docs/latest/getting_started/installation/).
The evaluated wheel's platform tag targets macOS 26 arm64. A stable-to-2.x
migration and older-Mac installation are **NOT_VERIFIED**. License obligations
must be reviewed for any eventual redistribution; no subscription was necessary
for this local stable-wheel experiment.

## Shared strategy experiment

The reference invokes the existing PR4 simulator without changing its rules.
The native implementations use LEAN `QCAlgorithm`/equities and Nautilus
`BacktestEngine`/`Equity`/orders. Both consume the same frozen source bars and
precomputed order intentions. No custom fill model was introduced to force
parity. Ten cases cover the original fixture, deterministic post-signal variants,
and one previously frozen PR7B signal.

Common intent: $10,000 cash, 1% planned risk, signal available March 10, 2026 at
20:15 UTC, activation March 11 at 13:30 UTC, buy stop 130.60, initial stop 125.50,
three eligible sessions and a target at two times actual entry risk. Common
cost configuration is $0.005/share commission plus $0.50/order, with $0.01/share
adverse slippage where the native model applies it. Separate native-cost runs
leave each engine's default fees/slippage in place.

An ordinary native stop order needs a quantity before the unknown opening gap.
Both prototypes therefore precommit 19 shares using trigger plus slippage minus
stop. PR4 natively sizes at the executable opening price and buys 15. At 132.01,
actual initial risk is $123.69 versus PR4's $97.65. The planned $100 risk budget
is not the actual native gap risk. This is a sizing-policy difference, not a
future-open quantity masquerading as a precommitted order.

| Common-cost case | PR4 native net dollars | LEAN observation | Nautilus observation |
| --- | ---: | --- | --- |
| Favorable entry gap | 194.000 | Closed, 246.190 | Closed, 245.99 |
| Losing stop | -98.950 | Closed, -125.070 | Closed, -125.08 |
| Gap through stop | -181.450 | Closed, -229.570 | Closed, -229.58 |
| Gap through target | 268.550 | Closed, 340.620 | Closed, 245.99 |
| Expired entry | No trade | No fills | No fills |
| Stop and target in same daily bar | -98.950, conservative stop first | **Both exits fill; -19 shares remain** | Target fills first, 245.99 |
| Breakout on third eligible session | 192.800 | Closed, 192.990 | Closed, 192.79 |
| Intraday entry and ambiguous exit | -98.470 | Open position | Open position |
| Delayed information availability | 130.670 | Later activation preserved; open position | Later activation preserved; stop rejected |
| Original frozen PR7B signal | Not a PR4 candidate replay | Timestamp preserved; open position | Timestamp preserved; stop rejected |

Closed native dollar figures in this table describe computed ledgers; every LEAN
row still has a failed launcher status. Open positions and the overclosed bracket
have **no admitted realized trade P&L/R**. Their raw cash, marked equity and signed
holdings remain visible in the evidence.

The divergences have specific causes:

- **Order semantics/configuration:** native targets are sell limits; PR4 uses
  market-on-touch economics. LEAN's target gap sells at 150.00. Nautilus uses its
  native bar path/limit price; the common one-tick slippage configuration produces
  145.02 versus the posted 145.03. Its separate default-slippage run preserves
  the limit. This configuration needs rejection or revision before admission.
- **Daily-bar ordering:** Nautilus's fixed native OHLC path chooses the target in
  the collision. That is simulated ordering, not observed intraday evidence.
  PR4 deliberately chooses the stop and flags ambiguity.
- **Prototype implementation gap:** LEAN's independent protective orders plus
  callback cancellation are not atomic OCO. Both are processed before the
  cancellation protects this daily bracket. Cash-account configuration alone did
  not enforce the intended one-long invariant. This adapter must fail admission;
  this result does not establish that every possible LEAN bracket must overclose.
- **Entry admission:** Nautilus's native `reject_stop_orders=True` rejects an
  already-triggered stop; LEAN accepts it. The delayed-availability and frozen
  PR7B controls expose that difference without shifting their original clocks.
- **Entry/terminal event ordering:** protective orders created after an intraday
  entry are not retroactively tested against preceding daily extremes. Neither
  prototype silently adds PR4's conservative same-bar or end-of-data full exit.

Signal, submission and activation clocks are distinct fields. Daily engine fill
events are often stamped at the 20:00 UTC processing time even for modeled open
prices. They must not be relabeled as observed 13:30 intraday executions. The
reference retains its explicit open/unknown-intraday windows.

The favorable native reconciliation illustrates the separate cost fields:

| Dollars, 19 shares | LEAN | Nautilus |
| --- | ---: | ---: |
| Gross before modeled slippage | 247.570 | 247.57 |
| Slippage | 0.190 | 0.38 |
| Nominal commission | 0.1900 | 0.190 |
| Fixed fees | 1.00 | 1.00 |
| Currency rounding residual on fees | 0.0000 | 0.010 |
| Net | 246.190 | 245.99 |
| Actual initial risk | 123.690 | 123.69 |
| Net realized R | 1.9903791737408036 | 1.9887622281510227 |

Gross/slippage attribution is reconstructed from frozen bars and pinned native
order semantics; it is labeled as reconstructed, not an engine-reported field.
Closed ledgers reconcile both gross-to-net and native equity. LEAN settled and
unsettled cash are captured separately: available cash during settlement is not
the same as total portfolio equity. Default-cost sensitivity is separate from
this common-cost audit; no fee or fill was tuned to match PR4.

## Historical universe and lifecycle compatibility

Two complementary tests use PR8A. The scale adapter consumes the actual validated
synthetic panel and frozen monthly membership. The identity probe projects actual
master assertions as of May 15, 2008; May 15, 2015; and May 16, 2022, retaining
20, 21 and 23 known records respectively. Its separate input seal is
`978bd2766c756ab54aad4df704f316545ab809a3063adcc632bd9242cc9128db`.
Unknown/future assertions are not promoted to historical facts. Native IDs remain
distinct for reused tickers, separate classes and reorganized/relisted securities.
These are identifier/cache projections; full trading through those transitions
is **NOT_VERIFIED**.

An additional, explicitly invented lifecycle control uses PR8A's calendar and
contracts: ALPHA becomes BETA on April 18, 2022; a 2-for-1 split changes 100 to 50;
a $1 dividend occurs April 20; April 13 is missing; April 19 is halted; and an
April 22 delisting has **unknown terminal value**. These controls are not presented
as observations contained in the original provider panel.

| Requirement | LEAN observed behavior | Nautilus observed behavior / required work |
| --- | --- | --- |
| Stable identity / rename | Native map event ALPHA→BETA, same SID; consumes mapped BETA rows | Permanent native ID with raw-symbol metadata update; external PIT mapping required |
| Reuse / classes / relisting | Source master maps to distinct native SIDs | Source master maps to distinct native instrument IDs; issuer/class keys preserved externally |
| Raw split | Native factor/split event changes 2 shares to 4 | Generic Equity + bars leaves shares unchanged; needs explicit action ledger/module |
| Dividend | Native dividend event credits $1 per eligible share | No automatic cash credit in configured generic feed |
| Adjusted view | Native SPLIT_ADJUSTED price view verified alongside RAW | Explicit separate adjusted price/volume control; not automatic action accounting |
| Missing bars | Fill-forward disabled; absent bars stay absent | Absent bars stay absent |
| Halt | A market order can fill at cached 50 despite no halted-day bar | `HALT`/`is_trading=False` alone did not prevent a 50.01 market fill |
| Unknown delisting terminal | Native auto-liquidation at last 49 is **unverified and not admitted** | NOT_AVAILABLE_FOR_TRADING leaves position outstanding; no invented close value |
| Monthly membership | Precomputed schedule works; native ScheduledUniverse tested separately | Frozen membership gates precomputed orders; no replacement screening engine |
| Open-auction order | Native order types available; benchmark clock assumptions remain explicit | Native AT_THE_OPEN request rejected as unsupported in this simulator setup |
| Source vintages / field availability | CSV/map/factor files do not carry our complete publication-time contract | ts_event/ts_init primitives do not themselves enforce our source-vintage rules |

The native LEAN ScheduledUniverse probe selects the supplied PIT list causally,
but first-month entrants have no seed price and their May orders do not fill;
June orders do. A causal warmup/seeding adapter is required. The main portfolio
benchmark preloads instruments and gates orders using membership, so it must not
be mistaken for proof that dynamic native subscriptions are production-ready.

Nautilus instrument IDs include venue. This experiment deliberately uses stable
simulation IDs with source exchange stored separately; transferring an open
position across venues is **NOT_VERIFIED**. Neither present-day ticker lookup nor
native symbol metadata is an authoritative historical security master.

For both engines, missing observations, stale-price eligibility and halts require
an explicit calendar/tradability gate. Corporate actions require verified event
dates, evidence and basis metadata. RAW execution and split-adjusted research
views must not be double-adjusted. An unknown terminal value must remain
unresolved even when an engine generates a convenient liquidation. Native event
support cannot replace PR8A admission checks. Revised-vintage replay through both
engines remains **NOT_VERIFIED**.

## Bounded multi-stock measurements

Both engines use the same January 3–June 30, 2022 synthetic panel: 124 sessions
per identity, with frozen May/June universe snapshots. Each selected security
gets a precomputed one-share entry and a fifth-session-open exit in each monthly
batch. Initial cash is $1 million, cash accounts, common costs, no leverage or
strategy optimization. Nautilus's simulated submit limit is explicitly increased
to 10,000/s for the bounded batch; its default 100/s would throttle this test.

There are **24 fresh sequential processes**: two engines × three sizes ×
orders/feed-only × two repetitions. Every run delivered its expected bar count;
order runs had 40, 400 or 4,000 fills and ended flat. A 100-member monthly subset
spans 102 distinct IDs because membership changes; the 1,000-member runs span
1,000. These are active-member counts, not an assertion that every subset is
constant across months.

The following order-run figures show repetition 1 / repetition 2. RSS is peak
process memory in MiB, including native allocations. LEAN numbers describe a
computation **followed by launcher failure**, not operationally successful runs.

| Engine / active members | Delivered bars | Wall seconds | Bars / wall second | Peak RSS MiB | Loop seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nautilus / 10 | 1,240 | 7.941 / 7.160 | 156 / 173 | 416 / 534 | .267 / .190 |
| LEAN / 10 | 1,240 | 19.255 / 12.254 | 64 / 101 | 531 / 878 | .223 / .135 |
| Nautilus / 100 | 12,648 | 8.922 / 6.163 | 1,418 / 2,052 | 511 / 548 | 1.375 / 1.240 |
| LEAN / 100 | 12,648 | 17.795 / 12.048 | 711 / 1,050 | 781 / 837 | .631 / .462 |
| Nautilus / 1,000 | 124,000 | 39.417 / 34.073 | 3,146 / 3,639 | 436 / 568 | 28.381 / 22.952 |
| LEAN / 1,000 | 124,000 | 36.782 / 34.658 | 3,371 / 3,578 | 1,303 / 1,635 | 13.656 / 9.934 |

Wall time includes adapter preparation, startup, execution and termination; it is
the more useful cross-engine throughput comparison. Loop scopes differ: Nautilus
times `engine.run`, while LEAN times first data callback through end callback.
Nautilus receives per-bar callbacks and LEAN aggregated daily slices. Loop rates
are diagnostic, not interchangeable engine speed claims. Two repetitions are not
a confidence interval or a sustained-load test.

At 1,000 stocks, Nautilus recorded initialization .148/.083 seconds and bar
construction/loading 2.993/2.754 seconds; its one global `add_data` avoids repeated
sorting. LEAN recorded initialization 1.896/1.566 seconds; its separate native
CSV read cost is interleaved with simulation and **NOT_VERIFIED** as a pure I/O
measurement. Wrapper preparation/launcher timings remain in raw records. All
sizes parse the same full transport JSON before selecting their subset, so these
RSS figures do not establish production partition-streaming memory requirements.

Orders-minus-feed paired loop increments at 1,000 stocks were 15.372/9.119 seconds
for Nautilus and 12.503/8.681 for LEAN. These include order handling, accounting
and strategy callbacks; isolated ledger overhead is **NOT_VERIFIED**. Full staged
and feed-only measurements are published, not inferred from total wall time.

All **12 repetition pairs** match both ordered fills/state and economic content
after removing volatile resource/time/UUID fields. Economic comparisons also
normalize tied instrument ordering; the stricter ordered comparison passed too.
At 1,000 stocks, final flat equity was 998,700 for Nautilus and 998,920 for LEAN
in both repetitions. These differ because of execution timing/native cost
application, not different input selection, and are not strategy performance
claims. Deterministic computation does not erase LEAN's process failure.

The separate lifecycle controls above test missing data/delistings; the complete
regular scale slice does not measure large-universe lifecycle churn. Capacity at
3,000 stocks, twenty years or five million bars, other hardware, real-provider
completeness and IBKR integration are all **NOT_VERIFIED**. No extrapolation is
used in the decision.

## Adapter design and migration work

The demonstrated boundary is:

```text
immutable PR8A master + panel + source evidence
    → validated PIT membership + session/availability clocks
    → frozen PR7B signal identity, original timestamp and order intent
    → native engine instruments/orders/fills/account state
    → immutable raw records + separately audited dollar/risk results
```

The frozen PR7B signal is consumed without regenerating it or shifting its
availability. It remains a synthetic, NOT_ADMITTED execution probe. Scale uses
explicit precomputed controls, not thousands of newly generated PR7B signals.
MarketContext remains descriptive. PR7C signal-outcome measurements are neither
replaced nor mixed into executed trade returns.

| Boundary | Required adapter responsibility |
| --- | --- |
| Identity | Permanent security ID → engine ID; time-bounded ticker/venue mapping; separate issuer/class IDs; no present-day substitution |
| Calendar/time | Source sessions, America/New_York/DST → aware UTC clocks; explicit missing/stale/halt gates |
| Availability | Gate every feature/signal and source assertion by known-at time, then activate no earlier than the permitted session |
| Actions/basis | Verified actions and terminal evidence; separate raw/adjusted price and volume basis; preserve unknowns |
| Orders | Declare precommitted sizing versus fill-time sizing, expiry clock, target type, ambiguous-bar policy and long-only invariant |
| Portfolio | Preserve native cash/unsettled cash/holdings; reconcile closed gross, fees, slippage, rounding, net and original actual risk |
| Provenance | Seal inputs, software/environment identity, native outputs and analysis; reject inconsistent or incomplete artifacts |

LEAN's native equity files reduce lifecycle machinery to implement, but producing
correct vintage-specific map/factor files, retaining source availability, fixing
the bracket and obtaining a clean Python process are substantial migration gates.
Nautilus's Python strategy callbacks and clean isolated wheel operation are easier
locally; explicit equity lifecycle accounting/tradability and venue mapping are
larger adapter obligations. Neither migration is a dependency swap. A credible
effort estimate requires the next acceptance experiment; no calendar estimate is
invented here.

Retain PR4 as the conservative arithmetic/timing oracle, PR8A as the identity and
PIT authority, PR7B as strategy definitions, PR7C as independent signal-outcome
analysis, and the hash-pinned shared indicator wheel as the only shared ATR math.
Keep immutable evidence/admission policies above either framework.

## Weighted assessment and next PR

Scale: 1 = observed blocking failure/major unmet requirement, 3 = useful bounded
demonstration with material adapter gaps, 5 = demonstrated research-readiness
across the evaluated requirement. Untested capabilities are listed as
**NOT_VERIFIED**, not assigned imagined capability scores. Ratings below cover
only the dimensions actually exercised; they are judgment, not measured precision.

| Evaluated dimension | Weight | LEAN | Nautilus | Demonstrated reason |
| --- | ---: | ---: | ---: | --- |
| Backtesting correctness | 30% | 2 | 3 | Auditable closed ledgers in both; LEAN bracket overclose; NT daily-path/limit-slippage and entry-admission mismatches |
| PIT universe/data integration | 25% | 3 | 2 | LEAN native split/dividend/map events; both need PIT/tradability gates; NT generic setup lacks action accounting |
| Bounded multi-stock scalability | 20% | 3 | 4 | Both compute 124k bars and repeat; NT clean exit/lower observed RSS; LEAN faster inner loop but failed termination |
| Python strategy development | 15% | 2 | 4 | Both actual Python strategies; LEAN CLR/runtime friction; NT direct stable callbacks, with 1.x/2.x maintenance caveat |
| Local operations, maintenance and cost | 10% | 1 | 4 | Both account-free local computation; NT clean wheel runs; LEAN SDK/build/Python shutdown and dependency audit gates |
| **Weighted total / 5** | **100%** | **2.35** | **3.20** | Neither passes readiness gates |

Suggested next PR: **Nautilus stable-1.x equity adapter acceptance gates**, still
offline and bounded. Implement only enough explicit split/dividend accounting,
halt/missing/stale rejection and unknown-terminal handling to pass the lifecycle
controls; add long-only/cash/risk invariants and declared daily ambiguity/limit
semantics; replay the frozen signal without changing its timestamp; then require
identical input provenance and repeated reconciled outputs. Do not adopt it as
primary until those gates pass. Investigate LEAN's clean shutdown and atomic
protective-order behavior separately before spending effort on a production LEAN
adapter. Neither engine is automatically selected by the weighted total.

## Regression and preservation

Command: `.venv/bin/python -m pytest -q`.
Result: **487 passed in 101.59s (0:01:41)**, no skips, with network denied by the
offline regression harness. Seven new tests cover immutable transport,
precommitted sizing/expiry, PIT portfolio scheduling, cash/risk reconciliation,
cost/rounding attribution and deterministic comparison. Actual native-engine
experiments are separate from these dependency-free core regression tests.

The [preservation audit](evidence/backtest-engine-spike-v1/preservation.json)
compared **3,618 existing files** in history cache, research datasets and original
fixtures: **unchanged**, no overwritten run directory. `git diff --check` passes;
core source, project dependencies, vendor wheel and original fixtures have no
diff from the inspected base. This branch is an evaluation only and is not
automatically merged.
