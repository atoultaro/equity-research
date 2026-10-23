"""Bitemporal identity assertions and lifecycle evidence, keyed by stable security ID."""

from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path

from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..models import timestamp, number

LEVELS = {"PIT_VERIFIED", "PIT_RECONSTRUCTED", "PIT_UNVERIFIED"}
REQUIRED = {"security_id", "issuer_id", "share_class_id", "symbol", "exchange", "security_type",
            "currency", "trading_status", "listing_start", "listing_end", "provider_security_id"}


def day(value):
    return date.fromisoformat(value).isoformat()


def known(record, cutoff, reconstructed=False):
    value = record.get("known_at")
    return (timestamp(value) < timestamp(cutoff)) if value is not None else reconstructed


def source_quality(source):
    """Timestamps alone never establish independently verified historical vintages."""
    required = ("availability_evidence", "identity_evidence", "vintage_evidence", "coverage_evidence")
    if (source.get("origin") != "SYNTHETIC" and source.get("reviewed_pit_attestation") is True
            and all(source.get(k) for k in required)):
        return "PIT_VERIFIED"
    return "PIT_RECONSTRUCTED" if source.get("coverage_evidence") else "PIT_UNVERIFIED"


def import_master(capture, output):
    raw = Path(capture).read_bytes()
    record = json.loads(raw)
    if record.get("schema_version") != "security_master_capture_v1":
        raise ValueError("unsupported master capture")
    source = record["source"]
    if not source.get("provider") or source.get("origin") not in {"SYNTHETIC", "RECORDED"}:
        raise ValueError("explicit source and origin required")
    facts, events = record["records"], record["lifecycle_events"]
    seen = set()
    for fact in facts:
        if not REQUIRED <= fact.keys() or not fact.get("security_id"):
            raise ValueError("incomplete security assertion")
        key = (fact["fact_id"], fact["revision"])
        if key in seen or type(fact["revision"]) is not int or fact["revision"] < 1:
            raise ValueError("duplicate/invalid fact revision")
        seen.add(key)
        day(fact["effective_from"])
        if fact["listing_start"] is not None:
            day(fact["listing_start"])
        for field in ("effective_to", "listing_end"):
            if fact.get(field) is not None:
                day(fact[field])
        if fact.get("effective_to") is not None and fact["effective_to"] <= fact["effective_from"]:
            raise ValueError("empty effective interval")
        if fact["known_at"] is not None:
            timestamp(fact["known_at"])
        if fact["identity_confidence"] not in {"VERIFIED", "ASSERTED", "WEAK"}:
            raise ValueError("identity evidence/confidence required")
    groups = defaultdict(list)
    for fact in facts:
        groups[fact["fact_id"]].append(fact)
    for group in groups.values():
        ordered = sorted(group, key=lambda f: f["revision"])
        if len({f["security_id"] for f in ordered}) != 1:
            raise ValueError("revision cannot change security identity")
        times = [timestamp(f["known_at"]) for f in ordered if f["known_at"] is not None]
        if times != sorted(set(times)):
            raise ValueError("revision publication must increase")
        if len(ordered) > 1 and any(f["known_at"] is None for f in ordered):
            raise ValueError("unknown-time corrections cannot be ordered safely")
    ids = {f["security_id"] for f in facts}
    eventids = set()
    for event in events:
        if event["event_id"] in eventids or event["security_id"] not in ids:
            raise ValueError("duplicate lifecycle event or unknown security")
        eventids.add(event["event_id"])
        if event.get("effective_date") is not None:
            day(event["effective_date"])
        if event["known_at"] is not None:
            timestamp(event["known_at"])
        if not event.get("evidence_reference"):
            raise ValueError("lifecycle source evidence required")
        for field in ("terminal_value", "cash_consideration", "amount", "ratio"):
            if event.get(field) is not None and number(event[field]) < 0:
                raise ValueError("negative lifecycle amount/ratio")
        # Terminal value and cash consideration remain independent source assertions;
        # neither creates a bar, execution, inferred recovery or terminal return.
    sha = digest(raw)
    normalized = [{**f, "source_snapshot_sha256": sha, "source_provider": source["provider"],
                   "original_observation_reference": f"records/{i}"} for i, f in enumerate(facts)]
    lifecycle = [{**e, "source_snapshot_sha256": sha, "original_observation_reference": f"lifecycle_events/{i}"}
                 for i, e in enumerate(events)]
    report = audit(normalized, lifecycle, source)
    manifest = {"schema_version": "security_master_v1", "self_contained": True,
                "source_snapshot_sha256": sha, "source": source, "quality": source_quality(source)}
    return write_bundle(Path(output), {"security_master_manifest.json": encode(manifest),
                "security_master_records.json": encode(normalized), "security_lifecycle_events.json": encode(lifecycle),
                "quality_report.json": encode(report), "source_capture.json": raw})


def audit(facts, events, source):
    symbols, issuers, exchanges = defaultdict(set), defaultdict(set), defaultdict(set)
    for f in facts:
        if f["symbol"] is not None: symbols[f["symbol"]].add(f["security_id"])
        if f["issuer_id"] is not None and f["share_class_id"] is not None: issuers[f["issuer_id"]].add(f["share_class_id"])
        if f["exchange"] is not None: exchanges[f["security_id"]].add(f["exchange"])
    terminal = [e for e in events if e["event_type"] in {"DELISTING", "BANKRUPTCY", "MERGER"}]
    return {"security_count": len({f["security_id"] for f in facts}), "assertion_count": len(facts),
            "listing_dates": dict(sorted(Counter(start or "UNKNOWN" for _, start in {(f["security_id"], f["listing_start"]) for f in facts}).items())),
            "delisting_dates": dict(sorted(Counter(e.get("effective_date") or "UNKNOWN" for e in terminal).items())),
            "reused_tickers": {k: sorted(v) for k, v in sorted(symbols.items()) if len(v) > 1},
            "multiple_share_classes": {k: sorted(v) for k, v in sorted(issuers.items()) if len(v) > 1},
            "exchange_changes": {k: sorted(v) for k, v in sorted(exchanges.items()) if len(v) > 1},
            "weak_identity_assertions": sum(f["identity_confidence"] == "WEAK" for f in facts),
            "incomplete_identity_assertions": sum(any(f[k] is None for k in REQUIRED - {"listing_end"}) or not f["identity_evidence"] for f in facts),
            "unknown_knowledge_assertions": sum(f["known_at"] is None for f in facts),
            "lifecycle_event_types": dict(sorted(Counter(e["event_type"] for e in events).items())),
            "terminal_evidence_count": sum(e.get("terminal_value") is not None for e in terminal),
            "unresolved_terminal_events": [e["event_id"] for e in terminal if e.get("terminal_value") is None],
            "corporate_action_completeness": source.get("corporate_action_completeness", "UNKNOWN"),
            "survivorship_coverage": source.get("coverage_evidence", "UNKNOWN"), "pit_quality": source_quality(source)}


class SecurityMaster:
    def __init__(self, path):
        files, hashes = read_bundle(Path(path))
        self.path, self.content_sha256 = Path(path), hashes["bundle_sha256"]
        self.manifest = json.loads(files["security_master_manifest.json"])
        if self.manifest["schema_version"] != "security_master_v1":
            raise ValueError("unsupported security master")
        if digest(files["source_capture.json"]) != self.manifest["source_snapshot_sha256"]:
            raise ValueError("source hash mismatch")
        self.records = json.loads(files["security_master_records.json"])
        self.events = json.loads(files["security_lifecycle_events.json"])
        self.quality = json.loads(files["quality_report.json"])
        self.by_id = defaultdict(list)
        for record in self.records:
            self.by_id[record["security_id"]].append(record)

    def as_of(self, security_id, effective_date, decision_timestamp, *, reconstruct_unknown=False):
        day(effective_date); timestamp(decision_timestamp)
        versions = {}
        for f in self.by_id.get(security_id, []):
            if known(f, decision_timestamp, reconstruct_unknown):
                if f["fact_id"] not in versions or versions[f["fact_id"]]["revision"] < f["revision"]:
                    versions[f["fact_id"]] = f
        matches = [f for f in versions.values() if f["effective_from"] <= effective_date and
                   (f.get("effective_to") is None or effective_date < f["effective_to"])]
        if len(matches) > 1:
            raise ValueError(f"ambiguous effective identity: {security_id}")
        return matches[0] if matches else None

    def resolve_symbol(self, symbol, effective_date, decision_timestamp, **kwargs):
        matches = [f for sid in sorted(self.by_id) if
                   (f := self.as_of(sid, effective_date, decision_timestamp, **kwargs)) is not None and f["symbol"] == symbol
                   and f["listing_start"] is not None and f["listing_start"] <= effective_date and (f["listing_end"] is None or effective_date <= f["listing_end"])]
        if len(matches) != 1:
            raise ValueError("ticker resolution is missing or ambiguous; use stable security ID")
        return matches[0]

    def lifecycle_as_of(self, security_id, decision_timestamp):
        return [e for e in self.events if e["security_id"] == security_id and known(e, decision_timestamp)]
