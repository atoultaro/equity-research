# General swing strategy framework — PR 7B

This milestone records opposing breakout hypotheses and contemporaneous market
observations. It does not establish an edge, reconstruct screening membership,
optimize parameters, or trade earnings. The authoritative task is PR 7B; its
research inventory supersedes the older one-policy restriction in AGENTS.md.
Strict execution remains one security at a time and long only.

Branch: `feat/general-swing-strategies-v1`. Inspected base/latest main:
`c5a8b649783d44d2cd6c2919c6cc8e0e22ab7772` (merged PR 7A #9).
The shared wheel remains market_shared 0.2.0, built from finwhaling commit
`57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`; finwhaling is unchanged.

## Architecture and existing capabilities reused

| Component | Responsibility |
| --- | --- |
| `swing/model.py` | Frozen typed Configuration, Boundary, Setup, Trigger, Signal and TradePlan records; deterministic identities; boundary/trigger/plan pure functions |
| `swing/engine.py` | Causal completed-session feature windows, trend gate, independent failed-attempt lifecycle and inventory; no provider or fill logic |
| `swing/dataset.py` | Self-contained frozen studies and MarketContext, immutable output, integrity checks and semantic recomputation |
| `swing/execution.py` | Strict CSV admission, rebuild eligible plans from those admitted inputs, convert long plans to existing buy-stop orders, reserve one security |
| `swing/cli.py` | Explicit offline research and strict replay commands |

A **setup** is a price structure with an observed boundary. A **trigger** is a
completed-session event activating it. A **signal** combines the trigger with
identity, features, availability and provenance. A **trade plan** proposes entry,
stop, expiry and provisional risk. An **order** is an instruction to the simulator;
a **fill** is its simulated execution. Neither a setup nor a SHORT signal implies
that any order, fill or trade exists.

PR 5D's ResearchDataset supplies canonical native-basis prices and lineage.
PR 6A/6B EventStudy supplies the frozen calendar, complete corporate-event inventory
and evidence-backed `as_known` subset. PR 7A's `context_as_of` supplies context.
The existing immutable `encode/digest/read_bundle/write_bundle` conventions and
pinned dependency identity are reused. No ATR formula is duplicated: full ATR14
uses the wheel's gap-aware `true_range` and `atr_simple_last` after 15 bars.
SMA50 and SMA200 each require their full completed-observation window.

PR 4 inspection confirmed **long-only** buys and full-position sells. Its raw CSV
loader, price grid, actual-fill integer sizing, cash/notional limits, slippage,
commissions, fees, stop/target ordering, maximum holding, end-of-data exits and
fixed original-risk R accounting are reused. The fill loop is exposed as
`execution.replay_order`; the legacy `simulate` delegates to the same loop after
its original qualification and planning. Existing legacy qualification is not
silently imposed on the new SMA50/SMA200 strategy. There is no second fill engine.

There is no external cancellation event interface, short borrow/financing,
trailing or partial exit, portfolio optimizer, margin model or compounded NAV.
Unsupported cancellation and short execution are explicit result fields.

## Versioned configuration and geometry

`Configuration().record()` emits `swing_strategy_config_v1`, strategy version `1`,
with `breakout_continuation_v1`, prior-N-session High boundary N=20, strict close
comparison, SMA50/SMA200 gates, ATR14 stop multiple 1.5, three-session order
validity, and reconstructed close-plus-60-minute signal availability.
`Configuration(FAILED).record()` selects `failed_breakout_v1`, disables continuation
trend gates and adds K=3 following sessions for failure confirmation. Other timing,
boundary and ATR defaults remain explicit. These are engineering defaults, with
no parameter search or performance-based selection.

For session t, resistance is exactly `max(High[t-N], ..., High[t-1])`.
The current High is excluded. The boundary records its construction rule, first
and last observation, latest input session, price dataset SHA256 and configuration
SHA256. `prior_boundary`, `evaluate_trigger` and `build_plan` separate geometry,
trigger and risk policy. A later VCP, horizontal pivot or descending-trendline
detector can construct a Boundary and use the trigger layer without changing
execution. Those detectors are not implemented here.

Continuation setup observations require complete boundary/ATR/SMA windows and
`Close > SMA50 > SMA200`. A trigger additionally requires `Close > resistance`.
Equality never triggers. This is a simple continuation baseline, not a full
Minervini model.

For failed breakouts:

1. An attempt requires completed `High > resistance`, with the original prior-N
   boundary retained. There is no continuation trend gate.
2. If that attempt already closes below the boundary, record
   `IMMEDIATE_FAILURE_OBSERVATION_ONLY`; emit no reversal signal or plan.
3. Otherwise, inspect each of the following K expected completed sessions. The
   first `Close < original resistance` confirms a SHORT signal. Equality waits.
   Confirmation on the Kth session takes precedence over expiration.
4. If no confirmation occurs by the Kth close, record `EXPIRED`. Attempts still
   open at the evaluation endpoint are `PENDING_END_OF_EVALUATION`.
5. A higher attempt creates a separate immutable setup; it neither resets nor
   changes an existing boundary or deadline. Overlapping attempts may confirm on
   the same session and remain separate observations with distinct stable IDs.
   They are correlated observations, not independent performance samples.

Each attempt has one terminal outcome in `setup_outcomes.json`, separate from its
original observation. No later outcome is fed into original setup features.
Missing, duplicate, off-calendar, nonfinite, inconsistent or identity-mismatched
price sessions fail the run. There is no forward fill, shortened lookback or
conversion of missing sessions into elapsed valid sessions.

## Availability, context and corporate actions

Signals become available at completed regular-session close plus the declared
60-minute delay (including actual early closes/DST from the frozen calendar).
A later explicitly supplied bar availability can only delay them. Explicit bar
availability must follow completion and precede the next listed open. Features
use no bar beyond the triggering session; the boundary ends before the attempt.
A fixed availability model is an assumption, not a historical dissemination or
price-vintage archive. No same-close fill is allowed.

Every signal calls `context_as_of(signal_available_at)` after detection. The full
returned continuous trend/volatility/participation observations, optional state,
missing breadth/leadership flags, reference-set identity, feature version,
dissemination caveats and context bundle hash are retained. PR 7A's strict
**available_at < decision** rule is unchanged: with equal close-plus-60-minute
models, the signal links to the preceding eligible context, not that same day's
new row. No eligible row means explicit UNAVAILABLE, with no later fallback.
Changing UPTREND/DOWNTREND/MIXED/unknown context cannot change raw trigger detection,
plan construction or signal identity. Market context never approves a trade.

The complete source-backed corporate-event inventory remains embedded, including
unknown ex-dates and source publication limitations. Only the existing
`EventDataset.as_known` evidence subset can invalidate detection: a sourced
effective split or dividend date within a relevant boundary/indicator window
makes that observation unavailable; a known discontinuity across an active attempt
invalidates it. Evidence must be public strictly before that decision. Later
publications and retrospective alignments cannot alter historical input features.
Unknown ex-dates represent global incomplete evidence and never imply overlap with
every setup. Record/payment dates are never used as ex-dates.

The actual AAPL/GOOG sources do not establish a complete historical corporate-action
knowledge archive. This conservative known-event rule cannot guarantee absence of
undiscovered discontinuities. Native IBKR split-adjusted price and volume semantics
remain unresolved for execution; no new adjustment or event publication rule is
introduced. See the existing AAPL/GOOG studies for source-specific limitations.

## Plans versus strict execution

A LONG plan references signal Close and fixed `Close - 1.5 * ATR14` stop.
A SHORT plan references `Close + 1.5 * ATR14`, always with
`SHORT_EXECUTION_UNSUPPORTED`. Nonpositive risk or stop yields an invalid plan.
Quantity and planned dollar risk remain null until actual execution assumptions
are known. Each plan includes null future-outcome linkage slots for horizon
returns, MFE/MAE, entry/holding context, realized R and rejection/expiry. These
slots are not input features or computed P&L.

The explicit long entry policy is a **buy stop at the planning Close rounded up
to the execution price increment**, beginning no earlier than the following
regular session whose open follows signal availability. The stop rounds down.
A gap up fills at `max(Open, trigger) + adverse slippage`; a gap down waits for a
trigger touch. This is not a guaranteed next-open market fill. The existing engine
sizes integer shares using actual allowed entry minus the placed fixed stop, cash
and risk limits. Quantity never derives from a hypothetical same-close fill.
Order validity counts eligible sessions including the third close. Target prices
use actual entry risk; same-bar collisions remain stop-first with ambiguity flags.
Original risk is `(actual entry - initial stop) * shares`, before costs, fixed for
net R. Gross dollars, modeled slippage, commissions, fees and net dollars stay separate.

The strict adapter first calls the unchanged `load_dataset`. It rebuilds the
inventory from those exact admitted bytes/configuration, so arbitrary plans or
foreign signal IDs cannot become orders. Native research bundle hashes do not
substitute for strict raw/no-actions certification. The actual IBKR datasets are
not admitted or replayed. Synthetic authored raw/no-action evidence exercises the
strict path without pretending it certifies real stocks.

Duplicate selected IDs are deduplicated. Sequential candidates reserve the
security through an order's expiry or a position's exit session; competing plans
are retained as explicit rejections. There is no same-session re-entry. Each
replay uses the declared fixed initial capital/risk budget; per-trade final cash
is not a compounded portfolio account or aggregate NAV.

## Actual local inventories

The fixed interval is **2024-01-02 through 2026-10-20**, exactly 703 sessions per
stock. No earlier frozen stock warmup was added. Evaluable means all required
windows exist before the continuation trend gate. Continuation setups are daily
trend-qualified boundary observations, even without a trigger; failed setups are
actual High-above-boundary attempts. Attempt counts are High-above-boundary
observations among the respective evaluable sessions, before the continuation
trend gate. Warmup differences explain why attempt counts differ by strategy.

| Security / strategy | Evaluable | Setups | Attempts | Triggers | Failed confirmations | Incomplete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AAPL continuation | 504 | 260 | 95 | 42 | 0 | 199 |
| GOOG continuation | 504 | 280 | 90 | 37 | 0 | 199 |
| AAPL failed breakout | 683 | 126 | 126 | 29 | 29 | 20 |
| GOOG failed breakout | 683 | 110 | 110 | 20 | 20 | 20 |

Continuation warmup excludes 199 sessions; failed-breakout boundary warmup excludes
20 (ATR14 is already warm by then). Additional continuation trend failures are
244 AAPL / 224 GOOG observations. Failed attempts end as:

| Security | Immediate observation only | Confirmed | Expired | Pending |
| --- | ---: | ---: | ---: | ---: |
| AAPL | 60 | 29 | 37 | 0 |
| GOOG | 56 | 20 | 34 | 0 |

Context coverage is 42/42, 37/37, 29/29 and 20/20 respectively, with zero unavailable
links. AAPL continuation: 42 UPTREND; GOOG continuation: 36 UPTREND and 1 MIXED;
AAPL failed: 29 UPTREND; GOOG failed: 20 UPTREND. No signals fall in DOWNTREND or
UNCLASSIFIED here. This distribution emerges from the fixed data/rules; it is not
a context filter. The complete 703-row context has 640 UPTREND, 48 MIXED and
15 DOWNTREND observations. All signals retain the seven unavailable optional
breadth/leadership features and unverified historical dissemination caveats.

These counts do not imply profitability, causation, selection skill or independent
samples. Every emitted signal and candidate, including future losers/unfilled
ones, remains local. There are **no real-stock fills or realized P&L**. Licensed
row-level prices/signals stay in ignored storage. Permitted aggregate evidence,
input references and full hashes are in
[evidence/general-swing-strategies-v1.json](evidence/general-swing-strategies-v1.json).

## Synthetic strict demonstration

The explicit synthetic schedule has 205 bars, full SMA200 warmup and two
continuation signals. All selected signals are replayed; the losing case remains.
For the first, the planning Close is 143 on 2026-02-04, but next-session gap entry
is 146.01 on February 5. ATR14-based stop rounds down to 139.67, quantity is 15,
and original risk is 95.10 dollars. The 2R target is 158.69; exit after slippage
is 158.68. Gross dollars 190.35 minus slippage 0.30, commission 0.15 and fees 1.00
gives net 188.90, net R `188.90 / 95.10 = 1.986330178759200841219768665`.

The second enters 20 shares at 150.01 with stop 145.07 and original risk 98.80.
Conservative daily stop-first execution yields gross -98.60, slippage 0.40,
commission 0.20, fees 1.00, net -100.20 and net R
`-100.20 / 98.80 = -1.014170040485829959514170040`. Both stop/target and entry/exit
ordering ambiguity flags remain true. These are engineering arithmetic examples,
not historical strategy performance; their cash balances must not be combined
as an invented portfolio.

Regression cases separately exercise order expiration before a later touch,
nonpositive stops, security reservation, identity mismatch, strict native-basis
rejection, unknown context, exact context cutoff, immutability, reproduction and
provider/network-free loading. Unsupported external cancellation is reported,
not simulated.

## Offline reproduction and artifacts

From the repository root (optional dependencies are needed only for generating
new synthetic/provider-normalized fixture inputs, not frozen loading):

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from pathlib import Path
from equity_research.ingestion.storage import encode
from equity_research.swing import Configuration, FAILED
with Path('/tmp/failed-breakout-config-new.json').open('xb') as f:
    f.write(encode(Configuration(FAILED).record()))
PY
PYTHONPATH=src .venv/bin/python -m equity_research.cli swing research \
  --study data/research_datasets/pr6b-goog-5b2nlv7-study-v2 \
  --context data/research_datasets/pr7a-market-jfyafm7i-context-v1 \
  --strategy-config /tmp/failed-breakout-config-new.json \
  --start 2024-01-02 --end 2026-10-20 --output /tmp/goog-failed-new
PYTHONPATH=src .venv/bin/python scripts/run_frozen_swing_study.py \
  --aapl-study data/research_datasets/pr6b-aapl-5b2nlv7-study-v4 \
  --goog-study data/research_datasets/pr6b-goog-5b2nlv7-study-v2 \
  --context data/research_datasets/pr7a-market-jfyafm7i-context-v1 \
  --output /tmp/pr7b-all-inventories-new
PYTHONPATH=src .venv/bin/python scripts/make_swing_strategy_example.py \
  --output /tmp/pr7b-synthetic-input-new
PYTHONPATH=src .venv/bin/python -m equity_research.cli swing replay \
  --data /tmp/pr7b-synthetic-input-new/data.csv \
  --manifest /tmp/pr7b-synthetic-input-new/manifest.json \
  --output /tmp/pr7b-synthetic-replay-new
.venv/bin/python -m pytest -q
```

Every output path must be unused. A research bundle contains the manifest,
configuration, setup observations, triggers, signals, provisional plans, context
links, exclusions, lifecycle outcomes, quality and provenance plus all embedded
study/context dependency bytes. `load_strategy(path)` verifies hashes, identities,
configurations and semantically recomputes outputs from embedded frozen inputs.
Source paths are provenance only, not loader dependencies. No cache pointer,
calendar regeneration, provider SDK, network, TWS or fallback is required. Given
the same input paths/bytes, configuration and implementation, repeated bundles
are byte-identical. Stable IDs hash security, price input, config, setup and trigger,
not wall-clock run times. No existing frozen input/run is overwritten.

## Limits and later work

Two selected stocks are not a historical investable universe. Corporate-action
and vendor-vintage completeness, verified dissemination and real execution basis
remain unresolved. Context has ETF proxies rather than constituent breadth or
historical setup share. Daily OHLC cannot determine true intraday ordering,
liquidity or real fills. Independent failed attempts overlap, and research counts
are sensitive to a declared setup definition without constituting optimization.

Future research can link the reserved outcome fields without changing causal
features, then study context-conditional outcomes with correlated-signal handling.
Separate geometry modules could later model Grimes pullbacks, Minervini VCP and
JLaw descending trendlines; none is implemented or labeled complete here.
PR 7C has not begun. No broker connection, vendor request, account query, order
submission, settings change, live/paper trade, optimization, deployment or merge
is part of PR 7B.
