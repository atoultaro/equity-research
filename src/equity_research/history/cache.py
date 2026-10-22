"""Per-provider Parquet cache with atomic version pointers and immutable lineage."""

from contextlib import contextmanager
from datetime import date, timedelta
import io
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from .contracts import DailyProvider, interval, now_utc, select_securities
from .normalize import read_acquisition, reconcile
from ..ingestion.storage import digest, encode, read_bundle, write_bundle

ROW_FIELDS = ("security_id", "symbol", "provider", "provider_symbol", "session_date", "open", "high", "low",
              "close", "adj_close", "volume", "price_basis", "volume_basis", "source_snapshot_sha256")


def parquet_bytes(rows):
    import pyarrow as pa
    import pyarrow.parquet as pq
    # Numbers remain exact decimal strings. The nested locator has its own JSON
    # column so Parquet never coerces integers/decimals through a float column.
    columns = {name: [row.get(name) for row in rows] for name in ROW_FIELDS}
    columns["source_row_json"] = [encode(row["source_row"]).decode() for row in rows]
    table = pa.table(columns, schema=pa.schema([(k, pa.string()) for k in columns]))
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="zstd", version="2.6")
    return buffer.getvalue()


def parquet_rows(content):
    import pyarrow.parquet as pq
    rows = pq.read_table(io.BytesIO(content)).to_pylist()
    for row in rows:
        row["source_row"] = json.loads(row.pop("source_row_json"))
    return rows


class HistoryCache:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def entry(self, provider, security):
        return self.root / provider / digest(encode(security.provider_key(provider)))

    @contextmanager
    def lock(self, provider, security):
        entry = self.entry(provider, security)
        entry.mkdir(parents=True, exist_ok=True)
        lock = entry / ".lock"
        try:
            lock.mkdir()
        except FileExistsError:
            raise ValueError("CACHE_BUSY: another writer or stale lock; inspect before removing") from None
        try:
            yield
        finally:
            lock.rmdir()

    def load_cached_daily(self, provider, security, start, end):
        interval(start, end)
        path = self.entry(provider, security)
        if not (path / "current.json").exists():
            return {"cache_status": "MISS", "rows": [], "metadata": None}
        try:
            pointer = json.loads((path / "current.json").read_bytes())
            version = pointer["version"]
            if not isinstance(version, str) or not re.fullmatch(r"[0-9a-f]{32}", version):
                raise ValueError("unsafe cache version")
            files, hashes = read_bundle(path / "versions" / version)
            if hashes["bundle_sha256"] != pointer["bundle_sha256"]:
                raise ValueError("cache pointer hash mismatch")
            metadata = json.loads(files["metadata.json"])
            if metadata["schema_version"] != "provider_cache_v1" or metadata["version"] != version:
                raise ValueError("invalid cache schema/version")
            if metadata["security"] != security.record() or metadata["provider"] != provider:
                return {"cache_status": "IDENTITY_MISMATCH", "rows": [], "metadata": None}
            all_rows = parquet_rows(files["bars.parquet"])
            if digest(encode(all_rows)) != metadata["rows_sha256"]:
                raise ValueError("Parquet logical content mismatch")
            rows = [r for r in all_rows if start <= r["session_date"] <= end]
            quality = reconcile(rows, security, start, end)
            return {"cache_status": "HIT" if quality["status"] == "PASS" else "INCOMPLETE",
                    "rows": rows, "all_rows": all_rows, "metadata": metadata, "quality": quality}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # A read never repairs or initiates a network request. Explicit full
            # refresh can replace only the pointer; damaged evidence stays visible.
            return {"cache_status": "CORRUPT", "rows": [], "metadata": None,
                    "errors": [{"code": "CACHE_INTEGRITY_ERROR", "exception_type": type(exc).__name__}]}

    def update(self, provider, security, start, end, acquisition, *, full=False, clock=now_utc):
        if acquisition["request"]["provider"] != provider or any(
                row["provider"] != provider or row["security_id"] != security.security_id or row["symbol"] != security.symbol
                for row in acquisition["rows"]):
            raise ValueError("source provider/security differs from the selected cache identity")
        old = self.load_cached_daily(provider, security, start, end)
        if old["cache_status"] == "IDENTITY_MISMATCH":
            raise ValueError("cache security mapping differs; use a separate cache root")
        if old["cache_status"] == "CORRUPT" and not full:
            raise ValueError("cache corrupt; explicit full refresh required")
        incoming = acquisition["rows"]
        issues = list(acquisition["issues"])
        duplicates = len({r["session_date"] for r in incoming}) != len(incoming)
        req = acquisition["request"]
        calendar_quality = reconcile(incoming, security, req["start"], req["end"])
        bad_calendar = any(calendar_quality[k] for k in ("off_calendar_sessions", "outside_listing_sessions", "duplicate_sessions"))
        usable = (incoming and not duplicates and not bad_calendar and
                  not any(i["status"] == "FAIL" for i in issues) and
                  acquisition["acquisition"]["status"] in {"SUCCESS", "PARTIAL_RESPONSE"})
        qualified = acquisition["acquisition"].get("qualified_contract")
        if old["metadata"] and old["metadata"].get("qualified_contract") != qualified:
            raise ValueError("qualified contract changed across cache vintages")
        if not usable:
            return {"cache_status": "NOT_PROMOTED", "quality": calendar_quality, "issues": issues,
                    "previous_version": old["metadata"]["version"] if old["metadata"] else None}
        if old["metadata"] and old["metadata"]["basis"] != acquisition["basis"]:
            raise ValueError("basis changed across cache vintages; use a separate cache root")
        previous = {r["session_date"]: r for r in old.get("all_rows", [])}
        fresh = {r["session_date"]: r for r in incoming}
        # A fresh interval replaces that interval, including explicitly removed
        # sessions. Retaining an old missing response would conceal a coverage gap.
        survivors = {day: row for day, row in previous.items() if not req["start"] <= day <= req["end"]}
        rows = [row for _, row in sorted((survivors | fresh).items())]
        corrections = [{"session_date": day, "field": field, "before": previous[day][field], "after": fresh[day][field]}
                       for day in sorted(previous.keys() & fresh.keys())
                       for field in ("open", "high", "low", "close", "adj_close", "volume")
                       if previous[day][field] != fresh[day][field]]
        removed = sorted(day for day in previous if req["start"] <= day <= req["end"] and day not in fresh)
        sources = dict(old["metadata"]["sources"]) if old["metadata"] else {}
        sources[acquisition["snapshot_sha256"]] = acquisition["snapshot_reference"]
        version = uuid4().hex
        metadata = {"schema_version": "provider_cache_v1", "version": version, "provider": provider,
                    "security": security.record(), "basis": acquisition["basis"], "sources": sources,
                    "qualified_contract": qualified, "rows_sha256": digest(encode(rows)),
                    "created_at": clock().isoformat(), "corrections": corrections, "removed_sessions": removed,
                    "refresh_request": req, "acquisition_status": acquisition["acquisition"]["status"],
                    "previous_version": old["metadata"]["version"] if old["metadata"] else None,
                    "recovered_corrupt_cache": old["cache_status"] == "CORRUPT",
                    "excluded_incomplete_sessions": acquisition["excluded_incomplete_sessions"],
                    "events": acquisition["events"], "issues": issues,
                    "permission_reference": acquisition.get("permission_reference"),
                    "historical_availability": "unknown", "corporate_action_completeness": "unknown"}
        entry = self.entry(provider, security)
        hashes = write_bundle(entry / "versions" / version,
                              {"metadata.json": encode(metadata), "bars.parquet": parquet_bytes(rows)})
        temporary = entry / f"pointer-{version}.tmp"
        with temporary.open("xb") as stream:
            stream.write(encode({"version": version, "bundle_sha256": hashes["bundle_sha256"]}))
        os.replace(temporary, entry / "current.json")
        result = self.load_cached_daily(provider, security, start, end)
        return {"cache_status": result["cache_status"], "version": version, "quality": result["quality"],
                "corrections": corrections, "removed_sessions": removed,
                "recovered_corrupt_cache": metadata["recovered_corrupt_cache"]}


def history(cache, provider: DailyProvider, securities, start, end, *, mode="auto", overlap_days=7, clock=now_utc,
            permission_reference=None):
    """Only this orchestrator calls a provider. Offline reads use HistoryCache directly."""
    interval(start, end)
    if mode not in {"auto", "incremental", "full", "offline"}:
        raise ValueError("invalid refresh mode")
    if type(overlap_days) is not int or not 0 <= overlap_days <= 365:
        raise ValueError("overlap_days must be 0..365")
    select_securities([s.record() for s in securities], [s.symbol for s in securities], provider.name)
    outcomes = []
    for security in securities:
        result = {"symbol": security.symbol, "security_id": security.security_id, "provider": provider.name,
                  "provider_symbol": security.yahoo_symbol if provider.name == "yahoo" else security.ibkr_symbol,
                  "requested_interval": {"start": start, "end": end},
                  "snapshot_reference": None, "snapshot_sha256": None, "acquisition_status": "NOT_REQUESTED",
                  "retrieved_at": None, "errors": [], "historical_availability": "unknown"}
        try:
            with cache.lock(provider.name, security):
                old = cache.load_cached_daily(provider.name, security, start, end)
                result["previous_cache_status"] = old["cache_status"]
                if old["cache_status"] == "IDENTITY_MISMATCH":
                    raise ValueError("CACHE_IDENTITY_MISMATCH")
                if mode == "offline" or (mode == "auto" and old["cache_status"] == "HIT"):
                    result.update(cache_status=old["cache_status"], quality=old.get("quality"),
                                  acquisition_status="NOT_REQUESTED",
                                  cache_version=old["metadata"]["version"] if old["metadata"] else None,
                                  cache_source_snapshots=sorted(old["metadata"]["sources"]) if old["metadata"] else [])
                else:
                    if old["cache_status"] == "CORRUPT" and mode != "full":
                        raise ValueError("CACHE_CORRUPT_FULL_REFRESH_REQUIRED")
                    fetch_start = start
                    if mode != "full" and old.get("rows"):
                        latest = max(r["session_date"] for r in old["rows"])
                        overlap = max(start, (date.fromisoformat(latest) - timedelta(days=overlap_days)).isoformat())
                        missing = old["quality"]["missing_sessions"]
                        fetch_start = min([overlap] + missing)
                    path = cache.root / "snapshots" / provider.name / uuid4().hex
                    result["snapshot_reference"] = str(path)
                    fresh = provider.fetch_daily(security, fetch_start, end, path)
                    # Load and verify the actual saved capture; never trust a
                    # provider's in-memory summary as the source of cached values.
                    fresh = read_acquisition(path, security)
                    fresh["permission_reference"] = permission_reference
                    result.update(acquisition_status=fresh["acquisition"]["status"],
                                  errors=fresh["acquisition"]["errors"],
                                  retrieved_at=fresh["acquisition"]["completed_at"],
                                  returned_coverage=fresh["acquisition"].get("coverage"), basis=fresh["basis"],
                                  snapshot_sha256=fresh["snapshot_sha256"], request=fresh["request"],
                                  excluded_incomplete_sessions=fresh["excluded_incomplete_sessions"])
                    if fresh["acquisition"].get("termination"):
                        result["termination"] = fresh["acquisition"]["termination"]
                    result.update(cache.update(provider.name, security, start, end, fresh,
                                               full=mode == "full", clock=clock))
        except Exception as exc:
            # Per-symbol failure does not prevent the next security's attempt.
            code = str(exc) if isinstance(exc, ValueError) and str(exc) in {
                "CACHE_IDENTITY_MISMATCH", "CACHE_CORRUPT_FULL_REFRESH_REQUIRED"} else "HISTORY_FAILED"
            result.update(cache_status="FAILED", errors=[{"code": code, "exception_type": type(exc).__name__}])
            if result["snapshot_reference"] and result["snapshot_sha256"] is None:
                result["incomplete_attempt_reference"] = result["snapshot_reference"]
                result["snapshot_reference"] = None
                result["acquisition_status"] = "UNKNOWN_NO_COMPLETE_CAPTURE"
        outcomes.append(result)
    report = {"schema_version": "history_batch_v1", "provider": provider.name, "mode": mode,
              "permission_reference": permission_reference,
              "start": start, "end": end, "overlap_calendar_days": overlap_days,
              "results": outcomes, "status": "SUCCESS" if all(
                  r["cache_status"] == "HIT" and r.get("acquisition_status") in {"SUCCESS", "NOT_REQUESTED"}
                  for r in outcomes) else "PARTIAL_OR_FAILED"}
    report_path = cache.root / "reports" / uuid4().hex
    write_bundle(report_path, {"history.json": encode(report)})
    return dict(report, report_reference=str(report_path))
