"""Self-contained market context bundles, shared source lineage and offline lookup."""

from bisect import bisect_left
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from .model import (Configuration, DEFINITION_VERSION, GROUPS, ROLES, SCHEMA,
                    build_rows, feature_definitions, required_history_sessions, timestamp)
from ..history.contracts import interval
from ..history.dataset import ResearchDataset
from ..ingestion.storage import digest, encode, read_bundle, write_bundle


def _configuration(record):
    config = Configuration(**{k: record[k] for k in ("availability", "delay_minutes", "describe_state")})
    if record != config.record():
        raise ValueError("unsupported market-context configuration")
    return config


def _definitions(datasets):
    return {name: {**d, "source_dataset_hashes": {r: datasets[r].content_sha256 for r in d["inputs"]},
                    "input_security_ids": {r: datasets[r].manifest["securities"][r]["security"]["security_id"] for r in d["inputs"]}}
            for name, d in feature_definitions().items()}


def _quality(rows):
    counts = {g: sum(all(v["status"] == "AVAILABLE" for v in r[g].values()) for r in rows) for g in GROUPS}
    core = GROUPS[:3]
    complete = [r for r in rows if all(v["status"] == "AVAILABLE" for g in core for v in r[g].values())]
    return {"schema_version": "market_feature_quality_v1", "evaluation_rows": len(rows),
            "complete_rows_by_group": counts, "complete_core_rows": len(complete),
            "incomplete_core_rows": len(rows) - len(complete),
            "first_complete_core_session": complete[0]["session_date"] if complete else None,
            "last_complete_core_session": complete[-1]["session_date"] if complete else None,
            "rows_with_missing_optional_features": sum(any(r[g] and any(v["status"] != "AVAILABLE" for v in r[g].values()) for g in GROUPS[3:]) for r in rows),
            "missing_feature_counts": dict(Counter(n for r in rows for n in r["missing_features"])),
            "descriptive_state_counts": dict(Counter(r["descriptive_state"] for r in rows if r["descriptive_state"])),
            "historical_availability_verified": False, "trading_policy": "NONE"}


def freeze_market_context(reference_paths, start, end, output, *, configuration=None):
    """Only freezes existing inputs; no acquisition or mutable-cache access."""
    from ..ingestion.calendar import schedule

    interval(start, end)
    if Path(output).exists():
        raise FileExistsError(output)
    if set(reference_paths) != set(ROLES):
        raise ValueError("reference roles must be exactly SPY, QQQ, RSP")
    configuration = configuration or Configuration()
    files, refs, datasets, embedded = {}, {}, {}, {}
    for role in ROLES:
        original, hashes = read_bundle(Path(reference_paths[role]))
        ds = ResearchDataset(original, hashes)
        datasets[role] = ds
        sha = hashes["bundle_sha256"]
        if sha not in embedded:
            names = {name: f"reference-{sha}-{name}" for name in original}
            files.update({names[name]: value for name, value in original.items()})
            embedded[sha] = {"hashes": hashes, "members": names}
        refs[role] = {"bundle_sha256": sha, "security": ds.manifest["securities"][role]["security"],
                      "qualified_contract": ds.manifest["securities"][role]["qualified_contract"],
                      "basis": ds.manifest["securities"][role]["basis"]}
    calendar = schedule(min([start] + [d.manifest["start"] for d in datasets.values()]), end)
    rows = build_rows(datasets, calendar, start, end, configuration)
    if not rows:
        raise ValueError("evaluation interval has no exchange sessions")
    context = {"schema_version": SCHEMA, "evaluation_start": start, "evaluation_end": end,
               "feature_definition_version": DEFINITION_VERSION,
               "market_reference_set_id": digest(encode({r: ref["security"] for r, ref in refs.items()})),
               "source_dataset_hashes": {r: d.content_sha256 for r, d in datasets.items()},
               "required_observations_including_evaluation_session": required_history_sessions(),
               "required_preceding_sessions": required_history_sessions() - 1,
               "assumed_availability": configuration.record(),
               "historical_price_vintage_availability": "UNKNOWN",
               "participation_interpretation": "NATIVE_ETF_RELATIVE_PRICE_PROXY_NOT_CONSTITUENT_BREADTH_OR_TOTAL_RETURN",
               "execution_admission": "UNCHANGED_NOT_GRANTED"}
    lineage = {"references": refs, "embedded_datasets": embedded}
    parts = {"market_context_manifest.json": context, "reference_dataset_lineage.json": lineage,
             "feature_definitions.json": _definitions(datasets), "market_context_daily.json": rows,
             "feature_quality.json": _quality(rows), "configuration.json": configuration.record(),
             "calendar.json": calendar}
    files.update({name: encode(value) for name, value in parts.items()})
    files["provenance.json"] = encode({
        "schema_version": "market_context_provenance_v1", "input_hashes": context["source_dataset_hashes"],
        "self_contained": True, "trading_policy": "NONE",
        "implementation_sha256": {name: digest(Path(__file__).with_name(name).read_bytes()) for name in ("model.py", "dataset.py")},
        "shared_dependency": datasets["SPY"].manifest["shared_dependency"],
        "component_sha256": {name: digest(files[name]) for name in parts}})
    return write_bundle(Path(output), files)


class MarketContext:
    def __init__(self, files, hashes):
        self._manifest = json.loads(files["market_context_manifest.json"])
        self._hashes = hashes
        m = self._manifest
        if m["schema_version"] != SCHEMA or m["feature_definition_version"] != DEFINITION_VERSION:
            raise ValueError("unsupported market context schema")
        interval(m["evaluation_start"], m["evaluation_end"])
        if (m["required_observations_including_evaluation_session"] != required_history_sessions() or
                m["required_preceding_sessions"] != required_history_sessions() - 1):
            raise ValueError("warmup definition mismatch")
        config = _configuration(json.loads(files["configuration.json"]))
        if m["assumed_availability"] != config.record():
            raise ValueError("availability configuration mismatch")
        lineage = json.loads(files["reference_dataset_lineage.json"])
        datasets = {}
        for sha, ref in lineage["embedded_datasets"].items():
            original = {name: files[frozen] for name, frozen in ref["members"].items()}
            actual = {name: digest(value) for name, value in sorted(original.items())}
            if actual != ref["hashes"]["files"] or digest(encode(actual)) != sha or sha != ref["hashes"]["bundle_sha256"]:
                raise ValueError("embedded reference integrity mismatch")
            datasets[sha] = ResearchDataset(original, ref["hashes"])
        self._references = {r: datasets[ref["bundle_sha256"]] for r, ref in lineage["references"].items()}
        if set(self._references) != set(ROLES):
            raise ValueError("reference roles mismatch")
        for role, ds in self._references.items():
            ref, entry = lineage["references"][role], ds.manifest["securities"][role]
            if any(ref[k] != entry[k] for k in ("security", "qualified_contract", "basis")):
                raise ValueError("reference identity provenance mismatch")
        if (m["source_dataset_hashes"] != {r: d.content_sha256 for r, d in self._references.items()} or
                m["market_reference_set_id"] != digest(encode({r: ref["security"] for r, ref in lineage["references"].items()}))):
            raise ValueError("source hash/reference identity mismatch")
        calendar = json.loads(files["calendar.json"])
        if (calendar["calendar"] != "XNYS" or calendar["version"] != "4.13.1" or
                calendar["schedule_sha256"] != digest(encode({k: v for k, v in calendar.items() if k != "schedule_sha256"}))):
            raise ValueError("frozen calendar mismatch")
        self._rows = json.loads(files["market_context_daily.json"])
        if (json.loads(files["feature_definitions.json"]) != _definitions(self._references) or
                self._rows != build_rows(self._references, calendar, m["evaluation_start"], m["evaluation_end"], config)):
            raise ValueError("frozen features differ from causal windows/configuration")
        self._quality = json.loads(files["feature_quality.json"])
        if self._quality != _quality(self._rows):
            raise ValueError("feature quality mismatch")
        provenance = json.loads(files["provenance.json"])
        if any(digest(files[name]) != sha for name, sha in provenance["component_sha256"].items()):
            raise ValueError("context component provenance mismatch")
        self._eligible = [(timestamp(r["available_at"]), i) for i, r in enumerate(self._rows) if r["available_at"] is not None]

    @property
    def content_sha256(self): return self._hashes["bundle_sha256"]

    @property
    def manifest(self): return deepcopy(self._manifest)

    @property
    def quality(self): return deepcopy(self._quality)

    def observations(self): return deepcopy(self._rows)

    def context_as_of(self, decision_timestamp):
        decision = timestamp(decision_timestamp)
        # Strictly before the decision, not at equality with modeled availability.
        index = bisect_left([t for t, _ in self._eligible], decision) - 1
        if index < 0:
            return {"status": "UNAVAILABLE", "reason": "NO_HISTORICALLY_ELIGIBLE_SNAPSHOT",
                    "decision_timestamp": decision.isoformat(), "historical_dissemination_verified": False}
        row = deepcopy(self._rows[self._eligible[index][1]])
        return {"status": "AVAILABLE_UNDER_RECONSTRUCTED_ASSUMPTION", "context": row,
                "decision_timestamp": decision.isoformat(), "historical_dissemination_verified": False,
                "market_reference_set_id": self._manifest["market_reference_set_id"],
                "source_dataset_hashes": deepcopy(self._manifest["source_dataset_hashes"]),
                "feature_definition_version": DEFINITION_VERSION,
                "latest_snapshot_may_have_missing_features": True}


def load_market_context(path):
    """Standard-library plus pinned shared math; no provider/cache/calendar imports."""
    return MarketContext(*read_bundle(Path(path)))
