"""Offline integration evidence only; all outputs must use a fresh directory.

Run from the repository root:
PYTHONPATH=src .venv/bin/python PATH/validate.py --output NEW_DIRECTORY
"""

import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys

from equity_research.ingestion.storage import encode, read_bundle
from equity_research.universe import HistoricalUniverse, build_universe
from equity_research.universe.storage import verify


def denied(*args, **kwargs):
    raise AssertionError("network forbidden during PR8A integration validation")


socket.socket.connect = denied
socket.socket.connect_ex = denied
socket.create_connection = denied
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
checks = []
for name, scale in (("pilot", None), ("scale100", 100), ("scale1000", 1000)):
    original = Path(f"data/research_datasets/pr8a-{name}-8xc4tbfk-v1")
    target = args.output / name
    wrapper = """import runpy, socket, sys
def denied(*args, **kwargs):
    raise AssertionError('network forbidden during synthetic pilot')
socket.socket.connect = denied
socket.socket.connect_ex = denied
socket.create_connection = denied
sys.argv = ['scripts/pilot_historical_universe.py', *sys.argv[1:]]
runpy.run_path('scripts/pilot_historical_universe.py', run_name='__main__')
"""
    command = [sys.executable, "-c", wrapper, "--output", str(target)]
    if scale is not None:
        command.extend(["--scale", str(scale)])
    with (args.output / f"{name}-stdout.json").open("xb") as stdout, (args.output / f"{name}-stderr.txt").open("xb") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr)
    report = json.loads((target / "evidence/pilot_report.json").read_bytes())
    previous_report = json.loads((original / "evidence/pilot_report.json").read_bytes())
    assert report["source_commit"] == source_commit
    assert not report["source_worktree_dirty"]
    assert report["hashes"] == previous_report["hashes"]
    assert report["source_capture_hashes"] == previous_report["source_capture_hashes"]
    assert report["months"] == previous_report["months"]
    assert report["turnover"] == previous_report["turnover"]
    for component in ("security_master", "research_panel"):
        assert verify(target / component) == verify(original / component)
    old = HistoricalUniverse(original / "universe", master=original / "security_master", panel=original / "research_panel")
    replay = target / "replayed-original-universe"
    rebuilt = build_universe(original / "security_master", original / "research_panel", old.definition,
        [s["selection_month"] for s in old.snapshots], replay,
        decisions={s["selection_month"]: s["decision_timestamp"] for s in old.snapshots})
    assert read_bundle(replay) == read_bundle(original / "universe")
    loaded = HistoricalUniverse(replay, master=original / "security_master", panel=original / "research_panel")
    assert loaded.content_sha256 == old.content_sha256 == rebuilt["bundle_sha256"]
    query_count = 0
    for snapshot in old.snapshots:
        day = snapshot["effective_start"]
        cutoff = day + "T23:00:00-04:00"
        assert loaded.members_as_of(day, decision_timestamp=cutoff) == old.members_as_of(day, decision_timestamp=cutoff)
        query_count += 1
    checks.append({"case": name, "original": str(original), "output": str(target),
        "source_capture_bytes_reproduced": True, "master_panel_hashes_identical": True,
        "universe_rebuilt_from_original_dependencies_byte_identical": True,
        "all_original_data_bundle_hashes_identical": report["hashes"],
        "monthly_snapshots": len(old.snapshots), "membership_queries_equal": query_count,
        "price_rows": report["price_rows"], "members_per_snapshot": [len(s["members"]) for s in old.snapshots],
        "original_and_replayed_universes_semantically_valid": True})
    print(f"{name}: original inputs, data hashes, selections, changes, quality and queries reproduced", flush=True)
result = {"schema_version": "pr8a_main_integration_validation_v1", "source_commit": source_commit,
    "network": "SOCKETS_DENIED_IN_PARENT_AND_PILOT_SUBPROCESSES", "checks": checks,
    "limitations": ["Synthetic fixtures only; no real historical coverage or strategy edge claim",
        "Resource timings are incidental integration-run observations, not new scale benchmarks"]}
(args.output / "validation.json").write_bytes(encode(result))
print(json.dumps(result, indent=2))
