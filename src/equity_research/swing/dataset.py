"""Self-contained immutable strategy research with validated frozen dependencies."""

from copy import deepcopy
import json
from pathlib import Path

from .engine import evaluate
from .model import Configuration
from ..events.dataset import EventStudy, _embed, _extract
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..market_context.dataset import MarketContext
from ..reporting import shared_identity


def _results(study, context, config, start, end):
    m = study.manifest
    if (study.prices.quality(m["symbol"])["status"] != "PASS" or
            study.prices.manifest["shared_dependency"] != shared_identity()):
        raise ValueError("complete valid prices and pinned shared indicators required")
    return evaluate(study.bars(), study._calendar, m["symbol"], m["security_id"], study.prices.content_sha256,
                    config, start=start, end=end, context=context, events=study.event_dataset)


def freeze_strategy(study_path, context_path, output, *, configuration=None, start="2024-01-02", end="2026-10-20"):
    if Path(output).exists():
        raise FileExistsError(output)
    files = {}
    study_files, study_hashes = read_bundle(Path(study_path))
    study = EventStudy(study_files, study_hashes)
    config = configuration or Configuration()
    study_ref = _embed(files, "study-", study_files, study_hashes)
    context, context_ref = None, None
    if context_path is not None:
        context_files, context_hashes = read_bundle(Path(context_path))
        context = MarketContext(context_files, context_hashes)
        context_ref = _embed(files, "context-", context_files, context_hashes)
    results = _results(study, context, config, start, end)
    m = study.manifest
    manifest = {"schema_version": "swing_research_v1", "symbol": m["symbol"], "security_id": m["security_id"],
                "evaluation_start": start, "evaluation_end": end, "configuration_sha256": config.sha256,
                "price_dataset_sha256": study.prices.content_sha256, "study_sha256": study.content_sha256,
                "context_bundle_sha256": context.content_sha256 if context else None,
                "execution_admission": "UNCHANGED_NOT_GRANTED", "inputs": {"study": study_ref, "context": context_ref}}
    inventory = study.retrospective["events"]
    parts = {"strategy_manifest.json": manifest, "strategy_config.json": config.record(),
             **{name + ".json": value for name, value in results.items()},
             "corporate_action_inventory.json": {"interpretation": "RETROSPECTIVE_EVIDENCE_NOT_DETECTION_INPUT_UNLESS_AS_KNOWN",
                                                   "events": inventory, "quality": study.event_dataset.quality}}
    files.update({name: encode(value) for name, value in parts.items()})
    files["provenance.json"] = encode({"schema_version": "swing_provenance_v1", "self_contained": True,
        "source_paths_at_freeze": {"study": str(Path(study_path)), "context": str(Path(context_path)) if context_path else None},
        "input_hashes": {"study": study.content_sha256, "prices": study.prices.content_sha256,
                         "context": context.content_sha256 if context else None},
        "shared_dependency": shared_identity(),
        "implementation_sha256": {p.name: digest(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))},
        "components": {name: digest(files[name]) for name in parts}})
    return write_bundle(Path(output), files)


class StrategyResearch:
    def __init__(self, files, hashes):
        m = json.loads(files["strategy_manifest.json"])
        if m["schema_version"] != "swing_research_v1" or m["execution_admission"] != "UNCHANGED_NOT_GRANTED":
            raise ValueError("unsupported strategy bundle")
        config = Configuration.from_record(json.loads(files["strategy_config.json"]))
        study = EventStudy(*_extract(files, m["inputs"]["study"]))
        context = MarketContext(*_extract(files, m["inputs"]["context"])) if m["inputs"]["context"] else None
        if (m["symbol"] != study.manifest["symbol"] or m["security_id"] != study.manifest["security_id"] or
                m["configuration_sha256"] != config.sha256 or m["study_sha256"] != study.content_sha256 or
                m["price_dataset_sha256"] != study.prices.content_sha256 or
                m["context_bundle_sha256"] != (context.content_sha256 if context else None)):
            raise ValueError("strategy source identity/hash mismatch")
        results = _results(study, context, config, m["evaluation_start"], m["evaluation_end"])
        if any(json.loads(files[name + ".json"]) != value for name, value in results.items()):
            raise ValueError("strategy records differ from causal inputs/configuration")
        inventory = json.loads(files["corporate_action_inventory.json"])
        if inventory["events"] != study.retrospective["events"] or inventory["quality"] != study.event_dataset.quality:
            raise ValueError("corporate action inventory mismatch")
        provenance = json.loads(files["provenance.json"])
        if (provenance["shared_dependency"] != shared_identity() or any(digest(files[name]) != sha for name, sha in provenance["components"].items()) or
                provenance["input_hashes"] != {"study": study.content_sha256, "prices": study.prices.content_sha256,
                                               "context": context.content_sha256 if context else None}):
            raise ValueError("strategy provenance mismatch")
        self._results, self._manifest, self._hashes = results, m, hashes

    @property
    def content_sha256(self): return self._hashes["bundle_sha256"]

    @property
    def manifest(self): return deepcopy(self._manifest)

    @property
    def results(self): return deepcopy(self._results)


def load_strategy(path):
    """No calendar generation, SDK imports, providers, cache pointers or network."""
    return StrategyResearch(*read_bundle(Path(path)))
