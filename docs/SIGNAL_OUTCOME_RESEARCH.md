# Signal-outcome measurement and market-context research — PR 7C

PR 7C measures subsequent price paths after the original PR 7B signals. It asks
whether direction-aligned movement persists, how excursions evolve across horizons,
how reference timing changes the measurement, and what the captured context can
support descriptively. It does not turn a signal into an order or a hypothetical
reference into a fill. It does not fit models, optimize parameters, alter detection,
choose a regime gate, reconstruct screening membership or establish an edge.

Authoritative task: PR 7C. Branch: `research/signal-outcomes-v1`. Inspected base is
`e8c76038cbbcf00766cfc78f03e02da5c699ddda`, merged PR 7B #10. Earlier one-policy
AGENTS guidance remains the strict replay boundary; this authorized additive
research analysis consumes both existing strategy inventories without execution.

## Architecture, input identities and immutable results

`outcomes/model.py` defines `outcome_definitions_v1`, `signal_outcome_v1` and the
pure `measure` function. `outcomes/analysis.py` defines deterministic dependence
diagnostics, grouped summaries and paired-reference comparisons. `outcomes/dataset.py`
provides `FrozenSignals`, `freeze_outcomes` and `load_outcomes`. `outcomes/cli.py`
registers the explicit offline `outcomes` command.

The consumer supports the common `swing_research_v1` / `swing_signal_v1` inventory
schema, with arbitrary compatible strategy identities rather than hardcoded
AAPL/GOOG signal counts. It validates original signal/setup/trigger identities,
configuration and component hashes, stock/security identity, frozen calendar,
corporate-event lineage and captured context links. Duplicate original signal IDs
across input bundles fail explicitly; distinct overlapping attempts remain distinct.
Strategies for one security must use the same price/calendar/context vintage.

PR 5 supplies canonical stock prices and exact dataset hashes; PR 6 supplies the
frozen expected calendar, event inventory, source assertions and retrospective
alignment. PR 7A's original context bytes and PR 7B's original signals, signal-time
ATR and context links are consumed directly. The reader deliberately avoids
`load_strategy`, whose validation reruns detection. It never calls detection,
recomputes ATR or invokes `context_as_of` with a new cutoff. Source rules, PR 4
execution/accounting, PR 6 publication policies and PR 7A context are unchanged.

Existing immutable storage and embedded-dependency verification are reused.
Input strategy bundles are embedded as content-addressed byte blobs with original
member maps and full hash records. Identical dependency bytes are stored once.
An outcome bundle contains definitions, manifest, complete original signal
inventory/context links, outcomes, corporate-action annotations, dependence
clusters, reference comparisons, descriptive summaries, quality and provenance.
Loading verifies byte hashes and identities and recomputes only outcome semantics
from captured inputs. It requires no original source path, mutable cache,
exchange-calendar regeneration, provider SDK or network. Same inputs/config/code
produce identical canonical outputs. Existing output directories cannot be reused.

## Reference, return and path definitions

Let t be the completed signal session and e the first expected regular session
whose **Open timestamp is strictly after signal availability**. A signal available
exactly at a session's Open cannot use that Open. Expected session indexing comes
from the embedded calendar, preserving holidays, DST and early closes.

| Reference | Price P | Horizons | Endpoint | Excursion sessions |
| --- | --- | --- | --- | --- |
| SIGNAL_CLOSE | Close[t] | 1, 5, 10, 20 | Close[t+h] | t+1 through t+h, excluding all signal-day High/Low |
| NEXT_ELIGIBLE_OPEN | Open[e] | 0, 1, 5, 10, 20 | Close[e+h] | e through e+h, including the reference session |

The Close is a signal observation reference. The next Open is a retrospective
hypothetical reference; there is no assumption of a fill at either price.
Every row records the exact signal, reference, first eligible and endpoint sessions.

- Raw stock return percent: `100 * (endpoint Close / P - 1)`.
- Direction-normalized return: raw for LONG, negative raw for SHORT.
- Entry gap percent: `100 * (Open[e] / Close[t] - 1)`. This is not slippage.
- LONG favorable price excursion: `max(0, max(window High) - P)`;
  adverse excursion: `max(0, P - min(window Low))`.
- SHORT favorable excursion uses the same downward magnitude; adverse excursion
  uses the same upward magnitude.
- `MFE_pct` / `MAE_pct` are `100 * excursion / P`.
- `MFE_ATR` / `MAE_ATR` are `excursion / original signal features.atr14`.

Excursions are nonnegative magnitudes. The original ATR14 must have a nonfuture
signal-time observation cutoff and be positive/finite. It is never recomputed
using future bars. ATR units are not realized R. Daily High/Low order remains
UNKNOWN; no stop, target, borrow, short financing, fee, slippage, cash or P&L
sequence is inferred. Direction-normalized SHORT movement is a signed underlying
stock move, not an exact short-sale return or evidence of shortability.

## Completeness, unavailable data and quality

A price-path result requires every expected session from reference through endpoint,
a valid signal reference, matching security and price hashes, valid OHLCV and an
observed endpoint. An intermediate hole is MISSING_EXPECTED_SESSION; missing tail
coverage is INSUFFICIENT_FUTURE_COVERAGE. Missing next-open references, invalid
prices/references and mismatched input identities are explicit. No row is skipped
to compress a horizon, forward filled, or silently extended with new prices.
A missing long horizon does not remove shorter complete horizons or the signal.

AVAILABLE means the price path and ATR-normalized metrics are complete.
UNAVAILABLE means price-path measurements are null with precise reasons.
PARTIAL retains valid returns and percent excursions but null ATR units and
MISSING_SIGNAL_ATR when original normalization evidence is absent/nonpositive.
Summary available counts refer to valid price paths, with fully available and
partial-ATR counts reported separately. Each metric reports its valid sample size.
There are no PARTIAL rows in the actual demonstration.

Native IBKR TRADES split-adjusted price semantics, unverified volume units and
independently unverified basis are copied exactly. Returns are native-price
comparisons, not raw execution-grade returns, cash-dividend-adjusted total returns
or mechanically adjusted dividend effects. The vendor's historical price-vintage
and dissemination archive remains unverified.

Corporate annotations are retrospective **outcome quality only**, excluded from
signal-time inputs. They reuse PR 6's distinction between sourced effective actions,
bounds that might intersect and globally unknown ex-dates. Close-reference action
windows exclude the signal day; Open-reference windows conservatively include
the opening reference session. A flag does not establish causal attribution or a
mechanical adjustment effect. Verified dates with conflicting/unverified alignment
remain uncertain. Record/payment dates never substitute for ex-dates. Complete
source events and unresolved fields remain embedded.

Each row retains known-action and bounded-uncertainty lists, global unknown-date
references and archive completeness UNKNOWN. Sensitivity summaries separately
exclude known/bounded comparability flags without deleting raw signals or outcomes.
Unbounded unknown ex-dates do not become fabricated window overlaps or exclusions.
The actual inventory has 11 unresolved AAPL and nine unresolved GOOG ex-dates;
one GOOG dividend has a source-supported effective date. No known/bounded action
intersects the configured actual outcome windows. That does not establish a
complete action archive or certify the native price basis.

## Captured market context and dependence

Original context links are retained byte-for-value, including bundle hash,
reference-set identity, session/availability, continuous SPY/QQQ/RSP features,
optional state, missing breadth/leadership and reconstructed dissemination caveats.
The reader validates the recorded context's membership and strict timing against
its original frozen bundle, without selecting a different snapshot. UNAVAILABLE
stays unavailable. An available snapshot lacking an optional descriptor is
UNDESCRIBED, distinct from unavailable context. No state suppresses observations.

Dependency intervals are closed intervals from each signal session to its longest
requested expected outcome endpoint across both references. They include unavailable
paths and are explicitly marked if the frozen calendar truncates a requested end.
Per-security connected components of intersecting intervals form event clusters,
across strategies; a chain-connected cluster does not require all members to
mutually overlap. IDs depend deterministically on their original signal members.
Same-security/same-session clusters, setup/attempt lineage, original boundaries
and direct overlapping signal IDs are also retained. Clustering never deletes
signals and is a diagnostic, not a proof that different clusters are independent.
Broad-market and cross-security time dependence remains.

Descriptive groups retain strategy, security, direction, horizon, reference type,
context descriptor and availability. They report counts, missing reasons, raw and
direction-normalized mean/median/population standard deviation, positive/negative/
zero counts, median excursions and ATR units, and cluster counts. A fixed default
warning threshold of ten available event clusters is an engineering visibility
rule, not a significance or power threshold. Smaller groups remain visible with
INSUFFICIENT_EVENT_CLUSTERS; all groups retain dependence/native-basis warnings.
No confidence intervals, fitted models, significance tests or causal effects are
claimed. Configurable horizons are integers through 252 sessions; defaults were
specified before measuring actual outcomes.

## Actual complete inventories

The fixed source interval is 2024-01-02 through 2026-10-20, 703 actual sessions per
stock. All 42/37 continuation LONG and 29/20 failed-breakout SHORT signals remain.
There are 1,152 signal/reference/horizon rows: 1,147 AVAILABLE, five UNAVAILABLE,
zero PARTIAL. Every unavailable row has INSUFFICIENT_FUTURE_COVERAGE:

- AAPL continuation: all Close horizons have 42/42; Open horizons 0/1/5/10 have
  42/42 and Open20 has 41/42.
- GOOG continuation: all Close/Open horizons have 37/37.
- AAPL failed breakout: Close1/5/10 and Open0/1/5/10 have 29/29; Close20 and Open20
  each have 27/29. The two missing horizons are retained for both signals.
- GOOG failed breakout: every horizon has 20/20.

All 128 original context links remain available under the reconstructed assumption:
127 UPTREND, one MIXED (GOOG continuation), zero DOWNTREND/UNCLASSIFIED/unavailable.
All retain seven missing optional breadth/leadership features. There is no defensible
regime comparison with one MIXED signal and no other regime observations.

| Security | Raw signals | Same-session clusters | Event clusters | Signals with overlaps | Largest event cluster |
| --- | ---: | ---: | ---: | ---: | ---: |
| AAPL | 71 | 65 | 11 | 69 | 18 |
| GOOG | 57 | 57 | 11 | 54 | 15 |
| Total | 128 | 122 | 22 | 123 | 18 |

Strategy-specific available cluster counts are AAPL continuation 7, GOOG
continuation 7, AAPL failed 10 and GOOG failed 11. Components shared across
strategies must not be added to estimate a population size. The two continuation
groups trigger the default insufficient-cluster warning even though their raw
signal counts exceed ten.

The following tables cover **every** default horizon/reference; no favorable
signals are selected. Values are percentages unless labeled ATR, rounded here to
three decimals; exact Decimal summaries, missing reasons and context strata are
in the aggregate evidence. C means continuation LONG, F means failed breakout SHORT;
Close means SIGNAL_CLOSE and Open means NEXT_ELIGIBLE_OPEN. `n` is available/original.

### Return summaries

| Stock | Setup | Ref | h | n | Raw mean % | Direction mean % | Direction median % | Direction stddev % | Clusters |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| AAPL | C | Open | 0 | 42/42 | 0.022 | 0.022 | -0.011 | 0.999 | 7 |
| AAPL | C | Open | 1 | 42/42 | 0.167 | 0.167 | 0.197 | 1.385 | 7 |
| AAPL | C | Open | 5 | 42/42 | -0.033 | -0.033 | 0.659 | 3.629 | 7 |
| AAPL | C | Open | 10 | 42/42 | 0.022 | 0.022 | 1.642 | 5.286 | 7 |
| AAPL | C | Open | 20 | 41/42 | -1.123 | -1.123 | -0.490 | 6.433 | 7 |
| AAPL | C | Close | 1 | 42/42 | 0.068 | 0.068 | -0.006 | 1.138 | 7 |
| AAPL | C | Close | 5 | 42/42 | -0.139 | -0.139 | 0.719 | 3.548 | 7 |
| AAPL | C | Close | 10 | 42/42 | 0.264 | 0.264 | 1.394 | 4.603 | 7 |
| AAPL | C | Close | 20 | 42/42 | -1.075 | -1.075 | -1.088 | 6.509 | 7 |
| GOOG | C | Open | 0 | 37/37 | -0.003 | -0.003 | -0.005 | 1.525 | 7 |
| GOOG | C | Open | 1 | 37/37 | 0.129 | 0.129 | 0.341 | 2.606 | 7 |
| GOOG | C | Open | 5 | 37/37 | 1.631 | 1.631 | 1.106 | 5.019 | 7 |
| GOOG | C | Open | 10 | 37/37 | 3.102 | 3.102 | 1.571 | 7.234 | 7 |
| GOOG | C | Open | 20 | 37/37 | 4.271 | 4.271 | 2.591 | 11.051 | 7 |
| GOOG | C | Close | 1 | 37/37 | 0.118 | 0.118 | -0.158 | 1.946 | 7 |
| GOOG | C | Close | 5 | 37/37 | 1.483 | 1.483 | 0.987 | 4.888 | 7 |
| GOOG | C | Close | 10 | 37/37 | 3.118 | 3.118 | 2.636 | 6.703 | 7 |
| GOOG | C | Close | 20 | 37/37 | 4.004 | 4.004 | 2.997 | 10.858 | 7 |
| AAPL | F | Open | 0 | 29/29 | 0.251 | -0.251 | 0.008 | 1.167 | 10 |
| AAPL | F | Open | 1 | 29/29 | 0.145 | -0.145 | -0.495 | 2.340 | 10 |
| AAPL | F | Open | 5 | 29/29 | 0.227 | -0.227 | -0.485 | 3.470 | 10 |
| AAPL | F | Open | 10 | 29/29 | 0.598 | -0.598 | -1.150 | 4.762 | 10 |
| AAPL | F | Open | 20 | 27/29 | -0.146 | 0.146 | 2.769 | 7.085 | 10 |
| AAPL | F | Close | 1 | 29/29 | -0.062 | 0.062 | -0.160 | 1.949 | 10 |
| AAPL | F | Close | 5 | 29/29 | 0.103 | -0.103 | 0.496 | 3.959 | 10 |
| AAPL | F | Close | 10 | 29/29 | -0.266 | 0.266 | 0.507 | 5.416 | 10 |
| AAPL | F | Close | 20 | 27/29 | -0.732 | 0.732 | 3.144 | 7.094 | 10 |
| GOOG | F | Open | 0 | 20/20 | -0.062 | 0.062 | -0.009 | 1.369 | 11 |
| GOOG | F | Open | 1 | 20/20 | 0.318 | -0.318 | -1.019 | 2.723 | 11 |
| GOOG | F | Open | 5 | 20/20 | -0.548 | 0.548 | 0.688 | 4.178 | 11 |
| GOOG | F | Open | 10 | 20/20 | 0.733 | -0.733 | -0.673 | 5.844 | 11 |
| GOOG | F | Open | 20 | 20/20 | 0.342 | -0.342 | -1.082 | 9.083 | 11 |
| GOOG | F | Close | 1 | 20/20 | 0.367 | -0.367 | 0.027 | 2.260 | 11 |
| GOOG | F | Close | 5 | 20/20 | 0.123 | -0.123 | 1.014 | 4.880 | 11 |
| GOOG | F | Close | 10 | 20/20 | 1.513 | -1.513 | -1.151 | 6.495 | 11 |
| GOOG | F | Close | 20 | 20/20 | 0.799 | -0.799 | -1.504 | 9.519 | 11 |

### Median excursion summaries

| Stock | Setup | Ref | h | MFE % | MAE % | MFE ATR | MAE ATR |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| AAPL | C | Open | 0 | 0.762 | 0.671 | 0.365 | 0.352 |
| AAPL | C | Open | 1 | 1.302 | 1.097 | 0.630 | 0.593 |
| AAPL | C | Open | 5 | 2.132 | 1.882 | 1.173 | 0.849 |
| AAPL | C | Open | 10 | 3.719 | 2.237 | 1.866 | 0.913 |
| AAPL | C | Open | 20 | 4.876 | 4.370 | 2.691 | 1.904 |
| AAPL | C | Close | 1 | 0.779 | 0.552 | 0.432 | 0.340 |
| AAPL | C | Close | 5 | 2.114 | 1.657 | 1.208 | 0.688 |
| AAPL | C | Close | 10 | 3.594 | 2.050 | 1.859 | 0.885 |
| AAPL | C | Close | 20 | 4.509 | 4.283 | 2.432 | 1.925 |
| GOOG | C | Open | 0 | 1.163 | 1.107 | 0.425 | 0.429 |
| GOOG | C | Open | 1 | 1.731 | 1.286 | 0.673 | 0.590 |
| GOOG | C | Open | 5 | 2.875 | 2.283 | 1.325 | 0.939 |
| GOOG | C | Open | 10 | 4.687 | 2.638 | 2.201 | 1.025 |
| GOOG | C | Open | 20 | 7.289 | 4.095 | 2.855 | 1.813 |
| GOOG | C | Close | 1 | 0.855 | 1.217 | 0.308 | 0.533 |
| GOOG | C | Close | 5 | 3.137 | 1.788 | 1.299 | 0.778 |
| GOOG | C | Close | 10 | 4.710 | 2.185 | 2.104 | 0.797 |
| GOOG | C | Close | 20 | 7.532 | 3.282 | 3.780 | 1.396 |
| AAPL | F | Open | 0 | 0.669 | 0.749 | 0.312 | 0.448 |
| AAPL | F | Open | 1 | 1.106 | 1.361 | 0.581 | 0.707 |
| AAPL | F | Open | 5 | 2.271 | 2.976 | 0.971 | 1.299 |
| AAPL | F | Open | 10 | 2.848 | 3.630 | 1.483 | 1.713 |
| AAPL | F | Open | 20 | 5.518 | 5.063 | 2.765 | 2.183 |
| AAPL | F | Close | 1 | 0.714 | 0.858 | 0.360 | 0.360 |
| AAPL | F | Close | 5 | 2.242 | 2.301 | 1.093 | 1.199 |
| AAPL | F | Close | 10 | 3.079 | 3.143 | 1.548 | 1.744 |
| AAPL | F | Close | 20 | 5.187 | 4.517 | 2.724 | 1.991 |
| GOOG | F | Open | 0 | 0.780 | 0.704 | 0.297 | 0.279 |
| GOOG | F | Open | 1 | 0.921 | 1.828 | 0.465 | 0.820 |
| GOOG | F | Open | 5 | 2.973 | 2.527 | 1.286 | 1.092 |
| GOOG | F | Open | 10 | 3.311 | 3.964 | 1.492 | 1.696 |
| GOOG | F | Open | 20 | 6.021 | 5.400 | 2.569 | 2.566 |
| GOOG | F | Close | 1 | 0.637 | 1.036 | 0.260 | 0.391 |
| GOOG | F | Close | 5 | 2.540 | 2.441 | 1.355 | 1.095 |
| GOOG | F | Close | 10 | 2.860 | 3.480 | 1.355 | 1.484 |
| GOOG | F | Close | 20 | 6.007 | 5.246 | 2.380 | 2.553 |

### Controlled reference comparisons

Each comparison uses the same original signals and the same endpoint. Close h=5
therefore compares with Open h=4 for ordinary next-session availability, rather
than Open h=5. Only signals with both complete paths contribute; unmatched signals
remain in the main inventory. Entry gaps are reported on that same paired set.

| Stock | Setup | Close h / Open h | Pairs | Mean entry gap % | Direction Close-minus-Open pp |
| --- | --- | --- | ---: | ---: | ---: |
| AAPL | C | 1 / 0 | 42 | 0.046 | 0.046 |
| AAPL | C | 5 / 4 | 42 | 0.046 | 0.042 |
| AAPL | C | 10 / 9 | 42 | 0.046 | 0.042 |
| AAPL | C | 20 / 19 | 42 | 0.046 | 0.046 |
| GOOG | C | 1 / 0 | 37 | 0.134 | 0.121 |
| GOOG | C | 5 / 4 | 37 | 0.134 | 0.116 |
| GOOG | C | 10 / 9 | 37 | 0.134 | 0.120 |
| GOOG | C | 20 / 19 | 37 | 0.134 | 0.151 |
| AAPL | F | 1 / 0 | 29 | -0.309 | 0.313 |
| AAPL | F | 5 / 4 | 29 | -0.309 | 0.316 |
| AAPL | F | 10 / 9 | 29 | -0.309 | 0.297 |
| AAPL | F | 20 / 19 | 27 | -0.322 | 0.324 |
| GOOG | F | 1 / 0 | 20 | 0.428 | -0.429 |
| GOOG | F | 5 / 4 | 20 | 0.428 | -0.448 |
| GOOG | F | 10 / 9 | 20 | 0.428 | -0.461 |
| GOOG | F | 20 / 19 | 20 | 0.428 | -0.441 |

For a common endpoint and raw fractional returns, the identity is
`1 + r_close = (1 + entry_gap) * (1 + r_open)`. The denominator change means a
reference difference is not simply a fixed gap subtraction. SHORT sign-normalized
comparisons invert the raw difference. The 20-session AAPL-failure comparison uses
27 paired signals, so its gap mean differs from the 29-signal shorter comparisons.

Strategy contrasts use matched reference/horizon definitions, retaining security,
direction, counts and cluster counts. Their signal populations are **unpaired**;
there is no claim that the two strategies triggered on identical dates. At the
20-session Close endpoint, continuation's normalized mean is -1.075% for AAPL and
+4.004% for GOOG, while failed breakout is +0.732% and -0.799% respectively. Those
different stock-specific patterns preclude a broad strategy conclusion. They come
from only two selected securities, few overlapping event clusters and almost
entirely one context state. Averages are descriptive, not independent-trial
estimates, causal regime effects, realized returns or a performance ranking.
All exact conditional strata, including the single MIXED observation, remain in
the aggregate evidence with sample-size warnings. No threshold or filter was
selected from these results.

## Offline reproduction

Use the existing local inputs from PR 7B. The command accepts repeated immutable
inventory paths, optional horizons/reference conventions and the warning threshold.
The evaluation window comes from the original inventories and is never extended.
A missing dependency fails explicitly; no acquisition or synthetic substitution
occurs. Example (every output name must be unused):

```bash
PYTHONPATH=src .venv/bin/python -m equity_research.cli outcomes \
  --strategy data/research_datasets/pr7b-swing-6k_eq8qj-v2/aapl-breakout_continuation_v1 \
  --strategy data/research_datasets/pr7b-swing-6k_eq8qj-v2/aapl-failed_breakout_v1 \
  --strategy data/research_datasets/pr7b-swing-6k_eq8qj-v2/goog-breakout_continuation_v1 \
  --strategy data/research_datasets/pr7b-swing-6k_eq8qj-v2/goog-failed_breakout_v1 \
  --output /tmp/signal-outcomes-new
```

Defaults are Close1/5/10/20 and Open0/1/5/10/20. For a deliberately narrower
measurement, append `--references open --horizons 0 1 5` and use another new output
path. This changes outcome definitions, not original detection or signal IDs.
`--minimum-clusters 10` is the default visibility warning threshold.

```python
from equity_research.outcomes import load_outcomes
research = load_outcomes('/tmp/signal-outcomes-new')
print(research.content_sha256)
print(research.results['quality_report.json'])
```

Source and output bundle hashes, exact aggregate metrics, preservation checks and
test results are recorded in
[evidence/signal-outcome-research-v1.json](evidence/signal-outcome-research-v1.json).
Licensed row-level prices, original signals, window endpoints and outcomes remain
local in ignored research storage. Committed tables contain aggregates only.

## Final artifact and verification

Implementation commit: `7ccec23c17091ded432cf360e7ff92aef530a00f`.
The final self-contained bundle is
`data/research_datasets/pr7c-outcomes-cy8dhfxk-v2`. The preliminary v1 bundle
remains preserved; all outcome, signal, context, cluster, comparison, definition
and summary records are semantically identical. Only implementation provenance
changed after final identity-validation checks were committed.

| Source or output | Bundle SHA256 |
| --- | --- |
| AAPL continuation signals | `4c499694c32d69b367a198dc7668936ae437e21be93d881a05dc26875e23a40a` |
| AAPL failed-breakout signals | `97da500b27f13380902b487e4996d871fb4497fde389f3f4b2e755288138dcd7` |
| GOOG continuation signals | `0368acdf9268020dece37e859d75099ec5f5c322007ed5e63abb34bec3e4f3e9` |
| GOOG failed-breakout signals | `78c054ac03ef2c95278876974fd852c0abda2d8ef04947a0535afe15bc86aefe` |
| Final combined outcomes v2 | `adc2f662c42b5199ff01c7810d205794a9e8418c19496b1f1660144e30fb978a` |

Exact stock-price, event-study, context, configuration, component and baseline
hashes accompany the aggregate evidence. The captured MarketContext hash remains
`d9a5547daf856364fdb398431ce17498d26c039ff926d44016bc4f5a9cddf271`.
All 1,045 pre-existing cache/research files retain their starting hashes; original
PR 4–7B execution, history, event, market-context and strategy modules are unchanged.

Final command: `.venv/bin/python -m pytest -q`.
Result: **400 passed in 74.47s (0:01:14)**, zero failures/skips, including all 336
prior cases and 64 new outcome cases. Core-only installation, SDK/provider/swing
import-denied frozen loading, no-regeneration/no-context-lookup spies, immutable
byte reproduction, input-order independence and semantic tamper rejection passed.
`git diff --check` passed. An independent source-price Fraction calculation
checked every available return, excursion and ATR unit (1,147 rows), all 36
stock/strategy/reference/horizon return means/medians and excursion medians; it
also verified all five unavailable paths and the independent overlap graph.
All 128 original signals and captured context links compare exactly with inputs.

## Scope and next research requirements

The initial population is AAPL and Alphabet Class C GOOG in roughly three years,
with no historical investable-universe reconstruction. Means are sensitive to
which stock and overlapping windows enter a group. Same-session duplicates and
larger clusters cannot supply independent precision. Unverified price vintages,
native basis, corporate-event completeness, dissemination and seven missing
optional context features constrain interpretation. No information here verifies
stock borrow, fills, fees or executable returns.

Larger-universe research would need independently supported point-in-time
membership, prices and event evidence, broader context-state coverage, prespecified
measurement policies and dependence-aware inference. Changes to detection,
thresholds, execution or prediction require separate work. PR 7D has not begun.
No broker connection, vendor request, account/position query, order, trade,
settings change, optimization, deployment, finwhaling modification or merge occurs
in this PR.
