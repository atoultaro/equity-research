# Grimes reconstruction findings: October 18–26, 2026

The strongest finding is that our assumed execution and management conventions explain the discrepancies better than treating the source ledger as wrong. CDE's continued management contradicts a mandatory full +1R exit under the conventional next-Open entry; EBAY's old hard stop is genuinely crossed under the examined already-active entries, while a later review convention can preserve the source sequence. Neither result identifies Grimes' actual fills or policy.

The comparison covers all 26 episodes and all 72 source actions. Source states remain 14 OPEN and 12 CLOSED, including CDE SHORT / OPEN / UNDERWAY / 13.90 and EBAY LONG / OPEN / ENTERABLE / 117.50. Four October 26 additions have concrete prospective hypotheses but no observed execution window before the fixed October 26 data cutoff. The other 22 have at least one observed, geometrically admissible candidate. Three clock schedules × four entry hypotheses produce 312 candidate records; these are repeated hypotheses, not 312 trades or independent samples.

Use the [leading-scenario table](GRIMES_RECONSTRUCTION_LEADING_SCENARIOS_20261018_26.md), [machine-readable comparisons](../evidence/pr9a-reconstruction-v1/episodes.json), [adjustment diagnostics](GRIMES_PRICE_VOLUME_DIAGNOSTICS_20261018_26.md) and [method](../GRIMES_RECONSTRUCTION_METHOD.md). The generated episode appendix below retains the complete source sequence, every candidate and policy comparison. “Leading” means best under the declared compatibility/simplicity ordering, not observed, probable or uniquely identified.

## What the comparisons change

1. **A full +1R exit is too restrictive as a universal interpretation.** CDE's October 19 Open reference 15.46 with opening stop 16.40 has 0.94 per-share reference risk (about 1.217 ATR). Its +1R price is 14.52; October 22 Open 14.51 already passes that level before the evening UNDERWAY transition. Full realization conflicts with continued source management. A partial runner and holding with reported stops both retain compatible exposure; source actions cannot distinguish their sizes. Simplicity ranks holding above an assumed 50% partial, but that is an ordinal preference, not evidence that no partial occurred.

2. **EBAY's discrepancy survives the weekly timing alternatives.** Friday Open 120.84, Monday Open 121.24 and the conditional Friday Close 121.41 all expose a previously active long to October 26 Low 117.87 below the then-known 119.20 stop. None of these references reaches its +1R price first in the available intervening bars. The evening revision to 117.50 cannot retrospectively change a hard-stop outcome. The retained conId-matched nominal Low anchor corroborates 117.87 for that session. Price-only scaling sufficient to avoid the stop contradicts that anchor. A Close-review/next-Open convention remains pending at the sample end and can use the evening revision prospectively; it is a different, unverified management convention. A later intraday execution or other discretionary behavior needs better timing evidence. No reentry is invented.

3. **Shorts are not uniformly tighter when risk is measured from plausible entries.** The per-episode midpoint of the conditional reference-risk range has a median of approximately 1.405 ATR for 10 usable shorts versus 0.973 ATR for 12 usable longs. These are selected, unmatched hypotheses, not actual risk. Same-alert H1 comparisons expose the counterexamples: October 20 additions ASST/OMER are about 0.284/0.707 ATR versus 0.884–1.340 for the three longs; October 21 additions AAOI/AMD/ANET/SNDK are 1.491–1.860 ATR versus GME 0.836. The direction pattern reverses between alerts. This challenges extrapolating PR17's stop-to-quote geometry into a general claim about executed short risk.

4. **Tight risk can express an immediate-movement hypothesis, but does not establish it.** The four smallest observed late-clock H1 risks are AAPL 0.266, ASST 0.284, CAT 0.310 and SNOW 0.343 ATR. Their first-session directional Open-to-Close quote changes are respectively +0.323, −1.470, +0.459 and −0.586 ATR. Two move favorably and two adversely. These are quote changes, including prices after any hypothetical exit, not held-position returns. They support investigating immediate follow-through without proving either intent or an edge.

5. **Widening usually accompanies adverse or entry-sensitive quote progress here, with a clear exception.** Of 11 widening revisions, ten have an adverse or entry-sensitive directional difference across the constructed entry references; AAPL's first widening on October 19 occurs after favorable +2.16 quote progress. Of 16 tightening revisions, 12 have favorable progress across references; T's October 21 change and GTLB's October 26 change depend on entry reference, while HUM's October 22 tightening and ELF's weekly tightening occur with adverse quote progress under the late clock. Thus “widen only losers” and “tighten only winners” both fail. No counterfactual quote progress is relabeled as exposure after a model exit.

6. **UNDERWAY is consistent with established movement, not an execution instruction.** All seven transitions have favorable quote differences across the available prior entry references in the late-clock comparison. T's first transition has only +0.05 native price units, while the tech shorts on October 22 have larger movement. This does not identify a common +1R threshold, trigger price, partial realization or entry time. Same-alert stop changes and transitions are clustered rather than counted as independent confirmations. ENTERABLE remains compatible with the source reporting an open episode and later changing its stop.

7. **DROPPED is not a known exit reason.** The 12 closed episodes remain in every output. For CAT, full +1R can precede the reported DROP while holding can remain active until it; the source cannot select a realized cause. For ASST, daily stop/target order changes a full-exit explanation. For several tightly trailed tech shorts, the hard-stop convention can end a hypothetical path before the next DROP without contradicting any intervening source continuation. The ranking nevertheless favors a path still active at the DROP when that supplies another compatible source observation. That scoring choice must not be mistaken for proof of discretionary exit timing. Exact exit price, cause and realized P&L remain unknown.

## Structure and entry selection

Long pullback/compression and short continuation are useful candidate descriptions, not documented universal Grimes rules. In the late-clock pre-alert diagnostics, AAPL, CLMT, GME and SLB are within one ATR of SMA20/50 (4/14 longs). Seven of 13 longs with sufficient warmup have a 10-session/previous-20 range ratio below one; TEVA lacks that warmup. HUM, SIG and MMM are counterexamples to a simple compression description. The daily compression ratio is an agent-defined test, not a quoted Grimes setup definition.

Only CAT, AAOI and GE meet all three declared downtrend conditions (3/12 shorts); T and SNOW meet the separate bounce-within-downtrend description. None of the 12 short opening snapshots satisfies the narrow same-bar failed-20-session-breakout or closing-breakdown diagnostic. That rejects those exact definitions as universal explanations, not the broader possibility of a prior failed rally or multi-bar continuation. CAT's confirmation and GME's pullback can tie their next-Open alternatives; many other confirmation/pullback candidates are untriggered, geometrically invalid or right-censored. Absence of a modeled trigger never means no actual source trade occurred.

Stop proximity is heterogeneous. Opening HUM stop 404 is about 0.020 ATR from the pre-alert SMA20, and SNOW's 330.70 about 0.055 ATR from SMA50; by contrast EBAY's opening stop is over 1.5 ATR from even the nearest measured level in its late-clock construction snapshot. Such proximity supports structural placement as a candidate explanation in specific cases, not a blanket moving-average stop rule. Signed distances to all measured MAs, pivots and consolidation boundaries are retained for every episode, avoiding selection of only the closest favorable level. Nearness to a non-protective swing is not itself support/resistance evidence.

## Prospective cases at the sample boundary

SAIL, SLB, GE and SCCO were added after the final observed session. H1 references the October 27 Open with price unknown; H2 is rejected because October 26 Close precedes publication. Pre-alert H3 reference levels are SAIL 22.30 (last completed High), SLB 53.45 (prior20 High), GE 284.57 (last completed Low) and SCCO 180.82 (prior20 Low). SLB also has a causal H4 SMA50 pullback reference 52.4592 between Close and stop 51.10; the other three lack a valid level under the fixed H4 definition. These are concrete trigger hypotheses with a fixed three-session horizon, not actual executions or recommendations. Later opening gaps, revised stops or absent triggers could change the hypothetical outcome. No post-cutoff bars are imported or invented.

## Shared market context

The preserved PR17 market snapshots show QQQ down about 2.859% and SPY down 1.181% on October 22, when six UNDERWAY transitions and eleven stop revisions are co-published. Five short transitions accompany favorable stock quote movement; AAPL is the long transition. This is consistent with managing established moves during broad weakness, but does not separate stock structure from regime response. The same alert also widens ELF/GME/TEVA and tightens HUM: a single market event does not imply one universal stop response. The late weekly snapshot uses Friday prices conditionally; the early clock must instead use Thursday prices. Per-decision relative returns and pre-alert levels are available in the machine report. These shared shocks and co-published decisions are not independent evidence samples.

## What remains unresolved

The simple holding policy leads ten late-clock episodes; deferred Close-review/next-Open leads twelve, with several entry ties. Four episodes cannot rank because the execution window is beyond the cutoff. The deferred-review prevalence demonstrates how strongly hard-stop versus review conventions affect source compatibility; it does **not** establish that Grimes used that policy. The review model deliberately adds flexibility and is penalized, but compatibility is ranked before that penalty. Equal source-observation signatures are reported separately from ordinal rankings; many full/partial/holding explanations cannot be distinguished by this short source sequence.

Daily extrema order sometimes changes an individual hypothetical stop/target outcome. It does not remove CDE's +1R/continued-management discrepancy or EBAY's already-active hard-stop breach. Exact entry timing, intervening alerts, contemporaneous chart annotations and a stated stop/partial-exit convention would be more informative than fitting extra parameters to these bars. Four next-session additions require later data; this task does not acquire it.

AAPL and GOOG split windows corroborate native split adjustment: post-split Open/pre-split Close ratios are about 1.022 and 1.006 rather than approximately 1/4 and 1/20. Undoing only the documented split component produces 0.256 and 0.050, respectively. The observed five-session median native-volume ratios of 1.409 and 1.822 do not identify shares, lots or volume adjustment factors. No raw price/volume history, dividend convention, dollar-volume eligibility or complete action inventory is claimed. ASST's longer identity/scale history and TEVA's limited local warmup remain particular limitations.

No existing source ledger, published status table, execution simulator, universe implementation or frozen research output is revised. This is a conditional explanation of a source-selected 26-episode sample, with no performance or population inference.

## Validation and preservation

Final command: `.venv/bin/python -m pytest -q`; result: **657 passed in 655.66s (0:10:55)**. Final local study `runs/grimes-reconstruction-20261018-26-v1/study-v4` has SHA-256 `a1524b3f07d04bce4e5165ad3d6b3eccfa72ce32d41ca80ebbbf051725310315`; all 135 members replay byte-for-byte. All 67848 pre-existing runs/data/reports files are unchanged. The published status CSV remains `a32c812f95a51a56dc90fd8f49634b4976cd7f175fb1b326faf773ff22e4c527`. See [sealed validation](../evidence/pr9a-reconstruction-v1/validation.json) for the baseline inventory hash and limits. Native proof and full subscriber bodies remain local.

---

## Generated comparison appendix

# Grimes reconstruction: October 18–26, 2026

Conditional system identification over 26 source episodes, not observed execution or a strategy backtest. The source ledger remains authoritative: 14 OPEN, 12 CLOSED. Exact fills, sizes and realized P&L are unknown. Daily OHLC paths describe possibilities, not probabilities. All references assume native price/nominal stop compatibility except bounded corroborating quote anchors.

## Leading explanations

Rank vectors minimize continuation-conflict alert clusters, then maximize compatible later alert clusters, then prefer fewer extra management conventions, then construction support. Final source OPEN counts as a continuation constraint, not an independent later alert. Co-published actions count once. A leading scenario can still conflict with evidence; no score is a probability. Right-censored or untriggered entries cannot win through absence of evidence. Equal observation signatures remain equivalent even when simplicity breaks a ranking tie.

| Symbol | Reported direction/status/setup/stop | Leading late-bound reference | Compatibility vector | Other clocks |
|---|---|---|---|---|
| AAPL | LONG / CLOSED / UNDERWAY / 344.70 | H1_NEXT_OPEN 2026-10-19 @340.780, CLOSE_REVIEW_NEXT_OPEN | [0, -5, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| CLMT | LONG / CLOSED / ENTERABLE / 53.02 | H1_NEXT_OPEN 2026-10-19 @57.470, CLOSE_REVIEW_NEXT_OPEN | [0, -3, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| TEVA | LONG / CLOSED / ENTERABLE / 39.05 | H1_NEXT_OPEN 2026-10-19 @41.420, CLOSE_REVIEW_NEXT_OPEN | [0, -3, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| CAT | SHORT / CLOSED / ENTERABLE / 748.75 | H1_NEXT_OPEN 2026-10-19 @739.500, HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION 2026-10-19 @728.690, HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2]; [0, -1, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS, H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS, H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS |
| CDE | SHORT / OPEN / UNDERWAY / 13.90 | H1_NEXT_OPEN 2026-10-19 @15.460, HOLD_WITH_REPORTED_STOPS | [0, -3, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| T | SHORT / CLOSED / UNDERWAY / 22.20 | H1_NEXT_OPEN 2026-10-19 @23.250, CLOSE_REVIEW_NEXT_OPEN | [0, -3, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| ELF | LONG / OPEN / ENTERABLE / 109.20 | H1_NEXT_OPEN 2026-10-21 @115.310, HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| HUM | LONG / OPEN / ENTERABLE / 408.10 | H1_NEXT_OPEN 2026-10-21 @431.520, HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| SIG | LONG / OPEN / ENTERABLE / 112.50 | H1_NEXT_OPEN 2026-10-21 @115.770, HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| ASST | SHORT / CLOSED / ENTERABLE / 28.45 | H1_NEXT_OPEN 2026-10-21 @27.900, CLOSE_REVIEW_NEXT_OPEN | [0, -1, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| OMER | SHORT / OPEN / ENTERABLE / 17.35 | H1_NEXT_OPEN 2026-10-21 @16.570, HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| GME | LONG / CLOSED / ENTERABLE / 24.40 | H1_NEXT_OPEN 2026-10-22 @26.000, CLOSE_REVIEW_NEXT_OPEN; H4_PULLBACK 2026-10-22 @25.582, CLOSE_REVIEW_NEXT_OPEN | [0, -3, 2, -2]; [0, -3, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN, H4_PULLBACK/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN, H4_PULLBACK/CLOSE_REVIEW_NEXT_OPEN |
| AAOI | SHORT / CLOSED / UNDERWAY / 70.70 | H1_NEXT_OPEN 2026-10-22 @72.330, CLOSE_REVIEW_NEXT_OPEN; H3_CONFIRMATION 2026-10-22 @72.330, CLOSE_REVIEW_NEXT_OPEN | [0, -2, 2, -2]; [0, -2, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS, H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN, H3_CONFIRMATION/CLOSE_REVIEW_NEXT_OPEN |
| AMD | SHORT / CLOSED / UNDERWAY / 519.35 | H1_NEXT_OPEN 2026-10-22 @523.110, CLOSE_REVIEW_NEXT_OPEN | [0, -2, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| ANET | SHORT / CLOSED / UNDERWAY / 175.20 | H1_NEXT_OPEN 2026-10-22 @178.500, CLOSE_REVIEW_NEXT_OPEN | [0, -3, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| SNDK | SHORT / CLOSED / UNDERWAY / 1296.00 | H1_NEXT_OPEN 2026-10-22 @1317.260, CLOSE_REVIEW_NEXT_OPEN | [0, -2, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| ABBV | LONG / OPEN / ENTERABLE / 276.30 | H1_NEXT_OPEN 2026-10-26 @287.050, HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| CNQ | LONG / OPEN / ENTERABLE / 53.30 | H1_NEXT_OPEN 2026-10-26 @54.590, HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| EBAY | LONG / OPEN / ENTERABLE / 117.50 | H1_NEXT_OPEN 2026-10-26 @121.240, CLOSE_REVIEW_NEXT_OPEN | [0, -1, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| GTLB | LONG / OPEN / ENTERABLE / 52.10 | H1_NEXT_OPEN 2026-10-26 @56.400, HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| MMM | LONG / OPEN / ENTERABLE / 169.90 | H1_NEXT_OPEN 2026-10-26 @175.000, HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS |
| SNOW | SHORT / CLOSED / ENTERABLE / 330.70 | H1_NEXT_OPEN 2026-10-26 @324.700, CLOSE_REVIEW_NEXT_OPEN | [0, -1, 2, -2] | EARLY_BEFORE_FIRST_OPEN: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; FIRST_SESSION_CLOSE_COMPATIBLE: H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN |
| SAIL | LONG / OPEN / ENTERABLE / 20.90 | No observed comparable entry | censored | EARLY_BEFORE_FIRST_OPEN: unranked; FIRST_SESSION_CLOSE_COMPATIBLE: unranked |
| SLB | LONG / OPEN / ENTERABLE / 51.10 | No observed comparable entry | censored | EARLY_BEFORE_FIRST_OPEN: unranked; FIRST_SESSION_CLOSE_COMPATIBLE: unranked |
| GE | SHORT / OPEN / ENTERABLE / 295.80 | No observed comparable entry | censored | EARLY_BEFORE_FIRST_OPEN: unranked; FIRST_SESSION_CLOSE_COMPATIBLE: unranked |
| SCCO | SHORT / OPEN / ENTERABLE / 191.70 | No observed comparable entry | censored | EARLY_BEFORE_FIRST_OPEN: unranked; FIRST_SESSION_CLOSE_COMPATIBLE: unranked |

## Timing and interpretation

Known alerts use their displayed minute bounds; their earlier RTH Close cannot be an execution after publication. The weekly source publication remains UNKNOWN. Conditional source-order/email bounds span Thursday evening through Sunday morning. EARLY_BEFORE_FIRST_OPEN tests Friday entry, LATE_EMAIL_BOUND tests Monday entry, and FIRST_SESSION_CLOSE_COMPATIBLE tests a Friday-close reference. These boundary clocks do not exhaust every possible intraday publication. The four Monday-evening additions require Tuesday bars absent from this fixed study.

## Stop geometry and decision patterns

All diagnostic definitions are agent-specified hypotheses, not documented Grimes entry rules. Twenty-session extrema, SMA distances, confirmed pivots and range ratios use only completed, available bars. ATR comes from the project's pinned shared mathematics. Reference risk uses the stop reported before hypothetical activation; the opening stop is also retained. It never resets after entry. Intraday candidate risk ranges span compatible OHLC references, without asserting executable slippage bounds.

- LONG: 14 episodes; 12 with conditional risk references; median episode midrange 0.973 ATR; stop changes {'WIDENING': 10, 'TIGHTENING': 6}. This mixes setups and is not a matched causal comparison.
- SHORT: 12 episodes; 10 with conditional risk references; median episode midrange 1.405 ATR; stop changes {'TIGHTENING': 10, 'WIDENING': 1}. This mixes setups and is not a matched causal comparison.

Same-opening-alert H1 comparisons (shared information clock, not matched volatility/structure):

- alert-1: LONG: AAPL 0.266 ATR, CLMT 1.097 ATR, TEVA 0.902 ATR; SHORT: CAT 0.310 ATR, CDE 1.217 ATR, T 1.149 ATR
- alert-3: LONG: ELF 1.254 ATR, HUM 1.340 ATR, SIG 0.884 ATR; SHORT: ASST 0.284 ATR, OMER 0.707 ATR
- alert-4: LONG: GME 0.836 ATR; SHORT: AAOI 1.860 ATR, AMD 1.691 ATR, ANET 1.491 ATR, SNDK 1.561 ATR
- alert-6: LONG: ABBV 1.480 ATR, CNQ 0.920 ATR, EBAY 0.582 ATR, GTLB 1.686 ATR, MMM 1.220 ATR; SHORT: SNOW 0.343 ATR
- Long price near SMA20/50 (within 1 ATR): 4/14 usable (0 unavailable). Support: AAPL, CLMT, GME, SLB; counterexamples: TEVA, ELF, HUM, SIG, ABBV, CNQ, EBAY, GTLB, MMM, SAIL. Descriptive overlap cannot identify the entry rule.
- Long range10/previous20 below 1: 7/13 usable (1 unavailable). Support: AAPL, CLMT, ELF, GME, ABBV, GTLB, SLB; counterexamples: HUM, SIG, CNQ, EBAY, MMM, SAIL. Descriptive overlap cannot identify the entry rule.
- Short established downtrend: 3/12 usable (0 unavailable). Support: CAT, AAOI, GE; counterexamples: CDE, T, ASST, OMER, AMD, ANET, SNDK, SNOW, SCCO. Descriptive overlap cannot identify the entry rule.
- Short failed 20-session breakout: 0/12 usable (0 unavailable). Support: none; counterexamples: CAT, CDE, T, ASST, OMER, AAOI, AMD, ANET, SNDK, SNOW, GE, SCCO. Descriptive overlap cannot identify the entry rule.
- Short 20-session breakdown: 0/12 usable (0 unavailable). Support: none; counterexamples: CAT, CDE, T, ASST, OMER, AAOI, AMD, ANET, SNDK, SNOW, GE, SCCO. Descriptive overlap cannot identify the entry rule.
- Short bounce within downtrend: 2/12 usable (0 unavailable). Support: T, SNOW; counterexamples: CAT, CDE, ASST, OMER, AAOI, AMD, ANET, SNDK, GE, SCCO. Descriptive overlap cannot identify the entry rule.

Tight-risk/immediate-movement checks (H1, late clock):

- AAPL: risk 0.266 ATR; first-session directional Open-to-Close quote change 0.323 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- CLMT: risk 1.097 ATR; first-session directional Open-to-Close quote change -0.954 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- TEVA: risk 0.902 ATR; first-session directional Open-to-Close quote change -0.097 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- CAT: risk 0.310 ATR; first-session directional Open-to-Close quote change 0.459 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- CDE: risk 1.217 ATR; first-session directional Open-to-Close quote change 0.168 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- T: risk 1.149 ATR; first-session directional Open-to-Close quote change 0.077 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- ELF: risk 1.254 ATR; first-session directional Open-to-Close quote change -0.399 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- HUM: risk 1.340 ATR; first-session directional Open-to-Close quote change -0.297 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- SIG: risk 0.884 ATR; first-session directional Open-to-Close quote change -0.223 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- ASST: risk 0.284 ATR; first-session directional Open-to-Close quote change -1.470 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- OMER: risk 0.707 ATR; first-session directional Open-to-Close quote change 0.348 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- GME: risk 0.836 ATR; first-session directional Open-to-Close quote change -0.515 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- AAOI: risk 1.860 ATR; first-session directional Open-to-Close quote change 0.453 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- AMD: risk 1.691 ATR; first-session directional Open-to-Close quote change 0.549 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- ANET: risk 1.491 ATR; first-session directional Open-to-Close quote change 0.869 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- SNDK: risk 1.561 ATR; first-session directional Open-to-Close quote change 0.625 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- ABBV: risk 1.480 ATR; first-session directional Open-to-Close quote change -0.043 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- CNQ: risk 0.920 ATR; first-session directional Open-to-Close quote change 0.371 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- EBAY: risk 0.582 ATR; first-session directional Open-to-Close quote change -0.748 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- GTLB: risk 1.686 ATR; first-session directional Open-to-Close quote change 0.088 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- MMM: risk 1.220 ATR; first-session directional Open-to-Close quote change -0.529 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- SNOW: risk 0.343 ATR; first-session directional Open-to-Close quote change -0.586 ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- SAIL: risk unavailable ATR; first-session directional Open-to-Close quote change unavailable ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- SLB: risk unavailable ATR; first-session directional Open-to-Close quote change unavailable ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- GE: risk unavailable ATR; first-session directional Open-to-Close quote change unavailable ATR. Quote change includes any hypothetical exit and is not held-position P&L.
- SCCO: risk unavailable ATR; first-session directional Open-to-Close quote change unavailable ATR. Quote change includes any hypothetical exit and is not held-position P&L.

Widening/tightening challenges to PR17 (late clock, all constructed entry references):

- TIGHTENING: 16 changes; 16 with entry references; favorable across references 12; adverse/entry-sensitive 4; unavailable 0. Event identifiers: favorable ['alert-5:line-14', 'alert-6:line-18', 'alert-2:line-12', 'alert-5:line-19', 'alert-6:line-20', 'alert-2:line-13', 'alert-6:line-17', 'alert-5:line-16', 'alert-5:line-17', 'alert-5:line-18', 'alert-6:line-19', 'alert-5:line-20']; counterexamples ['alert-4:line-15', 'alert-6:line-15', 'alert-5:line-12', 'alert-7:line-14']; unavailable [].
- WIDENING: 11 changes; 11 with entry references; favorable across references 1; adverse/entry-sensitive 10; unavailable 0. Event identifiers: favorable ['alert-2:line-10']; counterexamples ['alert-3:line-14', 'alert-2:line-11', 'alert-3:line-15', 'alert-4:line-14', 'alert-5:line-13', 'alert-5:line-10', 'alert-5:line-15', 'alert-5:line-11', 'alert-6:line-16', 'alert-7:line-13']; unavailable [].

These comparisons test whether widening gives an adverse trade more room and tightening follows progress; exceptions prevent universal rules. MA/pivot distances, old-stop clearance and market-relative returns at each revision are retained in management_decisions.json. Their proximity alone cannot prove a causal stop-placement rule or regime motivation.

## ENTERABLE, UNDERWAY and DROPPED

UNDERWAY is an observed source classification, not a fill timestamp or proof of a particular trigger. Seven transitions are compared with pre-alert prices and all candidate paths below. Twelve DROPPED episodes remain in the inventory. An earlier model exit is an assumption conflict, not the source's closure cause. A DROP with a still-active path establishes only that Grimes stopped reporting the episode, not an exact execution, profit, time stop or discretionary rationale.

UNDERWAY transitions with quote progress across the available entry references:

- AAPL: 7.440–7.440 native price units, observed at 2026-10-22 under the late clock.
- CDE: 1.580–1.580 native price units, observed at 2026-10-22 under the late clock.
- T: 0.050–0.050 native price units, observed at 2026-10-19 under the late clock.
- AAOI: 4.260–4.260 native price units, observed at 2026-10-22 under the late clock.
- AMD: 15.180–15.180 native price units, observed at 2026-10-22 under the late clock.
- ANET: 5.700–7.430 native price units, observed at 2026-10-22 under the late clock.
- SNDK: 15.070–56.330 native price units, observed at 2026-10-22 under the late clock.

Favorable quote progress at these transitions is consistent with an established move; it does not identify an entry or prove +1R, partial realization, confirmation or a universal UNDERWAY threshold. ENTERABLE can coexist with exposure or later stop changes in the source; the labels alone do not encode execution size.

## CDE and EBAY

CDE remains SHORT / OPEN / UNDERWAY / 13.90. The H1 reference is 15.460 against opening stop 16.40; activation R is 0.940, with +1R price 14.520. Compare full-exit, partial-runner and continued-holding terminal paths below: a +1R touch alone does not establish a full source exit. The illustrative 50% fraction is not observed Grimes sizing.

EBAY remains LONG / OPEN / ENTERABLE / 117.50. Compare the Friday/Monday entry cases, the old hard-stop paths and the deferred-review alternative below. An after-session revision cannot rescue a prior hard stop. Any independent quote anchors constrain price-only rescaling (see adjustment diagnostics). Untriggered confirmation is possible but is not evidence that no trade existed. Neither a leading alternative nor a pending review establishes Grimes' actual policy. A later intraday entry can differ; finer timing is needed to distinguish it.

## Episode comparisons

### AAPL — LONG

Reported final state: CLOSED / UNDERWAY; opening stop 339.00; latest 344.70. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-18T15:20:00-04:00 OPEN_NEW_POSITION stop 339.00 setup ENTERABLE
- 2026-10-19T18:19:00-04:00 STOP_CHANGED stop 337.80 from 339.00 setup ENTERABLE
- 2026-10-20T18:25:00-04:00 STOP_CHANGED stop 336.25 from 337.80 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 343.50 from 336.25 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 SETUP_CHANGED setup UNDERWAY
- UNKNOWN STOP_CHANGED stop 344.70 from 343.50 setup UNDERWAY
- 2026-10-26T18:10:00-04:00 DROPPED setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.236, sma50 1.988, prior20_high -1.368, prior20_low 1.972, confirmed_swing_low 1.972, confirmed_swing_high -1.368. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-19T18:19:00-04:00 | 2026-10-19 | 2.160–2.160 | WIDENING / 0.614 | 0.028 / 1.793 | SPY 0.021; QQQ 0.044; RSP 0.008; IWM 0.065 |
| STOP_CHANGED / 2026-10-20T18:25:00-04:00 | 2026-10-20 | -1.280–-1.280 | WIDENING / 0.283 | -0.226 / 1.554 | SPY 0.005; QQQ 0.041; RSP -0.015; IWM 0.041 |
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 7.440–7.440 | TIGHTENING / 1.967 | 0.810 / 2.446 | SPY 0.041; QQQ 0.091; RSP -0.001; IWM 0.055 |
| SETUP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 7.440–7.440 | n/a / unavailable | unavailable / unavailable | SPY 0.041; QQQ 0.091; RSP -0.001; IWM 0.055 |
| STOP_CHANGED / UNKNOWN | 2026-10-23 | 6.950–6.950 | TIGHTENING / 0.684 | 0.937 / 2.463 | SPY 0.035; QQQ 0.078; RSP -0.006; IWM 0.043 |
| DROPPED / 2026-10-26T18:10:00-04:00 | 2026-10-26 | 3.130–3.130 | n/a / unavailable | unavailable / unavailable | SPY 0.017; QQQ 0.051; RSP -0.019; IWM 0.027 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @340.780 [340.780–340.780] | 0.266–0.266 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 4/0/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/4/3 HYPOTHETICAL_STOP_GAP:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/4/2 HYPOTHETICAL_STOP_GAP:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/5/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @340.780 [340.780–340.780] | 0.266–0.266 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 4/0/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/4/3 HYPOTHETICAL_STOP_GAP:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/4/2 HYPOTHETICAL_STOP_GAP:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/5/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @340.780 [340.780–340.780] | 0.266–0.266 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 4/0/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/4/3 HYPOTHETICAL_STOP_GAP:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/4/2 HYPOTHETICAL_STOP_GAP:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/5/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### CLMT — LONG

Reported final state: CLOSED / ENTERABLE; opening stop 55.25; latest 53.02. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-18T15:20:00-04:00 OPEN_NEW_POSITION stop 55.25 setup ENTERABLE
- 2026-10-19T18:19:00-04:00 STOP_CHANGED stop 53.40 from 55.25 setup ENTERABLE
- 2026-10-20T18:25:00-04:00 STOP_CHANGED stop 53.02 from 53.40 setup ENTERABLE
- 2026-10-21T18:50:00-04:00 DROPPED setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -0.262, sma50 1.156, prior20_high -2.283, prior20_low 1.937, confirmed_swing_low 1.937, confirmed_swing_high -2.283. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-19T18:19:00-04:00 | 2026-10-19 | -1.930–-0.241 | WIDENING / 0.133 | -1.030 / 0.077 | SPY -0.036; QQQ -0.014; RSP -0.048; IWM 0.006 |
| STOP_CHANGED / 2026-10-20T18:25:00-04:00 | 2026-10-20 | -1.420–0.269 | WIDENING / 1.222 | -1.205 / -0.196 | SPY -0.001; QQQ 0.035; RSP -0.021; IWM 0.035 |
| DROPPED / 2026-10-21T18:50:00-04:00 | 2026-10-21 | -4.880–-3.191 | n/a / unavailable | unavailable / unavailable | SPY -0.040; QQQ -0.012; RSP -0.057; IWM -0.014 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @57.470 [57.470–57.470] | 1.097–1.097 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-19 @55.781 [53.830–55.781] | 0.000–0.262 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @57.470 [57.470–57.470] | 1.097–1.097 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-19 @55.781 [53.830–55.781] | 0.000–0.262 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @57.470 [57.470–57.470] | 1.097–1.097 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-19 @55.781 [53.830–55.781] | 0.000–0.262 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### TEVA — LONG

Reported final state: CLOSED / ENTERABLE; opening stop 40.40; latest 39.05. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-18T15:20:00-04:00 OPEN_NEW_POSITION stop 40.40 setup ENTERABLE
- 2026-10-21T18:50:00-04:00 STOP_CHANGED stop 39.35 from 40.40 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 39.05 from 39.35 setup ENTERABLE
- UNKNOWN DROPPED setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.389, prior20_high -1.432, prior20_low 1.900. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-21T18:50:00-04:00 | 2026-10-21 | -0.800–-0.800 | WIDENING / 0.204 | -0.758 / unavailable | SPY 0.034; QQQ 0.064; RSP 0.016; IWM 0.062 |
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | -1.210–-1.210 | WIDENING / 0.781 | -1.017 / unavailable | SPY 0.004; QQQ 0.052; RSP -0.037; IWM 0.018 |
| DROPPED / UNKNOWN | 2026-10-23 | -2.010–-2.010 | n/a / unavailable | unavailable / unavailable | SPY 0.021; QQQ 0.063; RSP -0.020; IWM 0.028 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @41.420 [41.420–41.420] | 0.902–0.902 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_GAP:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_GAP:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_GAP:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @41.420 [41.420–41.420] | 0.902–0.902 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_GAP:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_GAP:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_GAP:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @41.420 [41.420–41.420] | 0.902–0.902 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_GAP:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_GAP:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_GAP:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### CAT — SHORT

Reported final state: CLOSED / ENTERABLE; opening stop 748.75; latest 748.75. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-18T15:20:00-04:00 OPEN_NEW_POSITION stop 748.75 setup ENTERABLE
- 2026-10-20T18:25:00-04:00 DROPPED setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.886, sma50 -2.142, prior20_high -4.290, prior20_low 1.497, confirmed_swing_low -1.797, confirmed_swing_high -4.290. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| DROPPED / 2026-10-20T18:25:00-04:00 | 2026-10-20 | 3.450–14.260 | n/a / unavailable | unavailable / unavailable | SPY -0.097; QQQ -0.065; RSP -0.115; IWM -0.065 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @739.500 [739.500–739.500] | 0.310–0.310 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-19 @728.690 [718.440–728.690] | 0.671–1.014 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @739.500 [739.500–739.500] | 0.310–0.310 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-19 @728.690 [718.440–728.690] | 0.671–1.014 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @739.500 [739.500–739.500] | 0.310–0.310 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-19 @728.690 [718.440–728.690] | 0.671–1.014 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### CDE — SHORT

Reported final state: OPEN / UNDERWAY; opening stop 16.40; latest 13.90. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-18T15:20:00-04:00 OPEN_NEW_POSITION stop 16.40 setup ENTERABLE
- 2026-10-19T18:19:00-04:00 STOP_CHANGED stop 16.24 from 16.40 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 14.30 from 16.24 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 SETUP_CHANGED setup UNDERWAY
- UNKNOWN STOP_CHANGED stop 13.90 from 14.30 setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.399, sma50 -3.476, prior20_high -5.476, prior20_low 2.233, confirmed_swing_low 0.220, confirmed_swing_high -1.417. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-19T18:19:00-04:00 | 2026-10-19 | 0.130–0.130 | TIGHTENING / 1.450 | -1.398 / -3.800 | SPY -0.207; QQQ -0.189; RSP -0.217; IWM -0.173 |
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 1.580–1.580 | TIGHTENING / 2.870 | -2.725 / -5.492 | SPY -0.264; QQQ -0.229; RSP -0.294; IWM -0.254 |
| SETUP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 1.580–1.580 | n/a / unavailable | unavailable / unavailable | SPY -0.264; QQQ -0.229; RSP -0.294; IWM -0.254 |
| STOP_CHANGED / UNKNOWN | 2026-10-23 | 2.010–2.010 | TIGHTENING / 1.065 | -2.947 / -6.032 | SPY -0.290; QQQ -0.260; RSP -0.318; IWM -0.284 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @15.460 [15.460–15.460] | 1.217–1.217 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 3/1/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/3/2 ACTIVE:remaining=0.5; HOLD_WITH_REPORTED_STOPS: 0/3/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/3/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @15.460 [15.460–15.460] | 1.217–1.217 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 3/1/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/3/2 ACTIVE:remaining=0.5; HOLD_WITH_REPORTED_STOPS: 0/3/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/3/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @15.460 [15.460–15.460] | 1.217–1.217 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 3/1/4 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/3/2 ACTIVE:remaining=0.5; HOLD_WITH_REPORTED_STOPS: 0/3/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/3/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### T — SHORT

Reported final state: CLOSED / UNDERWAY; opening stop 24.00; latest 22.20. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-18T15:20:00-04:00 OPEN_NEW_POSITION stop 24.00 setup ENTERABLE
- 2026-10-19T18:19:00-04:00 STOP_CHANGED stop 23.80 from 24.00 setup ENTERABLE
- 2026-10-19T18:19:00-04:00 SETUP_CHANGED setup UNDERWAY
- 2026-10-21T18:50:00-04:00 STOP_CHANGED stop 22.20 from 23.80 setup UNDERWAY
- 2026-10-22T18:27:00-04:00 DROPPED setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -0.351, sma50 -1.425, prior20_high -2.772, prior20_low 3.125, confirmed_swing_low 3.125, confirmed_swing_high -1.486. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-19T18:19:00-04:00 | 2026-10-19 | 0.050–0.050 | TIGHTENING / 1.254 | -0.496 / -1.753 | SPY -0.080; QQQ -0.059; RSP -0.091; IWM -0.040 |
| SETUP_CHANGED / 2026-10-19T18:19:00-04:00 | 2026-10-19 | 0.050–0.050 | n/a / unavailable | unavailable / unavailable | SPY -0.080; QQQ -0.059; RSP -0.091; IWM -0.040 |
| STOP_CHANGED / 2026-10-21T18:50:00-04:00 | 2026-10-21 | -0.020–1.340 | TIGHTENING / 2.532 | -2.228 / -3.555 | SPY -0.140; QQQ -0.115; RSP -0.155; IWM -0.117 |
| DROPPED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | -0.850–0.510 | n/a / unavailable | unavailable / unavailable | SPY -0.103; QQQ -0.060; RSP -0.139; IWM -0.090 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @23.250 [23.250–23.250] | 1.149–1.149 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 1/1/7 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/2/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @21.890 [21.890–21.890] | 2.929–2.929 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @23.250 [23.250–23.250] | 1.149–1.149 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 1/1/7 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/2/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @21.890 [21.890–21.890] | 2.929–2.929 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-19 @23.250 [23.250–23.250] | 1.149–1.149 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 1/1/7 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/2/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @21.890 [21.890–21.890] | 2.929–2.929 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### ELF — LONG

Reported final state: OPEN / ENTERABLE; opening stop 110.50; latest 109.20. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-20T18:25:00-04:00 OPEN_NEW_POSITION stop 110.50 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 108.60 from 110.50 setup ENTERABLE
- UNKNOWN STOP_CHANGED stop 109.20 from 108.60 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 1.108, sma50 2.098, prior20_high -2.031, prior20_low 3.519, confirmed_swing_low 3.519, confirmed_swing_high 2.789. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | -0.320–-0.320 | WIDENING / 1.181 | 0.258 / 1.401 | SPY 0.148; QQQ 0.203; RSP 0.102; IWM 0.164 |
| STOP_CHANGED / UNKNOWN | 2026-10-23 | -1.070–-1.070 | TIGHTENING / 1.481 | 0.222 / 1.439 | SPY 0.165; QQQ 0.213; RSP 0.119; IWM 0.174 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @115.310 [115.310–115.310] | 1.254–1.254 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/2/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/2/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/2/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @115.310 [115.310–115.310] | 1.254–1.254 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/2/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/2/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/2/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @115.310 [115.310–115.310] | 1.254–1.254 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/2/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/2/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/2/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @115.310 [115.310–115.310] | 1.254–1.254 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/2/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/2/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/2/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @115.310 [115.310–115.310] | 1.254–1.254 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/2/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/2/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/2/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @115.310 [115.310–115.310] | 1.254–1.254 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/2/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/2/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/2/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### HUM — LONG

Reported final state: OPEN / ENTERABLE; opening stop 404.00; latest 408.10. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-20T18:25:00-04:00 OPEN_NEW_POSITION stop 404.00 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 408.10 from 404.00 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.020, sma50 0.421, prior20_high -2.557, prior20_low 1.698, confirmed_swing_low 1.371, confirmed_swing_high -2.557. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | -10.550–-10.550 | TIGHTENING / 0.830 | -0.003 / 0.540 | SPY 0.112; QQQ 0.164; RSP 0.067; IWM 0.127 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @431.520 [431.520–431.520] | 1.340–1.340 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @431.520 [431.520–431.520] | 1.340–1.340 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @431.520 [431.520–431.520] | 1.340–1.340 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @431.520 [431.520–431.520] | 1.340–1.340 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @431.520 [431.520–431.520] | 1.340–1.340 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-21 @431.520 [431.520–431.520] | 1.340–1.340 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### SIG — LONG

Reported final state: OPEN / ENTERABLE; opening stop 111.80; latest 112.50. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-20T18:25:00-04:00 OPEN_NEW_POSITION stop 111.80 setup ENTERABLE
- UNKNOWN STOP_CHANGED stop 112.50 from 111.80 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 1.221, sma50 3.377, prior20_high -2.414, prior20_low 2.866, confirmed_swing_low 2.592, confirmed_swing_high 1.154. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / UNKNOWN | 2026-10-23 | 1.410–1.410 | TIGHTENING / 1.297 | 0.935 / 3.491 | SPY 0.163; QQQ 0.211; RSP 0.117; IWM 0.172 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @115.770 [115.770–115.770] | 0.884–0.884 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @115.770 [115.770–115.770] | 0.884–0.884 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @115.770 [115.770–115.770] | 0.884–0.884 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### ASST — SHORT

Reported final state: CLOSED / ENTERABLE; opening stop 28.45; latest 28.45. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-20T18:25:00-04:00 OPEN_NEW_POSITION stop 28.45 setup ENTERABLE
- 2026-10-21T18:50:00-04:00 DROPPED setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.160, sma50 1.964, prior20_high -1.873, prior20_low 3.080, confirmed_swing_low 3.080, confirmed_swing_high -1.873. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| DROPPED / 2026-10-21T18:50:00-04:00 | 2026-10-21 | -2.850–-2.611 | n/a / unavailable | unavailable / unavailable | SPY 0.053; QQQ 0.084; RSP 0.035; IWM 0.082 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @27.900 [27.900–27.900] | 0.284–0.284 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/5 HYPOTHETICAL_FULL_1R:remaining=0,HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-21 @28.139 [28.139–31.510] | 0.000–0.160 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @27.900 [27.900–27.900] | 0.284–0.284 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/5 HYPOTHETICAL_FULL_1R:remaining=0,HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-21 @28.139 [28.139–31.510] | 0.000–0.160 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @27.900 [27.900–27.900] | 0.284–0.284 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/5 HYPOTHETICAL_FULL_1R:remaining=0,HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-21 @28.139 [28.139–31.510] | 0.000–0.160 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### OMER — SHORT

Reported final state: OPEN / ENTERABLE; opening stop 17.20; latest 17.35. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-20T18:25:00-04:00 OPEN_NEW_POSITION stop 17.20 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 17.35 from 17.20 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.777, sma50 -1.362, prior20_high -4.532, prior20_low 1.520, confirmed_swing_low -0.920, confirmed_swing_high -3.410. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | -0.290–-0.290 | WIDENING / 0.384 | -1.182 / -1.333 | SPY -0.159; QQQ -0.119; RSP -0.193; IWM -0.147 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @16.570 [16.570–16.570] | 0.707–0.707 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @16.570 [16.570–16.570] | 0.707–0.707 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-21 @16.570 [16.570–16.570] | 0.707–0.707 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### GME — LONG

Reported final state: CLOSED / ENTERABLE; opening stop 25.01; latest 24.40. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-21T18:50:00-04:00 OPEN_NEW_POSITION stop 25.01 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 24.78 from 25.01 setup ENTERABLE
- UNKNOWN STOP_CHANGED stop 24.40 from 24.78 setup ENTERABLE
- 2026-10-26T18:10:00-04:00 DROPPED setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -0.483, sma50 2.466, prior20_high -2.780, prior20_low 1.656, confirmed_swing_low 0.820, confirmed_swing_high -2.780. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | -0.610–-0.192 | WIDENING / 0.305 | -0.659 / 2.051 | SPY 0.019; QQQ 0.068; RSP -0.022; IWM 0.033 |
| STOP_CHANGED / UNKNOWN | 2026-10-23 | -1.180–-0.762 | WIDENING / 0.032 | -1.031 / 1.659 | SPY 0.077; QQQ 0.122; RSP 0.035; IWM 0.085 |
| DROPPED / 2026-10-26T18:10:00-04:00 | 2026-10-26 | -2.100–-1.682 | n/a / unavailable | unavailable / unavailable | SPY -0.002; QQQ 0.032; RSP -0.037; IWM 0.008 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @26.000 [26.000–26.000] | 0.836–0.836 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-22 @25.582 [24.610–25.582] | 0.000–0.483 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @26.000 [26.000–26.000] | 0.836–0.836 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-22 @25.582 [24.610–25.582] | 0.000–0.483 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @26.000 [26.000–26.000] | 0.836–0.836 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary; Not observed within three eligible sessions; not proof of no actual trade | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | CONSTRUCTED 2026-10-22 @25.582 [24.610–25.582] | 0.000–0.483 (zero excluded) | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### AAOI — SHORT

Reported final state: CLOSED / UNDERWAY; opening stop 89.82; latest 70.70. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-21T18:50:00-04:00 OPEN_NEW_POSITION stop 89.82 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 70.70 from 89.82 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 SETUP_CHANGED setup UNDERWAY
- UNKNOWN DROPPED setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.020, sma50 -1.889, prior20_high -4.396, prior20_low 1.784, confirmed_swing_low -0.404, confirmed_swing_high -4.396. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 4.260–4.260 | TIGHTENING / 2.319 | -2.885 / -3.783 | SPY -0.323; QQQ -0.291; RSP -0.351; IWM -0.314 |
| SETUP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 4.260–4.260 | n/a / unavailable | unavailable / unavailable | SPY -0.323; QQQ -0.291; RSP -0.351; IWM -0.314 |
| DROPPED / UNKNOWN | 2026-10-23 | 4.820–4.820 | n/a / unavailable | unavailable / unavailable | SPY -0.324; QQQ -0.296; RSP -0.351; IWM -0.319 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @72.330 [72.330–72.330] | 1.860–1.860 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @72.330 [72.330–72.330] | 1.860–1.860 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @72.330 [72.330–72.330] | 1.860–1.860 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @72.330 [72.330–72.330] | 1.860–1.860 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @72.330 [72.330–72.330] | 1.860–1.860 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @72.330 [72.330–72.330] | 1.860–1.860 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### AMD — SHORT

Reported final state: CLOSED / UNDERWAY; opening stop 569.90; latest 519.35. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-21T18:50:00-04:00 OPEN_NEW_POSITION stop 569.90 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 519.35 from 569.90 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 SETUP_CHANGED setup UNDERWAY
- UNKNOWN DROPPED setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.051, sma50 1.041, prior20_high -3.203, prior20_low 1.637, confirmed_swing_low -0.946, confirmed_swing_high -3.203. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 15.180–15.180 | TIGHTENING / 2.128 | -2.526 / -0.764 | SPY -0.189; QQQ -0.151; RSP -0.222; IWM -0.178 |
| SETUP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 15.180–15.180 | n/a / unavailable | unavailable / unavailable | SPY -0.189; QQQ -0.151; RSP -0.222; IWM -0.178 |
| DROPPED / UNKNOWN | 2026-10-23 | 6.320–6.320 | n/a / unavailable | unavailable / unavailable | SPY -0.168; QQQ -0.134; RSP -0.201; IWM -0.162 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @523.110 [523.110–523.110] | 1.691–1.691 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/2/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/5 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @523.110 [523.110–523.110] | 1.691–1.691 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/6 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @523.110 [523.110–523.110] | 1.691–1.691 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @523.110 [523.110–523.110] | 1.691–1.691 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @523.110 [523.110–523.110] | 1.691–1.691 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @523.110 [523.110–523.110] | 1.691–1.691 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### ANET — SHORT

Reported final state: CLOSED / UNDERWAY; opening stop 191.25; latest 175.20. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-21T18:50:00-04:00 OPEN_NEW_POSITION stop 191.25 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 176.80 from 191.25 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 SETUP_CHANGED setup UNDERWAY
- UNKNOWN STOP_CHANGED stop 175.20 from 176.80 setup UNDERWAY
- 2026-10-26T18:10:00-04:00 DROPPED setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.159, sma50 -0.770, prior20_high -3.060, prior20_low 1.694, confirmed_swing_low 1.694, confirmed_swing_high -3.060. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 5.700–7.430 | TIGHTENING / 2.173 | -2.436 / -2.180 | SPY -0.165; QQQ -0.125; RSP -0.199; IWM -0.153 |
| SETUP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 5.700–7.430 | n/a / unavailable | unavailable / unavailable | SPY -0.165; QQQ -0.125; RSP -0.199; IWM -0.153 |
| STOP_CHANGED / UNKNOWN | 2026-10-23 | 4.400–6.130 | TIGHTENING / 0.466 | -2.366 / -2.230 | SPY -0.153; QQQ -0.118; RSP -0.186; IWM -0.147 |
| DROPPED / 2026-10-26T18:10:00-04:00 | 2026-10-26 | -0.470–1.260 | n/a / unavailable | unavailable / unavailable | SPY -0.135; QQQ -0.106; RSP -0.165; IWM -0.126 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @178.500 [178.500–178.500] | 1.491–1.491 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/2/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @176.770 [169.870–176.770] | 1.694–2.501 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/2/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @178.500 [178.500–178.500] | 1.491–1.491 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/2/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @176.770 [169.870–176.770] | 1.694–2.501 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/2/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @178.500 [178.500–178.500] | 1.491–1.491 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/2/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @176.770 [169.870–176.770] | 1.694–2.501 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/2/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/3/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### SNDK — SHORT

Reported final state: CLOSED / UNDERWAY; opening stop 1458.00; latest 1296.00. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-21T18:50:00-04:00 OPEN_NEW_POSITION stop 1458.00 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 STOP_CHANGED stop 1296.00 from 1458.00 setup ENTERABLE
- 2026-10-22T18:27:00-04:00 SETUP_CHANGED setup UNDERWAY
- UNKNOWN DROPPED setup UNDERWAY

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.382, sma50 -1.585, prior20_high -4.927, prior20_low 2.019, confirmed_swing_low 2.019, confirmed_swing_high -3.804. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 15.070–56.330 | TIGHTENING / 2.088 | -2.775 / -3.212 | SPY -0.278; QQQ -0.244; RSP -0.307; IWM -0.268 |
| SETUP_CHANGED / 2026-10-22T18:27:00-04:00 | 2026-10-22 | 15.070–56.330 | n/a / unavailable | unavailable / unavailable | SPY -0.278; QQQ -0.244; RSP -0.307; IWM -0.268 |
| DROPPED / UNKNOWN | 2026-10-23 | 37.970–79.230 | n/a / unavailable | unavailable / unavailable | SPY -0.293; QQQ -0.264; RSP -0.321; IWM -0.288 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @1317.260 [1317.260–1317.260] | 1.561–1.561 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/2/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/2/3 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/5 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @1276.000 [1244.600–1276.000] | 2.019–2.367 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; PARTIAL_50_AT_1R: 0/2/4 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/6 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @1317.260 [1317.260–1317.260] | 1.561–1.561 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @1276.000 [1244.600–1276.000] | 2.019–2.367 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-22 @1317.260 [1317.260–1317.260] | 1.561–1.561 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-22 @1276.000 [1244.600–1276.000] | 2.019–2.367 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/1/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/1/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/2/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### ABBV — LONG

Reported final state: OPEN / ENTERABLE; opening stop 276.30; latest 276.30. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- UNKNOWN OPEN_NEW_POSITION stop 276.30 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.167, sma50 1.401, prior20_high -2.079, prior20_low 2.538, confirmed_swing_low 2.538, confirmed_swing_high -2.079. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-23 @284.580 [284.580–284.580] | 1.112–1.112 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-23 @285.760 [285.760–286.770] | 1.271–1.406 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @287.050 [287.050–287.050] | 1.480–1.480 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-26 @287.050 [287.050–287.050] | 1.480–1.480 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @287.050 [287.050–287.050] | 1.480–1.480 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/7 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | CONSTRUCTED 2026-10-23 @285.640 [285.640–285.640] | 1.254–1.254 | Near-close reference only if publication can precede that Close; no current-bar setup information | FULL_EXIT_AT_1R: 0/0/6 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/6 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/3 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/9 ACTIVE:remaining=1.0 |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-26 @287.050 [287.050–287.050] | 1.480–1.480 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/5 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/5 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/8 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### CNQ — LONG

Reported final state: OPEN / ENTERABLE; opening stop 53.30; latest 53.30. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- UNKNOWN OPEN_NEW_POSITION stop 53.30 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 1.912, sma50 2.218, prior20_high -1.411, prior20_low 4.790, confirmed_swing_low 4.790, confirmed_swing_high 0.706. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-23 @54.540 [54.540–54.540] | 0.891–0.891 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-23 @55.280 [55.280–55.500] | 1.423–1.581 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @54.590 [54.590–54.590] | 0.920–0.920 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @54.590 [54.590–54.590] | 0.920–0.920 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/7 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | CONSTRUCTED 2026-10-23 @55.060 [55.060–55.060] | 1.265–1.265 | Near-close reference only if publication can precede that Close; no current-bar setup information | FULL_EXIT_AT_1R: 0/0/6 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/6 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/3 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/9 ACTIVE:remaining=1.0 |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-26 @55.280 [55.280–55.290] | 1.411–1.419 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/5 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/5 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/8 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### EBAY — LONG

Reported final state: OPEN / ENTERABLE; opening stop 119.20; latest 117.50. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- UNKNOWN OPEN_NEW_POSITION stop 119.20 setup ENTERABLE
- 2026-10-26T18:10:00-04:00 STOP_CHANGED stop 117.50 from 119.20 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 1.542, sma50 2.868, prior20_high -1.538, prior20_low 4.164, confirmed_swing_low 4.164, confirmed_swing_high -1.538. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-26T18:10:00-04:00 | 2026-10-26 | -2.620–-2.620 | WIDENING / -0.162 | 0.874 / 2.240 | SPY 0.106; QQQ 0.143; RSP 0.067; IWM 0.117 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-23 @120.840 [120.840–120.840] | 0.466–0.466 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 REVIEW_PENDING:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @121.240 [121.240–121.240] | 0.582–0.582 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 REVIEW_PENDING:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @121.240 [121.240–121.240] | 0.582–0.582 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 REVIEW_PENDING:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | CONSTRUCTED 2026-10-23 @121.410 [121.410–121.410] | 0.628–0.628 | Near-close reference only if publication can precede that Close; no current-bar setup information | FULL_EXIT_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 2/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 2/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/2 REVIEW_PENDING:remaining=1.0 |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### GTLB — LONG

Reported final state: OPEN / ENTERABLE; opening stop 51.60; latest 52.10. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- UNKNOWN OPEN_NEW_POSITION stop 51.60 setup ENTERABLE
- 2026-10-26T18:10:00-04:00 STOP_CHANGED stop 52.10 from 51.60 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -0.282, sma50 1.043, prior20_high -2.210, prior20_low 2.593, confirmed_swing_low 0.457, confirmed_swing_high -2.210. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| STOP_CHANGED / 2026-10-26T18:10:00-04:00 | 2026-10-26 | -0.490–0.250 | TIGHTENING / 1.830 | -0.299 / 1.156 | SPY 0.226; QQQ 0.268; RSP 0.183; IWM 0.239 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-23 @54.350 [54.350–54.350] | 0.992–0.992 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 2/0/7 HYPOTHETICAL_FULL_1R:remaining=0; PARTIAL_50_AT_1R: 0/1/3 ACTIVE:remaining=0.5; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-23 @56.650 [56.650–57.140] | 1.822–1.999 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @56.400 [56.400–56.400] | 1.686–1.686 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-26 @57.140 [57.140–57.160] | 1.946–1.953 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @56.400 [56.400–56.400] | 1.686–1.686 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/1/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/7 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | CONSTRUCTED 2026-10-23 @56.280 [56.280–56.280] | 1.689–1.689 | Near-close reference only if publication can precede that Close; no current-bar setup information | FULL_EXIT_AT_1R: 0/1/6 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/6 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/3 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/9 ACTIVE:remaining=1.0 |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-26 @56.650 [56.650–57.160] | 1.774–1.953 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/1/5 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/1/5 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/1/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/1/8 ACTIVE:remaining=1.0 |
| H4_PULLBACK | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### MMM — LONG

Reported final state: OPEN / ENTERABLE; opening stop 169.90; latest 169.90. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- UNKNOWN OPEN_NEW_POSITION stop 169.90 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.994, sma50 0.182, prior20_high -1.502, prior20_low 2.559, confirmed_swing_low 1.902, confirmed_swing_high -0.258. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-23 @174.220 [174.220–174.220] | 1.052–1.052 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/3 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/3 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/5 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-23 @174.770 [174.770–175.280] | 1.186–1.310 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/6 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @175.000 [175.000–175.000] | 1.220–1.220 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/2 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/2 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/3 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @175.000 [175.000–175.000] | 1.220–1.220 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/4 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/4 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/1 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/7 ACTIVE:remaining=1.0 |
| H2_ALERT_SESSION_CLOSE | CONSTRUCTED 2026-10-23 @173.460 [173.460–173.460] | 0.867–0.867 | Near-close reference only if publication can precede that Close; no current-bar setup information | FULL_EXIT_AT_1R: 0/0/6 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/6 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/3 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/9 ACTIVE:remaining=1.0 |
| H3_CONFIRMATION | CONSTRUCTED 2026-10-26 @175.000 [175.000–175.000] | 1.220–1.220 | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/5 ACTIVE:remaining=1.0; PARTIAL_50_AT_1R: 0/0/5 ACTIVE:remaining=1.0; HOLD_WITH_REPORTED_STOPS: 0/0/2 ACTIVE:remaining=1.0; CLOSE_REVIEW_NEXT_OPEN: 0/0/8 ACTIVE:remaining=1.0 |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### SNOW — SHORT

Reported final state: CLOSED / ENTERABLE; opening stop 330.70; latest 330.70. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- UNKNOWN OPEN_NEW_POSITION stop 330.70 setup ENTERABLE
- 2026-10-26T18:10:00-04:00 DROPPED setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -0.227, sma50 -0.055, prior20_high -2.280, prior20_low 1.628, confirmed_swing_low 1.628, confirmed_swing_high -2.280. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|
| DROPPED / 2026-10-26T18:10:00-04:00 | 2026-10-26 | -10.250–-10.250 | n/a / unavailable | unavailable / unavailable | SPY 0.021; QQQ 0.056; RSP -0.015; IWM 0.032 |

**EARLY_BEFORE_FIRST_OPEN** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-23 @310.310 [310.310–310.310] | 1.217–1.217 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @324.700 [324.700–324.700] | 0.343–0.343 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/2 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 1. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | CONSTRUCTED 2026-10-26 @324.700 [324.700–324.700] | 0.343–0.343 | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/5 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/3 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/1 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H2_ALERT_SESSION_CLOSE | CONSTRUCTED 2026-10-23 @325.430 [325.430–325.430] | 0.315–0.315 | Near-close reference only if publication can precede that Close; no current-bar setup information | FULL_EXIT_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; PARTIAL_50_AT_1R: 0/0/6 HYPOTHETICAL_STOP_TOUCH:remaining=0; HOLD_WITH_REPORTED_STOPS: 0/0/4 HYPOTHETICAL_STOP_TOUCH:remaining=0; CLOSE_REVIEW_NEXT_OPEN: 0/1/2 SOURCE_DROPPED_EXECUTION_UNOBSERVED:remaining=0 |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 2. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### SAIL — LONG

Reported final state: OPEN / ENTERABLE; opening stop 20.90; latest 20.90. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-26T18:10:00-04:00 OPEN_NEW_POSITION stop 20.90 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.794, sma50 1.150, prior20_high -1.207, prior20_low 2.378, confirmed_swing_low 2.378, confirmed_swing_high 0.756. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### SLB — LONG

Reported final state: OPEN / ENTERABLE; opening stop 51.10; latest 51.10. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-26T18:10:00-04:00 OPEN_NEW_POSITION stop 51.10 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 0.950, sma50 -0.859, prior20_high -1.485, prior20_low 2.484, confirmed_swing_low 2.484, confirmed_swing_high 0.310. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### GE — SHORT

Reported final state: OPEN / ENTERABLE; opening stop 295.80; latest 295.80. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-26T18:10:00-04:00 OPEN_NEW_POSITION stop 295.80 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.104, sma50 -2.992, prior20_high -3.236, prior20_low 1.994, confirmed_swing_low -0.093, confirmed_swing_high -2.903. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

### SCCO — SHORT

Reported final state: OPEN / ENTERABLE; opening stop 191.70; latest 191.70. Actual entry, exit cause and P&L unknown.

Source sequence (UNKNOWN remains a source fact):

- 2026-10-26T18:10:00-04:00 OPEN_NEW_POSITION stop 191.70 setup ENTERABLE

Opening-stop minus pre-alert structural level, in ATR (signed native price distance): sma20 -1.066, sma50 -1.191, prior20_high -2.435, prior20_low 1.367, confirmed_swing_low -0.087, confirmed_swing_high -2.347. Proximity does not establish why that stop was chosen.

Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):

| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |
|---|---|---|---|---|---|

**EARLY_BEFORE_FIRST_OPEN** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**LATE_EMAIL_BOUND** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

**FIRST_SESSION_CLOSE_COMPATIBLE** — NO_OBSERVED_ENTRY_TO_RANK

| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |
|---|---|---|---|---|
| H1_NEXT_OPEN | MISSING_OR_FUTURE_ENTRY_SESSION 2026-10-27 @unavailable [unavailable] | unavailable | Conventional next eligible Open; initial stop known from opening alert | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H2_ALERT_SESSION_CLOSE | REJECTED  @unavailable [unavailable] | unavailable | Near-close reference only if publication can precede that Close; no current-bar setup information; Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION  @unavailable [unavailable] | unavailable | Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |
| H4_PULLBACK | REJECTED  @unavailable [unavailable] | unavailable | First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop; No causal, geometrically valid predeclared level | FULL_EXIT_AT_1R: 0/0/unranked ; PARTIAL_50_AT_1R: 0/0/unranked ; HOLD_WITH_REPORTED_STOPS: 0/0/unranked ; CLOSE_REVIEW_NEXT_OPEN: 0/0/unranked  |

Observational-equivalence groups: 0. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json.

Unresolved: Actual entry/activation convention and timing unknown; Native/nominal stop-scale compatibility assumed unless session quote-anchored; Daily extrema do not identify intraday ordering; Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies.

## Limits

No inference of historical screening membership, population performance or trading edge. The sample is source-selected and tiny. Ranks are conditional diagnostic ordering, not estimated likelihoods. Two canonical daily extrema orders expose ambiguity but do not exhaust every intraday oscillation or gap; no execution-cost/size/P&L simulator is introduced. MFE/MAE fields are upper envelopes over merged compatible paths, not simultaneous realized excursions. No new market data were acquired. Native volume units and dollar-volume eligibility remain unverified. The preserved public source-status CSV is not regenerated by this study.
