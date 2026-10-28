"""Self-contained, semantically replayed inference study over pinned old studies."""

import json
from pathlib import Path

from ..comprehension.inputs import _check_hashes, capture_proof, replay_proof
from ..events.model import EventDataset
from ..ingestion.calendar import schedule
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..management.study import _files as management_files
from ..lifecycle.study import read_inputs as lifecycle_inputs
from .analysis import derive
from .basis import split_diagnostics
from .report import markdown, adjustment_markdown


def identity():
    return {p.name: digest(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))}


def freeze_inputs(parent, config, output):
    source, hashes = read_bundle(parent)
    if hashes["bundle_sha256"] != config["parent_pr17_sha256"]:
        raise ValueError("declared PR17 parent differs")
    proof = capture_proof(config["split_price_source"], sorted(config["split_events"]), "2020-08-01", "2022-08-31")
    if proof["source_bundle_hashes"]["bundle_sha256"] != config["split_price_source_sha256"]:
        raise ValueError("split price dependency differs")
    files = {"config.json": encode(config), "pr17-hashes.json": encode(hashes),
        **{f"pr17-{k}": v for k, v in source.items()}, "split-proof.json": encode(proof)}
    for symbol, reference in config["split_events"].items():
        members, seal = read_bundle(reference["path"])
        if seal["bundle_sha256"] != reference["bundle_sha256"]:
            raise ValueError("split event dependency differs")
        EventDataset(members, seal)
        files.update({f"events-{symbol}-{k}": v for k, v in members.items()})
        files[f"events-{symbol}-hashes.json"] = encode(seal)
    read_inputs(files)
    return write_bundle(output, files)


def read_inputs(files):
    config = json.loads(files["config.json"])
    if (config["schema_version"] != "grimes_reconstruction_config_v1" or config["mode"] != "EXPLORATORY_RECONSTRUCTION"
            or config["trigger_valid_sessions"] != 3 or config["fit_parameters_to_profit"] is not False):
        raise ValueError("fixed reconstruction definition and explicit exploratory mode required")
    source = {k[len("pr17-"):]: v for k, v in files.items() if k.startswith("pr17-") and k != "pr17-hashes.json"}
    hashes = json.loads(files["pr17-hashes.json"])
    _check_hashes(source, hashes)
    if hashes["bundle_sha256"] != config["parent_pr17_sha256"]:
        raise ValueError("PR17 parent hash differs from config")
    old_parent = {k[len("parent-"):]: v for k, v in source.items() if k.startswith("parent-") and k != "parent-hashes.json"}
    parent_hashes = json.loads(source["parent-hashes.json"])
    if source != management_files(old_parent, parent_hashes, json.loads(source["config.json"])):
        raise ValueError("PR17 semantic output mismatch")
    # management_files has already semantically validated these exact PR16
    # bytes. Reuse them without running that entire derivation a second time.
    parent = {k: json.loads(v) for k, v in old_parent.items() if k.endswith(".json")}
    input_files = {k[len("input-"):]: v for k, v in old_parent.items()
        if k.startswith("input-") and k != "input-hashes.json"}
    inputs = lifecycle_inputs(input_files)
    proof = json.loads(files["split-proof.json"])
    if proof["source_bundle_hashes"]["bundle_sha256"] != config["split_price_source_sha256"]:
        raise ValueError("split price proof differs from config")
    split_prices, _ = replay_proof(proof, "2020-08-01", "2022-08-31")
    splits = []
    for symbol, reference in config["split_events"].items():
        prefix = f"events-{symbol}-"
        members = {k[len(prefix):]: v for k, v in files.items() if k.startswith(prefix) and k != prefix+"hashes.json"}
        seal = json.loads(files[prefix+"hashes.json"])
        _check_hashes(members, seal)
        if seal["bundle_sha256"] != reference["bundle_sha256"]:
            raise ValueError("split event proof differs from config")
        events = EventDataset(members, seal).events
        chosen = [e for e in events if e["event_id"] == reference["event_id"]]
        if len(chosen) != 1:
            raise ValueError("one declared split event required")
        splits.append({"symbol": symbol, "event": chosen[0]})
    return config, parent, inputs, split_prices, splits, {k: json.loads(v) for k, v in source.items() if k in {"long_short.json", "relationships.json"}}


def _files(inputs_files, input_hashes):
    config, parent, inputs, prices, splits, prior_findings = read_inputs(inputs_files)
    result = derive(parent, inputs, config)
    result["split_diagnostics.json"] = split_diagnostics(prices, splits, schedule("2020-08-01", "2022-08-31"))
    result["pr17_hypotheses_under_test.json"] = prior_findings
    result["manifest.json"] = {"schema_version": "grimes_reconstruction_study_v1", "mode": config["mode"],
        "inputs_bundle_sha256": input_hashes["bundle_sha256"], "implementation": identity(),
        "inspected_main_commit": config["inspected_main_commit"], "source_episodes": 26, "source_actions": 72,
        "source_ledger_rewritten": False, "historical_universe_policy_changed": False, "actual_fills_known": False,
        "no_new_market_data_acquisition": True}
    files = {k: encode(v) for k, v in result.items()}
    files["report.md"] = markdown(result).encode()
    files["price_volume_diagnostics.md"] = adjustment_markdown(result).encode()
    files.update({"input-hashes.json": encode(input_hashes), **{f"input-{k}": v for k, v in inputs_files.items()}})
    return files


def freeze_study(inputs, output):
    files, hashes = read_bundle(inputs)
    return write_bundle(output, _files(files, hashes))


def load_study(path):
    files, hashes = read_bundle(path)
    source = {k[len("input-"):]: v for k, v in files.items() if k.startswith("input-") and k != "input-hashes.json"}
    seal = json.loads(files["input-hashes.json"])
    _check_hashes(source, seal)
    if files != _files(source, seal):
        raise ValueError("reconstruction semantic output mismatch")
    return {"files": files, "hashes": hashes}
