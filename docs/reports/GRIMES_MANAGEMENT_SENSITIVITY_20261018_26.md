## Management-policy sensitivity amendment

CLOSE_REVIEW_NEXT_OPEN is an exploratory explanation, not evidence of Grimes' actual stop-order convention. Its additional flexibility can improve source compatibility without identifying the policy that generated the alerts. This comparison reuses unchanged frozen entries, daily paths, source facts and ranking vectors; it does not refit a simulator.

The fixed cohort contains 22 episodes with observed, complete candidate paths under LATE_EMAIL_BOUND. Excluded right-censored episodes: SAIL, SLB, GE, SCCO. Clocks are evaluated separately; they are not pooled as independent trades.

Each co-published alert is one cluster. Final reported OPEN is a separate constraint, never another alert. The inherited ranking vector counts that final constraint once: EBAY's two conflicts mean one actual alert plus final OPEN, not two alerts. A fully compatible entry must be ACTIVE_COMPATIBLE at every later source cluster and final-state check, with at least one later alert. DROP after an earlier hypothetical exit has unresolved cause, not automatic agreement or robust conflict. The first five count columns partition the cohort: at least one fully compatible entry; otherwise every observed entry has a robust conflict; otherwise at least one path-dependent entry whose other checks are compatible; otherwise unresolved; or no later alerts. Robust conflict means all modeled extrema-order possibilities are closed before a continued source-management constraint. The last two columns overlap: any path-dependent check, and any clustered compatibility signature shared with a different policy, possibly at another observed entry. Equivalence is shown as all matching signatures / fully compatible matching signatures: two models can be equivalently wrong. It excludes final-state-only cases and means equivalent source-status explanations, not identical exits, sizes or P&L. Candidate-level details and symbols behind every count are in sensitivity.json.

### LATE_EMAIL_BOUND

| Policy | ≥1 fully compatible | All entries conflict | Path-dependent only | Other unresolved | No later alerts | Any path check | Equivalent (all / compatible) |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL_EXIT_AT_1R | 6 | 6 | 0 | 7 | 3 | 0 | 17 / 6 |
| PARTIAL_50_AT_1R | 7 | 4 | 0 | 8 | 3 | 0 | 19 / 7 |
| HOLD_WITH_REPORTED_STOPS | 7 | 4 | 0 | 8 | 3 | 0 | 19 / 7 |
| CLOSE_REVIEW_NEXT_OPEN | 19 | 0 | 0 | 0 | 3 | 0 | 7 / 7 |

Hard-stop-only re-ranking preserves the original lexicographic evidence score and simplicity weights, filtering out deferred review. It can select a least-conflicting explanation that still fails a source constraint. Entry ranks minimize each entry's best eligible policy vector; no profit, target or threshold is optimized.

Changed leading entry sets: none. Changed ordinal entry ranks: none. Changed best entry vectors: AAPL, CLMT, TEVA, T, ASST, GME, AAOI, AMD, ANET, SNDK, EBAY, SNOW. Best hard-stop explanation still conflicts: CLMT, TEVA, GME, EBAY.

| Episode | All-policy leaders | Hard-stop-only leaders | Best hard-stop vector |
|---|---|---|---|
| AAPL | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -4, 0, -2] |
| CLMT | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| TEVA | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| CAT | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| CDE | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -3, 0, -2] |
| T | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| ELF | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| HUM | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| SIG | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ASST | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| OMER | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| GME | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; H4_PULLBACK/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H4_PULLBACK/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| AAOI | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; H3_CONFIRMATION/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| AMD | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ANET | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| SNDK | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ABBV | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| CNQ | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| EBAY | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| GTLB | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| MMM | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| SNOW | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |

### EARLY_BEFORE_FIRST_OPEN

| Policy | ≥1 fully compatible | All entries conflict | Path-dependent only | Other unresolved | No later alerts | Any path check | Equivalent (all / compatible) |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL_EXIT_AT_1R | 9 | 6 | 0 | 4 | 3 | 0 | 17 / 9 |
| PARTIAL_50_AT_1R | 10 | 4 | 0 | 5 | 3 | 0 | 19 / 10 |
| HOLD_WITH_REPORTED_STOPS | 10 | 4 | 0 | 5 | 3 | 0 | 19 / 10 |
| CLOSE_REVIEW_NEXT_OPEN | 19 | 0 | 0 | 0 | 3 | 0 | 10 / 10 |

Hard-stop-only re-ranking preserves the original lexicographic evidence score and simplicity weights, filtering out deferred review. It can select a least-conflicting explanation that still fails a source constraint. Entry ranks minimize each entry's best eligible policy vector; no profit, target or threshold is optimized.

Changed leading entry sets: none. Changed ordinal entry ranks: none. Changed best entry vectors: AAPL, CLMT, TEVA, T, ASST, GME, ANET, EBAY, SNOW. Best hard-stop explanation still conflicts: CLMT, TEVA, GME, EBAY.

| Episode | All-policy leaders | Hard-stop-only leaders | Best hard-stop vector |
|---|---|---|---|
| AAPL | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -4, 0, -2] |
| CLMT | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| TEVA | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| CAT | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| CDE | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -3, 0, -2] |
| T | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| ELF | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| HUM | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| SIG | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ASST | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| OMER | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| GME | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; H4_PULLBACK/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H4_PULLBACK/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| AAOI | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| AMD | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| ANET | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| SNDK | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| ABBV | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| CNQ | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| EBAY | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| GTLB | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| MMM | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| SNOW | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |

### FIRST_SESSION_CLOSE_COMPATIBLE

| Policy | ≥1 fully compatible | All entries conflict | Path-dependent only | Other unresolved | No later alerts | Any path check | Equivalent (all / compatible) |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL_EXIT_AT_1R | 6 | 6 | 0 | 7 | 3 | 0 | 17 / 6 |
| PARTIAL_50_AT_1R | 7 | 4 | 0 | 8 | 3 | 0 | 19 / 7 |
| HOLD_WITH_REPORTED_STOPS | 7 | 4 | 0 | 8 | 3 | 0 | 19 / 7 |
| CLOSE_REVIEW_NEXT_OPEN | 19 | 0 | 0 | 0 | 3 | 0 | 7 / 7 |

Hard-stop-only re-ranking preserves the original lexicographic evidence score and simplicity weights, filtering out deferred review. It can select a least-conflicting explanation that still fails a source constraint. Entry ranks minimize each entry's best eligible policy vector; no profit, target or threshold is optimized.

Changed leading entry sets: none. Changed ordinal entry ranks: none. Changed best entry vectors: AAPL, CLMT, TEVA, T, ASST, GME, AAOI, AMD, ANET, SNDK, EBAY, SNOW. Best hard-stop explanation still conflicts: CLMT, TEVA, GME, EBAY.

| Episode | All-policy leaders | Hard-stop-only leaders | Best hard-stop vector |
|---|---|---|---|
| AAPL | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -4, 0, -2] |
| CLMT | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| TEVA | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| CAT | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| CDE | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -3, 0, -2] |
| T | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| ELF | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| HUM | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| SIG | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ASST | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| OMER | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| GME | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; H4_PULLBACK/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H4_PULLBACK/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| AAOI | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN; H3_CONFIRMATION/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS; H3_CONFIRMATION/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| AMD | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ANET | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -2, 0, -2] |
| SNDK | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| ABBV | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| CNQ | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| EBAY | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [2, 0, 0, -2] |
| GTLB | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, -1, 0, -2] |
| MMM | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |
| SNOW | H1_NEXT_OPEN/CLOSE_REVIEW_NEXT_OPEN | H1_NEXT_OPEN/HOLD_WITH_REPORTED_STOPS | [0, 0, 0, -2] |

These counts quantify sensitivity within a fixed source-selected sample and finite entry/policy menu. They cannot identify actual fills, partial-exit fractions, stop-order type or discretionary intent, nor resolve all intraday paths. No later-alert cases supply only a final source constraint; equivalent policies and uncertain DROP causes must not be promoted to policy identification. Removing deferred review leaves stop geometry, quote progress and source-reported statuses unchanged. A better-fitting deferred-review explanation establishes sensitivity to assumptions, not evidence that Grimes used deferred review. Zero path-dependent source-compatibility checks does not resolve all intraday outcomes: ASST can have different stop/target exit causes while both paths are already closed before the same unresolved source DROP.

### Offline reproduction

Use unused output directories. The parent is the existing immutable PR19 study-v4; its full native/source proof stays local. The new layer verifies and rederives that parent before aggregating or replaying the sensitivity results. It lives outside the original reconstruction package so historical implementation identities and v4 replay remain valid.

```sh
PYTHONPATH=src .venv/bin/python scripts/grimes_management_sensitivity.py --help
PYTHONPATH=src .venv/bin/python scripts/grimes_management_sensitivity.py freeze --study runs/grimes-reconstruction-20261018-26-v1/study-v4 --output runs/grimes-management-sensitivity-20261028-v1/study-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_management_sensitivity.py replay --study runs/grimes-management-sensitivity-20261028-v1/study-NEW --output runs/grimes-management-sensitivity-20261028-v1/replay-NEW
.venv/bin/python -m pytest -q
```
