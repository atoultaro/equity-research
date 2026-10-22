"""Native basis metadata, canonical conversion and independent session reconciliation."""

from collections import Counter
from datetime import datetime
import json

from ..ingestion.calendar import schedule
from ..ingestion.canonical import convert
from ..ingestion.frames import restore_frame
from ..ingestion.storage import digest, encode, read_bundle

BASIS = {
    "yahoo": {"price_basis": "YAHOO_NATIVE_UNVERIFIED", "volume_basis": "YAHOO_NATIVE_UNVERIFIED",
              "verified": False, "data_type": "OHLC_auto_adjust_false",
              "limitation": "auto_adjust=False does not prove raw as-traded prices or share units"},
    "ibkr": {"price_basis": "IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED",
             "volume_basis": "IBKR_NATIVE_UNITS_UNVERIFIED", "verified": False, "data_type": "TRADES_RTH",
             "limitation": "TRADES documented split-adjusted, not dividend-adjusted; filtered feed; units unverified"},
}


def read_acquisition(path, security):
    files, hashes = read_bundle(path)
    req, acq = json.loads(files["request.json"]), json.loads(files["acquisition.json"])
    provider = req["provider"]
    if (provider not in BASIS or req.get("schema_version") != f"{provider}_request_v1"
            or acq.get("schema_version") != f"{provider}_acquisition_v1"):
        raise ValueError("unsupported acquisition schema")
    identity = {k: digest(v) for k, v in sorted(files.items()) if k != "acquisition.json"}
    if acq["content_sha256"] != digest(encode(identity)):
        raise ValueError("acquisition content hash mismatch")
    mapped = security.yahoo_symbol if provider == "yahoo" else security.ibkr_symbol
    if req["research_symbol"] != security.symbol or req["provider_symbol"] != mapped:
        raise ValueError("snapshot identity does not match explicit mapping")
    if provider == "ibkr" and req["security"] != security.record():
        raise ValueError("IBKR snapshot mapping differs")
    result = convert(restore_frame(files["returned_frame.json"]), security_id=security.security_id,
                     provider_symbol=mapped, frame_sha256=hashes["files"]["returned_frame.json"],
                     snapshot_sha256=hashes["bundle_sha256"]) if "returned_frame.json" in files else {
                         "rows": [], "events": [], "issues": [{"code": "MISSING_FRAME", "status": "FAIL"}]}
    basis = BASIS[provider]
    for row in result["rows"]:
        row.update(symbol=security.symbol, provider=provider, price_basis=basis["price_basis"],
                   volume_basis=basis["volume_basis"])
        if provider == "ibkr" and "native_row_indices" in acq:
            row["source_row"].update(native_file="returned_bars.json",
                native_sha256=hashes["files"]["returned_bars.json"],
                native_row=acq["native_row_indices"][row["source_row"]["row"]])
    # Retain all native observations in the snapshot. Completed-session filtering is
    # explicit and only affects the reusable cache; it never edits the capture.
    sessions = {s["session_date"]: s for s in schedule(req["start"], req["end"])["sessions"]}
    begun = datetime.fromisoformat(acq["started_at"])
    if begun.tzinfo is None:
        raise ValueError("acquisition time must be aware")
    rows, excluded = [], []
    for row in result["rows"]:
        session = sessions.get(row["session_date"])
        if session and datetime.fromisoformat(session["closes_at"]) > begun:
            excluded.append(row["session_date"])
        else:
            rows.append(row)
    return {"request": req, "acquisition": acq, "rows": rows, "issues": result["issues"],
            "events": result["events"], "basis": dict(basis), "excluded_incomplete_sessions": excluded,
            "snapshot_sha256": hashes["bundle_sha256"], "snapshot_reference": str(path),
            "historical_availability": "unknown", "corporate_action_completeness": "unknown"}


def reconcile(rows, security, start, end):
    calendar = schedule(start, end)
    for boundary in (security.first_session, security.last_session):
        if boundary and not schedule(boundary, boundary)["sessions"]:
            raise ValueError("listing boundary must be an actual research-calendar session")
    counts = Counter(row["session_date"] for row in rows)
    sessions = {s["session_date"] for s in calendar["sessions"]}
    excluded = sorted(day for day in sessions if
                      (security.first_session and day < security.first_session) or
                      (security.last_session and day > security.last_session))
    expected = sessions - set(excluded)
    missing = sorted(expected - counts.keys())
    off_calendar = sorted(day for day in counts if day not in sessions)
    outside_listing = sorted(set(excluded) & counts.keys())
    duplicates = sorted(day for day, count in counts.items() if count > 1)
    return {"schema_version": "research_calendar_quality_v1", "calendar": calendar,
            "listing_venue": security.listing_venue, "listing_reference": security.listing_reference,
            "listing_exclusions": excluded, "missing_sessions": missing, "off_calendar_sessions": off_calendar,
            "outside_listing_sessions": outside_listing, "duplicate_sessions": duplicates,
            "gap_interpretation": "explicit_listing_boundaries" if security.listing_reference else "listing_history_unknown",
            "status": "FAIL" if missing or off_calendar or outside_listing or duplicates else "PASS"}
