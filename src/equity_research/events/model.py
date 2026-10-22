"""Versioned evidence assertions. Capture time never implies historical knowledge."""

from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
from urllib.parse import urlparse

from ..ingestion.storage import digest, encode, read_bundle, write_bundle

EVENT_SCHEMA = "corporate_events_v1"
RELATIONS = {"BEFORE_OPEN", "DURING_SESSION", "AFTER_CLOSE", "UNKNOWN"}
PRECISIONS = {"DATE", "MINUTE", "SECOND", "UNKNOWN"}
REQUIRED = {"event_id", "revision", "security_id", "event_type", "event_date", "announced_at",
            "announced_time_precision", "announced_session_relation", "relation_evidence_status",
            "effective_date", "fiscal_period", "payload", "currency", "source_ids", "captured_at",
            "evidence_status", "unresolved_fields"}


def timestamp(value):
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("timestamps require an explicit timezone offset")
    return result


def day(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError("dates require canonical ISO dates")
    return value


def claim(event):
    """Source assertions bind values, not capture times or other source references."""
    return {k: deepcopy(v) for k, v in event.items() if k not in {"source_ids", "captured_at"}}


def _positive(value):
    number = Decimal(value)
    if not number.is_finite() or number <= 0:
        raise ValueError("expected a finite positive decimal")


def validate(events, sources):
    if not isinstance(events, list) or not isinstance(sources, list):
        raise ValueError("events and sources must be arrays")
    by_source, duplicate_sources = {}, []
    seen_documents = set()
    for source in sources:
        sid = source["source_id"]
        if not isinstance(sid, str) or not sid or sid in by_source:
            raise ValueError("duplicate/invalid source_id")
        by_source[sid] = source
        if urlparse(source["url"]).scheme != "https" or not source["source_document_id"]:
            raise ValueError("source needs HTTPS URL and document identity")
        captured = timestamp(source["captured_at"])
        if source["publication_precision"] not in PRECISIONS:
            raise ValueError("invalid source publication precision")
        if source["published_at"] is not None:
            if source["publication_precision"] not in {"MINUTE", "SECOND"}:
                raise ValueError("date-only publications must keep timestamp null")
            if timestamp(source["published_at"]) > captured:
                raise ValueError("publication after capture")
        if source["publication_evidence_status"] not in {"VERIFIED", "UNKNOWN"}:
            raise ValueError("invalid publication evidence status")
        if not source["evidence_note"] or not isinstance(source["assertions"], dict):
            raise ValueError("source evidence note and assertions required")
        document = (source["url"], source["source_document_id"])
        if document in seen_documents:
            duplicate_sources.append(sid)
        seen_documents.add(document)
    identities, semantic, duplicate_events = {}, {}, []
    for event in events:
        if not REQUIRED <= event.keys():
            raise ValueError("missing event fields")
        if not all(isinstance(event[k], str) and event[k] for k in ("event_id", "security_id")):
            raise ValueError("invalid event identity")
        if type(event["revision"]) is not int or event["revision"] < 1:
            raise ValueError("invalid event revision")
        key = revision_key(event)
        if key in identities:
            raise ValueError("duplicate event revision identity; retain alternatives as separate revisions")
        identities[key] = event
        day(event["event_date"])
        if event["effective_date"] is not None:
            day(event["effective_date"])
        captured = timestamp(event["captured_at"])
        precision = event["announced_time_precision"]
        if precision not in PRECISIONS or event["announced_session_relation"] not in RELATIONS:
            raise ValueError("invalid announcement precision/relation")
        if event["announced_at"] is None:
            if precision in {"MINUTE", "SECOND"}:
                raise ValueError("timestamp required for minute/second precision")
        else:
            from zoneinfo import ZoneInfo
            announced = timestamp(event["announced_at"])
            if precision not in {"MINUTE", "SECOND"} or announced > captured:
                raise ValueError("invalid announcement timestamp")
            if announced.astimezone(ZoneInfo("America/New_York")).date().isoformat() != event["event_date"]:
                raise ValueError("announcement date must be its New York date, not fiscal/effective date")
        if event["relation_evidence_status"] not in {"VERIFIED", "UNKNOWN"}:
            raise ValueError("invalid relation evidence")
        if event["evidence_status"] not in {"VERIFIED", "PARTIAL", "UNVERIFIED"}:
            raise ValueError("invalid event evidence status")
        if not isinstance(event["unresolved_fields"], list) or not isinstance(event["payload"], dict):
            raise ValueError("invalid typed event payload")
        if event["currency"] != "USD":
            raise ValueError("v1 supports explicitly reviewed USD common stock only")
        kind, payload = event["event_type"], event["payload"]
        if kind == "EARNINGS":
            period = event["fiscal_period"]
            if not isinstance(period, dict) or period["quarter"] not in {1, 2, 3, 4}:
                raise ValueError("earnings requires fiscal year/quarter/period_end")
            if type(period["year"]) is not int:
                raise ValueError("invalid fiscal year")
            day(period["period_end"])
            if period["period_end"] > event["event_date"]:
                raise ValueError("fiscal period ends after release")
            for name in ("eps_diluted_gaap", "revenue_usd"):
                if payload.get(name) is not None and not Decimal(payload[name]).is_finite():
                    raise ValueError("nonfinite reported value")
        elif kind == "DIVIDEND":
            _positive(payload["cash_per_share"])
            for name in ("record_date", "payment_date", "ex_date"):
                if payload[name] is not None:
                    day(payload[name])
            if payload["ex_date"] != event["effective_date"]:
                raise ValueError("dividend effective date must be ex-date, never record/payment date")
            if payload["ex_date_status"] not in {"VERIFIED", "UNKNOWN"}:
                raise ValueError("invalid ex-date evidence")
            if payload["ex_date"] is not None and payload["ex_date_status"] != "VERIFIED":
                raise ValueError("unverified ex-date must stay null")
        elif kind == "SPLIT":
            _positive(payload["new_shares"])
            _positive(payload["old_shares"])
            for name in ("record_date", "distribution_date"):
                if payload[name] is not None:
                    day(payload[name])
            if event["effective_date"] is None:
                raise ValueError("split requires sourced first new-share-basis trading date")
        else:
            raise ValueError("unsupported event type")
        if not event["source_ids"] or len(set(event["source_ids"])) != len(event["source_ids"]):
            raise ValueError("source references must be nonempty and unique")
        supported = False
        for sid in event["source_ids"]:
            source = by_source[sid]
            if timestamp(source["captured_at"]) > captured:
                raise ValueError("event capture precedes source capture")
            assertion = source["assertions"].get(key)
            if assertion is not None:
                if assertion != claim(event):
                    raise ValueError("source assertion differs from event revision")
                supported = True
        if not supported:
            raise ValueError("no source binds this event revision's complete assertion")
        signature = digest(encode({k: v for k, v in claim(event).items() if k != "revision"}))
        if signature in semantic:
            duplicate_events.append(key)
        semantic[signature] = key
    # Alternatives/corrections remain visible. v1 deliberately does not adjudicate
    # conflicting revisions or infer a historical revision sequence.
    grouped = {}
    for event in events:
        grouped.setdefault(event["event_id"], []).append(event)
    conflicts = [eid for eid, rows in grouped.items() if len({digest(encode(
        {k: v for k, v in claim(e).items() if k != "revision"})) for e in rows}) > 1]
    return {"schema_version": "event_quality_v1", "status": "REVIEW" if conflicts else "PASS_WITH_LIMITATIONS",
            "conflicting_event_ids": sorted(conflicts), "duplicate_source_ids": duplicate_sources,
            "duplicate_event_revisions": duplicate_events, "event_count": len(events),
            "unknown_announcement_times": sum(e["announced_at"] is None for e in events),
            "unverified_ex_dates": sum(e["event_type"] == "DIVIDEND" and e["effective_date"] is None for e in events),
            "point_in_time_archive_completeness": "UNKNOWN"}


def revision_key(event):
    return f"{event['event_id']}@{event['revision']}"


def freeze_events(events, sources, output):
    quality = validate(events, sources)
    return write_bundle(Path(output), {
        "events.json": encode({"schema_version": EVENT_SCHEMA, "events": events}),
        "event_sources.json": encode({"schema_version": "event_sources_v1", "sources": sources}),
        "event_quality.json": encode(quality)})


class EventDataset:
    def __init__(self, files, hashes):
        self._files, self._hashes = files, hashes
        records, sources = json.loads(files["events.json"]), json.loads(files["event_sources.json"])
        if records["schema_version"] != EVENT_SCHEMA or sources["schema_version"] != "event_sources_v1":
            raise ValueError("unsupported event/source schema")
        self._events, self._sources = records["events"], sources["sources"]
        quality = validate(self._events, self._sources)
        if quality != json.loads(files["event_quality.json"]):
            raise ValueError("event quality differs from evidence")
        self._quality = quality

    @property
    def content_sha256(self):
        return self._hashes["bundle_sha256"]

    @property
    def events(self):
        return deepcopy(self._events)

    @property
    def sources(self):
        return deepcopy(self._sources)

    @property
    def quality(self):
        return deepcopy(self._quality)

    def as_known(self, cutoff):
        """Proven public strictly before cutoff; minute stamps use end-of-minute.

        Applies to each full revision, never substitutes today's captured_at for
        publication. This is an evidence-backed subset, not a complete PIT archive.
        """
        cutoff = timestamp(cutoff)
        selected, unknown = [], []
        sources = {s["source_id"]: s for s in self._sources}
        for event in self._events:
            if (event["event_id"] in self._quality["conflicting_event_ids"] or
                    event["evidence_status"] == "UNVERIFIED"):
                unknown.append(revision_key(event))
                continue
            bounds = []
            for sid in event["source_ids"]:
                source = sources[sid]
                if (source["assertions"].get(revision_key(event)) == claim(event) and
                        source["publication_evidence_status"] == "VERIFIED" and source["published_at"] is not None):
                    upper = timestamp(source["published_at"])
                    if source["publication_precision"] == "MINUTE":
                        upper += timedelta(minutes=1)
                    bounds.append(upper)
            if not bounds:
                unknown.append(revision_key(event))
            elif min(bounds) < cutoff:
                selected.append(deepcopy(event))
        return {"view": "AS_KNOWN_EVIDENCE_SUBSET", "cutoff": cutoff.isoformat(), "events": selected,
                "knowledge_unknown": unknown, "archive_completeness": "UNKNOWN"}


def load_events(path):
    return EventDataset(*read_bundle(Path(path)))
