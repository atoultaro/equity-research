"""Self-contained immutable research datasets and an offline standard-library reader."""

from copy import deepcopy
import importlib.metadata
import json
from pathlib import Path
from statistics import mean

from .contracts import Security, interval, now_utc, select_securities
from ..ingestion.storage import digest, encode, read_bundle, write_bundle


def freeze(cache, provider, securities, start, end, output, *, allow_incomplete=False, clock=now_utc):
    from .normalize import reconcile
    from ..reporting import shared_identity

    interval(start, end)
    select_securities([s.record() for s in securities], [s.symbol for s in securities], provider)
    if Path(output).exists():
        raise FileExistsError(output)
    files, entries, sources = {}, {}, {}
    for security in securities:
        saved = cache.load_cached_daily(provider, security, start, end)
        if saved["cache_status"] not in {"HIT", "INCOMPLETE"}:
            raise ValueError(f"cannot freeze {security.symbol}: {saved['cache_status']}")
        rows, meta = saved["rows"], saved["metadata"]
        quality = reconcile(rows, security, start, end)
        if quality["status"] != "PASS" and not allow_incomplete:
            raise ValueError(f"missing/invalid sessions for {security.symbol}; no dataset written")
        # Copy complete original captures, including acquisition metadata and
        # native actions. No frozen file refers to a mutable external path.
        source_ids = sorted({row["source_snapshot_sha256"] for row in rows})
        events, capture_issues = [], []
        for source_id in source_ids:
            if source_id not in sources:
                original, hashes = read_bundle(Path(meta["sources"][source_id]))
                if hashes["bundle_sha256"] != source_id:
                    raise ValueError("snapshot lineage hash mismatch")
                names = {name: f"source-{source_id}-{name}" for name in original}
                files.update({names[name]: content for name, content in original.items()})
                sources[source_id] = {"files": names, "hashes": hashes}
            # Keep each referenced snapshot's native action observations, not an
            # unsupported completeness declaration or a manufactured empty set.
            from .normalize import read_acquisition
            native = read_acquisition(Path(meta["sources"][source_id]), security)
            events.extend(native["events"])
            capture_issues.extend({**issue, "source_snapshot_sha256": source_id} for issue in native["issues"])
        token = digest(encode(security.symbol))[:24]
        bars_name, quality_name = f"bars-{token}.json", f"quality-{token}.json"
        files[bars_name] = encode({"schema_version": "research_daily_v1", "rows": rows})
        files[quality_name] = encode({**quality, "issues": meta["issues"], "source_capture_issues": capture_issues,
                                      "provider_events": events,
                                      "basis_interpretation": "unresolved", "historical_availability": "unknown",
                                      "corporate_action_completeness": "unknown",
                                      "execution_export": "NOT_EVALUATED_USE_EXISTING_EXPORT_GATES"})
        entries[security.symbol] = {"security": security.record(), "basis": meta["basis"],
                                    "bars_file": bars_name, "quality_file": quality_name,
                                    "cache_version_at_freeze": meta["version"], "sources": source_ids,
                                    "permission_reference": meta.get("permission_reference"),
                                    "qualified_contract": meta.get("qualified_contract")}
    manifest = {"schema_version": "research_dataset_v1", "canonical_schema": "research_daily_v1",
                "provider": provider, "start": start, "end": end, "created_at": clock().isoformat(),
                "securities": entries, "sources": sources, "allow_incomplete": allow_incomplete,
                "calendar": {"name": "XNYS", "version": "4.13.1", "overrides": []},
                "configuration_version": "historical_equity_v1",
                "converter_sha256": digest(Path(__file__).with_name("normalize.py").read_bytes()),
                "dependencies": {name: importlib.metadata.version(name) for name in
                                 ("pandas", "numpy", "exchange-calendars", "tzdata", "pyarrow")},
                "identity_evidence": "explicit_user_mapping_not_independently_verified",
                "purpose": "offline_technical_research_not_execution_admission"}
    package = Path(__file__).resolve().parents[1]
    manifest["implementation_sha256"] = {name: digest((package / name).read_bytes()) for name in (
        "history/contracts.py", "history/normalize.py", "history/cache.py", "history/dataset.py",
        "ingestion/canonical.py", "ingestion/frames.py", "ingestion/calendar.py", "ingestion/storage.py")}
    manifest["shared_dependency"] = shared_identity()
    manifest["source_origins"] = sorted({json.loads(files[source["files"]["request.json"]])["origin"]
                                         for source in sources.values()})
    manifest["synthetic_only"] = manifest["source_origins"] == ["synthetic"]
    files["dataset.json"] = encode(manifest)
    return write_bundle(Path(output), files)


class ResearchDataset:
    def __init__(self, files, hashes):
        self._files, self._hashes = files, hashes
        self._manifest = json.loads(files["dataset.json"])
        if self._manifest["schema_version"] != "research_dataset_v1":
            raise ValueError("unsupported research dataset schema")
        self._rows, self._qualities = {}, {}
        for source_id, source in self._manifest["sources"].items():
            recorded = source["hashes"]
            actual = {name: digest(files[frozen]) for name, frozen in source["files"].items()}
            if actual != recorded["files"] or digest(encode(actual)) != source_id or recorded["bundle_sha256"] != source_id:
                raise ValueError("invalid embedded snapshot lineage")
        for symbol, entry in self._manifest["securities"].items():
            security = Security(**entry["security"])
            if symbol != security.symbol:
                raise ValueError("dataset security symbol mismatch")
            canonical = json.loads(files[entry["bars_file"]])
            if canonical["schema_version"] != "research_daily_v1":
                raise ValueError("invalid canonical schema")
            rows = canonical["rows"]
            for row in rows:
                source = self._manifest["sources"][row["source_snapshot_sha256"]]
                if (row["source_snapshot_sha256"] not in entry["sources"] or
                        row["security_id"] != security.security_id or row["symbol"] != symbol or
                        row["provider"] != self._manifest["provider"] or
                        row["price_basis"] != entry["basis"]["price_basis"] or
                        row["volume_basis"] != entry["basis"]["volume_basis"] or
                        row["source_row"]["sha256"] != source["hashes"]["files"]["returned_frame.json"]):
                    raise ValueError("canonical row provenance mismatch")
            self._rows[symbol] = rows
            self._qualities[symbol] = json.loads(files[entry["quality_file"]])

    @property
    def manifest(self):
        return deepcopy(self._manifest)

    @property
    def content_sha256(self):
        return self._hashes["bundle_sha256"]

    def bars(self, symbol):
        return tuple(deepcopy(self._rows[symbol]))

    def quality(self, symbol):
        return deepcopy(self._qualities[symbol])

    def _complete(self, symbol):
        if self._qualities[symbol]["status"] != "PASS":
            raise ValueError("indicators require complete, valid sessions; no forward fill")
        return self._rows[symbol]

    def indicators(self, symbol):
        """Full-window SMAs/volume, first-close-seeded EMA, gap-aware simple ATR.

        ATR needs a previous close and 14 ranges (15 bars), matching the strategy's
        warmup contract. No execution eligibility or historical availability claim.
        """
        from market_shared import atr_simple_series, ema_series, true_range
        from ..reporting import shared_identity
        if shared_identity() != self._manifest["shared_dependency"]:
            raise ValueError("shared indicator dependency differs from frozen dataset")
        rows = self._complete(symbol)
        closes = [float(r["close"]) for r in rows]
        volumes = [float(r["volume"]) for r in rows]
        ema = ema_series(closes, 50)
        ranges = [true_range(float(rows[i]["high"]), float(rows[i]["low"]), closes[i - 1])
                  for i in range(1, len(rows))]
        atr = [None] + atr_simple_series(ranges, 14) if rows else []

        def average(values, i, period):
            return mean(values[i + 1 - period:i + 1]) if i + 1 >= period else None

        return {"interpretation": "technical_diagnostics_native_basis_availability_unknown",
                "basis": deepcopy(self._manifest["securities"][symbol]["basis"]),
                "rows": [{"session_date": row["session_date"], "sma50": average(closes, i, 50),
                          "sma200": average(closes, i, 200), "ema50": ema[i], "atr14": atr[i],
                          "volume_average20": average(volumes, i, 20)} for i, row in enumerate(rows)]}

    def relative_strength(self, symbol, benchmark):
        from decimal import Decimal
        a, b = self._complete(symbol), self._complete(benchmark)
        if [r["session_date"] for r in a] != [r["session_date"] for r in b]:
            raise ValueError("relative strength requires identical sessions; no implicit alignment")
        return {"interpretation": "diagnostic_native_close_ratio_not_total_return_or_historical_rank",
                "rows": [{"session_date": x["session_date"], "ratio": str(Decimal(x["close"]) / Decimal(y["close"]))}
                         for x, y in zip(a, b, strict=True)]}


def load_research_dataset(path):
    """No cache lookup, calendar regeneration, provider import or network access."""
    return ResearchDataset(*read_bundle(Path(path)))
