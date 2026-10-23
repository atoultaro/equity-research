"""Immutable outcome composition; consume captured signals, never regenerate them."""

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from .analysis import cluster_signals, summarize, context_descriptor
from .model import Configuration, measure
from ..events.dataset import EventStudy, _extract
from ..history.dataset import ResearchDataset
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..models import timestamp


def _context_identity(files, manifest):
    """Verify frozen context lineage/components without another as-of lookup."""
    if manifest["context_bundle_sha256"] is None:
        if manifest["inputs"]["context"] is not None: raise ValueError("context identity mismatch")
        return None, set()
    members, hashes = _extract(files, manifest["inputs"]["context"])
    if hashes["bundle_sha256"] != manifest["context_bundle_sha256"]: raise ValueError("context hash mismatch")
    m = json.loads(members["market_context_manifest.json"])
    if m["schema_version"] != "market_context_v1": raise ValueError("unsupported context version")
    lineage = json.loads(members["reference_dataset_lineage.json"])
    if (set(lineage['references']) != set(m['source_dataset_hashes']) or
            m['market_reference_set_id'] != digest(encode({r:ref['security'] for r,ref in lineage['references'].items()}))):
        raise ValueError('context reference-set identity mismatch')
    for sha, ref in lineage["embedded_datasets"].items():
        ds = ResearchDataset(*_extract(members, {**ref,"bundle_sha256":sha}))
        for role, entry in lineage["references"].items():
            if entry["bundle_sha256"] == sha:
                if m["source_dataset_hashes"][role] != sha or entry["security"] != ds.manifest["securities"][role]["security"]:
                    raise ValueError("context reference identity mismatch")
    provenance = json.loads(members["provenance.json"])
    if any(digest(members[n]) != sha for n,sha in provenance["component_sha256"].items()): raise ValueError("context component mismatch")
    return m, {digest(encode(r)) for r in json.loads(members["market_context_daily.json"])}


class FrozenSignals:
    """Schema-compatible captured inventory, backed by its complete frozen inputs.

    PR7B's load_strategy recomputes detection for its own validation. Outcome work
    deliberately validates the recorded identities, components and dependencies
    without calling that reader, a detector, ATR calculation or context_as_of.
    """
    def __init__(self, files, hashes):
        self.files,self.hashes=files,hashes
        m=json.loads(files["strategy_manifest.json"])
        if m["schema_version"] != "swing_research_v1":raise ValueError("unsupported strategy inventory")
        config=json.loads(files["strategy_config.json"])
        if config["schema_version"] != "swing_strategy_config_v1" or digest(encode(config)) != m["configuration_sha256"]:
            raise ValueError("strategy configuration identity mismatch")
        study=EventStudy(*_extract(files,m["inputs"]["study"]))
        if (m["study_sha256"] != study.content_sha256 or m["price_dataset_sha256"] != study.prices.content_sha256 or
                m["symbol"] != study.manifest["symbol"] or m["security_id"] != study.manifest["security_id"]):
            raise ValueError("PRICE_DATASET_MISMATCH or signal/security identity mismatch")
        cm,context_rows=_context_identity(files,m)
        self.signals=json.loads(files["signals.json"])
        self.links=json.loads(files["market_context_links.json"])
        setups=json.loads(files["setup_observations.json"]);triggers=json.loads(files["triggers.json"])
        bylink={l["link_sha256"]:l for l in self.links}
        if len(bylink)!=len(self.links) or len({s["signal_id"] for s in self.signals})!=len(self.signals):raise ValueError("duplicate signal/link identity")
        for signal in self.signals:
            if (signal["schema_version"] != "swing_signal_v1" or signal["symbol"] != m["symbol"] or signal["security_id"] != m["security_id"] or
                    signal["price_dataset_sha256"] != m["price_dataset_sha256"] or signal["configuration_sha256"] != m["configuration_sha256"] or
                    signal["strategy_id"] != config["strategy_id"] or signal["strategy_version"] != config["strategy_version"] or
                    signal['setup']['boundary']['price_dataset_sha256'] != m['price_dataset_sha256'] or
                    signal['setup']['boundary']['configuration_sha256'] != m['configuration_sha256'] or
                    signal["setup"] not in setups or signal["trigger"] not in triggers or
                    signal["setup"]["setup_id"] != signal["trigger"]["setup_id"] or
                    signal["signal_id"] != "signal:"+digest(encode([signal["setup"]["setup_id"],signal["trigger"]]))):
                raise ValueError("original signal identity/provenance mismatch")
            if not m["evaluation_start"] <= signal["trigger"]["session_date"] <= m["evaluation_end"]:raise ValueError("signal outside evaluation interval")
            link=bylink[signal["market_context_reference"]]
            if (link["signal_id"] != signal["signal_id"] or link["context_bundle_sha256"] != m["context_bundle_sha256"] or
                    timestamp(link['decision_timestamp']) != timestamp(signal['trigger']['available_at']) or
                    digest(encode({k:v for k,v in link.items() if k != "link_sha256"})) != link["link_sha256"]):
                raise ValueError("original context link identity mismatch")
            if link["status"] != "UNAVAILABLE":
                if (cm is None or digest(encode(link["context"])) not in context_rows or
                        timestamp(link["context"]["available_at"]) >= timestamp(signal["trigger"]["available_at"]) or
                        link["market_reference_set_id"] != cm["market_reference_set_id"] or
                        link["feature_definition_version"] != cm["feature_definition_version"] or
                        link["source_dataset_hashes"] != cm["source_dataset_hashes"]):raise ValueError("ineligible or foreign captured context")
        if {l["signal_id"] for l in self.links} != {s["signal_id"] for s in self.signals}:raise ValueError("orphan context link")
        inventory=json.loads(files["corporate_action_inventory.json"])
        if inventory["events"] != study.event_dataset.events or inventory["quality"] != study.event_dataset.quality:raise ValueError("event inventory mismatch")
        p=json.loads(files["provenance.json"])
        required={'strategy_manifest.json','strategy_config.json','signals.json','market_context_links.json',
                  'setup_observations.json','triggers.json','corporate_action_inventory.json'}
        if not required <= set(p['components']) or any(digest(files[n]) != sha for n,sha in p["components"].items()):raise ValueError("strategy component mismatch")
        if p["input_hashes"] != {"study":study.content_sha256,"prices":study.prices.content_sha256,"context":m["context_bundle_sha256"]}:
            raise ValueError("strategy source provenance mismatch")
        self.manifest=m;self.study=study;self.rows=study.bars();self.calendar=study._calendar
        self.basis=study.prices.manifest["securities"][m["symbol"]]["basis"]
        self.actions=[e for e in study.event_dataset.events if e["event_type"] in {"SPLIT","DIVIDEND"}]
        self.alignments=study._alignment["events"];self.conflicts=study.event_dataset.quality["conflicting_event_ids"]
        self.content_sha256=hashes["bundle_sha256"]


def _calculate(inputs,config):
    ids=[s["signal_id"] for source in inputs for s in source.signals]
    if len(set(ids))!=len(ids):raise ValueError("duplicate original signal across input inventories; choose one immutable version")
    # The same security must retain one stock/calendar/context vintage across its
    # strategies. Different securities may have different price and event inputs.
    identities={}
    for source in inputs:
        m=source.manifest
        key=(m["price_dataset_sha256"],digest(encode(source.calendar)),m["context_bundle_sha256"])
        if m["security_id"] in identities and identities[m["security_id"]]!=key:raise ValueError("incompatible security input vintages")
        identities[m["security_id"]]=key
    outcomes,comparisons,signals,links=[],[],[],[]
    for source in inputs:
        for signal in source.signals:
            measured,paired=measure(signal,source.rows,source.calendar,price_sha=source.manifest["price_dataset_sha256"],
                strategy_sha=source.content_sha256,basis=source.basis,configuration=config,
                actions=source.actions,alignments=source.alignments,conflicting_events=source.conflicts)
            outcomes.extend(measured);comparisons.extend(paired)
        signals.extend(deepcopy(source.signals));links.extend(deepcopy(source.links))
    outcomes.sort(key=lambda r:(r["signal_id"],r["reference_type"],r["horizon"]))
    signals.sort(key=lambda r:r["signal_id"]);links.sort(key=lambda r:r["signal_id"])
    clusters=cluster_signals(inputs,config)
    summary=summarize(outcomes,links,clusters,comparisons,config)
    return {"outcomes.json":outcomes,"signal_inventory.json":signals,"context_links.json":links,
        "corporate_action_annotations.json":[{"signal_id":r["signal_id"],"reference_type":r["reference_type"],"horizon":r["horizon"],
            **r["corporate_action_uncertainty"]} for r in outcomes],
        "dependency_clusters.json":clusters,"reference_comparisons.json":sorted(comparisons,key=lambda r:(r["signal_id"],r["signal_close_horizon"])),
        "descriptive_summary.json":summary,
        "quality_report.json":{"original_signal_count":len(ids),"preserved_signal_count":len(signals),"outcome_rows":len(outcomes),
            "status_counts":dict(Counter(r["outcome_status"] for r in outcomes)),
            "unavailable_reason_counts":dict(sorted(Counter(reason for r in outcomes for reason in r["unavailable_reasons"]).items())),
            "context_status_counts":dict(Counter(l["status"] for l in links)),
            "context_state_counts":dict(Counter(context_descriptor(l) for l in links)),
            "outcome_interpretation":"DESCRIPTIVE_NATIVE_PRICE_PATHS_NOT_EXECUTABLE_RETURNS",
            "execution_admission":"UNCHANGED_NOT_GRANTED","signal_generation":"NOT_RUN","context_lookup":"NOT_RUN"}}


def _embed(files, original, hashes):
    members={name:"blob-"+digest(value) for name,value in original.items()}
    for name,value in original.items():files[members[name]]=value
    return {"bundle_sha256":hashes["bundle_sha256"],"hashes":hashes,"members":members}


def freeze_outcomes(strategy_paths,output,*,configuration=None):
    if Path(output).exists():raise FileExistsError(output)
    config=configuration or Configuration()
    files,inputs,refs={},[],{}
    paths=sorted(map(Path,strategy_paths),key=str)
    if not paths:raise ValueError("at least one frozen strategy bundle required")
    for path in paths:
        original,hashes=read_bundle(path)
        sha=hashes["bundle_sha256"]
        if sha in refs:raise ValueError("duplicate strategy bundle input")
        inputs.append(FrozenSignals(original,hashes))
        refs[sha]={**_embed(files,original,hashes),"source_path_at_freeze":str(path)}
    inputs.sort(key=lambda s:s.content_sha256)
    parts=_calculate(inputs,config)
    parts["outcome_definitions.json"]=config.record()
    parts["outcome_manifest.json"]={"schema_version":"signal_outcome_bundle_v1","definition_sha256":config.sha256,
        "inputs":refs,"signal_inventory_sha256":digest(encode(parts["signal_inventory.json"])),
        "purpose":"RESEARCH_ONLY_NO_EXECUTION_OR_DETECTION"}
    files.update({n:encode(v) for n,v in parts.items()})
    files["provenance.json"]=encode({"schema_version":"outcome_provenance_v1","self_contained":True,
        "input_hashes":sorted(refs),"components":{n:digest(files[n]) for n in parts},
        "implementation_sha256":{p.name:digest(p.read_bytes()) for p in sorted(Path(__file__).parent.glob('*.py'))}})
    return write_bundle(Path(output),files)


class OutcomeResearch:
    def __init__(self,files,hashes):
        m=json.loads(files["outcome_manifest.json"])
        if m["schema_version"]!="signal_outcome_bundle_v1" or m["purpose"]!="RESEARCH_ONLY_NO_EXECUTION_OR_DETECTION":raise ValueError("unsupported outcome bundle")
        config=Configuration.from_record(json.loads(files["outcome_definitions.json"]))
        if config.sha256!=m["definition_sha256"]:raise ValueError("outcome definition identity mismatch")
        inputs=[]
        for sha,ref in sorted(m["inputs"].items()):
            source=FrozenSignals(*_extract(files,ref))
            if source.content_sha256!=sha:raise ValueError("input strategy identity mismatch")
            inputs.append(source)
        results=_calculate(inputs,config)
        if any(json.loads(files[n])!=v for n,v in results.items()):raise ValueError("outcome semantic result mismatch")
        if digest(files['signal_inventory.json'])!=m['signal_inventory_sha256']:raise ValueError("signal inventory identity mismatch")
        p=json.loads(files['provenance.json'])
        expected=set(results)|{'outcome_manifest.json','outcome_definitions.json'}
        if (set(p['components'])!=expected or p['input_hashes']!=sorted(m['inputs']) or
                any(digest(files[n])!=sha for n,sha in p['components'].items())):raise ValueError("outcome provenance mismatch")
        self._manifest,self._results,self._hashes=m,results,hashes
    @property
    def content_sha256(self):return self._hashes['bundle_sha256']
    @property
    def manifest(self):return deepcopy(self._manifest)
    @property
    def results(self):return deepcopy(self._results)


def load_outcomes(path):return OutcomeResearch(*read_bundle(Path(path)))
