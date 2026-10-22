"""Independent reconciliation and affirmative evidence gates; no provider imports."""

from collections import Counter
from datetime import date, timedelta
import importlib.metadata
from pathlib import Path
import platform

from ..models import timestamp
from .calendar import schedule
from .canonical import convert
from .snapshots import read_snapshot
from .storage import digest, encode


def verified(record):
    return (isinstance(record, dict) and record.get("status") == "VERIFIED"
            and isinstance(record.get("reference"), str) and bool(record["reference"].strip()))


def analyze(snapshot: Path, evidence: dict | None = None) -> dict:
    saved = read_snapshot(snapshot)
    req, acq, hashes = saved["request"], saved["acquisition"], saved["hashes"]
    evidence = evidence if evidence is not None else {"schema_version": "research_evidence_v1"}
    if not isinstance(evidence, dict) or evidence.get("schema_version") != "research_evidence_v1":
        raise ValueError("expected research_evidence_v1 evidence object")
    for section in ("identity", "basis", "actions", "availability"):
        if not isinstance(evidence.get(section, {}), dict):
            raise ValueError(f"invalid evidence section: {section}")
    identity, basis = evidence.get("identity", {}), evidence.get("basis", {})
    action_evidence, availability = evidence.get("actions", {}), evidence.get("availability", {})
    start, end = req["start"], req["end"]
    completed = timestamp(acq["completed_at"])
    horizon = max(end, completed.date().isoformat())
    frozen_schedule = schedule(start, end)
    frame_hash = hashes["files"].get("returned_frame.json")
    canonical = convert(saved["frame"], security_id=identity.get("security_id"),
                        provider_symbol=req["provider_symbol"], frame_sha256=frame_hash,
                        snapshot_sha256=hashes["bundle_sha256"]) if saved["frame"] is not None else {
                            "schema_version": "canonical_daily_v1", "rows": [], "events": [],
                            "issues": [{"code": "MISSING_RETURNED_FRAME", "status": "FAIL"}]}
    # Evidence must concern exactly this request+frame content. Synthetic claims
    # are not accepted as evidence for a real acquisition.
    bound = evidence.get("snapshot_content_sha256") == acq["content_sha256"]
    kind_ok = (evidence.get("kind") == "synthetic" if req.get("origin") == "synthetic"
               else evidence.get("kind") == "recorded_evidence")
    bound = bound and kind_ok

    def covers(section):
        try:
            return (date.fromisoformat(section["coverage_start"]) <= date.fromisoformat(start)
                    and date.fromisoformat(section["coverage_end"]) >= date.fromisoformat(horizon))
        except (KeyError, TypeError, ValueError):
            return False

    def valid_identity():
        try:
            return (bound and verified(identity) and isinstance(identity.get("security_id"), str)
                    and bool(identity["security_id"].strip())
                    and identity.get("provider_symbol") == req["provider_symbol"]
                    and identity.get("research_symbol") == req["research_symbol"]
                    and identity.get("currency") == "USD" and bool(identity.get("listing_venue"))
                    and timestamp(identity["known_at"]) <= completed
                    and date.fromisoformat(identity["valid_from"]) <= date.fromisoformat(start)
                    and date.fromisoformat(identity["valid_through"]) >= date.fromisoformat(end))
        except (ValueError, TypeError, KeyError):
            return False

    identity_ok = valid_identity()
    alignment_ok = identity_ok and (identity.get("listing_venue") == "XNYS"
                                   or verified(identity.get("xnys_alignment")))
    counts = Counter(r["session_date"] for r in canonical["rows"])
    invalid = {i.get("row") for i in canonical["issues"] if i["status"] == "FAIL"}
    expected = {s["session_date"]: s for s in frozen_schedule["sessions"]}
    reconciliation = []
    known_boundaries = identity.get("listing_boundaries", {})
    if not isinstance(known_boundaries, dict):
        raise ValueError("invalid listing boundary evidence")
    for key in ("first_session", "last_session"):
        if key in known_boundaries:
            date.fromisoformat(known_boundaries[key])
    boundary_ok = identity_ok and verified(known_boundaries)
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    for offset in range((last - first).days + 1):
        day = (first + timedelta(days=offset)).isoformat()
        if day not in expected:
            label = "OFF_CALENDAR_OBSERVATION" if counts[day] else "VALID_MARKET_CLOSURE"
        elif (boundary_ok and (day < known_boundaries.get("first_session", day)
                              or day > known_boundaries.get("last_session", day))):
            label = "KNOWN_OUTSIDE_LISTING_PERIOD" if not counts[day] else "BAR_OUTSIDE_LISTING_PERIOD"
        elif not counts[day]:
            label = "EXPECTED_SESSION_MISSING" if boundary_ok else "UNKNOWN_SECURITY_SPECIFIC_GAP"
        elif counts[day] != 1:
            label = "INVALID_SESSION_BAR"
        else:
            row = next(r for r in canonical["rows"] if r["session_date"] == day)
            label = "EXPECTED_SESSION_VALID" if row["source_row"]["row"] not in invalid else "INVALID_SESSION_BAR"
            if timestamp(expected[day]["closes_at"]) > completed:
                label = "INCOMPLETE_SESSION"
        reconciliation.append({"session_date": day, "classification": label, "returned_rows": counts[day]})
    for day in sorted(d for d in counts if d is not None and not start <= d <= end):
        reconciliation.append({"session_date": day, "classification": "OUTSIDE_REQUEST_INTERVAL",
                               "returned_rows": counts[day]})
    calendar_errors = [r for r in reconciliation if r["classification"] not in {
        "EXPECTED_SESSION_VALID", "VALID_MARKET_CLOSURE", "KNOWN_OUTSIDE_LISTING_PERIOD"}]
    # No silent truncation around listing boundaries: require a fresh narrower
    # request for an exportable experiment rather than omitting listed sessions.
    listing_exclusions = any(r["classification"] == "KNOWN_OUTSIDE_LISTING_PERIOD" for r in reconciliation)
    price_basis = basis.get("price_basis", "UNKNOWN")
    if price_basis not in {"RAW_VERIFIED", "SPLIT_ADJUSTED", "OTHER_ADJUSTED", "UNKNOWN"}:
        raise ValueError("invalid price basis classification")
    basis_ok = (bound and price_basis == "RAW_VERIFIED" and verified(basis) and covers(basis)
                and all(verified(basis.get(k)) and basis[k].get("convention") == "unadjusted"
                        for k in ("split_adjustment", "dividend_adjustment"))
                and verified(basis.get("volume")) and basis["volume"].get("units") == "contemporaneous_shares")
    independent_events = action_evidence.get("events", [])
    if not isinstance(independent_events, list):
        raise ValueError("action events must be a list")
    actions = {"schema_version": "corporate_actions_v1", "provider_events": canonical["events"],
               "source_snapshot_sha256": hashes["bundle_sha256"], "retrieved_at": acq["completed_at"],
               "provider_coverage": "returned_interval_only_unknown_completeness",
               "independent_evidence": action_evidence, "required_horizon": {"start": start, "end": horizon}}
    actions_ok = (bound and verified(action_evidence) and covers(action_evidence)
                  and not canonical["events"] and not independent_events)
    availability_ok = bound and verified(availability) and availability.get("historical_availability") == "verified"
    bar_times = availability.get("sessions", {})
    if not isinstance(bar_times, dict):
        raise ValueError("availability sessions must be a mapping")
    availability_issues = []
    # Check against actual next exchange open, including the last exported bar.
    extended = schedule(start, (last + timedelta(days=10)).isoformat())["sessions"]
    next_opens = {s["session_date"]: extended[i + 1]["opens_at"] for i, s in enumerate(extended[:-1])}
    for day, row in expected.items():
        try:
            at = timestamp(bar_times[day])
            if not timestamp(row["closes_at"]) <= at < timestamp(next_opens[day]) or at > completed:
                raise ValueError("invalid historical availability")
        except (ValueError, KeyError, TypeError):
            availability_ok = False
            availability_issues.append({"session_date": day, "code": "HISTORICAL_AVAILABILITY_UNKNOWN_OR_INVALID"})
    quality_ok = bool(canonical["rows"]) and not canonical["issues"]
    acquisition_ok = (acq["status"] == "SUCCESS" and not acq.get("errors")
                      and timestamp(acq["started_at"]) <= completed)
    gates = {
        "acquisition": "PASS" if acquisition_ok else "FAIL",
        "data_quality": "PASS" if quality_ok else "FAIL",
        "calendar": "PASS" if not calendar_errors and not listing_exclusions and alignment_ok else (
            "FAIL" if calendar_errors or listing_exclusions else "UNKNOWN"),
        "identity": "PASS" if identity_ok else "UNKNOWN",
        "price_basis": "PASS" if basis_ok else ("FAIL" if price_basis in {"SPLIT_ADJUSTED", "OTHER_ADJUSTED"} else "UNKNOWN"),
        "corporate_actions": "PASS" if actions_ok else ("FAIL" if canonical["events"] or independent_events else "UNKNOWN"),
        "availability": "PASS" if availability_ok else "UNKNOWN",
    }
    blockers = ["BLOCKED_" + name.upper() for name, status in gates.items() if status != "PASS"]
    quality = {"schema_version": "data_quality_v1", "request": req, "acquisition": acq,
               "security_identity": identity, "evidence_binding": "PASS" if bound else "UNKNOWN",
               "assessment_origin": "synthetic" if req.get("origin") == "synthetic" else "user_supplied_evidence_not_independently_verified",
               "gates": gates, "export_decision": "EXPORT_READY" if not blockers else "BLOCKED",
               "blocking_reasons": blockers, "issues": canonical["issues"], "calendar": reconciliation,
               "calendar_counts": dict(Counter(r["classification"] for r in reconciliation)),
               "corporate_actions": actions,
               "basis": {"price_basis": "UNKNOWN", "split_adjustment": {"status": "UNKNOWN"},
                         "dividend_adjustment": {"status": "UNKNOWN"}, "volume": {"status": "UNKNOWN"}, **basis},
               "provider_basis_documentation": {
                   "reported_close": "split_adjusted_per_Yahoo_field_documentation_not_response_verified",
                   "reported_adjusted_close": "splits_and_distributions_per_Yahoo_documentation",
                   "api_ohlc_basis": "UNKNOWN", "api_volume_units": "UNKNOWN",
                   "reference": "docs/YAHOO_DATA_SOURCE_AUDIT.md#b-price-basis-and-corporate-actions"},
               "historical_availability": "verified" if availability_ok else "unknown",
               "availability_issues": availability_issues,
               "unapproved_availability_proposal": "A close-plus-latency model would assume historical finalization; no such model is implemented or approved.",
               "revision_comparison": {"status": "NOT_APPLICABLE", "reason": "Separate compare operation; no second snapshot supplied."},
               "source": {"snapshot_bundle_sha256": hashes["bundle_sha256"], "snapshot_content_sha256": acq["content_sha256"]},
               "artifacts": {"canonical": "canonical.json", "schedule": "schedule.json", "actions": "actions.json",
                             "evidence": "evidence.json", "provenance": "provenance.json"}}
    prepared = {"canonical.json": encode(canonical), "schedule.json": encode(frozen_schedule),
                "actions.json": encode(actions), "evidence.json": encode(evidence)}
    source = Path(__file__).parent.parent
    code_hashes = {str(p.relative_to(source)): digest(p.read_bytes())
                   for package in ("ingestion", "providers") for p in sorted((source / package).glob("*.py"))}
    provenance = {"schema_version": "yahoo_provenance_v1", "snapshot_hashes": hashes,
                  "request": req, "acquisition": acq, "evidence": evidence,
                  "converter_source_sha256": digest(encode(code_hashes)), "converter_files": code_hashes,
                  "python": platform.python_version(),
                  "dependencies": {k: importlib.metadata.version(k) for k in ("pandas", "numpy", "exchange-calendars", "tzdata", "pytz")},
                  "upstream_files": {name: digest(data) for name, data in sorted(prepared.items())}}
    prepared["provenance.json"] = encode(provenance)
    quality["artifact_sha256"] = {name: digest(data) for name, data in sorted(prepared.items())}
    prepared["quality.json"] = encode(quality)
    lines = ["# Data preparation quality", "", f"Export decision: {quality['export_decision']}",
             f"Snapshot bundle SHA-256: {hashes['bundle_sha256']}",
             f"Provider symbol: {req['provider_symbol']}", f"Acquisition: {acq['status']}",
             f"Historical availability: {quality['historical_availability']}", "",
             "| Gate | Status |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in gates.items()]
    lines += ["", "Blocking reasons: " + (", ".join(blockers) or "none"), "",
              "## Request and returned coverage", "",
              f"Requested inclusive interval: {start} through {end}.",
              f"Returned rows: {len(canonical['rows'])}. Client: {acq.get('client')} {acq.get('client_version')}.",
              f"Retrieval completed (UTC): {acq['completed_at']}. Capture: {acq['capture_level']}.",
              f"Errors: {encode(acq.get('errors', [])).decode().strip()}", "",
              "## Calendar reconciliation", "", "| Classification | Dates |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in sorted(quality["calendar_counts"].items())]
    lines += ["", "## OHLCV findings", "", "| Code | Status | Row | Session |", "| --- | --- | --- | --- |"]
    lines += [f"| {i['code']} | {i['status']} | {i.get('row')} | {i.get('session_date')} |" for i in canonical["issues"]]
    lines += ["", "## Actions, basis and identity", "",
              f"Returned provider events: {len(canonical['events'])}; independent events: {len(independent_events)}.",
              f"Required action/basis horizon: {start} through {horizon} (retrieval UTC date included).",
              f"Asserted basis: {price_basis}; split/dividend and volume evidence are separate gates.",
              "Identity and affirmative evidence are caller-supplied; references are not independently authenticated by this program.",
              "No returned events does not establish complete action coverage.", "",
              "## Artifacts and revisions", "",
              "Revision comparison: NOT_APPLICABLE here; use the separate compare command for two snapshots.",
              "See [quality.json](quality.json) for every affected session and all evidence limitations.",
              "See [canonical.json](canonical.json), [schedule.json](schedule.json), [actions.json](actions.json),",
              "[evidence.json](evidence.json) and [provenance.json](provenance.json).", "",
              "| Artifact | SHA-256 |", "| --- | --- |"]
    lines += [f"| {name} | {value} |" for name, value in quality["artifact_sha256"].items()]
    lines += ["",
              "", "Price discontinuities and zero volume require investigation; no repair or automatic action inference.",
              quality["unapproved_availability_proposal"], "",
              "An evidenced synthetic fixture validates gates only; it is not Yahoo basis or strategy evidence.", ""]
    prepared["summary.md"] = "\n".join(lines).encode()
    return {"files": prepared, "quality": quality, "schedule": frozen_schedule,
            "canonical": canonical, "evidence": evidence, "snapshot": saved}
