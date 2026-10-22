"""Immutable composition; research_dataset_v1 and execution admission stay intact."""

from copy import deepcopy
import platform
import json
from pathlib import Path

from .alignment import ALIGNMENT_VERSION, align_event, event_schedule
from .diagnostics import diagnostics
from .model import EVENT_SCHEMA, EventDataset
from ..history.dataset import ResearchDataset
from ..ingestion.storage import digest, encode, read_bundle, write_bundle


def _embed(files, prefix, members, hashes):
    names = {name: prefix + name for name in members}
    files.update({names[name]: data for name, data in members.items()})
    return {"bundle_sha256": hashes["bundle_sha256"], "hashes": hashes, "members": names}


def _extract(files, reference):
    original = {name: files[frozen] for name, frozen in reference["members"].items()}
    actual = {name: digest(data) for name, data in sorted(original.items())}
    hashes = reference["hashes"]
    if (hashes["schema_version"] != "artifact_hashes_v1" or hashes["algorithm"] != "sha256" or
            actual != hashes["files"] or digest(encode(actual)) != hashes["bundle_sha256"] or
            hashes["bundle_sha256"] != reference["bundle_sha256"]):
        raise ValueError("embedded bundle lineage mismatch")
    return original, hashes


def freeze_study(price_path, event_path, symbol, output):
    if Path(output).exists():
        raise FileExistsError(output)
    price_files, price_hashes = read_bundle(Path(price_path))
    event_files, event_hashes = read_bundle(Path(event_path))
    prices, events = ResearchDataset(price_files, price_hashes), EventDataset(event_files, event_hashes)
    manifest = prices.manifest
    if set(manifest["securities"]) != {symbol}:
        raise ValueError("v1 composes one explicitly reviewed security")
    if any(e["security_id"] != manifest["securities"][symbol]["security"]["security_id"] for e in events.events):
        raise ValueError("event/price identity mismatch")
    calendar = event_schedule(events.events, manifest["start"], manifest["end"])
    aligned = [align_event(e, calendar) for e in events.events]
    report = diagnostics(prices, symbol, events, aligned, calendar)
    files = {"event_alignment.json": encode({"schema_version": ALIGNMENT_VERSION, "events": aligned}),
             "calendar.json": encode(calendar), "diagnostics.json": encode(report)}
    price_ref = _embed(files, "prices-", price_files, price_hashes)
    event_ref = _embed(files, "events-", event_files, event_hashes)
    package = Path(__file__).resolve().parent
    combined = {"schema_version": "event_aware_research_v1", "symbol": symbol,
                "security_id": manifest["securities"][symbol]["security"]["security_id"],
                "prices": price_ref, "events": event_ref, "event_schema": EVENT_SCHEMA,
                "alignment_version": ALIGNMENT_VERSION, "calendar_sha256": digest(files["calendar.json"]),
                "alignment_sha256": digest(files["event_alignment.json"]),
                "diagnostics_sha256": digest(files["diagnostics.json"]),
                "price_quality_sha256": price_hashes["files"][manifest["securities"][symbol]["quality_file"]],
                "event_quality_sha256": event_hashes["files"]["event_quality.json"],
                "source_references_sha256": event_hashes["files"]["event_sources.json"],
                "implementation_sha256": {name: digest((package / name).read_bytes()) for name in
                                          ("model.py", "alignment.py", "diagnostics.py", "dataset.py")},
                "software": {"equity_research": "0.1.0", "event_schema": EVENT_SCHEMA,
                             "calendar": manifest["calendar"], "shared": manifest["shared_dependency"],
                             "python": platform.python_version()},
                "purpose": "retrospective_research_with_evidence_backed_as_known_subset",
                "point_in_time_archive_completeness": "UNKNOWN", "execution_admission": "UNCHANGED_NOT_GRANTED"}
    files["combined_provenance.json"] = encode(combined)
    return write_bundle(Path(output), files)



class EventStudy:
    def __init__(self, files, hashes):
        self._manifest = json.loads(files["combined_provenance.json"])
        self._hashes = hashes
        m = self._manifest
        if (m["schema_version"] != "event_aware_research_v1" or m["event_schema"] != EVENT_SCHEMA or
                m["alignment_version"] != ALIGNMENT_VERSION):
            raise ValueError("unsupported study schema")
        self.prices = ResearchDataset(*_extract(files, m["prices"]))
        self.event_dataset = EventDataset(*_extract(files, m["events"]))
        if (set(self.prices.manifest["securities"]) != {m["symbol"]} or
                self.prices.manifest["securities"][m["symbol"]]["security"]["security_id"] != m["security_id"] or
                any(e["security_id"] != m["security_id"] for e in self.event_dataset.events)):
            raise ValueError("combined identity mismatch")
        for filename, key in (("calendar.json", "calendar_sha256"), ("event_alignment.json", "alignment_sha256"),
                              ("diagnostics.json", "diagnostics_sha256")):
            if digest(files[filename]) != m[key]:
                raise ValueError("composed artifact hash mismatch")
        self._calendar = json.loads(files["calendar.json"])
        schedule_core = {k: v for k, v in self._calendar.items() if k != "schedule_sha256"}
        if (digest(encode(schedule_core)) != self._calendar["schedule_sha256"] or
                self._calendar["calendar"] != "XNYS" or self._calendar["version"] != "4.13.1"):
            raise ValueError("invalid frozen event calendar")
        self._alignment = json.loads(files["event_alignment.json"])
        if self._alignment != {"schema_version": ALIGNMENT_VERSION,
                               "events": [align_event(e, self._calendar) for e in self.event_dataset.events]}:
            raise ValueError("frozen alignment differs from evidence/calendar")
        self._diagnostics = json.loads(files["diagnostics.json"])
        symbol_entry = self.prices.manifest["securities"][m["symbol"]]
        if (m["price_quality_sha256"] != m["prices"]["hashes"]["files"][symbol_entry["quality_file"]] or
                m["event_quality_sha256"] != m["events"]["hashes"]["files"]["event_quality.json"] or
                m["source_references_sha256"] != m["events"]["hashes"]["files"]["event_sources.json"]):
            raise ValueError("quality/source provenance mismatch")

    @property
    def content_sha256(self):
        return self._hashes["bundle_sha256"]

    @property
    def manifest(self):
        return deepcopy(self._manifest)

    @property
    def retrospective(self):
        return {"view": "RETROSPECTIVE", "events": self.event_dataset.events,
                "alignment": deepcopy(self._alignment), "quality": self.event_dataset.quality}

    @property
    def diagnostics(self):
        return deepcopy(self._diagnostics)

    def as_known(self, cutoff):
        # Deliberately excludes retrospective alignments and price outcomes.
        return self.event_dataset.as_known(cutoff)

    def bars(self):
        return self.prices.bars(self._manifest["symbol"])


def load_event_study(path):
    """Self-contained standard-library reader; never imports a provider or connects."""
    return EventStudy(*read_bundle(Path(path)))
