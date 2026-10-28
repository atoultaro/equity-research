"""Offline observed-contract pilot over existing captures; never a population census.

PR8A policies are used unchanged. Native units and unknown identity/publication
evidence are retained, including when they prevent strict universe admission.
"""

from collections import Counter
from datetime import timedelta
import importlib.metadata
import json
from pathlib import Path
import platform

from ..comprehension.inputs import capture_proof, replay_proof
from ..ingestion.calendar import schedule
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..models import timestamp
from ..reporting import shared_identity
from ..universe import SecurityMaster, ResearchPanel, HistoricalUniverse, import_master, freeze_panel, build_universe, default_definition


def inventory_local_datasets(root):
    """Inspect retained standard datasets; SDK installation is not data coverage."""
    from ..history.dataset import load_research_dataset
    root = Path(root)
    datasets, requests, dbn = [], [], []
    for directory in (root / "data", root / "runs"):
        if not directory.exists():
            continue
        for p in sorted(directory.rglob("dataset.json")):
            record = json.loads(p.read_bytes())
            if record.get("schema_version") != "research_dataset_v1":
                continue
            dataset = load_research_dataset(p.parent)
            origins = dataset.manifest["source_origins"]
            instruments = []
            for symbol in sorted(dataset.manifest["securities"]):
                rows = dataset.bars(symbol)
                instruments.append({"symbol": symbol, "observed_sessions": len(rows),
                    "first_session": rows[0]["session_date"] if rows else None,
                    "last_session": rows[-1]["session_date"] if rows else None})
            datasets.append({"path": str(p.parent.relative_to(root)), "provider": dataset.manifest["provider"],
                "origins": origins, "synthetic_only": dataset.manifest["synthetic_only"],
                "instruments": instruments, "bundle_sha256": json.loads((p.parent / "hashes.json").read_bytes())["bundle_sha256"],
                "validation": "Bundle and embedded source lineage verified by existing history loader"})
        for p in sorted(directory.rglob("request.json")):
            record = json.loads(p.read_bytes())
            if record.get("schema_version") == "yahoo_request_v1":
                requests.append({"path": str(p.relative_to(root)), "origin": record["origin"]})
        dbn.extend(str(p.relative_to(root)) for p in directory.rglob("*") if p.is_file() and ".dbn" in p.name.lower())
    return {"schema_version": "existing_local_source_inventory_v1", "scope": "Repository data/ and runs/ only; no account or credential inspection",
        "datasets": datasets, "yahoo_requests": requests, "databento_dbn_files": sorted(dbn),
        "real_yahoo_dataset_count": sum(r["provider"] == "yahoo" and "yahoo_client" in r["origins"] for r in datasets),
        "databento_equity_coverage": "NOT_ESTABLISHED; no dataset entitlement or external-machine inventory inferred",
        "new_acquisition": False}


def capture_inputs(config, output):
    if config["schema_version"] != "observed_universe_config_v1":
        raise ValueError("versioned observed-universe configuration required")
    proofs = []
    for source in config["sources"]:
        proof = capture_proof(source["path"], source["symbols"], config["inventory_start"], config["end"])
        if proof["source_bundle_hashes"]["bundle_sha256"] != source["bundle_sha256"]:
            raise ValueError("existing immutable source hash differs from configuration")
        proofs.append(proof)
    files = {"config.json": encode(config), "source-proofs.json": encode(proofs)}
    read_inputs(files)
    return write_bundle(output, files)


def read_inputs(files):
    config, proofs = json.loads(files["config.json"]), json.loads(files["source-proofs.json"])
    if (config["schema_version"] != "observed_universe_config_v1"
            or config["origin"] not in {"RECORDED", "SYNTHETIC"}
            or len(config["sources"]) != len(proofs)
            or config["pilot_start"] < config["inventory_start"] or config["pilot_start"] > config["end"]):
        raise ValueError("invalid bounded observed-data inputs")
    prices, coverage, kinds = {}, {}, {}
    for source, proof in zip(config["sources"], proofs, strict=True):
        if (proof["source_bundle_hashes"]["bundle_sha256"] != source["bundle_sha256"]
                or sorted(proof["symbols"]) != sorted(source["symbols"])):
            raise ValueError("declared source dependency mismatch")
        rows, info = replay_proof(proof, config["inventory_start"], config["end"])
        expected_origin = "ibkr_client" if config["origin"] == "RECORDED" else "synthetic"
        if any(r["origin"] != expected_origin for r in info.values()):
            raise ValueError("synthetic and real evidence must not be mixed")
        if set(rows) & set(prices):
            raise ValueError("one selected source per symbol; revisions must not be silently combined")
        prices.update(rows)
        coverage.update(info)
        kinds.update({r["security"]["symbol"]: r["kind"] for r in json.loads(proof["files"]["plan.json"])["config"]["instruments"]
                      if r["security"]["symbol"] in rows})
    conids = [r["contract"]["conId"] for r in coverage.values()]
    if len(set(conids)) != len(conids):
        raise ValueError("ambiguous contract identity: conId reused across selected symbols")
    for symbol, rows in prices.items():
        dates = [r["session_date"] for r in rows]
        if dates != sorted(set(dates)):
            raise ValueError(f"duplicate or unordered observations: {symbol}")
    return config, prices, coverage, kinds


def coverage_inventory(prices, coverage, kinds, calendar, cycles):
    expected = [s["session_date"] for s in calendar["sessions"]]
    result = []
    for symbol, rows in sorted(prices.items()):
        days = {r["session_date"] for r in rows}
        first, last = (min(days), max(days)) if days else (None, None)
        gaps = [d for d in expected if first and first <= d <= last and d not in days]
        result.append({"capture_symbol": symbol, "con_id": coverage[symbol]["contract"]["conId"], "kind": kinds[symbol],
            "first_observed_session": first, "last_observed_session": last, "observed_sessions": len(days),
            "missing_internal_sessions": gaps, "missing_internal_count": len(gaps),
            "source_bundle_sha256": coverage[symbol]["source_bundle_sha256"],
            "price_basis": coverage[symbol]["price_basis"], "volume_basis": coverage[symbol]["volume_basis"],
            "historical_publication_times": "UNKNOWN", "corporate_action_completeness": "UNKNOWN",
            "historical_ticker_and_listing_history": "NOT_ESTABLISHED_BY_CURRENT_CONTRACT_QUALIFICATION",
            "request_windows": coverage[symbol]["request_windows"],
            "request_diagnostic_count": len(coverage[symbol]["request_diagnostics"]),
            "native_finding_counts": dict(sorted(Counter(f["code"] for f in coverage[symbol]["native_capture_findings"]).items())),
            "cycles": [{"label": c["label"], "start": c["start"], "end": c["end"],
                "expected_sessions": sum(c["start"] <= d <= c["end"] for d in expected),
                "observed_sessions": sum(c["start"] <= d <= c["end"] for d in days),
                "unobserved_sessions": [d for d in expected if c["start"] <= d <= c["end"] and d not in days],
                "interpretation": "Unobserved does not distinguish pre-listing, provider gaps or absent captures"} for c in cycles]})
    return result


def observed_snapshots(master, panel, months):
    """Retrospective bar-presence inventory, with no common-stock admission claim."""
    snapshots = []
    for month in months:
        session = [s for s in panel.calendar["sessions"] if s["session_date"].startswith(month)][-1]
        day = session["session_date"]
        decision = (timestamp(session["closes_at"])+timedelta(hours=2)).isoformat()
        expected = [s["session_date"] for s in panel.calendar["sessions"] if s["session_date"] <= day][-60:]
        if len(expected) != 60:
            raise ValueError("60 expected sessions required for observed-window diagnostics")
        records = []
        for sid in sorted(master.by_id):
            fact = master.as_of(sid, day, decision, reconstruct_unknown=True)
            # Use the frozen current capture alias only for display. It is never
            # promoted to the symbol known to traders at the historical date.
            display = master.by_id[sid][0]["capture_symbol"]
            rows = panel.rows_as_of(sid, decision, through=day, start=expected[0], reconstruct_unknown=True)
            days = {r["session_date"] for r in rows}
            missing = [d for d in expected if d not in days]
            records.append({"security_id": sid, "capture_symbol": display,
                "historical_symbol": None, "observed_by_date": fact is not None,
                "observed_window_sessions": len(days), "missing_window_sessions": missing,
                "complete_60_session_native_window": not missing,
                "historical_identity_status": "UNVERIFIED", "native_basis_admission": "NOT_GRANTED"})
        snapshots.append({"selection_date": day, "decision_timestamp": decision,
            "interpretation": "RETROSPECTIVE_OBSERVED_CONTRACT_COHORT_NOT_A_HISTORICAL_POPULATION",
            "availability_assumption": "PR8A explicit reconstruction uses completed Close +60min; source timestamps remain null",
            "catalogue_count": len(records), "observed_contracts": sum(r["observed_by_date"] for r in records),
            "complete_60_session_windows": sum(r["complete_60_session_native_window"] for r in records), "records": records})
    return snapshots


def markdown(report, inventory):
    lines = ["# PR8B existing-source historical equity pilot", "",
        f"Origin: **{report['origin']}**. Existing immutable captures only; no new acquisition.", "",
        f"Observed catalogue: {report['observed_catalogue']['all_instruments']} contracts; "
        f"pilot: {report['pilot_stock_count']} stocks, {report['pilot_price_rows']:,} daily rows.", "",
        "This is a retrospectively chosen observed-contract cohort. It is not a complete historical stock population, "
        "a historical screening list or survivorship-bias-free research. Capture symbols are display aliases; "
        "historical ticker/issuer/share-class continuity is unverified.", "",
        "## Two dated observations and unchanged admission gates", "",
        "| Date | Observed contracts | Complete 60-session native windows | Strict admitted | Reconstructed admitted |",
        "|---|---:|---:|---:|---:|"]
    for i, snapshot in enumerate(report["observed_snapshots"]):
        lines.append(f"| {snapshot['selection_date']} | {snapshot['observed_contracts']} | {snapshot['complete_60_session_windows']} | "
            f"{report['universe_admission']['strict'][i]['members']} | {report['universe_admission']['reconstruction'][i]['members']} |")
    lines += ["", "A complete native window is a bar-presence measurement, not eligibility for PR8A liquidity ranking. "
        "The strict gate requires historically known identity; the explicit reconstruction gate additionally exposes "
        "missing classification/listing history and unadmitted split-adjusted price/unverified volume units. "
        "Both return PIT_UNVERIFIED. Source clocks remain null; Close +60 minutes is only the existing explicit "
        "reconstruction query assumption. No prices, listing dates, corporate actions or terminal returns are inferred.", "",
        "## Observed coverage by contract", "",
        "Gaps use the frozen XNYS session calendar within each observed first/last span. "
        "Unobserved periods outside that span cannot be distinguished as pre-listing versus unavailable data. "
        "ETFs are context instruments and do not enter the stock pilot.", "",
        "| Capture alias | conId | Kind | First observed | Last observed | Sessions | Internal gaps |",
        "|---|---:|---|---|---|---:|---:|"]
    for row in inventory:
        lines.append(f"| {row['capture_symbol']} | {row['con_id']} | {row['kind']} | {row['first_observed_session']} | "
            f"{row['last_observed_session']} | {row['observed_sessions']} | {row['missing_internal_count']} |")
    lines += ["", "## Coverage across fixed market-cycle windows", "",
        "Counts are contracts with any bars / all expected bars in that window, not the number of stocks that existed then. "
        "A later-chosen surviving or expert-mentioned sample cannot establish historical cross-sectional performance.", "",
        "| Window | Stocks any / full | ETFs any / full |", "|---|---:|---:|"]
    for i, cycle in enumerate(inventory[0]["cycles"]):
        groups = [[r for r in inventory if (r["kind"] == "stock") == is_stock] for is_stock in (True, False)]
        values = [f"{sum(r['cycles'][i]['observed_sessions'] > 0 for r in group)} / "
            f"{sum(r['cycles'][i]['observed_sessions'] == r['cycles'][i]['expected_sessions'] for r in group)}" for group in groups]
        lines.append(f"| {cycle['label']} | {values[0]} | {values[1]} |")
    lines += ["", "## Remaining uncertainty", "",
        "All included native histories retain documented IBKR split-adjusted prices and unverified volume units. "
        "Original historical dissemination times and corporate-action completeness are unknown for every instrument. "
        "Qualified conIds establish captured contract identity; they do not establish historic symbols, listing status "
        "or complete issuer histories. Zero verified delisted histories were imported; the count of omitted historical "
        "securities is UNKNOWN because no complete population denominator exists. An empty imported action inventory "
        "means not supplied, not no actions.", "",
        "The 26-trade Grimes status CSV is a separate source-ledger projection, not this price cohort. "
        "No actual trade fills, source closure causes, strategy edge, returns from a tradable universe or execution "
        "admission are claimed.", "", "## Immutable dependency hashes", ""]
    for name, sha in sorted(report["hashes"].items()):
        lines.append(f"- {name}: `{sha}`")
    lines += [f"- inputs: `{report['inputs_bundle_sha256']}`", ""]
    return "\n".join(lines).encode()


def freeze_pilot(inputs, output):
    files, input_seal = read_bundle(inputs)
    config, prices, coverage, kinds = read_inputs(files)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    origin = config["origin"]
    source = {"provider": "IBKR_EXISTING_CAPTURES", "origin": origin, "status": "SUCCESS", "failure_codes": [],
        "permission_reference": "Existing operator-authorized local captures; no new connection or publication of raw data",
        "coverage_evidence": "Observed selected contracts only; complete historical population UNKNOWN",
        "identity_evidence": "Qualified conIds in frozen native checkpoints; historical issuer/class/ticker evidence incomplete",
        "availability_evidence": None, "vintage_evidence": None, "reviewed_pit_attestation": False,
        "corporate_action_completeness": "UNKNOWN", "inputs_bundle_sha256": input_seal["bundle_sha256"]}
    calendar = schedule(config["pilot_start"], config["calendar_end"])
    inventory_calendar = schedule(config["inventory_start"], config["end"])
    facts, observations = [], []
    for symbol in sorted(prices):
        if kinds[symbol] != "stock":
            continue
        selected = [r for r in prices[symbol] if config["pilot_start"] <= r["session_date"] <= config["end"]]
        if not selected:
            continue
        info = coverage[symbol]
        sid = f"ibkr:conid:{info['contract']['conId']}"
        facts.append({"fact_id": sid+"/observed", "revision": 1, "security_id": sid,
            "issuer_id": None, "share_class_id": None, "symbol": None, "exchange": None, "security_type": None,
            "currency": "USD", "trading_status": None, "listing_start": None, "listing_end": None,
            "provider_security_id": str(info["contract"]["conId"]), "identity_confidence": "WEAK",
            "identity_evidence": info["source_bundle_sha256"], "effective_from": selected[0]["session_date"],
            "effective_to": None, "known_at": None, "capture_symbol": symbol, "qualified_contract": info["contract"],
            "effective_interval_interpretation": "Observed panel span only; not listing dates or historical symbol validity",
            "original_source_bundle_sha256": info["source_bundle_sha256"]})
        for row in selected:
            if row["price_basis"] != "IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED" or row["volume_basis"] != "IBKR_NATIVE_UNITS_UNVERIFIED":
                raise ValueError("unexpected native basis; no automatic reinterpretation")
            observations.append({k: row[k] for k in ("session_date", "open", "high", "low", "close", "volume")} | {
                "security_id": sid, "currency": "USD", "price_basis": "SPLIT_ADJUSTED", "volume_basis": "VENDOR_UNVERIFIED",
                "native_price_basis": row["price_basis"], "native_volume_basis": row["volume_basis"],
                "revision": 1, "known_at": None, "available_at": None, "availability_status": "UNKNOWN", "quality_status": "VALID",
                "original_observation_reference": f"{info['source_bundle_sha256']}/{row['source_row']['checkpoint']}/{row['source_row']['file']}/{row['source_row']['row']}",
                "native_source_row": row["source_row"], "native_source_snapshot_sha256": row["source_snapshot_sha256"]})
    if not facts:
        raise ValueError("pilot requires observed real stock bars (or explicitly synthetic test evidence)")
    captures = output / "captures"
    captures.mkdir()
    master_source = captures / "master.json"
    master_source.write_bytes(encode({"schema_version": "security_master_capture_v1", "source": source,
                                     "records": facts, "lifecycle_events": []}))
    master_hashes = import_master(master_source, output / "security_master")
    batches = []
    for i in range(0, len(observations), 5000):
        p = captures / f"prices-{i//5000:04d}.json"
        p.write_bytes(encode({"schema_version": "daily_panel_capture_v1", "source": source, "rows": observations[i:i+5000]}))
        batches.append(p)
    panel_hashes = freeze_panel(batches, calendar, output / "research_panel")
    universes, universe_hashes = {}, {}
    for label, policy in (("strict", "EXCLUDE"), ("reconstruction", "RECONSTRUCT_EXPLICITLY")):
        definition = default_definition(config["top_n"])
        definition["unknown_knowledge_policy"] = policy
        hashes = build_universe(output / "security_master", output / "research_panel", definition,
                                config["selection_months"], output / (label+"_universe"))
        universe = HistoricalUniverse(output / (label+"_universe"), master=output / "security_master", panel=output / "research_panel")
        universes[label], universe_hashes[label] = universe, hashes["bundle_sha256"]
    master, panel = universes["strict"].master, universes["strict"].panel
    observed = observed_snapshots(master, panel, config["selection_months"])
    inventory = coverage_inventory(prices, coverage, kinds, inventory_calendar, config["cycles"])
    report = {"schema_version": "existing_source_universe_pilot_v1", "origin": origin,
        "inputs_bundle_sha256": input_seal["bundle_sha256"], "base_commit": config["base_commit"],
        "implementation": {"files": {str(p.relative_to(Path(__file__).parents[1])): digest(p.read_bytes())
            for p in [Path(__file__), *sorted((Path(__file__).parents[1] / "universe").glob("*.py")),
                      Path(__file__).parents[1] / "comprehension/inputs.py", Path(__file__).parents[1] / "history/depth_store.py",
                      Path(__file__).parents[1] / "ingestion/calendar.py"]},
            "python": platform.python_version(), "pyarrow": importlib.metadata.version("pyarrow"),
            "exchange_calendars": importlib.metadata.version("exchange-calendars"), "shared_dependency": shared_identity(),
            "revision_interpretation": "Base commit is the merged starting point; exact implementation bytes are authoritative"},
        "observed_catalogue": {"all_instruments": len(prices), "kinds": dict(sorted(Counter(kinds.values()).items()))},
        "pilot_stock_count": len(facts), "pilot_price_rows": len(observations),
        "strict_historical_population": "NOT_ESTABLISHED", "survivorship_bias_free": False,
        "verified_delisted_stock_histories": 0, "missing_historical_securities_count": None,
        "missing_historical_securities_interpretation": "Unknown denominator; zero verified delisted histories is not zero delistings",
        "historical_actions": "UNKNOWN; empty imported lifecycle inventory means not supplied, not no actions",
        "observed_snapshots": observed,
        "universe_admission": {label: [{"selection_date": s["selection_date"], "members": len(s["members"]),
            "pit_quality": s["pit_quality"], "exclusion_counts": s["summary"]["rejection_counts"]} for s in u.snapshots]
            for label, u in universes.items()},
        "hashes": {"security_master": master_hashes["bundle_sha256"], "research_panel": panel_hashes["bundle_sha256"], **universe_hashes},
        "no_new_acquisition": True, "execution_admission": "NOT_GRANTED"}
    return write_bundle(output / "report", {"report.json": encode(report), "coverage.json": encode(inventory), "report.md": markdown(report, inventory),
        "panel_quality.json": encode(panel.quality), "master_quality.json": encode(master.quality)})
