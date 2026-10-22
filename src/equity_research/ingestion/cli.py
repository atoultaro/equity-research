"""Data subcommands; optional libraries load only within the chosen operation."""

import json
from pathlib import Path
from uuid import uuid4


def register(commands):
    parser = commands.add_parser("data", help="explicit acquisition and offline data preparation")
    operations = parser.add_subparsers(dest="operation", required=True)
    fetch = operations.add_parser("fetch-yahoo")
    fetch.add_argument("--symbol", required=True)
    fetch.add_argument("--start", required=True)
    fetch.add_argument("--end", required=True, help="inclusive final research date")
    fetch.add_argument("--output", type=Path, required=True, help="parent directory for a new attempt UUID")
    for name in ("validate", "export"):
        command = operations.add_parser(name)
        command.add_argument("--snapshot", type=Path, required=True)
        command.add_argument("--evidence", type=Path, help="research_evidence_v1 attestations; unknown if absent")
        command.add_argument("--output", type=Path, required=True, help="exclusive new output directory")
    compare = operations.add_parser("compare")
    compare.add_argument("--before", type=Path, required=True)
    compare.add_argument("--after", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    from ..history.cli import register as register_history
    register_history(operations)
    from ..events.cli import register as register_events
    register_events(operations)


def dispatch(args):
    from .storage import encode, write_bundle

    if args.operation in {"events-freeze", "event-study"}:
        from ..events.cli import dispatch as dispatch_events
        return dispatch_events(args)
    if args.operation in {"history", "freeze", "compare-providers"}:
        from ..history.cli import dispatch as dispatch_history
        return dispatch_history(args)
    if args.operation == "fetch-yahoo":
        from ..providers.yahoo import fetch
        path = args.output / str(uuid4())
        result = fetch(args.symbol, args.start, args.end, path)
        print(encode({"snapshot": str(path), "status": result["status"]}).decode(), end="")
        return 0 if result["status"] == "SUCCESS" else 3
    if args.operation == "compare":
        from .snapshots import compare
        result = compare(args.before, args.after)
        write_bundle(args.output, {"comparison.json": encode(result)})
        print(encode({"status": result["status"]}).decode(), end="")
        return 0 if result["status"] == "PASS" else 3
    from .export import export, validate
    evidence = json.loads(args.evidence.read_bytes()) if args.evidence else None
    result = (export if args.operation == "export" else validate)(args.snapshot, args.output, evidence)
    print(encode({"export_decision": result["export_decision"],
                  "blocking_reasons": result["blocking_reasons"]}).decode(), end="")
    return 3 if args.operation == "export" and result["export_decision"] != "EXPORT_READY" else 0
