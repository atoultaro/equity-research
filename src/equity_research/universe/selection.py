"""Causal monthly liquidity selection; membership is independent of holdings."""

from calendar import monthrange
from datetime import date, timedelta
from decimal import Context, localcontext
import json
from pathlib import Path
from statistics import mean, median
from zoneinfo import ZoneInfo

from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..models import number, timestamp
from .master import SecurityMaster, day
from .panel import ResearchPanel


def default_definition(top_n=1000):
    return {"schema_version": "universe_definition_v1", "top_n": top_n, "history_sessions": 60,
            "minimum_close": "5", "currency": "USD", "venues": ["XASE", "XNAS", "XNYS"],
            "eligible_types": ["COMMON", "REIT_COMMON"],
            "excluded_types": ["ADR", "BDC", "SPAC_COMMON", "SPAC_UNIT", "ETF", "ETN", "CEF", "PREFERRED", "WARRANT", "RIGHT", "DEBT", "OTHER"],
            "dual_classes": "EACH_SECURITY", "recent_ipos": "REQUIRE_60_COMPLETED_SESSIONS",
            "price_basis": "RAW_TRADED", "volume_basis": "RAW_SHARES",
            "liquidity": "MEDIAN_60_CLOSE_TIMES_VOLUME", "ties": "ASCENDING_SECURITY_ID",
            "reconstitution": "MONTH_END_CLOSE_THEN_NEXT_OPEN_AFTER_DECISION",
            "unknown_knowledge_policy": "EXCLUDE", "minimum_price_comparison": "GREATER_OR_EQUAL"}


def validate_definition(definition):
    template = default_definition(definition["top_n"])
    template["minimum_close"] = definition["minimum_close"]
    template["unknown_knowledge_policy"] = definition["unknown_knowledge_policy"]
    if (definition != template or type(definition["top_n"]) is not int or not 1 <= definition["top_n"] <= 3000
            or number(definition["minimum_close"]) <= 0
            or definition["unknown_knowledge_policy"] not in {"EXCLUDE", "RECONSTRUCT_EXPLICITLY"}):
        raise ValueError("unsupported universe definition")


def _selection(master, panel, definition, month, decision):
    year, monthnum = map(int, month.split("-"))
    first = date(year, monthnum, 1).isoformat()
    last = date(year, monthnum, monthrange(year, monthnum)[1]).isoformat()
    if panel.calendar["start"] > first or panel.calendar["end"] < last:
        raise ValueError("calendar must cover the complete selection month")
    sessions = panel.calendar["sessions"]
    monthly = [s for s in sessions if first <= s["session_date"] <= last]
    observation_day = monthly[-1]["session_date"]
    decision = decision or (timestamp(monthly[-1]["closes_at"]) + timedelta(hours=2)).isoformat()
    cutoff = timestamp(decision)
    if cutoff <= timestamp(monthly[-1]["closes_at"]):
        raise ValueError("monthly decision must follow final completed month session")
    activation = next((s for s in sessions if timestamp(s["opens_at"]) > cutoff), None)
    if activation is None:
        raise ValueError("frozen calendar must include next eligible open")
    expected = [s["session_date"] for s in sessions if s["session_date"] <= observation_day][-60:]
    if len(expected) != 60:
        raise ValueError("calendar lacks required 60 completed sessions")
    reconstruct = definition["unknown_knowledge_policy"] == "RECONSTRUCT_EXPLICITLY"
    candidates = []
    for sid in sorted(master.by_id):
        fact = master.as_of(sid, observation_day, decision, reconstruct_unknown=reconstruct)
        reasons = []
        row = {"security_id": sid, "identity": fact, "liquidity_score": None, "rank": None,
               "selected": False, "pit_quality": "PIT_UNVERIFIED", "observation_cutoff": observation_day,
               "availability_cutoff": decision, "input_observations_sha256": None}
        if fact is None:
            reasons.append("IDENTITY_NOT_KNOWN_OR_NOT_EFFECTIVE")
        else:
            if fact["listing_start"] is None: reasons.append("UNKNOWN_LISTING_DATE")
            if fact["listing_start"] is not None and fact["listing_start"] > expected[0]: reasons.append("INSUFFICIENT_LISTED_HISTORY")
            if fact["listing_end"] is not None and fact["listing_end"] < observation_day: reasons.append("LISTING_ENDED_AS_KNOWN")
            if fact["security_type"] not in definition["eligible_types"]: reasons.append("INELIGIBLE_SECURITY_TYPE")
            if fact["currency"] != "USD": reasons.append("NON_USD")
            if fact["exchange"] not in definition["venues"]: reasons.append("INELIGIBLE_VENUE")
            if fact["trading_status"] != "ACTIVE": reasons.append("NOT_ACTIVE_AS_KNOWN")
            if fact["identity_confidence"] == "WEAK": reasons.append("WEAK_IDENTITY")
            if any(fact[k] is None for k in ("issuer_id", "share_class_id", "provider_security_id", "security_type", "currency", "symbol", "exchange", "trading_status")) or not fact["identity_evidence"]:
                reasons.append("INCOMPLETE_IDENTITY_OR_CLASSIFICATION")
            history_facts = [master.as_of(sid, d, decision, reconstruct_unknown=reconstruct) for d in expected]
            if any(f is None or f["exchange"] not in definition["venues"] or f["currency"] != "USD"
                   or f["security_type"] not in definition["eligible_types"] or f["trading_status"] != "ACTIVE"
                   or f["listing_start"] is None or f["listing_start"] > d
                   or f["listing_end"] is not None and f["listing_end"] < d for d, f in zip(expected, history_facts)):
                reasons.append("INSUFFICIENT_ELIGIBLE_SESSION_HISTORY")
            prices = {r["session_date"]: r for r in panel.rows_as_of(sid, decision, through=observation_day, start=expected[0], reconstruct_unknown=reconstruct)}
            window = [prices[d] for d in expected if d in prices]
            row["available_sessions"] = len(window)
            if len(window) != 60: reasons.append("MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS")
            if any(r["volume"] is None for r in window): reasons.append("MISSING_VOLUME")
            if any(r["volume"] is not None and number(r["volume"]) <= 0 for r in window): reasons.append("NONPOSITIVE_VOLUME")
            if any(r["price_basis"] != definition["price_basis"] or r["volume_basis"] != definition["volume_basis"] for r in window): reasons.append("UNADMITTED_LIQUIDITY_BASIS")
            if any(r["quality_status"] != "VALID" for r in window): reasons.append("UNVERIFIED_OBSERVATION_QUALITY")
            if window and number(window[-1]["close"]) < number(definition["minimum_close"]): reasons.append("BELOW_MINIMUM_PRICE")
            row["input_observations_sha256"] = digest(encode(window))
            row["source_snapshots"] = sorted({r["source_snapshot_sha256"] for r in window} | {fact["source_snapshot_sha256"]})
            unknown = fact["known_at"] is None or any(r["known_at"] is None or r["available_at"] is None for r in window)
            qualities = [master.manifest["quality"]] + [s["quality"] for s in panel.manifest["sources"] if s["source_snapshot_sha256"] in row["source_snapshots"]]
            documented = fact["identity_confidence"] == "VERIFIED" and all(r["availability_status"] == "DOCUMENTED" for r in window)
            row["pit_quality"] = ("PIT_UNVERIFIED" if unknown or "PIT_UNVERIFIED" in qualities else
                                  "PIT_VERIFIED" if documented and all(q == "PIT_VERIFIED" for q in qualities) else "PIT_RECONSTRUCTED")
            if not reasons:
                row["liquidity_score"] = str(median([number(r["close"])*number(r["volume"]) for r in window]))
        row["rejection_reasons"] = reasons
        candidates.append(row)
    ranked = sorted((r for r in candidates if not r["rejection_reasons"]), key=lambda r: (-number(r["liquidity_score"]), r["security_id"]))
    for rank, row in enumerate(ranked, 1):
        row["rank"] = rank
        row["selected"] = rank <= definition["top_n"]
    members = [r for r in ranked if r["selected"]]
    source_quality = master.manifest["quality"]
    unknown_identity = any(f["known_at"] is None and f["effective_from"] <= observation_day and
                           (f["effective_to"] is None or observation_day < f["effective_to"]) for f in master.records)
    incomplete_ranking = any(set(c["rejection_reasons"]) & {"WEAK_IDENTITY", "INCOMPLETE_IDENTITY_OR_CLASSIFICATION", "UNKNOWN_LISTING_DATE", "MISSING_VOLUME", "UNVERIFIED_OBSERVATION_QUALITY"}
                             or c["identity"] is not None and c["identity"]["security_type"] in definition["eligible_types"]
                             and c["identity"]["listing_start"] is not None and c["identity"]["listing_start"] <= expected[0] and c["identity"]["trading_status"] == "ACTIVE"
                             and "MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS" in c["rejection_reasons"] for c in candidates)
    quality = ("PIT_UNVERIFIED" if unknown_identity or incomplete_ranking or source_quality == "PIT_UNVERIFIED" or any(r["pit_quality"] == "PIT_UNVERIFIED" for r in members) else
               "PIT_VERIFIED" if members and source_quality == "PIT_VERIFIED" and all(r["pit_quality"] == "PIT_VERIFIED" for r in members) else "PIT_RECONSTRUCTED")
    # Membership expires at the next scheduled reconstitution even when that
    # snapshot is missing. A sparse pilot must not carry one list across years.
    nextfirst = (date(year, monthnum, 28) + timedelta(days=4)).replace(day=1)
    nextlast = date(nextfirst.year, nextfirst.month, monthrange(nextfirst.year, nextfirst.month)[1]).isoformat()
    following = [s for s in sessions if s["session_date"] > nextlast]
    expires = following[0]["session_date"] if following else (date.fromisoformat(nextlast) + timedelta(days=1)).isoformat()
    if activation["session_date"] >= expires:
        raise ValueError("decision arrived after next scheduled reconstitution")
    return {"scheduled_expiry": expires, "selection_month": month, "selection_date": observation_day, "decision_timestamp": decision,
            "effective_start": activation["session_date"], "effective_end": None,
            "history_start": expected[0], "observation_cutoff": observation_day, "pit_quality": quality,
            "candidates": candidates, "members": members,
            "summary": {"known_effective_securities": sum(c["identity"] is not None for c in candidates),
                        "eligible_count": len(ranked), "member_count": len(members),
                        "requested_count_met": len(members) == definition["top_n"],
                        "incomplete_candidate_ranking_evidence": bool(unknown_identity or incomplete_ranking),
                        "missing_price_candidates": sum("MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS" in c["rejection_reasons"] for c in candidates),
                        "missing_volume_candidates": sum("MISSING_VOLUME" in c["rejection_reasons"] for c in candidates),
                        "rejection_counts": {reason: sum(reason in c["rejection_reasons"] for c in candidates)
                                             for reason in sorted({reason for c in candidates for reason in c["rejection_reasons"]})},
                        "median_liquidity": str(median([number(r["liquidity_score"]) for r in members])) if members else None,
                        "mean_liquidity": str(mean([number(r["liquidity_score"]) for r in members])) if members else None}}


def _universe_records(master, panel, definition, months, *, decisions=None):
    """Derive all semantic outputs from frozen inputs and declared selection clocks."""
    validate_definition(definition)
    if not months or list(months) != sorted(set(months)):
        raise ValueError("unique ascending selection months required")
    unknown_ids = set(panel.index) - set(master.by_id)
    if unknown_ids:
        raise ValueError("panel contains securities absent from master")
    with localcontext(Context(prec=28)):
        snapshots = [_selection(master, panel, definition, m, (decisions or {}).get(m)) for m in months]
    starts = [s["effective_start"] for s in snapshots]
    times = [timestamp(s["decision_timestamp"]) for s in snapshots]
    if starts != sorted(set(starts)) or times != sorted(set(times)):
        raise ValueError("delayed reconstitutions must retain strictly increasing effective starts and decisions")
    changes, previous = [], set()
    for i, snapshot in enumerate(snapshots):
        snapshot["effective_end"] = snapshot["scheduled_expiry"]
        if i + 1 < len(snapshots):
            # An explicitly delayed next decision may legitimately retain the
            # prior list, but an absent monthly selection creates a coverage gap.
            a = date.fromisoformat(snapshot["selection_month"] + "-01")
            expected_month = ((a.replace(day=28) + timedelta(days=4)).replace(day=1)).strftime("%Y-%m")
            if snapshots[i+1]["selection_month"] == expected_month:
                snapshot["effective_end"] = snapshots[i+1]["effective_start"]
        current = {r["security_id"] for r in snapshot["members"]}
        previous_month = snapshots[i-1]["selection_month"] if i else None
        interval = ((int(snapshot["selection_month"][:4])-int(previous_month[:4]))*12 +
                    int(snapshot["selection_month"][5:])-int(previous_month[5:])) if previous_month else None
        changes.append({"previous_selection_date": snapshots[i-1]["selection_date"] if i else None,
                        "comparison_interval_months": interval, "consecutive_months": interval == 1,
                        "selection_date": snapshot["selection_date"], "effective_start": snapshot["effective_start"],
                        "entrants": sorted(current-previous), "exits": sorted(previous-current), "persisting": sorted(current & previous),
                        "turnover_fraction": str(len(current-previous)/len(current)) if current else None})
        previous = current
    manifest = {"schema_version": "historical_universe_v1", "self_contained": False,
                "dependencies": {"security_master": master.content_sha256, "research_panel": panel.content_sha256},
                "universe_definition_sha256": digest(encode(definition)),
                "availability_interpretation": definition["unknown_knowledge_policy"],
                "last_snapshot_end": "EXPIRES_AT_NEXT_SCHEDULED_RECONSTITUTION; gaps are unavailable",
                "execution_admission": "NOT_GRANTED", "candidate_coverage": master.manifest["source"].get("coverage_evidence", "UNKNOWN")}
    quality = {"master": master.quality, "monthly": [{"selection_date": s["selection_date"],
                "pit_quality": s["pit_quality"], **s["summary"]} for s in snapshots],
                "price_panel_quality_sha256": panel.hashes["files"]["quality_report.json"],
                "historical_validity": "Synthetic fixtures and reconstructed vintages do not establish real survivorship-free coverage"}
    return {"universe_manifest.json": manifest, "universe_definition.json": definition,
            "universe_membership_snapshots.json": snapshots, "universe_changes.json": changes,
            "quality_report.json": quality}


def build_universe(master_path, panel_path, definition, months, output, *, decisions=None):
    master, panel = SecurityMaster(master_path), ResearchPanel(panel_path)
    records = _universe_records(master, panel, definition, months, decisions=decisions)
    return write_bundle(Path(output), {name: encode(record) for name, record in records.items()})


class HistoricalUniverse:
    def __init__(self, path, *, master, panel):
        files, hashes = read_bundle(Path(path))
        self.content_sha256 = hashes["bundle_sha256"]
        self.manifest = json.loads(files["universe_manifest.json"])
        self.master, self.panel = SecurityMaster(master), ResearchPanel(panel)
        if self.manifest["schema_version"] != "historical_universe_v1" or self.manifest["dependencies"] != {
                "security_master": self.master.content_sha256, "research_panel": self.panel.content_sha256}:
            raise ValueError("universe dependency hash mismatch")
        self.definition = json.loads(files["universe_definition.json"])
        validate_definition(self.definition)
        if digest(encode(self.definition)) != self.manifest["universe_definition_sha256"]:
            raise ValueError("universe definition hash mismatch")
        self.snapshots = json.loads(files["universe_membership_snapshots.json"])
        self.changes = json.loads(files["universe_changes.json"])
        self.quality = json.loads(files["quality_report.json"])
        # Months and decision clocks are the v1 run inputs. Every other field,
        # including derived dates, candidate evidence and aggregate QA, must be
        # reproduced from the declared immutable master, panel and definition.
        # Do this once at load; members_as_of only reads the validated inventory.
        months = [s["selection_month"] for s in self.snapshots]
        decisions = {s["selection_month"]: s["decision_timestamp"] for s in self.snapshots}
        expected = _universe_records(self.master, self.panel, self.definition, months, decisions=decisions)
        for name, record in expected.items():
            # Canonical bytes also distinguish JSON booleans from integers;
            # Python equality alone would accept rank=True in place of rank=1.
            if encode(json.loads(files[name])) != encode(record):
                raise ValueError(f"universe semantic result mismatch: {name}")

    def members_as_of(self, effective_date, *, decision_timestamp):
        day(effective_date)
        if effective_date > timestamp(decision_timestamp).astimezone(ZoneInfo("America/New_York")).date().isoformat():
            raise ValueError("membership query date follows decision date")
        if not self.panel.calendar["start"] <= effective_date <= self.panel.calendar["end"]:
            return {"status": "UNAVAILABLE", "members": [], "reason": "OUTSIDE_FROZEN_CALENDAR"}
        eligible = [s for s in self.snapshots if s["effective_start"] <= effective_date and
                    (s["effective_end"] is None or effective_date < s["effective_end"]) and
                    timestamp(s["decision_timestamp"]) < timestamp(decision_timestamp)]
        if not eligible:
            return {"status": "UNAVAILABLE", "members": [], "reason": "NO_EFFECTIVE_KNOWN_RECONSTITUTION"}
        snapshot = eligible[-1]
        return {"status": "AVAILABLE", "selection_date": snapshot["selection_date"],
                "effective_start": snapshot["effective_start"], "effective_end": snapshot["effective_end"],
                "pit_quality": snapshot["pit_quality"], "members": snapshot["members"],
                "lifecycle_diagnostics": {m["security_id"]: self.master.lifecycle_as_of(m["security_id"], decision_timestamp) for m in snapshot["members"]},
                "position_policy": "Membership changes never create fills or remove existing holdings"}
