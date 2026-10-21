# Historical data preparation v1

PR 5B implements the [PR 5A audit](YAHOO_DATA_SOURCE_AUDIT.md) with an optional
acquisition boundary and offline validation. Strategy, qualification, execution,
accounting, `load_dataset`, the existing synthetic inputs and shared wheel are
unchanged. One request means one provider symbol, no batching or concurrency.
The [README](../README.md#prepare-historical-daily-data) contains runnable examples.

## Evidence and dependency boundaries

Starting equity revision: `d874f15c712fa32096435e30ef56b048565409db` (merged
GitHub PR #2). Starting reference cannoslim revision:
`6f1a01d1db2cbc24abc845c190af7acaf6701834`. Its inspected prices, symbol conversion,
manual calendar and price tests match the audit; no discrepancy or changes to
cannoslim/finwhaling were introduced. Only narrow request/symbol/shape knowledge
was reused; the complete application is not a dependency.

The `data` and `yahoo` extras are separate from core installation. All optional
imports are behind explicit operations. Replay's clean-install acceptance test
still installs only local equity/shared wheels without data libraries. Full
development tests require both optional extras. The pinned yfinance callable's
signature is exercised offline, and adapter tests use mocked responses. This
does not establish live provider compatibility or data quality.

The supported [yfinance 0.2.66 download interface](https://raw.githubusercontent.com/ranaroussi/yfinance/0.2.66/yfinance/multi.py)
returns a DataFrame and exposes no documented response-payload callback. We use
no private session or monkeypatch for acquisition. `capture_level="client_return"`
is deliberate: upstream client normalization, duplicate/date changes and missing
volume conversion may already have occurred. Even `keepna=True`, `repair=False`
and `auto_adjust=False` cannot restore lost wire observations. Unsupported frame
types create a `SCHEMA_FAILURE` record, not a fabricated payload.

The frozen calendar is XNYS from exchange-calendars 4.13.1, with explicit
start/end construction bounds and no overrides. Tests establish observed holidays,
13:00 early close, DST and the January 9, 2025 closure. This community library is
a reference implementation, not an exchange certification. Actual listing venue
is separate; a non-XNYS listing requires affirmative date-specific
`xnys_alignment` evidence for export. Other session conventions and historical
14:00 early closes remain unsupported by the unchanged replay loader.

## Artifact schemas

All JSON is UTF-8 with sorted keys, no nonstandard NaN literals and a final LF.
Hashes are SHA-256 of exact stored bytes. Directories are exclusively created;
they are never refreshed in place. An incomplete write lacks a valid final hash
record and is not accepted as a completed bundle. Hashes establish integrity,
not a provider signature or a trustworthy external attestation.

| Record | Schema and content |
| --- | --- |
| `request.json` | `yahoo_request_v1`: provider, origin, requested and mapped symbols, inclusive dates, exact download parameters. Dot/slash class notation maps to dash; invalid multi-symbol strings reject. |
| `acquisition.json` | `yahoo_acquisition_v1`: attempt identity, UTC start/completion, client/version, status, safe error codes/types, returned row count/range where available, historical availability unknown, client-return capture limitation, deterministic content hash. |
| `returned_frame.json` | `client_frame_v1`: tagged axis/scalar representation, column hierarchy and dtypes, null/NA/NaT, row order, duplicate rows/columns, finite floats via `float.hex`, nonfinite diagnostic values via tags. Preserves supported pandas numeric, object, nullable and categorical data without pickle. Unsupported scalars fail explicitly. |
| `hashes.json` | `artifact_hashes_v1`: file hashes and canonical file-map bundle hash; self excluded. Reject missing, extra or corrupted members. |
| `canonical.json` | `canonical_daily_v1`: every returned row with stable local ID if evidenced, provider symbol, session date, OHLCV decimal strings, separate optional Adj Close, source bundle hash and frame-row locator; issues, provider events and conversion threshold. Invalid values remain in the original frame and receive explicit canonical diagnostics; rows are not removed. |
| `schedule.json` | `exchange_schedule_v1`: reference calendar/package version, timezone, inclusive bounds, overrides, ordered sessions with UTC opens/closes and schedule hash. Generated independently of prices; no `available_at` invented. |
| `actions.json` | `corporate_actions_v1`: separately retained nonzero split/dividend/capital-gain observations, source row/snapshot and retrieval identity, unknown completeness, independent evidence and required horizon. No absent feed is treated as an empty verified event set. |
| `quality.json` | `data_quality_v1`: request/acquisition, identity, basis, gates and blockers, all row and calendar findings, availability unknowns, artifact hashes/relative references; comparison is separate and marked NOT_APPLICABLE when no second snapshot is supplied. |
| `provenance.json` | `yahoo_provenance_v1`: original snapshot hash map, acquisition/request metadata, evidence, converter Python source hashes, actual data dependency versions and canonical/schedule/action/evidence hashes. No credentials or personal filesystem paths are recorded by acquisition. |

Acquisition UUID directories identify attempts; `content_sha256` hashes the request
and frame separately from timestamps/attempt outcomes. Exact same request/frame
on two attempts has the same content identity but different acquisition/bundle
bytes. Hashes and lineage distinguish them. Canonical conversion is deterministic
for the same snapshot, evidence, code and dependency environment.

Successful export adds exact `data.csv` and `data_manifest.json` to the quality
bundle, plus its existing Markdown summary. Manifest fields meet the existing
loader, reference provenance/quality hashes, and explicitly retain evidence kind.
Dataset creation time is null (not inferred from retrieval); retrieval times
remain in provenance. Output directory names do not enter content hashes.
Export validates a temporary copy with the unchanged loader before writing a
ready bundle. Blocked export writes reports but never these two replay files.

## Validation and gate semantics

`PASS` means a tested condition or supplied affirmative attestation passes its
checks; `FAIL` is a known violation; `UNKNOWN` is missing/unusable evidence;
`NOT_APPLICABLE` is reserved for an irrelevant operation. A caller-supplied
reference is **not independently authenticated by this program**. Real evidence
is labeled `user_supplied_evidence_not_independently_verified`, consistent with
the existing candidate-provenance boundary. Review is still required to decide
whether the cited external documents support the assertions.

Missing/malformed/nonfinite values, duplicate/conflicting dates, missing/extra
columns, invalid OHLC, negative/fractional volume, bad ordering and date anomalies
are explicit failures. Zero volume, Adj Close disagreement and >50% adjacent-close
changes are investigation warnings and conservatively block automatic export in
v1. A discontinuity never establishes a corporate action. There is no warning
waiver/repair mechanism in this slice. Adj Close is never manufactured.

Calendar classifications distinguish valid bars, missing expected sessions,
unknown security-specific gaps, off-calendar/out-of-range rows, legitimate
closures, evidenced pre/post-listing dates, invalid bars and incomplete sessions.
Missing listing history never excuses a gap. Known listing exclusions remain
export blockers: obtain a deliberately narrower request rather than silently
truncating the existing one. A real session omitted from prices and proposed
availability/manifest remains present in the independent reference schedule.

Acquisition statuses are SUCCESS, PARTIAL_RESPONSE, EMPTY_RESPONSE, SCHEMA_FAILURE
and REQUEST_FAILED. A complete-looking response can still fail numeric quality.
Client errors logged rather than raised are retained as safe categories; arbitrary
error text/URLs are excluded because they can contain secrets or local paths.
The underlying client can make more than one HTTP request; its timeout is not a
whole-job deadline. No retry loop, provider fallback, concurrency or scheduler is
implemented. Errors and empty returns remain distinguishable only to the extent
the client exposes them through its public return/log behavior.

## Affirmative export evidence

Optional `--evidence FILE` accepts `research_evidence_v1`. With no evidence all
non-observable gates remain UNKNOWN. The synthetic generator produces a concrete
example with **synthetic claims only**, bound to a synthetic-origin snapshot.
Synthetic attestations cannot authorize a Yahoo-client-origin snapshot.

Required fields for an eligible record:

- Top level: `schema_version`, `kind` (`synthetic` or `recorded_evidence`),
  `snapshot_content_sha256` matching exactly the request/frame identity.
- `identity`: `status="VERIFIED"`, nonempty `reference`, string `security_id`,
  matching `research_symbol`/`provider_symbol`, actual `listing_venue`, `currency="USD"`,
  aware `known_at` not later than acquisition, and `valid_from`/`valid_through`
  covering the requested interval. Optional `listing_boundaries` requires its
  own VERIFIED/reference and `first_session`/`last_session`; a non-XNYS venue
  also needs VERIFIED/reference `xnys_alignment`.
- `basis`: VERIFIED/reference, `price_basis="RAW_VERIFIED"`, `coverage_start`/
  `coverage_end` covering the full requested history through retrieval's UTC
  date. Separate `split_adjustment` and `dividend_adjustment` each require
  VERIFIED/reference and `convention="unadjusted"`; `volume` requires
  VERIFIED/reference and `units="contemporaneous_shares"`. SPLIT_ADJUSTED,
  OTHER_ADJUSTED or UNKNOWN cannot be relabeled raw.
- `actions`: VERIFIED/reference, coverage through that same horizon and explicit
  `events=[]`. Nonzero captured provider events or independent events block export,
  including later splits and rename/reorganization observations. V1 is conservative
  about all events in the evidence horizon and does not implement cash flows.
- `availability`: VERIFIED/reference, `historical_availability="verified"`, and
  `sessions` mapping each expected date to an aware actual historical availability
  timestamp. Each must be at/after close, before next actual exchange open and
  not after acquisition. No modeled latency or publication timestamp is inferred.

Every required gate must PASS. Reasons are BLOCKED_ACQUISITION,
BLOCKED_DATA_QUALITY, BLOCKED_CALENDAR, BLOCKED_IDENTITY, BLOCKED_PRICE_BASIS,
BLOCKED_CORPORATE_ACTIONS and BLOCKED_AVAILABILITY. All failures are reported
together. Current Yahoo-client captures will normally remain blocked without
independent evidence, and PR 5B does not approve a historical availability model.

## Revision comparison

`data compare` verifies both bundles and requires the same provider/symbol and
overlapping requested dates. It reports exact stored-file and frame-byte changes,
schema/dtype changes, added/removed session dates and tagged per-field changes
(including nulls and adjusted/action values) within the overlap. Invalid or
duplicate keys yield UNKNOWN rather than selecting a row. Prior snapshots are
never changed. A successful comparison indicates that the comparison ran, not
that the new prices are correct. Two equal retrievals cannot prove historical
point-in-time availability or permanent stability.

## Validation and limits

Run `.venv/bin/python -m pytest -q` after installing the development extras.
The existing socket guard applies to new fixtures. Tests cover the schema and
calendar cases in PR 5B, immutable writes/corruption, safe failed attempts, null
and adjustment revisions, unknown/bound evidence, export compatibility and a
fresh-process replay that rejects importing yfinance/curl_cffi. A new synthetic
provider vintage cannot change byte-identical downstream output for the same
frozen dataset. Existing synthetic replay/accounting assertions remain unchanged.

This is data preparation, not a new strategy, historical universe, split-aware
backtester, provider license determination or evidence of edge. Local artifacts
should live outside tracked source by default. Do not commit provider data without
established redistribution rights. The [pilot record](YAHOO_PROVIDER_PILOT.md)
explains why no real data was acquired in this PR. Do not begin PR 6 automatically.
