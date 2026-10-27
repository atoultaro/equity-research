"""Reproduce PR8A's offline pilot or bounded scale case; never acquires data.

PYTHONPATH=src .venv/bin/python scripts/pilot_historical_universe.py --output NEW_DIR
PYTHONPATH=src .venv/bin/python scripts/pilot_historical_universe.py --scale 1000 --output NEW_DIR
Each invocation must run in a fresh process for meaningful peak RSS reporting.
"""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
from time import perf_counter

from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode, write_bundle
from equity_research.universe import (import_master, freeze_panel, build_universe, HistoricalUniverse, default_definition)
from equity_research.universe.synthetic import write_fixture_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scale", type=int, choices=(100, 1000))
    args = parser.parse_args()
    started = perf_counter()
    args.output.mkdir(parents=True, exist_ok=False)
    count = args.scale or 100
    if args.scale:
        calendar = schedule("2022-01-01", "2022-07-31")
        windows = [("2022-01-01", "2022-06-30")]
        months = ["2022-04", "2022-05"]
    else:
        calendar = schedule("2007-01-01", "2026-10-23")
        windows = [(f"{year}-01-01", f"{year}-06-30") for year in (2008, 2015, 2020, 2022)] + [("2026-01-01", "2026-10-23")]
        months = [f"{year}-{month}" for year in (2008, 2015, 2020, 2022) for month in ("04", "05")] + ["2026-08", "2026-09"]
    source, captures = write_fixture_inputs(args.output / "inputs", calendar, count, windows=windows, hard_cases=not args.scale)
    generated = perf_counter()
    master = import_master(source, args.output / "security_master")
    panel = freeze_panel(captures, calendar, args.output / "research_panel")
    frozen = perf_counter()
    definition = default_definition(count if args.scale else 50)
    universe = build_universe(args.output / "security_master", args.output / "research_panel", definition, months, args.output / "universe")
    built = perf_counter()
    u = HistoricalUniverse(args.output / "universe", master=args.output / "security_master", panel=args.output / "research_panel")
    loaded = perf_counter()
    integration = None
    if not args.scale:
        from equity_research.universe.integration import single_security_inputs
        from equity_research.swing.engine import evaluate
        from equity_research.swing.model import Configuration as SwingConfig
        from equity_research.outcomes.model import Configuration as OutcomeConfig, measure
        swing, outcome = SwingConfig(), OutcomeConfig()
        chosen = u.snapshots[-1]["members"][0]
        sid = chosen["security_id"]
        rows, cal, manifest = single_security_inputs(u, sid, "2026-10-01", "2026-10-01T09:20:00-04:00",
            price_cutoff_timestamp="2026-10-24T00:00:00Z", history_start="2026-01-01",
            strategy_configuration_sha256=swing.sha256, outcome_configuration_sha256=outcome.sha256)
        signals = evaluate(rows, cal, chosen["identity"]["symbol"], sid, u.panel.content_sha256, swing,
                           start="2026-10-01", end="2026-10-23")
        paths = []
        if signals["signals"]:
            paths, _ = measure(signals["signals"][0], rows, cal, price_sha=u.panel.content_sha256,
                strategy_sha=swing.sha256, basis={"price_basis": "SYNTHETIC_RAW", "verified": False}, configuration=outcome)
        integration = write_bundle(args.output / "integration", {"universe_research_manifest.json": encode(manifest),
            "strategy_configuration.json": encode(swing.record()), "outcome_configuration.json": encode(outcome.record()),
            "signals.json": encode(signals["signals"]), "first_signal_outcomes.json": encode(paths),
            "limitations.json": encode({"origin": "SYNTHETIC", "no_strategy_edge": True,
                 "signal_count": len(signals["signals"]), "outcome_rows": len(paths),
                 "actions": "Incomplete synthetic evidence; no execution certification", "context": "UNAVAILABLE"})})
    elapsed = perf_counter() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == "darwin" else rss*1024
    revision = subprocess.run(["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], text=True, capture_output=True, check=True).stdout)
    report = {"schema_version": "universe_pilot_evidence_v1", "origin": "SYNTHETIC", "real_securities_acquired": 0,
        "provider_access_blocker": "No authorized listed/delisted master, vintage archive or licensed bulk source supplied",
        "source_commit": revision, "source_worktree_dirty": dirty,
        "environment": {"python": platform.python_version(), "system": platform.platform(),
            "machine": platform.machine(), "pyarrow": importlib.metadata.version("pyarrow"),
            "exchange_calendars": importlib.metadata.version("exchange-calendars"),
            "market_shared": importlib.metadata.version("market-shared")},
        "security_master_count": u.master.quality["security_count"], "materialization_windows": windows,
        "price_rows": u.panel.quality["row_count"], "partition_count": sum(len(v) for v in u.panel.index.values()),
        "months": [{"selection_date": s["selection_date"], "members": len(s["members"]), "quality": s["pit_quality"],
                    "eligible": s["summary"]["eligible_count"]} for s in u.snapshots],
        "timing_seconds": {"fixture_generation": generated-started, "master_and_panel_freeze": frozen-generated,
            "universe_build": built-frozen, "dependency_validation_and_load": loaded-built, "total": elapsed},
        "peak_process_rss_bytes": rss_bytes, "rss_measurement": "fresh-process getrusage(RUSAGE_SELF).ru_maxrss; includes Python and Arrow native allocations",
        "hashes": {"security_master": master["bundle_sha256"], "research_panel": panel["bundle_sha256"],
                   "universe": universe["bundle_sha256"], "integration": integration["bundle_sha256"] if integration else None},
        "source_capture_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, *captures]},
        "master_quality": u.master.quality, "turnover": u.changes,
        "engineering_scope": "Bounded rows across all securities; not a 5-million-bar or real historical coverage benchmark"}
    evidence = write_bundle(args.output / "evidence", {"pilot_report.json": encode(report)})
    print(json.dumps({"report": report, "evidence_bundle_sha256": evidence["bundle_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
