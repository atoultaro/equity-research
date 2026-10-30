# Grimes prospective decision prediction — PR9C

PR9C tests explicit predictions of later **source-reported management**, separately from source facts and hypothetical execution. It builds on merged PR20 (`b23707704228767f5d49a277bd8b70a1e0be0647`, PR20 head `4ebfd20b24dd3693168e6349389e71afcc1ebfed`). It adds no trading, account access, subscriber fetching, monitoring service, backtesting engine or model training.

The original evidence remains unchanged:

- CDE challenges mandatory full realization at +1R, while protected residual exposure remains compatible.
- CLMT, TEVA and GME recover above their old stops by the Close; closing confirmation can conditionally explain continued management.
- EBAY closes below its old stop. Already-active hard-stop and same-day closing-confirmation exposure conflict with continued source management.
- An unconditional next-Open commitment and discretionary review are observationally equivalent at that cutoff. An evening revision cannot cancel an unconditional commitment.
- ENTERABLE, UNDERWAY and DROPPED are source states, not verified broker fills or positions.

These facts motivated the hypotheses. Replaying those same alerts cannot turn them into independent predictive evidence.

## Research modes and information boundaries

`RETROSPECTIVE_DRY_RUN` uses six transitions among the original seven alerts. A separate predictor process receives a sealed **view only**, with a prefix of source events, available canonical prices, contract identities and the pinned XNYS calendar. It never receives the archive or target-alert path. Experiment replay independently regenerates each prefix view from its declared frozen archive and verifies the cutoff, source sequence and released target; resealed changes to those records are rejected. The preparer seals the prediction before releasing the target into a separate reveal bundle. Dated alerts use the last completed Close + 61 minutes before their publication, after the previous alert's upper availability bound. This historical schedule uses publication metadata retrospectively; it is not a record of live forecasts. The unknown weekly alert uses the prior source availability bound, admitting no Friday prices to that forecast.

`FORWARD_REGISTERED` records the actual registration clock. Its target is the next complete alert **published strictly after registration**, through the end of the fifth subsequent XNYS session date (23:59:59.999999 ET, including after-hours alerts). The observation cutoff is separately recorded: this pilot knows the source through October 26 at 18:11 ET and market prices through October 26. Registration is later, so missing intervening sessions are listed. This is a forecast from stale evidence, not a claim that the last verified source book is today's actual portfolio. An already-past October 27 alert cannot become its forward outcome.

No later genuine source observations were supplied for PR9C. The forward artifact stays `UNRESOLVED_NO_LATER_ALERT_IMPORTED`. A later evaluation is a new bundle referencing its immutable prediction hash; it never rewrites the prediction's outcome field.

The inherited conditional IBKR split-adjusted price convention and unverified native volume units remain unchanged; this is not raw-basis execution certification. Prices are admitted only when the cash Close plus 60 minutes is strictly before the information cutoff. Future rows are removed while preparing views and rejected if inserted into a prediction view. Feature windows reuse `Evidence`/`Panel` and the pinned shared ATR calculation. Missing required sessions produce an unresolved model path or unavailable feature, never a compressed path or forward fill. TEVA's short native history continues to limit SMA50 and pivots. The exact retained vendor revisions were captured later: Close+60 is reconstructed availability, not proof that each historical cutoff had that identical price vintage. In the forward artifact, the October26 cutoff describes source/observation event time; all retained input snapshots were already present before the actual October28 registration. Only that later registration can anchor a genuine prospective test.

The weekly publication remains UNKNOWN. EARLY, CLOSE_BOUNDARY and LATE are fixed conditional schedules derived only from metadata in the prefix, not future source actions. The late receipt bound is evidence of availability, not an inferred exact publication. Scenarios propagate into entry references, stop paths, progress, forecasts and stability flags. No schedule is selected because it fits the next alert.

## Fixed decision models

All five hypotheses use the same frozen input view. Costs are ordinal counts of added conventions, not probabilities. Forecast-equivalent hypotheses remain indistinguishable; simpler equal forecasts need fewer conventions, but that preference does not identify the expert's policy.

| Model | Fixed rule | Cost |
| --- | --- | --- |
| A: mechanical stop | Hypothetical next-eligible-Open activation with positive protective risk; first intraday stop touch exits. No re-entry. | 0 |
| B: closing confirmation | Same activation, but only a Close at/beyond the stop known at that session's Open creates an idealized closing exit condition. | 1 |
| C: unconditional next Open | A closing violation commits to the following eligible Open regardless of later stop revisions or price recovery. | 2 |
| D: bounded review | At the next Open after a closing violation, retain only if the Open is protective to the stop known then. At most one such retention per episode; a second violation commits unconditionally. No arbitrary per-trade override. | 3 |
| E: price structure | The fixed rules below propose source stop changes and UNDERWAY transitions, without assuming an exact entry or +1R. | 3 |

A–D have a deliberately strict **reporting bridge**: hypothetically closed exposure predicts an explicit DROP; active exposure predicts a broad continuation set (management, UNDERWAY or omission). This bridge is not established by the source. A pending C/D condition permits continuation before its next Open; after that Open C expects DROP while D needs the actual opening price to resolve review. Publication-time conditions are frozen before reveal and resolved from metadata, not from the observed action.

A wrong prediction can falsify the **combined entry assumption, price rule and reporting bridge** without disproving the execution convention alone. In particular, the author can decide to DROP a setup before a hypothetical next-Open liquidation, or DROP for a reason other than stop violation. Those possibilities help explain why retrospective compatibility is not predictive success. C/D can be compatible in PR20 yet miss a subsequent DROP forecast here; the earlier reconstruction was allowed to terminate a hypothesis on the observed DROP, whereas this predictor cannot use that future label.

No A–D model predicts numerical stop levels. Their stop-direction/level fields explicitly abstain. A broad continuation set is measured as set coverage, not credited as an exact action-category prediction.

## Price-structure hypothesis E

These are repository-defined research rules, not attributed to Grimes:

1. Use the latest available Close, ATR14, SMA20/50, prior-20 extremes, confirmed three-bar pivots and relative SPY 20-session return. Confirmed pivots require their right-hand bars to be available.
2. Reference progress to the last available Close before the assumed opening-alert clock, divided by the ATR available then, with the sign of the trade. This is not actual initial risk, return on a fill, or +1R.
3. For an ENTERABLE episode, predict UNDERWAY when progress is at least one reference ATR and either a directional 20-session closing breakout/breakdown occurs, or two consecutive favorable closing moves coexist with favorable SPY-relative performance.
4. If the latest Close is adverse to the currently reported stop, predict DROP and abstain on a numerical revision.
5. Otherwise, after a touch/recovery against the stop **known at that bar's Open**, use that bar's directional extreme minus/plus 0.25 current ATR as a widening candidate. Without a recovery, use the first protective level in fixed priority: confirmed directional pivot, SMA20, then directional prior-20 extreme; buffer it by 0.25 ATR.
6. Predict tightening only when progress is at least 0.5 reference ATR and the candidate tightens protection. Predict widening only on the declared recovery condition. Reject nonpositive or nonprotective candidates. Otherwise predict no adjustment. An offered interval is ±0.25 ATR around the rounded candidate, clipped so the whole interval is positive, protective and in the declared adjustment direction.
7. Predict continued management when a stop revision is proposed without UNDERWAY; otherwise predict omission/no adjustment. Without a completed post-alert session, use a low-confidence no-change source projection. Missing necessary price/ATR features cause abstention.

All thresholds are fixed in `rules.json`, with no search or post-score retuning. Confidence is `LOW_HEURISTIC_NOT_A_CALIBRATED_PROBABILITY`. A one-ATR progress rule is an initial falsifiable heuristic, not an asserted universal expert threshold.

## Evaluation and dependence

The target is one complete alert, not the next mention of each stock. Actual categories are DROPPED, UNDERWAY, CONTINUED_MANAGEMENT and NOT_MENTIONED. Co-published stop/setup actions are one trade/alert cluster. Omission never changes the source position state. New positions in the target are not scored as if known at the earlier cutoff.

Report exact-category correctness only for point forecasts, action-set coverage separately, stop-direction correctness with both all-action and actual-revision-only denominators, absolute stop error in the **forecast** ATR, interval coverage, disjoint-forecast wins/losses, abstentions and unresolved conditions. Aggregate trade descriptives and shared-alert clusters separately. A mixed cluster is retained as mixed for distinguishing tests. The three publication schedules are not pooled into three times as many observations. No significance tests, calibrated probabilities, profit measures or parameter optimization follow.

A fresh evaluation requires known publication wholly after registration and inside the fixed window, plus operator attestations that the supplied alert is the next complete one after registration and that the source chain since known history is complete. Missing attestations, unknown publication, partial-window overlap or missing review-market evidence remain unresolved. Earlier supplied alerts may be imported as non-scoring backfill, then advanced into a new history before a new forecast is sealed. No unobserved alert is invented.

The original 26 stocks are the initial tracked cohort. A later alert's valid actions outside that cohort are retained in raw capture and explicitly quarantined; they do not expand the research population. Reopenings of tracked symbols receive new source episode IDs using the unchanged ledger reconstruction. Source stop-history mismatches fail instead of fabricating omitted revisions.

## Offline CLI workflow

Run from the repository root. Every output must be a new directory. All commands deny network sockets. The full native parent and supplied original alert bodies remain local; committed evidence is a derived projection.

```sh
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py --help

# Verify/import the merged PR20 local native study once.
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py baseline --parent runs/grimes-forensics-20261018-26-v1/study-v4 --output runs/pr9c-archive-NEW

# Build a physically bounded input view; predictor has no archive argument.
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py view --archive runs/pr9c-archive-NEW --cutoff 2026-10-26T18:11:00-04:00 --output runs/pr9c-view-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py predict --view runs/pr9c-view-NEW --mode FORWARD_REGISTERED --output runs/pr9c-prediction-NEW

# Only after the prediction exists, supply an authorized complete alert file.
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py reveal --prediction runs/pr9c-prediction-NEW --alert /path/to/supplied-alert.json --output runs/pr9c-reveal-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py evaluate --prediction runs/pr9c-prediction-NEW --reveal runs/pr9c-reveal-NEW --output runs/pr9c-evaluation-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py advance --archive runs/pr9c-archive-NEW --prediction runs/pr9c-prediction-NEW --reveal runs/pr9c-reveal-NEW --output runs/pr9c-archive-NEXT

# Recompute every derived prediction or evaluation; do not overwrite it.
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py replay-prediction --prediction runs/pr9c-prediction-NEW --output runs/pr9c-prediction-replay-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py replay-evaluation --prediction runs/pr9c-prediction-NEW --reveal runs/pr9c-reveal-NEW --evaluation runs/pr9c-evaluation-NEW --output runs/pr9c-evaluation-replay-NEW

# Historical workflow test, explicitly retrospective.
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py dry-run --archive runs/pr9c-archive-NEW --output runs/pr9c-dry-run-NEW
PYTHONPATH=src .venv/bin/python scripts/grimes_predictions.py replay-dry-run --study runs/pr9c-dry-run-NEW --output runs/pr9c-dry-run-replay-NEW
.venv/bin/python -m pytest -q
```

The authorized alert file is JSON containing `origin: "operator"`, an `alerts` array with exactly one complete alert, and `sequence_attestation: {"next_complete_alert_after_registration": true, "complete_since_known_history": true}` when those facts are actually confirmed. Each alert supplies `alert_id`, `published_at` (aware timestamp or null), `publication_precision` (MINUTE/SECOND, or UNKNOWN when publication is null), `email_received_at` if publication is unknown, `original_publication_display`, `source_reference`, and verbatim `text` with all four original action sections. `source_sequence` is normalized locally; no publication date is invented. Attestations are operator assertions, not independently verified subscriber-feed completeness.

`advance` supports optional `--calendar` for an extended pinned XNYS schedule preserving the existing history, and `--market-observations` for a supplied JSON canonical update. That update declares `schema_version: grimes_market_update_v1`, `source_reference`, `native_bundle_sha256`, `market_observation_end`, and `prices` keyed by existing symbols using the inherited canonical row/basis/identity schema. Existing rows cannot be replaced, and the cohort cannot expand. Such updates are explicitly operator-supplied; their native provenance is not automatically promoted to a fully replayed provider proof. Use the existing separately authorized acquisition/preparation workflows to supply data. No acquisition is performed by these commands. With no update, the next view retains and discloses the old observation end.

The original `reports/grimes_trade_status.csv`, PR16–PR20 source artifacts, native captures and implementation files remain unchanged. See [historical evaluation](reports/GRIMES_WALK_FORWARD_EVALUATION.md), [next-alert registration](reports/GRIMES_NEXT_ALERT_PREDICTIONS.md) and [verification record](evidence/pr9c-validation-v1/validation.json).
