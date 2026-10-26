"""Append-only depth-audit checkpoints and offline, source-derived coverage."""

from collections import Counter
from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
import re

from ..ingestion.storage import digest, encode, read_bundle, write_bundle


class Journal:
    def __init__(self, root):
        self.root = Path(root)
        files, self.plan_hashes = read_bundle(self.root / "plan")
        self.plan = json.loads(files["plan.json"])
        self.calendar = json.loads(files["calendar.json"])
        self.events, self.abandoned = [], []
        previous = self.plan_hashes["bundle_sha256"]
        self.sequence = 0
        for path in sorted((self.root / "events").iterdir()):
            if path.is_symlink() or not path.is_dir() or not re.fullmatch(r"[0-9]{8}", path.name):
                raise ValueError("invalid audit checkpoint path")
            self.sequence = max(self.sequence, int(path.name) + 1)
            if not (path / "hashes.json").exists():
                self.abandoned.append(path.name)  # Interrupted write; never delete or adopt it.
                continue
            content, hashes = read_bundle(path)
            event = json.loads(content["event.json"])
            if event["sequence"] != int(path.name) or event["previous_sha256"] != previous:
                raise ValueError("audit checkpoint chain mismatch")
            previous = hashes["bundle_sha256"]
            self.events.append({"event": event, "files": content, "hashes": hashes, "path": path.name})
        self.tip = previous

    def append(self, event, extra=None):
        event = {**event, "sequence": self.sequence, "previous_sha256": self.tip}
        files = {"event.json": encode(event), **(extra or {})}
        hashes = write_bundle(self.root / "events" / f"{self.sequence:08d}", files)
        item = {"event": event, "files": files, "hashes": hashes, "path": f"{self.sequence:08d}"}
        self.events.append(item)
        self.tip = hashes["bundle_sha256"]
        self.sequence += 1
        return item


def window_rows(item, security):
    """Recompute from frozen native-return frame; don't trust summary counters."""
    from ..ingestion.canonical import convert
    from ..ingestion.frames import restore_frame

    event = item["event"]
    if "returned_frame.json" not in item["files"]:
        return [], [], []
    result = convert(restore_frame(item["files"]["returned_frame.json"]),
        security_id=security["security_id"], provider_symbol=security["ibkr_symbol"],
        frame_sha256=item["hashes"]["files"]["returned_frame.json"],
        snapshot_sha256=item["hashes"]["bundle_sha256"])
    selected, excluded = [], []
    for row in result["rows"]:
        day = row["session_date"]
        if day is None or not event["start"] <= day <= event["end"]:
            excluded.append({"row": row["source_row"]["row"], "session_date": day,
                             "reason": "INVALID_DATE" if day is None else "OUTSIDE_WINDOW"})
        else:
            row.update(symbol=security["symbol"], provider="ibkr",
                price_basis="IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED",
                volume_basis="IBKR_NATIVE_UNITS_UNVERIFIED")
            row["source_row"]["checkpoint"] = item["path"]
            selected.append(row)
    return selected, result["issues"], excluded


def head_date(value):
    from zoneinfo import ZoneInfo
    stamp = datetime.fromisoformat(value)
    if stamp.tzinfo is None:
        raise ValueError("head timestamp must be aware")
    return stamp.astimezone(ZoneInfo("America/New_York")).date().isoformat()


def progress(journal, symbol):
    cursor = journal.plan["end"]
    empty = 0
    security = next(i["security"] for i in journal.plan["config"]["instruments"] if i["security"]["symbol"] == symbol)
    head = None
    for item in journal.events:
        event = item["event"]
        if event.get("symbol") == symbol and event["kind"] == "head" and event["status"] == "SUCCESS" and head is None:
            head = head_date(event["timestamp"])
        if event.get("symbol") == symbol and event["kind"] == "window":
            if event["end"] != cursor:
                raise ValueError("checkpoint window does not follow replayed cursor")
            if event.get("decision") in {"ADVANCE", "BOUNDARY"}:
                overlap = journal.plan["config"]["overlap_days"]
                if event["status"] == "SUCCESS":
                    rows, _, _ = window_rows(item, security)
                    if not rows:
                        raise ValueError("successful advance without bounded observations")
                    earliest = min(r["session_date"] for r in rows)
                    floor = max(journal.plan["start"], head or journal.plan["start"])
                    first = next((s["session_date"] for s in journal.calendar["sessions"] if s["session_date"] >= floor), floor)
                    next_cursor = None if earliest <= first else min(
                        (date.fromisoformat(cursor)-timedelta(days=1)).isoformat(),
                        (date.fromisoformat(earliest)+timedelta(days=overlap-1)).isoformat())
                elif event["status"] in {"EMPTY_RESPONSE", "NO_DATA"}:
                    next_cursor = min((date.fromisoformat(cursor)-timedelta(days=1)).isoformat(),
                        (date.fromisoformat(event["start"])+timedelta(days=overlap-1)).isoformat())
                else:
                    raise ValueError("failed request cannot advance historical coverage")
                if next_cursor != event["next_cursor"] or (next_cursor is None) != (event["decision"] == "BOUNDARY"):
                    raise ValueError("checkpoint progress disagrees with frozen observations")
                cursor = next_cursor
                empty = empty + 1 if event["status"] in {"EMPTY_RESPONSE", "NO_DATA"} else 0
    return cursor, empty


def summarize(journal):
    """Deterministic offline interpretation, with separate search/quality status."""
    plan = journal.plan
    calendar_days = {s["session_date"] for s in journal.calendar["sessions"]}
    reports, bars = [], {}
    for instrument in plan["config"]["instruments"]:
        security = instrument["security"]
        symbol = security["symbol"]
        items = [i for i in journal.events if i["event"].get("symbol") == symbol]
        qualifications = [i["event"] for i in items if i["event"]["kind"] == "qualification"]
        contracts = [e["contract"] for e in qualifications if e["status"] == "SUCCESS"]
        contract = contracts[0] if contracts else None
        identity_changed = any(c != contract for c in contracts)
        heads = [i["event"] for i in items if i["event"]["kind"] == "head" and i["event"]["status"] == "SUCCESS"]
        head = heads[0]["timestamp"] if heads else None
        earliest_claim = head_date(head) if head else None
        windows = [i for i in items if i["event"]["kind"] == "window"]
        rows, overlaps, issues, exclusions, all_statuses = {}, [], [], [], Counter()
        for item in windows:
            event = item["event"]
            all_statuses[event["status"]] += 1
            selected, findings, excluded = window_rows(item, security)
            exclusions.extend({**v, "checkpoint": item["path"]} for v in excluded)
            issues.extend({**v, "checkpoint": item["path"]} for v in findings)
            if event["status"] != "SUCCESS":
                continue  # Diagnostic partial returns from failed calls are not successful coverage.
            for row in selected:
                day = row["session_date"]
                if day in rows:
                    fields = ("open", "high", "low", "close", "volume")
                    conflict = any(rows[day][f] != row[f] for f in fields)
                    overlaps.append({"session_date": day, "classification": "CONFLICT" if conflict else "IDENTICAL",
                        "first_source": rows[day]["source_row"], "other_source": row["source_row"]})
                else:
                    rows[day] = row  # Explicit first observation; all competing values remain captured.
        observed = set(rows)
        ordered = sorted(observed)
        first, last = (ordered[0], ordered[-1]) if ordered else (None, None)
        expected = {d for d in calendar_days if plan["start"] <= d <= plan["end"]}
        listing_excluded = {d for d in expected if
            (security.get("first_session") and d < security["first_session"]) or
            (security.get("last_session") and d > security["last_session"])}
        expected -= listing_excluded
        missing = sorted(expected - observed)
        internal = [d for d in missing if first and first < d < last]
        trailing = [d for d in missing if last and d > last]
        leading = [d for d in missing if first is None or d < first]
        off_calendar = sorted(observed - calendar_days)
        conflicts = sorted({v["session_date"] for v in overlaps if v["classification"] == "CONFLICT"})
        qualification_failed = any(e["status"] != "SUCCESS" for e in qualifications)
        quality_fail = (identity_changed or (qualification_failed and contracts) or off_calendar or conflicts or observed & listing_excluded or
                        any(v["status"] == "FAIL" for v in issues))
        cursor, empty = progress(journal, symbol)
        reached = cursor is None
        provider_exhausted = bool(reached and earliest_claim and earliest_claim > plan["start"] and first == earliest_claim
            and not [d for d in missing if d >= earliest_claim] and not quality_fail)
        stops = [i["event"] for i in items if i["event"]["kind"] == "instrument_stop"]
        stop = stops[-1]["reason"] if stops else None
        if stop is None and any(i["event"]["kind"] == "run_error" for i in journal.events):
            stop = "CONNECTION_FAILED"
        if reached and not missing and not quality_fail:
            status = "complete"
        elif provider_exhausted:
            status = "exhausted"
        elif observed:
            status = "partial"
        elif stop in {"DATA_PERMISSION", "QUALIFICATION_FAILED", "IDENTITY_CHANGED", "REQUEST_FAILED", "CONNECTION_FAILED"}:
            status = "failed"
        else:
            status = "inconclusive"
        warnings = []
        if leading:
            warnings.append("LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth")
        if internal or trailing:
            warnings.append("UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled")
        if all_statuses["EMPTY_RESPONSE"] or all_statuses["NO_DATA"]:
            warnings.append("EMPTY_OR_NO_DATA_IS_NOT_EXHAUSTION")
        if any(k not in {"SUCCESS", "EMPTY_RESPONSE"} for k in all_statuses):
            warnings.append("REQUEST_FAILURES_RETAINED; inspect request diagnostics")
        if quality_fail:
            warnings.append("QUALITY_OR_IDENTITY_FAILURE; no automatic repair or revision choice")
        if len(set(e["timestamp"] for e in heads)) > 1:
            warnings.append("PROVIDER_HEAD_TIMESTAMP_CHANGED; first claim retained")
        if contract is None:
            warnings.append("CONTRACT_NOT_QUALIFIED")
        diagnostics = [{"checkpoint": i["path"], **{k: i["event"][k] for k in
            ("kind", "status", "category", "code", "exception_type", "reason", "errors") if k in i["event"]}}
            for i in items if i["event"].get("status") not in {None, "SUCCESS"}]
        if any(i["event"]["kind"] == "head" and i["event"]["status"] != "SUCCESS" for i in items):
            warnings.append("PROVIDER_HEAD_UNAVAILABLE; older coverage remains unconfirmed")
        reports.append({"symbol": symbol, "security_id": security["security_id"], "instrument_kind": instrument["kind"],
            "security_type": "STK" if contract else None, "contract": contract,
            "requested_earliest_date": plan["start"], "requested_latest_date": plan["end"],
            "actual_earliest_bar": first, "actual_latest_bar": last, "observed_sessions": len(observed),
            "expected_sessions": len(expected), "missing_sessions": internal + trailing,
            "internal_gaps": internal, "trailing_missing_sessions": trailing, "unobserved_leading_sessions": leading,
            "all_missing_sessions": missing, "listing_exclusions": sorted(listing_excluded),
            "off_calendar_sessions": off_calendar, "conflicting_sessions": conflicts, "overlaps": overlaps,
            "issues": issues, "excluded_native_rows": exclusions, "data_basis": "TRADES", "use_rth": True,
            "native_basis_verified": False, "volume_units": "IBKR_NATIVE_UNITS_UNVERIFIED",
            "provider_head_timestamp": head, "provider_reported_earliest_date": earliest_claim,
            "exhaustion_evidence": "HEAD_TIMESTAMP_AND_MATCHING_OBSERVED_BOUNDARY" if provider_exhausted else None,
            "search_boundary_reached": reached, "resume_cursor": cursor, "status": status,
            "request_status_counts": dict(sorted(all_statuses.items())), "stop_reason": stop,
            "warnings": warnings, "diagnostics": diagnostics, "historical_listing_completeness": "UNKNOWN",
            "corporate_action_completeness": "UNKNOWN", "historical_publication_times": "UNKNOWN"})
        bars[symbol] = [rows[d] for d in ordered]
    return reports, bars


def markdown(reports, plan):
    lines = ["# IBKR daily historical-depth audit", "",
        f"Origin: **{plan['origin']}**. Frozen as-of: {plan['as_of']}. Data: completed daily TRADES, RTH.", "",
        "Coverage describes this endpoint/contract/retrieval, not survivorship-free or point-in-time research readiness.", "",
        "| Symbol / conId | Kind | Requested start | Observed first | Observed last | Sessions | Unexpected missing | Status |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- |"]
    for r in reports:
        con_id = r["contract"]["conId"] if r["contract"] else "unqualified"
        lines.append(f"| {r['symbol']} / {con_id} | {r['instrument_kind']} | {r['requested_earliest_date']} | "
            f"{r['actual_earliest_bar'] or 'UNKNOWN'} | {r['actual_latest_bar'] or 'UNKNOWN'} | "
            f"{r['observed_sessions']} | {len(r['missing_sessions'])} | {r['status']} |")
    lines += ["", "Leading unobserved sessions are reported separately; they are not automatically internal gaps or pre-IPO history.",
        "Exhausted requires a provider head timestamp matched by an observed boundary with complete coverage above it.",
        "An empty response or a failed request alone never proves historical exhaustion.",
        "TRADES retains IBKR's documented split-adjusted convention, not verified raw execution prices; volume units remain unverified.",
        "No forward filling, action inference, trade reconstruction or account query is performed.", ""]
    for r in reports:
        lines += [f"## {r['symbol']}", "", f"Stop: {r['stop_reason'] or 'not recorded'}; provider head: {r['provider_head_timestamp'] or 'UNKNOWN'}; "
            f"leading unobserved: {len(r['unobserved_leading_sessions'])}; conflicting sessions: {len(r['conflicting_sessions'])}.", ""]
        lines += [f"- {w}" for w in r["warnings"]] or ["- No detected coverage/quality warning in this bounded audit."]
        lines.append("")
    return "\n".join(lines)


def freeze_report(audit, output):
    journal = load_audit(audit)
    reports, bars = summarize(journal)
    manifest = {"schema_version": "ibkr_depth_report_v1", "provider": "ibkr", "origin": journal.plan["origin"],
        "plan_sha256": journal.plan_hashes["bundle_sha256"], "journal_tip_sha256": journal.tip,
        "checkpoint_hashes": {i["path"]: i["hashes"]["bundle_sha256"] for i in journal.events},
        "abandoned_unsealed_checkpoints": journal.abandoned, "plan": journal.plan,
        "calendar_sha256": digest(encode(journal.calendar)), "instrument_count": len(reports),
        "status_counts": dict(Counter(r["status"] for r in reports)), "adjusted_last_comparison": "NOT_REQUESTED",
        "capture_level": "ib_async_client_return_not_wire_payload", "account_identifiers_retained": False}
    files = {"audit_manifest.json": encode(manifest), "plan.json": encode(journal.plan), "plan-hashes.json": encode(journal.plan_hashes),
        "coverage.json": encode(reports), "daily_bars.json": encode(bars),
        "calendar.json": encode(journal.calendar), "summary.md": markdown(reports, journal.plan).encode()}
    # Self-contained replay: embed original checkpoint bytes under safe flat keys.
    for item in journal.events:
        for name, content in item["files"].items():
            files[f"checkpoint-{item['path']}-{name}"] = content
        files[f"checkpoint-{item['path']}-hashes.json"] = encode(item["hashes"])
    return write_bundle(Path(output), files)


def load_audit(path):
    """A frozen report can reproduce itself offline after the journal is removed."""
    path = Path(path)
    if not (path / "audit_manifest.json").exists():
        return Journal(path)
    files, _ = read_bundle(path)
    manifest = json.loads(files["audit_manifest.json"])
    journal = object.__new__(Journal)
    journal.plan_hashes = json.loads(files["plan-hashes.json"])
    journal.plan, journal.calendar = json.loads(files["plan.json"]), json.loads(files["calendar.json"])
    previous = journal.plan_hashes["bundle_sha256"]

    def check(content, hashes):
        if hashes["bundle_sha256"] != digest(encode(hashes["files"])) or {k: digest(v) for k, v in content.items()} != hashes["files"]:
            raise ValueError("embedded checkpoint integrity mismatch")
    check({"plan.json": files["plan.json"], "calendar.json": files["calendar.json"]}, journal.plan_hashes)
    if manifest["plan_sha256"] != previous:
        raise ValueError("embedded plan mismatch")
    journal.events = []
    for name, sha in sorted(manifest["checkpoint_hashes"].items()):
        prefix = f"checkpoint-{name}-"
        hashes = json.loads(files[prefix + "hashes.json"])
        content = {k[len(prefix):]: v for k, v in files.items() if k.startswith(prefix) and k != prefix + "hashes.json"}
        check(content, hashes)
        event = json.loads(content["event.json"])
        if hashes["bundle_sha256"] != sha or event["previous_sha256"] != previous or event["sequence"] != int(name):
            raise ValueError("embedded checkpoint chain mismatch")
        journal.events.append({"event": event, "files": content, "hashes": hashes, "path": name})
        previous = sha
    if previous != manifest["journal_tip_sha256"]:
        raise ValueError("embedded tip mismatch")
    journal.tip, journal.abandoned = previous, manifest["abandoned_unsealed_checkpoints"]
    return journal
