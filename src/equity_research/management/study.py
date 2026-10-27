"""Small immutable analytical layer over PR16; no changes to its pinned reader."""

import json
from pathlib import Path

from ..comprehension.inputs import _check_hashes
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..lifecycle.study import _files as parent_files, identity as parent_identity, read_inputs
from .analysis import derive
from .report import markdown, dossier


def identity():
    return {"PR16": parent_identity(), "management": {p.name: digest(p.read_bytes())
        for p in sorted(Path(__file__).parent.glob("*.py"))}}


def validate_parent(files, hashes):
    _check_hashes(files, hashes)
    manifest = json.loads(files["manifest.json"])
    if manifest["schema_version"] != "grimes_lifecycle_study_v1" or manifest["implementation"] != parent_identity():
        raise ValueError("authoritative PR16 implementation differs from frozen parent")
    inputs = {k[len("input-"):]: v for k, v in files.items() if k.startswith("input-") and k != "input-hashes.json"}
    seals = json.loads(files["input-hashes.json"])
    _check_hashes(inputs, seals)
    if files != parent_files(inputs, seals):
        raise ValueError("PR16 semantic parent mismatch")
    return {k: json.loads(v) for k, v in files.items() if k.endswith(".json")}, read_inputs(inputs)


def _files(source, source_hashes, config):
    if (config.get("schema_version") != "grimes_management_config_v1"
            or config["parent_bundle_sha256"] != source_hashes["bundle_sha256"]
            or len(config["commentary_synopses"]) != 7
            or not config["inspected_main_commit"] or not config["inspected_pr16_commit"]):
        raise ValueError("explicit PR17 version, original parent hash and seven commentary references required")
    parent, inputs = validate_parent(source, source_hashes)
    if {r["alert_id"] for r in config["commentary_synopses"]} != {a["alert_id"] for a in parent["alerts.json"]["alerts"]}:
        raise ValueError("one commentary synopsis for each original alert required")
    result = derive(parent, inputs)
    result["commentary_synopses.json"] = config["commentary_synopses"]
    result["manifest.json"].update(parent_bundle_sha256=source_hashes["bundle_sha256"], implementation=identity(),
        inspected_main_commit=config["inspected_main_commit"], inspected_pr16_commit=config["inspected_pr16_commit"],
        source_price_bundles=parent["provenance.json"]["source_price_bundles"],
        historical_identity_cautions=inputs[0].get("identity_notes", []))
    files = {k: encode(v) for k, v in result.items()}
    files["report.md"] = markdown(result).encode()
    for p in result["positions.json"]:
        files[f"summary-{p['symbol']}.md"] = dossier(result, p["symbol"]).encode()
    files.update({"config.json": encode(config), "parent-hashes.json": encode(source_hashes),
        **{f"parent-{k}": v for k, v in source.items()}})
    return files


def freeze_study(parent, config, output):
    source, seals = read_bundle(parent)
    return write_bundle(Path(output), _files(source, seals, config))


def load_study(path):
    files, hashes = read_bundle(path)
    source = {k[len("parent-"):]: v for k, v in files.items() if k.startswith("parent-") and k != "parent-hashes.json"}
    seals = json.loads(files["parent-hashes.json"])
    if files != _files(source, seals, json.loads(files["config.json"])):
        raise ValueError("management semantic output mismatch")
    return {"files": files, "hashes": hashes}
