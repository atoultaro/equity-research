"""Explicitly offline lifecycle commands. Native acquisition remains in PR14."""

import json
from pathlib import Path


def register(commands):
    parser = commands.add_parser("lifecycle", help="offline source/model lifecycle reconstruction")
    sub = parser.add_subparsers(dest="lifecycle_operation", required=True)
    alerts = sub.add_parser("capture-alerts")
    alerts.add_argument("--input", type=Path, required=True, help="seven original bodies with explicit source/publication metadata")
    alerts.add_argument("--output", type=Path, required=True)
    inputs = sub.add_parser("freeze-inputs")
    inputs.add_argument("--spec", type=Path, required=True)
    inputs.add_argument("--alerts", type=Path, required=True, help="sealed original-alert capture bundle")
    inputs.add_argument("--methodology", type=Path, required=True)
    inputs.add_argument("--audit", nargs=2, action="append", required=True, metavar=("REPORT", "SYMBOLS_CSV"))
    inputs.add_argument("--output", type=Path, required=True)
    study = sub.add_parser("study")
    study.add_argument("--inputs", type=Path, required=True)
    study.add_argument("--output", type=Path, required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--study", type=Path, required=True)
    replay.add_argument("--output", type=Path, required=True)


def dispatch(args):
    from ..ingestion.storage import encode, write_bundle
    from .study import freeze_alerts, freeze_inputs, freeze_study, load_study
    if args.lifecycle_operation == "capture-alerts":
        hashes = freeze_alerts(args.input, args.output)
    elif args.lifecycle_operation == "freeze-inputs":
        hashes = freeze_inputs(json.loads(args.spec.read_bytes()), args.alerts,
            [(Path(p), symbols.split(",")) for p, symbols in args.audit], args.methodology, args.output)
    elif args.lifecycle_operation == "study":
        hashes = freeze_study(args.inputs, args.output)
    else:
        checked = load_study(args.study)
        hashes = write_bundle(args.output, checked["files"])
    print(encode({"output": str(args.output), "sha256": hashes["bundle_sha256"]}).decode(), end="")
    return 0
