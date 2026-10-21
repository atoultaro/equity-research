# First swing research slice — policy long_trend_breakout_v1

This is one offline candidate, one security, one long configuration and one replay.
It addresses Q2 qualification and Q3 execution mechanics, not profitability. Latest
project PR4 instructions supersede older two-style milestone schedules. No broker,
vendor adapters, Minervini template, relative-strength model, fundamental analysis,
portfolio machinery, partial exits or trailing stops are implemented.

## Modules

| Module | Responsibility |
| --- | --- |
| `models.py` | Aware observation/availability timestamps, validated configuration, Decimal conversion |
| `data.py` | CSV/hash validation and explicit session schedule; raw prices only |
| `qualification.py` | Independent SMA/rising/ATR/liquidity decision with as-of timestamps |
| `strategy.py` | Fixed trigger/stop/order activation and expiration plan |
| `execution.py` | Daily opening/touch events and full exits; no network path |
| `accounting.py` | Integer sizing, cash/notional cap, costs and immutable original-risk R |
| `reporting.py`, `cli.py` | Captured immutable inputs, code/dependency identity, artifacts and command |

Shared `true_range` and `atr_simple_last` come from the pinned market_shared wheel;
SMA is the only new indicator math. There is no new backtesting framework dependency.

## Data and supported sessions

CSV columns must be exactly `symbol,session_date,open,high,low,close,volume`.
One row must exist for every manifest session in ascending order for one symbol;
no sort, merge, duplicate removal, forward fill or imputation happens silently.
Prices must be finite, positive and consistent; volume finite and nonnegative.
The manifest must hash the original CSV bytes and record source/revision/version,
creation timestamp (null means unknown), raw adjustment convention, empty corporate
actions, exchange/timezone, calendar version and explicit session timestamps.
The example also records its known authoring date; no retrieval time is invented.

Supported schedules are caller-supplied XNYS/America_New_York dates, weekday open
09:30 ET and close16:00 or explicit13:00 ET early close. ZoneInfo resolves DST.
Bar completion is close; per-session `available_at` must be at/after close and
before the next listed open. Offsets and local dates/hours are validated. There
is **no exchange-calendar library**: the caller must supply an authoritative
complete schedule for real research. Validation catches absent CSV sessions
relative to that list, not a missing session omitted from both list and CSV.
Holidays are never inferred by creating weekday bars. The committed example is
an explicitly labeled synthetic schedule, not licensed historical market data.

Adjusted data and any declared split/dividend/rename/delisting/corporate action
cause input rejection. CSV extra action columns are also rejected. “No actions”
is a source attestation; the program cannot discover unreported events from prices.
Prices and indicators use the same raw basis. Real data must be audited accordingly.

## Candidate and qualification timing

Manual input requires symbol, source, observed_at, available_at, candidate_session,
setup_family and provenance. Observation describes the original observation, not
the vendor's unpublished execution time. Availability cannot precede observation;
candidate session cannot follow its ET observation date. Publication timestamps
are not manufactured. A kind (`synthetic` or `recorded_observation`) and nonempty
reference are required to qualify. User-supplied recorded observations are labeled
not independently verified. Non-manual sources are recorded but rejected as
unsupported. No DeepVue/Mantis/Grimes historical membership or ratings are inferred.

One decision is evaluated at candidate availability using only bars through its
signal session that were available by then. Later known sessions do not revise the
signal. The candidate must be observed after that signal session closes and the
signal bar must be available. Features carry decision_at, feature_asof_ts and last
completed session. Insufficient history is WATCH, not a pass. No later automatic
requalification of WATCH candidates occurs in this slice.

Defaults: close>SMA50; SMA50 above its value5 sessions earlier; positive simple
ATR14; mean volume over20 sessions≥100,000. At least max(50+5,14+1,20)=55 history
bars are needed. ATR uses gap-aware shared true ranges and a simple average, not
Wilder smoothing; it is consumed only after full history despite the shared
function's partial-window capability. SMA uses a full window via statistics.mean.
Rule failures return machine reasons; low liquidity/unsupported source/provenance
are REJECT, trend/history/volatility conditions are WATCH, all passes ELIGIBLE.
These thresholds are research hypotheses, not statements of predictive value.

## Entry, exits and ordering

1. Trigger=signal high+buffer(default$0.10), rounded up to the configured price grid
   ($0.01). Initial stop=signal close−2×ATR, rounded down. It must be positive and
   below trigger. Both are fixed from completed information.
2. Order activation is the first listed session strictly after the signal date
   with open≥candidate availability. If information arrives after a session opens,
   the entire session is skipped; daily OHLC cannot justify an earlier/open fill.
3. Only active-session high can trigger. Reference entry=max(open,trigger);
   actual entry adds fixed adverse per-share slippage(default$0.01). Quantity is
   sized then using that executable price, never that day's close. Unfilled order
   expires after3 eligible sessions, including the third close. If data ends before
   that count it is UNFILLED_END_OF_DATA. Unknown future expiration timestamp stays
   null; no future calendar date is invented.
4. On a held position, open≤stop exits at open minus slippage. Open≥target exits at
   open minus slippage. Known opening events precede the later daily range.
5. Otherwise, stop touch is low≤stop; target touch is high≥target. If both touched,
   use stop first and set stop_target_ambiguous. A target is a modeled market-on-touch
   exit, not a guaranteed limit-price fill. Exit slippage is charged on every exit.
6. Same-day entry/exits are supported conservatively. An intraday-triggered entry
   cannot exit at the earlier open. If that day's low touched stop, assume a stop
   after entry and flag entry_exit_order_ambiguous; the low might actually predate
   entry. Stop/target collision has its own flag. No actual intraday path is claimed.
7. Fixed target(default2R) uses actual entry plus2×original actual per-share risk,
   rounded up once. No trailing, partial exit or stop change is supported.
8. Maximum holding(default10) includes entry session as1; if no earlier price exit,
   liquidate at that session's close minus slippage. End of data similarly forces
   full liquidation at final observed close, explicitly labeled end_of_data. This
   terminal assumption is not a promise of an executable last-ever market price.

Open/close fills have exact declared time. Intraday fills have a session-wide
window with timing=intraday_order_unknown, not an invented clock timestamp. The
model ignores spread/liquidity/volume participation and does not guarantee fills.
If adverse slippage would create a nonpositive fill, the configuration/data model
is invalid and execution fails explicitly.

## Sizing, dollars and reproducibility

Risk budget=initial equity×risk fraction(default$10,000×1%=$100). Quantity is floor
of budget/(actual entry−initial stop), capped by cash including entry commission
and fees and optional maximum actual position notional. Integer shares, multiplier1,
no minimum share, no leverage. Invalid stops or zero affordable quantity reject the
trade. The gap's actual entry risk can reduce size. Cash is one initial cash balance;
there is no concurrent allocation or portfolio ledger.

Initial risk dollars=(actual entry−initial stop)×quantity, before fees, saved once.
Gross PnL uses reference fill prices before modeled slippage. Modeled slippage is
the sum of per-side reference-to-actual degradation. Price PnL after slippage is
also recorded. Net=gross−slippage−commission−fees; realized R=net/original risk.
Default commission$0.005/share/side and fees$0.50/order, separately reported. There
is no broker-specific fee rounding. Decimal precision28 controls replay arithmetic;
indicators use shared binary float math. R never means an unplaced reference stop.

Artifacts preserve all input bytes, configuration, policy/code revision and actual
code hash, shared artifact identity, result and hashes. No wall clock/random path
appears in canonical artifacts. A run uses an exclusive new directory; reusing an
existing directory is an error. Qualification rejection, WATCH and unfilled/expired
outcomes remain visible with a header-only trade CSV. Invalid datasets/configs
fail before creating a completed run; they are not converted into no-trade evidence.

Source SHA is read from the equity checkout, with a dirty flag and installed source
hash. Outside the checkout, --source-commit is required and explicitly labeled
user_supplied; the system does not claim to verify that asserted Git history.
Artifact hashes exclude their own file; the bundle hash covers the ordered hash
map. Same source/runtime/config/input bytes produce byte-identical canonical artifacts
in different run directories. Source changes legitimately change hashes.
