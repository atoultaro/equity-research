# PR9D current MarketLife evidence and registration

PR9D starts from merged PR9C, commit `4ee534ada90ad622872f677cac809b6ae05d8628`, on branch `research/marketlife-current-evidence-v1`. It adds current source/native-market intake, immutable archives and readiness validation. The setup lifecycle, fresh-entry eligibility, opportunity versions and unobserved subscriber executions remain separate. The PR9C eligibility-persistence and exploratory price-extension models are unchanged.

The latest run connected to the operator-confirmed **non-paper, read-only TWS on port 7496** and retrieved all 11 instruments through October 29. Forecast registration remains **blocked** by six native revisions and unverified source completeness; the earlier no-connection snapshots remain unchanged. See the [market audit](reports/MARKETLIFE_CURRENT_DATA_AUDIT.md), [source completeness](reports/MARKETLIFE_SOURCE_COMPLETENESS.md), [readiness report](reports/MARKETLIFE_PROSPECTIVE_READINESS.md), and [machine audit](evidence/pr9d-current-readiness-v3/registration-audit.json). Existing historical artifacts and the October 26 CSV remain unchanged.

## Evidence and availability

The latest required session is derived at audit, acquisition and actual registration using the pinned XNYS calendar and cash Close + 60 minutes strictly before the current clock. It advances automatically; October 29 is only the cutoff for this recorded run. Weekends, holidays, early closes and daylight-saving changes come from the existing calendar. The minimum is 60 consecutive completed sessions for every active source setup, including UNDERWAY setups, plus SPY. No missing session is skipped or forward filled.

Existing Evidence/Panel and the pinned shared wheel calculate ATR14, SMA10/20/50, confirmed swings, previous-20 extremes, volatility, compression and relative SPY movement. Values retain their underlying session. An older last-observed ATR is descriptive stale evidence, never a replacement for a current required feature. Absence of a confirmed swing can reflect the observed structure; it is distinct from a missing daily bar.

The inspected PR9C archive contains recorded qualified contracts for CNQ, MMM, SAIL, SIG, SLB and SPY through October 26. CRWV, DUK, FCX, NBIS and PAA have no market evidence in that baseline or the inspected declared datasets. Those baseline gaps are now filled in a new immutable live archive: 65 sessions per instrument (715 selected observations) over July 30–October 29, with all 60 required sessions complete. All five new instruments were qualified. The 44 bounded historical requests returned 1,012 native rows, including explicitly excluded over-return. Other real SPY datasets remain historical references. Synthetic datasets are not real-market coverage.

TRADES/RTH prices retain the documented IBKR split-adjusted convention and unverified native volume units. Corporate-action completeness and complete historical ticker identities remain UNKNOWN. These datasets are for descriptive research, not raw-price execution certification. New qualification verifies symbol, conId, STK, USD, SMART and primary exchange. Existing qualified identities must reconcile, including local/trading symbols. An ambiguous match is a blocker, never a ticker-only substitute.

## Source intake

Retain each operator batch as a separate immutable bundle. This preserves its own captured_at and original source bytes. It avoids widening an earlier DATE-only publication bound when later alerts arrive. Original PR9C records are not rewritten.

A new input JSON uses `schema_version: marketlife_operator_alerts_v1`, `captured_at` as an aware receipt timestamp, and ordered `alerts`. Each alert supplies `alert_id`, `text` with all four original action sections, `source_reference`, `source_date`, nullable `published_at`, and `publication_precision` DATE/MINUTE/SECOND. Preserve original displayed metadata when available. No subscriber content is fetched automatically.

The complete retained chronology is reconciled before sealing. Stop chains, previous entry eligibility, explicit returns to ENTERABLE and ADDED/reopening after DROPPED must agree. IDs cannot repeat. Repeated body text at a different publication date may legitimately describe a new setup episode; it is not deleted merely because the wording repeats. The original weekly publication remains UNKNOWN, and the original October 27–29 records keep their date-only uncertainty.

Source completeness is a separate operator assertion, not inferred from hash consistency. The assurance JSON must contain:

```json
{
  "complete": true,
  "complete_through": "REGISTRATION",
  "alert_manifest_sha256": "ORDERED_MANIFEST_HASH_FROM_THE_AUDIT",
  "source_reference": "operator's actual completeness check reference",
  "asserted_at": "ACTUAL_OFFSET_AWARE_ASSERTION_TIME",
  "operator_statement": "the actual statement confirming complete history through registration"
}
```

Do not use these placeholders as evidence or infer a completeness claim from a pasted alert. Missing, inconsistent or future-dated assertions block registration. A declaration remains an operator assertion, not independent subscriber-feed verification; confirm it for the registration being authorized. The operator said “I gave you all I have.” This is retained as an availability statement, not promoted to a complete external-feed assertion. No additional subscriber material is requested; no source-completeness assertion is invented.

## Commands

Run from the repository root. Every output path must be unused. Inspect `--help` before acquisition. Offline operations explicitly deny sockets; only `acquire` can connect.

```sh
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py --help
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py acquire --help

# Inspect required identities, dates, basis and warmup before connecting.
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py plan \
  --parent-archive runs/grimes-prospective-20261028-v1/archive-v1 \
  --source runs/marketlife-opportunities-20261029-v1/operator-source-v1 \
  --output runs/current-pre-audit-NEW

# Validate a legitimately supplied later alert batch; retain the new output.
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py source \
  --parent-archive runs/grimes-prospective-20261028-v1/archive-v1 \
  --source runs/marketlife-opportunities-20261029-v1/operator-source-v1 \
  --incoming /path/to/authorized-later-alerts.json --output runs/current-source-NEXT
```

For subsequent commands repeat `--source` in chronological batch order, including every earlier bundle. A source addition requires a new pre-acquisition audit so the selected active setups and source manifest match. The October 29 snapshot is not hard-coded as the current universe.

The operator explicitly corrected the account mode to **non-paper**, port **7496**, with Read-Only API enabled. This confirmation supersedes the original brief’s paper wording. Acquisition requires explicit account mode, socket/Read-Only confirmation and connection intent. Mode is operator-reported, never inferred by querying accounts. No program changes TWS configuration or starts a session. The legacy paper confirmation flag remains supported for actual paper sessions; conflicting mode flags fail.

```sh
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py acquire \
  --parent-archive runs/grimes-prospective-20261028-v1/archive-v1 \
  --source runs/marketlife-opportunities-20261029-v1/operator-source-v1 \
  --pre-audit runs/current-pre-audit-NEW \
  --ibkr-port 7496 --ibkr-client-id 931 \
  --connect --read-only-api-confirmed --account-mode non-paper \
  --permission-reference 'actual operator confirmation and authorized research scope' \
  --output runs/current-ibkr-intake-NEW
```

A positive unique client ID is required; its low-level handshake fails if unavailable. The local endpoint is fixed at 127.0.0.1. The existing restricted backend avoids high-level account synchronization. Only contract details and daily historical market data are requested; no balances, positions, executions or orders. The adapter preserves its existing request pacing, bounded retries and safe error classifications, with no entitlement workaround or paid subscription.

Qualification is retained before daily acquisition. Each successful contract requests the current 60-session feature interval plus five prior sessions for overlap checking, using bounded existing daily TRADES/RTH requests. Failed captures remain evidence; the returned paths are attempts, not proof of complete history. Re-run a new audit after a cutoff change or source update. No resume overwrites an existing attempt directory.

```sh
# Combine exact native inputs with preserved parent/source bytes, then run gates.
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py archive \
  --parent-archive runs/grimes-prospective-20261028-v1/archive-v1 \
  --source runs/marketlife-opportunities-20261029-v1/operator-source-v1 \
  --acquisition-root runs/current-ibkr-intake-NEW \
  --source-assurance /path/to/actual-confirmed-assurance.json \
  --output runs/current-archive-NEW

# Recompute every derived canonical row, ledger and audit offline.
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py replay \
  --archive runs/current-archive-NEW --output runs/current-archive-replay-NEW

# Actual-clock registration only; this FAILs before writing if not ready.
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py register \
  --archive runs/current-archive-NEW --output runs/current-prediction-NEW
PYTHONPATH=src .venv/bin/python scripts/marketlife_current.py replay \
  --prediction runs/current-prediction-NEW --output runs/current-prediction-replay-NEW
```

`archive` can freeze both earlier no-acquisition blockers and a live acquired archive with unresolved revision/source blockers, as retained in this PR. It embeds the exact parent archive and hash registry, separate source proof bundles, original native market captures, qualified mapping records, canonical appended rows, source ledgers, coverage, assertion and readiness findings. The native data stays local. The declared observed end reflects actual retained bars, not the desired cutoff.

Existing canonical observations remain byte-identical. Numerically equal overlaps retain the earlier row and provenance. Any conflicting OHLCV overlap is recorded and blocks registration; it is not silently revised, deduplicated, spliced or rescaled. Duplicate/future/off-calendar observations, wrong identities and incompatible bases cannot enter the current series. Synthetic native updates cannot be mixed into an operational archive.

## Forecast and replay

The wrapper runs the unchanged PR9C gate and model implementation through explicitly labeled conditional information-time views. Different source batches retain different receipt bounds in the factual ledger. The internal model view projects one predeclared timing scenario at a time to PR9C's numerical interface; projected times are never stored as actual publication facts. Regression tests compare forecasts with the original model for known and date-only/reopened source histories. No model constants, stop rules or execution conventions change.

The readiness audit adds full identity/mapping, source-assertion, required-feature and native-overlap checks. A PASS of the original gate alone cannot override these failures. Registration replays the archive semantically, reads the actual current clock and rechecks current readiness. There is no --asof or caller-supplied now for operational registration. Synthetic fixtures test the positive sealing path but cannot be operationally registered. Predictions retain an unresolved outcome; this PR performs no prospective scoring and never backdates a forecast.

The source-removal and numeric-stop abstentions remain intact. Hypothetical subscriber stop-out cannot imply source DROPPED. There are no inferred fills, quantities, returns, P&L or performance claims.

```sh
# Reproduce the three committed reports using only public derived evidence.
PYTHONPATH=src .venv/bin/python scripts/report_marketlife_current.py report \
  --evidence docs/evidence/pr9d-current-readiness-v3 --output runs/current-reports-NEW
.venv/bin/python -m pytest -q
```

Public projection files are hash-checkable derived evidence, not original provider payloads. Full semantic replay needs the local inputs. Inherited PR9C prices were previously semantically verified before its archive was sealed; that archive's exact canonical rows and provenance are retained here. Current imports independently recompute native normalization. Neither procedure proves identical historical vendor vintages or complete corporate actions. No existing historical research, execution simulator, finwhaling code, CI or paid provider is changed.

## Recorded live result and remaining blockers

The live run used client ID 931 on 127.0.0.1:7496 with operator-reported non-paper mode. All 11 qualified contracts and all 11 daily captures succeeded. No balances, positions, executions, orders or account identifiers were queried or stored. New native responses, request/error metadata and qualifiers remain in `runs/marketlife-current-20261030-live-v1/acquisition-v1`; the immutable combined archive and offline replay are adjacent `archive-v1` and `archive-replay-v1`.

Current ATR14 and technical measurements are available on October 29 for all 11 instruments. The final audit has eight blockers: six retained/native vintage conflicts plus two source-completeness checks. Five differences are October 26 native volume revisions (CNQ, MMM, SAIL, SLB, SPY); SIG High changed from 118.85 to 118.86. [The exact before/fresh/retained values](evidence/pr9d-current-readiness-v3/revision-audit.json) preserve both vintages. Older canonical rows are retained byte-for-byte and conflicts are not waived. No forecast was created, no model was retuned and no historical source event or prediction was rewritten.
