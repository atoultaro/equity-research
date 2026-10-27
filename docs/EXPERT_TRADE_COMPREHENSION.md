# Expert trade comprehension — October 26, 2026 amendment

PR #15 analyzes the four operator-provided Adam Grimes **OPEN_NEW_POSITION**
recommendations: SAIL LONG stop 20.90, SLB LONG stop 51.10, GE SHORT stop 295.80 and
SCCO SHORT stop 191.70. “Added” means newly opened, never increased holdings.
[Original wording and recommendation input](../experiments/grimes-20261026-observations-v1.json)
are unchanged. Actual entry prices, execution times, quantities, individual targets,
trade-specific exit instructions and executed exits remain unknown.

Read the [corrected four-stock report](reports/GRIMES_20261026.md). The
[original v2 report](reports/GRIMES_20261026_V2.md), all frozen captures and prior
local study bundles remain preserved. The amendment uses existing IBKR prices
entirely offline: no broker connection, download, order, account query or simulator
change was made.

## Facts, observations and interpretations

Structured outputs and report sections distinguish:

| Attribution | Meaning |
| --- | --- |
| `EXPERT_REPORTED` | Direction, new-position action and stop reported by the operator; not independently verified |
| `MARKET_OBSERVED` | Historical OHLCV measurements from frozen provider captures, under documented basis and availability assumptions |
| `RESEARCH_HYPOTHESIS` | Competing explanations, researcher-defined alignment and invalidation candidates, and optional reference arithmetic; not expert intent |

The separate current methodology has source status **OPERATOR_REPORTED**. It is
not upgraded to an independently observed exit instruction for any individual trade.

The research cutoff remains **2026-10-26 17:00 America/New_York / 21:00 UTC**.
Completed-session availability is reconstructed as cash close +60 minutes, as in
existing MarketContext. This does not establish recommendation or execution time.
October 27 observations cannot enter these features. Captured-vintage data may
contain revisions and is not proof of the original historical dissemination vintage.

## Correct return horizons and independent QQQ verification

All return calculations require the full ordered calendar window of n+1 observations:

`return_n = Close(t) / Close(t − n completed trading sessions) − 1`.

No missing bar or insufficient lookback is silently skipped, compressed or filled.
The explicit keys are `daily_return`, `return_5d`, `return_20d`, `return_60d`, with
horizon, required-observation count, first/last sessions and fraction units. Legacy
`return1/5/20/60` keys remain aliases for compatibility; new report/comparison
headings state horizons and display percentages. Moving averages, ATR, volatility,
drawdown and 5/20/60/120-session evolution remain available.

| October 26 market proxy | Daily return (1 session) | Trailing 5-session return | Trailing 20-session return | Trailing 60-session return |
| --- | ---: | ---: | ---: | ---: |
| SPY | +0.710554% | −0.144818% | −0.031348% | +2.455055% |
| QQQ | +1.107325% | −0.857509% | −3.303328% | +3.518946% |
| RSP | +0.346356% | +1.822868% | +3.599695% | +1.060416% |
| IWM | +0.449683% | +2.104836% | −1.082066% | −4.879808% |

Independent Decimal arithmetic divides the original frozen canonical closes,
without reusing the feature-calculation function:

- **QQQ daily:** October 23 Close 704.40 → October 26 Close 712.20 gives
  **+1.107325383304940374787052800%**. The preceding completed session is Friday
  October 23, not the intervening weekend. This rounds to +1.11% at two decimals.
- **QQQ trailing 20 sessions:** September 28 Close 736.53 → October 26 Close 712.20
  gives **−3.303327766689747871777117020%**.

The daily difference from the operator's approximately +1.10% is **+0.0073253833
percentage points**. The trailing-20 difference from the previous report's −3.30%
is **−0.0033277667 percentage points**. Both are within the explicitly recorded
0.01-percentage-point approximation tolerance. Both horizons are valid; −3.30%
is not October 26's daily return. No user approximation replaces an IBKR close.
`return_validation.json` retains exact fractions, percentages, dates, source-row
locators, basis, comparison provenance and discrepancy status. Larger discrepancies
remain visible as `DISCREPANCY_REQUIRES_REVIEW`.

## Competing setup hypotheses

The old closing-breakdown-plus-SMA50 detector is a **researcher-defined diagnostic**,
not a documented Grimes requirement. The amendment removes the automatic
`inferred_setup` classification and leaves `intended_expert_setup` null. Multiple
hypotheses are preserved in `research_setup_hypotheses`, including unresolved ones.

The retained diagnostics have precise definitions:

- Breakout: current Close exceeds the previous 20 completed-session Highs.
- Breakdown: current Close falls below the previous 20 completed-session Lows.
- Single-bar failed breakout: current High exceeds those prior Highs and Close
  returns below that boundary.
- Legacy composites additionally use SMA50, or upward-trend MA proximity within
  one ATR. They remain named researcher parameters, not claimed expert rules.
- Trend context: Close/SMA50−1, SMA50 slope over 20 sessions and trailing 20-session
  price return are all positive or all negative. Continuation is a compatible
  hypothesis without requiring a fresh 20-session closing extreme.
- Support/resistance rejection: current Low/High touches or crosses a pre-existing
  strict three-neighbor confirmed swing Low/High and Close returns to its opposite
  side. Pivot confirmation must strictly precede the current session; only bars
  through each snapshot are used.

Interpretations considered are continuation, pullback/recovery, failed rally or
breakout, support/resistance rejection, potential second leg and other/uncertain.
There is **no second-leg detector**: an ordered impulse/pullback/renewal structure
has not been validated here, and two declines alone do not establish one. The
report never claims Grimes uses these parameters or assigns his intended setup.

The four observed cases retain distinct tensions:

- **SAIL:** positive trend/momentum and strong SPY/QQQ-relative performance can be
  consistent with a LONG continuation hypothesis despite the intraday rejection
  above the previous 20-session High. Both interpretations remain represented;
  the rejection alone neither identifies intent nor invalidates the LONG.
- **SLB:** bullish MA-proximity supports investigating recovery/pullback, while
  trailing 20-session stock/XLE ratio change is −8.0735%. Recovery need not mean
  absolute energy-sector leadership. The actual entry/path remains unverified.
- **GE:** measured bearish trend context supports a continuation hypothesis even
  without a fresh 20-session closing breakdown. Failed rally and second leg remain
  unresolved rather than being asserted from the recommendation's direction.
- **SCCO:** trailing 20-session stock/SPY ratio change is −8.1734%, while stock/COPX
  is +6.0383%. That mixed peer evidence remains explicit. No unique setup or private
  motive is manufactured.

## Stop interpretation and operator-reported 1R methodology

Stop analysis separates the **nearest numerical technical level** from
**directionally relevant invalidation candidates**. LONG candidates are measured
support below reference Close: swing lows, prior 20-session lows and applicable
moving averages. SHORT candidates are resistance above reference Close: swing
highs, prior 20-session highs and applicable moving averages. Each candidate records
absolute/ATR-normalized distance and whether the reported stop lies strictly below
support or above resistance. A nearest swing low is not automatically a SHORT
invalidation level. These are candidate proxies, not demonstrated expert stop logic.

The separate versioned
[methodology specification](../experiments/grimes-current-methodology-v1.json)
records the operator's current convention:

| Direction | At +1 original R | Remaining position | Unknown details |
| --- | --- | --- | --- |
| SHORT | Close 100% | No runner | Pre-target/subsequent management not independently observed |
| LONG | Close at least 1/3 of original size | Allow remaining position to run | Exact fraction, remaining fraction, stop adjustments, final exit rules and timing |

The LONG exact fraction is null, not fixed at 1/3; its remaining fraction is also
null, not assumed 2/3. Effective date is unknown. Application to these four positions
is the operator's stated current methodology, not observed per-trade exit evidence.

For LONG, `R = E − S`, `target_1R = E + R`. For SHORT, `R = S − E`,
`target_1R = E − R`. R must be strictly positive. Unknown actual E leaves actual
R and target unknown. Quantities, actual initial-dollar risk and P&L are not computed.

The optional `--close-reference-1r` scenario records
`reference_entry_basis=OCT_26_CLOSE`, `is_actual_execution=false`,
`hypothetical_1R_target`, the operator profit-taking convention and `actual_target=null`.
It assumes compatible price units only for arithmetic; reported-stop adjustment
basis remains unverified. Invalid/nonpositive reference R leaves that scenario
unavailable, without declaring the actual recommendation invalid.

| Symbol | Hypothetical entry: October 26 Close | Reported stop | Hypothetical per-share R | Hypothetical +1R target | Actual target |
| --- | ---: | ---: | ---: | ---: | --- |
| SAIL LONG | 21.75 | 20.90 | 0.85 | 22.60 | UNKNOWN |
| SLB LONG | 53.08 | 51.10 | 1.98 | 55.06 | UNKNOWN |
| GE SHORT | 288.43 | 295.80 | 7.37 | 281.06 | UNKNOWN |
| SCCO SHORT | 186.01 | 191.70 | 5.69 | 180.32 | UNKNOWN |

These are reference scenarios, never verified actual entry/target prices, fills,
executed exits or hypothetical portfolio performance.

## ES coverage and remaining data limits

The preserved Databento ES source is important for future historical regime
research going back to 2010. The **last verified locally available session is
2026-05-04**, with inspected file timestamp bounds May 3 18:00 through May 4 15:59 ET.
The source hash remains
`a5cb59c37ac932628479a1be6d0871094b5a6b7588af13eb4e6f95cc07b02d6e`.
The missing study interval is **May 5–October 26, 2026**, covering **121 XNYS
cash-session reference dates**. This is not a futures ETH completeness assertion.
The [amendment evidence](../experiments/grimes-20261026-amendment-v1.json) records
that boundary and the scope of verification. Original ES metadata, roll/adjustment
uncertainties and source hashes remain embedded without revision. No continuous
futures reconstruction, extrapolation, new download or automatic recent-IBKR-futures
replacement occurs. October 26 broad-market context uses SPY/QQQ/RSP/IWM.

All original IBKR history remains unchanged: 16 qualified identities, 18,547 selected
observations, 1,208 sessions per full 2022-01-03–2026-10-26 slice, and 427 sessions
for the current SAIL listing beginning 2025-02-13. SAIL's three-year target remains
unmet. GE's pre-separation history is not constant-business aerospace history.
Native TRADES is documented split-adjusted, not dividend-adjusted or verified raw
execution prices. Native volume units and historical publication clocks remain
unverified. No forward fill, basis mixing or ticker-history splice is performed.

Dated issuer/regulator evidence and analyst proxy mappings are preserved in the
[original research specification](../experiments/grimes-20261026-research-v1.json).
They are not licensed historical GICS or ETF membership. Event publication
availability remains UNKNOWN_OR_MISSING where exact dissemination times were not
verified; SEC acceptance and retrieval clocks are not substituted. Corporate-action,
macro and industry-news completeness, actual executions and private motives remain
unknown. The simulator and accounting policies are unchanged.

## Immutable versions, source identity and validation

| Artifact | Canonical bundle SHA256 |
| --- | --- |
| Original source inputs-v1 | `01968c15438d78b47217d1402e95cb4b097eea297c0b5aef2921e8903e0e8a49` |
| Original study-final-v2, preserved | `762e71789143e4f19ec6f3f9e2e8b7155131febefe1cca86eb7f4eb2addf7e85` |
| Amended study-v3 and offline replay | `9a999268979d7199caa7776b200283aeb70a1058b2476e875b31cee2eba8ef54` |
| Effective amended embedded inputs | `a740d10a34cb3b7115bd57c4fccad6a2f820d3726b55db48f996a232fe6c7f7f` |

New local root: `runs/grimes-amendment-20261026-v1/`. The 23 sealed study members
include the original requested outputs, four dossiers, new `expert_methodology.json`,
`trade_management.json`, `return_validation.json`, unchanged source input bytes,
methodology/amendment/options input bytes and input seals. The source-parent hash
is explicitly linked and verified. Loading recomputes all derived JSON and Markdown
from frozen native frames and rejects semantically altered, even resealed, outputs.
Hashes establish integrity, not provider authenticity.

The original report commit inspected for this amendment is
`dff09c2bc87f40b571e295761de44aa730cee9d6`; existing PR15 branch is
`research/grimes-trade-comprehension-20261026-v1`. Earlier inspected commits remain
main/merged PR14 `0b4be335e53e646e4de0216d307607810434280d`, PR14 head
`c85a8c731915f7fc102feda28f6928df23a428cd`, and read-only shared finwhaling/ibkr-data
checkout `57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`. No external finance repository
was changed. The unchanged pinned shared ATR and existing MarketContext mathematics
remain the calculation sources. Python and implementation hashes are pinned per study.

Final offline suite: **478 passed in 85.46s (0:01:25)**, no skips, using
`.venv/bin/python -m pytest -q`. Twenty amendment cases cover attribution, return
horizons, October 23→26 alignment, missing lookback, future poisoning, independent
return reconciliation/discrepancy handling, LONG/SHORT 1R arithmetic, unknown actual
targets, minimum-versus-exact exit fractions, directional levels, causal pivot
confirmation, stale ES and deterministic semantic validation. Prior regressions
remain included. `git diff --check` passes. Replay is independently checked with
sockets and acquisition-library imports denied; all bytes and the bundle hash match.
All 7,003 inventoried pre-existing fixture/data/audit/study files remain unchanged.

## Exact offline regeneration

Use the existing pinned development environment and optional data dependencies
from README. No brokerage library, TWS, original cache or live request is needed.
Every command requires a new output directory.

Rebuild the amended study from unchanged source inputs plus the two new versioned
specifications, explicitly enabling the optional hypothetical scenario:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli expert study \
  --inputs runs/grimes-comprehension-20261026-v1/inputs-v1 \
  --methodology experiments/grimes-current-methodology-v1.json \
  --amendment experiments/grimes-20261026-amendment-v1.json \
  --close-reference-1r --output /tmp/grimes-amended-study-v3
```

Replay the new self-contained bundle without any of those original paths:

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli expert replay \
  --study runs/grimes-amendment-20261026-v1/study-v3 \
  --output /tmp/grimes-amended-replay-v3
```

Omit `--close-reference-1r` to leave hypothetical targets disabled. Omitting the
methodology input leaves conventions explicitly unavailable; it never silently
assumes exact one-third exits. The current reader pins the new implementation:
reproducing an original v2 output requires the preserved original code at
`dff09c2bc87f40b571e295761de44aa730cee9d6`, rather than treating new code as identical.

A clean synthetic example is still available without local licensed captures:

```bash
PYTHONPATH=src .venv/bin/python scripts/make_comprehension_example.py \
  --output /tmp/grimes-synthetic-example-v3
```

The synthetic example provides arithmetic and artifact evidence only, never an
expert selection edge, actual execution or historical stock performance claim.
