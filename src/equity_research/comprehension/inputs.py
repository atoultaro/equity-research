"""Small, self-contained views of PR14's immutable native-return checkpoints.

Retain the complete checkpoint hash chain and original report's file registry,
but copy native frames only for relevant windows. Never trust daily_bars.json
or a copied coverage summary. Recompute the selected price inventory on load.
"""

import json
from pathlib import Path

from ..events.model import timestamp, day
from ..history.depth_store import load_audit, window_rows
from ..ingestion.storage import digest, encode, read_bundle, write_bundle

PRICE_BASIS = "IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED"
VOLUME_BASIS = "IBKR_NATIVE_UNITS_UNVERIFIED"


def _check_hashes(files, hashes, *, complete=True):
    if (hashes.get("schema_version") != "artifact_hashes_v1" or hashes.get("algorithm") != "sha256"
            or digest(encode(hashes["files"])) != hashes["bundle_sha256"]
            or (complete and set(files) != set(hashes["files"]))
            or any(digest(v) != hashes["files"].get(k) for k, v in files.items())):
        raise ValueError("source proof hash mismatch")


def _relevant(event, symbols, start, end):
    return (event.get("symbol") in symbols and event["kind"] == "window"
            and event["start"] <= end and event["end"] >= start)


def capture_proof(path, symbols, start, end):
    files, hashes = read_bundle(path)
    # Existing PR14 loader independently checks the full source chain first.
    journal = load_audit(path)
    keep = {k: files[k] for k in ("audit_manifest.json", "plan.json", "plan-hashes.json", "calendar.json", "coverage.json")}
    for item in journal.events:
        prefix = f"checkpoint-{item['path']}-"
        names = item["files"] if _relevant(item["event"], symbols, start, end) else ("event.json",)
        for name in names:
            keep[prefix + name] = files[prefix + name]
        keep[prefix + "hashes.json"] = files[prefix + "hashes.json"]
    return {"source_bundle_hashes": hashes, "symbols": sorted(symbols),
            "files": {k: v.decode("utf-8") for k, v in keep.items()}}


def replay_proof(proof, start, end):
    files = {k: v.encode("utf-8") for k, v in proof["files"].items()}
    _check_hashes(files, proof["source_bundle_hashes"], complete=False)
    plan, calendar, manifest = (json.loads(files[k]) for k in ("plan.json", "calendar.json", "audit_manifest.json"))
    plan_hashes = json.loads(files["plan-hashes.json"])
    _check_hashes({k: files[k] for k in ("plan.json", "calendar.json")}, plan_hashes)
    if (manifest["schema_version"] != "ibkr_depth_report_v1" or manifest["plan"] != plan
            or manifest["origin"] not in {"ibkr_client", "synthetic"}
            or manifest["plan_sha256"] != plan_hashes["bundle_sha256"]
            or manifest["calendar_sha256"] != digest(encode(calendar))):
        raise ValueError("source plan mismatch")
    by_symbol = {i["security"]["symbol"]: i["security"] for i in plan["config"]["instruments"]}
    symbols = proof["symbols"]
    if not symbols or len(symbols) != len(set(symbols)) or set(symbols) - set(by_symbol):
        raise ValueError("ambiguous selected source identities")
    events, previous = [], plan_hashes["bundle_sha256"]
    for sequence, sha in sorted(manifest["checkpoint_hashes"].items()):
        prefix = f"checkpoint-{sequence}-"
        seal = json.loads(files[prefix + "hashes.json"])
        content = {k[len(prefix):]: v for k, v in files.items() if k.startswith(prefix) and k != prefix + "hashes.json"}
        event = json.loads(content["event.json"])
        _check_hashes(content, seal, complete=_relevant(event, symbols, start, end))
        if (seal["bundle_sha256"] != sha or event["sequence"] != int(sequence)
                or event["previous_sha256"] != previous):
            raise ValueError("source checkpoint chain mismatch")
        events.append({"event": event, "files": content, "hashes": seal, "path": sequence})
        previous = sha
    if previous != manifest["journal_tip_sha256"]:
        raise ValueError("source tip mismatch")
    prices, coverage = {}, {}
    for symbol in symbols:
        security = by_symbol[symbol]
        selected = [i for i in events if i["event"].get("symbol") == symbol]
        qualifications = [i["event"] for i in selected if i["event"]["kind"] == "qualification"]
        contracts = [e.get("contract") for e in qualifications if e["status"] == "SUCCESS"]
        if not contracts or any(c != contracts[0] for c in contracts) or any(e["status"] != "SUCCESS" for e in qualifications):
            raise ValueError(f"unqualified/ambiguous contract: {symbol}")
        contract = contracts[0]
        if (contract["symbol"] != security["ibkr_symbol"] or contract["currency"] != "USD"
                or contract["secType"] != "STK" or contract["exchange"] != "SMART"
                or contract["primaryExchange"] != security["primary_exchange"]
                or type(contract["conId"]) is not int or contract["conId"] <= 0
                or security.get("con_id") not in {None, contract["conId"]}):
            raise ValueError("qualified source identity mismatch")
        rows, conflicts, issues, windows, diagnostics = {}, [], [], [], []
        for item in selected:
            event = item["event"]
            if event.get("status") not in {None, "SUCCESS"}:
                diagnostics.append(event)
            if not _relevant(event, symbols, start, end):
                continue
            params = event["parameters"]
            if (params["whatToShow"] != "TRADES" or params["barSizeSetting"] != "1 day"
                    or params["useRTH"] is not True or params["keepUpToDate"] is not False):
                raise ValueError("incompatible native data basis")
            windows.append({k: event.get(k) for k in ("start", "end", "started_at", "completed_at", "status")})
            native, findings, _ = window_rows(item, security)
            issues.extend({**f, "checkpoint": item["path"]} for f in findings)
            if event["status"] != "SUCCESS":
                continue
            for row in native:
                d = row["session_date"]
                if not start <= d <= end:
                    continue
                if d in rows and any(rows[d][k] != row[k] for k in ("open", "high", "low", "close", "volume")):
                    conflicts.append(d)
                else:
                    rows.setdefault(d, row)
        if conflicts or any(f["status"] == "FAIL" and (f["session_date"] is None or start <= f["session_date"] <= end) for f in issues):
            raise ValueError(f"invalid/conflicting in-scope source data: {symbol}")
        prices[symbol] = [rows[d] for d in sorted(rows)]
        coverage[symbol] = {"contract": contract, "security": security, "origin": plan["origin"],
            "source_bundle_sha256": proof["source_bundle_hashes"]["bundle_sha256"],
            "price_basis": PRICE_BASIS, "volume_basis": VOLUME_BASIS, "request_windows": windows,
            "native_capture_findings": issues, "request_diagnostics": diagnostics,
            "historical_publication_times": "UNKNOWN", "corporate_action_completeness": "UNKNOWN",
            "original_global_audit_summary_claim": next(r for r in json.loads(files["coverage.json"]) if r["symbol"] == symbol),
            "global_summary_validation_scope": "Original source claim, hash-bound; only selected-window native frames recomputed here"}
    return prices, coverage


def validate_observations(record):
    if record["schema_version"] != "expert_observations_v1" or not record["source_reference"] or not record["original_source_text"] or not record["expert"]:
        raise ValueError("explicit expert source required")
    cutoff = timestamp(record["analysis_cutoff"])
    from zoneinfo import ZoneInfo
    local = cutoff.astimezone(ZoneInfo("America/New_York"))
    if local.date().isoformat() != day(record["recommendation_date"]) or local.hour < 16:
        raise ValueError("explicit after-close same-day cutoff required")
    seen = set()
    from decimal import Decimal
    for r in record["recommendations"]:
        if r["symbol"] in seen or r["direction"] not in {"LONG", "SHORT"} or r["action"] != "OPEN_NEW_POSITION":
            raise ValueError("distinct new-position observations required")
        seen.add(r["symbol"])
        stop = Decimal(r["reported_stop"])
        if not stop.is_finite() or stop <= 0 or not r["original_recommendation"] or r["original_recommendation"] not in record["original_source_text"]:
            raise ValueError("preserve original recommendation and positive reported stop")
        if any(r[k] is not None for k in ("publication_timestamp", "execution_timestamp", "entry_price", "quantity", "profit_targets")):
            raise ValueError("this observation workflow requires unknown execution and publication fields")
    if not seen:
        raise ValueError("empty expert inventory")
    return cutoff


def freeze_inputs(spec, audits, output):
    """audits = [(frozen_report_path, [explicit symbols]), ...]; entirely offline."""
    validate_observations(spec["observations"])
    start, end = day(spec["analysis_start"]), day(spec["observations"]["recommendation_date"])
    proofs = [capture_proof(path, symbols, start, end) for path, symbols in audits]
    files = {"research.json": encode(spec), "source-proofs.json": encode(proofs)}
    # Validate the independently replayed source inputs before sealing anything.
    read_inputs(files)
    return write_bundle(Path(output), files)


def read_inputs(files):
    spec = json.loads(files["research.json"])
    if spec["schema_version"] != "expert_research_inputs_v1":
        raise ValueError("unsupported expert research input schema")
    validate_observations(spec["observations"])
    start, end = day(spec["analysis_start"]), spec["observations"]["recommendation_date"]
    prices, coverage = {}, {}
    for proof in json.loads(files["source-proofs.json"]):
        rows, info = replay_proof(proof, start, end)
        if set(prices) & set(rows):
            raise ValueError("multiple source identities/revisions for one symbol")
        prices.update(rows)
        coverage.update(info)
    ids = [v["contract"]["conId"] for v in coverage.values()]
    if len(ids) != len(set(ids)):
        raise ValueError("contract alias collision")
    from ..ingestion.calendar import schedule
    calendar = schedule(start, end)
    valid = {s["session_date"] for s in calendar["sessions"]}
    for symbol, rows in prices.items():
        if any(r["session_date"] not in valid for r in rows):
            raise ValueError(f"off-calendar source: {symbol}")
    return spec, prices, coverage, calendar
