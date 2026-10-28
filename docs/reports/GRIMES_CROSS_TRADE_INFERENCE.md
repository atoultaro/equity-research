# Grimes cross-trade inference — PR9B

The new evidence separates three stop-touch recoveries from EBAY’s adverse Close, while CDE isolates a mandatory-target failure. These distinctions improve interpretation without identifying an operational policy. A rule fitting every observed alert may owe its fit to sparse or censored observations.

## Fixed cohort and clustered comparisons

All 26 source episodes are retained, including 12 source CLOSED and 14 OPEN. The 22 observed next-Open entries exclude right-censored SAIL, SLB, GE and SCCO. After removing CLMT, TEVA, GME, EBAY and control CDE, the remaining 21 comprise 17 observed episodes and those 4 censored episodes. Rows below count episode compatibility, not independent experiments: co-published actions are one alert cluster per episode, and cross-trade evidence is grouped by shared alert IDs in JSON. Final source OPEN is a separate constraint, not a new alert. Fully compatible requires at least one later source alert and no unresolved check. UNRESOLVED includes a source DROP after a hypothetical earlier exit: matching final CLOSED does not establish matching closure cause.

| Weekly clock | H1 management convention | Fully compatible | Robust conflict | Path-dependent | Unresolved | No later alerts |
| --- | --- | --- | --- | --- | --- | --- |
| EARLY_BEFORE_FIRST_OPEN | INTRADAY_HARD_STOP | 10 | 4 | 0 | 5 | 3 |
| EARLY_BEFORE_FIRST_OPEN | CLOSE_CONFIRMATION | 11 | 1 | 0 | 7 | 3 |
| EARLY_BEFORE_FIRST_OPEN | NEXT_OPEN_AFTER_CLOSE | 19 | 0 | 0 | 0 | 3 |
| EARLY_BEFORE_FIRST_OPEN | CLOSE_REVIEW_NEXT_OPEN | 19 | 0 | 0 | 0 | 3 |
| LATE_EMAIL_BOUND | INTRADAY_HARD_STOP | 7 | 4 | 0 | 8 | 3 |
| LATE_EMAIL_BOUND | CLOSE_CONFIRMATION | 11 | 1 | 0 | 7 | 3 |
| LATE_EMAIL_BOUND | NEXT_OPEN_AFTER_CLOSE | 19 | 0 | 0 | 0 | 3 |
| LATE_EMAIL_BOUND | CLOSE_REVIEW_NEXT_OPEN | 19 | 0 | 0 | 0 | 3 |
| FIRST_SESSION_CLOSE_COMPATIBLE | INTRADAY_HARD_STOP | 7 | 4 | 0 | 8 | 3 |
| FIRST_SESSION_CLOSE_COMPATIBLE | CLOSE_CONFIRMATION | 11 | 1 | 0 | 7 | 3 |
| FIRST_SESSION_CLOSE_COMPATIBLE | NEXT_OPEN_AFTER_CLOSE | 19 | 0 | 0 | 0 | 3 |
| FIRST_SESSION_CLOSE_COMPATIBLE | CLOSE_REVIEW_NEXT_OPEN | 19 | 0 | 0 | 0 | 3 |

Hard-stop H1 under the late clock has 7 fully compatible episodes,4 robust protective conflicts,8 unresolved DROP cases and 3 without later alerts. Removing four cases and CDE leaves **6 fully compatible,0 robust conflicts,8 unresolved and 3 no-later-alert** among 17 observed comparison episodes. Absence of a robust contradiction in 18/22 overall is weaker than positive support for a stop rule. The early clock changes AAOI, AMD and SNDK from unresolved DROP-after-exit cases to compatible source closure before that price path. This is publication sensitivity, not three additional independent confirmations.

Closing confirmation reduces robust H1 conflicts from 4 to 1 under every weekly clock. CLMT and GME move to unresolved DROP attribution, TEVA becomes fully compatible, and EBAY still conflicts. The additional rise from 7 to 11 fully compatible under the late clock also includes AAOI, AMD and SNDK; inspect their source/Close timings in JSON. An unconditional next-Open exit after a closing breach fits 19 later-alert cases and 3 final-state-only cases, just like the existing review at the source-status level. This is **observational equivalence at this cutoff**, not equivalent future exits: the unconditional rule must execute a queued exit even after an evening stop revision, whereas review may retain exposure. EBAY’s queued October 27 exit is unobserved. No policy is inferred from that censoring.

## Delayed-entry falsification across 26 episodes

D1 uses a reported-stop touch/recovery, D2 two protective Closes, with the first trigger only, three completed eligible sessions, Close+60minute availability and next-Open execution reference. The stop level must already be known at that day’s Open. These rules are explicit competing explanations, not reported Grimes rules, and are not optimized.

| Weekly clock | Fixed rule | 26-episode outcomes |
| --- | --- | --- |
| EARLY_BEFORE_FIRST_OPEN | RECLAIM_THEN_NEXT_OPEN | CONSTRUCTED: 4; NO_OBSERVED_TRIGGER: 18; RIGHT_CENSORED_NO_H1_ENTRY: 4 |
| EARLY_BEFORE_FIRST_OPEN | TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | CONSTRUCTED: 10; NO_OBSERVED_TRIGGER: 6; REJECTED_NONPROTECTIVE_ENTRY: 1; RIGHT_CENSORED_NO_H1_ENTRY: 4; SOURCE_DROPPED_BEFORE_ACTIVATION: 1; TRIGGER_OBSERVED_ENTRY_RIGHT_CENSORED: 4 |
| LATE_EMAIL_BOUND | RECLAIM_THEN_NEXT_OPEN | CONSTRUCTED: 3; NO_OBSERVED_TRIGGER: 16; RIGHT_CENSORED_NO_H1_ENTRY: 4; SOURCE_DROPPED_BEFORE_ACTIVATION: 3 |
| LATE_EMAIL_BOUND | TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | CONSTRUCTED: 10; NO_OBSERVED_TRIGGER: 7; REJECTED_NONPROTECTIVE_ENTRY: 1; RIGHT_CENSORED_NO_H1_ENTRY: 4; SOURCE_DROPPED_BEFORE_ACTIVATION: 4 |
| FIRST_SESSION_CLOSE_COMPATIBLE | RECLAIM_THEN_NEXT_OPEN | CONSTRUCTED: 3; NO_OBSERVED_TRIGGER: 16; RIGHT_CENSORED_NO_H1_ENTRY: 4; SOURCE_DROPPED_BEFORE_ACTIVATION: 3 |
| FIRST_SESSION_CLOSE_COMPATIBLE | TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | CONSTRUCTED: 10; NO_OBSERVED_TRIGGER: 7; REJECTED_NONPROTECTIVE_ENTRY: 1; RIGHT_CENSORED_NO_H1_ENTRY: 4; SOURCE_DROPPED_BEFORE_ACTIVATION: 4 |

At the late clock, D1 constructs CLMT Tuesday, TEVA Thursday and GME Friday. All require at least one earlier source revision to be interpreted as management of an intended plan. GME’s Friday entry still breaches24.78 before the late weekly revision. D2 rejects TEVA at Wednesday Open 40.10 because its then-known 40.40 stop gives nonpositive long risk; it never buys first and repairs the stop retroactively. D2 cannot enter CAT before source DROP. It also leaves AAPL/CLMT/CDE/T/ELF/HUM/OMER/ANET pre-entry source actions unresolved. T’s already-reported UNDERWAY before D2 activation specifically weakens a universal pending-plan reading. Neither D1 nor D2 produces a trigger for EBAY. No trigger does not establish that Grimes had no actual trade. Thus delayed activation can explain some exposure histories only conditionally; it does not uniformly outperform next-Open without added semantic assumptions.

## Stop revisions, market context and dependence

The 27 stop changes comprise 16 directional tightenings and 11 loosenings across 6 shared alert clusters. They are not27 independent behavioral observations. Signed direction accounts for short stops.

| Shared alert | Loosenings (symbol old→new) | Tightenings (symbols) |
| --- | --- | --- |
| alert-2 | AAPL 339.0→337.8; CLMT 55.25→53.4 | CDE, T |
| alert-3 | AAPL 337.8→336.25; CLMT 53.4→53.02 | none |
| alert-4 | TEVA 40.4→39.35 | T |
| alert-5 | TEVA 39.35→39.05; ELF 110.5→108.6; OMER 17.2→17.35; GME 25.01→24.78 | AAPL, CDE, HUM, AAOI, AMD, ANET, SNDK |
| alert-6 | GME 24.78→24.4 | AAPL, CDE, ELF, SIG, ANET |
| alert-7 | EBAY 119.2→117.5 | GTLB |

The four protective-conflict cases are all LONG/ENTERABLE and all their disputed continuation clusters occur in the same seven-alert market episode. CLMT and TEVA are loosened following intraday breaches that recovered by the Close; GME is similarly loosened after Thursday’s recovery and again in the weekly alert. EBAY is loosened even after an adverse Close. Counterexample OMER also widens17.20→17.35 as a SHORT/ENTERABLE without the same hard-stop continuation failure. A stop adjustment alone cannot distinguish intended risk from an order.

The per-decision tables retain ATR14, SMA20/50, pre-known confirmed pivots, SPY/QQQ20-session returns and relative SPY strength. CLMT, GME and EBAY have longer native histories; TEVA lacks SMA50/pivot warmup. Three outliers exhibit stop-touch recoveries during shared QQQ weakness and a mixed SPY path; that concentration is descriptive. We cannot separate regime, side, setup type and alert-date effects with this selected sample. Other source ENTERABLE trades do not force the same contradiction, while CDE UNDERWAY remains hard-stop compatible. ENTERABLE may mix intended and active exposure, but this data does not demonstrate that interpretation.

## What survives and what cannot be identified

- Supported conditional finding: closing confirmation explains the three recovered-close continuations with less discretion than next-Open review.
- Robust counterexample: EBAY already-held exposure fails both intraday and Close-confirmed stops; a late entry cannot repair an adverse final Close.
- CDE shows that full+1R realization can be too restrictive even when ordinary protective stops are compatible. Partial runners are plausible, quantities unidentified.
- Late intraday entry is particularly feasible for TEVA; GME depends on weekly publication timing; CLMT’s final-bar breach remains unresolved.
- No rule identifies actual fills, position size, stop-order type or discretionary intent. No predictive model, historical universe inference or profitability claim follows.

**CLOSE_REVIEW_NEXT_OPEN is an exploratory explanation, not evidence of Grimes’ actual stop-order convention.** Its fixed complexity cost 2 does not turn compatibility into identification. The new unconditional next-Open diagnostic is less discretionary but remains a censored alternative at this cutoff.

## Provenance, preservation and offline reproduction

The local immutable study embeds the 139-member PR19 sensitivity parent and the four-window native capture, revalidating PR19’s semantic chain before deriving these outputs. The new layer lives outside the pinned reconstruction/lifecycle implementation directories. No execution simulator, original source ledger, frozen result or trade-status CSV is changed. Public derived evidence includes original source event IDs/hashes, qualified identities, all three clocks, old candidate/policy outcomes, new diagnostic outcomes and explicit hypothesis verdicts. Native provider returns and complete subscriber inputs remain local.

```sh
PYTHONPATH=src .venv/bin/python scripts/grimes_forensics.py --help
PYTHONPATH=src .venv/bin/python scripts/grimes_forensics.py freeze --parent runs/grimes-management-sensitivity-20261028-v1/study-v1 --intraday runs/grimes-forensics-20261018-26-v1/intraday-v1 --documentary docs/evidence/pr9b-forensics-v1/documentary.json --output runs/grimes-forensics-20261018-26-v1/study-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_forensics.py replay --study runs/grimes-forensics-20261018-26-v1/study-NEW --output runs/grimes-forensics-20261018-26-v1/replay-NEW
.venv/bin/python -m pytest -q
```

Use unused output paths. Offline freeze/replay denies network connections. The separate capture script requires explicit `--connect --read-only-api-confirmed`, local port and client ID; it is never invoked by tests or offline research commands. Retrieval windows are fixed to CLMT October 19, TEVA October 21 and GME October 22–23; no further acquisition is needed to replay. Public-only readers can inspect derived evidence; full native semantic replay requires retained local parent/capture bundles.

See [verification record](../evidence/pr9b-forensics-v1/validation.json) for exact hashes, regression results and preservation checks.
