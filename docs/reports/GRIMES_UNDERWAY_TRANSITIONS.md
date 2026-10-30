# Grimes ENTERABLE → UNDERWAY transitions

UNDERWAY means the source judges a setup too extended for attractive fresh entry. It establishes neither a profitable held position nor an executed entry. This study describes the observable boundary without fitting a threshold or assuming universal +1R.

Native semantic study SHA256: `fbeed403c844c47ff11824d8c9977e7be7d43689a04c10e0addf267cfe77bce7`. Public evidence SHA256: `1138634f02be7b1921e7cc395d3fef0a4d7eb596a672e702e5cb53bbd5c2627e`. [Derived evidence and input registry](../evidence/pr9c-setup-opportunities-v1/manifest.json); [validation](../evidence/pr9c-setup-validation-v1/validation.json).

There are 14 source transitions across 5 shared alert clusters. Only 7 have new completed daily reference movement: 1 LONG and 6 SHORT across 2 clusters. The additional seven reports lack October 27–29 daily evidence. Scenarios are conditional timing sensitivity, not replicated observations.

## Predeclared measurements

Directional movement is sign × (available Close − anchor price), normalized separately by anchor completed ATR14 and current completed ATR14. Anchors are ADDED’s available Close, the latest eligible opportunity Close before the assessment, the last explicit ENTERABLE assessment Close, and the first eligible regular Open after ADDED when its full daily bar is already available by the transition. None is an observed entry; ATR distance is not initial R. Co-published revisions are outcomes of one atomic assessment and cannot become prior predictors of that same transition.

The machine evidence retains each anchor session/price/ATR, previous and newly published stops, favorable-session counts, signed SMA10/20 extension, SMA50, confirmed swing/prior-20 distances, volatility, compression and relative SPY movement. Missing features stay unavailable; TEVA’s inherited short history remains insufficient for SMA50. Date-only EARLY/CLOSE clocks can have no newly completed observation, which is not evidence of no intraday movement.

## LATE conditional schedule: all transitions

| Symbol | Direction | UNDERWAY alert | Last explicit E alert | Available session | Added Close ATR | Prior opportunity Close ATR | First Open ATR | Close-to-new-stop ATR | Favorable sessions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T | SHORT | alert-2 | alert-1 | 2026-10-19 | 0.368 | 0.368 | 0.077 | 0.941 | 1 |
| AAPL | LONG | alert-5 | alert-3 | 2026-10-22 | 0.712 | 1.451 | 1.112 | 0.776 | 2 |
| AAOI | SHORT | alert-5 | alert-4 | 2026-10-22 | 0.984 | 0.984 | 0.453 | 0.280 | 1 |
| AMD | SHORT | alert-5 | alert-4 | 2026-10-22 | 1.619 | 1.619 | 0.549 | 0.392 | 1 |
| ANET | SHORT | alert-5 | alert-4 | 2026-10-22 | 1.551 | 1.551 | 0.869 | 0.617 | 1 |
| CDE | SHORT | alert-5 | alert-2 | 2026-10-22 | 2.058 | 1.965 | 2.045 | 0.511 | 2 |
| SNDK | SHORT | alert-5 | alert-4 | 2026-10-22 | 1.301 | 1.301 | 0.625 | 0.371 | 1 |
| SAIL | LONG | operator-20261027 | alert-7 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| SLB | LONG | operator-20261027 | alert-7 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| GTLB | LONG | operator-20261028 | operator-20261027 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| DUK | LONG | operator-20261029 | operator-20261028 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| MMM | LONG | operator-20261029 | alert-6 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| PAA | LONG | operator-20261029 | operator-20261028 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| SIG | LONG | operator-20261029 | alert-6 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |

## Same-direction setups remaining ENTERABLE

Controls were ENTERABLE before the same alert and remain so afterward. Newly ADDED setups are not controls. An omitted control carries its last reported eligibility; omission is not a new explicit attractiveness assessment. Repeated OMER comparisons in one alert are a single shared control observation, not independent corroboration. The table deduplicates controls by alert and setup.

| Alert | Control | Direction | Assessment | Added Close ATR | Prior opportunity Close ATR | Close-to-stop ATR |
| --- | --- | --- | --- | --- | --- | --- |
| alert-2 | CAT | SHORT | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | 0.166 | 0.166 | 0.755 |
| alert-2 | CDE | SHORT | EXPLICIT_UPDATE | 0.181 | 0.181 | 1.233 |
| alert-5 | TEVA | LONG | EXPLICIT_UPDATE | -1.140 | -0.379 | 1.054 |
| alert-5 | ELF | LONG | EXPLICIT_UPDATE | 0.065 | 0.065 | 1.681 |
| alert-5 | HUM | LONG | EXPLICIT_UPDATE | -0.312 | -0.312 | 0.629 |
| alert-5 | SIG | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | 0.272 | 0.272 | 1.235 |
| alert-5 | GME | LONG | EXPLICIT_UPDATE | -0.760 | -0.760 | 0.490 |
| alert-5 | OMER | SHORT | EXPLICIT_UPDATE | -0.348 | -0.348 | 0.553 |
| operator-20261027 | ELF | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261027 | HUM | LONG | EXPLICIT_UPDATE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261027 | SIG | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261027 | ABBV | LONG | EXPLICIT_UPDATE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261027 | CNQ | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261027 | GTLB | LONG | EXPLICIT_UPDATE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261027 | MMM | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261028 | SIG | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261028 | CNQ | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261028 | MMM | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261028 | PLTR | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| operator-20261029 | CNQ | LONG | CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |

## What the evidence can identify

At the October 22 cluster, five SHORT transitions have positive directional extension from ADDED (roughly 0.98–2.06 anchor ATR), while the available SHORT control OMER moves adversely (about −0.35 ATR). AAPL advances about 0.71 ATR from ADDED but 1.45 ATR from its prior opportunity assessment; the chosen causal reference matters. T becomes UNDERWAY after about 0.37 ATR from ADDED, while CAT/CDE controls advance about 0.17/0.18 ATR. These are descriptive associations, not independent threshold validation.

A single universal one-ATR rule cannot explain these reports across anchors and directions. The measurable LONG sample is one transition; six SHORT transitions share only two alerts. No balanced classification accuracy, fitted cutoff, causal decision rule or trading edge follows. Current volatility/structure may help formulate future hypotheses, but cannot establish why the source changed state. Newer mostly LONG reports cannot close this gap without their missing daily observations.

SAIL explicitly returns from UNDERWAY to ENTERABLE on October 29 using stop 20.70. This is direct source evidence that eligibility can reopen; absent October 27–29 prices, the price condition motivating the return is unidentified. Actual entries, exits, sizing, execution convention and returns remain unknown.

The original Model E results (4/26 revision directions and 3/26 intervals) remain exploratory failures. This amendment neither changes those targets nor treats source backfill as new prospective success. Future held-out eligibility observations, complete contemporaneous price evidence and explicit forecast registration are needed before evaluating an explanatory rule.
