# Prospective MarketLife setup-decision prediction

This PR9C amendment changes the primary target to **source setup selection and fresh-entry eligibility**. It does not infer Grimes' or subscribers' actual positions from MarketLife alerts. The [setup model](MARKETLIFE_SETUP_AND_OPPORTUNITY_MODEL.md) defines the source/opportunity/execution separation. Hypothetical execution closure must never mechanically predict source DROPPED.

The earlier five-model experiment remains an immutable historical baseline. Its [original method](evidence/pr9c-setup-opportunities-v1/historical-method.md), [walk-forward report](reports/GRIMES_WALK_FORWARD_EVALUATION.md) and [original registration](reports/GRIMES_NEXT_ALERT_PREDICTIONS.md) retain their original bytes and conditional results. Their execution-to-DROP bridge is superseded. The original forward bundle `36b732cdb82e74a9c90f8add9d6e66015f31bcf9da156cb6213a858bf7676135` is **non-operational**, preserved and unevaluated. The historical Model E failures (4/26 actual revision directions, 3/26 intervals) remain exploratory failures; no stop-price rule is optimized or retuned here.

## Current evidence and registration state

The user supplied three additional complete action-section bodies dated October 27–29, with no publication times. They extend the source-only inventory from 26 to 34 captured setups. They do not establish complete source history through a future registration instant, supply missing market prices, or validate the old forecast prospectively. The original weekly publication remains UNKNOWN. Date-only source bounds and all three conditional schedules are retained; no calendar time is invented as a source fact.

At October 29, 23:37 ET, the latest eligible completed session is October 29. Existing frozen daily observations end October 26. SIG, CNQ, MMM, SAIL, SLB and SPY lack October 27–29 sessions. DUK, PAA, FCX, CRWV and NBIS lack qualified identities/history in the archive. Current technical features for all ten active setups are unavailable. Explicit source completeness through registration is also unattested. [The frozen audit](evidence/pr9c-setup-opportunities-v1/registration-audit.json) records these blockers. **No replacement forecast is registered.**

## Completeness gate

Operational `register` uses the actual aware clock; its CLI has no backdating option. Before any output directory is created, it independently derives the latest XNYS session with cash Close + 60 minutes strictly before registration, and requires:

- All available operator-supplied source alerts, preserving original bodies, section order, source IDs and publication uncertainty. Stop chains and reported previous eligibility must reconcile; no omitted stop is manufactured.
- An operator source-history attestation tied to the ordered alert ID/body-hash manifest, explicitly complete through REGISTRATION. This is a declared completeness claim, not independent subscriber-feed verification. It must be renewed when the supplied history changes.
- Unique qualified contract identities for every active setup, including UNDERWAY setups that may return to ENTERABLE, plus benchmark SPY. No ticker-only invented identity is accepted.
- Sixty consecutive completed daily feature sessions for each required identity through the independently derived latest session. Missing, duplicate, nonchronological, future/incomplete or invalid OHLCV/native-basis observations fail. Nothing forward fills or silently takes an older last observation.
- The declared market observation end must match that latest session. Completed ATR14, SMA50 and relative SPY technical features must be available for every active setup. Calendar/availability rules reuse the pinned project infrastructure and shared ATR, not a duplicated ATR implementation.

The expected attestation file contains `complete: true`, `complete_through: "REGISTRATION"`, `alert_manifest_sha256` from the audit, and a nonempty `source_reference`. Supply it only if the operator can actually confirm that claim. The audit's fixed timestamp describes a historical check; a later registration always rechecks the current clock and may require additional sessions/alerts.

A `PENDING_CURRENT_SOURCE_AND_MARKET_EVIDENCE` result is a valid blocked registration, not a forecast. The old `grimes_predictions.py predict --mode FORWARD_REGISTERED` command is disabled. Its existing low-level archival routines and retrospective/replay commands remain solely for reproducing sealed historical experiments; they do not meet the amended operational registration contract. The amended loader rejects old forecast schemas as operational registrations.

## Primary forecast targets and bounded initial rules

Each amended forecast separates observed source setup status, ENTERABLE/UNDERWAY eligibility and published stop from UNKNOWN subscriber execution. It forecasts eligibility, setup removal and new-opportunity implications. Numeric stop prediction explicitly abstains as a secondary diagnostic.

The source-persistence baseline carries current eligibility. A separate predeclared exploratory flag proposes UNDERWAY for an ENTERABLE setup only after at least one directional ATR of progress from ADDED's causal Close reference and a directional closing breakout beyond prior-20 High/Low. This is a repository-defined hypothesis, not MarketLife guidance, a fitted threshold, +1R, or a demonstrated decision rule. Missing anchor evidence leaves that flag inactive, with persistence only. Confidence is LOW and uncalibrated. The descriptive transition evidence does not establish a universal one-ATR boundary, and this initial flag is not reported as validated.

Setup removal explicitly **abstains** until a defensible source-decision rule is identified. Hypothetical stop touches and closing violations cannot close the source setup or force a removal forecast. Opportunity outcomes are separately stated as conditions: an ENTERABLE revision creates a version; co-published UNDERWAY leaves no usable window; an UNDERWAY-only revision remains monitor-only; explicit return creates an eligible version; DROPPED ends setup eligibility without implying an execution.

Three conditional publication schedules remain separate. A forecast includes current cutoffs, input identities/hashes, actual registration, a five-subsequent-session-date observation deadline, and an unresolved outcome. Synthetic payloads are labeled SYNTHETIC_TEST_ONLY and cannot be operationally registered. A later source observation/evaluation must be additive; nothing rewrites the sealed forecast. No new forward evaluation or predictive success is claimed by this amendment.

## Offline commands and input retention

All outputs must use new paths. Commands prohibit network sockets. Native provider frames and full source commentaries remain in ignored local immutable bundles; the committed derived projection has source action lines, timestamps/bounds, reference measurements, opportunity ledgers, comparisons and hash registries. It is independently hash-checkable; full semantic replay requires the local frozen inputs.

```sh
PYTHONPATH=src .venv/bin/python scripts/marketlife_setups.py --help

# Recompute the source/opportunity study and a dated completeness audit offline.
PYTHONPATH=src .venv/bin/python scripts/marketlife_setups.py study \
  --archive runs/grimes-prospective-20261028-v1/archive-v1 \
  --operator-source runs/marketlife-opportunities-20261029-v1/operator-source-v1 \
  --asof 2026-10-29T23:37:00-04:00 --output runs/marketlife-study-NEW
PYTHONPATH=src .venv/bin/python scripts/marketlife_setups.py replay \
  --study runs/marketlife-study-NEW --output runs/marketlife-replay-NEW

# Independently reproduce the versioned Markdown reports from public evidence.
PYTHONPATH=src .venv/bin/python scripts/report_marketlife_setups.py report \
  --evidence docs/evidence/pr9c-setup-opportunities-v1 --output runs/marketlife-reports-NEW

# Only after legitimately supplied current source and canonical daily evidence
# have been retained in NEW immutable input bundles and completeness confirmed:
PYTHONPATH=src .venv/bin/python scripts/marketlife_setups.py audit \
  --archive /path/to/current-archive --operator-source /path/to/current-source \
  --source-assurance /path/to/confirmed-assurance.json --output runs/current-audit-NEW
PYTHONPATH=src .venv/bin/python scripts/marketlife_setups.py register \
  --archive /path/to/current-archive --operator-source /path/to/current-source \
  --source-assurance /path/to/confirmed-assurance.json --output runs/current-forecast-NEW

.venv/bin/python -m pytest -q
```

The existing archive contract retains canonical prices, qualified coverage identities, original alert capture, calendar and declared observation end. Current data must be supplied using the project's separately authorized preparation workflows and sealed into a new archive; these commands fetch nothing. The operator source bundle retains `operator-alerts.json` and `guidance.json`; each extra alert has original text, a unique ID, `source_date`, nullable `published_at`, explicit precision and source reference, plus a receipt timestamp for the bundle. Do not modify original source or price bundles to make the gate pass.

## Interpretation limits

The [four-case reassessment](reports/GRIMES_ENTRY_OPPORTUNITIES.md) removes apparent setup/execution contradictions without proving subscriber re-entry or closing-stop use. The [UNDERWAY study](reports/GRIMES_UNDERWAY_TRANSITIONS.md) retains all 14 reports, with seven daily-measurable transitions across only two alert clusters. Same-direction controls are descriptive and dependent; omission carries source state without confirming fresh assessment. No threshold fitting, profit inference, edge claim or historical-population membership inference follows.

Native split-adjusted price compatibility, unverified volume units, UNKNOWN weekly publication and reconstructed Close+60 availability remain limitations. Later captured vendor revisions do not prove identical historical price vintages. PR16–PR20 artifacts, the original PR9C baseline and the 26-row October 26 CSV remain unchanged. No execution simulator, brokerage connection, provider acquisition, subscription, GitHub Actions or automatic merge is introduced.
