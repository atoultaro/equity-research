"""Offline quality reporting and conditional export to the unchanged replay loader."""

import csv
import io
import tempfile
from pathlib import Path

from ..data import load_dataset
from .quality import analyze
from .storage import digest, encode, write_bundle


def validate(snapshot: Path, output: Path, evidence: dict | None = None) -> dict:
    result = analyze(snapshot, evidence)
    write_bundle(output, result["files"])
    return result["quality"]


def export(snapshot: Path, output: Path, evidence: dict | None = None) -> dict:
    result = analyze(snapshot, evidence)
    files, quality = result["files"], result["quality"]
    if quality["export_decision"] == "EXPORT_READY":
        ev, req = result["evidence"], result["snapshot"]["request"]
        columns = ["symbol", "session_date", "open", "high", "low", "close", "volume"]
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in result["canonical"]["rows"]:
            writer.writerow({"symbol": req["research_symbol"], **{k: row[k] for k in columns[1:]}})
        files["data.csv"] = stream.getvalue().encode()
        sessions = [dict(s, available_at=ev["availability"]["sessions"][s["session_date"]])
                    for s in result["schedule"]["sessions"]]
        manifest = {"symbol": req["research_symbol"], "source": req["provider"],
                    "source_revision": result["snapshot"]["acquisition"]["content_sha256"],
                    "dataset_version": "yahoo_research_v1", "created_at": None,
                    "adjustment": "raw", "corporate_actions": [], "exchange": "XNYS",
                    "timezone": "America/New_York", "calendar_version": result["schedule"]["schedule_sha256"],
                    "availability_convention": "affirmative per-session evidence; " + ev["availability"]["reference"],
                    "sessions": sessions, "data_sha256": digest(files["data.csv"]),
                    "provenance_sha256": digest(files["provenance.json"]),
                    "quality_sha256": digest(files["quality.json"]),
                    "evidence_kind": ev["kind"]}
        files["data_manifest.json"] = encode(manifest)
        # Exercise the existing strict loader before publishing any ready bundle.
        with tempfile.TemporaryDirectory(prefix="equity-export-check-") as tmp:
            directory = Path(tmp)
            for name in ("data.csv", "data_manifest.json"):
                (directory / name).write_bytes(files[name])
            load_dataset(directory / "data.csv", directory / "data_manifest.json")
    write_bundle(output, files)
    return quality
