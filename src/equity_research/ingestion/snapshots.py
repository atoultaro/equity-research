"""Immutable acquisition records and integrity-checked historical comparison."""

import json
from pathlib import Path

from .frames import capture_frame, restore_frame
from .storage import digest, encode, read_bundle, write_bundle


def snapshot_files(request: dict, acquisition: dict, frame=None) -> dict[str, bytes]:
    files = {"request.json": encode(request)}
    if frame is not None:
        files["returned_frame.json"] = capture_frame(frame)
    # Stable content identity excludes attempt/timing/outcome metadata.
    identity = {name: digest(content) for name, content in sorted(files.items())}
    acquisition = dict(acquisition, schema_version="yahoo_acquisition_v1", capture_level="client_return",
                       content_sha256=digest(encode(identity)))
    files["acquisition.json"] = encode(acquisition)
    return files


def write_snapshot(output: Path, request: dict, acquisition: dict, frame=None):
    """Also usable for explicitly synthetic fixtures; acquisition uses a preclaimed path."""
    return write_bundle(output, snapshot_files(request, acquisition, frame))


def read_snapshot(path: Path) -> dict:
    files, hashes = read_bundle(path)
    if not {"request.json", "acquisition.json"} <= files.keys():
        raise ValueError("incomplete acquisition snapshot")
    request, acquisition = json.loads(files["request.json"]), json.loads(files["acquisition.json"])
    if (request.get("schema_version") != "yahoo_request_v1"
            or acquisition.get("schema_version") != "yahoo_acquisition_v1"):
        raise ValueError("unsupported snapshot schema")
    identity = {name: digest(content) for name, content in sorted(files.items()) if name != "acquisition.json"}
    if acquisition["content_sha256"] != digest(encode(identity)):
        raise ValueError("snapshot content identity mismatch")
    return {"request": request, "acquisition": acquisition, "hashes": hashes,
            "frame": restore_frame(files["returned_frame.json"]) if "returned_frame.json" in files else None,
            "files": files}


def compare(before: Path, after: Path) -> dict:
    from .canonical import price_columns, session_date
    from .frames import pack

    a, b = read_snapshot(before), read_snapshot(after)
    if (a["request"]["provider_symbol"], a["request"]["provider"]) != (
            b["request"]["provider_symbol"], b["request"]["provider"]):
        raise ValueError("comparison requires the same provider and symbol")
    start = max(a["request"]["start"], b["request"]["start"])
    end = min(a["request"]["end"], b["request"]["end"])
    if start > end:
        raise ValueError("snapshot request intervals do not overlap")
    result = {"schema_version": "snapshot_diff_v1", "before": a["hashes"]["bundle_sha256"],
              "after": b["hashes"]["bundle_sha256"], "overlap": {"start": start, "end": end},
              "stored_bytes_changed": a["hashes"]["files"] != b["hashes"]["files"],
              "frame_bytes_changed": a["hashes"]["files"].get("returned_frame.json") != b["hashes"]["files"].get("returned_frame.json")}
    result["stored_file_changes"] = [
        {"file": name, "before_sha256": a["hashes"]["files"].get(name), "after_sha256": b["hashes"]["files"].get(name)}
        for name in sorted(a["hashes"]["files"].keys() | b["hashes"]["files"].keys())
        if a["hashes"]["files"].get(name) != b["hashes"]["files"].get(name)]
    if a["frame"] is None or b["frame"] is None:
        return dict(result, status="UNKNOWN", reason="MISSING_RETURNED_FRAME")

    def keyed(snapshot):
        f = snapshot["frame"]
        columns = price_columns(f, snapshot["request"]["provider_symbol"])
        out = {}
        for i, raw in enumerate(f.index):
            key = session_date(raw)
            if key is None or key in out:
                raise ValueError("comparison requires unambiguous valid session keys")
            if start <= key <= end:
                out[key] = {name: pack(f.iloc[i, position]) for name, position in columns.items()}
        return out

    # Ambiguous inputs produce a diagnostic, never last-row-wins comparison.
    try:
        x, y = keyed(a), keyed(b)
    except ValueError:
        return dict(result, status="UNKNOWN", reason="AMBIGUOUS_SCHEMA_OR_SESSION_KEYS")
    fa, fb = json.loads(a["files"]["returned_frame.json"]), json.loads(b["files"]["returned_frame.json"])
    schema = lambda f: {k: f[k] for k in ("columns", "dtypes")} | {"index": {k: v for k, v in f["index"].items() if k not in {"values", "start", "stop", "codes"}}}
    changes = [{"session_date": day, "field": name, "before": x[day].get(name), "after": y[day].get(name)}
               for day in sorted(x.keys() & y.keys()) for name in sorted(x[day].keys() | y[day].keys())
               if x[day].get(name) != y[day].get(name)]
    return dict(result, status="PASS", schema_changed=schema(fa) != schema(fb),
                new_dates=sorted(y.keys() - x.keys()), removed_dates=sorted(x.keys() - y.keys()),
                changes=changes)
