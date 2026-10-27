# Grimes trade management and decision analysis

## Executive summary

This discovery study includes all 26 source positions and 72 actions across seven October 18–26, 2026 alerts: 26 openings, 27 stop revisions, seven underway transitions and 12 source closures; 14 source positions remain right-censored. PLTR/PEP stay excluded. Actual fills, size, realized P&L and discretionary intent remain unknown.

The clearest source-only difference is stop direction: LONG widening 10/16 (62.5%) versus SHORT widening 1/11 (9.1%). This describes this alert sample, not a fitted or verified management algorithm.

Among conditional, still-active observations, tightening follows positive signed price progress in 11/13 (84.6%); underway follows positive progress in 6/6 (100.0%). Unusable/post-exit observations remain in the tables. Co-publication and sector overlap prevent treating these decisions as independent evidence.

Counterexamples to tightening-only-after-favorable-progress: HUM (alert-5:line-12, -2.444846125324); ELF (alert-6:line-15, -0.92793339693). Favorable-progress widening observations: AAPL (alert-2:line-10, 0.633840014085). These are hypothetical reference-price comparisons, not realized trade profits.

EBAY preserves the PR16 source/model contradiction: source remains OPEN with the 119.20→117.50 revision; the original modeled episode has already stopped under the inherited timing/scale assumptions. Its later decision has no current held-position progress. No model outcome identifies an actual source closure cause.

## Stop management

Source change percentages do not require native-bar compatibility. Price, ATR and original-R comparisons do; the full table is conditional, with primary corroboration recorded separately. New stops are reported outcomes, not pre-publication features. Pre-alert stops exclude all changes first published in the same alert.

| Symbol / event | Direction / setup | Old → new | Change | Source % | Conditional ΔATR | Conditional progress % | Conditional MFE / MAE % | Conditional old-stop clearance ATR | Model-path status |
|---|---|---|---|---|---|---|---|---|---|
| AAPL / alert-2:line-10 | LONG / ENTERABLE | 339.00 → 337.80 | WIDENING | -0.3540 | -0.1870 | 0.6338 | 1.5318 / 0.1966 | 0.6139 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| CLMT / alert-2:line-11 | LONG / ENTERABLE | 55.25 → 53.40 | WIDENING | -3.3484 | -0.8461 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 0.1326 | MODELED_CLOSED_BEFORE_DECISION |
| CDE / alert-2:line-12 | SHORT / ENTERABLE | 16.40 → 16.24 | TIGHTENING | -0.9756 | 0.2168 | 0.8409 | 1.2613 / 0.8409 | 1.4501 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| T / alert-2:line-13 | SHORT / ENTERABLE | 24.00 → 23.80 | TIGHTENING | -0.8333 | 0.3135 | 0.2151 | 0.7742 / 0.7312 | 1.2542 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AAPL / alert-3:line-14 | LONG / ENTERABLE | 337.80 → 336.25 | WIDENING | -0.4589 | -0.2580 | -0.3756 | 1.5318 / 0.6104 | 0.2830 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| CLMT / alert-3:line-15 | LONG / ENTERABLE | 53.40 → 53.02 | WIDENING | -0.7116 | -0.1752 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 1.2220 | MODELED_CLOSED_BEFORE_DECISION |
| TEVA / alert-4:line-14 | LONG / ENTERABLE | 40.40 → 39.35 | WIDENING | -2.5990 | -0.9716 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 0.2036 | MODELED_CLOSED_BEFORE_DECISION |
| T / alert-4:line-15 | SHORT / UNDERWAY | 23.80 → 22.20 | TIGHTENING | -6.7227 | 2.1435 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 2.5321 | MODELED_CLOSED_BEFORE_DECISION |
| ELF / alert-5:line-10 | LONG / ENTERABLE | 110.50 → 108.60 | WIDENING | -1.7195 | -0.4999 | -0.2775 | 0.4943 / 3.4863 | 1.1814 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| GME / alert-5:line-11 | LONG / ENTERABLE | 25.01 → 24.78 | WIDENING | -0.9196 | -0.1848 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 0.3054 | MODELED_CLOSED_BEFORE_DECISION |
| HUM / alert-5:line-12 | LONG / ENTERABLE | 404.00 → 408.10 | TIGHTENING | 1.0149 | 0.2004 | -2.4448 | 0.6048 / 3.2513 | 0.8296 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| TEVA / alert-5:line-13 | LONG / ENTERABLE | 39.35 → 39.05 | WIDENING | -0.7624 | -0.2726 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 0.7813 | MODELED_CLOSED_BEFORE_DECISION |
| AAPL / alert-5:line-14 | LONG / ENTERABLE | 336.25 → 343.50 | TIGHTENING | 2.1561 | 1.1916 | 2.1832 | 2.2243 / 0.6104 | 1.9674 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| OMER / alert-5:line-15 | SHORT / ENTERABLE | 17.20 → 17.35 | WIDENING | 0.8721 | -0.1693 | -1.7502 | 2.5347 / 1.9010 | 0.3837 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AAOI / alert-5:line-16 | SHORT / ENTERABLE | 89.82 → 70.70 | TIGHTENING | -21.2870 | 2.0388 | 5.8897 | 8.3644 / 1.1337 | 2.3192 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AMD / alert-5:line-17 | SHORT / ENTERABLE | 569.90 → 519.35 | TIGHTENING | -8.8700 | 1.7356 | 2.9019 | 3.9208 / 1.3133 | 2.1277 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| ANET / alert-5:line-18 | SHORT / ENTERABLE | 191.25 → 176.80 | TIGHTENING | -7.5556 | 1.5562 | 4.1625 | 4.8347 / 0.1232 | 2.1732 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| CDE / alert-5:line-19 | SHORT / ENTERABLE | 16.24 → 14.30 | TIGHTENING | -11.9458 | 2.3592 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 2.8700 | MODELED_CLOSED_BEFORE_DECISION |
| SNDK / alert-5:line-20 | SHORT / ENTERABLE | 1458.00 → 1296.00 | TIGHTENING | -11.1111 | 1.7161 | 4.2763 | 5.5160 / 2.8650 | 2.0876 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| ELF / alert-6:line-15 | LONG / ENTERABLE | 108.60 → 109.20 | TIGHTENING | 0.5525 | 0.1575 | -0.9279 | 0.8152 / 3.4863 | 1.4806 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| GME / alert-6:line-16 | LONG / ENTERABLE | 24.78 → 24.40 | WIDENING | -1.5335 | -0.3080 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 0.0324 | MODELED_CLOSED_BEFORE_DECISION |
| SIG / alert-6:line-17 | LONG / ENTERABLE | 111.80 → 112.50 | TIGHTENING | 0.6261 | 0.1687 | 1.2179 | 2.0558 / 1.9003 | 1.2968 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AAPL / alert-6:line-18 | LONG / UNDERWAY | 343.50 → 344.70 | TIGHTENING | 0.3493 | 0.1940 | 2.0394 | 3.2132 / 0.6104 | 0.6838 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| ANET / alert-6:line-19 | SHORT / UNDERWAY | 176.80 → 175.20 | TIGHTENING | -0.9050 | 0.1681 | 3.4342 | 5.7479 / 0.1232 | 0.4655 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| CDE / alert-6:line-20 | SHORT / UNDERWAY | 14.30 → 13.90 | TIGHTENING | -2.7972 | 0.5010 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 1.0647 | MODELED_CLOSED_BEFORE_DECISION |
| EBAY / alert-7:line-13 | LONG / ENTERABLE | 119.20 → 117.50 | WIDENING | -1.4262 | -0.4736 | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | -0.1616 | MODELED_CLOSED_BEFORE_DECISION |
| GTLB / alert-7:line-14 | LONG / ENTERABLE | 51.60 → 52.10 | TIGHTENING | 0.9690 | 0.1812 | 0.4433 | 1.3475 / 0.9752 | 1.8302 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |

| Revision kind | Source events | Current conditional progress median[min,max] | Old-stop clearance ATR median[min,max] | SPY vol20 median[min,max] | Distinct alert bounds | Setup counts |
|---|---|---|---|---|---|---|
| TIGHTENING | 16 | 2.0394 [-2.4448, 5.8897]; usable 13/16 | 1.6554 [0.4655, 2.8700]; usable 16/16 | 0.0060 [0.0054, 0.0060]; usable 16/16 | 5 | {'ENTERABLE': 12, 'UNDERWAY': 4} |
| WIDENING | 11 | -0.3266 [-1.7502, 0.6338]; usable 4/11 | 0.3054 [-0.1616, 1.2220]; usable 11/11 | 0.0060 [0.0054, 0.0060]; usable 11/11 | 6 | {'ENTERABLE': 11} |

**Tightening revisions follow favorable current conditional price progress** Supporting fraction: 11/13 (84.6%); total source events 16.

Supporting observations: CDE (alert-2:line-12, 0.840879689521); T (alert-2:line-13, 0.215053763441); AAPL (alert-5:line-14, 2.183226715183); AAOI (alert-5:line-16, 5.889672335131); AMD (alert-5:line-17, 2.90187532259); ANET (alert-5:line-18, 4.162464985994); SNDK (alert-5:line-20, 4.276300806219); SIG (alert-6:line-17, 1.217932106763); AAPL (alert-6:line-18, 2.03943893421); ANET (alert-6:line-19, 3.434173669468); GTLB (alert-7:line-14, 0.443262411348).

Counterexamples: HUM (alert-5:line-12, -2.444846125324); ELF (alert-6:line-15, -0.92793339693).

Unavailable: T (alert-4:line-15), CDE (alert-5:line-19), CDE (alert-6:line-20).

Confounders: Hypothetical entry; post-exit observations excluded; direction/sector and co-published decisions confound association. Needed: Independent alert sample with exact entries, publication and revision clocks and compatible units.

**Widening can also follow favorable progress, challenging a profit-tightening-only interpretation** Supporting fraction: 1/4 (25.0%); total source events 11.

Supporting observations: AAPL (alert-2:line-10, 0.633840014085).

Counterexamples: AAPL (alert-3:line-14, -0.375608897236); ELF (alert-5:line-10, -0.277512791605); OMER (alert-5:line-15, -1.750150875075).

Unavailable: CLMT (alert-2:line-11), CLMT (alert-3:line-15), TEVA (alert-4:line-14), GME (alert-5:line-11), TEVA (alert-5:line-13), GME (alert-6:line-16), EBAY (alert-7:line-13).

Confounders: Conditional basis and model-survival censoring; source-open conflicts are retained but current progress unavailable. Needed: Independent source/entry records including adverse and favorable examples.

**Widening coincides with Close within one ATR of the previous stop** Supporting fraction: 9/11 (81.8%); total source events 11.

Supporting observations: AAPL (alert-2:line-10, True); CLMT (alert-2:line-11, True); AAPL (alert-3:line-14, True); TEVA (alert-4:line-14, True); GME (alert-5:line-11, True); TEVA (alert-5:line-13, True); OMER (alert-5:line-15, True); GME (alert-6:line-16, True); EBAY (alert-7:line-13, True).

Counterexamples: CLMT (alert-3:line-15, False); ELF (alert-5:line-10, False).

Unavailable: None.

Confounders: Fixed descriptive one-ATR cut; stop/native units unverified except bounded EBAY; price proximity is not held-position progress or causation. Needed: Compatible quotes and intraday revision/stop activation evidence on a separate sample.

**Revisions move toward the pre-existing direction-selected protective swing** Supporting fraction: 9/25 (36.0%); total source events 27.

Supporting observations: AAPL (alert-2:line-10, True); CLMT (alert-2:line-11, True); AAPL (alert-3:line-14, True); CLMT (alert-3:line-15, True); ELF (alert-5:line-10, True); GME (alert-5:line-11, True); OMER (alert-5:line-15, True); GME (alert-6:line-16, True); EBAY (alert-7:line-13, True).

Counterexamples: CDE (alert-2:line-12, False); T (alert-2:line-13, False); T (alert-4:line-15, False); HUM (alert-5:line-12, False); AAPL (alert-5:line-14, False); AAOI (alert-5:line-16, False); AMD (alert-5:line-17, False); ANET (alert-5:line-18, False); CDE (alert-5:line-19, False); SNDK (alert-5:line-20, False); ELF (alert-6:line-15, False); SIG (alert-6:line-17, False); AAPL (alert-6:line-18, False); ANET (alert-6:line-19, False); CDE (alert-6:line-20, False); GTLB (alert-7:line-14, False).

Unavailable: TEVA (alert-4:line-14), TEVA (alert-5:line-13).

Confounders: Confirmed pivots are agent-selected diagnostics, not expert levels; missing warmup; direction and widening/tightening confound association. Needed: Independent dated annotations identifying levels actually used by the expert.

## Underway transitions

The seven transitions are source facts. Progress does not create a transition. Current progress is unavailable when the model was already closed or its exit path became ambiguous; a separately retained pre-exit summary must not substitute for progress at the transition.

| Symbol / event | H sessions | Conditional progress % / ATR / original R | Conditional MFE / MAE % | Initial / latest source stop | Model-path status |
|---|---|---|---|---|---|
| T / alert-2:line-16 | 1 | 0.2151 / 0.0766 / 0.0667 | 0.7742 / 0.7312 | 24.00 / 23.80 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AAPL / alert-5:line-23 | 4 | 2.1832 / 1.1121 / 4.1798 | 2.2243 / 0.6104 | 339.00 / 343.50 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AAOI / alert-5:line-24 | 1 | 5.8897 / 0.4531 / 0.2436 | 8.3644 / 1.1337 | 89.82 / 70.70 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| AMD / alert-5:line-25 | 1 | 2.9019 / 0.5486 / 0.3244 | 3.9208 / 1.3133 | 569.90 / 519.35 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| ANET / alert-5:line-26 | 1 | 4.1625 / 0.8691 / 0.5827 | 4.8347 / 0.1232 | 191.25 / 176.80 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| CDE / alert-5:line-27 | 4 | UNAVAILABLE / UNAVAILABLE / UNAVAILABLE | UNAVAILABLE / UNAVAILABLE | 16.40 / 14.30 | MODELED_CLOSED_BEFORE_DECISION |
| SNDK / alert-5:line-28 | 1 | 4.2763 / 0.6248 / 0.4002 | 5.5160 / 2.8650 | 1458.00 / 1296.00 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |

AAOI/AMD/ANET/SNDK share one October 22 publication opportunity and the fixed XLK context proxy. Their eligible-session horizons are [1, 1, 1, 1]. Their common market snapshot is one observation, not four independent confirmations.

| Grouped conditional measurement | Median[min,max], usable/4 |
|---|---|
| progress_percent | 4.2194 [2.9019, 5.8897]; usable 4/4 |
| progress_ATR | 0.5867 [0.4531, 0.8691]; usable 4/4 |
| progress_original_R | 0.3623 [0.2436, 0.5827]; usable 4/4 |
| mfe_percent | 5.1754 [3.9208, 8.3644]; usable 4/4 |
| mae_percent | 1.2235 [0.1232, 2.8650]; usable 4/4 |

Existing native-price geometry and 20-session relative strength (fractions, not target returns):

| Transition | Breakout20 | Breakdown20 | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | Stock/SPY20 | Stock/QQQ20 | Stock/RSP20 | Stock/IWM20 | Stock/sector20 |
|---|---|---|---|---|---|---|---|---|---|---|
| T | False | False | -0.0106 | -0.0380 | -0.0690 | -0.0801 | -0.0591 | -0.0915 | -0.0404 | -0.0498 |
| AAPL | True | False | 0.0176 | 0.0285 | 0.0597 | 0.0410 | 0.0905 | -0.0012 | 0.0553 | 0.1069 |
| AAOI | False | True | -0.2029 | -0.3037 | -0.3589 | -0.3234 | -0.2912 | -0.3508 | -0.3141 | -0.2805 |
| AMD | False | True | -0.0935 | -0.1433 | -0.0622 | -0.1894 | -0.1508 | -0.2223 | -0.1783 | -0.1381 |
| ANET | False | True | -0.1042 | -0.1422 | -0.1318 | -0.1648 | -0.1251 | -0.1987 | -0.1534 | -0.1119 |
| CDE | False | True | -0.1073 | -0.1609 | -0.2623 | -0.2641 | -0.2291 | -0.2939 | -0.2539 | -0.2957 |
| SNDK | False | True | -0.1009 | -0.1907 | -0.2116 | -0.2779 | -0.2436 | -0.3072 | -0.2680 | -0.2322 |

| October22 quartet | Breakdown20 | Close/SMA20−1 | Close/SMA50−1 | Range10/prior20 |
|---|---|---|---|---|
| AAOI | True | -0.3037 | -0.3589 | 1.3557 |
| AMD | True | -0.1433 | -0.0622 | 0.7002 |
| ANET | True | -0.1422 | -0.1318 | 1.5232 |
| SNDK | True | -0.1907 | -0.2116 | 0.9706 |

Matched ENTERABLE controls use the same elapsed eligible-session horizon at a source alert opportunity no later than the target transition. All co-published actions are included when checking source state. Later final outcomes do not select controls. Controls with closed/ambiguous conditional model episodes are retained as exclusions. Shared controls and different dates/directions/sectors confound comparison.

| Transition | H | Conditional target progress % | Usable / candidate peers | Favorable controls / usable | Control median[min,max] progress % |
|---|---|---|---|---|---|
| T | 1 | 0.2151 | 3 / 25 | 2/3 (66.7%) | 0.6338 [-0.2656, 0.8409]; usable 3/25 |
| AAPL | 4 | 2.1832 | 0 / 25 | 0/0 (undefined) | UNAVAILABLE [UNAVAILABLE, UNAVAILABLE]; usable 0/25 |
| AAOI | 1 | 5.8897 | 7 / 25 | 3/7 (42.9%) | -0.2656 [-1.4136, 1.8709]; usable 7/25 |
| AMD | 1 | 2.9019 | 7 / 25 | 3/7 (42.9%) | -0.2656 [-1.4136, 1.8709]; usable 7/25 |
| ANET | 1 | 4.1625 | 7 / 25 | 3/7 (42.9%) | -0.2656 [-1.4136, 1.8709]; usable 7/25 |
| CDE | 4 | UNAVAILABLE | 0 / 25 | 0/0 (undefined) | UNAVAILABLE [UNAVAILABLE, UNAVAILABLE]; usable 0/25 |
| SNDK | 1 | 4.2763 | 7 / 25 | 3/7 (42.9%) | -0.2656 [-1.4136, 1.8709]; usable 7/25 |

Favorable movement is not sufficient to assign UNDERWAY. Still-ENTERABLE positive-progress counterexamples at matched horizons: AAPL at 2026-10-19T18:20:00-04:00, 0.6338%; CDE at 2026-10-19T18:20:00-04:00, 0.8409%; OMER at 2026-10-21T18:51:00-04:00, 1.8709%. Shared peers are listed once here; their repetition across transition comparisons is not additional independent evidence.

Favorable-progress evidence: 6/6 (100.0%). Support: T (alert-2:line-16, 0.215053763441); AAPL (alert-5:line-23, 2.183226715183); AAOI (alert-5:line-24, 5.889672335131); AMD (alert-5:line-25, 2.90187532259); ANET (alert-5:line-26, 4.162464985994); SNDK (alert-5:line-28, 4.276300806219). Counterexamples: None among usable observations. Unavailable: CDE.

Completion of an entry setup or deterioration for new entrants cannot be established from movement alone. The existing breakout/pullback and confirmed-swing diagnostics are retained as competing geometry measurements, not expert setup labels.

## Exit interpretation

All 12 DROPs confirm source closure; the actual cause is EXIT_REASON_UNRESOLVED in every case. Stop, target and time hypotheses are nonexclusive price-based explanations. A LONG +1R touch removes at least one-third under the inherited convention and cannot establish a full exit. Intraday stop/target collisions preserve unknown order. Exit-day OHLC are excluded from exposure MFE/MAE; source closure-day candles are included only when fully available before the closure bound.

| Source DROP | Direction | Availability-bound sessions / publication range | Primary stop observation | Conditional stop observation | Conditional +1R observation | Earlier nonprogress flag / terminal time hypothesis |
|---|---|---|---|---|---|---|
| CAT / alert-3:line-21 | SHORT | 2 / [2, 2] | UNAVAILABLE / no supporting modeled observation | UNAVAILABLE / no supporting modeled observation | 2026-10-19 HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN | False / None |
| CLMT / alert-4:line-21 | LONG | 3 / [3, 3] | UNAVAILABLE / no supporting modeled observation | 2026-10-19 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |
| ASST / alert-4:line-22 | SHORT | 1 / [1, 1] | UNAVAILABLE / no supporting modeled observation | 2026-10-21 CANDIDATE_ORDER_UNKNOWN | 2026-10-21 CANDIDATE_ORDER_UNKNOWN | False / None |
| T / alert-5:line-31 | SHORT | 4 / [4, 4] | UNAVAILABLE / no supporting modeled observation | UNAVAILABLE / no supporting modeled observation | 2026-10-21 HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN | True / None |
| TEVA / alert-6:line-26 | LONG | 5 / UNKNOWN; bracket [4, 5] | UNAVAILABLE / no supporting modeled observation | 2026-10-21 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | True / None |
| AAOI / alert-6:line-27 | SHORT | 2 / UNKNOWN; bracket [1, 2] | UNAVAILABLE / no supporting modeled observation | 2026-10-23 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |
| AMD / alert-6:line-28 | SHORT | 2 / UNKNOWN; bracket [1, 2] | UNAVAILABLE / no supporting modeled observation | 2026-10-23 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |
| SNDK / alert-6:line-29 | SHORT | 2 / UNKNOWN; bracket [1, 2] | UNAVAILABLE / no supporting modeled observation | 2026-10-23 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |
| GME / alert-7:line-20 | LONG | 3 / [3, 3] | UNAVAILABLE / no supporting modeled observation | 2026-10-22 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |
| AAPL / alert-7:line-21 | LONG | 6 / [6, 6] | UNAVAILABLE / no supporting modeled observation | 2026-10-26 TRIGGER_OBSERVED_UNDER_ASSUMPTION | 2026-10-19 HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN | True / None |
| SNOW / alert-7:line-22 | SHORT | 1 / UNKNOWN; bracket [1, 2] | UNAVAILABLE / no supporting modeled observation | 2026-10-26 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |
| ANET / alert-7:line-23 | SHORT | 3 / [3, 3] | UNAVAILABLE / no supporting modeled observation | 2026-10-26 TRIGGER_OBSERVED_UNDER_ASSUMPTION | UNAVAILABLE / no supporting modeled observation | False / None |

| Source closure | Initial / latest source stop | Stop revisions | Source setup | Last complete active-path session | Conditional pre-exit MFE / MAE % |
|---|---|---|---|---|---|
| CAT | 748.75 / 748.75 | 0 | ENTERABLE | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE |
| CLMT | 55.25 / 53.02 | 2 | ENTERABLE | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE |
| ASST | 28.45 / 28.45 | 0 | ENTERABLE | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE |
| T | 24.00 / 22.20 | 2 | UNDERWAY | 2026-10-20 | 0.7742 / 1.8495 |
| TEVA | 40.40 / 39.05 | 2 | ENTERABLE | 2026-10-20 | 1.1106 / 1.4969 |
| AAOI | 89.82 / 70.70 | 1 | UNDERWAY | 2026-10-22 | 8.3644 / 1.1337 |
| AMD | 569.90 / 519.35 | 1 | UNDERWAY | 2026-10-22 | 3.9208 / 1.3133 |
| SNDK | 1458.00 / 1296.00 | 1 | UNDERWAY | 2026-10-22 | 5.5160 / 2.8650 |
| GME | 25.01 / 24.40 | 2 | ENTERABLE | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE |
| AAPL | 339.00 / 344.70 | 4 | UNDERWAY | 2026-10-23 | 3.2132 / 0.6104 |
| SNOW | 330.70 / 330.70 | 0 | ENTERABLE | UNAVAILABLE | UNAVAILABLE / UNAVAILABLE |
| ANET | 191.25 / 175.20 | 2 | UNDERWAY | 2026-10-23 | 5.7479 / 0.1232 |

An earlier 2/3/5-session flag is not a terminal time-exit explanation when the model has already closed or its exit path is ambiguous. In those cases terminal exposure is unavailable, rather than assumed to continue until the source DROP.

Actual holding duration is unknown without fills. Publication-based session ranges describe source reporting intervals; where weekly publication is unresolved, the separate ordered-publication/email bracket is explicitly conditional. Fourteen not-dropped histories are right-censored, and the four final additions lack an eligible completed modeled entry before cutoff.

## Long versus short behavior

| Source direction | Positions | Tightening revisions | Widening revisions | Positions widened | Underway | Source closed |
|---|---|---|---|---|---|---|
| LONG | 14 | 6/16 (37.5%) | 10/16 (62.5%) | 6/14 (42.9%) | 1/14 (7.1%) | 4/14 (28.6%) |
| SHORT | 12 | 10/11 (90.9%) | 1/11 (9.1%) | 1/12 (8.3%) | 6/12 (50.0%) | 8/12 (66.7%) |

| Direction | Availability-bound eligible duration | Conditional pre-exit MFE % | Conditional pre-exit MAE % | Conditional pre-exit original-R progress |
|---|---|---|---|---|
| LONG | 2.0000 [0.0000, 6.0000]; usable 14/14 | 1.1106 [0.3200, 3.2132]; usable 9/14 | 1.4969 [0.5862, 3.7681]; usable 9/14 | -0.1940 [-0.5588, 3.9045]; usable 9/14 |
| SHORT | 2.0000 [0.0000, 6.0000]; usable 12/12 | 3.9208 [0.7742, 8.3644]; usable 7/12 | 1.8495 [0.1232, 2.8650]; usable 7/12 | 0.3511 [-0.2267, 0.4808]; usable 7/12 |

Duration mixes censored reporting histories and chosen availability bounds; it is not estimated mean holding time. Excursion distributions omit unavailable/ambiguous exit-day exposure but retain the full source-position denominator. None is realized trade performance.

## Market context

Original commentary, native-price measurements and interpretation are separate. Sector and style exposure, overlapping positions and common alert publication are confounders. RSP/SPY is a participation proxy; true market breadth is unavailable. No stale ES observations are used.

| Bound / session | Source commentary synopsis | Decision counts | SPY daily / 5d / 20d / 60d % | QQQ daily % | SPY volatility expansion |
|---|---|---|---|---|---|
| 2026-10-18T15:21:00-04:00 / 2026-10-16 | Operator-supplied commentary describes energy leadership, technology weakness and a Dow bear-flag short idea. | {'OPEN_NEW_POSITION': 6} | -1.1065 / -1.9677 / 0.2048 / 3.3962 | -2.5000 | True |
| 2026-10-19T18:20:00-04:00 / 2026-10-19 | Operator-supplied commentary describes an S&P/Nasdaq bounce weakening the short setup while the Dow bear flag remains attractive. | {'STOP_CHANGED': 4, 'SETUP_CHANGED': 1} | 0.4232 / -1.4934 / -0.9076 / 3.7284 | 1.2060 | False |
| 2026-10-20T18:26:00-04:00 / 2026-10-20 | Operator-supplied commentary describes a Nasdaq inside day, muted Russell bounce and weekly Dow bear flag, with earnings risk noted. | {'OPEN_NEW_POSITION': 5, 'STOP_CHANGED': 2, 'DROPPED': 1} | 0.3353 / -1.1517 / -0.5599 / 4.0536 | -0.1016 | True |
| 2026-10-21T18:51:00-04:00 / 2026-10-21 | Operator-supplied commentary favors the Nasdaq short context over Dow/Russell and discusses technology-heavy candidates. | {'OPEN_NEW_POSITION': 5, 'STOP_CHANGED': 2, 'DROPPED': 2} | 0.5253 / 0.4535 / 0.6877 / 4.3503 | 1.0549 | False |
| 2026-10-22T18:28:00-04:00 / 2026-10-22 | Operator-supplied commentary describes Nasdaq weakness versus a drifting Dow. | {'STOP_CHANGED': 11, 'SETUP_CHANGED': 6, 'DROPPED': 1} | -1.1810 / -1.0145 / -0.4197 / 4.7295 | -2.8585 | True |
| 2026-10-25T12:57:45+00:00 / 2026-10-23 | Operator-supplied weekly commentary describes bearish pressure across stock indexes; exact publication date remains unresolved. | {'OPEN_NEW_POSITION': 6, 'STOP_CHANGED': 6, 'DROPPED': 4} | -0.5223 / -0.4297 / -1.4753 / 2.4646 | -0.0099 | False |
| 2026-10-26T18:11:00-04:00 / 2026-10-26 | Operator-supplied commentary describes the S&P in a wide range and cleaner Russell/Dow short setups; crude/futures remarks are kept separate from computed equity context. | {'OPEN_NEW_POSITION': 4, 'STOP_CHANGED': 2, 'DROPPED': 4} | 0.7106 / -0.1448 / -0.0313 / 2.4551 | 1.1073 | True |

| Decision type | Events | Usable context | Distinct alert bounds | SPY negative day | Positive day, negative 5d | SPY vol20 expansion |
|---|---|---|---|---|---|---|
| OPEN_NEW_POSITION | 26 | 26 | 5 | 12/26 (46.2%) | 9/26 (34.6%) | 15/26 (57.7%) |
| STOP_CHANGED | 27 | 27 | 6 | 17/27 (63.0%) | 8/27 (29.6%) | 15/27 (55.6%) |
| SETUP_CHANGED | 7 | 7 | 2 | 6/7 (85.7%) | 1/7 (14.3%) | 6/7 (85.7%) |
| DROPPED | 12 | 12 | 5 | 5/12 (41.7%) | 5/12 (41.7%) | 6/12 (50.0%) |

All four ETF return/trend/volatility vectors, participation ratios, stock-to-market/sector strength and event links are retained in market_context.json and decision_features.json. Coincidence with a weak day, rebound proxy or volatility increase does not establish why a source action occurred.

## Limitations

The sample is 26 selected source positions in seven alerts, not an unselected opportunity universe. There are no actual entries, fills or sizes; stop/native-unit compatibility remains extensively unverified; missing intraday sequencing censors exposure; model-survival and source publication opportunities select usable comparisons. Four co-published technology transitions and repeated market snapshots are dependent observations. TEVA has limited history under its new ordinary-share contract; ASST has business/split and sector uncertainty; SNDK is its current separated identity. PR16's weekly publication remains unresolved, with the same separate email-availability assumption. Earnings/action completeness is unknown. No parameter fitting, significance, causal claim, predictive model, realized P&L or statistical-edge conclusion is justified.

## Next research hypotheses

Ranked by strength of evidence and practical relevance; test on a separate, independently selected historical alert sample with the same predeclared definitions:

1. **Direction and widening:** LONG revisions have a higher widening fraction than SHORT revisions. Discovery evidence is source-only: 10/16 (62.5%) versus 1/11 (9.1%). Test the sign of that difference across independent periods, reporting both revision and unique-position/alert denominators. This could identify management asymmetry; source selection and clustered shorts are confounders.

2. **Underway after favorable movement:** signed pre-transition progress is positive more often, or has a higher median, than at equivalent ENTERABLE opportunities. Discovery support 6/6 (100.0%); matched control tables retain exceptions and unavailable cases. Exact entries, publication clocks and compatible units are needed. Shared technology/context exposure is a competing explanation.

3. **Widening near the previous stop:** widening opportunities more often have absolute Close-to-old-stop distance <=1 ATR than matched unchanged/tightening opportunities. Discovery support among widening events is 9/11 (81.8%). Keep one ATR fixed; do not tune it to these 26 positions. Stop-scale validation, intraday clocks and an independent no-change opportunity sample are required; observed proximity alone cannot establish causation.

## Complete sample and individual summaries

| Stock | Direction | Source final | Setup | Source event count | Conditional path status |
|---|---|---|---|---|---|
| [AAPL](summary-AAPL.md) | LONG | CLOSED | UNDERWAY | 7 | MODELED_CLOSED_BEFORE_DECISION |
| [CLMT](summary-CLMT.md) | LONG | CLOSED | ENTERABLE | 4 | MODELED_CLOSED_BEFORE_DECISION |
| [TEVA](summary-TEVA.md) | LONG | CLOSED | ENTERABLE | 4 | MODELED_CLOSED_BEFORE_DECISION |
| [CAT](summary-CAT.md) | SHORT | CLOSED | ENTERABLE | 2 | MODELED_CLOSED_BEFORE_DECISION |
| [CDE](summary-CDE.md) | SHORT | OPEN | UNDERWAY | 5 | MODELED_CLOSED_BEFORE_DECISION |
| [T](summary-T.md) | SHORT | CLOSED | UNDERWAY | 5 | MODELED_CLOSED_BEFORE_DECISION |
| [ELF](summary-ELF.md) | LONG | OPEN | ENTERABLE | 3 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [HUM](summary-HUM.md) | LONG | OPEN | ENTERABLE | 2 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [SIG](summary-SIG.md) | LONG | OPEN | ENTERABLE | 2 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [ASST](summary-ASST.md) | SHORT | CLOSED | ENTERABLE | 2 | AMBIGUOUS_EXIT_PATH |
| [OMER](summary-OMER.md) | SHORT | OPEN | ENTERABLE | 2 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [GME](summary-GME.md) | LONG | CLOSED | ENTERABLE | 4 | MODELED_CLOSED_BEFORE_DECISION |
| [AAOI](summary-AAOI.md) | SHORT | CLOSED | UNDERWAY | 4 | MODELED_CLOSED_BEFORE_DECISION |
| [AMD](summary-AMD.md) | SHORT | CLOSED | UNDERWAY | 4 | MODELED_CLOSED_BEFORE_DECISION |
| [ANET](summary-ANET.md) | SHORT | CLOSED | UNDERWAY | 5 | MODELED_CLOSED_BEFORE_DECISION |
| [SNDK](summary-SNDK.md) | SHORT | CLOSED | UNDERWAY | 4 | MODELED_CLOSED_BEFORE_DECISION |
| [ABBV](summary-ABBV.md) | LONG | OPEN | ENTERABLE | 1 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [CNQ](summary-CNQ.md) | LONG | OPEN | ENTERABLE | 1 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [EBAY](summary-EBAY.md) | LONG | OPEN | ENTERABLE | 2 | MODELED_CLOSED_BEFORE_DECISION |
| [GTLB](summary-GTLB.md) | LONG | OPEN | ENTERABLE | 2 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [MMM](summary-MMM.md) | LONG | OPEN | ENTERABLE | 1 | AVAILABLE_AT_LAST_OBSERVABLE_SESSION |
| [SNOW](summary-SNOW.md) | SHORT | CLOSED | ENTERABLE | 2 | MODELED_CLOSED_BEFORE_DECISION |
| [SAIL](summary-SAIL.md) | LONG | OPEN | ENTERABLE | 1 | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| [SLB](summary-SLB.md) | LONG | OPEN | ENTERABLE | 1 | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| [GE](summary-GE.md) | SHORT | OPEN | ENTERABLE | 1 | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |
| [SCCO](summary-SCCO.md) | SHORT | OPEN | ENTERABLE | 1 | NO_ELIGIBLE_COMPLETED_ENTRY_SESSION |

## Measurement definitions and provenance

- **decision_clock:** Immediately before PR16 effective_at: subtract one microsecond; original publication and email bound remain separate.
- **price_availability:** PR16 XNYS cash close +60 minutes strictly before decision bound; no current intraday candle.
- **entry:** Unchanged PR16 next eligible RTH Open scenario; actual fills and size unknown.
- **progress:** s*(Close-E), percent=100*s*(Close-E)/E; s=+1 LONG,-1 SHORT.
- **mfe:** max(0,max(High-E)) LONG; max(0,max(E-Low)) SHORT, over complete eligible active-session bars.
- **mae:** max(0,max(E-Low)) LONG; max(0,max(High-E)) SHORT; reported as a nonnegative adverse excursion.
- **risk:** Unchanged PR16 hypothetical original R: E-initial_stop LONG, initial_stop-E SHORT; revisions never reset R.
- **atr:** Existing Panel/shared-wheel simple ATR14; progress/excursions use pre-entry ATR, stop adjustments use pre-decision ATR.
- **exit_censoring:** Exclude all price-trigger/ambiguous exit-day OHLC: daily extrema/Close may follow exit; earlier full-session path is a separate pre-exit summary.
- **source_drop_censoring:** Source DROP only known when its own bound is strictly before cutoff; after-hours modeled source closure may retain earlier completed RTH bar.
- **stop_change_percent:** 100*(new-old)/old, source-only; direction-aware tightening sign=s*(new-old).
- **stop_adjustment_atr:** s*(new-old)/pre-decision ATR14; conditional unless nominal stop/native units corroborated.
- **previous_stop_clearance:** s*(Close-old_stop), divided by Close for percent or pre-decision ATR; this is a price observation, not post-exit exposure.
- **near_stop:** abs(Close-old_stop)/ATR14 <=1; fixed agent-defined descriptive cut, not fitted or a Grimes rule.
- **sma10:** Arithmetic mean of exactly10 available completed Closes; Close/SMA10-1; SMA20/50 reused from Panel.
- **swing:** Most recent Panel strict3-bar pivot confirmed by the previous available session; protective Low for LONG, High for SHORT; never choose pivot after seeing revised stop.
- **recent_swing_distances:** For both currently confirmed High/Low: Close-level, 100*(Close/level-1), and (Close-level)/pre-decision ATR; currently confirmed levels are distinct from the stricter previous-session protective-pivot hypothesis.
- **toward_swing:** abs(new_stop-preexisting_protective_pivot) < abs(old_stop-pivot); equality is not toward.
- **relative_strength:** Panel ratio_change: (stock_t/proxy_t)/(stock_t-n/proxy_t-n)-1 on matching calendar sessions, n=1,5,20,60.
- **market_weakness:** SPY daily price return <0; rebound proxy=positive SPY day with negative trailing5-session return; not a causal regime classification.
- **volatility_expansion:** SPY realized_volatility20 now / prior available session value >1; continuous ratio retained.
- **elapsed_sessions:** Count eligible calendar sessions since scenario entry with cash-close+60 minutes before bound, never count rows after skipping gaps.
- **duration:** Publication-based eligible completed-session count/range, not actual holding duration; unknown weekly publication stays null; email-bound scenario separately labeled.
- **matched_controls:** Other source-OPEN ENTERABLE episodes at their first alert opportunity after the same Hth eligible session, before H+1 session and no later than target transition bound; evaluate whole co-published alert; no future final-state filtering.
- **time_stop:** Reuse PR16 available 2/3/5-session nonpositive-progress exploratory flags known before source closure; no definitive time exit.
- **inference:** Selected discovery sample; report observations, counterexamples and usable denominators; no optimization, significance, realized P&L or causal identification.

Authoritative PR16 bundle: `4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604`. Inspected merged main: `35f0a4b1f138b3606180a1b3ec29a049422f530e`; PR16 head: `3a2fd4757a7bc81166b005dcbb1a5ffabf8d03b5`. Original subscriber content and raw provider frames remain in the embedded local parent. Public reports contain derived facts and paraphrased commentary, not full subscriber originals.
