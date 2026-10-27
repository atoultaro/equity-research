# Grimes management decisions: October 18–26, 2026

PR17 analyzes the complete PR16 discovery sample: 26 openings, 27 stop revisions,
seven underway transitions, 12 source DROPs and 14 source histories without an
observed closure. The [research report](reports/grimes-management-20261018-26/report.md)
contains every revision, transition and closure, matched ENTERABLE comparisons,
counterexamples, market context and links to all 26 individual stock summaries.
PLTR and PEP remain excluded. There is no PR8A dependency.

The authoritative task is the operator's **PR #17: Grimes Trade Management and
Decision Analysis**. Branch: `research/grimes-management-decisions-20261018-26-v1`.
Inspected merged main: `35f0a4b1f138b3606180a1b3ec29a049422f530e`.
Inspected PR16 head: `3a2fd4757a7bc81166b005dcbb1a5ffabf8d03b5`.

## What the sample supports

- **Source-only management asymmetry:** LONG revisions widen 10/16 times
  (62.5%); SHORT revisions widen 1/11 times (9.1%). All 11 widening revisions
  occur while ENTERABLE. The four revisions after UNDERWAY all tighten.
  These are source facts, independent of bar/stop compatibility.
- **Conditional progress:** 11/13 usable tightening revisions follow positive
  hypothetical price progress. HUM (−2.44%) and ELF (−0.93%) are counterexamples.
  AAPL widens once despite positive progress (+0.63%). Three tightening and
  seven widening observations lack usable current modeled exposure; none is
  silently counted as a loss, success or zero.
- **Conditional proximity:** 9/11 widening revisions have the reference Close
  within one native ATR of the prior stop, but CLMT and ELF provide counterexamples.
  This is quote proximity, including source/model conflicts, not post-exit
  position progress. Only EBAY has the inherited bounded primary corroboration.
- **No universal swing-level explanation:** only 9/25 usable revisions move
  toward the pre-existing direction-selected protective swing. Two revisions
  lack the necessary warmup. These agent-selected levels are not verified levels
  used by Grimes.
- **Underway:** six usable current-progress observations are favorable (6/6);
  CDE is unavailable because its conditional model has already exited at +1R.
  The October 22 AAOI/AMD/ANET/SNDK cluster follows one completed eligible session
  with favorable progress of 2.90%–5.89%, or 0.244–0.583 original hypothetical R.
  All four show the existing 20-session breakdown diagnostic and weak relative
  strength, but range contraction is mixed. Their shared publication and sector
  context form one cluster, not four independent confirmations of a rule.
- **ENTERABLE counterexamples:** the quartet's seven usable matched observations
  have median progress −0.27%; three are favorable despite remaining ENTERABLE
  at that horizon. AAPL, CDE and OMER show why favorable movement alone cannot
  define UNDERWAY. Different dates, sectors and directions confound comparison.
- **Exits:** all 12 actual source closure reasons remain unresolved. Under the
  inherited conditional model, nine have resolved stop observations, CAT/T have
  full SHORT +1R observations, and ASST has an unknown stop/target order.
  AAPL's earlier LONG +1R partial does not itself establish full closure.
  Earlier nonprogress flags for T, TEVA and AAPL are retained but cannot become
  terminal time-exit explanations after modeled price closure.

The report ranks at most three falsifiable hypotheses for an independent alert
sample: direction-associated widening, underway versus matched ENTERABLE progress,
and widening near a prior stop. None is a fitted Grimes algorithm or evidence of
a statistical edge. The next useful evidence is independent source/entry/revision
clocks and compatible units, not parameter optimization.

## Timing, units and censoring

Every event uses the instant immediately **before** PR16's existing effective
bound. Native daily bars require XNYS cash close +60 minutes strictly before
that instant. Intraday decisions cannot use that day's completed bar. Even the
future scenario entry price and original R are masked at an opening alert until
the entry session becomes observable.

The weekly exact publication timestamp remains null. PR16's explicitly enabled
email availability bound remains a separate modeling clock. Publication-based
duration is not actual holding duration. Known publication intervals yield
eligible-session ranges; unknown weekly timing has a separately labeled
conditional bracket using publication sequence and email availability. For
example, SNOW's opening-to-DROP interval is one session under the email bound
or one–two sessions under that conditional bracket. TEVA's weekly source DROP
is bracketed at four–five eligible sessions. Actual fill/exit times are unknown.

The latest stop first reported in the **same alert** is an observed decision
outcome, not information already available before publication. The feature table
keeps `stop_known_before_alert` separate from `latest_stop_in_source_sequence`.
For AAOI's transition these are 89.82 and 70.70 respectively.

Prices, moving averages and relative-strength measurements retain native PR16
provenance. SMA10 is a full-window arithmetic mean; SMA20/50, strict confirmed
pivots and ATR reuse existing features and the pinned shared mathematics. The
protective swing is fixed by direction and must already be confirmed by the
previous available session. It is never selected after seeing the new stop.
Separate native-price distances to both recent confirmed High and Low are also
reported. Those recent levels may be newly confirmed in the latest available
session; they do not become pre-existing levels for the stricter stop hypothesis.
Missing expected sessions/warmup remain unavailable; no forward fill occurs.

Source stop-change percentages and classifications are source-only arithmetic.
Native-price/stop comparisons require corroborated units in the primary view;
otherwise they remain explicitly conditional. Only 1/27 revision comparisons
(EBAY) has the PR16 bounded session-scale evidence. This is not a complete
corporate-action audit. TEVA's new ordinary-share identity, ASST's business/split
and sector cautions, SNDK's separated identity and earnings incompleteness remain
unchanged. Fixed sector proxies are agent choices, not historical ETF membership.

MFE is nonnegative favorable movement and MAE is nonnegative adverse movement,
both measured from the hypothetical Open. Progress is side-correct signed Close
movement. Original-R normalization always uses the initial stop; revisions never
reset it. ATR progress uses pre-entry ATR, while adjustment/proximity uses the
pre-decision ATR. Mathematical definitions are frozen in `methodology.json`.

The inherited native feature formulas remain those of
[MarketContext](MARKET_CONTEXT_INFRASTRUCTURE.md) and
[expert-comprehension features](EXPERT_TRADE_COMPREHENSION.md). With `C,H,L,V`
denoting completed native bars, their relevant definitions are:

| Measurement | Mathematical definition |
|---|---|
| SMA N and Close relationship | `SMA_N(t)=mean(C[t-N+1:t])`; `C(t)/SMA_N(t)-1` |
| MA slope and pair relationship | `SMA_N(t)/SMA_N(t-k)-1`; `SMA_fast(t)/SMA_slow(t)-1` |
| Daily / N-session return | `C(t)/C(t-N)-1`; requires N+1 consecutive observations |
| Realized volatility20 | Population standard deviation, ddof=0, of 20 simple daily returns; not annualized |
| Shared simple ATR14 | Mean of 14 `max(H-L, abs(H-C_prev), abs(L-C_prev))` ranges; requires 15 bars and calls the pinned wheel |
| Relative strength / participation | `(C_stock/C_proxy)(t)/(C_stock/C_proxy)(t-N)-1` on the same ordered dates |
| Confirmed swing | A strict High/Low against three bars on each side, with the third following bar establishing confirmation |
| Confirmed-level distance | `C-level`; percent `100*(C/level-1)`; ATR units `(C-level)/ATR14` |
| Breakout / breakdown20 | Close above the preceding20-session maximum High / below preceding20-session minimum Low |
| Single-bar failed breakout | Current High > preceding20-session maximum High > current Close |
| Support / resistance rejection | `Low<=pre-existing swing Low<Close` / `High>=pre-existing swing High>Close` |
| Range / contraction | `(max(H)-min(L))/C`; contraction compares last20 range to last60, or last10 to the nonoverlapping previous20 |
| Other retained window levels | `max(H)` / `min(L)`; Close/high−1 and Close/low−1 use those window extremes |
| Native volume diagnostics | `V(t)/mean(previous20 V)` and `mean(last20 C*V)`; volume units remain unverified and do not estimate position size |

Geometry flags are agent-selected measurements, not documented Grimes entry or
management rules. Warmup and missing-session checks apply separately to every
window, including fields retained from the parent feature inventory.

An entire modeled price-exit or ambiguous-exit day is excluded from exposure
MFE/MAE: its High/Low/Close may occur after the exit. Earlier full-session paths
are retained as **pre-exit summaries**, never substituted for current progress
at a later decision. An already observed resolved target may provide a lower
bound of +1R without inventing the full exit-day excursion. A source DROP is not
known before its own bound; a fully available RTH bar may precede an after-hours
source closure. No actual executions, sizes, costs or realized P&L are inferred.

EBAY remains source OPEN after its 119.20→117.50 revision. Its modeled original
episode is closed under PR16's timing/session-scale assumptions, so current
progress is unavailable and no re-entry is created. The 117.87 Low remains a
market observation, not a position's post-stop MAE.

## Comparisons and confounding

For an H-session transition, ENTERABLE controls use their own first alert
opportunity after the Hth completed eligible session, before H+1 opens, and no
later than the target transition bound. State includes all co-published source
actions. It does not filter on later final outcomes. Every other source position
remains in the 25-candidate exclusion ledger, with explicit eligibility/reason.
Closed/ambiguous model paths cannot provide current exposure. The quartet
reuses the same seven controls; it does not create 28 independent comparisons.

Market tables distinguish original commentary, observed SPY/QQQ/RSP/IWM returns,
trend/volatility, participation proxies, and agent interpretation. Of 27 source
revisions, 17/27 coincide with negative SPY days; those revisions occupy only six
alert bounds. Six of seven underway transitions share one weak/volatility-expanding
snapshot. Event-weighted rates are not independent samples. RSP/SPY is a proxy;
true breadth remains unavailable. Stale Databento ES history is not used.

## Immutable outputs and offline reproduction

Authoritative parent:
`runs/grimes-lifecycle-20261018-26-v1/study-v5`, SHA-256
`4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604`.

PR17 study:
`runs/grimes-management-20261018-26-v1/study-v2`, SHA-256
`fb2fd81dc3eeef6b10a185057930776a1534230a3534d63793d72d3e257342ca`.

The earlier `study-v1` remains preserved at
`a818e4d670230b1ede7001e036b9e002f8d4b19a8eccc7e7d4246ae069c871e0`;
v2 adds the complete native swing-distance inventory and closure-path display.

The study contains all 72 decision rows, stop/underway/closure comparisons,
matched-control exclusion ledgers, 26 position summaries, long/short comparisons,
market clusters, relationships with counterexamples, definitions, commentary,
26 Markdown summaries and the comprehensive report. It embeds the sealed full
parent with source proofs and records source/code/shared-dependency hashes.
Every load independently validates PR16 semantic outputs and recomputes PR17
outputs. Resealing altered output records cannot bypass validation.

```bash
equity-research management study \
  --parent runs/grimes-lifecycle-20261018-26-v1/study-v5 \
  --config experiments/grimes-management-20261018-26-v1.json \
  --output runs/my-grimes-management-study-v1

equity-research management replay \
  --study runs/grimes-management-20261018-26-v1/study-v2 \
  --output runs/my-grimes-management-replay-v1
```

Use unused output directories. These commands are offline and require the local
frozen bundle. Subscriber originals and native frames remain in ignored local
storage; public Markdown copies contain derived facts and paraphrased commentary.
PR16's reader, source records, frozen reports, adapter, execution accounting and
price policies remain unchanged. No acquisition, account action, new dataset,
CI workflow, strategy engine or predictive model is added.

## Validation

Complete local regression suite: `.venv/bin/python -m pytest -q` →
**533 passed in 110.05s (0:01:50)**. The 26 added cases cover scope/counts,
direction-aware excursions and scale normalization, stops, strict availability,
future-entry masking, fixed original R, source/model separation, missing/basis
uncertainty, pre-existing pivots, weekly time, source closure censoring, no
post-exit exposure, controls/denominators, immutable replay and resealed semantic
corruption in both parent and child outputs. No test requires a broker connection.

- Offline replay with socket connect/connect_ex/create_connection denied is byte-identical to the final study: `fb2fd81dc3eeef6b10a185057930776a1534230a3534d63793d72d3e257342ca`.
- **1348 frozen PR16 files checked; zero changed.** Its original bundle remains `4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604`.
- All 27 public Markdown files match their frozen generated originals byte-for-byte.
- Local immutable verification: `runs/grimes-management-20261018-26-v1/verification-v1`, SHA-256 `5df2c982d7f23a16b121be3095d12474b7e038c973fb221f9cb39b53beadb9ea`.
- `git diff --check` passed; no GitHub Actions workflow is introduced.
