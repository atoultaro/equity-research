"""Immutable, bounded-batch daily panels partitioned by permanent ID and year.

Only this module's I/O requires the history extra (PyArrow). No provider SDKs.
"""

from collections import Counter, defaultdict
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
import tempfile

from ..ingestion.storage import digest, encode
from ..models import number, timestamp
from .master import day, known, source_quality
from .storage import Writer, verify

BASES = {"RAW_TRADED", "SPLIT_ADJUSTED", "DIVIDEND_ADJUSTED", "TOTAL_RETURN", "VENDOR_UNVERIFIED"}
VOLUME_BASES = {"RAW_SHARES", "SPLIT_ADJUSTED_SHARES", "VENDOR_UNVERIFIED"}
MAX_BATCH_ROWS = 25000
MAX_BATCH_BYTES = 32 * 1024 * 1024


def validate_bar(row, calendar):
    if not row.get("security_id") or row["session_date"] not in calendar:
        raise ValueError("unknown security/off-calendar observation")
    day(row["session_date"])
    values = {k: number(row[k]) for k in ("open", "high", "low", "close")}
    if (min(values.values()) <= 0 or values["high"] < max(values.values()) or values["low"] > min(values.values())):
        raise ValueError("invalid OHLC")
    if row["volume"] is not None:
        volume = number(row["volume"])
        if volume < 0 or volume != volume.to_integral_value():
            raise ValueError("invalid volume")
    if row["price_basis"] not in BASES or row["volume_basis"] not in VOLUME_BASES or row["currency"] != "USD":
        raise ValueError("unknown price/volume basis or currency")
    if type(row["revision"]) is not int or row["revision"] < 1:
        raise ValueError("invalid observation revision")
    if row["availability_status"] not in {"DOCUMENTED", "RECONSTRUCTED", "UNKNOWN"}:
        raise ValueError("invalid availability status")
    if row["quality_status"] not in {"VALID", "MISSING_VOLUME", "UNVERIFIED"}:
        raise ValueError("invalid quality status")
    if (row["available_at"] is None) != (row["availability_status"] == "UNKNOWN"):
        raise ValueError("unknown availability must retain a null timestamp")
    if row["available_at"] is not None and timestamp(row["available_at"]) < timestamp(calendar[row["session_date"]]["closes_at"]):
        raise ValueError("availability precedes session completion")
    if row["known_at"] is not None:
        timestamp(row["known_at"])
    if not row.get("original_observation_reference"):
        raise ValueError("source observation locator required")


def freeze_panel(captures, calendar, output, *, base=None):
    """Resume into a NEW snapshot, copying sealed accepted bytes unchanged.

    Each capture <=25k rows/32MiB. Same (ID, session, revision) is never replaced.
    A changed observation requires a later, explicitly published revision. Failed
    batches carry failure codes and can be complemented in a later snapshot.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    sessions = {s["session_date"]: s for s in calendar["sessions"]}
    if len(sessions) != len(calendar["sessions"]) or list(sessions) != sorted(sessions):
        raise ValueError("unique ascending frozen calendar required")
    unsigned = {k: v for k, v in calendar.items() if k != "schedule_sha256"}
    if digest(encode(unsigned)) != calendar["schedule_sha256"]:
        raise ValueError("calendar source hash mismatch")
    previous = ResearchPanel(base) if base else None
    if previous and previous.calendar != calendar:
        raise ValueError("incremental panel requires identical frozen calendar")
    writer = Writer(output)
    index = defaultdict(list)
    sources = []
    if previous:
        for name in previous.hashes["files"]:
            if name.startswith(("part-", "source-")):
                writer.copy(name, previous.path / name)
        index.update({sid: list(parts) for sid, parts in previous.index.items()})
        sources.extend(previous.manifest["sources"])
    source_hashes = {s["source_snapshot_sha256"] for s in sources}
    for capture in captures:
        path = Path(capture)
        if path.stat().st_size > MAX_BATCH_BYTES:
            raise ValueError("capture exceeds bounded batch bytes")
        raw = path.read_bytes()
        sha = digest(raw)
        if sha in source_hashes:
            raise ValueError("capture already accepted; resume with only new batches")
        record = json.loads(raw)
        if record.get("schema_version") != "daily_panel_capture_v1" or len(record["rows"]) > MAX_BATCH_ROWS:
            raise ValueError("unsupported or oversized daily batch")
        source = record["source"]
        if (source.get("origin") not in {"SYNTHETIC", "RECORDED"} or not source.get("provider")
                or source.get("status") not in {"SUCCESS", "PARTIAL", "FAILED"}):
            raise ValueError("source origin/provider/acquisition status required")
        if source["status"] != "SUCCESS" and not source.get("failure_codes"):
            raise ValueError("partial acquisition must record failure codes")
        if source["status"] == "FAILED" and record["rows"]:
            raise ValueError("failed capture cannot contain accepted observations")
        if not record["rows"] and source["status"] == "SUCCESS":
            raise ValueError("empty successful acquisition")
        groups = defaultdict(list)
        for row in record["rows"]:
            validate_bar(row, sessions)
            normalized = {**row, "source_snapshot_sha256": sha, "provider": source["provider"]}
            groups[(row["security_id"], row["session_date"][:4])].append(normalized)
        for (sid, year), rows in sorted(groups.items()):
            rows.sort(key=lambda r: (r["session_date"], r["revision"]))
            name = f"part-{digest(sid.encode())[:20]}-{year}-{sha}.parquet"
            # JSON preserves exact decimal text, nulls and native metadata; selected
            # columns enable projection/filtering without lossy float conversion.
            table = pa.table({"security_id": [sid]*len(rows), "session_date": [r["session_date"] for r in rows],
                              "revision": [r["revision"] for r in rows],
                              "observation_json": [encode(r).decode() for r in rows]})
            with tempfile.TemporaryDirectory() as temporary:
                p = Path(temporary) / "partition.parquet"
                pq.write_table(table, p, compression="zstd", version="2.6")
                writer.copy(name, p)
            index[sid].append(name)
        writer.put(f"source-{sha}.json", raw)
        sources.append({**source, "source_snapshot_sha256": sha, "quality": source_quality(source)})
        source_hashes.add(sha)
    writer.put("calendar.json", encode(calendar))
    manifest = {"schema_version": "research_panel_v1", "self_contained": True,
                "parent_panel_sha256": previous.content_sha256 if previous else None,
                "calendar_sha256": calendar["schedule_sha256"], "sources": sources,
                "partitions": {sid: sorted(parts) for sid, parts in sorted(index.items())}}
    writer.put("research_panel_manifest.json", encode(manifest))
    # Audit one security at a time; retained prices are never held panel-wide.
    quality = {}
    for sid, parts in sorted(index.items()):
        rows = _read_parts(writer.path, parts)
        versions = defaultdict(list)
        for row in rows:
            versions[row["session_date"]].append(row)
        for group in versions.values():
            revisions = [r["revision"] for r in group]
            if len(revisions) != len(set(revisions)):
                raise ValueError("duplicate source observation (security/session/revision)")
            ordered = sorted(group, key=lambda r: r["revision"])
            if len(group) > 1:
                if any(r["known_at"] is None for r in group):
                    raise ValueError("unknown publication time for revised observation")
                times = [timestamp(r["known_at"]) for r in ordered]
                if times != sorted(set(times)):
                    raise ValueError("revision knowledge times must strictly increase")
        days = sorted(versions)
        expected = [d for d in sessions if days[0] <= d <= days[-1]] if days else []
        latest = [max(versions[d], key=lambda r: r["revision"]) for d in days]
        discontinuities = [b["session_date"] for a, b in zip(latest, latest[1:]) if a["volume"] is not None
                           and b["volume"] is not None and number(a["volume"]) > 0 and
                           (number(b["volume"]) / number(a["volume"]) > 10 or number(b["volume"]) / number(a["volume"]) < Decimal("0.1"))]
        missing = [d for d in expected if d not in versions]
        quality[sid] = {"observations": len(rows), "sessions": len(days), "first_session": days[0], "last_session": days[-1],
                        "missing_sessions_within_materialized_span": missing[:50],
                        "missing_session_count": len(missing), "missing_session_examples_truncated": len(missing) > 50,
                        "missing_volume": sum(r["volume"] is None for r in latest),
                        "unknown_availability": sum(r["available_at"] is None or r["known_at"] is None for r in latest),
                        "price_bases": sorted({r["price_basis"] for r in rows}),
                        "volume_bases": sorted({r["volume_basis"] for r in rows}),
                        "volume_discontinuities": discontinuities, "revised_sessions": sum(len(v) > 1 for v in versions.values())}
    writer.put("quality_report.json", encode({"securities": quality,
                "security_count": len(index), "row_count": sum(q["observations"] for q in quality.values()),
                "acquisition_failures": [s for s in sources if s["status"] != "SUCCESS"],
                "corporate_actions": "Evidence in separate security master; no automatic adjustment or terminal fills"}))
    return writer.finish()


def _read_parts(path, parts):
    import pyarrow.parquet as pq
    rows = []
    for part in parts:
        rows.extend(json.loads(value) for value in pq.read_table(Path(path) / part, columns=["observation_json"])["observation_json"].to_pylist())
    return sorted(rows, key=lambda r: (r["session_date"], r["revision"]))


class ResearchPanel:
    def __init__(self, path):
        self.path = Path(path)
        self.hashes = verify(path)  # Stream all dependencies; load partitions lazily.
        self.content_sha256 = self.hashes["bundle_sha256"]
        self.manifest = json.loads((self.path / "research_panel_manifest.json").read_bytes())
        if self.manifest["schema_version"] != "research_panel_v1" or not self.manifest["self_contained"]:
            raise ValueError("unsupported research panel")
        self.calendar = json.loads((self.path / "calendar.json").read_bytes())
        unsigned = {k: v for k, v in self.calendar.items() if k != "schedule_sha256"}
        if (digest(encode(unsigned)) != self.calendar["schedule_sha256"] or
                self.manifest["calendar_sha256"] != self.calendar["schedule_sha256"]):
            raise ValueError("calendar dependency hash mismatch")
        self.sessions = {s["session_date"]: s for s in self.calendar["sessions"]}
        self.index = self.manifest["partitions"]
        expected_parts = {p for parts in self.index.values() for p in parts}
        if expected_parts != {name for name in self.hashes["files"] if name.startswith("part-")}:
            raise ValueError("partition index mismatch")
        for source in self.manifest["sources"]:
            sha = source["source_snapshot_sha256"]
            if self.hashes["files"].get(f"source-{sha}.json") != sha:
                raise ValueError("source hash mismatch")
        self.quality = json.loads((self.path / "quality_report.json").read_bytes())

    def observations(self, security_id, *, start=None, end=None):
        parts = [p for p in self.index.get(security_id, [])
                 if (start is None or p.split("-")[2] >= start[:4]) and (end is None or p.split("-")[2] <= end[:4])]
        return [r for r in _read_parts(self.path, parts)
                if (start is None or r["session_date"] >= start) and (end is None or r["session_date"] <= end)]

    def rows_as_of(self, security_id, decision_timestamp, *, through=None, start=None, reconstruct_unknown=False):
        cutoff = timestamp(decision_timestamp)
        versions = {}
        for row in self.observations(security_id, start=start, end=through):
            if through is not None and row["session_date"] > through:
                continue
            if not known(row, decision_timestamp, reconstruct_unknown):
                continue
            available = row["available_at"]
            if available is None:
                if not reconstruct_unknown:
                    continue
                available = (timestamp(self.sessions[row["session_date"]]["closes_at"]) + timedelta(minutes=60)).isoformat()
            if timestamp(available) >= cutoff:
                continue
            old = versions.get(row["session_date"])
            if old is None or old["revision"] < row["revision"]:
                versions[row["session_date"]] = row
        return [versions[d] for d in sorted(versions)]
